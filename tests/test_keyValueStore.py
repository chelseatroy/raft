import pytest
from src.key_value_store import KeyValueStore

class TestKeyValueStore():
    def test_get(self):
        kvs = KeyValueStore(server_name="DorianGray")
        kvs.data = {"Sibyl": "cruelty"}
        assert kvs.get("Sibyl") == "cruelty"

    def test_set(self):
        kvs = KeyValueStore(server_name="DorianGray")
        kvs.set("Sibyl", "cruelty")
        assert kvs.get("Sibyl") == "cruelty"

    def test_delete(self):
        kvs = KeyValueStore(server_name="DorianGray")
        kvs.data = {"Sibyl": "cruelty"}
        kvs.delete("Sibyl")
        assert kvs.get("Sibyl") == ""

    def test_write_to_log(self):
        test_log_path = "tests/test_kvs_logs.txt"
        self.cleanup_file(test_log_path)

        kvs = KeyValueStore(server_name="DorianGray")
        kvs.write_to_log("set Sibyl cruelty", test_log_path)
        self.assert_on_file(path=test_log_path, length=2, lines="0 set Sibyl cruelty")

        kvs.write_to_log("Set Basil wrath", test_log_path)
        self.assert_on_file(path=test_log_path, length=3, lines=["0 set Sibyl cruelty", "0 set Basil wrath"])


    def test_catch_up(self):
        test_log_path = "tests/test_kvs_logs.txt"
        self.cleanup_file(test_log_path)

        kvs = KeyValueStore(server_name="DorianGray")
        kvs.write_to_log("0 set Sibyl cruelty", test_log_path)
        kvs.write_to_log("0 set Basil wrath", test_log_path)
        kvs.data = {} #Ensure that in-memory data is empty

        kvs.catch_up(path_to_logs=test_log_path)
        assert kvs.get("Sibyl") == "cruelty"
        assert kvs.get("Basil") == "wrath"


    def test_get_latest_term_before_catchup(self):
        kvs = KeyValueStore(server_name="DorianGray")
        null_latest_term = kvs.get_latest_term()
        assert not null_latest_term

    def test_get_latest_term_after_catchup(self):
        kvs = KeyValueStore(server_name="DorianGray")
        test_log_path = "tests/test_kvs_logs.txt"

        kvs.catch_up(path_to_logs=test_log_path)
        latest_term = kvs.get_latest_term()
        assert latest_term == 0

        kvs.write_to_log("1 set Sibyl cruelty", test_log_path)
        kvs.data = {}

        kvs.catch_up(path_to_logs=test_log_path)

        latest_term = kvs.get_latest_term()
        assert latest_term == 1

    def test_execute(self):
        pass


    def assert_on_file(self, path, length, lines):
        with open(path, "r") as file:
            lines = file.read().split("\n")
            assert len(lines) == length
            for index, line in enumerate(lines):
                assert lines[index] == line

    def cleanup_file(self, filename):
        open(filename, 'w').close()



