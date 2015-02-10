import os
from .exceptions import NpmInstallArgumentsError, NpmInstallError
from .settings import PATH_TO_NPM, NPM_INSTALL_PATH_TO_PYTHON, NPM_INSTALL_COMMAND
from .utils import (
    NPM_NAME, npm_installed, npm_version, npm_version_raw, raise_if_dependency_missing,
    raise_if_dependency_version_less_than, run_command
)

is_installed = npm_installed
version = npm_version
version_raw = npm_version_raw


def ensure_installed():
    """
    A method which will raise an exception if NPM is not installed.
    """
    raise_if_dependency_missing(NPM_NAME)


def ensure_version_gte(required_version):
    """
    A method which will raise an exception if the installed version of NPM is
    less than the version required.

    Arguments:

    - `version_required`: a tuple containing the minimum version required.

    ```
    from django_node import npm

    npm_version_required = (2, 0, 0)

    npm.ensure_version_gte(npm_version_required)
    ```
    """
    ensure_installed()
    raise_if_dependency_version_less_than(NPM_NAME, required_version)


def run(*args):
    """
    A method which will invoke NPM with the arguments provided and return the resulting stderr and stdout.

    ```
    from django_node import npm

    stderr, stdout = npm.run('install', '--save', 'some-package')
    ```
    """
    ensure_installed()
    command = (PATH_TO_NPM,) + tuple(args)
    if NPM_INSTALL_PATH_TO_PYTHON:
        command += ('--python={path_to_python}'.format(path_to_python=NPM_INSTALL_PATH_TO_PYTHON),)
    return run_command(command)


def install(target_dir, *args, **kwargs):
    """
    A method that will invoke `npm install` in a specified directory. Optional arguments will be
    appended to the invoked command.

    Arguments:

    - `target_dir`: a string pointing to the directory which the command will be invoked in.
    - `*args`: optional strings to append to the invoked command.
    - `silent`: an optional keyword argument indicating that NPM's output should not be printed to the terminal.

    ```
    from django_node import npm

    # Install the dependencies in a particular directory
    stderr, stdout = npm.install('/path/to/some/directory/')

    # Install a dependency into a particular directory and persist it to the package.json file
    stderr, stdout = npm.install('/path/to/some/directory/', '--save', 'some-package')

    # Install dependencies but suppress NPM's output
    stderr, stdout = npm.install('/path/to/some/directory/', silent=True)
    ```
    """

    if not isinstance(target_dir, str):
        raise NpmInstallArgumentsError(
            'npm.install\'s `target_dir` parameter must be either a str or unicode. Received: {0}'.format(target_dir)
        )

    if not os.path.exists(target_dir) or not os.path.isdir(target_dir):
        raise NpmInstallArgumentsError(
            'npm.install\'s `target_dir` parameter must be a string pointing to a directory. Received: {0}'.format(
                target_dir
            )
        )

    args = tuple(args)

    silent = kwargs.get('silent', False)

    ensure_installed()

    origin_dir = os.getcwd()

    os.chdir(target_dir)

    stderr, stdout = run(NPM_INSTALL_COMMAND, *args)

    if stderr:
        for line in stderr.splitlines():
            if line.lower().startswith('npm warn'):
                print(line)
            else:
                os.chdir(origin_dir)
                raise NpmInstallError(stderr)

    if stdout and not silent:
        print('-' * 80)
        print(
            'Output from running `{command}` in {target_dir}'.format(
                command=' '.join((PATH_TO_NPM, NPM_INSTALL_COMMAND,) + args),
                target_dir=target_dir,
            )
        )
        print('-' * 80)
        print(stdout.strip())
        print('-' * 80)

    os.chdir(origin_dir)

    return stderr, stdout