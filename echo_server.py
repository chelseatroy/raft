import socket
import threading
from key_value_operations import KeyValueStore
from message_pass import *

def run_server():
    kvs = KeyValueStore()
    catch_up(kvs)
    server_address = ('localhost', 10000)
    print("starting up on " + str(server_address[0]) + "port "  +str(server_address[1]))

    sock = socket.socket()
    sock.bind(server_address)
    sock.listen(1)

    while True:
        connection, client_address = sock.accept()
        print("connection from " + str(client_address))

        threading.Thread(target=handle_client, args=(connection, kvs)).start()

def handle_client(connection, kvs):
    while True:
        print('waiting for a connection')

        try:
            while True:
                operation = receive_message(connection)

                if operation:
                    string_operation = operation.decode("utf-8")
                    print("received " + string_operation)

                    f = open("commands.txt", "a")
                    f.write(string_operation + '\n')
                    f.close()

                    response = kvs.execute(string_operation)
                    send_message(connection, response.encode('utf-8'))

                else:
                    print("no more data")
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
