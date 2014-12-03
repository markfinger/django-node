import unittest
from .environment import (
    node_installed, node_version, node_version_string,
    npm_installed, npm_version, npm_version_string,
    ensure_node_version_gte, ensure_npm_version_gte
)
from .exceptions import OutdatedVersionException, MalformedVersionInputException


class TestDjangoNode(unittest.TestCase):
    def test_node_installed(self):
        self.assertTrue(node_installed)

    def test_node_version_string(self):
        self.assertTrue(isinstance(node_version_string, basestring))
        self.assertGreater(len(node_version_string), 0)

    def test_node_version(self):
        self.assertTrue(isinstance(node_version, tuple))
        self.assertGreaterEqual(len(node_version), 3)
        
    def test_npm_installed(self):
        self.assertTrue(npm_installed)

    def test_npm_version_string(self):
        self.assertTrue(isinstance(npm_version_string, basestring))
        self.assertGreater(len(npm_version_string), 0)

    def test_npm_version(self):
        self.assertTrue(isinstance(npm_version, tuple))
        self.assertGreaterEqual(len(npm_version), 3)

    def test_ensure_node_version_greater_than(self):
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, 'v99999.0.0')
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, '99999.0.0')
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, (None,))
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, (10,))
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, (999999999,))
        self.assertRaises(MalformedVersionInputException, ensure_node_version_gte, (999999999, 0,))

        self.assertRaises(OutdatedVersionException, ensure_node_version_gte, (999999999, 0, 0,))

        ensure_node_version_gte((0, 0, 0,))
        ensure_node_version_gte((0, 9, 99999999))
        ensure_node_version_gte((0, 10, 33,))

    def test_ensure_npm_version_greater_than(self):
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, 'v99999.0.0')
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, '99999.0.0')
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, (None,))
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, (10,))
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, (999999999,))
        self.assertRaises(MalformedVersionInputException, ensure_npm_version_gte, (999999999, 0,))

        self.assertRaises(OutdatedVersionException, ensure_npm_version_gte, (999999999, 0, 0,))

        ensure_npm_version_gte((0, 0, 0,))
        ensure_npm_version_gte((0, 9, 99999999))
        ensure_npm_version_gte((2, 1, 8,))