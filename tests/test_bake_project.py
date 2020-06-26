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
from importlib import util
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Any, Dict, Iterable, Iterator, Tuple

# import yaml
from click.testing import CliRunner
from cookiecutter.utils import rmtree
from py._path.local import LocalPath  # Decprecated: replace with pathlib later.
from pytest_cookies.plugin import Cookies, Result


@contextmanager
def inside_dir(dirpath) -> Iterator[None]:
    """
    Execute code from inside the given directory
    :param dirpath: String, path of the directory the command is being run.
    """
    # print(type(dirpath))
    old_path = os.getcwd()
    try:
        os.chdir(dirpath)
        yield
    finally:
        os.chdir(old_path)


@contextmanager
def bake_in_temp_dir(cookies: Cookies, *args: Any, **kwargs: Dict[str, str]) -> Result:
    """
    Delete the temporal directory that is created when executing the tests
    :param cookies: pytest_cookies.Cookies,
        cookie to be baked and its temporal files will be removed
    """
    result = cookies.bake(*args, **kwargs)
    # print('=' * 80 + '\n', "Result info:", repr(result), '\n' + ('=' * 80))
    try:
        yield result
    finally:
        rmtree(str(result.project))


def run_inside_dir(command: str, dirpath: str):
    """
    Run a command from inside a given directory, returning the exit status
    :param command: Command that will be executed
    :param dirpath: String, path of the directory the command is being run.
    """
    with inside_dir(dirpath):
        return_val = subprocess.check_call(shlex.split(command))
        # print(type(return_val))
        return return_val


def check_output_inside_dir(command, dirpath):
    "Run a command from inside a given directory, returning the command output"
    with inside_dir(dirpath):
        return subprocess.check_output(shlex.split(command))


def test_year_compute_in_license_file(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies) as result:
        license_file_path: LocalPath = result.project.join('LICENSE')
        now: datetime.datetime = datetime.datetime.now()
        assert str(now.year) in license_file_path.read()


def project_info(result: Result) -> Tuple[str, str, str]:
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = str(result.project)
    project_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, "src", project_slug)
    return project_path, project_slug, project_dir


def test_bake_with_defaults(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies) as result:
        assert result.project.isdir()
        assert result.exit_code == 0
        assert result.exception is None

        found_toplevel_files = [f.basename for f in result.project.listdir()]
        assert 'setup.py' in found_toplevel_files
        assert 'tox.ini' in found_toplevel_files
        assert 'tests' in found_toplevel_files
        assert 'src' in found_toplevel_files
        assert 'my_python_package' in os.listdir(
            os.path.join(str(result.project), "src")
        )


# def test_bake_and_run_tests(cookies):
#     with bake_in_temp_dir(cookies) as result:
#         assert result.project.isdir()
#         run_inside_dir('python setup.py test', str(result.project)) == 0
#         print("test_bake_and_run_tests path", str(result.project))


# def test_bake_withspecialchars_and_run_tests(cookies):
#     """Ensure that a `full_name` with double quotes does not break setup.py"""
#     with bake_in_temp_dir(
#         cookies, extra_context={'full_name': 'name "quote" name'}
#     ) as result:
#         assert result.project.isdir()
#         run_inside_dir('python setup.py test', str(result.project)) == 0


# def test_bake_with_apostrophe_and_run_tests(cookies):
#     """Ensure that a `full_name` with apostrophes does not break setup.py"""
#     with bake_in_temp_dir(cookies, extra_context={'full_name': "O'connor"}) as result:
#         assert result.project.isdir()
#         run_inside_dir('python setup.py test', str(result.project)) == 0


# def test_bake_without_author_file(cookies):
#     with bake_in_temp_dir(cookies, extra_context={'create_author_file': 'n'}) as result:
#         found_toplevel_files = [f.basename for f in result.project.listdir()]
#         assert 'AUTHORS.rst' not in found_toplevel_files
#         doc_files = [f.basename for f in result.project.join('docs').listdir()]
#         assert 'authors.rst' not in doc_files

#         # Assert there are no spaces in the toc tree
#         docs_index_path = result.project.join('docs/index.rst')
#         with open(str(docs_index_path)) as index_file:
#             assert 'contributing\n   history' in index_file.read()

#         # Check that
#         manifest_path = result.project.join('MANIFEST.in')
#         with open(str(manifest_path)) as manifest_file:
#             assert 'AUTHORS.rst' not in manifest_file.read()


# def test_make_help(cookies):
#     with bake_in_temp_dir(cookies) as result:
#         # The supplied Makefile does not support win32
#         if sys.platform != "win32":
#             output = check_output_inside_dir('make help', str(result.project))
#             assert b"check code coverage quickly with the default Python" in output


