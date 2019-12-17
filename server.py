from socket import *
import threading
from key_value_store import KeyValueStore
from message_pass import *
from config import server_nodes

class Server:
    def __init__(self, name, port=10000):
        self.port = port
        self.name = name
        self.kvs = KeyValueStore()
        self.catch_up(self.kvs)

    def start(self):
        server_address = ('localhost', self.port)
        print("starting up on " + str(server_address[0]) + "port "  +str(server_address[1]))
        server_nodes[self.name] = server_address
        print(str(server_nodes))

        sock = socket()
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        sock.bind(server_address)
        sock.listen(1)

        while True:
            connection, client_address = sock.accept()
            print("connection from " + str(client_address))

            threading.Thread(target=self.handle_client, args=(connection, self.kvs)).start()

    def handle_client(self, connection, kvs):
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


    def catch_up(self, key_value_store):
        f = open("commands.txt", "r")
        log = f.read()
        f.close()

        for command in log.split('\n'):
            key_value_store.execute(command)


