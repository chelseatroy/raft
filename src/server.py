import threading
from socket import *
import time

from src.message_pass import *

from src.key_value_store import KeyValueStore
from src.parsing import address_of, with_return_address, broadcast, return_address_and_message
from src.append_entries_call import AppendEntriesCall

from src.config import other_server_names, server_nodes, destination_addresses
import ast


class Server:
    def __init__(self, name, port=10000, leader=False):
        self.port = port
        self.name = name
        self.key_value_store = KeyValueStore(server_name=name)
        self.key_value_store.catch_up()
        self.term = self.key_value_store.get_latest_term()
        self.leader = leader
        self.followers_with_update_status = {}
        self.current_operation = ''
        self.current_operation_committed = False

        for server_name in other_server_names(name):
            self.followers_with_update_status[server_name] = False

    def send(self, message, to_server_address):
        print(f"connecting to {to_server_address[0]} port {to_server_address[1]}")

        peer_socket = socket(AF_INET, SOCK_STREAM)

        try:
            peer_socket.connect(to_server_address)
            encoded_message = message.encode('utf-8')

            try:
                print(f"sending {encoded_message} to {to_server_address}")
                send_message(peer_socket, encoded_message)
                time.sleep(0.5)
                peer_socket.close()
            except Exception as e:
                print(f"closing socket due to {str(e)}")
                peer_socket.close()
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
        self.server_socket.listen(6000)

        if self.leader:
            self.prove_aliveness()

        while True:
            connection, client_address = self.server_socket.accept()
            print("connection from " + str(client_address))

            threading.Thread(target=self.manage_messaging, args=(connection, self.key_value_store)).start()

    def prove_aliveness(self):
        print("Sending Heartbeat!")
        if self.leader:
            broadcast(self, with_return_address(
                self,
                AppendEntriesCall(
                    previous_index=self.key_value_store.highest_index,
                    previous_term=self.key_value_store.latest_term,
                    entries=[]
                ).to_message()
            ))
            threading.Timer(5.0, self.prove_aliveness).start()

    def mark_updated(self, server_name):
        self.followers_with_update_status[server_name] = True

        trues = len(list(filter(lambda x: x is True, self.followers_with_update_status.values())))
        falses = len(list(filter(lambda x: x is False, self.followers_with_update_status.values())))
        if trues >= falses:
            print("Committing entry: " + self.current_operation)
            self.current_operation_committed = True
            self.key_value_store.write_to_state_machine(self.current_operation, term_absent=True, write=False)
            broadcast(self, with_return_address(self, "commit_entries ['" + self.current_operation + "']"))

            self.current_operation_committed = False
            for server_name in other_server_names(self.name):
                self.followers_with_update_status[server_name] = False


    # Thinks it's not used but actually it is in a thread above
    def manage_messaging(self, connection, kvs):
        try:
            while True:
                operation = receive_message(connection)

                if operation:
                    destination, response = self.respond(kvs, operation)

                    if response == '':
                        break

                    if destination == "client":
                        send_message(connection, response.encode('utf-8'))
                    else:
                        self.send(response, to_server_address=address_of(destination))

                else:
                    print("no more data")
                    break

        finally:
            connection.close()

    def respond(self, key_value_store, operation):
        send_pending = True
        string_request = operation.decode("utf-8")
        server_name, string_operation = return_address_and_message(string_request)
        print("from " + server_name + ": received " + string_operation)

        response = ''

        if string_operation.split(" ")[0] == "append_entries":
            # followers do this to update their logs.
            call = AppendEntriesCall.from_message(string_operation)

            if self.key_value_store.command_at(
                call.previous_index,
                call.previous_term
            ) != None:
                key_value_store.remove_logs_after_index(call.previous_index)
                [key_value_store.write_to_log(log, term_absent=False) for log in call.entries]
                print("State machine after appending: " + str(key_value_store.data))

                response = "Append entries call successful!"
            else:
                response = "append_entries_unsuccessful. Please send log prior to: " + str(call.previous_index) + " " + str(call.previous_term)
        elif string_operation.split(" ")[0] == "append_entries_unsuccessful.":

            response_components = string_operation.split(" ")
            max_index = len(response_components)

            latest_tried_index = int(response_components[max_index - 2])
            latest_tried_term = int(response_components[max_index - 1])

            log_position = self.key_value_store.log_access_object().ordered_logs.index(
                str(latest_tried_index) + " " + str(latest_tried_term)
            )

            #TODO: if log_position < 1:
                #if we are starting from scratch

            ordered_logs = self.key_value_store.log_access_object().ordered_logs
            term_indexed_logs = self.key_value_store.log_access_object().term_indexed_logs
            new_key_to_try = ordered_logs[log_position - 1]

            new_values_to_send = list(
                map(
                    lambda x: term_indexed_logs[x],
                    ordered_logs[log_position:]
                )
            )

            try_this_index = new_key_to_try.split(" ")[0]
            try_this_term = new_key_to_try.split(" ")[1]

            response = AppendEntriesCall(
                previous_index=try_this_index,
                previous_term=try_this_term,
                entries=new_values_to_send
            ).to_message()

        elif string_operation.split(" ")[0] == "commit_entries":
            # followers do this to update their logs.
            stringified_logs_to_append = string_operation.replace("commit_entries ", "")
            print("Preparing to commit: " + stringified_logs_to_append)
            logs_to_append = ast.literal_eval(stringified_logs_to_append)
            [key_value_store.write_to_state_machine(command, term_absent=True) for command in logs_to_append]

            response = "Commit entries call successful!"
            print("State machine after committing: " + str(key_value_store.data))
        elif string_operation in [
            "Caught up. Thanks!",
            "Sorry, I don't understand that command.",
            "Broadcasting to other servers to catch up their logs.",
            "Commit entries call successful!",
        ]:
            send_pending = False
        elif string_operation == "Append entries call successful!":
            if self.leader:
                self.mark_updated(server_name)
            send_pending = False
        else:
            if self.leader:
                self.current_operation = string_operation

                if self.current_operation.split(" ")[0] in ["set", "delete"]:
                    key_value_store.write_to_log(string_operation, term_absent=True)
                    broadcast(self, with_return_address(
                        self,
                        AppendEntriesCall(
                            previous_index=self.key_value_store.highest_index - 1, #because we incremented it to update our own logs
                            previous_term=self.key_value_store.latest_term,
                            entries=[self.current_operation]
                        ).to_message()
                    ))

                    while not self.current_operation_committed:
                        pass

                    send_pending = False
                    #TODO: Something about this block closes the connection
                else:
                    response = key_value_store.read(self.current_operation)
            else:
                response = "I am not the leader. Please leave me alone."

        if send_pending:
            response = with_return_address(self, response)

        return server_name, response
