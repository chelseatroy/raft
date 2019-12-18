from socket import *
import threading
from key_value_store import KeyValueStore
from message_pass import *
from config import server_nodes
import ast


class Server:
    def __init__(self, name, port=10000):
        self.port = port
        self.name = name
        self.kvs = KeyValueStore(server_name=name)
        self.kvs.catch_up()

    def destination_addresses(self):
        other_servers = {k: v for (k, v) in server_nodes().items() if k != self.name}
        return list(other_servers.values())

    def address_of(self, server_name):
        return server_nodes()[server_name]

    def tell(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect(to_server_address)
        encoded_message = message.encode('utf-8')

        try:
            print(f"sending {encoded_message} to {to_server_address}")
            send_message(self.client_socket, encoded_message)
        except Exception as e:
            print(f"closing socket")
            self.client_socket.close()


    def start(self):
        server_address = ('localhost', self.port)

        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port " + str(server_address[1]))

        self.server_socket = socket(AF_INET, SOCK_STREAM)
        self.server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.server_socket.bind(server_address)
        self.server_socket.listen(1)

        while True:
            connection, client_address = self.server_socket.accept()
            print("connection from " + str(client_address))

            threading.Thread(target=self.handle_client, args=(connection, self.kvs)).start()

    def handle_client(self, connection, kvs):
        while True:
            print('waiting for a connection')

            try:
                while True:
                    operation = receive_message(connection)

                    if operation:
                        send_pending = True
                        string_request = operation.decode("utf-8")
                        server_name, string_operation = self.return_address_and_message(string_request)

                        print("received " + string_operation)

                        if string_operation == "log_length?":
                            response = "log_length " + str(len(self.kvs.log))
                        elif string_operation.split(" ")[0] == "log_length":
                            catch_up_start_index = int(string_operation.split(" ")[1])

                            if len(self.kvs.log) > catch_up_start_index:
                                response = "catch_up_logs " + str(self.kvs.log[catch_up_start_index:])
                            else:
                                response = "Your info is at least as good as mine!"
                        elif string_operation.split(" ")[0] == "catch_up_logs":
                            logs_to_append = ast.literal_eval(string_operation.split("catch_up_logs ")[1])
                            [self.kvs.execute(log) for log in logs_to_append]

                            response = "Caught up. Thanks!"
                        elif string_operation == "show_log":
                            response = str(self.kvs.log)
                        elif string_operation == "youre_the_leader":
                            self.broadcast(self.with_return_address('log_length?'))
                            response = "Broadcasting to other servers to catch up their logs."
                        elif string_operation in [
                            "Caught up. Thanks!",
                            "Sorry, I don't understand that command.",
                            "Your info is at least as good as mine!",
                            "Broadcasting to other servers to catch up their logs."
                        ]:
                            send_pending = False
                        else:
                            response = kvs.execute(string_operation)

                        if send_pending:
                            response = self.with_return_address(response)

                            if server_name == "client":
                                send_message(connection, response.encode('utf-8'))
                            else:
                                self.tell(response, to_server_address=self.address_of(server_name))

                    else:
                        print("no more data")
                        break

            finally:
                connection.close()

    def return_address_and_message(self, string_request):
        address_with_message = string_request.split("@")
        return address_with_message[0], "@".join(address_with_message[1:])

    def with_return_address(self, response):
        return self.name + "@" + response

    def broadcast(self, message):
        for other_server_address in self.destination_addresses():
            self.tell(message, to_server_address=other_server_address)
