import ast

from src.config import server_nodes, destination_addresses


def respond(server, key_value_store, operation):
    send_pending = True
    string_request = operation.decode("utf-8")
    server_name, string_operation = return_address_and_message(string_request)
    print("from " + server_name + ": received " + string_operation)

    response = ''

    if string_operation.split(" ")[0] == "append_entries":
        stringified_logs_to_append = string_operation.split(" ")[1]
        print(stringified_logs_to_append)
        logs_to_append = ast.literal_eval(stringified_logs_to_append)
        [key_value_store.execute(log, term_absent=False) for log in logs_to_append]

        send_pending = False

    elif string_operation in [
        "Caught up. Thanks!",
        "Sorry, I don't understand that command.",
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
        server.send(message, to_server_address=other_server_address)

def with_return_address(server, response):
    return server.name + "@" + response


def address_of(server_name):
    return server_nodes()[server_name]


