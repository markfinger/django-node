import os
import sys
import atexit
import json
import subprocess
import logging
import tempfile
import requests
from requests.exceptions import ConnectionError, ReadTimeout, Timeout
from django.utils import six
if six.PY2:
    from urlparse import urljoin
elif six.PY3:
    from urllib.parse import urljoin
from .services import EchoService
from .settings import (
    PATH_TO_NODE, SERVER_PROTOCOL, SERVER_ADDRESS, SERVER_PORT, NODE_VERSION_REQUIRED, NPM_VERSION_REQUIRED,
    SERVICES, INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME
)
from .exceptions import (
    NodeServerConnectionError, NodeServerStartError, NodeServerAddressInUseError, NodeServerTimeoutError,
    MalformedServiceConfig
)
from .utils import resolve_dependencies, discover_services
from .package_dependent import PackageDependent


class NodeServer(PackageDependent):
    """
    A persistent Node server which sits alongside the python process
    and responds over HTTP
    """

    protocol = SERVER_PROTOCOL
    address = SERVER_ADDRESS
    port = SERVER_PORT
    path_to_source = os.path.join(os.path.dirname(__file__), 'node_modules', 'django-node-server', 'index.js')
    package_dependencies = os.path.dirname(__file__)
    shutdown_on_exit = True
    is_running = False
    logger = logging.getLogger(__name__)
    echo_service = EchoService()
    services = (EchoService,)
    service_config = SERVICES
    process = None

    def __init__(self):
        resolve_dependencies(
            node_version_required=NODE_VERSION_REQUIRED,
            npm_version_required=NPM_VERSION_REQUIRED,
        )
        if not isinstance(self.service_config, tuple):
            raise MalformedServiceConfig(
                'DJANGO_NODE[\'SERVICES\'] setting must be a tuple. Found "{setting}"'.format(setting=SERVICES)
            )
        services = discover_services(self.service_config)
        if services:
            self.services += services
        if INSTALL_PACKAGE_DEPENDENCIES_DURING_RUNTIME:
            for dependent in (self,) + self.services:
                dependent.install_dependencies()

    def get_config(self):
        services = ()
        for service in self.services:
            services += ({
                'name': service.get_name(),
                'path_to_source': service.get_path_to_source(),
            },)
        return {
            'address': self.address,
            'port': self.port,
            'services': services,
            'startup_output': self.get_startup_output(),
        }

    def get_serialised_config(self):
        return json.dumps(self.get_config())

    def start(self, debug=None, use_existing_process=None, blocking=None):
        if debug is None:
            debug = False
        if use_existing_process is None:
            use_existing_process = True
        if blocking is None:
            blocking = False

        if debug:
            use_existing_process = False
            blocking = True

        if use_existing_process and self.test():
            self.is_running = True
            return

        if not use_existing_process and self.test():
            raise NodeServerAddressInUseError(
                'A process is already listening at {server_url}'.format(
                    server_url=self.get_server_url()
                )
            )

        # Ensure that the process is terminated if the python process stops
        if self.shutdown_on_exit:
            atexit.register(self.stop)

        with tempfile.NamedTemporaryFile() as config_file:
            config_file.write(six.b(self.get_serialised_config()))
            config_file.flush()

            cmd = (PATH_TO_NODE,)
            if debug:
                cmd += ('debug',)
            cmd += (
                self.path_to_source,
                '--config', config_file.name,
            )

            self.log('Starting process with {cmd}'.format(cmd=cmd))

            if blocking:
                # Start the server in a blocking process
                subprocess.call(cmd)
                return

            # While rendering templates Django will silently ignore some types of exceptions,
            # so we need to intercept them and raise our own class of exception
            try:
                # TODO: set NODE_ENV. See `env` arg https://docs.python.org/2/library/subprocess.html#popen-constructor
                self.process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
            except (TypeError, AttributeError):
                msg = 'Failed to start server with {arguments}'.format(arguments=cmd)
                six.reraise(NodeServerStartError, NodeServerStartError(msg), sys.exc_info()[2])

            # Block until the server is ready and pushes the expected output to stdout
            output = self.process.stdout.readline()
            output = output.decode('utf-8')

            if output.strip() != self.get_startup_output():
                # Read in the rest of the error message
                output += self.process.stdout.read().decode('utf-8')
                if 'EADDRINUSE' in output:
                    raise NodeServerAddressInUseError(
                        (
                            'Port "{port}" already in use. '
                            'Try changing the DJANGO_NODE[\'SERVER_PORT\'] setting. '
                            '{output}'
                        ).format(
                            port=self.port,
                            output=output,
                        )
                    )
                else:
                    raise NodeServerStartError(output)

        self.is_running = True

        # Ensure that the server is running
        if not self.test():
            self.stop()
            raise NodeServerStartError(
                'Server does not appear to be running. Tried to test the server at "{echo_endpoint}"'.format(
                    echo_endpoint=self.echo_service.get_name(),
                )
            )

        self.log('Started process')

    def get_startup_output(self):
        return 'Node server listening at {server_url}'.format(
            server_url=self.get_server_url()
        )

    def stop(self):
        if self.process is not None and self.test():
            self.process.terminate()
            self.log('Terminated process')
        self.is_running = False

    def get_server_url(self):
        if self.protocol and self.address and self.port:
            return '{protocol}://{address}:{port}'.format(
                protocol=self.protocol,
                address=self.address,
                port=self.port,
            )

    def log(self, message):
        self.logger.info(
            '{server_name} [Address: {server_url}] {message}'.format(
                server_name=self.__class__.__name__,
                server_url=self.get_server_url(),
                message=message,
            )
        )

    def test(self):
        """
        Returns a boolean indicating if the server is currently running
        """
        return self.echo_service.test()

    def send_request_to_service(self, endpoint, timeout=None, data=None, ensure_started=None):
        if ensure_started is None:
            ensure_started = True

        if ensure_started and not self.is_running:
            self.start()

        self.log('Sending request to endpoint "{url}" with data "{data}"'.format(
            url=endpoint,
            data=data,
        ))

        absolute_url = urljoin(self.get_server_url(), endpoint)

        try:
            return requests.post(absolute_url, timeout=timeout, data=data)
        except ConnectionError as e:
            six.reraise(NodeServerConnectionError, NodeServerConnectionError(absolute_url, *e.args), sys.exc_info()[2])
        except (ReadTimeout, Timeout) as e:
            six.reraise(NodeServerTimeoutError, NodeServerTimeoutError(absolute_url, *e.args), sys.exc_info()[2])