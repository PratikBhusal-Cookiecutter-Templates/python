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
"""
Copyright (c) 2013-2019, Ionel Cristian Mărieș
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from typing import Tuple, Optional, Iterable
{%- if cookiecutter.command_line_interface == 'Click' %}
import click
{%- elif cookiecutter.command_line_interface == 'Argparse' %}
import argparse
{%- endif %}
{%- if cookiecutter.command_line_interface == 'Click' %}

@click.command()
@click.argument('args', nargs=-1)
def main(args: Tuple[str]) -> None:
    click.echo(repr(args))
{%- elif cookiecutter.command_line_interface == 'Argparse' %}

parser = argparse.ArgumentParser(description='My python package.')
parser.add_argument('args', metavar='Arguments', nargs=argparse.ZERO_OR_MORE,
                    help="Command line Arguments.")


def main(args: Optional[Iterable[str]] = None) -> None:
    args = parser.parse_args(args=args)
    print(args.names)
{%- endif %}
