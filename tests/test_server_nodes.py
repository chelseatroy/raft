from unittest import TestCase
from src.config import server_nodes


class TestServer_nodes(TestCase):
    def test_server_nodes(self):
        registry = server_nodes("tests/example_registry.txt")

        assert registry["Dorian"] == ('localhost', 10002)
        assert registry["Basil"] == ('localhost', 10001)
