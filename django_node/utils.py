import sys
import subprocess
import tempfile
import importlib
import re
import inspect
from django.utils import six
from .settings import (
    PATH_TO_NODE, PATH_TO_NPM, NODE_VERSION_COMMAND, NODE_VERSION_FILTER, NPM_VERSION_COMMAND, NPM_VERSION_FILTER,
)
from .exceptions import (
    DynamicImportError, ErrorInterrogatingEnvironment, MalformedVersionInput, MissingDependency, OutdatedDependency,
    ModuleDoesNotContainAnyServices
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
        error = '{application} is not installed or cannot be found at path "{path}".'.format(
            application=application,
            path=path,
        )
        if required_version:
            error += 'Version {required_version} or greater is required.'.format(
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
            (
                'The installed {application} version is outdated. Version {current_version} is installed, but version '
                '{required_version} is required. Please update {application}.'
            ).format(
                application=application,
                current_version=_format_version(current_version),
                required_version=_format_version(required_version),
            )
        )
    

def dynamic_import_module(import_path):
    try:
        return importlib.import_module(import_path)
    except ImportError as e:
        msg = 'Failed to import "{import_path}"'.format(
            import_path=import_path
        )
        six.reraise(DynamicImportError, DynamicImportError(msg, e.__class__.__name__, *e.args), sys.exc_info()[2])


def dynamic_import_attribute(import_path):
    module_import_path = '.'.join(import_path.split('.')[:-1])
    imported_module = dynamic_import_module(module_import_path)
    try:
        return getattr(imported_module, import_path.split('.')[-1])
    except AttributeError as e:
        msg = 'Failed to import "{import_path}"'.format(
            import_path=import_path
        )
        six.reraise(DynamicImportError, DynamicImportError(msg, e.__class__.__name__, *e.args), sys.exc_info()[2])

html_entity_map = {
    '&nbsp;': ' ',
    '&lt;': '<',
    '&gt;': '>',
    '&amp;': '&',
    '&lsquo;': '\'',
    '&rsquo;': '\'',
    '&quot;;': '"',
    '&ldquo;': '"',
    '&rdquo;': '"',
    '&ndash;': '-',
    '&mdash;': '-',
    '&acute;': '`',
}


# The various HTML decoding solutions that are proposed by
# the python community seem to have issues where the unicode
# characters are printed in encoded form. This solution is
# not desirable, but works for django-node's purposes.
def decode_html_entities(html):
    """
    Decodes a limited set of HTML entities.
    """
    if not html:
        return html

    for entity, char in six.iteritems(html_entity_map):
        html = html.replace(entity, char)

    return html


def convert_html_to_plain_text(html):
    if not html:
        return html

    if six.PY2:
        html = html.decode('utf-8')

    html = decode_html_entities(html)
    # Replace HTML break rules with new lines
    html = html.replace('<br>', '\n')
    # Remove multiple spaces
    html = re.sub(' +', ' ', html)

    return html


def resolve_dependencies(node_version_required=None, npm_version_required=None, path_to_run_npm_install_in=None):
    from . import node, npm  # Avoid a circular import

    # Ensure that the external dependencies are met
    if node_version_required is not None:
        node.ensure_version_gte(node_version_required)
    if npm_version_required is not None:
        npm.ensure_version_gte(npm_version_required)

    # Ensure that the required packages have been installed
    if path_to_run_npm_install_in is not None:
        npm.install(path_to_run_npm_install_in)


def discover_services(service_config):
    from .base_service import BaseService  # Avoid a circular import

    services = ()

    for import_path in service_config:
        module = dynamic_import_module(import_path)
        module_contains_services = False
        for attr_name in dir(module):
            service = getattr(module, attr_name)
            if (
                inspect.isclass(service) and
                service is not BaseService and
                issubclass(service, BaseService) and
                service not in services and
                getattr(service, 'path_to_source', None)
            ):
                service.validate()
                services += (service,)
                module_contains_services = True
        if not module_contains_services:
            raise ModuleDoesNotContainAnyServices(import_path)

    return services