# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import Any

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.types import DateTime, Text
from sqlalchemy.dialects.postgresql import JSONB


class Base(DeclarativeBase):
    type_annotation_map = {
        str: Text,
        datetime: DateTime(timezone=True),
        Any: JSONB,
    }


class NvdCve(Base):
    __tablename__ = 'nvd_cve'

    cve_id: Mapped[str] = mapped_column(primary_key=True)
    last_mod: Mapped[datetime]
    data: Mapped[Any]
