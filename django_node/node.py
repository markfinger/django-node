from .settings import PATH_TO_NODE
from .utils import (
    run_command, ensure_dependency_installed, ensure_dependency_version_gte, NODE_NAME,
    node_installed as installed,
    node_version as version,
    node_version_raw as version_raw,
)


def ensure_installed():
    ensure_dependency_installed(NODE_NAME)


def ensure_version_gte(required_version):
    ensure_installed()
    ensure_dependency_version_gte(NODE_NAME, required_version)


def run(cmd_to_run):
    ensure_installed()
    return run_command(
        (PATH_TO_NODE,) + cmd_to_run
    )