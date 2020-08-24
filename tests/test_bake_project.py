# coding: utf-8

"""
Unit Tests for cookie cutter template

Copyright (c) Audrey Roy Greenfeld and individual contributors.
All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    1. Redistributions of source code must retain the above copyright notice,
       this list of conditions and the following disclaimer.

    2. Redistributions in binary form must reproduce the above copyright
       notice, this list of conditions and the following disclaimer in the
       documentation and/or other materials provided with the distribution.

    3. Neither the name of Audrey Roy Greenfeld nor the names of its
       contributors may be used to endorse or promote products derived from this
       software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
 LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

import datetime
import os
import shlex
import subprocess
import sys
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, Iterable, Iterator, Optional, Tuple

from _pytest.capture import CaptureFixture

# import yaml
from click.testing import CliRunner
from helper_functions import (
    bake_in_temp_dir,
    check_output_inside_dir,
    get_cli,
    project_info,
    run_inside_dir,
)
from hypothesis import example, given
from hypothesis import strategies as st
from py._path.local import LocalPath  # Decprecated(?): replace with pathlib later.
from pytest import mark, raises
from pytest_cookies.plugin import Cookies, Result


def test_year_compute_in_license_file(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies) as result:
        license_file_path: LocalPath = result.project.join("LICENSE")
        now: datetime.datetime = datetime.datetime.now()
        assert str(now.year) in license_file_path.read()


def test_bake_with_defaults(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies) as result:
        assert result.project.isdir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = [f.basename for f in result.project.listdir()]
        assert "setup.py" in found_toplevel_files
        assert "tox.ini" in found_toplevel_files
        assert "docs" in found_toplevel_files
        assert "src" in found_toplevel_files
        assert "tests" in found_toplevel_files
        assert "my_python_package" in os.listdir(
            os.path.join(str(result.project), "src")
        )


def test_bake_without_author_file(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies, extra_context={"create_author_file": "n"}) as result:
        found_toplevel_files = [f.basename for f in result.project.listdir()]
        assert "AUTHORS.rst" not in found_toplevel_files
        # doc_files = [f.basename for f in result.project.join('docs').listdir()]
        # assert 'authors.rst' not in doc_files

        # # Assert there are no spaces in the toc tree
        # docs_index_path = result.project.join('docs/index.rst')
        # with open(str(docs_index_path)) as index_file:
        #     assert 'contributing\n   history' in index_file.read()

        # # Check that
        # manifest_path = result.project.join('MANIFEST.in')
        # with open(str(manifest_path)) as manifest_file:
        #     assert 'AUTHORS.rst' not in manifest_file.read()


# def test_make_help(cookies):
#     with bake_in_temp_dir(cookies) as result:
#         # The supplied Makefile does not support win32
#         if sys.platform != "win32":
#             output = check_output_inside_dir('make help', str(result.project))
#             assert b"check code coverage quickly with the default Python" in output


@mark.parametrize(
    "license_info",
    [
        ("MIT", "MIT"),
        ("Apache 2.0 License", "Licensed under the Apache License, Version 2.0"),
    ],
)
def test_bake_selecting_license(
    cookies: Cookies, license_info: Tuple[str, str]
) -> None:
    license: str
    target_string: str
    result: Result

    license, target_string = license_info
    with bake_in_temp_dir(cookies, extra_context={"license": license}) as result:
        assert target_string in result.project.join("LICENSE").read()
        assert license in result.project.join("setup.py").read()


def test_bake_other_license(cookies: Cookies) -> None:
    result: Result
    with bake_in_temp_dir(cookies, extra_context={"license": "Other"}) as result:
        found_toplevel_files: Iterable[str] = [
            f.basename for f in result.project.listdir()
        ]
        assert "setup.py" in found_toplevel_files
        assert "LICENSE" not in found_toplevel_files
        assert "License" not in result.project.join("README.markdown").read()


@mark.parametrize(
    "args",
    [
        ({"command_line_interface": "Click"}, True),
        ({"command_line_interface": "Argparse"}, True),
        ({"command_line_interface": "None"}, False),
    ],
)
def test_bake_cli(cookies: Cookies, args: Tuple[Dict[str, str], bool]) -> None:
    context: Dict[str, str]
    is_present: bool
    context, is_present = args

    result: Result = cookies.bake(extra_context=context)
    project_path, _, project_dir = project_info(result)
    found_project_files: Iterable[str] = os.listdir(project_dir)
    assert ("cli.py" in found_project_files) == is_present

    setup_path: str = os.path.join(project_path, 'setup.py')
    with open(setup_path, 'r') as setup_file:
        assert ("entry_points" in setup_file.read()) == is_present


@mark.hypothesis
def test_run_click_cli(cookies: Cookies) -> None:
    cli: ModuleType = get_cli(cookies, {"command_line_interface": "Click"})

    runner: CliRunner = CliRunner()

    help_result = runner.invoke(cli.main, ["--help"])  # type: ignore
    assert help_result.exit_code == 0
    assert "Show this message" in help_result.output

    @given(st.lists(st.text(alphabet=st.from_regex("^[^-]{1,2}.*", fullmatch=True))))
    @example([])
    @example([''])
    def helper_args_cli(args: Iterable[str]) -> None:
        arg_result: Result = runner.invoke(cli.main, args)  # type: ignore
        assert arg_result.exit_code == 0
        assert str(tuple(args)) == arg_result.output.strip()

    helper_args_cli()


@mark.hypothesis
def test_run_argparse_cli(cookies: Cookies, capsys: CaptureFixture) -> None:
    cli: ModuleType = get_cli(cookies, {"command_line_interface": "Argparse"})

    with raises(SystemExit):
        cli.main(["--help"])  # type: ignore
    assert "show this help message" in capsys.readouterr().out

    @given(st.lists(st.text(alphabet=st.from_regex("^[^-]{1,2}.*", fullmatch=True))))
    @example([])
    @example([''])
    def helper_args_cli(args: Iterable[str]) -> None:
        cli.main(args)  # type: ignore
        assert str(args) == capsys.readouterr().out.strip()

    helper_args_cli()


def test_bake_sphinx(cookies: Cookies) -> None:

    result: Result
    with bake_in_temp_dir(
        cookies, extra_context={"documentation_framework": "Sphinx"}
    ) as result:
        project_path: str = project_info(result)[0]
        root_files: Iterable[str] = os.listdir(project_path)

        assert "Pipfile" in root_files
        with open(os.path.join(project_path, "Pipfile"), 'r') as pipfile:
            lines: Iterable[str] = pipfile.read().splitlines()
            assert 'mkdocs = "*"' not in lines

            assert 'sphinx = ">=3.0"' in lines
            assert 'sphinx-rtd-theme = "*"' in lines

        assert "docs" in root_files
        assert "source" in os.listdir(os.path.join(project_path, "docs"))
        docs_source_dir_name: str = os.path.join(project_path, "docs", "source")
        docs_source_dir: Iterable[str] = os.listdir(docs_source_dir_name)

        assert "index.rst" in docs_source_dir
        assert "index.markdown" not in docs_source_dir

        assert "conf.py" in docs_source_dir
        with open(os.path.join(docs_source_dir_name, "conf.py"), 'r') as docs_setup:
            lines = docs_setup.read().splitlines()

            for extension in ["autodoc", "coverage", "viewcode", "napoleon"]:
                assert next((s for s in lines if extension in s), None)

            rtd_theme_init_line: Optional[str] = next(
                (s for s in lines if "sphinx_rtd_theme" in s), None
            )
            assert rtd_theme_init_line is not None

            rtd_theme_set_line: str = 'html_theme = "sphinx_rtd_theme"'
            assert rtd_theme_init_line != rtd_theme_set_line
            assert rtd_theme_set_line in lines


def test_bake_mkdocs(cookies: Cookies) -> None:

    result: Result
    with bake_in_temp_dir(
        cookies, extra_context={"documentation_framework": "MkDocs"}
    ) as result:
        project_path: str = project_info(result)[0]
        root_files: Iterable[str] = os.listdir(project_path)

        assert "Pipfile" in root_files
        with open(os.path.join(project_path, "Pipfile"), 'r') as pipfile:
            lines: Iterable[str] = pipfile.read().splitlines()

            assert 'sphinx = ">=3.0"' not in lines

            assert 'mkdocs-awesome-pages-plugin = "*"' in lines
            assert 'mkdocs = "*"' in lines
            assert 'mkdocs-material = "*"' in lines
            assert 'mkdocs-minify-plugin = "*"' in lines
            assert 'Pygments = "*"' in lines

        assert "docs" in root_files

        docs_dir_name: str = os.path.join(project_path, "docs")
        docs_dir: Iterable[str] = os.listdir(docs_dir_name)

        assert "mkdocs.yml" in docs_dir
        with open(os.path.join(docs_dir_name, "mkdocs.yml"), 'r') as docs_setup:
            lines = docs_setup.read().splitlines()

            for plugin in ["search", "minify", "awesome-pages", "codehilite"]:
                assert next((s for s in lines if plugin in s), None)

        assert "source" in docs_dir
        docs_source_dir: Iterable[str] = os.listdir(
            os.path.join(docs_dir_name, "source")
        )

        assert "conf.py" not in docs_source_dir
        assert "index.rst" not in docs_source_dir
        assert "index.markdown" in docs_source_dir


def test_bake_no_docs(cookies: Cookies) -> None:

    result: Result
    with bake_in_temp_dir(
        cookies, extra_context={"documentation_framework": "None"}
    ) as result:
        project_path: str = project_info(result)[0]
        root_files: Iterable[str] = os.listdir(project_path)

        assert "Pipfile" in root_files
        with open(os.path.join(project_path, "Pipfile"), 'r') as pipfile:
            lines: Iterable[str] = pipfile.read().splitlines()
            assert 'mkdocs = "*"' not in lines
            assert 'sphinx = "*"' not in lines

        assert "docs" not in root_files


@mark.slow
@mark.parametrize(
    "context",
    [
        {},
        {"full_name": 'name "quote" name', "documentation_framework": "Sphinx"},
        {"full_name": "O'connor", "documentation_framework": "Sphinx"},
        {"full_name": 'name "quote" name', "documentation_framework": "MkDocs"},
        {"full_name": "O'connor", "documentation_framework": "MkDocs"},
    ],
)
def test_bake_and_generate_docs(cookies: Cookies, context: Dict[str, str]) -> None:
    with bake_in_temp_dir(cookies, extra_context=context) as result:
        assert result.project.isdir()
        test_file_path = result.project.join("tests/test_my_python_package.py")
        assert "import pytest" in test_file_path.read()

        assert run_inside_dir("tox -e docs", str(result.project)) == 0


def test_bake_no_test_framework(cookies: Cookies) -> None:
    result: Result
    with bake_in_temp_dir(cookies, extra_context={"have_tests": "n"}) as result:
        project_path: str = project_info(result)[0]
        root_files: Iterable[str] = set(os.listdir(project_path))

        assert "pytest.ini" not in root_files

        assert "tests" not in root_files

        assert "src" in root_files
        assert "conftest.py" not in os.listdir(os.path.join(project_path, "src"))

        assert "mypy.ini" in root_files
        with open(os.path.join(project_path, "mypy.ini"), 'r') as mypy_config:
            assert not next(
                (s for s in mypy_config.read().splitlines() if "mypy-pytest" in s), None
            )

        assert "setup.py" in root_files
        with open(os.path.join(project_path, "setup.py"), 'r') as setup_config:
            assert not next(
                (
                    s
                    for s in setup_config.read().splitlines()
                    if 'test_suite="tests"' in s
                ),
                None,
            )

        assert "Pipfile" in root_files
        with open(os.path.join(project_path, "Pipfile"), 'r') as pipfile:
            lines: Iterable[str] = set(pipfile.read().splitlines())
            assert 'pytest = "*"' not in lines
            assert 'hypothesis = "*"' not in lines
            assert 'pytest-cov = "*"' not in lines


@mark.slow
def test_bake_and_run_tests(cookies: Cookies) -> None:
    result: Result
    with bake_in_temp_dir(cookies, extra_context={}) as result:
        project_path: str = project_info(result)[0]
        root_files: Iterable[str] = set(os.listdir(project_path))

        assert "pytest.ini" in root_files

        assert "tests" in root_files
        assert "test_my_python_package.py" in os.listdir(
            os.path.join(project_path, "tests")
        )

        assert "src" in root_files
        assert "conftest.py" in os.listdir(os.path.join(project_path, "src"))

        assert "mypy.ini" in root_files
        with open(os.path.join(project_path, "mypy.ini"), 'r') as mypy_config:
            assert next(
                (s for s in mypy_config.read().splitlines() if "mypy-pytest" in s), None
            )

        assert "setup.py" in root_files
        with open(os.path.join(project_path, "setup.py"), 'r') as setup_config:
            assert next(
                (
                    s
                    for s in setup_config.read().splitlines()
                    if 'test_suite="tests"' in s
                ),
                None,
            )

        assert "Pipfile" in root_files
        with open(os.path.join(project_path, "Pipfile"), 'r') as pipfile:
            lines: Iterable[str] = set(pipfile.read().splitlines())
            assert 'pytest = "*"' in lines
            assert 'hypothesis = "*"' in lines
            assert 'pytest-cov = "*"' in lines

        tox_envs: str = ','.join(
            env
            for env in check_output_inside_dir(
                "tox --listenvs", str(result.project)
            ).split()
            if env.startswith("py3")
        )
        assert run_inside_dir("tox -e " + tox_envs, str(result.project)) == 0
