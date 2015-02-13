from django.core.management.base import BaseCommand
from optparse import make_option


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option(
            '--debug',
            dest='debug',
            action='store_const',
            const=True,
            help='Start the server with a debugger',
        ),
    )

    def handle(self, *args, **options):
        from django_node.server import server

        print('Starting server at {server_url}'.format(server_url=server.get_server_url()))

        if options['debug']:
            server.start(use_existing_process=False, debug=True)
        else:
            server.start(use_existing_process=False)