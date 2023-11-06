# SPDX-License-Identifier: MIT

import requests
import requests.adapters
import urllib3


class RetrySession(requests.Session):
    def __init__(self) -> None:
        super().__init__()
        adapter = requests.adapters.HTTPAdapter(
            max_retries=urllib3.Retry(
                total=5,
                backoff_factor=1,
                allowed_methods=None,
                status_forcelist=[429, 500, 502, 503, 504],
            ),
        )
        self.mount("https://", adapter)
