# SPDX-License-Identifier: MIT

from __future__ import annotations

from ..registry import CliRegistry


cli = CliRegistry('glvd')

cli.add_argument(
    '--server',
    default='http://localhost:5000',
    help='the server to use',
)
cli.add_argument(
    '--debug',
    action='store_true',
    help='enable debug output',
)
