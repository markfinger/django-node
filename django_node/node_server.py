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
from .exceptions import NodeServerConnectionError, NodeServerStartError, NodeServerError, ErrorAddingEndpoint


class ServerEndpoint(object):
    server = None
    endpoint = None

    def __init__(self, server, endpoint):
        self.server = server
        self.endpoint = endpoint

    def get(self, params=None):
        return self.server.get(self.endpoint, params=params)

    def post(self, data=None):
        return self.server.post(self.endpoint, data=data)


class NodeServer(object):
    """
    A persistent Node server which sits alongside the python process
    and responds over HTTP
    """
    # TODO: replace the debug prints with django logger calls

    debug = SERVER_DEBUG
    path_to_source = os.path.join(os.path.dirname(__file__), 'server.js')
    start_on_init = False
    resolve_dependencies_on_init = True
    shutdown_on_exit = True
    protocol = 'http'
    desired_address = '127.0.0.1'
    desired_port = '0'
    address = None
    port = None
    has_started = False
    has_stopped = False

    _test_endpoint = '/__test__'
    _add_endpoint = '/__add__'

    _expected_startup_output = 'Started NodeServer'
    _expected_test_output = 'NodeServer running {token}'.format(
        token=uuid.uuid4(),
    )
    _expected_add_output = 'Added endpoint {token}'.format(
        token=uuid.uuid4(),
    )

    _process = None
    _startup_output = None
    _server_details_json = None
    _server_details = None

    def __init__(self):
        if self.resolve_dependencies_on_init:
            # Ensure that the external dependencies are met
            node.ensure_version_gte(NODE_VERSION_REQUIRED)
            npm.ensure_version_gte(NPM_VERSION_REQUIRED)

            # Ensure that the required packages have been installed
            npm.install(os.path.dirname(__file__))

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
            '--address', self.desired_address,
            '--port', self.desired_port,
            '--expected-startup-output', self._expected_startup_output,
            '--test-endpoint', self._test_endpoint,
            '--expected-test-output', self._expected_test_output,
            '--add-endpoint', self._add_endpoint,
            '--expected-add-output', self._expected_add_output,
        )

        # While rendering templates Django will silently ignore some types of exceptions,
        # so we need to intercept them and raise our own class of exception
        try:
            self._process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        except (TypeError, AttributeError):
            msg = 'Failed to start server with {arguments}'.format(arguments=arguments)
            six.reraise(NodeServerStartError, NodeServerStartError(msg), sys.exc_info()[2])

        # Check the first line of the server's output to ensure that it has started successfully
        self._startup_output = self._process.stdout.readline().decode()
        if self._startup_output.strip() != self._expected_startup_output:
            self._startup_output += self._process.stdout.read().decode()
            self.stop()
            raise NodeServerStartError(
                'Error starting server: {startup_output}'.format(
                    startup_output=self._startup_output
                )
            )

        server_details_json = self._process.stdout.readline()
        self._server_details_json = server_details_json.decode()
        self._server_details = json.loads(self._server_details_json)

        # If the server is defining its own address or port, we need to record it
        self.address = self._server_details['address']
        self.port = self._server_details['port']

        self.has_started = True
        self.has_stopped = False

        # Ensure that we can connect to the server over the network
        if not self.test():
            self.stop()
            raise NodeServerStartError(
                'Cannot test server to determine if startup successful. Tried {test_url}'.format(
                    test_url=self.get_test_url()
                )
            )

        if self.debug:
            print('NodeServer now listening at {server_url}'.format(
                server_url=self.get_server_url()
            ))

    def stop(self):
        if self.debug:
            print('Stopping NodeServer...'.format(
                server_url=self.get_server_url()
            ))

        if self._process is not None and not self.has_stopped:
            self._process.terminate()

        self.has_stopped = True
        self.has_started = False

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

        return self._check_response(url, response)

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

        return self._check_response(url, response)

    def get_server_url(self):
        return '{protocol}://{address}:{port}'.format(
            protocol=self.protocol,
            address=self.address,
            port=self.port,
        )

    def absolute_url(self, url):
        return '{server_url}{separator}{url}'.format(
            server_url=self.get_server_url(),
            separator='/' if not url.startswith('/') else '',
            url=url,
        )

    def get_test_url(self):
        return self.absolute_url(self._test_endpoint)

    def _clean_html_output(self, html):
        # Convert the error message from HTML to plain text
        html = html.replace('<br>', '\n')
        html = html.replace('&nbsp;', ' ')
        html = html.replace('&quot;', '"')
        # Remove multiple spaces
        html = ' '.join(html.split())
        return html

    def _check_response(self, url, response):
        if response.status_code != 200:
            error_message = self._clean_html_output(response.text)
            raise NodeServerError(
                'Error at {url}: {error_message}'.format(
                    url=url,
                    error_message=error_message,
                )
            )

        return response

    def test(self):
        if self.debug:
            print('Testing server at {server_url}'.format(
                server_url=self.get_server_url()
            ))

        test_url = self.get_test_url()

        try:
            response = requests.get(test_url)
        except ConnectionError:
            return False

        if response.status_code != 200:
            return False

        return response.text == self._expected_test_output

    def add_endpoint(self, endpoint, path_to_source):
        if self.debug:
            print('Adding endpoint {endpoint} to {server_url} with source "{path_to_source}"'.format(
                endpoint=endpoint,
                server_url=self.get_server_url(),
                path_to_source=path_to_source,
            ))

        response = self.post(
            self._add_endpoint,
            data={
                'endpoint': endpoint,
                'path_to_source': path_to_source,
            }
        )

        if response.text != self._expected_add_output:
            error_message = self._clean_html_output(response.text)
            raise ErrorAddingEndpoint(error_message)

        return ServerEndpoint(
            server=self,
            endpoint=endpoint
        )