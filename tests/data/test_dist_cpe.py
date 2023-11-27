# SPDX-License-Identifier: MIT

import pytest

from glvd.data.dist_cpe import DistCpeMapper


class TestDistCpeMapper:
    def test(self) -> None:
        with pytest.raises(NotImplementedError):
            DistCpeMapper()('')


class TestDistCpeMapperDebian:
    @pytest.mark.parametrize(
        'codename,version',
        [
            ('woody', '3.0'),
            ('sarge', '3.1'),
            ('etch', '4.0'),
            ('lenny', '5.0'),
            ('squeeze', '6.0'),
            ('wheezy', '7'),
            ('jessie', '8'),
            ('stretch', '9'),
            ('buster', '10'),
            ('bullseye', '11'),
            ('bookworm', '12'),
            ('trixie', '13'),
            ('forky', '14'),
            ('', ''),
        ],
    )
    def test_valid(self, codename: str, version: str) -> None:
        m = DistCpeMapper.new('debian')
        c = m(codename)

        assert c.cpe_vendor == 'debian'
        assert c.cpe_product == 'debian_linux'
        assert c.cpe_version == version
        assert c.deb_codename == codename

    def test_invalid(self) -> None:
        m = DistCpeMapper.new('debian')

        with pytest.raises(KeyError):
            m('invalid')


class TestDistCpeMapperGardenlinux:
    def test_valid(self) -> None:
        m = DistCpeMapper.new('gardenlinux')
        c = m('999.9')

        assert c.cpe_vendor == 'sap'
        assert c.cpe_product == 'gardenlinux'
        assert c.cpe_version == '999.9'
        assert c.deb_codename == '999.9'
