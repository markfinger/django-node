import os
from .settings import PATH_TO_NODE
from .utils import (
    node_installed, node_version_raw, raise_if_dependency_missing, NODE_NAME, node_version,
    raise_if_dependency_version_less_than, run_command,
)

is_installed = node_installed
version = node_version
version_raw = node_version_raw


def ensure_installed():
    raise_if_dependency_missing(NODE_NAME)


def ensure_version_gte(required_version):
    ensure_installed()
    raise_if_dependency_version_less_than(NODE_NAME, required_version)


def run(*args, **kwargs):
    ensure_installed()

    production = kwargs.pop('production', None)
    if production:
        node_env = os.environ.get('NODE_ENV', None)
        os.environ['NODE_ENV'] = 'production'

    results = run_command(
        (PATH_TO_NODE,) + tuple(args)
    )

    if production:
        if node_env is not None:
            os.environ['NODE_ENV'] = node_env
        else:
            del os.environ['NODE_ENV']

    return results