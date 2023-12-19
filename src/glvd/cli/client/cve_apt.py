# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import json
import logging
import sys
import urllib.parse

from glvd.data.cvss import CvssSeverity
from glvd.util import requests
from . import cli


logger = logging.getLogger(__name__)


class ClientCveApt:
    server: str
    cvss3_severity_min: CvssSeverity

    @staticmethod
    @cli.register(
        'cve-apt',
        arguments=[
            cli.prepare_argument(
                '--cvss3-severity-min',
                choices=[i.name for i in CvssSeverity if i != CvssSeverity.NONE],
                default='LOW',
                help='only return CVE with at least this CVSS severity',
            ),
        ],
    )
    def run(*, argparser: argparse.ArgumentParser, cvss3_severity_min: str, server: str, debug: bool) -> None:
        logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)

        # Python-Apt is no PYPI reachable dependency, it only exists on Debian systems as package.
        try:
            import apt  # noqa: F401
        except ImportError:
            argparser.error('please install python3-apt')

        ClientCveApt(server, CvssSeverity[cvss3_severity_min])()

    def __init__(self, server: str, cvss3_severity_min: CvssSeverity) -> None:
        self.server = server
        self.cvss3_severity_min = cvss3_severity_min

    def get_sources(self) -> set[tuple[str, str, str, str]]:
        import apt

        ret = set()

        for pkg in apt.Cache():
            if inst := pkg.installed:
                for origin in inst.origins:
                    if origin.origin:
                        ret.add((origin.origin, origin.codename, inst.source_name, inst.source_version))

        return ret

    def request_data(self) -> dict[str, list[str]]:
        return {
            'source[]': [
                '_'.join(i)
                for i in sorted(self.get_sources())
            ],
        }

    def request_params(self) -> dict[str, str]:
        return {
            'cvssV3SeverityMin': self.cvss3_severity_min.name,
        }

    def __call__(self) -> None:
        with requests.RetrySession() as rsession:
            resp = rsession.post(
                urllib.parse.urljoin(self.server, 'v1/cves/findBySources'),
                params=self.request_params(),
                data=self.request_data(),
            )
            if resp.status_code == 200:
                data = resp.json()
                json.dump(data, sys.stdout, indent=2)
            else:
                resp.raise_for_status()


if __name__ == '__main__':
    ClientCveApt.run()
