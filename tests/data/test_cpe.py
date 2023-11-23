# SPDX-License-Identifier: MIT

from glvd.data.cpe import Cpe, CpePart


class TestCpe:
    def test_init(self):
        c = Cpe()

        assert c.part is Cpe.ANY
        assert c.vendor is Cpe.ANY
        assert c.product is Cpe.ANY
        assert c.version is Cpe.ANY
        assert c.update is Cpe.ANY
        assert c.lang is Cpe.ANY
        assert c.sw_edition is Cpe.ANY
        assert c.target_sw is Cpe.ANY
        assert c.target_hw is Cpe.ANY
        assert c.other is Cpe.ANY

    def test_parse(self):
        s = r'cpe:2.3:h:a:b:c\:\%\*\;c:d:*:-:-:-:*:*'
        c = Cpe.parse(s)

        assert c.part is CpePart.HARDWARE
        assert c.vendor == 'a'
        assert c.product == 'b'
        assert c.version == 'c:%\\*;c'
        assert c.update == 'd'
        assert c.lang is None
        assert c.sw_edition is None
        assert c.target_sw is None
        assert c.target_hw is Cpe.ANY
        assert c.other is Cpe.ANY
        assert str(c) == s

    def test_debian(self):
        s = r'cpe:2.3:o:debian:debian_linux:12:d:*:-:-:-:*:deb_source\=hello\,deb_version\=1'
        c = Cpe.parse(s)

        assert c.part is CpePart.OS
        assert c.vendor == 'debian'
        assert c.product == 'debian_linux'
        assert c.version == '12'
        assert c.update == 'd'
        assert c.lang is None
        assert c.sw_edition is None
        assert c.target_sw is None
        assert c.target_hw is Cpe.ANY
        assert c.other.deb_source == 'hello'
        assert c.other.deb_version == '1'
        assert str(c) == s
