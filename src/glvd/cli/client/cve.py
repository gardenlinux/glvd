# SPDX-License-Identifier: MIT

from __future__ import annotations

import json
import logging
import sys
import urllib.parse

from ...util import requests
from . import cli


logger = logging.getLogger(__name__)


class ClientCve:
    server: str

    @staticmethod
    @cli.register(
        'cve',
        arguments=[
            cli.prepare_argument(
                'cve',
                help='the CVE to look up',
                metavar='CVE',
            ),
        ]
    )
    def run(*, argparser: None, cve: str, server: str, debug: bool) -> None:
        logging.basicConfig(level=debug and logging.DEBUG or logging.INFO)
        ClientCve(server)(cve)

    def __init__(self, server: str) -> None:
        self.server = server

    def __call__(self, cve: str) -> None:
        with requests.RetrySession() as rsession:
            resp = rsession.get(
                urllib.parse.urljoin(self.server, f'v1/cves/{cve}'),
            )
            if resp.status_code == 200:
                data = resp.json()
                json.dump(data, sys.stdout, indent=2)
            elif resp.status_code == 404:
                print(f'{cve} not found', file=sys.stderr)
            else:
                resp.raise_for_status()


if __name__ == '__main__':
    ClientCve.run()
