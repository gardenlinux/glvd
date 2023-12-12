# SPDX-License-Identifier: MIT

import pytest

from glvd.data.cpe import Cpe, CpePart


class TestCpe:
    def test_init(self):
        c = Cpe()

        assert c.part is None
        assert c.vendor is None
        assert c.product is None
        assert c.version is None
        assert c.update is None
        assert c.lang is None
        assert c.sw_edition is None
        assert c.target_sw is None
        assert c.target_hw is None
        assert c.other is None
        assert c.is_debian is False
        with pytest.raises(TypeError):
            c.other_debian

    def test_parse(self):
        s = r'cpe:2.3:h:a:b:c\:\%\*\;c:d:*:-:-:-:*:*'
        c = Cpe.parse(s)

        assert c.part is CpePart.HARDWARE
        assert c.vendor == 'a'
        assert c.product == 'b'
        assert c.version == 'c:%\\*;c'
        assert c.update == 'd'
        assert c.lang == '-'
        assert c.sw_edition == '-'
        assert c.target_sw == '-'
        assert c.target_hw is None
        assert c.other is None
        assert c.is_debian is False
        with pytest.raises(TypeError):
            c.other_debian
        assert str(c) == s

    def test_debian(self):
        s = r'cpe:2.3:o:debian:debian_linux:12:d:*:*:*:*:*:deb_source\=hello\,deb_version\=1'
        c = Cpe.parse(s)

        assert c.part is CpePart.OS
        assert c.vendor == 'debian'
        assert c.product == 'debian_linux'
        assert c.version == '12'
        assert c.update == 'd'
        assert c.lang is None
        assert c.sw_edition is None
        assert c.target_sw is None
        assert c.target_hw is None
        assert c.other_debian.deb_source == 'hello'
        assert c.other_debian.deb_version == '1'
        assert c.is_debian is True
        assert str(c) == s

    def test_debian_any(self):
        s = r'cpe:2.3:o:debian:debian_linux:12:d:*:*:*:*:*:*'
        c = Cpe.parse(s)

        assert c.other_debian.deb_source is None
        assert c.other_debian.deb_version is None
        assert c.is_debian is True
        assert str(c) == s
