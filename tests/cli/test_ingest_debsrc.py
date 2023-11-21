# SPDX-License-Identifier: MIT

from sqlalchemy import select

from glvd.cli.ingest_debsrc import IngestDebsrc
from glvd.database import Debsrc
from glvd.data.debsrc import DebsrcFile


class TestIngestDebsrc:
    async def test_import(self, db_session):
        f = DebsrcFile()
        f['test1'] = Debsrc(
            deb_source='test1',
            deb_version='1',
        )
        f['test2'] = Debsrc(
            deb_source='test2',
            deb_version='2',
        )

        ingest = IngestDebsrc('debian', 'bookworm', None)
        await ingest.import_insert(db_session, f)

        r = (await db_session.execute(select(Debsrc).order_by(Debsrc.deb_source))).all()
        assert len(r) == 2
        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test1'
        assert t.deb_version == '1'

        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test2'
        assert t.deb_version == '2'

        f['test2'] = Debsrc(
            deb_source='test2',
            deb_version='3',
        )

        await ingest.import_update(db_session, f)

        r = (await db_session.execute(select(Debsrc).order_by(Debsrc.deb_source))).all()
        assert len(r) == 2
        t = r.pop(1)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test2'
        assert t.deb_version == '3'
