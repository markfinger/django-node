from django_node import settings
settings.INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME = False

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from django_node.settings import PACKAGE_DEPENDENCIES
        if PACKAGE_DEPENDENCIES:
            print('Uninstalling package dependencies in {package_dependencies}'.format(
                package_dependencies=PACKAGE_DEPENDENCIES
            ))
            from django_node.package_dependent import uninstall_configured_package_dependencies
            uninstall_configured_package_dependencies()

        from django_node.server import server
        for dependent in (server,) + server.services:
            print('Uninstalling package dependencies for {dependent}'.format(dependent=dependent))
            dependent.uninstall_dependencies()