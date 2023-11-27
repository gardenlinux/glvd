# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from typing import (
    AsyncGenerator,
)

import asyncio
from sqlalchemy import (
    bindparam,
    select,
    text,
)
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from ..database import Base, DistCpe, DebCve
from ..data.cpe import Cpe


logger = logging.getLogger(__name__)


class CombineDeb:
    stmt_combine_new = (
        text('''
            SELECT
                    cve.cve_id
                    , src.deb_source
                    , src.deb_version
                    , COALESCE(src.deb_version < cve.deb_version_fixed, TRUE) AS debsec_vulnerable
                FROM
                    debsrc as src
                    LEFT OUTER JOIN debsec_cve AS cve ON src.deb_source = cve.deb_source
                WHERE
                    src.dist_id = :dist_id
                    AND cve.dist_id = ANY(:dists_fallback_id)
        ''')
        .bindparams(
            bindparam('dist_id'),
            bindparam('dists_fallback_id'),
        )
    )

    async def combine_dists(
        self,
        session: AsyncSession,
    ) -> AsyncGenerator[tuple[DistCpe, list[DistCpe]], None]:
        stmt = (
            select(DistCpe)
            # Empty version is a fallback, make sure we see them first
            .order_by(DistCpe.cpe_version)
        )

        dists_fallback: dict[tuple[str, str], DistCpe] = {}

        async for r in await session.stream(stmt):
            entry = r[0]

            if entry.cpe_version == '':
                dists_fallback[(entry.cpe_vendor, entry.cpe_product)] = entry
            else:
                dists = [entry]
                if fallback := dists_fallback.get((entry.cpe_vendor, entry.cpe_product)):
                    dists.append(fallback)
                # XXX: Handle fallback to Debian
                yield entry, dists

    async def combine_update(
        self,
        session: AsyncSession,
        dist: DistCpe,
        new_entries: dict[tuple[str, str], DebCve],
    ) -> None:
        stmt = (
            select(DebCve)
            .where(DebCve.dist == dist)
        )

        async for r in await session.stream(stmt):
            entry = r[0]

            new_entry = new_entries.pop((entry.cve_id, entry.deb_source), None)
            if not new_entry:
                # XXX: Delete entry
                continue

            # Update object in place. Only real changes will be commited
            entry.merge(new_entry)

    async def combine_insert(
        self,
        session: AsyncSession,
        dist: DistCpe,
        new_entries: dict[tuple[str, str], DebCve],
    ) -> None:
        for entry in new_entries.values():
            session.add(entry)

    async def combine(
        self,
        session: AsyncSession,
    ) -> None:
        # Find all applying CVE for a source.  Was not able to make this work in ORM.
        async for dist, dists_fallback in self.combine_dists(session):
            new_entries: dict[tuple[str, str], DebCve] = {}

            async for r in await session.stream(self.stmt_combine_new, {
                'dist_id': dist.id,
                'dists_fallback_id': [i.id for i in dists_fallback],
            }):
                cve_id, deb_source, deb_version, debsec_vulnerable = r

                cpe = Cpe(
                    part=Cpe.PART.OS,
                    vendor=dist.cpe_vendor,
                    product=dist.cpe_product,
                    version=dist.cpe_version,
                )

                cpe_match = {
                    'criteria': str(cpe),
                    'vulnerable': debsec_vulnerable,
                }

                new_entries[(cve_id, deb_source)] = DebCve(
                    dist=dist,
                    cve_id=cve_id,
                    deb_source=deb_source,
                    deb_version=deb_version,
                    debsec_vulnerable=debsec_vulnerable,
                    data_cpe_match=cpe_match,
                )

            await self.combine_update(session, dist, new_entries)
            await self.combine_insert(session, dist, new_entries)

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
    import argparse
    logging.basicConfig(level=logging.DEBUG)
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    engine = create_async_engine(
        "postgresql+asyncpg:///",
        echo=True,
    )
    main = CombineDeb()
    asyncio.run(main(engine))
