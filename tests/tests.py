import os
import shutil
import unittest
import json
from django.utils import six
from django_node import node, npm
from django_node.node_server import NodeServer
from django_node.server import server
from django_node.exceptions import (
    OutdatedDependency, MalformedVersionInput, NodeServerError, NodeServerAddressInUseError, NodeServerTimeoutError,
)

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_TO_NODE_MODULES = os.path.join(TEST_DIR, 'node_modules')
DEPENDENCY_PACKAGE = 'yargs'
PATH_TO_INSTALLED_PACKAGE = os.path.join(PATH_TO_NODE_MODULES, DEPENDENCY_PACKAGE)
PACKAGE_TO_INSTALL = 'jquery'
PATH_TO_PACKAGE_TO_INSTALL = os.path.join(PATH_TO_NODE_MODULES, PACKAGE_TO_INSTALL)
PATH_TO_PACKAGE_JSON = os.path.join(TEST_DIR, 'package.json')
TEST_SERVICE_PATH_TO_SOURCE = os.path.join(TEST_DIR, 'test_service.js')
TIMEOUT_SERVICE_PATH_TO_SOURCE = os.path.join(TEST_DIR, 'timeout_service.js')


class TestDjangoNode(unittest.TestCase):

    def setUp(self):
        self.package_json_contents = self.read_package_json()

    def tearDown(self):
        if os.path.exists(PATH_TO_NODE_MODULES):
            shutil.rmtree(PATH_TO_NODE_MODULES)
        self.write_package_json(self.package_json_contents)
        if server.has_started:
            # Reset the server
            server.stop()

    def read_package_json(self):
        with open(PATH_TO_PACKAGE_JSON, 'r') as package_json_file:
            return package_json_file.read()

    def write_package_json(self, contents):
        with open(PATH_TO_PACKAGE_JSON, 'w+') as package_json_file:
            package_json_file.write(contents)

    def test_node_is_installed(self):
        self.assertTrue(node.is_installed)

    def test_node_version_raw(self):
        self.assertTrue(isinstance(node.version_raw, six.string_types))
        self.assertGreater(len(node.version_raw), 0)

    def test_node_version(self):
        self.assertTrue(isinstance(node.version, tuple))
        self.assertGreaterEqual(len(node.version), 3)
        
    def test_npm_is_installed(self):
        self.assertTrue(npm.is_installed)

    def test_npm_version_raw(self):
        self.assertTrue(isinstance(npm.version_raw, six.string_types))
        self.assertGreater(len(npm.version_raw), 0)

    def test_npm_version(self):
        self.assertTrue(isinstance(npm.version, tuple))
        self.assertGreaterEqual(len(npm.version), 3)

    def test_ensure_node_installed(self):
        node.ensure_installed()

    def test_ensure_npm_installed(self):
        npm.ensure_installed()

    def test_ensure_node_version_greater_than(self):
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, 'v99999.0.0')
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, '99999.0.0')
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, (None,))
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, (10,))
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, (999999999,))
        self.assertRaises(MalformedVersionInput, node.ensure_version_gte, (999999999, 0,))

        self.assertRaises(OutdatedDependency, node.ensure_version_gte, (999999999, 0, 0,))

        node.ensure_version_gte((0, 0, 0,))
        node.ensure_version_gte((0, 9, 99999999))
        node.ensure_version_gte((0, 10, 33,))

    def test_ensure_npm_version_greater_than(self):
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, 'v99999.0.0')
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, '99999.0.0')
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, (None,))
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, (10,))
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, (999999999,))
        self.assertRaises(MalformedVersionInput, npm.ensure_version_gte, (999999999, 0,))

        self.assertRaises(OutdatedDependency, npm.ensure_version_gte, (999999999, 0, 0,))

        npm.ensure_version_gte((0, 0, 0,))
        npm.ensure_version_gte((0, 9, 99999999))
        npm.ensure_version_gte((2, 1, 8,))

    def test_node_run_returns_output(self):
        stderr, stdout = node.run('--version',)
        stdout = stdout.strip()
        self.assertEqual(stdout, node.version_raw)

    def test_npm_run_returns_output(self):
        stderr, stdout = npm.run('--version',)
        stdout = stdout.strip()
        self.assertEqual(stdout, npm.version_raw)

    def test_npm_install_installs_packages(self):
        stderr, stdout = npm.install(TEST_DIR, silent=True)
        self.assertTrue(os.path.exists(PATH_TO_NODE_MODULES))
        self.assertTrue(os.path.exists(PATH_TO_INSTALLED_PACKAGE))
        self.assertIn(DEPENDENCY_PACKAGE, stdout)

    def test_npm_install_can_install_a_specific_package(self):
        stderr, stdout = npm.install(TEST_DIR, PACKAGE_TO_INSTALL, silent=True)
        self.assertTrue(os.path.exists(PATH_TO_NODE_MODULES))
        self.assertTrue(os.path.exists(PATH_TO_PACKAGE_TO_INSTALL))
        self.assertIn(PACKAGE_TO_INSTALL, stdout)

    def test_npm_install_can_install_a_specific_package_and_save_to_package_json(self):
        stderr, stdout = npm.install(TEST_DIR, PACKAGE_TO_INSTALL, '--save', silent=True)
        self.assertTrue(os.path.exists(PATH_TO_NODE_MODULES))
        self.assertTrue(os.path.exists(PATH_TO_PACKAGE_TO_INSTALL))
        self.assertIn(PACKAGE_TO_INSTALL, stdout)
        package_json_contents = self.read_package_json()
        package_json = json.loads(package_json_contents)
        self.assertIn('jquery', package_json['dependencies'])

    def test_node_server_can_start_and_stop(self):
        self.assertIsInstance(server, NodeServer)
        server.start()
        self.assertTrue(server.has_started)
        self.assertFalse(server.has_stopped)
        self.assertTrue(server.test())
        server.stop()
        self.assertFalse(server.has_started)
        self.assertTrue(server.has_stopped)
        self.assertFalse(server.test())
        server.start()
        self.assertTrue(server.has_started)
        self.assertFalse(server.has_stopped)
        self.assertTrue(server.test())
        server.stop()
        self.assertFalse(server.has_started)
        self.assertTrue(server.has_stopped)
        self.assertFalse(server.test())

    def test_node_server_can_add_an_endpoint(self):
        endpoint = '/test-endpoint'
        server.add_service(endpoint, TEST_SERVICE_PATH_TO_SOURCE)
        expected_output = 'NodeServer test-endpoint'
        response = server.get_service(endpoint, params={
            'output': expected_output
        })
        self.assertEqual(response.text, expected_output)

    def test_node_server_returns_a_service_when_adding_one(self):
        service = server.add_service('/test-endpoint', TEST_SERVICE_PATH_TO_SOURCE)
        self.assertEqual(service.endpoint, '/test-endpoint')
        self.assertEqual(service.server_name, server.get_server_name())
        expected_output = 'NodeServer test-endpoint'
        response = service(output=expected_output)
        self.assertEqual(response.text, expected_output)

    def test_node_server_cannot_add_an_endpoint_without_an_opening_slash(self):
        malformed_endpoint = 'malformed_endpoint'
        self.assertRaises(NodeServerError, server.add_service, malformed_endpoint, TEST_SERVICE_PATH_TO_SOURCE)
        server.add_service('/' + malformed_endpoint, TEST_SERVICE_PATH_TO_SOURCE)

    def test_node_server_can_check_the_endpoints_added(self):
        endpoint = '/test-endpoint'
        self.assertNotIn(endpoint, server.get_endpoints())
        server.add_service(endpoint, TEST_SERVICE_PATH_TO_SOURCE)
        self.assertIn(endpoint, server.get_endpoints())

    def test_node_server_cannot_add_certain_endpoints(self):
        for endpoint in server._blacklisted_endpoints:
            self.assertRaises(NodeServerError, server.add_service, endpoint, TEST_SERVICE_PATH_TO_SOURCE)

    def test_node_server_process_can_rely_on_externally_controlled_processes(self):
        self.assertFalse(server.test())
        new_server = NodeServer()
        new_server.start()
        self.assertTrue(server.test())
        new_server.stop()
        self.assertFalse(new_server.test())
        self.assertFalse(server.test())

    def test_node_server_process_can_raise_on_port_collisions(self):
        self.assertFalse(server.test())
        new_server = NodeServer()
        new_server.start()
        self.assertTrue(server.test())
        self.assertEqual(server.address, new_server.address)
        self.assertEqual(server.port, new_server.port)
        self.assertRaises(NodeServerAddressInUseError, server.start, use_existing_process=False)
        new_server.stop()
        self.assertFalse(server.test())
        server.start(use_existing_process=False)
        self.assertTrue(server.test())

    def test_node_server_processes_can_share_endpoints(self):
        new_server = NodeServer()
        new_server.start()
        service_on_new_server = new_server.add_service('/test-endpoint', TEST_SERVICE_PATH_TO_SOURCE)
        self.assertEqual(service_on_new_server(output='test').text, 'test')
        self.assertIn('/test-endpoint', server.get_endpoints())
        service_on_server = server.service_factory('test-endpoint')
        self.assertEqual(service_on_server(output='test').text, 'test')
        new_server.stop()
        self.assertFalse(server.test())

    def test_node_server_throws_timeout_on_long_running_services(self):
        service = server.add_service('/long-running-service', TIMEOUT_SERVICE_PATH_TO_SOURCE)
        # Temporarily lower the timeout threshold
        default_timeout = server.timeout
        server.timeout = 2
        self.assertRaises(NodeServerTimeoutError, service)
        server.timeout = default_timeout