# SPDX-License-Identifier: MIT

from __future__ import annotations

import argparse
import dataclasses
from collections.abc import (
    Callable,
    Iterable,
)


@dataclasses.dataclass
class _ActionWrapper:
    args: tuple
    kw: dict


class Cli:
    parser: argparse.ArgumentParser
    subparsers: argparse._SubParsersAction

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            allow_abbrev=False,
            prog='glvd',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )
        self.subparsers = self.parser.add_subparsers(
            help='sub-command help',
        )

    def add_argument(self, *args, **kw) -> _ActionWrapper:
        return _ActionWrapper(args, kw)

    def register(
        self,
        name: str,
        arguments: Iterable[_ActionWrapper],
        usage: str = '%(prog)s',
        epilog: str | None = None,
    ) -> Callable:
        parser_main = argparse.ArgumentParser(
            allow_abbrev=False,
            prog=f'glvd.{name}',
            usage=usage,
            epilog=epilog,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        parser_sub = self.subparsers.add_parser(
            name=name,
            usage=usage,
            epilog=epilog,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        )

        for p in (parser_main, parser_sub):
            for w in arguments:
                p.add_argument(*w.args, **w.kw)

        def wrap(func: Callable) -> Callable:
            parser_sub.set_defaults(func=func)

            def run() -> None:
                args = parser_main.parse_args()
                func(**vars(args))

            return run

        return wrap

    def main(self) -> None:
        args = self.parser.parse_args()
        v = vars(args)
        func = v.pop('func', None)
        if func:
            func(**v)
        else:
            self.parser.print_help()


cli = Cli()
