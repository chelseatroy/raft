import threading
from socket import *
import time
import random

from src.message_pass import *

from src.log_manager import LogManager
from src.append_entries_call import AppendEntriesCall
from src.request_vote_call import RequestVoteCall

import ast


class Server:
    def __init__(self, name, port=10000, voting=True):
        self.port = port
        self.name = name
        self.log_manager = LogManager(server_name=name)
        self.log_manager.catch_up()
        self.latest_leader = "yet unelected"

        self.leader = False
        self.voting = voting
        self.heartbeat_timer = None

        self.followers_with_update_status = {}
        self.current_operation = ''
        self.current_operation_committed = False

        self.timeout = float(random.randint(10, 18))
        self.election_countdown = threading.Timer(self.timeout, self.start_election)
        print("Server started with timeout of : " + str(self.timeout))
        self.election_countdown.start()

        self.election_allowed = True
        self.allow_election_countdown = threading.Timer(float(10), self.allow_election)
        self.allow_election_countdown.start()

        for server_name in self.log_manager.other_server_names(name):
            self.followers_with_update_status[server_name] = False

        if self.voting:
            self.log_manager.voted_for_me[self.name] = False

    def allow_election(self):
        self.election_allowed = True

    def start_election(self):
        if not self.leader:
            self.log_manager.current_term += 1
            self.timeout = float(random.randint(10, 18))
            self.election_countdown = threading.Timer(self.timeout, self.start_election)
            print("Server reset election timeout to : " + str(self.timeout))
            self.election_countdown.start()

            self.log_manager.voted_for_me[self.name] = True
            self.broadcast(self, self.with_return_address(
                self,
                RequestVoteCall(
                    for_term=str(self.log_manager.current_term),
                    latest_log_index=str(self.log_manager.highest_index),
                    latest_log_term=str(self.log_manager.latest_term_in_logs)
                ).to_message()
            ))

    def send(self, message, to_port):
        print(f"connecting to port {to_port}")

        to_address = ("localhost", int(to_port))

        peer_socket = socket(AF_INET, SOCK_STREAM)

        try:
            peer_socket.connect(to_address)
            encoded_message = message.encode('utf-8')

            try:
                print(f"sending {encoded_message} to {to_port}")
                send_message(peer_socket, encoded_message)
                time.sleep(0.5)
                peer_socket.close()
            except Exception as e:
                print(f"closing socket due to {str(e)}")
                peer_socket.close()
        except OSError as e:
            print("Bad file descriptor, supposedly: " + str(e))
        except ConnectionRefusedError as e:
            print(f"Ope, looks like port {to_port} isn't up right now")


    def start(self):
        server_address = ('localhost', self.port)

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

            threading.Thread(target=self.manage_messaging, args=(connection, self.log_manager)).start()

    def prove_aliveness(self):
        print("Sending Heartbeat!")
        if self.leader:
            self.broadcast(self, self.with_return_address(
                self,
                AppendEntriesCall(
                    in_term=self.log_manager.current_term,
                    previous_index=self.log_manager.highest_index,
                    previous_term=self.log_manager.latest_term_in_logs,
                    entries=[]
                ).to_message()
            ))
            self.heartbeat_timer = threading.Timer(5.0, self.prove_aliveness)
            self.heartbeat_timer.start()

    def mark_updated(self, server_name):
        self.followers_with_update_status[server_name] = True

        trues = len(list(filter(lambda x: x is True, self.followers_with_update_status.values())))
        falses = len(list(filter(lambda x: x is False, self.followers_with_update_status.values())))
        if trues >= falses:
            print("Committing entry: " + self.current_operation)
            self.current_operation_committed = True
            self.log_manager.write_to_state_machine(self.current_operation, term_absent=True)
            self.broadcast(self, self.with_return_address(self, "commit_entries ['" + self.current_operation + "']"))

            self.current_operation_committed = False
            for server_name in self.log_manager.other_server_names(self.name):
                self.followers_with_update_status[server_name] = False

    def mark_voted(self, server_name):
        self.log_manager.voted_for_me[server_name] = True

        trues = len(list(filter(lambda x: x is True, self.log_manager.voted_for_me.values())))
        falses = len(list(filter(lambda x: x is False, self.log_manager.voted_for_me.values())))
        if trues >= falses:
            print("I win the election for term " + str(self.log_manager.current_term) + "!")
            self.log_manager.catch_up(new_leader=True)
            self.leader = True

            self.prove_aliveness()

            for server_name in self.log_manager.voted_for_me.keys():
                self.log_manager.voted_for_me[server_name] = False

        # Thinks it's not used but actually it is in a thread above
    def manage_messaging(self, connection, kvs):
        try:
            while True:
                operation = receive_message(connection)

                if operation:
                    destination_name, destination_port, response = self.respond(kvs, operation)

                    if response == '':
                        break

                    if destination_name == "client":
                        send_message(connection, response.encode('utf-8'))
                    else:
                        self.send(response, to_port=int(destination_port))

                else:
                    print("no more data")
                    break

        finally:
            connection.close()

    def broadcast(self, server, message):
        print("Broadcasting " + message)
        for other_server_address in self.log_manager.destination_addresses(server.name):
            server.send(message, to_port=other_server_address)

    def with_return_address(self, server, response):
        return server.name + "|" + str(server.port) + "@" + response

    def return_address_and_message(self, string_request):
        address_with_message = string_request.split("@")
        name, port = address_with_message[0].split("|")
        return name, port, "@".join(address_with_message[1:])

    def respond(self, log_manager, operation):
        send_pending = True
        string_request = operation.decode("utf-8")
        server_name, server_port, string_operation = self.return_address_and_message(string_request)
        print("from " + server_name + ": received " + string_operation)

        response = ''

        if string_operation.split(" ")[0] == "append_entries":
            call = AppendEntriesCall.from_message(string_operation)

            if call.in_term < self.log_manager.current_term:
                response = "Your term is out of date. You can't be the leader."
            else:
                self.latest_leader = server_name

                self.election_allowed = False
                self.allow_election_countdown.cancel()
                self.allow_election_countdown = threading.Timer(float(10), self.allow_election)
                self.allow_election_countdown.start()

                self.election_countdown.cancel()
                self.election_countdown = threading.Timer(self.timeout, self.start_election)
                self.election_countdown.start()

                self.leader = False
                if self.heartbeat_timer:
                    self.heartbeat_timer.cancel()
                self.log_manager.current_term = call.in_term

                if self.log_manager.command_at(
                    call.previous_index,
                    call.previous_term
                ) != None:
                    log_manager.remove_logs_after_index(call.previous_index)
                    [log_manager.write_to_log(log, term_absent=False) for log in call.entries]
                    print("State machine after appending: " + str(log_manager.data))

                    if self.voting == False:
                        self.broadcast(self, self.with_return_address(
                            self,
                            "I can vote now!"
                        ))
                        self.voting = True
                    response = "Append entries call successful!"
                else:
                    response = "append_entries_unsuccessful. Please send log prior to: " + str(call.previous_index) + " " + str(call.previous_term)
        elif string_operation == "I can vote now!":
            if self.leader:
                if self.log_manager.voted_for_me.get(server_name, "Not already voting") == "Not already voting":
                    log_manager.write_to_log(f"register {server_name} voting", term_absent=True)
                else:
                    send_pending = False
            else:
                send_pending = False
        elif string_operation.split(" ")[0] == "append_entries_unsuccessful.":

            response_components = string_operation.split(" ")
            max_index = len(response_components)

            latest_tried_index = int(response_components[max_index - 2])
            latest_tried_term = int(response_components[max_index - 1])

            log_position = self.log_manager.log_access_object().ordered_logs.index(
                str(latest_tried_index) + " " + str(latest_tried_term)
            )

            ordered_logs = self.log_manager.log_access_object().ordered_logs
            term_indexed_logs = self.log_manager.log_access_object().term_indexed_logs
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
                in_term=self.log_manager.current_term,
                previous_index=try_this_index,
                previous_term=try_this_term,
                entries=new_values_to_send
            ).to_message()

        elif string_operation.split(" ")[0] == "commit_entries":
            # followers do this to update their logs.
            stringified_logs_to_append = string_operation.replace("commit_entries ", "")
            print("Preparing to commit: " + stringified_logs_to_append)
            logs_to_append = ast.literal_eval(stringified_logs_to_append)
            [log_manager.write_to_state_machine(command, term_absent=True) for command in logs_to_append]

            response = "Commit entries call successful!"
            print("State machine after committing: " + str(log_manager.data))
        elif string_operation.split(" ")[0] == "can_I_count_on_your_vote_in_term":
            if self.allow_election:
                request_vote_call = RequestVoteCall.from_message(string_operation)
                if request_vote_call.for_term > self.log_manager.current_term \
                    and request_vote_call.latest_log_term >= self.log_manager.latest_term_in_logs \
                    and request_vote_call.latest_log_index >= self.log_manager.highest_index \
                    and self.voting:
                        response = "You can count on my vote!"
                else:
                    response = "Your log is out of date. I'm not voting for you!"
            else:
                response = "I heard from a leader recently, so I'm not voting for you."
        elif string_operation == "You can count on my vote!":
            self.mark_voted(server_name)
            self.log_manager.current_term += 1
            send_pending = False
        elif string_operation == "Append entries call successful!":
            if self.leader:
                self.mark_updated(server_name)
            send_pending = False
        elif string_operation in [
            "Caught up. Thanks!",
            "Sorry, I don't understand that command.",
            "Broadcasting to other servers to catch up their logs.",
            "Commit entries call successful!",
            "Sorry, already voted.",
            "Your term is out of date. You can't be the leader.",
            "Your log is out of date. I'm not voting for you!",
            "I heard from a leader recently, so I'm not voting for you."
        ] or string_operation.startswith("I am not the leader"):
            send_pending = False
        else:
            if self.leader:
                self.current_operation = string_operation

                if self.current_operation.split(" ")[0] in ["set", "delete", "register", "deregister"]:
                    string_operation_with_term = log_manager.write_to_log(string_operation, term_absent=True)

                    self.broadcast(self, with_return_address(
                        self,
                        AppendEntriesCall(
                            in_term=self.log_manager.current_term,
                            previous_index=self.log_manager.highest_index - 1, #because we incremented it to update our own logs
                            previous_term=self.log_manager.latest_term_in_logs,
                            entries=[string_operation_with_term]
                        ).to_message()
                    ))

                    while not self.current_operation_committed:
                        pass

                    response = "Aye aye, cap'n!"
                else:
                    response = log_manager.read(self.current_operation)
            else:
                response = "I am not the leader. The last leader I heard from is " + str(self.latest_leader) + "."

        if send_pending:
            response = self.with_return_address(self, response)

        return server_name, server_port, response
