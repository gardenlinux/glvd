# SPDX-License-Identifier: MIT

from datetime import datetime

from sqlalchemy import select

from glvd.cli.combine_deb import CombineDeb
from glvd.data.cvss import CvssSeverity
from glvd.data.dist_cpe import DistCpeMapper
from glvd.database import DistCpe, DebCve, DebsecCve, Debsrc, NvdCve


class TestIngestDebsrc:
    dist_mapper = DistCpeMapper.new('debian')

    def debsec_cve(self, *, deb_version_fixed: str, debsec_note: str | None, dist: DistCpe) -> DebsecCve:
        return DebsecCve(
            cve_id='TEST-1',
            deb_source='test',
            deb_version_fixed=deb_version_fixed,
            debsec_note=debsec_note,
            dist=dist,
        )

    def debsrc(self, *, dist: DistCpe) -> Debsrc:
        return Debsrc(
            deb_source='test',
            deb_version='1',
            dist=dist,
        )

    def nvd_cve(self) -> NvdCve:
        return NvdCve(
            cve_id='TEST-1',
            last_mod=datetime.now(),
            data={
                'metrics': {
                    'cvssMetricV31': [{
                        'type': 'Primary',
                        'cvssData': {
                            'baseSeverity': 'MEDIUM',
                        },
                    }],
                },
            },
        )

    async def test_combine_base(self, db_session):
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='1', debsec_note=None, dist=dist_test))
        db_session.add(self.debsrc(dist=dist_test))
        db_session.add(self.nvd_cve())
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.cvss_severity is CvssSeverity.MEDIUM
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is False
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'cvssSeverity': 'MEDIUM',
                'versionEndExcluding': '1',
                'versionLatest': '1',
            },
            'vulnerable': False,
        }

    async def test_combine_base_vulnerable(self, db_session):
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='2', debsec_note=None, dist=dist_test))
        db_session.add(self.debsrc(dist=dist_test))
        db_session.add(self.nvd_cve())
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.cvss_severity is CvssSeverity.MEDIUM
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is True
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'cvssSeverity': 'MEDIUM',
                'versionEndExcluding': '2',
                'versionLatest': '1',
            },
            'vulnerable': True,
        }

    async def test_combine_fallback(self, db_session):
        dist_fallback = self.dist_mapper('')
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='1', debsec_note=None, dist=dist_fallback))
        db_session.add(self.debsrc(dist=dist_test))
        db_session.add(self.nvd_cve())
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.cvss_severity is CvssSeverity.MEDIUM
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is False
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'cvssSeverity': 'MEDIUM',
                'versionEndExcluding': '1',
                'versionLatest': '1',
            },
            'vulnerable': False,
        }

    async def test_combine_fallback_vulnerable(self, db_session):
        dist_fallback = self.dist_mapper('')
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='2', debsec_note=None, dist=dist_fallback))
        db_session.add(self.debsrc(dist=dist_test))
        db_session.add(self.nvd_cve())
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.cvss_severity is CvssSeverity.MEDIUM
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is True
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'cvssSeverity': 'MEDIUM',
                'versionEndExcluding': '2',
                'versionLatest': '1',
            },
            'vulnerable': True,
        }

    async def test_combine_unimportant(self, db_session):
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='1', debsec_note='unimportant', dist=dist_test))
        db_session.add(self.debsrc(dist=dist_test))
        db_session.add(self.nvd_cve())
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.cvss_severity is CvssSeverity.UNIMPORTANT
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is False
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'cvssSeverity': 'UNIMPORTANT',
                'versionEndExcluding': '1',
                'versionLatest': '1',
            },
            'vulnerable': False,
        }
