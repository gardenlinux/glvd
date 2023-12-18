# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

import asyncio
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncEngine,
    create_async_engine,
)

from glvd.database import Base, NvdCve
from glvd.util import requests
from . import cli


logger = logging.getLogger(__name__)


class IngestNvd:
    wait: int

    @staticmethod
    @cli.register(
        'ingest-nvd',
        arguments=[
            cli.add_argument(
                '--database',
                default='postgresql+asyncpg:///',
                help='the database to use, must use asyncio compatible SQLAlchemy driver',
            ),
            cli.add_argument(
                '--debug',
                action='store_true',
                help='enable debug output',
            ),
        ]
    )
    def run(database: str, debug: bool) -> None:
        logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)
        engine = create_async_engine(database, echo=debug)
        asyncio.run(IngestNvd()(engine))

    def __init__(self, *, wait: int = 6) -> None:
        self.wait = wait

    async def insert_cve(
        self,
        conn: AsyncConnection,
        entries: list[Any],
    ) -> None:
        for entry_base in entries:
            entry = entry_base['cve']
            last_mod = datetime.fromisoformat(entry['lastModified'])
            insert_stmt = insert(NvdCve).values(
                cve_id=entry['id'],
                last_mod=last_mod,
                data=entry,
            ).on_conflict_do_update(
                index_elements=('cve_id', ),
                set_=dict(
                    last_mod=last_mod,
                    data=entry,
                ),
                where=(NvdCve.last_mod != last_mod),
            )
            await conn.execute(insert_stmt)

    async def fetch_cve_impl(
        self,
        conn: AsyncConnection,
        rsession: requests.RetrySession,
        params: dict[str, str],
    ) -> None:
        offset = 0

        while True:
            resp = rsession.get(
                'https://services.nvd.nist.gov/rest/json/cves/2.0/',
                params=params | {
                    'startIndex': str(offset),
                },
            )
            resp.raise_for_status()
            data = resp.json()

            logger.debug(f'Expect total results {data["totalResults"]}')

            if entries := data['vulnerabilities']:
                await self.insert_cve(conn, entries)

                offset += len(entries)
                logger.debug(f'Inserted {len(entries)} entries')

                await asyncio.sleep(self.wait)

            # No more entries left
            else:
                break

    async def fetch_cve(
        self,
        conn: AsyncConnection,
    ) -> None:
        with requests.RetrySession() as rsession:
            result = await conn.execute(select(func.max(NvdCve.last_mod)))
            last_mod = result.one()[0]

            now = datetime.now(timezone.utc)
            start = now - timedelta(days=60)

            if not last_mod or last_mod <= start:
                logger.info('Requesting all data')
                await self.fetch_cve_impl(conn, rsession, {})
                last_mod = now

            # Request seven days before the last modification.  This violates
            # parts the the best practices documented at
            # https://nvd.nist.gov/developers/start-here#:~:text=Best%20Practices
            # It turns out, we don't work on a stable snapshot, and the
            # modification timestamp changes.
            check = last_mod - timedelta(days=7)
            params: dict[str, str] = {
                'lastModStartDate': check.isoformat(),
                'lastModEndDate': now.isoformat(),
            }

            logger.info(f'Requesting data from {start} to {now}')
            await self.fetch_cve_impl(conn, rsession, params)

    async def __call__(self, engine: AsyncEngine) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with engine.begin() as conn:
            await self.fetch_cve(conn)
            await conn.commit()


if __name__ == '__main__':
    IngestNvd.run()
