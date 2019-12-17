import threading

class KeyValueStore:
    client_lock = threading.Lock()

    def __init__(self):
        self.data = {}
        self.log = []

    def get(self, key):
        return self.data.get(key, '')

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

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
                self.set(operands[key], value)
                response = f"key {operands[key]} set to {value}"
            elif operands[command] == "delete":
                self.delete(operands[key])
                response = f"key {key} deleted"
            elif operands[command] == "show":
                response = str(self.data)
            else:
                pass


        return response