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

SERVER_DEBUG = setting_overrides.get(
    'SERVER_DEBUG',
    False,
)
