from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from django_node.settings import PACKAGE_DEPENDENCIES
        if PACKAGE_DEPENDENCIES:
            print('Installing package dependencies in {package_dependencies}'.format(
                package_dependencies=PACKAGE_DEPENDENCIES
            ))
            from django_node.package_dependent import install_configured_package_dependencies
            install_configured_package_dependencies()

        from django_node.server import server
        for dependent in (server,) + server.services:
            print('Installing package dependencies for {dependent}'.format(dependent=dependent))
            dependent.install_dependencies()