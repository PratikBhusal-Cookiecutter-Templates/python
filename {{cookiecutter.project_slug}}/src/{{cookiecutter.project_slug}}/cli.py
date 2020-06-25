#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
from typing import Tuple

import click


@click.command()
@click.argument('names', nargs=-1)
def main(names: Tuple[str]) -> None:
    click.echo(repr(names))


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    main()
