# SPDX-License-Identifier: MIT

from io import StringIO

from glvd.data.debsrc import DebsrcFile


class TestDebsrcFile:
    case = StringIO('''\
Package: test1
Version: 1
Format: 3.0 (quilt)
Files:
 abcde 1 test1_1.dsc
Package-List:
 test1 deb devel optional arch=any

Package: test1
Version: 1extra
Extra-Source-Only: yes
Format: 3.0 (quilt)
Files:
 abcde 1 test2_2.dsc
Package-List:
 hello deb devel optional arch=any

Package: test2
Version: 2
Format: 3.0 (quilt)
Files:
 abcde 1 test2_2.dsc
Package-List:
 hello deb devel optional arch=any
''')

    def test_read(self):
        f = DebsrcFile()
        f.read(self.case)

        assert f.keys() == {'test1', 'test2'}
        assert f['test1'].deb_source == 'test1'
        assert f['test1'].deb_version == '1'
        assert f['test2'].deb_source == 'test2'
        assert f['test2'].deb_version == '2'
