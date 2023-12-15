# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging

import asyncio
from sqlalchemy import (
    select,
    text,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..database import Base, AllCve
from . import cli


logger = logging.getLogger(__name__)


class CombineAll:
    @staticmethod
    @cli.register(
        'combine-all',
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
        asyncio.run(CombineAll()(engine))

    stmt_combine_new = (
        text('''
        SELECT
                nvd_cve.cve_id
                , nvd_cve.data
                , array_to_json(
                    array_agg(deb_cve.data_cpe_match)
                ) AS data_cpe_matches
            FROM
                nvd_cve
                INNER JOIN deb_cve USING (cve_id)
            GROUP BY
                nvd_cve.cve_id
        ''')
    )

    async def combine_update(
        self,
        session: AsyncSession,
        new_entries: dict[str, AllCve],
    ) -> None:
        stmt = select(AllCve)

        async for r in await session.stream(stmt):
            entry = r[0]

            new_entry = new_entries.pop(entry.cve_id, None)
            if not new_entry:
                await session.delete(entry)
                continue

            # Update object in place. Only real changes will be commited
            entry.merge(new_entry)

    async def combine_insert(
        self,
        session: AsyncSession,
        new_entries: dict[str, AllCve],
    ) -> None:
        for entry in new_entries.values():
            session.add(entry)

    async def combine(
        self,
        session: AsyncSession,
    ) -> None:
        new_entries: dict[str, AllCve] = {}

        async for r in await session.stream(self.stmt_combine_new):
            cve_id, data, data_cpe_matches = r

            data.setdefault('configurations', []).append({
                'nodes': [{
                    'cpeMatch': data_cpe_matches,
                    'negate': False,
                    'operator': 'OR',
                }],
            })

            new_entries[cve_id] = AllCve(
                cve_id=cve_id,
                data=data,
            )

        await self.combine_update(session, new_entries)
        await self.combine_insert(session, new_entries)

    async def __call__(
        self,
        engine: AsyncEngine,
    ) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_sessionmaker(engine)() as session:
            await self.combine(session)
            await session.commit()


if __name__ == '__main__':
    CombineAll.run()
