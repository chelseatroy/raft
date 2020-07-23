import ast

from src.config import server_nodes, destination_addresses

def return_address_and_message(string_request):
    address_with_message = string_request.split("@")
    return address_with_message[0], "@".join(address_with_message[1:])


def broadcast(server, message):
    print("Broadcasting " + message)
    for other_server_address in destination_addresses(server.name):
        server.send(message, to_server_address=other_server_address)

def with_return_address(server, response):
    return server.name + "@" + response


def address_of(server_name):
    return server_nodes()[server_name]


