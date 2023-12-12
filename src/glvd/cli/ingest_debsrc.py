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

from ..database import Base, DistCpe, Debsrc
from ..data.debsrc import DebsrcFile
from ..data.dist_cpe import DistCpeMapper


logger = logging.getLogger(__name__)


class IngestDebsrc:
    def __init__(self, cpe_product: str, deb_codename: str, file: Path) -> None:
        self.file = file

        self.dist = DistCpeMapper.new(cpe_product)(deb_codename)

    def read(self) -> DebsrcFile:
        r = DebsrcFile()
        with self.file.open('r') as f:
            r.read(f)
        return r

    async def import_update(
        self,
        session: AsyncSession,
        file: DebsrcFile,
    ) -> None:
        # Find all existing entries for all versions of given product
        stmt = (
            select(Debsrc)
            .join(Debsrc.dist)
            .where(DistCpe.cpe_vendor == self.dist.cpe_vendor)
            .where(DistCpe.cpe_product == self.dist.cpe_product)
            .where(DistCpe.deb_codename == self.dist.deb_codename)
        )

        async for r in await session.stream(stmt):
            entry = r[0]

            new_entry = file.pop(entry.deb_source, None)
            if not new_entry:
                await session.delete(entry)
                continue

            # Update object in place. Only real changes will be commited
            entry.merge(new_entry)

    async def import_insert(
        self,
        session: AsyncSession,
        file: DebsrcFile,
    ) -> None:
        # Find all existing versions of given product
        stmt = (
            select(DistCpe)
            .where(DistCpe.cpe_vendor == self.dist.cpe_vendor)
            .where(DistCpe.cpe_product == self.dist.cpe_product)
            .where(DistCpe.deb_codename == self.dist.deb_codename)
        )

        dist = (await session.scalars(stmt)).one_or_none()
        if not dist:
            dist = self.dist
            session.add(dist)

        for entry in file.values():
            entry.dist = dist
            session.add(entry)

    async def import_file(
        self,
        session: AsyncSession,
    ) -> None:
        file_cve = self.read()

        await self.import_update(session, file_cve)
        await self.import_insert(session, file_cve)

    async def __call__(
        self,
        engine: AsyncEngine,
    ) -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        async with async_sessionmaker(engine)() as session:
            await self.import_file(session)
            await session.commit()


if __name__ == '__main__':
    import argparse
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'cpe_product',
        choices=sorted(DistCpeMapper.keys()),
        help=f'CPE product used for data, supported: {" ".join(sorted(DistCpeMapper.keys()))}',
        metavar='CPE_PRODUCT',
    )
    parser.add_argument(
        'deb_codename',
        help='codename of APT archive',
        metavar='CODENAME',
    )
    parser.add_argument(
        'file',
        help='uncompressed Sources file',
        metavar='SOURCES',
        type=Path,
    )
    args = parser.parse_args()
    engine = create_async_engine(
        "postgresql+asyncpg:///",
    )
    ingest = IngestDebsrc(args.cpe_product, args.deb_codename, args.file)
    asyncio.run(ingest(engine))
