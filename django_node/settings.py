import os
import sys
from django.conf import settings

setting_overrides = getattr(settings, 'DJANGO_NODE', {})

NODE_VERSION_REQUIRED = setting_overrides.get(
    'NODE_VERSION_REQUIRED',
    (0, 10, 25)
)

NPM_VERSION_REQUIRED = setting_overrides.get(
    'NPM_VERSION_REQUIRED',
    (2, 0, 0)
)

PATH_TO_NODE = setting_overrides.get(
    'PATH_TO_NODE',
    'node'
)

NODE_VERSION_COMMAND = setting_overrides.get(
    'NODE_VERSION_COMMAND',
    '--version',
)

NODE_VERSION_FILTER = setting_overrides.get(
    'NODE_VERSION_FILTER',
    lambda version: tuple(map(int, (version[1:] if version[0] == 'v' else version).split('.'))),
)

PATH_TO_NPM = setting_overrides.get(
    'PATH_TO_NPM',
    'npm'
)

NPM_VERSION_COMMAND = setting_overrides.get(
    'NPM_VERSION_COMMAND',
    '--version',
)

NPM_VERSION_FILTER = setting_overrides.get(
    'NPM_VERSION_FILTER',
    lambda version: tuple(map(int, version.split('.'))),
)

NPM_INSTALL_COMMAND = setting_overrides.get(
    'NPM_INSTALL_COMMAND',
    'install',
)

NPM_INSTALL_PATH_TO_PYTHON = setting_overrides.get(
    'NPM_INSTALL_PATH_TO_PYTHON',
    None,
)

SERVER = setting_overrides.get(
    'SERVER',
    'django_node.node_server.NodeServer',
)

SERVER_PROTOCOL = setting_overrides.get(
    'SERVER_PROTOCOL',
    'http',
)

SERVER_ADDRESS = setting_overrides.get(
    'SERVER_ADDRESS',
    '127.0.0.1',
)

# Read in the server port from a `DJANGO_NODE_SERVER_PORT` environment variable
SERVER_PORT = os.environ.get('DJANGO_NODE_SERVER_PORT', None)
if SERVER_PORT is None:
    SERVER_PORT = setting_overrides.get(
        'SERVER_PORT',
        '63578',
    )

SERVICES = setting_overrides.get(
    'SERVICES',
    (),
)

SERVICE_TIMEOUT = setting_overrides.get(
    'SERVICE_TIMEOUT',
    10.0,
)

SERVER_TEST_TIMEOUT = setting_overrides.get(
    'SERVER_TEST_TIMEOUT',
    2.0,
)

PACKAGE_DEPENDENCIES = setting_overrides.get(
    'PACKAGE_DEPENDENCIES',
    ()
)

INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME = setting_overrides.get(
    'INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME',
    True,
)

if INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME:
    # Prevent dependencies from being installed during init if
    # either of the package dependency commands are being run
    for i, arg in enumerate(sys.argv):
        if (
            arg.endswith('manage.py') and
            'uninstall_package_dependencies' in sys.argv or
            'install_package_dependencies' in sys.argv
        ):
            INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME = False
            break