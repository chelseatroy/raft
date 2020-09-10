import pytest
from src.log_manager import LogManager

TEST_LOG_PATH = "tests/test_kvs_logs.txt"

class TestKeyValueStore():
    def test_get(self):
        kvs = LogManager(server_name="DorianGray")
        kvs.data = {"Sibyl": "cruelty"}
        assert kvs.get("Sibyl") == "cruelty"

    def test_set(self):
        kvs = LogManager(server_name="DorianGray")
        kvs.set("Sibyl", "cruelty")
        assert kvs.get("Sibyl") == "cruelty"

    def test_delete(self):
        kvs = LogManager(server_name="DorianGray")
        kvs.data = {"Sibyl": "cruelty"}
        kvs.delete("Sibyl")
        assert kvs.get("Sibyl") == ""

    def test_write_to_log(self):
        self.clean_up_file(TEST_LOG_PATH)

        kvs = LogManager(server_name="DorianGray")
        kvs.write_to_log("set Sibyl cruelty", TEST_LOG_PATH)
        self.assert_on_file(path=TEST_LOG_PATH, length=1, lines="0 set Sibyl cruelty")

        kvs.write_to_log("Set Basil wrath", TEST_LOG_PATH)
        self.assert_on_file(path=TEST_LOG_PATH, length=2, lines=["0 set Sibyl cruelty", "0 set Basil wrath"])


    def test_catch_up(self):
        self.clean_up_file(TEST_LOG_PATH)

        kvs = LogManager(server_name="DorianGray")
        kvs.write_to_log("0 set Sibyl cruelty", TEST_LOG_PATH)
        kvs.write_to_log("0 set Basil wrath", TEST_LOG_PATH)
        kvs.data = {} #Ensure that in-memory data is empty

        kvs.catch_up(path_to_logs=TEST_LOG_PATH)
        assert kvs.get("Sibyl") == "cruelty"
        assert kvs.get("Basil") == "wrath"


    def test_get_latest_term_before_catchup(self):
        kvs = LogManager(server_name="DorianGray")
        null_latest_term = kvs.get_latest_term()
        assert not null_latest_term

    def test_get_latest_term_after_catchup(self):
        kvs = LogManager(server_name="DorianGray")

        kvs.catch_up(path_to_logs=TEST_LOG_PATH)
        latest_term = kvs.get_latest_term()
        assert latest_term == 0

        kvs.write_to_log("1 set Sibyl cruelty", TEST_LOG_PATH)
        kvs.data = {}

        kvs.catch_up(path_to_logs=TEST_LOG_PATH)

        latest_term = kvs.get_latest_term()
        assert latest_term == 1

    def test_execute_from_client(self):
        self.clean_up_file(TEST_LOG_PATH)
        kvs = LogManager(server_name="DorianGray")

        kvs.write_to_state_machine("set Sibyl cruelty", term_absent=True, path_to_logs=TEST_LOG_PATH)

        self.assert_on_file(path=TEST_LOG_PATH, length=1, lines="0 set Sibyl cruelty")
        assert kvs.get("Sibyl") == "cruelty"

    def test_execute_from_logs_upon_restart(self):
        self.clean_up_file(TEST_LOG_PATH)
        kvs = LogManager(server_name="DorianGray")
        kvs.write_to_log(string_operation="0 set Sibyl cruelty", path_to_logs=TEST_LOG_PATH)
        assert not kvs.get("Sibyl")

        kvs.write_to_state_machine("0 set Sibyl cruelty", term_absent=False, path_to_logs=TEST_LOG_PATH)

        self.assert_on_file(path=TEST_LOG_PATH, length=1, lines="0 set Sibyl cruelty")
        assert kvs.get("Sibyl") == "cruelty"

    def test_execute_from_leader_catchup_command(self):
        self.clean_up_file(TEST_LOG_PATH)
        kvs = LogManager(server_name="DorianGray")
        assert not kvs.get("Sibyl")

        kvs.write_to_state_machine("0 set Sibyl cruelty", term_absent=False, path_to_logs=TEST_LOG_PATH)

        self.assert_on_file(path=TEST_LOG_PATH, length=1, lines="0 set Sibyl cruelty")
        assert kvs.get("Sibyl") == "cruelty"

    def assert_on_file(self, path, length, lines):
        with open(path, "r") as file:
            lines = file.read().splitlines()
            assert len(lines) == length
            for index, line in enumerate(lines):
                assert lines[index] == line

    def clean_up_file(self, filename):
        open(filename, 'w').close()



