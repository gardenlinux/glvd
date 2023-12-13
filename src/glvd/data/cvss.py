# SPDX-License-Identifier: MIT

from __future__ import annotations

import enum


@enum.verify(enum.UNIQUE)
class CvssSeverity(enum.Enum):
    NONE = 0
    UNIMPORTANT = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    CRITICAL = 5

    @classmethod
    def from_score(cls, score: int) -> CvssSeverity:
        if score < 0 or score > 10:
            raise ValueError
        if score >= 9:
            return cls.CRITICAL
        if score >= 7:
            return cls.HIGH
        if score >= 4:
            return cls.MEDIUM
        if score > 0:
            return cls.LOW
        return cls.NONE
