# SPDX-License-Identifier: MIT

from __future__ import annotations

from collections.abc import Collection

from ..database import DistCpe


class DistCpeMapper:
    cpe_vendor: str
    cpe_product: str

    def __call__(self, codename: str) -> DistCpe:
        raise NotImplementedError

    @staticmethod
    def keys() -> Collection[str]:
        return {
            'debian',
            'gardenlinux',
        }

    @staticmethod
    def new(match: str) -> DistCpeMapper:
        return {
            'debian': DistCpeMapperDebian,
            'gardenlinux': DistCpeMapperGardenlinux,
        }[match]()


class DistCpeMapperDebian(DistCpeMapper):
    cpe_vendor = 'debian'
    cpe_product = 'debian_linux'

    def __call__(self, codename: str) -> DistCpe:
        version: str = {
            'woody': '3.0',
            'sarge': '3.1',
            'etch': '4.0',
            'lenny': '5.0',
            'squeeze': '6.0',
            'wheezy': '7',
            'jessie': '8',
            'stretch': '9',
            'buster': '10',
            'bullseye': '11',
            'bookworm': '12',
            'trixie': '13',
            'forky': '14',
            '': '',
        }[codename]
        return DistCpe(
            cpe_vendor='debian',
            cpe_product='debian_linux',
            cpe_version=version,
            deb_codename=codename,
        )


class DistCpeMapperGardenlinux(DistCpeMapper):
    cpe_vendor = 'sap'
    cpe_product = 'gardenlinux'

    def __call__(self, codename: str) -> DistCpe:
        return DistCpe(
            cpe_vendor='sap',
            cpe_product='gardenlinux',
            cpe_version=codename,
            deb_codename=codename,
        )
