# SPDX-License-Identifier: MIT

from io import StringIO

from glvd.data.debsec_cve import DebsecCveFile


class TestDebsecCveFile:
    case_fixed = StringIO('''\
CVE-2023-39323 ()
\t- golang-1.21 1.21.2-1
\t- golang-1.20 1.20.9-1
\t- golang-1.19 <unfixed>
\t[bookworm] - golang-1.19 <no-dsa> (Minor issue)
\t- golang-1.15 <removed>
\t[bullseye] - golang-1.15 <no-dsa> (Minor issue)
\t- golang-1.11 <removed>
\t[buster] - golang-1.11 <postponed> (Limited support, follow bullseye DSAs/point-releases)
\tNOTE: https://go.dev/issue/63211
''')

    def test_read_fixed(self):
        f = DebsecCveFile()
        f.read(self.case_fixed)

        assert f.keys() == {'', 'bookworm', 'bullseye', 'buster'}
        assert f[''].keys() == {
            ('CVE-2023-39323', 'golang-1.19'),
            ('CVE-2023-39323', 'golang-1.20'),
            ('CVE-2023-39323', 'golang-1.21'),
        }
        assert f['bookworm'].keys() == {
            ('CVE-2023-39323', 'golang-1.19'),
        }
        assert f['bullseye'].keys() == {
            ('CVE-2023-39323', 'golang-1.15'),
        }
        assert f['buster'].keys() == {
            ('CVE-2023-39323', 'golang-1.11'),
        }

    case_ignored = StringIO('''\
CVE-2023-45374 (Bla Bla ..)
\tNOT-FOR-US: MediaWiki extension
CVE-2023-45364
\tTODO: check
CVE-2023-31289
\tRESERVED
CVE-2023-5312
\tREJECTED
''')

    def test_read_ignored(self):
        f = DebsecCveFile()
        f.read(self.case_ignored)

        assert f == {}
