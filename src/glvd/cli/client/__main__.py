# SPDX-License-Identifier: MIT

from __future__ import annotations

from . import cli

# Import to register all the commands
from . import (  # noqa: F401
    cve,
    cve_apt,
)


def main() -> None:
    cli.main()


if __name__ == '__main__':
    main()
