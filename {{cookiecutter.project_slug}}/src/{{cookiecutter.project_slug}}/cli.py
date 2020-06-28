#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m {{cookiecutter.project_slug}}` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``{{cookiecutter.project_slug}}.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``{{cookiecutter.project_slug}}.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
{%- if cookiecutter.command_line_interface == 'Click' %}
from typing import Tuple

import click
{%- elif cookiecutter.command_line_interface == 'Argparse' %}
import argparse
from typing import Optional, Sequence
{%- endif %}


{%- if cookiecutter.command_line_interface == 'Click' %}


@click.command()
@click.argument('args', nargs=-1)
def main(args: Tuple[str]) -> None:
    click.echo(repr(args))
{%- elif cookiecutter.command_line_interface == 'Argparse' %}

def _construct_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description='My python package.')
    parser.add_argument(
        'args',
        metavar='Arguments',
        nargs=argparse.ZERO_OR_MORE,
        help="Command line Arguments.",
    )
    return parser


def main(args: Optional[Sequence[str]] = None) -> None:
    print(_construct_parser().parse_args(args=args).args)
{%- endif %}


if __name__ == "__main__":
    main()
