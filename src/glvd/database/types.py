# SPDX-License-Identifier: MIT

from __future__ import annotations

from sqlalchemy.types import (
    INT,
    TypeDecorator,
    UserDefinedType,
)

from ..data.cvss import CvssSeverity


class CvssSeverityType(TypeDecorator):
    cache_ok = True
    impl = INT

    def process_bind_param(self, value: CvssSeverity | None, dialect) -> int | None:
        if value is not None:
            return value.value
        return None

    def process_result_value(self, value: int | None, dialect) -> CvssSeverity | None:
        if value is not None:
            return CvssSeverity(value)
        return None


class DebVersion(UserDefinedType):
    cache_ok = True

    def get_col_spec(self, **kw) -> str:
        return 'debversion'
