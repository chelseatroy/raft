import threading
import time
import os

class KeyValueStore:
    client_lock = threading.Lock()

    def __init__(self, server_name):
        self.server_name = server_name
        self.data = {}
        self.log = []
        self.catch_up_successful = False
        self.latest_term = 0

    def get(self, key):
        return self.data.get(key, '')

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def catch_up(self, path_to_logs):
        if not path_to_logs:
            path_to_logs = "logs/" + self.server_name + "_log.txt"

        if os.path.exists(path_to_logs):
            f = open(path_to_logs, "r")
            log = f.read()
            f.close()

            for command in log.split('\n'):
                self.execute(command, term_absent=False, write=False)

        self.catch_up_successful = True

    def get_latest_term(self):
        if not self.catch_up_successful:
            print("This store isn't caught up, so it doesn't know what term we're in!")
            return

        return self.latest_term


    def execute(self, string_operation, term_absent, write=True, path_to_logs=''):
        print(string_operation)

        if len(string_operation) == 0:
            return

        if term_absent:
            string_operation = str(self.latest_term) + " " + string_operation

        operands = string_operation.split(" ")
        term, command, key, values = 0, 1, 2, 3

        response = "Sorry, I don't understand that command."

        with self.client_lock:
            self.latest_term = int(operands[term])

            if operands[command] == "get":
                response = self.get(operands[key])
            elif operands[command] == "set":
                value = " ".join(operands[values:])

                self.log.append(string_operation)
                if write:
                    self.write_to_log(string_operation, path_to_logs=path_to_logs)
                self.set(operands[key], value)
                response = f"key {operands[key]} set to {value}"
            elif operands[command] == "delete":
                self.log.append(string_operation)
                if write:
                    self.write_to_log(string_operation, path_to_logs=path_to_logs)
                self.delete(operands[key])
                response = f"key {key} deleted"
            elif operands[command] == "show":
                response = str(self.data)
            else:
                pass

        return response

    def write_to_log(self, string_operation, path_to_logs=''):
        if path_to_logs == '':
            path_to_logs = "logs/" + self.server_name + "_log.txt"
        f = open(path_to_logs, "a+")
        f.write(string_operation + '\n')
        f.close()