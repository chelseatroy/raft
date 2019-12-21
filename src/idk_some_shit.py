import ast

from src.config import server_nodes, destination_addresses

def respond(server, key_value_store, operation):
    send_pending = True
    string_request = operation.decode("utf-8")
    server_name, string_operation = return_address_and_message(string_request)
    print("from " + server_name + ": received " + string_operation)
    if string_operation == "log_length?":
        response = "log_length " + str(len(key_value_store.log))
    elif string_operation.split(" ")[0] == "log_length":
        catch_up_start_index = int(string_operation.split(" ")[1])

        if len(key_value_store.log) > catch_up_start_index:
            response = "catch_up_logs " + str(key_value_store.log[catch_up_start_index:])
        else:
            response = "Your info is at least as good as mine!"
    elif string_operation.split(" ")[0] == "catch_up_logs":
        logs_to_append = ast.literal_eval(string_operation.split("catch_up_logs ")[1])
        [key_value_store.execute(log, term_absent=False) for log in logs_to_append]

        response = "Caught up. Thanks!"
    elif string_operation == "term":
        response = str(server.term)
    elif string_operation == "destination_addresses":
        response = str(server.destination_addresses())
    elif string_operation == "show_log":
        response = str(key_value_store.log)
    elif string_operation == "youre_the_leader":
        broadcast(server, with_return_address(server, 'log_length?'))
        response = "Broadcasting to other servers to catch up their logs."
    elif string_operation in [
        "Caught up. Thanks!",
        "Sorry, I don't understand that command.",
        "Your info is at least as good as mine!",
        "Broadcasting to other servers to catch up their logs."
    ]:
        send_pending = False
    else:
        response = key_value_store.execute(string_operation, term_absent=True)
    if send_pending:
        response = with_return_address(server, response)

    return server_name, response

def return_address_and_message(string_request):
    address_with_message = string_request.split("@")
    return address_with_message[0], "@".join(address_with_message[1:])


def broadcast(server, message):
    for other_server_address in destination_addresses(server.name):
        server.tell(message, to_server_address=other_server_address)

def with_return_address(server, response):
    return server.name + "@" + response


def address_of(server_name):
    return server_nodes()[server_name]


