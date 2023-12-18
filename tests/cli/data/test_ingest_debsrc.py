# SPDX-License-Identifier: MIT

import pytest

from sqlalchemy import select

from glvd.cli.data.ingest_debsrc import IngestDebsrc
from glvd.database import Debsrc
from glvd.data.debsrc import DebsrcFile


@pytest.mark.incremental
class TestIngestDebsrc:
    async def test_import_insert(self, db_session_class):
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
        await ingest.import_insert(db_session_class, f)

        r = (await db_session_class.execute(select(Debsrc).order_by(Debsrc.deb_source))).all()
        assert len(r) == 2
        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test1'
        assert t.deb_version == '1'

        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test2'
        assert t.deb_version == '2'

    async def test_import_update(self, db_session_class):
        f = DebsrcFile()
        f['test1'] = Debsrc(
            deb_source='test1',
            deb_version='1',
        )
        f['test2'] = Debsrc(
            deb_source='test2',
            deb_version='3',
        )

        ingest = IngestDebsrc('debian', 'bookworm', None)
        await ingest.import_update(db_session_class, f)

        r = (await db_session_class.execute(select(Debsrc).order_by(Debsrc.deb_source))).all()
        assert len(r) == 2
        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test1'
        assert t.deb_version == '1'

        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test2'
        assert t.deb_version == '3'

    async def test_import_delete(self, db_session_class):
        f = DebsrcFile()
        f['test1'] = Debsrc(
            deb_source='test1',
            deb_version='1',
        )

        ingest = IngestDebsrc('debian', 'bookworm', None)
        await ingest.import_update(db_session_class, f)

        r = (await db_session_class.execute(select(Debsrc).order_by(Debsrc.deb_source))).all()
        assert len(r) == 1
        t = r.pop(0)[0]
        assert t.dist.cpe_version == '12'
        assert t.deb_source == 'test1'
        assert t.deb_version == '1'
