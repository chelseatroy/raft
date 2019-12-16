import socket
from key_value_operations import KeyValueStore

def run_server():
    kvs = KeyValueStore()
    catch_up(kvs)
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

            while True:
                operation = connection.recv(1024)

                if operation:
                    string_operation = operation.decode("utf-8")
                    print(f"received {string_operation}")

                    f = open("commands.txt", "a")
                    f.write(string_operation + '\n')
                    f.close()

                    response = kvs.execute(string_operation)
                    connection.sendall(response.encode('utf-8'))

                else:
                    print(f"no more data from {client_address}")
                    break

        finally:
            connection.close()

def catch_up(key_value_store):
    f = open("commands.txt", "r")
    log = f.read()
    f.close()

    for command in log.split('\n'):
        key_value_store.execute(command)



run_server()
