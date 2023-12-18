# SPDX-License-Identifier: MIT

from sqlalchemy import select

from glvd.cli.data.ingest_nvd import IngestNvd
from glvd.database import NvdCve


class TestIngestNvd:
    async def test_fetch_cve_empty(self, db_session, requests_mock):
        for i in range(2):
            requests_mock.get(
                f'https://services.nvd.nist.gov/rest/json/cves/2.0/?startIndex={i}',
                json={
                    'resultsPerPage': 1,
                    'startIndex': 0,
                    'totalResults': 2,
                    'format': 'NVD_CVE',
                    'version': '2.0',
                    'vulnerabilities': [
                        {
                            'cve': {
                                'id': f'TEST-{i}',
                                'lastModified': '2019-04-01T00:00:00',
                            },
                        },
                    ],
                },
            )

        requests_mock.get(
            'https://services.nvd.nist.gov/rest/json/cves/2.0/?startIndex=2',
            json={
                'resultsPerPage': 1,
                'startIndex': 2,
                'totalResults': 2,
                'format': 'NVD_CVE',
                'version': '2.0',
                'vulnerabilities': [],
            },
        )

        ingest = IngestNvd(wait=0)
        await ingest.fetch_cve(db_session)

        r = (await db_session.execute(select(NvdCve).order_by(NvdCve.cve_id))).all()
        assert len(r) == 2
        t = r.pop(0)[0]
        assert t.cve_id == 'TEST-0'
        t = r.pop(0)[0]
        assert t.cve_id == 'TEST-1'
