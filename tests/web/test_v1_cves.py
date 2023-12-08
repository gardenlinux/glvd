# SPDX-License-Identifier: MIT

import pytest

import json

from glvd.database import AllCve, DebCve, DistCpe


class TestCveId:
    @pytest.fixture(autouse=True, scope='class')
    async def setup_example(self, db_session_class):
        db_session_class.add(AllCve(
            cve_id='TEST-0',
            data={
                'id': 'TEST-0',
            },
        ))
        await db_session_class.flush()

    async def test_simple(self, client):
        resp = await client.get(
            '/v1/cves/TEST-0',
        )

        assert resp.status_code == 200
        assert json.loads((await resp.data)) == {
            'id': 'TEST-0',
        }

    async def test_nonexist(self, client):
        resp = await client.get(
            '/v1/cves/TEST-NONEXIST',
        )

        assert resp.status_code == 404


class TestCpeName:
    @pytest.fixture(autouse=True, scope='class')
    async def setup_example(self, db_session_class):
        for i in ('TEST-fixed', 'TEST-vuln'):
            db_session_class.add(AllCve(
                cve_id=i,
                data={
                    'id': i,
                },
            ))
        self.dist = DistCpe(
            cpe_vendor='debian',
            cpe_product='debian_linux',
            cpe_version='13',
            deb_codename='trixie',
        )
        db_session_class.add(self.dist)
        db_session_class.add(DebCve(
            cve_id='TEST-fixed',
            deb_source='test',
            deb_version='1',
            deb_version_fixed='1',
            debsec_vulnerable=False,
            dist=self.dist,
            data_cpe_match={},
        ))
        db_session_class.add(DebCve(
            cve_id='TEST-vuln',
            deb_source='test',
            deb_version='1',
            deb_version_fixed='2',
            debsec_vulnerable=True,
            dist=self.dist,
            data_cpe_match={},
        ))
        await db_session_class.flush()

    async def test_simple(self, client):
        resp = await client.get(
            r'/v1/cves/findByCpe?cpeName=cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:*',
        )

        assert resp.status_code == 200
        assert {i['id'] for i in json.loads((await resp.data))} == {
            'TEST-vuln',
        }

    async def test_source(self, client):
        resp = await client.get(
            r'/v1/cves/findByCpe?cpeName=cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test',
        )

        assert resp.status_code == 200
        assert {i['id'] for i in json.loads((await resp.data))} == {
            'TEST-vuln',
        }

    async def test_version(self, client):
        resp = await client.get(
            r'/v1/cves/findByCpe?cpeName=cpe:2.3:o:debian:debian_linux:13:*:*:*:*:*:*:deb_source\=test&debVersionEnd=0',
        )

        assert resp.status_code == 200
        assert {i['id'] for i in json.loads((await resp.data))} == {
            'TEST-fixed',
            'TEST-vuln',
        }

    async def test_nonexist(self, client):
        resp = await client.get(
            r'/v1/cves/findByCpe?cpeName=cpe:2.3:o:debian:debian_linux:14:*:*:*:*:*:*:*',
        )

        assert resp.status_code == 200
        assert json.loads((await resp.data)) == []
