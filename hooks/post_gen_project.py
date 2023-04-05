#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
import shutil
from os import path, remove

PROJECT_DIRECTORY: str = path.realpath(path.curdir)


def remove_file(filepath: str) -> None:
    remove(path.join(PROJECT_DIRECTORY, filepath))


if __name__ == "__main__":

    # if "{{ cookiecutter.create_author_file }}" != "y":
    #     remove_file("AUTHORS.rst")
    #     remove_file("docs/authors.rst")

    if "Nox" in "{{ cookiecutter.test_automation_tool }}":
        remove_file("tox.ini")
    else:
        remove_file("noxfile.py")

    if "None" in "{{ cookiecutter.command_line_interface }}":
        remove_file(path.join("src", "{{ cookiecutter.project_slug }}", "cli.py"))
        remove_file(path.join("src", "{{ cookiecutter.project_slug }}", "__main__.py"))

    if "{{ cookiecutter.have_tests }}" != "y":
        remove_file("pytest.ini")
        remove_file(path.join("src", "conftest.py"))
        shutil.rmtree(path.join(PROJECT_DIRECTORY, "tests"), ignore_errors=True)

    if "Other" == "{{ cookiecutter.license }}":
        remove_file("LICENSE")

    if "None" == "{{ cookiecutter.documentation_framework }}":
        shutil.rmtree(path.join(PROJECT_DIRECTORY, "docs"), ignore_errors=True)
    else:
        extension: str

        if "Sphinx" == "{{ cookiecutter.documentation_framework }}":
            extension = "markdown"
            remove_file(path.join("docs", "mkdocs.yml"))

            from html import unescape as unescape_chars

            full_name: str = unescape_chars("{{ cookiecutter.full_name | escape }}")

            if '"' in full_name:
                import fileinput
                import sys

                with fileinput.input(
                    path.join(PROJECT_DIRECTORY, "docs", "source", "conf.py"),
                    inplace=True,
                ) as f:
                    for line in f:
                        sys.stdout.write(
                            line.replace(f'"{full_name}"', f"'{full_name}'")
                        )
        elif "MkDocs" == "{{ cookiecutter.documentation_framework }}":
            extension = "rst"
            remove_file(path.join("docs", "source", "conf.py"))
            # for folder in ["_static", "_templates"]:
            #     shutil.rmtree(
            #         path.join(PROJECT_DIRECTORY, "docs", "source", folder),
            #         ignore_errors=True,
            #     )

        from glob import iglob

        for file_path in iglob(
            path.join(PROJECT_DIRECTORY, "docs", "source", "**/*." + extension),
            recursive=True,
        ):
            remove(file_path)
