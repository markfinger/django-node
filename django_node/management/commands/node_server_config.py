from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        from django_node.server import server
        print(server.get_serialised_config())