def test_bake_selecting_license(cookies: Cookies) -> None:
    license_strings: Dict[str, str] = {
        'MIT License': 'MIT',
        'Apache 2.0 License': 'Licensed under the Apache License, Version 2.0',
    }

    license: str
    target_string: str
    for license, target_string in license_strings.items():
        with bake_in_temp_dir(cookies, extra_context={'license': license}) as result:
            assert target_string in result.project.join('LICENSE').read()
            assert license in result.project.join('setup.py').read()


def test_bake_other_license(cookies: Cookies) -> None:
    result: Result
    with bake_in_temp_dir(cookies, extra_context={"license": "Other"}) as result:
        found_toplevel_files: Iterable[str] = [
            f.basename for f in result.project.listdir()
        ]
        assert 'setup.py' in found_toplevel_files
        assert 'LICENSE' not in found_toplevel_files
        assert 'License' not in result.project.join('README.markdown').read()


def test_using_pytest(cookies: Cookies) -> None:
    with bake_in_temp_dir(cookies, extra_context={'use_pytest': 'y'}) as result:
        # Test that the file was properly created
        assert result.project.isdir()
        test_file_path = result.project.join('tests/test_my_python_package.py')
        assert "import pytest" in ''.join(test_file_path.readlines())

        # # Test the new pytest target
        # run_inside_dir('python setup.py pytest', str(result.project)) == 0

        # # Test the test alias (which invokes pytest)
        # run_inside_dir('python setup.py test', str(result.project)) == 0


# def test_project_with_hyphen_in_module_name(cookies):
#     result = cookies.bake(
#         extra_context={'project_name': 'something-with-a-dash'}
#     )
#     assert result.project is not None
#     project_path = str(result.project)
#
#     # when:
#     travis_setup_cmd = ('python travis_pypi_setup.py'
#                         ' --repo audreyr/cookiecutter-pypackage'
#                         ' --password invalidpass')
#     run_inside_dir(travis_setup_cmd, project_path)
#
#     # then:
#     result_travis_config = yaml.load(
#         open(os.path.join(project_path, ".travis.yml"))
#     )
#     assert "secure" in result_travis_config["deploy"]["password"],\
#         "missing password config in .travis.yml"


def test_bake_with_no_console_script(cookies: Cookies) -> None:
    context: Dict[str, str] = {'command_line_interface': "None"}
    result: Result = cookies.bake(extra_context=context)
    project_path, _, project_dir = project_info(result)
    found_project_files: Iterable[str] = os.listdir(project_dir)
    assert "cli.py" not in found_project_files

    setup_path: str = os.path.join(project_path, 'setup.py')
    with open(setup_path, 'r') as setup_file:
        assert 'entry_points' not in setup_file.read()


def helper_bake_with_console_script_files(
    cookies: Cookies, context: Dict[str, str]
) -> None:
    result: Result = cookies.bake(extra_context=context)
    project_path, _, project_dir = project_info(result)
    found_project_files: Iterable[str] = os.listdir(project_dir)
    assert "cli.py" in found_project_files

    setup_path: str = os.path.join(project_path, 'setup.py')
    with open(setup_path, 'r') as setup_file:
        assert 'entry_points' in setup_file.read()


def test_bake_with_click_console_script_files(cookies: Cookies) -> None:
    helper_bake_with_console_script_files(cookies, {'command_line_interface': 'click'})


def test_bake_with_argparse_console_script_files(cookies: Cookies) -> None:
    helper_bake_with_console_script_files(
        cookies, {'command_line_interface': 'argparse'}
    )


def helper_bake_with_console_script_cli(
    cookies: Cookies, context: Dict[str, str]
) -> None:
    result: Result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(result)
    module_path: str = os.path.join(project_dir, 'cli.py')
    module_name: str = '.'.join([project_slug, 'cli'])
    spec: ModuleSpec = util.spec_from_file_location(module_name, module_path)
    cli: ModuleType = util.module_from_spec(spec)

    assert spec.loader is not None
    spec.loader.exec_module(cli)  # type: ignore
    runner: CliRunner = CliRunner()
    noarg_result: Result = runner.invoke(cli.main)  # type: ignore
    assert noarg_result.exit_code == 0
    # noarg_output: str = ' '.join(
    #     ['Replace this message by putting your code into', project_slug]
    # )
    # assert noarg_output in noarg_result.output
    help_result = runner.invoke(cli.main, ['--help'])  # type: ignore
    assert help_result.exit_code == 0
    assert 'Show this message' in help_result.output


def test_bake_with_click_console_script_cli(cookies: Cookies) -> None:
    helper_bake_with_console_script_cli(cookies, {'command_line_interface': 'click'})


def test_bake_with_argparse_console_script_cli(cookies: Cookies) -> None:
    helper_bake_with_console_script_cli(cookies, {'command_line_interface': 'argparse'})
