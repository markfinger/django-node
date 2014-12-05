import os
from .settings import NPM_INSTALL_COMMAND, PATH_TO_NPM, ALLOW_NPM_INSTALL
from .exceptions import NpmInstallError, NpmInstallArgumentsError, NpmInstallDisallowed
from .utils import (
    run_command, ensure_dependency_installed, ensure_dependency_version_gte, NPM_NAME,
    npm_installed as installed,
    npm_version as version,
    npm_version_raw as version_raw,
)


def ensure_installed():
    ensure_dependency_installed(NPM_NAME)


def ensure_version_gte(required_version):
    ensure_installed()
    ensure_dependency_version_gte(NPM_NAME, required_version)


def run(cmd_to_run):
    ensure_installed()
    return run_command(
        (PATH_TO_NPM,) + cmd_to_run
    )


def install(target_dir, packages=None, options=None, silent=None):
    """
    cd into `target_dir`,
    call `NPM_INSTALL_COMMAND`, and then
    cd back to the previous directory
    """

    if not ALLOW_NPM_INSTALL:
        raise NpmInstallDisallowed(
            'Trying to install in to "{target_dir}" the packages "{packages}" with options "{options}"'.format(
                target_dir=target_dir,
                packages=packages,
                options=options,
            )
        )

    ensure_installed()

    origin_dir = os.getcwd()

    os.chdir(target_dir)

    cmd_to_run = NPM_INSTALL_COMMAND

    if packages is not None and not isinstance(packages, tuple):
        raise NpmInstallArgumentsError(
            'packages argument must be either a tuple or None. Received: {0}'.format(packages)
        )

    if options is not None and not isinstance(options, tuple):
        raise NpmInstallArgumentsError(
            'options argument must be either a tuple or None. Received: {0}'.format(options)
        )

    if packages:
        cmd_to_run += packages

    if options:
        cmd_to_run += options

    stderr, stdout = run(cmd_to_run)

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
            'Output from `{command}` in {target_dir}'.format(
                command=' '.join((PATH_TO_NPM,) + NPM_INSTALL_COMMAND),
                target_dir=target_dir,
            )
        )
        print('-' * 80)
        print(stdout.strip())
        print('-' * 80)

    os.chdir(origin_dir)

    return stdout