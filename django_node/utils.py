import subprocess
import tempfile
from .settings import (
    PATH_TO_NODE, PATH_TO_NPM, NODE_VERSION_COMMAND, NPM_VERSION_COMMAND, NODE_VERSION_FILTER, NPM_VERSION_FILTER,
    RAISE_ON_MISSING_DEPENDENCIES, RAISE_ON_OUTDATED_DEPENDENCIES,
)
from .exceptions import ErrorInterrogatingEnvironment, MalformedVersionInput, MissingDependency, OutdatedDependency


def run_command(cmd_to_run):
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:

        # Run the command
        popen = subprocess.Popen(cmd_to_run, stdout=stdout_file, stderr=stderr_file)
        popen.wait()

        stdout_file.seek(0)
        stderr_file.seek(0)

        return stderr_file.read(), stdout_file.read()


def _interrogate(cmd_to_run, version_filter):
    try:
        stderr, stdout = run_command(cmd_to_run)
        if stderr:
            raise ErrorInterrogatingEnvironment(stderr)
        installed = True
        version_raw = stdout.strip()
    except OSError:
        installed = False
        version_raw = None
    version = None
    if version_raw:
        version = version_filter(version_raw)
    return installed, version, version_raw,

# Interrogate the system
node_installed, node_version, node_version_raw = _interrogate(NODE_VERSION_COMMAND, NODE_VERSION_FILTER)
npm_installed, npm_version, npm_version_raw = _interrogate(NPM_VERSION_COMMAND, NPM_VERSION_FILTER)

_missing_dependency_error_message = '{application} is not installed or cannot be found at path "{path}".'

_version_required_error_message = 'Version {required_version} or greater is required.'

_outdated_version_error_message = (
    'The installed {application} version is outdated. Version {current_version} is installed, but version '
    '{required_version} is required. Please update {application}.'
)

NPM_NAME = 'NPM'
NODE_NAME = 'Node.js'


def _validate_version_iterable(version):
    if not isinstance(version, tuple):
        raise MalformedVersionInput(
            'Versions must be tuples. Received {0}'.format(version)
        )
    if len(version) < 3:
        raise MalformedVersionInput(
            'Versions must have three numbers defined. Received {0}'.format(version)
        )
    for number in version:
        if not isinstance(number, (int, long,)):
            raise MalformedVersionInput(
                'Versions can only contain number. Received {0}'.format(version)
            )


def _check_if_version_is_outdated(current_version, required_version):
    _validate_version_iterable(required_version)
    for i, number_required in enumerate(required_version):
        if number_required > current_version[i]:
            return True
        elif number_required < current_version[i]:
            return False
    return current_version != required_version


def _format_version(version):
    return '.'.join(map(unicode, version))


def ensure_dependency_installed(application, required_version=None):
    if application == NPM_NAME:
        is_installed = npm_installed
        path = PATH_TO_NPM
    else:
        is_installed = node_installed
        path = PATH_TO_NODE
    if not is_installed:
        error = _missing_dependency_error_message.format(
            application=application,
            path=path,
        )
        if required_version:
            error += _version_required_error_message.format(
                required_version=_format_version(required_version)
            )
        e = MissingDependency(error)
        if RAISE_ON_MISSING_DEPENDENCIES:
            raise e
        else:
            print(e)


def ensure_dependency_version_gte(application, required_version):
    if application == NPM_NAME:
        current_version = npm_version
    else:
        current_version = node_version
    if _check_if_version_is_outdated(current_version, required_version):
        e = OutdatedDependency(
            _outdated_version_error_message.format(
                application=application,
                current_version=_format_version(current_version),
                required_version=_format_version(required_version),
            )
        )
        if RAISE_ON_OUTDATED_DEPENDENCIES:
            raise e
        else:
            print(e)