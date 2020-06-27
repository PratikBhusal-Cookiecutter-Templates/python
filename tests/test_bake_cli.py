# coding: utf-8

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

from click import ClickException

# import yaml
from click.testing import CliRunner
from cookiecutter.utils import rmtree
from hypothesis import assume, given
from hypothesis import strategies as st
from py._path.local import LocalPath  # Decprecated: replace with pathlib later.
from pytest_cookies.plugin import Cookies, Result
from pytest import mark

from helper_functions import project_info


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


def helper_bake__cli_tool(cookies: Cookies, context: Dict[str, str]) -> ModuleType:
    result: Result = cookies.bake(extra_context=context)
    project_path, project_slug, project_dir = project_info(result)
    module_path: str = os.path.join(project_dir, 'cli.py')
    module_name: str = '.'.join([project_slug, 'cli'])
    spec: ModuleSpec = util.spec_from_file_location(module_name, module_path)
    cli: ModuleType = util.module_from_spec(spec)

    assert spec.loader is not None
    spec.loader.exec_module(cli)  # type: ignore

    return cli


def helper_no_args_cli(cli: ModuleType) -> None:
    runner: CliRunner = CliRunner()
    noarg_result: Result = runner.invoke(cli.main)  # type: ignore
    assert noarg_result.exit_code == 0
    assert "()" == noarg_result.output.strip()

    help_result = runner.invoke(cli.main, ['--help'])  # type: ignore
    assert help_result.exit_code == 0
    assert 'Show this message' in help_result.output


@given(args=st.lists(st.text(alphabet=st.characters(blacklist_characters=['-']))))
def helper_args_cli(cli: ModuleType, args: Iterable[str]) -> None:
    runner: CliRunner = CliRunner()
    noarg_result: Result = runner.invoke(cli.main, args)  # type: ignore
    try:
        assert noarg_result.exit_code == 0
    except AssertionError as e:
        # print("=" * 80)
        # print("Reached exception location")
        # print("Args:", args)
        # ClickException.show(str(e))
        # print("=" * 80)
        print(noarg_result.output)
        raise e
    assert str(tuple(args)) == noarg_result.output.strip()


def helper_help_message_cli(cli: ModuleType) -> None:
    runner: CliRunner = CliRunner()

    help_result: Result = runner.invoke(cli.main, ['--help'])  # type: ignore
    assert help_result.exit_code == 0
    assert 'Show this message' in help_result.output


@mark.hypothesis
def test_bake_click_cli(cookies: Cookies) -> None:
    cli: ModuleType = helper_bake__cli_tool(
        cookies, {'command_line_interface': 'click'}
    )

    helper_no_args_cli(cli)
    helper_args_cli(cli)
    helper_help_message_cli(cli)


@mark.hypothesis
def test_bake_with_argparse__cli(cookies: Cookies) -> None:
    cli: ModuleType = helper_bake__cli_tool(
        cookies, {'command_line_interface': 'argparse'}
    )

    helper_no_args_cli(cli)
    helper_args_cli(cli)
    helper_help_message_cli(cli)
