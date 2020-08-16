import threading
import os

from src.log_data_access_object import LogDataAccessObject

class KeyValueStore:
    client_lock = threading.Lock()

    def __init__(self, server_name):
        self.server_name = server_name
        self.data = {}
        self.log = []
        self.catch_up_successful = False
        self.latest_term = 0
        self.highest_index = 1

    def get(self, key):
        return self.data.get(key, '')

    def set(self, key, value):
        self.data[key] = value

    def delete(self, key):
        del self.data[key]

    def catch_up(self, path_to_logs=''):
        if path_to_logs == '':
            path_to_logs = "logs/" + self.server_name + "_log.txt"

        if os.path.exists(path_to_logs):
            f = open(path_to_logs, "r+")

            all_lines = f.read().splitlines()
            non_empty_lines = list(filter(lambda x: x != '', all_lines))
            if len(non_empty_lines) == 0:
                f.seek(0)
                f.write("0 0 set  unreachable\n")
            f.close()

            last_command = ''
            for command in all_lines:
                if command != '':
                    last_command = command
                    self.write_to_state_machine(command, term_absent=False, write=False)

            if last_command != '':
                components = last_command.split(' ')

                #increment the index from the last call
                # so that the next log entry continues the count upward
                self.highest_index = int(components[0])
                self.latest_term = int(components[1])

        self.catch_up_successful = True

    def remove_logs_after_index(self, index, path_to_logs=''):
        if path_to_logs == '':
            path_to_logs = "logs/" + self.server_name + "_log.txt"

        if os.path.exists(path_to_logs):
            f = open(path_to_logs, "r+")
            log_list = f.readlines()

            while '' in log_list:
                log_list.remove('')
            f.seek(0)
            for line_to_keep in log_list[0:index + 1]:
                f.write(line_to_keep)
            f.truncate()
            f.close()

    def log_access_object(self, path_to_logs=''):
        as_dict = {}
        the_worst_array = []
        if path_to_logs == '':
            path_to_logs = "logs/" + self.server_name + "_log.txt"

        if os.path.exists(path_to_logs):
            f = open(path_to_logs, "r")
            log = f.read()
            f.close()

            for command in log.split('\n'):
                if command != '':
                    operands = command.split(" ")

                    as_dict[" ".join(operands[:2])] = " ".join(operands)
                    the_worst_array.append(" ".join(operands[:2]))

        return LogDataAccessObject(array=the_worst_array, dict=as_dict)

    def command_at(self, previous_index, previous_term):
        return self.log_access_object().term_indexed_logs.\
            get(str(previous_index) + " " + str(previous_term))


    def get_latest_term(self):
        if not self.catch_up_successful:
            print("This store isn't caught up, so it doesn't know what term we're in!")
            return

        return self.latest_term


    def write_to_state_machine(self, string_operation, term_absent, write=True, path_to_logs=''):
        print("Writing to state machine: " + string_operation)

        if len(string_operation) == 0:
            return

        if term_absent:
            string_operation = str(self.highest_index) + " " + str(self.latest_term) + " " + string_operation

        operands = string_operation.split(" ")
        index, term, command, key, values = 0, 1, 2, 3, 4

        response = "Sorry, I don't understand that command."

        with self.client_lock:
            self.latest_term = int(operands[term])

            if operands[command] == "set":
                value = " ".join(operands[values:])

                self.log.append(string_operation)
                if write:
                    self.write_to_log(string_operation, term_absent=False, path_to_logs=path_to_logs)
                self.set(operands[key], value)
                response = f"key {operands[key]} set to {value}"
            elif operands[command] == "delete":
                self.log.append(string_operation)
                if write:
                    self.write_to_log(string_operation, term_absent=False, path_to_logs=path_to_logs)
                self.delete(operands[key])
                response = f"key {key} deleted"
            else:
                pass

        return response

    def read(self, string_operation):
        print(string_operation)

        if len(string_operation) == 0:
            return

        operands = string_operation.split(" ")
        print("the read command is " + string_operation)
        command, key, values = 0, 1, 2

        response = "Sorry, I don't understand that command."

        with self.client_lock:
            if operands[command] == "get":
                response = self.get(operands[key])
            elif operands[command] == "show":
                response = str(self.data)
            else:
                pass

        return response

    #used in leader server when client sends a command
    def write_to_log(self, string_operation, term_absent, path_to_logs=''):
        print("Writing to log: " + string_operation)

        if len(string_operation) == 0:
            return ''

        operands = string_operation.split(" ")
        if term_absent:
            command, key, values = 0, 1, 2
        else:
            index, term, command, key, values = 0, 1, 2, 3, 4

        if operands[command] in ["set", "delete"]:
            if term_absent:
                self.highest_index = self.highest_index + 1
                string_operation = str(self.highest_index) + " " + str(self.latest_term) + " " + string_operation
            else:
                self.highest_index = index + 1
                self.latest_term = term

            if path_to_logs == '':
                path_to_logs = "logs/" + self.server_name + "_log.txt"
            f = open(path_to_logs, "a+")
            f.write(string_operation + '\n')
            f.close()

            return string_operation

        return ''

