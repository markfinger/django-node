import os
from . import settings
from . import utils

is_installed = utils.node_installed
version = utils.node_version
version_raw = utils.node_version_raw


def ensure_installed():
    """
    A method which will raise an exception if Node.js is not installed.
    """
    utils.raise_if_dependency_missing(utils.NODE_NAME)


def ensure_version_gte(required_version):
    """
    A method which will raise an exception if the installed version of Node.js is
    less than the version required.

    Arguments:

    `version_required`: a tuple containing the minimum version required.

    ```
    from django_node import node

    node_version_required = (0, 10, 0)

    node.ensure_version_gte(node_version_required)
    ```
    """
    ensure_installed()
    utils.raise_if_dependency_version_less_than(utils.NODE_NAME, required_version)


def run(*args, **kwargs):
    """
    A method which will invoke Node.js with the arguments provided and return the resulting stderr and stdout.

    Accepts an optional keyword argument, `production`, which will ensure that the command is run
    with the `NODE_ENV` environment variable set to 'production'.

    ```
    from django_node import node

    stderr, stdout = node.run('/path/to/some/file.js', '--some-argument')

    # With NODE_ENV set to production
    stderr, stdout = node.run('/path/to/some/file.js', '--some-argument', production=True)
    ```
    """
    ensure_installed()

    production = kwargs.pop('production', None)
    if production:
        node_env = os.environ.get('NODE_ENV', None)
        os.environ['NODE_ENV'] = 'production'

    results = utils.run_command(
        (settings.PATH_TO_NODE,) + tuple(args)
    )

    if production:
        if node_env is not None:
            os.environ['NODE_ENV'] = node_env
        else:
            del os.environ['NODE_ENV']

    return results