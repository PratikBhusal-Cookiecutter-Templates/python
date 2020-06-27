# coding: utf-8

import os
import shlex
import subprocess
from contextlib import contextmanager
from types import ModuleType
from typing import Any, Dict, Iterator, Tuple


# import yaml
from cookiecutter.utils import rmtree
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


def project_info(result: Result) -> Tuple[str, str, str]:
    """Get toplevel dir, project_slug, and project dir from baked cookies"""
    project_path = str(result.project)
    project_slug = os.path.split(project_path)[-1]
    project_dir = os.path.join(project_path, "src", project_slug)
    return project_path, project_slug, project_dir