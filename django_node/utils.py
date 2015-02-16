import sys
import subprocess
import tempfile
import importlib
from django.utils import six
from .settings import (
    PATH_TO_NODE, PATH_TO_NPM, NODE_VERSION_COMMAND, NODE_VERSION_FILTER, NPM_VERSION_COMMAND, NPM_VERSION_FILTER,
)
from .exceptions import (
    DynamicImportError, ErrorInterrogatingEnvironment, MalformedVersionInput, MissingDependency, OutdatedDependency,
)


def run_command(cmd_to_run):
    """
    Wrapper around subprocess that pipes the stderr and stdout from `cmd_to_run`
    to temporary files. Using the temporary files gets around subprocess.PIPE's
    issues with handling large buffers.

    Note: this command will block the python process until `cmd_to_run` has completed.

    Returns a tuple, containing the stderr and stdout as strings.
    """
    with tempfile.TemporaryFile() as stdout_file, tempfile.TemporaryFile() as stderr_file:

        # Run the command
        popen = subprocess.Popen(cmd_to_run, stdout=stdout_file, stderr=stderr_file)
        popen.wait()

        stderr_file.seek(0)
        stdout_file.seek(0)

        stderr = stderr_file.read()
        stdout = stdout_file.read()

        if six.PY3:
            stderr = stderr.decode()
            stdout = stdout.decode()

        return stderr, stdout


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
node_installed, node_version, node_version_raw = _interrogate(
    (PATH_TO_NODE, NODE_VERSION_COMMAND,),
    NODE_VERSION_FILTER,
)
npm_installed, npm_version, npm_version_raw = _interrogate(
    (PATH_TO_NPM, NPM_VERSION_COMMAND,),
    NPM_VERSION_FILTER,
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
        raise MalformedVersionInput(
            'Versions must be tuples. Received {0}'.format(version)
        )
    if len(version) < 3:
        raise MalformedVersionInput(
            'Versions must have three numbers defined. Received {0}'.format(version)
        )
    for number in version:
        if not isinstance(number, six.integer_types):
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
    return '.'.join(map(six.text_type, version))


def raise_if_dependency_missing(application, required_version=None):
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
        raise MissingDependency(error)


def raise_if_dependency_version_less_than(application, required_version):
    if application == NPM_NAME:
        current_version = npm_version
    else:
        current_version = node_version
    if _check_if_version_is_outdated(current_version, required_version):
        raise OutdatedDependency(
            _outdated_version_error_message.format(
                application=application,
                current_version=_format_version(current_version),
                required_version=_format_version(required_version),
            )
        )
    

def dynamic_import(import_path):
    module_import_path = '.'.join(import_path.split('.')[:-1])
    try:
        imported_module = importlib.import_module(module_import_path)
        imported_object = getattr(imported_module, import_path.split('.')[-1])
    except (ImportError, AttributeError) as e:
        msg = 'Failed to import "{import_path}"'.format(
            import_path=import_path
        )
        six.reraise(DynamicImportError, DynamicImportError(msg, e.__class__.__name__, *e.args), sys.exc_info()[2])
    return imported_object


_html_unescape = None
if six.PY2:
    import HTMLParser
    h = HTMLParser.HTMLParser()
    _html_unescape = h.unescape
elif six.PY3:
    try:
        import html.parser
        h = html.parser.HTMLParser()
        _html_unescape = h.unescape
    except ImportError:  # Py3.4+
        import html
        _html_unescape = html.unescape


def html_unescape(string):
    if _html_unescape:
        return _html_unescape(string).encode('utf-8')
    return string