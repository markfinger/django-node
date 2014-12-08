import settings
import utils

is_installed = utils.node_installed
version = utils.node_version
version_raw = utils.node_version_raw


def ensure_installed():
    """
    A method which will raise an exception if Node.js is not installed.
    """
    utils.ensure_dependency_installed(utils.NODE_NAME)


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
    utils.ensure_dependency_version_gte(utils.NODE_NAME, required_version)


def run(*args):
    """
    A method which will invoke Node.js with the arguments provided and return the resulting stderr and stdout.

    ```
    from django_node import node

    stderr, stdout = node.run('/path/to/some/file.js', '--some-argument')
    ```
    """
    ensure_installed()
    return utils.run_command(
        (settings.PATH_TO_NODE,) + tuple(args)
    )