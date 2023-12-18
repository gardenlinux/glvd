# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from pathlib import Path

import asyncio
from sqlalchemy import select
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from glvd.database import Base, DistCpe, DebsecCve
from glvd.data.debsec_cve import DebsecCveFile
from glvd.data.dist_cpe import DistCpeMapper
from . import cli


logger = logging.getLogger(__name__)


class IngestDebsec:
    @staticmethod
    @cli.register(
        'ingest-debsec',
        arguments=[
            cli.prepare_argument(
                'cpe_product',
                choices=sorted(DistCpeMapper.keys()),
                help=f'CPE product used for data, supported: {" ".join(sorted(DistCpeMapper.keys()))}',
                metavar='CPE_PRODUCT',
            ),
            cli.prepare_argument(
                'dir',
                help='data directory out of https://salsa.debian.org/security-tracker-team/security-tracker',
                metavar='DEBSEC',
                type=Path,
            ),
        ]
    )
    def run(cpe_product: str, dir: Path, database: str, debug: bool) -> None:
        logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)
        engine = create_async_engine(database, echo=debug)
        asyncio.run(IngestDebsec(cpe_product, dir)(engine))

    def __init__(self, cpe_product: str, path: Path) -> None:
        self.path = path

        self.dist_base = DistCpeMapper.new(cpe_product)

    def read_cve(self) -> DebsecCveFile:
        r = DebsecCveFile()
        with (self.path / 'CVE' / 'list').open('r') as f:
            r.read(f)
        return r

    async def import_cve_update(
        self,
        session: AsyncSession,
        file_cve: DebsecCveFile,
    ) -> None:
        # Find all existing entries for all versions of given product
        stmt = (
            select(DebsecCve)
            .join(DebsecCve.dist)
            .where(DistCpe.cpe_vendor == self.dist_base.cpe_vendor)
            .where(DistCpe.cpe_product == self.dist_base.cpe_product)
        )

        async for r in await session.stream(stmt):
            entry = r[0]

            new_entries = file_cve.get(entry.dist.deb_codename)
            if not new_entries:
                await session.delete(entry)
                continue
            new_entry = new_entries.pop((entry.cve_id, entry.deb_source), None)
            if not new_entry:
                await session.delete(entry)
                continue

            # Update object in place. Only real changes will be commited
            entry.merge(new_entry)

    async def import_cve_insert(
        self,
        session: AsyncSession,
        file_cve: DebsecCveFile,
    ) -> None:
        # Find all existing versions of given product
        stmt = (
            select(DistCpe)
            .where(DistCpe.cpe_vendor == self.dist_base.cpe_vendor)
            .where(DistCpe.cpe_product == self.dist_base.cpe_product)
        )

        dists = {
            i[0].deb_codename: i[0]
            async for i in await session.stream(stmt)
        }

        # We ignore some dists we can't handle
        file_cve.pop('experimental', None)

        for dist_codename, dist_entries in file_cve.items():
            dist = dists.get(dist_codename)

            # Generate a new dist entry if we have non yet
            if not dist:
                dist = dists[dist_codename] = self.dist_base(dist_codename)
                session.add(dist)

            for entry in dist_entries.values():
                entry.dist = dist
                session.add(entry)

    async def import_cve(
        self,
        session: AsyncSession,
    ) -> None:
        file_cve = self.read_cve()

        await self.import_cve_update(session, file_cve)
        await self.import_cve_insert(session, file_cve)

    async def __call__(
        self,
        engine: AsyncEngine,
    ) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_sessionmaker(engine)() as session:
            await self.import_cve(session)
            await session.commit()


if __name__ == '__main__':
    IngestDebsec.run()
