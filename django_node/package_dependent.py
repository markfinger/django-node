import os
import shutil
from .settings import PACKAGE_DEPENDENCIES
from .utils import resolve_dependencies


def install_dependencies(directory):
    resolve_dependencies(path_to_run_npm_install_in=directory)


def uninstall_dependencies(directory):
    path_to_dependencies = os.path.join(directory, 'node_modules')
    if os.path.isdir(path_to_dependencies):
        shutil.rmtree(path_to_dependencies)


def install_configured_package_dependencies():
    for directory in PACKAGE_DEPENDENCIES:
        install_dependencies(directory)


def uninstall_configured_package_dependencies():
    for directory in PACKAGE_DEPENDENCIES:
        uninstall_dependencies(directory)


class PackageDependent(object):
    # An optional path to a directory containing a package.json file
    package_dependencies = None

    @classmethod
    def install_dependencies(cls):
        if cls.package_dependencies is not None:
            install_dependencies(cls.package_dependencies)

    @classmethod
    def uninstall_dependencies(cls):
        if cls.package_dependencies is not None:
            uninstall_dependencies(cls.package_dependencies)