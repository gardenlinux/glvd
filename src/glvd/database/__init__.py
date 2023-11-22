# SPDX-License-Identifier: MIT

from __future__ import annotations

from datetime import datetime
from typing import (
    Any,
    Optional,
    Self,
)

from sqlalchemy import ForeignKey
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    MappedAsDataclass,
    mapped_column,
    relationship,
)
from sqlalchemy.sql import func
from sqlalchemy.types import (
    DateTime,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB


class Base(MappedAsDataclass, DeclarativeBase):
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


class DistCpe(Base):
    __tablename__ = 'dist_cpe'

    id: Mapped[int] = mapped_column(init=False, primary_key=True)
    cpe_vendor: Mapped[str]
    cpe_product: Mapped[str]
    cpe_version: Mapped[str]
    deb_codename: Mapped[str]


class Debsrc(Base):
    __tablename__ = 'debsrc'

    dist_id = mapped_column(ForeignKey(DistCpe.id), primary_key=True)
    last_mod: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
    deb_source: Mapped[str] = mapped_column(primary_key=True)
    deb_version: Mapped[str]

    dist: Mapped[Optional[DistCpe]] = relationship(lazy='selectin', default=None)

    def merge(self, other: Self) -> None:
        self.deb_version = other.deb_version


class DebsecCve(Base):
    __tablename__ = 'debsec_cve'

    dist_id = mapped_column(ForeignKey(DistCpe.id), primary_key=True)
    cve_id: Mapped[str] = mapped_column(primary_key=True)
    last_mod: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
    deb_source: Mapped[str] = mapped_column(primary_key=True)
    deb_version_fixed: Mapped[Optional[str]] = mapped_column(default=None)
    debsec_tag: Mapped[Optional[str]] = mapped_column(default=None)
    debsec_note: Mapped[Optional[str]] = mapped_column(default=None)

    dist: Mapped[Optional[DistCpe]] = relationship(lazy='selectin', default=None)

    def merge(self, other: Self) -> None:
        self.deb_version_fixed = other.deb_version_fixed
        self.debsec_tag = other.debsec_tag
        self.debsec_note = other.debsec_note


class DebCve(Base):
    __tablename__ = 'deb_cve'

    dist_id = mapped_column(ForeignKey(DistCpe.id), primary_key=True)
    cve_id: Mapped[str] = mapped_column(primary_key=True)
    last_mod: Mapped[datetime] = mapped_column(init=False, server_default=func.now(), onupdate=func.now())
    deb_source: Mapped[str] = mapped_column(primary_key=True)
    deb_version: Mapped[str]
    debsec_vulnerable: Mapped[bool]

    dist: Mapped[Optional[DistCpe]] = relationship(lazy='selectin', default=None)

    def merge(self, other: Self) -> None:
        self.deb_version = other.deb_version
        self.debsec_vulnerable = other.debsec_vulnerable
