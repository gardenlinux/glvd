# SPDX-License-Identifier: MIT

from sqlalchemy import select

from glvd.cli.combine_deb import CombineDeb
from glvd.data.dist_cpe import DistCpeMapper
from glvd.database import DistCpe, DebCve, DebsecCve, Debsrc


class TestIngestDebsrc:
    dist_mapper = DistCpeMapper.new('debian')

    def debsec_cve(self, *, deb_version_fixed: str, dist: DistCpe) -> DebsecCve:
        return DebsecCve(
            cve_id='TEST-1',
            deb_source='test',
            deb_version_fixed=deb_version_fixed,
            dist=dist,
        )

    def debsrc(self, *, dist: DistCpe) -> Debsrc:
        return Debsrc(
            deb_source='test',
            deb_version='1',
            dist=dist,
        )

    async def test_combine_base(self, db_session):
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='1', dist=dist_test))
        db_session.add(self.debsrc(dist=dist_test))
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is False
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'versionEndExcluding': '1',
                'versionLatest': '1',
            },
            'vulnerable': False,
        }

    async def test_combine_base_vulnerable(self, db_session):
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='2', dist=dist_test))
        db_session.add(self.debsrc(dist=dist_test))
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is True
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'versionEndExcluding': '2',
                'versionLatest': '1',
            },
            'vulnerable': True,
        }

    async def test_combine_fallback(self, db_session):
        dist_fallback = self.dist_mapper('')
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='1', dist=dist_fallback))
        db_session.add(self.debsrc(dist=dist_test))
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is False
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'versionEndExcluding': '1',
                'versionLatest': '1',
            },
            'vulnerable': False,
        }

    async def test_combine_fallback_vulnerable(self, db_session):
        dist_fallback = self.dist_mapper('')
        dist_test = self.dist_mapper('trixie')

        db_session.add(dist_test)
        db_session.add(self.debsec_cve(deb_version_fixed='2', dist=dist_fallback))
        db_session.add(self.debsrc(dist=dist_test))
        await db_session.flush()

        combine = CombineDeb()
        await combine.combine(db_session)

        r = (await db_session.execute(select(DebCve).order_by(DebCve.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist == dist_test
        assert t.deb_source == 'test'
        assert t.deb_version == '1'
        assert t.debsec_vulnerable is True
        assert t.data_cpe_match == {
            'criteria': r'cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
            'deb': {
                'versionEndExcluding': '2',
                'versionLatest': '1',
            },
            'vulnerable': True,
        }
