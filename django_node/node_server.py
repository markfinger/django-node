import os
import sys
import atexit
import json
import subprocess
import logging
import re
import requests
from requests.exceptions import ConnectionError, ReadTimeout, Timeout
from django.utils import six
from . import node, npm
from .settings import (
    PATH_TO_NODE, SERVER_PROTOCOL, SERVER_ADDRESS, SERVER_PORT, SERVER_TIMEOUT, SERVER_TEST_TIMEOUT,
    NODE_VERSION_REQUIRED, NPM_VERSION_REQUIRED,
)
from .exceptions import (
    NodeServerConnectionError, NodeServerStartError, NodeServerAddressInUseError, NodeServerError, ErrorAddingService,
    NodeServerTimeoutError
)
from .utils import html_unescape


class NodeServer(object):
    """
    A persistent Node server which sits alongside the python process
    and responds over HTTP
    """

    protocol = SERVER_PROTOCOL
    address = SERVER_ADDRESS
    port = SERVER_PORT
    path_to_source = os.path.join(os.path.dirname(__file__), 'node_server.js')
    start_on_init = False
    resolve_dependencies_on_init = True
    shutdown_on_exit = True
    has_started = False
    has_stopped = False
    logger = logging.getLogger(__name__)
    timeout = SERVER_TIMEOUT
    test_timeout = SERVER_TEST_TIMEOUT

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
        output = output.decode('utf-8')

        if output != self._expected_startup_output:
            # Read in the rest of the error message
            output += self._process.stdout.read().decode('utf-8')
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
                'Server does not appear to be running. Tried to test the server at "{test_endpoint}"'.format(
                    test_endpoint=self._test_endpoint,
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

    def _html_to_plain_text(self, html):
        html = html_unescape(html)
        html = html.decode('utf-8')
        # Replace HTML break rules with new lines
        html = html.replace('<br>', '\n')
        # Remove multiple spaces
        html = re.sub(' +', ' ', html)
        return html

    def _validate_response(self, response, url):
        if response.status_code != 200:
            error_message = self._html_to_plain_text(response.text)
            message = 'Error at {url}: {error_message}'
            if six.PY2:
                # Prevent UnicodeEncodeError
                message = unicode(message)
            raise NodeServerError(message.format(
                url=url,
                error_message=error_message,
            ))

        return response

    def _send_request(self, func, url, **kwargs):
        timeout = kwargs.pop('timeout', self.timeout)

        try:
            return func(url, timeout=timeout, **kwargs)
        except ConnectionError as e:
            six.reraise(NodeServerConnectionError, NodeServerConnectionError(url, *e.args), sys.exc_info()[2])
        except (ReadTimeout, Timeout) as e:
            six.reraise(NodeServerTimeoutError, NodeServerTimeoutError(url, *e.args), sys.exc_info()[2])

    def get_server_name(self):
        return self.__class__.__name__

    def log(self, message):
        self.logger.info(
            '{server_name} [Address: {server_url}] {message}'.format(
                server_name=self.get_server_name(),
                server_url=self.get_server_url(),
                message=message,
            )
        )

    def test(self):
        if self.address is None or self.port is None:
            return False

        self.log('Testing server at {test_endpoint}'.format(test_endpoint=self._test_endpoint))

        absolute_url = self.absolute_url(self._test_endpoint)

        try:
            response = self._send_request(
                requests.get,
                absolute_url,
                timeout=self.test_timeout,
            )
        except (NodeServerConnectionError, NodeServerTimeoutError):
            return False

        if response.status_code != 200:
            return False

        return response.text == self._expected_test_output

    def get_endpoints(self):
        self.ensure_started()

        response = self.get_service(self._get_endpoints_endpoint)

        endpoints = json.loads(response.text)

        return [endpoint for endpoint in endpoints]

    def service_factory(self, endpoint):
        def service(**kwargs):
            return self.get_service(endpoint, params=kwargs)

        service.endpoint = endpoint
        service.server_name = self.get_server_name()

        return service

    def add_service(self, endpoint, path_to_source):
        self.ensure_started()

        if endpoint not in self._blacklisted_endpoints and endpoint in self.get_endpoints():
            return self.service_factory(endpoint)

        self.log('Adding service at "{endpoint}" with source "{path_to_source}"'.format(
            endpoint=endpoint,
            path_to_source=path_to_source,
        ))

        absolute_url = self.absolute_url(self._add_service_endpoint)

        response = self._send_request(
            requests.post,
            absolute_url,
            data={
                'endpoint': endpoint,
                'path_to_source': path_to_source,
            },
        )

        response = self._validate_response(response, absolute_url)

        if response.text != self._expected_add_service_output:
            error_message = self._html_to_plain_text(response.text)
            raise ErrorAddingService(error_message)

        return self.service_factory(endpoint=endpoint)

    def get_service(self, endpoint, params=None):
        self.ensure_started()

        self.log('Sending request to endpoint "{url}" with params "{params}"'.format(
            url=endpoint,
            params=params,
        ))

        absolute_url = self.absolute_url(endpoint)

        response = self._send_request(
            requests.get,
            absolute_url,
            params=params,
        )

        return self._validate_response(response, endpoint)