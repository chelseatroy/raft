import socket
import sys

data = {}


def get(key):
    return data[key]

def set(key, value):
    data[key] = value

def delete(key):
    del data[key]

def run_server():
    server_address = ('localhost', 10000)
    print(f"starting up on {server_address[0]} port {server_address[1]}")

    sock = socket.socket()
    sock.bind(server_address)
    sock.listen(1)
    while True:
        print('waiting for a connection')
        connection, client_address = sock.accept()

        try:
            print(f"connection from {client_address}")

            # Receive the data in small chunks and retransmit it
            while True:
                operation = connection.recv(16)
                string_operation = operation.decode("utf-8")

                print(f"received {string_operation} of type {type(string_operation)}")
                if operation:
                    command, key, value = 0,1,2
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

                    connection.sendall(response.encode('utf-8'))

                else:
                    print(f"no more data from {client_address}")
                    break

        finally:
            # Clean up the connection
            connection.close()

run_server()
