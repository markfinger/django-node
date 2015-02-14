from optparse import make_option
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    option_list = (
        make_option(
            '-d', '--debug',
            dest='debug',
            action='store_const',
            const=True,
            help='Start the server with a debugger',
        ),
    ) + BaseCommand.option_list

    def handle(self, *args, **options):
        from django_node.server import server

        print('Starting server...\n')

        server.start(
            debug=options['debug'],
            use_existing_process=False,
            blocking=True,
        )
