# SPDX-License-Identifier: MIT

from __future__ import annotations

import dataclasses
import re
from enum import StrEnum
from typing import Any


class CpePart(StrEnum):
    APPLICATION = 'a'
    OS = 'o'
    HARDWARE = 'h'


@dataclasses.dataclass
class CpeOtherDebian:
    deb_source: str | None = dataclasses.field(default=None)
    deb_version: str | None = dataclasses.field(default=None)

    @classmethod
    def parse(cls, i: str) -> str | CpeOtherDebian | None:
        try:
            kw: dict[str, str | None] = {}
            for f in i.split(','):
                k, v = f.split('=', 1)
                kw[k] = v
            return cls(**kw)
        except ValueError:
            return cls()

    def __str__(self) -> str:
        m: list[str] = []
        allany: bool = True

        for field in dataclasses.fields(self):
            if j := getattr(self, field.name):
                m.append(f'{field.name}={j}')
                allany = False

        if allany:
            return '*'
        else:
            return ','.join(m)


@dataclasses.dataclass
class Cpe:
    PART = CpePart

    part: CpePart | None = dataclasses.field(default=None, metadata={'factory': CpePart})
    vendor: str | None = dataclasses.field(default=None)
    product: str | None = dataclasses.field(default=None)
    version: str | None = dataclasses.field(default=None)
    update: str | None = dataclasses.field(default=None)
    lang: str | None = dataclasses.field(default=None)
    sw_edition: str | None = dataclasses.field(default=None)
    target_sw: str | None = dataclasses.field(default=None)
    target_hw: str | None = dataclasses.field(default=None)
    other: str | CpeOtherDebian | None = dataclasses.field(default=None)
    is_debian: bool = dataclasses.field(init=False, default=False)

    __re = re.compile(r'''
        ^cpe:2.3:
        (?P<part>[hoa*-])
        (?<!\\):
        (?P<vendor>.*?)
        (?<!\\):
        (?P<product>.*?)
        (?<!\\):
        (?P<version>.*?)
        (?<!\\):
        (?P<update>.*?)
        (?<!\\):
        # Field "edition" should not be used
        \*:
        (?P<lang>.*?)
        (?<!\\):
        (?P<sw_edition>.*?)
        (?<!\\):
        (?P<target_sw>.*?)
        (?<!\\):
        (?P<target_hw>.*?)
        (?<!\\):
        (?P<other>.*?)
        $
    ''', re.VERBOSE | re.IGNORECASE)

    __re_quote = re.compile(r'''([!"#$%&'()+,/:;<=>@[\]^`{|}~])''')
    __re_unquote = re.compile(r'''\\([!"#$%&'()+,/:;<=>@[\]^`{|}~])''')

    def __post_init__(self) -> None:
        if (self.part, self.vendor, self.product) in [
            (CpePart.OS, 'debian', 'debian_linux'),
            (CpePart.OS, 'sap', 'gardenlinux'),
        ]:
            self.is_debian = True
            if isinstance(self.other, str):
                self.other = CpeOtherDebian.parse(self.other)
            elif self.other is None:
                self.other = CpeOtherDebian()

    @classmethod
    def _parse_one(cls, field: dataclasses.Field, v: str, /) -> Any:
        if v == '*':
            return None
        else:
            return field.metadata.get('factory', str)(cls.__re_unquote.sub(r'\1', v))

    @classmethod
    def parse(cls, v: str, /) -> Cpe:
        if match := cls.__re.match(v):
            part: CpePart | None
            kw: dict[str, str | None] = {}
            for field in dataclasses.fields(cls):
                if field.init:
                    if field.name == 'part':
                        part = cls._parse_one(field, match.group(field.name))
                    else:
                        kw[field.name] = cls._parse_one(field, match.group(field.name))
            return cls(part=part, **kw)

        raise ValueError(f'Unable to read CPE: {v}')

    def __str__(self) -> str:
        m: dict[str, str] = {}
        for field in dataclasses.fields(self):
            j = getattr(self, field.name)
            if j is None:
                m[field.name] = '*'
            else:
                m[field.name] = self.__re_quote.sub(r'\\\1', str(j))
        return 'cpe:2.3:{part}:{vendor}:{product}:{version}:{update}:*:{lang}:{sw_edition}:{target_sw}:{target_hw}:{other}'.format(**m)


if __name__ == '__main__':
    import sys

    for i in sys.argv[1:]:
        c = Cpe.parse(i)
        print(str(c))
        print(repr(c))
