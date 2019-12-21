import threading
from socket import *

from src.message_pass import *

from src.key_value_store import KeyValueStore
from src.idk_some_shit import respond, address_of


class Server:
    def __init__(self, name, port=10000):
        self.port = port
        self.name = name
        self.key_value_store = KeyValueStore(server_name=name)
        self.key_value_store.catch_up()
        self.term = self.key_value_store.get_latest_term()

    def tell(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        self.client_socket = socket(AF_INET, SOCK_STREAM)

        try:
            self.client_socket.connect(to_server_address)
            encoded_message = message.encode('utf-8')

            try:
                print(f"sending {encoded_message} to {to_server_address}")
                send_message(self.client_socket, encoded_message)
            except Exception as e:
                print(f"closing socket due to {str(e)}")
                self.client_socket.close()
        except OSError as e:
            print("Bad file descriptor, supposedly: " + str(e))
        except ConnectionRefusedError as e:
            print(f"Ope, looks like {to_server_address[0]} port {to_server_address[1]} isn't up right now")


    def start(self):
        server_address = ('localhost', self.port)

        f = open("logs/server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port " + str(server_address[1]))

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(5)

        while True:
            connection, client_address = self.server_socket.accept()
            print("connection from " + str(client_address))

            threading.Thread(target=self.handle_client, args=(connection, self.key_value_store)).start()

    def handle_client(self, connection, kvs):
        while True:
            print('waiting for a connection')

            try:
                while True:
                    operation = receive_message(connection)

                    if operation:
                        destination, response = respond(self, kvs, operation)

                        if destination == "client":
                            send_message(connection, response.encode('utf-8'))
                        else:
                            self.tell(response, to_server_address=address_of(destination))

                    else:
                        print("no more data")
                        break

            finally:
                connection.close()