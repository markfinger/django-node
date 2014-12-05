from django.conf import settings

setting_overrides = getattr(settings, 'DJANGO_NODE', {})

PATH_TO_NODE = setting_overrides.get(
    'PATH_TO_NODE',
    'node'
)

NODE_VERSION_COMMAND = setting_overrides.get(
    'NODE_VERSION_COMMAND',
    (PATH_TO_NODE, '--version',)
)

NODE_VERSION_FILTER = setting_overrides.get(
    'NODE_VERSION_FILTER',
    lambda version: tuple(map(int, (version[1:] if version[0] == 'v' else version).split('.'))),
)

PATH_TO_NPM = setting_overrides.get(
    'PATH_TO_NODE',
    'npm'
)

NPM_VERSION_COMMAND = setting_overrides.get(
    'NPM_VERSION_COMMAND',
    (PATH_TO_NPM, '--version',)
)

NPM_VERSION_FILTER = setting_overrides.get(
    'NPM_VERSION_FILTER',
    lambda version: tuple(map(int, version.split('.'))),
)

NPM_INSTALL_COMMAND = setting_overrides.get(
    'NPM_INSTALL_COMMAND',
    ('install',)
)

RAISE_ON_MISSING_DEPENDENCIES = setting_overrides.get(
    'RAISE_ON_MISSING_DEPENDENCIES',
    True,
)

RAISE_ON_OUTDATED_DEPENDENCIES = setting_overrides.get(
    'RAISE_ON_OUTDATED_DEPENDENCIES',
    True,
)

ALLOW_NPM_INSTALL = setting_overrides.get(
    'ALLOW_NPM_INSTALL',
    True,
)