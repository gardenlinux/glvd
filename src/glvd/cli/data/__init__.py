# SPDX-License-Identifier: MIT

from __future__ import annotations

from ..registry import CliRegistry


cli = CliRegistry('glvd-data')

cli.add_argument(
    '--database',
    default='postgresql+asyncpg:///',
    help='the database to use, must use asyncio compatible SQLAlchemy driver',
)
cli.add_argument(
    '--debug',
    action='store_true',
    help='enable debug output',
)
