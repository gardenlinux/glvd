# SPDX-License-Identifier: MIT

import pytest

from glvd.database import AllCve


class TestNvdCve:
    @pytest.fixture(autouse=True, scope='class')
    async def setup_example(self, db_session_class):
        for i in range(2):
            db_session_class.add(AllCve(
                cve_id=f'TEST-{i}',
                data={
                    'id': f'TEST-{i}',
                },
            ))
        await db_session_class.flush()

    async def test_deb_cveid_simple(self, client):
        resp = await client.get(
            '/rest/json/cves/2.0+deb',
            query_string={
                'cveId': 'TEST-0',
            },
        )

        assert resp.status_code == 200
        assert (await resp.json) == {
            'format': 'NVD_CVE',
            'version': '2.0+deb',
            'vulnerabilities': [
                {
                    'cve': {
                        'id': 'TEST-0',
                    },
                },
            ],
        }

    async def test_deb_cveid_nonexist(self, client):
        resp = await client.get(
            '/rest/json/cves/2.0+deb',
            query_string={
                'cveId': 'TEST-NONEXIST',
            },
        )

        assert resp.status_code == 200
        assert (await resp.json) == {
            'format': 'NVD_CVE',
            'version': '2.0+deb',
            'vulnerabilities': []
        }
