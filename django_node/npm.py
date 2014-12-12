import os
import settings
import exceptions
import utils

is_installed = utils.npm_installed
version = utils.npm_version
version_raw = utils.npm_version_raw


def ensure_installed():
    """
    A method which will raise an exception if NPM is not installed.
    """
    utils.raise_if_dependency_missing(utils.NPM_NAME)


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
    utils.raise_if_dependency_version_less_than(utils.NPM_NAME, required_version)


def run(*args):
    """
    A method which will invoke NPM with the arguments provided and return the resulting stderr and stdout.

    ```
    from django_node import npm

    stderr, stdout = npm.run('install', '--save', 'some-package')
    ```
    """
    ensure_installed()
    return utils.run_command(
        (settings.PATH_TO_NPM,) + tuple(args)
    )


def install(target_dir, arguments=None, silent=None):
    """
    A method that will invoke `npm install` in a specified directory. Optional arguments will be
    appended to the invoked command.

    Arguments:

    - `target_dir`: a string pointing to the directory which the command will be invoked in.
    - `arguments`: an optional tuple of strings to append to the invoked command.
    - `silent`: an optional boolean indicating that NPM's output should not be printed to the terminal.

    ```
    from django_node import npm

    # Install the dependencies in a particular directory
    stderr, stdout = npm.install('/path/to/some/directory/')

    # Install a dependency into a particular directory and persist it to the package.json file
    stderr, stdout = npm.install('/path/to/some/directory/', ('--save', 'some-package'))
    ```
    """

    if not isinstance(target_dir, str):
        raise exceptions.NpmInstallArgumentsError(
            'npm.install\'s `target_dir` parameter must be either a str or unicode. Received: {0}'.format(target_dir)
        )

    if arguments is None:
        arguments = ()
    elif not isinstance(arguments, tuple):
        raise exceptions.NpmInstallArgumentsError(
            'npm.install\'s `arguments` parameter must be either a tuple or None. Received: {0}'.format(arguments)
        )

    ensure_installed()

    origin_dir = os.getcwd()

    os.chdir(target_dir)

    stderr, stdout = run(settings.NPM_INSTALL_COMMAND, *arguments)

    if stderr:
        for line in stderr.splitlines():
            if line.lower().startswith('npm warn'):
                print(line)
            else:
                os.chdir(origin_dir)
                raise exceptions.NpmInstallError(stderr)

    if stdout and not silent:
        print('-' * 80)
        print(
            'Output from `{command}` in {target_dir}'.format(
                command=' '.join((settings.PATH_TO_NPM,) + arguments),
                target_dir=target_dir,
            )
        )
        print('-' * 80)
        print(stdout.strip())
        print('-' * 80)

    os.chdir(origin_dir)

    return stderr, stdout