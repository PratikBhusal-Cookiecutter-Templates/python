#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import os

PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def remove_file(filepath):
    os.remove(os.path.join(PROJECT_DIRECTORY, filepath))


if __name__ == "__main__":

    if "{{ cookiecutter.create_author_file }}" != "y":
        remove_file("AUTHORS.rst")
        remove_file("docs/authors.rst")

    if "None" in "{{ cookiecutter.command_line_interface }}":
        cli_file = os.path.join("src", "{{ cookiecutter.project_slug }}", "cli.py")
        remove_file(cli_file)

    if "Other" == "{{ cookiecutter.license }}":
        remove_file("LICENSE")
