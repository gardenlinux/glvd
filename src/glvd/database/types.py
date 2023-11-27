# SPDX-License-Identifier: MIT

from __future__ import annotations

from sqlalchemy.types import UserDefinedType


class DebVersion(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw) -> str:
        return 'debversion'
