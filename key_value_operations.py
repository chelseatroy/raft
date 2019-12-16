import json

data = {}

def get(key):
    return data[key]

def set(key, value):
    data[key] = value

def delete(key):
    del data[key]

def execute(string_operation):
    command, key, value = 0, 1, 2
    operands = string_operation.split(" ")

    response = "Sorry, I don't understand that command."

    if operands[command] == "get":
        response = get(operands[key])
    elif operands[command] == "set":
        set(operands[key], operands[value])
        response = f"key {operands[key]} set to {operands[value]}"
    elif operands[command] == "delete":
        delete(operands[key])
        response = f"key {key} deleted"
    elif operands[command] == "show":
        response = str(data)
    else:
        pass


    return response