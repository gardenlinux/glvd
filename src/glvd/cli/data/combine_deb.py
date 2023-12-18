# SPDX-License-Identifier: MIT

from __future__ import annotations

import logging
from typing import (
    Any,
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

from glvd.database import Base, DistCpe, DebCve
from glvd.data.cpe import Cpe, CpeOtherDebian
from glvd.data.cvss import CvssSeverity
from . import cli


logger = logging.getLogger(__name__)


class CombineDeb:
    @staticmethod
    @cli.register('combine-deb')
    def run(database: str, debug: bool) -> None:
        logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)
        engine = create_async_engine(database, echo=debug)
        asyncio.run(CombineDeb()(engine))

    stmt_combine_new = (
        text('''
            SELECT
                    debsec_cve.cve_id
                    , nvd_cve.data
                    , debsrc.deb_source
                    , debsrc.deb_version
                    , debsec_cve.deb_version_fixed
                    , COALESCE(debsrc.deb_version < debsec_cve.deb_version_fixed, TRUE) AS debsec_vulnerable
                    , debsec_note
                FROM
                    debsrc
                    LEFT OUTER JOIN debsec_cve ON debsec_cve.deb_source = debsrc.deb_source
                    INNER JOIN nvd_cve ON nvd_cve.cve_id = debsec_cve.cve_id
                WHERE
                    debsrc.dist_id = :dist_id
                    AND debsec_cve.dist_id = ANY(:dists_fallback_id)
        ''')
        .bindparams(
            bindparam('dist_id'),
            bindparam('dists_fallback_id'),
        )
    )

    def extract_cvss_severity(
        self,
        entry: Any,
    ) -> CvssSeverity | None:
        if metrics := entry.get('metrics'):
            for i in ('cvssMetricV31', 'cvssMetricV30'):
                if metrics_single := metrics.get(i):
                    metrics_primary = [i for i in metrics_single if i.get('type', None) == 'Primary']
                    if metrics_primary and (severity := metrics_primary[0].get('cvssData', {}).get('baseSeverity')):
                        try:
                            return CvssSeverity[severity]
                        except KeyError:
                            return None
        return None

    async def combine_dists(
        self,
        session: AsyncSession,
    ) -> AsyncGenerator[tuple[DistCpe, list[DistCpe]], None]:
        stmt = (
            select(DistCpe)
            # Debian and empty version are a fallback, make sure we see them first
            .order_by((DistCpe.cpe_vendor == 'debian').desc())
            .order_by((DistCpe.cpe_version == '').desc())
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
                # XXX: Remove hardcoded values somehow
                if entry.cpe_product == 'gardenlinux':
                    if fallback := dists_fallback.get(('debian', 'debian_linux')):
                        dists.append(fallback)
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
                (
                    cve_id,
                    nvd_data,
                    deb_source,
                    deb_version,
                    deb_version_fixed,
                    debsec_vulnerable,
                    debsec_note
                ) = r

                if debsec_note:
                    debsec_notes = [i.strip() for i in debsec_note.split(';')]
                else:
                    debsec_notes = []

                cvss_severity = self.extract_cvss_severity(nvd_data)
                if 'unimportant' in debsec_notes:
                    cvss_severity = CvssSeverity.UNIMPORTANT

                cpe = Cpe(
                    part=Cpe.PART.OS,
                    vendor=dist.cpe_vendor,
                    product=dist.cpe_product,
                    version=dist.cpe_version,
                    other=CpeOtherDebian(deb_source=deb_source),
                )

                cpe_match = {
                    'criteria': str(cpe),
                    'deb': {
                        'versionLatest': deb_version,
                    },
                    'vulnerable': debsec_vulnerable,
                }

                if cvss_severity:
                    cpe_match['deb']['cvssSeverity'] = cvss_severity.name
                if deb_version_fixed:
                    cpe_match['deb']['versionEndExcluding'] = deb_version_fixed

                new_entries[(cve_id, deb_source)] = DebCve(
                    dist=dist,
                    cve_id=cve_id,
                    cvss_severity=cvss_severity,
                    deb_source=deb_source,
                    deb_version=deb_version,
                    deb_version_fixed=deb_version_fixed,
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
    CombineDeb.run()
