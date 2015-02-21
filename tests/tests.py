import os
import shutil
import unittest
from django.utils import six
from django_node import node, npm
from django_node.node_server import NodeServer
from django_node.server import server
from django_node.base_service import BaseService
from django_node.exceptions import (
    OutdatedDependency, MalformedVersionInput, NodeServiceError, NodeServerAddressInUseError, NodeServerTimeoutError,
    ServiceSourceDoesNotExist, MalformedServiceName
)
from django_node.services import EchoService
from .services import TimeoutService, ErrorService
from .utils import StdOutTrap

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_TO_NODE_MODULES = os.path.join(TEST_DIR, 'node_modules')
DEPENDENCY_PACKAGE = 'yargs'
PATH_TO_INSTALLED_PACKAGE = os.path.join(PATH_TO_NODE_MODULES, DEPENDENCY_PACKAGE)
PACKAGE_TO_INSTALL = 'jquery'
PATH_TO_PACKAGE_TO_INSTALL = os.path.join(PATH_TO_NODE_MODULES, PACKAGE_TO_INSTALL)
PATH_TO_PACKAGE_JSON = os.path.join(TEST_DIR, 'package.json')

echo_service = EchoService()
timeout_service = TimeoutService()
error_service = ErrorService()


class TestDjangoNode(unittest.TestCase):

    maxDiff = None

    def setUp(self):
        self.package_json_contents = self.read_package_json()

    def tearDown(self):
        if os.path.exists(PATH_TO_NODE_MODULES):
            shutil.rmtree(PATH_TO_NODE_MODULES)
        self.write_package_json(self.package_json_contents)
        if server.is_running:
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

    def test_npm_install_can_install_dependencies(self):
        npm.install(TEST_DIR)
        self.assertTrue(os.path.exists(PATH_TO_NODE_MODULES))
        self.assertTrue(os.path.exists(PATH_TO_INSTALLED_PACKAGE))

    def test_node_server_services_can_be_validated(self):
        class MissingSource(BaseService):
            pass
        self.assertRaises(ServiceSourceDoesNotExist, MissingSource.validate)

        class AbsoluteUrlName(EchoService):
            name = 'http://foo.com'
        self.assertRaises(MalformedServiceName, AbsoluteUrlName.validate)

        class MissingOpeningSlashName(EchoService):
            name = 'foo/bar'
        self.assertRaises(MalformedServiceName, MissingOpeningSlashName.validate)

    def test_node_server_services_are_discovered(self):
        for service in (EchoService, ErrorService, TimeoutService):
            self.assertIn(service, server.services)

    def test_node_server_can_start_and_stop(self):
        self.assertIsInstance(server, NodeServer)
        server.start()
        self.assertTrue(server.is_running)
        self.assertTrue(server.test())
        server.stop()
        self.assertFalse(server.is_running)
        self.assertFalse(server.test())
        server.start()
        self.assertTrue(server.is_running)
        self.assertTrue(server.test())
        server.stop()
        self.assertFalse(server.is_running)
        self.assertFalse(server.test())

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

    def test_node_server_config_is_as_expected(self):
        config = server.get_config()
        self.assertEqual(config['address'], server.address)
        self.assertEqual(config['port'], server.port)
        self.assertEqual(config['startup_output'], server.get_startup_output())

        services = (EchoService, ErrorService, TimeoutService)
        self.assertEqual(len(config['services']), len(services))

        service_names = [obj['name'] for obj in config['services']]
        service_sources = [obj['path_to_source'] for obj in config['services']]
        for service in services:
            self.assertIn(service.get_name(), service_names)
            self.assertIn(service.get_path_to_source(), service_sources)

    def test_node_server_echo_service_pumps_output_back(self):
        response = echo_service.send(echo='test content')
        self.assertEqual(response.text, 'test content')

    def test_node_server_throws_timeout_on_long_running_services(self):
        self.assertRaises(NodeServerTimeoutError, timeout_service.send)

    def test_node_server_error_service_works(self):
        self.assertRaises(NodeServiceError, error_service.send)

    def test_node_server_config_management_command_provides_the_expected_output(self):
        from django_node.management.commands.node_server_config import Command

        with StdOutTrap() as output:
            Command().handle()

        self.assertEqual(''.join(output), server.get_serialised_config())