import os
import sys
import atexit
import json
import subprocess
import requests
import uuid
from requests.exceptions import ConnectionError
from django.utils import six
from . import node, npm
from .settings import PATH_TO_NODE, SERVER_DEBUG, NODE_VERSION_REQUIRED, NPM_VERSION_REQUIRED
from .exceptions import NodeServerConnectionError, NodeServerStartError, NodeServerError, EndpointRegistrationError

# Ensure that the external dependencies are met
node.ensure_version_gte(NODE_VERSION_REQUIRED)
npm.ensure_version_gte(NPM_VERSION_REQUIRED)

# Ensure that the required packages have been installed
npm.install(os.path.dirname(__file__))


class NodeServer(object):
    """
    A persistent Node server which sits alongside the python process
    and responds over the network
    """

    debug = SERVER_DEBUG
    path_to_source = os.path.join(os.path.dirname(__file__), 'server.js')
    start_on_init = False
    shutdown_on_exit = True
    protocol = 'http'
    address = '127.0.0.1'
    port = '0'

    has_started = False
    has_stopped = False

    _test_endpoint = '/__test__'
    _register_endpoint = '/__register__'

    _expected_startup_output = 'Started NodeServer'
    _expected_test_output = 'NodeServer running {token}'.format(
        token=uuid.uuid4(),
    )
    _expected_register_output = 'Registered endpoint {token}'.format(
        token=uuid.uuid4(),
    )

    _process = None
    _startup_output = None
    _server_details_json = None
    _server_details = None
    _actual_address = None
    _actual_port = None

    def __init__(self):
        if self.start_on_init:
            self.start()

    def start(self):
        if self.debug:
            print('NodeServer starting...')

        if self.shutdown_on_exit:
            atexit.register(self.stop)

        arguments = (
            PATH_TO_NODE,
            self.path_to_source,
            '--address', self.address,
            '--port', self.port,
            '--expected-startup-output', self._expected_startup_output,
            '--test-endpoint', self._test_endpoint,
            '--expected-test-output', self._expected_test_output,
            '--register-endpoint', self._register_endpoint,
            '--expected-register-output', self._expected_register_output,
        )

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            self._process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except (TypeError, AttributeError):
            msg = 'Failed to start server with {arguments}'.format(arguments=arguments)
            six.reraise(NodeServerStartError, NodeServerStartError(msg), sys.exc_info()[2])

        startup_output = self._process.stdout.readline()
        self._startup_output = startup_output.decode()

        if self._startup_output.strip() != self._expected_startup_output:
            self.stop()
            self._startup_output += self._process.stdout.read()
            raise NodeServerStartError(
                'Error starting server: {startup_output}'.format(
                    startup_output=self._startup_output
                )
            )

        server_details_json = self._process.stdout.readline()
        self._server_details_json = server_details_json.decode()
        self._server_details = json.loads(self._server_details_json)

        # If the server is defining its own address or port, we
        # need to record it
        self._actual_address = self._server_details['address']
        self._actual_port = self._server_details['port']

        self.has_started = True
        self.has_stopped = False

        # Ensure that we can connect to the server over the network
        if not self.test():
            self.stop()
            raise NodeServerStartError(
                'Cannot test server to determine if startup successful. Tried {test_url}'.format(
                    test_url=self.absolute_url(self._test_endpoint)
                )
            )

        if self.debug:
            print('NodeServer now listening at {server_url}'.format(
                server_url=self.get_server_url()
            ))

    def get_server_url(self):
        return '{protocol}://{address}:{port}'.format(
            protocol=self.protocol,
            address=self._actual_address,
            port=self._actual_port,
        )

    def absolute_url(self, url):
        return '{server_url}{separator}{url}'.format(
            server_url=self.get_server_url(),
            separator='/' if not url.startswith('/') else '',
            url=url,
        )

    def stop(self):
        if self.debug:
            print('Stopping NodeServer...'.format(
                server_url=self.get_server_url()
            ))

        if self._process is not None and not self.has_stopped:
            self._process.terminate()

        self.has_stopped = True
        self.has_started = False

    def _handle_response(self, url, response):
        if response.status_code != 200:
            error_message = response.text
            # Convert the error message from HTML to plain text
            error_message = error_message.replace('<br>', '\n')
            error_message = error_message.replace('&nbsp;', ' ')
            error_message = error_message.replace('&quot;', '"')
            # Remove multiple spaces
            error_message = ' '.join(error_message.split())
            raise NodeServerError(
                'Error at {url}: {error_message}'.format(
                    url=url,
                    error_message=error_message,
                )
            )

        return response

    def get(self, url, params=None):
        if not self.has_started:
            self.start()

        absolute_url = self.absolute_url(url)

        if self.debug:
            print('Sending GET request to {absolute_url} with params "{params}"'.format(
                absolute_url=absolute_url,
                params=params,
            ))

        try:
            response = requests.get(absolute_url, params=params)
        except ConnectionError:
            raise NodeServerConnectionError(absolute_url)

        return self._handle_response(absolute_url, response)

    def post(self, url, data=None):
        if not self.has_started:
            self.start()

        absolute_url = self.absolute_url(url)

        if self.debug:
            print('Sending POST request to {absolute_url} with data "{data}"'.format(
                absolute_url=absolute_url,
                data=json.dumps(data),
            ))

        try:
            response = requests.post(absolute_url, data=data)
        except ConnectionError:
            raise NodeServerConnectionError(absolute_url)

        return self._handle_response(absolute_url, response)

    def test(self):
        if self.debug:
            print('Testing server at {server_url}'.format(
                server_url=self.get_server_url()
            ))

        absolute_url = self.absolute_url(self._test_endpoint)

        try:
            response = requests.get(absolute_url)
        except ConnectionError:
            return False

        if response.status_code != 200:
            return False

        return response.text == self._expected_test_output

    def register(self, endpoint, path_to_source):
        if self.debug:
            print('Registering endpoint {endpoint} at {server_url} with source {path_to_source}'.format(
                endpoint=endpoint,
                server_url=self.get_server_url(),
                path_to_source=path_to_source,
            ))

        # if not endpoint.startswith('/'):
        #     raise EndpointRegistrationError('Endpoint "{endpoint}" does not start with "/"'.format(
        #         endpoint=endpoint
        #     ))

        response = self.post(
            self._register_endpoint,
            data={
                'endpoint': endpoint,
                'path_to_source': path_to_source,
            }
        )
        if response.text != self._expected_register_output:
            raise EndpointRegistrationError(response.text)

__server_singleton = NodeServer()


def get_server():
    """
    Returns a singleton of NodeServer
    """
    return __server_singleton