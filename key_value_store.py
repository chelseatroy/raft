import threading
import time
import os

class KeyValueStore:
    client_lock = threading.Lock()

    def __init__(self, server_name):
        self.server_name = server_name
        self.data = {}
        self.log = []

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
                self.execute(command)

    def execute(self, string_operation):
        self.log.append(string_operation)

        command, key = 0, 1
        operands = string_operation.split(" ")

        response = "Sorry, I don't understand that command."

        with self.client_lock:
            if operands[command] == "get":
                response = self.get(operands[key])
            elif operands[command] == "set":
                value = " ".join(operands[2:])
                self.write_to_log(string_operation)
                self.set(operands[key], value)
                response = f"key {operands[key]} set to {value}"
            elif operands[command] == "delete":
                self.write_to_log(string_operation)
                self.delete(operands[key])
                response = f"key {key} deleted"
            elif operands[command] == "show":
                response = str(self.data)
            else:
                pass

        return response

    def write_to_log(self, string_operation):
        f = open(self.server_name + "_log.txt", "a+")
        f.write(string_operation + '\n')
        f.close()