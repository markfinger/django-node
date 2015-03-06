import os
import subprocess
from .exceptions import NpmInstallArgumentsError
from .settings import PATH_TO_NPM, NPM_INSTALL_PATH_TO_PYTHON, NPM_INSTALL_COMMAND
from .utils import (
    NPM_NAME, npm_installed, npm_version, npm_version_raw, raise_if_dependency_missing,
    raise_if_dependency_version_less_than, run_command
)

is_installed = npm_installed
version = npm_version
version_raw = npm_version_raw


def ensure_installed():
    raise_if_dependency_missing(NPM_NAME)


def ensure_version_gte(required_version):
    ensure_installed()
    raise_if_dependency_version_less_than(NPM_NAME, required_version)


def run(*args):
    ensure_installed()
    return run_command((PATH_TO_NPM,) + tuple(args))


def install(target_dir):
    if not target_dir or not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        raise NpmInstallArgumentsError(
            'npm.install\'s `target_dir` parameter must be a string pointing to a directory. Received: {0}'.format(
                target_dir
            )
        )

    ensure_installed()

    command = (PATH_TO_NPM, NPM_INSTALL_COMMAND)

    if NPM_INSTALL_PATH_TO_PYTHON:
        command += ('--python={path_to_python}'.format(path_to_python=NPM_INSTALL_PATH_TO_PYTHON),)

    subprocess.call(command, cwd=target_dir)