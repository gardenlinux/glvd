# SPDX-License-Identifier: MIT

from sqlalchemy import select

from glvd.cli.ingest_debsec import IngestDebsec
from glvd.database import DebsecCve
from glvd.data.debsec_cve import DebsecCveFile


class TestIngestDebsec:
    async def test_import_cve(self, db_session):
        f = DebsecCveFile()
        f[''] = {
            ('TEST-1', 'hello'): DebsecCve(
                cve_id='TEST-1',
                deb_source='hello',
                deb_version_fixed='2',
            )
        }
        f['bookworm'] = {
            ('TEST-1', 'hello'): DebsecCve(
                cve_id='TEST-1',
                deb_source='hello',
                deb_version_fixed='1',
            )
        }

        ingest = IngestDebsec('debian', None)
        await ingest.import_cve_insert(db_session, f)

        r = (await db_session.execute(select(DebsecCve).order_by(DebsecCve.cve_id, DebsecCve.deb_version_fixed))).all()
        assert len(r) == 2
        t = r.pop(0)[0]
        assert t.cve_id == 'TEST-1'
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'hello'
        assert t.deb_version_fixed == '1'

        t = r.pop(0)[0]
        assert t.cve_id == 'TEST-1'
        assert t.dist.cpe_version == ''
        assert t.deb_source == 'hello'
        assert t.deb_version_fixed == '2'

        f[''] = {
            ('TEST-1', 'hello'): DebsecCve(
                cve_id='TEST-1',
                deb_source='hello',
                deb_version_fixed='3',
            )
        }

        await ingest.import_cve_update(db_session, f)

        r = (await db_session.execute(select(DebsecCve).order_by(DebsecCve.cve_id, DebsecCve.deb_version_fixed))).all()
        assert len(r) == 2
        t = r.pop(1)[0]
        assert t.cve_id == 'TEST-1'
        assert t.dist.cpe_version == ''
        assert t.deb_source == 'hello'
        assert t.deb_version_fixed == '3'
