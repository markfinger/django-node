import subprocess
import tempfile
import settings
import exceptions


def run_command(cmd_to_run):
    """
    Wrapper around subprocess that pipes the stderr and stdout from `cmd_to_run`
    to temporary files. Using the temporary files gets around subprocess.PIPE's
    issues with handling large buffers.

    Returns a tuple, containing the stderr and stdout as strings.
    """
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:

        # Run the command
        popen = subprocess.Popen(cmd_to_run, stdout=stdout_file, stderr=stderr_file)
        popen.wait()

        stderr_file.seek(0)
        stdout_file.seek(0)

        return stderr_file.read(), stdout_file.read()


def _interrogate(cmd_to_run, version_filter):
    try:
        stderr, stdout = run_command(cmd_to_run)
        if stderr:
            raise exceptions.ErrorInterrogatingEnvironment(stderr)
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
node_installed, node_version, node_version_raw = _interrogate(
    (settings.PATH_TO_NODE, settings.NODE_VERSION_COMMAND,),
    settings.NODE_VERSION_FILTER,
)
npm_installed, npm_version, npm_version_raw = _interrogate(
    (settings.PATH_TO_NPM, settings.NPM_VERSION_COMMAND,),
    settings.NPM_VERSION_FILTER,
)

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
        raise exceptions.MalformedVersionInput(
            'Versions must be tuples. Received {0}'.format(version)
        )
    if len(version) < 3:
        raise exceptions.MalformedVersionInput(
            'Versions must have three numbers defined. Received {0}'.format(version)
        )
    for number in version:
        if not isinstance(number, (int, long,)):
            raise exceptions.MalformedVersionInput(
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


def raise_if_dependency_missing(application, required_version=None):
    if application == NPM_NAME:
        is_installed = npm_installed
        path = settings.PATH_TO_NPM
    else:
        is_installed = node_installed
        path = settings.PATH_TO_NODE
    if not is_installed:
        error = _missing_dependency_error_message.format(
            application=application,
            path=path,
        )
        if required_version:
            error += _version_required_error_message.format(
                required_version=_format_version(required_version)
            )
        raise exceptions.MissingDependency(error)


def raise_if_dependency_version_less_than(application, required_version):
    if application == NPM_NAME:
        current_version = npm_version
    else:
        current_version = node_version
    if _check_if_version_is_outdated(current_version, required_version):
        raise exceptions.OutdatedDependency(
            _outdated_version_error_message.format(
                application=application,
                current_version=_format_version(current_version),
                required_version=_format_version(required_version),
            )
        )