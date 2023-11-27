# SPDX-License-Identifier: MIT

from __future__ import annotations

import re
from typing import TextIO

from ..database import DebsecCve


class DebsecCveFile(dict[str, dict[tuple[str, str], DebsecCve]]):
    __re = re.compile(r'''
        ^(?:
            (?P<id>[A-Z0-9-]+)
            (?:\s+[\[(].*?[\])])?
            |
            \s+
            (?:
                (?:REJECTED|RESERVED|NOT-FOR-US|TODO|NOTE)(?::\s.*)?
                |
                \{.*\}
                |
                (?:\[(?P<codename>\S+)\]\s+)?
                -\s+
                (?P<source>[a-zA-Z0-9.+-]+)\s+
                (?:
                    \<(?P<tag>[a-z-]+)\>
                    |
                    (?P<version_fixed>[A-Za-z0-9.+~:-]+)
                )
                (?:\s+\((?P<note>.*?)\))?
            )
        )$
    ''', re.VERBOSE)

    def _read_source(self, cve_id: str, match: re.Match) -> None:
        per_codename = self.setdefault(match['codename'] or '', {})

        # We don't care if a package does not exist or is not affected
        if (tag := match['tag']) in ('removed', 'not-affected'):
            return

        per_codename[cve_id, match['source']] = DebsecCve(
            cve_id=cve_id,
            dist=None,
            deb_source=match['source'],
            deb_version_fixed=match['version_fixed'],
            debsec_tag=tag,
            debsec_note=match['note'],
        )

    def read(self, f: TextIO) -> None:
        for line in f.readlines():
            if match := self.__re.match(line):
                if i := match['id']:
                    current_id = i
                elif match['source']:
                    self._read_source(current_id, match)
            else:
                raise RuntimeError(f'Unable to read line: {line}')


if __name__ == '__main__':
    import sys

    d = DebsecCveFile()
    with open(sys.argv[1]) as f:
        d.read(f)

    for codename, entries in d.items():
        print(f'Codename: {codename}')
        for entry in entries.values():
            print(f'  {entry!r}')
