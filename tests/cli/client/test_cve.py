# SPDX-License-Identifier: MIT

from glvd.cli.client.cve import ClientCve


class TestIngestNvd:
    async def test_one(self, requests_mock):
        requests_mock.get(
            'http://localhost/v1/cves/TEST-0',
            json=[
                {
                    'id': 'TEST-0',
                    'lastModified': '2019-04-01T00:00:00',
                },
            ],
        )

        client = ClientCve(server='http://localhost')
        assert client(cve='TEST-0') is None
