#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import shutil
from glob import iglob
from os import path, remove

PROJECT_DIRECTORY: str = path.realpath(path.curdir)


def remove_file(filepath: str) -> None:
    remove(path.join(PROJECT_DIRECTORY, filepath))


if __name__ == "__main__":

    # if "{{ cookiecutter.create_author_file }}" != "y":
    #     remove_file("AUTHORS.rst")
    #     remove_file("docs/authors.rst")

    if "None" in "{{ cookiecutter.command_line_interface }}":
        remove_file(path.join("src", "{{ cookiecutter.project_slug }}", "cli.py"))
        remove_file(path.join("src", "{{ cookiecutter.project_slug }}", "__main__.py"))

    if "Other" == "{{ cookiecutter.license }}":
        remove_file("LICENSE")

    if "None" == "{{ cookiecutter.documentation_framework }}":
        shutil.rmtree(path.join(PROJECT_DIRECTORY, "docs"), ignore_errors=True)
    else:
        extension: str

        if "Sphinx" == "{{ cookiecutter.documentation_framework }}":
            extension = "markdown"
            remove_file(path.join("docs", "mkdocs.yml"))
        elif "MkDocs" == "{{ cookiecutter.documentation_framework }}":
            extension = "rst"
            remove_file(path.join("docs", "source", "conf.py"))
            # for folder in ["_static", "_templates"]:
            #     shutil.rmtree(
            #         path.join(PROJECT_DIRECTORY, "docs", "source", folder),
            #         ignore_errors=True,
            #     )

        for file_path in iglob(
            path.join(PROJECT_DIRECTORY, "docs", "source", "**/*." + extension),
            recursive=True,
        ):
            remove(file_path)
