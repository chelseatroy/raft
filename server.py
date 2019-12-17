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
        self.kvs = KeyValueStore()

    def destination_addresses(self):
        other_servers = {k: v for (k, v) in server_nodes().items() if k != self.name}
        return list(other_servers.values())

    def start(self):
        server_address = ('localhost', self.port)

        f = open("server_registry.txt", "a")
        f.write(self.name + " localhost " + str(self.port) + '\n')
        f.close()

        print("starting up on " + str(server_address[0]) + " port "  + str(server_address[1]))

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

                        if string_operation == "log_length?":
                            response = "log_length " + str(len(self.kvs.log))
                        elif string_operation.split(" ")[0] == "log_length":
                            catch_up_start_index = int(string_operation.split(" ")[1])

                            if len(self.kvs.log) > catch_up_start_index:
                                response = "catch_up_logs " + str(self.kvs.log[catch_up_start_index:])
                            else:
                                response = "Your info is as good as mine!"
                        elif string_operation.split(" ")[0] == "catch_up_logs":
                            logs_to_append = ast.literal_eval(string_operation.split("catch_up_logs ")[1])
                            [self.kvs.execute(log) for log in logs_to_append]

                            response = "Caught up. Thanks!"
                        elif string_operation == "show_log":
                            response = str(self.kvs.log)
                        else:
                            response = kvs.execute(string_operation)

                        send_message(connection, response.encode('utf-8'))

                    else:
                        print("no more data")
                        break

            finally:
                connection.close()
