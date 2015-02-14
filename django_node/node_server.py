import os
import sys
import atexit
import json
import subprocess
import requests
from requests.exceptions import ConnectionError
from django.utils import six
from . import node, npm
from .settings import (
    PATH_TO_NODE, SERVER_ADDRESS, SERVER_PORT, SERVER_PRINT_LOG, NODE_VERSION_REQUIRED, NPM_VERSION_REQUIRED,
)
from .exceptions import (
    NodeServerConnectionError, NodeServerStartError, NodeServerAddressInUseError, NodeServerError, ErrorAddingService,
)


class NodeServer(object):
    """
    A persistent Node server which sits alongside the python process
    and responds over HTTP
    """

    protocol = 'http'
    address = SERVER_ADDRESS
    port = SERVER_PORT
    path_to_source = os.path.join(os.path.dirname(__file__), 'server.js')
    start_on_init = False
    resolve_dependencies_on_init = True
    shutdown_on_exit = True
    has_started = False
    has_stopped = False

    _test_endpoint = '/__test__'
    _add_service_endpoint = '/__add_service__'
    _get_endpoints_endpoint = '/__get_endpoints__'

    _blacklisted_endpoints = (
        '', '*', '/', _test_endpoint, _add_service_endpoint, _get_endpoints_endpoint,
    )

    _expected_startup_output = '__NODE_SERVER_IS_RUNNING__\n'
    _expected_test_output = '__SERVER_TEST__'
    _expected_add_service_output = '__ADDED_ENDPOINT__'

    _process = None

    def __init__(self):
        if self.resolve_dependencies_on_init:
            # Ensure that the external dependencies are met
            node.ensure_version_gte(NODE_VERSION_REQUIRED)
            npm.ensure_version_gte(NPM_VERSION_REQUIRED)
            # Ensure that the required packages have been installed
            npm.install(os.path.dirname(__file__))

        if self.start_on_init:
            self.start()

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
            self.has_started = True
            self.has_stopped = False
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

        cmd = (PATH_TO_NODE,)
        if debug:
            cmd += ('debug',)
        cmd += (
            self.path_to_source,
            '--address', self.address,
            '--port', self.port,
            '--test-endpoint', self._test_endpoint,
            '--expected-test-output', self._expected_test_output,
            '--add-service-endpoint', self._add_service_endpoint,
            '--expected-add-service-output', self._expected_add_service_output,
            '--get-endpoints-endpoint', self._get_endpoints_endpoint,
            '--blacklisted-endpoints', json.dumps(self._blacklisted_endpoints),
        )
        if blocking:
            cmd += (
                '--expected-startup-output',
                'Node server listening at {server_url}'.format(server_url=self.get_server_url()),
            )
        else:
            cmd += ('--expected-startup-output', self._expected_startup_output,)

        self.log('Starting process with {cmd}'.format(cmd=cmd))

        if blocking:
            # Start the server in a blocking process
            subprocess.call(cmd)
            return

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            # TODO: set NODE_ENV. See `env` arg https://docs.python.org/2/library/subprocess.html#popen-constructor
            self._process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except (TypeError, AttributeError):
            msg = 'Failed to start server with {arguments}'.format(arguments=cmd)
            six.reraise(NodeServerStartError, NodeServerStartError(msg), sys.exc_info()[2])

        # Block until the server is ready and pushes the expected output to stdout
        output = self._process.stdout.readline()

        if output != self._expected_startup_output:
            # Read in the rest of the error message
            output += self._process.stdout.read()
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

        self.has_started = True
        self.has_stopped = False

        # Ensure that the server is running
        if not self.test():
            self.stop()
            raise NodeServerStartError(
                'Server does not appear to be running. Tried to test the server at "{test_url}"'.format(
                    test_url=self.get_test_url()
                )
            )

        self.log('Started process')

    def ensure_started(self):
        if not self.has_started:
            self.start()

    def stop(self):
        if self._process is not None and not self.has_stopped:
            self._process.terminate()
            self.log('Terminated process')

        self.has_stopped = True
        self.has_started = False

    def get_server_url(self):
        if self.protocol and self.address and self.port:
            return '{protocol}://{address}:{port}'.format(
                protocol=self.protocol,
                address=self.address,
                port=self.port,
            )

    def absolute_url(self, url):
        separator = '/' if not url.startswith('/') else ''
        return '{server_url}{separator}{url}'.format(
            server_url=self.get_server_url(),
            separator=separator,
            url=url,
        )

    def get_test_url(self):
        return self.absolute_url(self._test_endpoint)

    def _html_to_plain_text(self, html):
        # TODO: replace this with an actual HTML decoder, see: http://stackoverflow.com/a/2087433
        # Convert the error message from HTML to plain text
        html = html.replace('<br>', '\n')
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&quot;', '"')
        # Remove multiple spaces
        html = ' '.join(html.split())
        return html

    def _validate_response(self, response, url):
        if response.status_code != 200:
            error_message = self._html_to_plain_text(response.text)
            raise NodeServerError(
                'Error at {url}: {error_message}'.format(
                    url=url,
                    error_message=error_message,
                )
            )

        return response

    def get_server_name(self):
        return self.__class__.__name__

    def log(self, message):
        # TODO: replace print with django's logger
        if SERVER_PRINT_LOG:
            print('{server_name} [Address: {server_url}] {message}'.format(
                server_name=self.get_server_name(),
                server_url=self.get_server_url(),
                message=message,
            ))

    def test(self):
        if self.address is None or self.port is None:
            return False

        test_url = self.get_test_url()

        self.log('Testing server at {test_url}'.format(test_url=test_url))

        try:
            response = requests.get(test_url)
        except ConnectionError:
            return False

        if response.status_code != 200:
            return False

        return response.text == self._expected_test_output

    def get_service(self, endpoint):
        def service(**kwargs):
            return self.get(endpoint, params=kwargs)
        service.__name__ = '{server_name} service {endpoint}'.format(
            server_name=self.get_server_name(),
            endpoint=endpoint,
        )
        return service

    def get_endpoints(self):
        self.ensure_started()

        response = self.get(self._get_endpoints_endpoint)

        endpoints = json.loads(response.text)

        return [endpoint for endpoint in endpoints]

    def add_service(self, endpoint, path_to_source):
        self.ensure_started()

        if endpoint not in self._blacklisted_endpoints and endpoint in self.get_endpoints():
            return self.get_service(endpoint)

        self.log('Adding service at "{endpoint}" with source "{path_to_source}"'.format(
            endpoint=endpoint,
            path_to_source=path_to_source,
        ))

        add_service_url = self.absolute_url(self._add_service_endpoint)

        try:
            response = requests.post(add_service_url, data={
                'endpoint': endpoint,
                'path_to_source': path_to_source,
            })
        except ConnectionError as e:
            six.reraise(NodeServerConnectionError, NodeServerConnectionError(*e.args), sys.exc_info()[2])

        response = self._validate_response(response, add_service_url)

        if response.text != self._expected_add_service_output:
            error_message = self._html_to_plain_text(response.text)
            raise ErrorAddingService(error_message)

        return self.get_service(endpoint=endpoint)

    def get(self, endpoint, params=None):
        self.ensure_started()

        self.log('Sending request to endpoint "{url}" with params "{params}"'.format(
            url=endpoint,
            params=params,
        ))

        absolute_url = self.absolute_url(endpoint)

        try:
            response = requests.get(absolute_url, params=params)
        except ConnectionError as e:
            six.reraise(NodeServerConnectionError, NodeServerConnectionError(*e.args), sys.exc_info()[2])

        return self._validate_response(response, endpoint)