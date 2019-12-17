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

    def destination_addresses(self):
        other_servers = {k: v for (k, v) in server_nodes().items() if k != self.name}
        return list(other_servers.values())

    def start(self):
        server_address = ('localhost', self.port)

        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port "  + str(server_address[1]))
        print(self.destination_addresses())

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

                        response = kvs.execute(string_operation)
                        send_message(connection, response.encode('utf-8'))

                    else:
                        print("no more data")
                        break

            finally:
                connection.close()

    #
    # def catch_up(self, key_value_store):
    #     f = open("commands.txt", "r")
    #     log = f.read()
    #     f.close()
    #
    #     for command in log.split('\n'):
    #         key_value_store.execute(command)


