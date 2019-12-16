import json

class KeyValueStore:
    def __init__(self):
        self.data = {}

    def get(self, key):
        return self.data[key]

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def execute(self, string_operation):
        command, key, value = 0, 1, 2
        operands = string_operation.split(" ")

        response = "Sorry, I don't understand that command."

        if operands[command] == "get":
            response = self.get(operands[key])
        elif operands[command] == "set":
            self.set(operands[key], operands[value])
            response = f"key {operands[key]} set to {operands[value]}"
        elif operands[command] == "delete":
            self.delete(operands[key])
            response = f"key {key} deleted"
        elif operands[command] == "show":
            response = str(self.data)
        else:
            pass


        return response