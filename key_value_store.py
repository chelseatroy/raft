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

    def catch_up(self):
        if os.path.exists(self.server_name + "_log.txt"):
            f = open(self.server_name + "_log.txt", "r")
            log = f.read()
            f.close()

            for command in log.split('\n'):
                self.execute(command, write=False)

        self.catch_up_successful = True

    def get_latest_term(self):
        if not self.catch_up_successful:
            print("This store isn't caught up, so it doesn't know what term we're in!")
            return

        return self.latest_term


    def execute(self, string_operation, write=True):
        if write:
            command, key, values = 0, 1, 2
            term = self.latest_term
        else:
            term, command, key, values = 0, 1, 2, 3

        if len(string_operation) == 0:
            return

        self.log.append(string_operation)


        operands = string_operation.split(" ")

        response = "Sorry, I don't understand that command."

        with self.client_lock:
            if not write:
                self.latest_term = int(operands[term])

            if operands[command] == "get":
                response = self.get(operands[key])
            elif operands[command] == "set":
                value = " ".join(operands[values:])
                if write:
                    self.write_to_log(term, string_operation)
                self.set(operands[key], value)
                response = f"key {operands[key]} set to {value}"
            elif operands[command] == "delete":
                if write:
                    self.write_to_log(term, string_operation)
                self.delete(operands[key])
                response = f"key {key} deleted"
            elif operands[command] == "show":
                response = str(self.data)
            else:
                pass

        return response

    def write_to_log(self, current_term, string_operation):
        f = open(self.server_name + "_log.txt", "a+")
        f.write(str(current_term) + " " + string_operation + '\n')
        f.close()