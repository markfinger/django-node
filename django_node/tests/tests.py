import os
import shutil
import unittest
import json
import six
from django_node import node, npm
from django_node.exceptions import OutdatedDependency, MalformedVersionInput

TEST_DIR = os.path.abspath(os.path.dirname(__file__))
PATH_TO_NODE_MODULES = os.path.join(TEST_DIR, 'node_modules')
DEPENDENCY_PACKAGE = 'yargs'
PATH_TO_INSTALLED_PACKAGE = os.path.join(PATH_TO_NODE_MODULES, DEPENDENCY_PACKAGE)
PACKAGE_TO_INSTALL = 'jquery'
PATH_TO_PACKAGE_TO_INSTALL = os.path.join(PATH_TO_NODE_MODULES, PACKAGE_TO_INSTALL)
PATH_TO_PACKAGE_JSON = os.path.join(TEST_DIR, 'package.json')


class TestDjangoNode(unittest.TestCase):
    package_json_contents = ''

    def read_package_json(self):
        with open(PATH_TO_PACKAGE_JSON, 'r') as package_json_file:
            return package_json_file.read()

    def write_package_json(self, contents):
        with open(PATH_TO_PACKAGE_JSON, 'w+') as package_json_file:
            package_json_file.write(contents)

    def setUp(self):
        self.package_json_contents = self.read_package_json()

    def tearDown(self):
        if os.path.exists(PATH_TO_NODE_MODULES):
            shutil.rmtree(PATH_TO_NODE_MODULES)
        self.write_package_json(self.package_json_contents)

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