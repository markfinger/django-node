import subprocess
from .settings import NODE_VERSION_COMMAND, NPM_VERSION_COMMAND, NODE_VERSION_FILTER, NPM_VERSION_FILTER
from .exceptions import (
    EnvironmentInterrogationException, MalformedVersionInputException, MissingDependencyException,
    OutdatedVersionException
)

# Interrogate the system's node
try:
    node_process = subprocess.Popen(NODE_VERSION_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    node_process.wait()
    stderr = node_process.stderr.read()
    if stderr:
        raise EnvironmentInterrogationException(stderr)
    node_installed = True
    node_version_string = node_process.stdout.read().strip()
except OSError:
    node_installed = False
    node_version_string = None
node_version = None
if node_version_string:
    node_version = NODE_VERSION_FILTER(node_version_string)

# Interrogate the system's npm
try:
    npm_process = subprocess.Popen(NPM_VERSION_COMMAND, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    npm_process.wait()
    stderr = npm_process.stderr.read()
    if stderr:
        raise EnvironmentInterrogationException(stderr)
    npm_installed = True
    npm_version_string = npm_process.stdout.read().strip()
except OSError:
    npm_installed = False
    npm_version_string = None
npm_version = None
if npm_version_string:
    npm_version = NPM_VERSION_FILTER(npm_version_string)


def _validate_version_iterable(version):
    if not isinstance(version, tuple):
        raise MalformedVersionInputException(
            'Versions must be tuples. Received {0}'.format(version)
        )
    if len(version) < 3:
        raise MalformedVersionInputException(
            'Versions must have three numbers defined. Received {0}'.format(version)
        )
    for number in version:
        if not isinstance(number, (int, long,)):
            raise MalformedVersionInputException(
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

_missing_dependency_error_message = (
    '{application} is not installed. Version {required_version} or greater is required.'
)

_outdated_version_error_message = (
    'The installed {application} version is outdated. Version {current_version} is installed, but version '
    '{required_version} is required. Please update {application}.'
)


def _format_version(version):
    return '.'.join(map(unicode, version))


def _ensure_dependency(application_name, is_installed, current_version, required_version):
    if not is_installed:
        raise MissingDependencyException(
            _missing_dependency_error_message.format(
                application=application_name,
                required_version=_format_version(required_version),
            )
        )
    if _check_if_version_is_outdated(current_version, required_version):
        raise OutdatedVersionException(
            _outdated_version_error_message.format(
                application=application_name,
                current_version=_format_version(current_version),
                required_version=_format_version(required_version),
            )
        )


def ensure_node_version_gte(required_version):
    _ensure_dependency('Node.js', node_installed, node_version, required_version)


def ensure_npm_version_gte(required_version):
    _ensure_dependency('NPM', npm_installed, npm_version, required_version)