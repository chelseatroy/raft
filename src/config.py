def server_nodes(path_to_registry="logs/server_registry.txt"):
    registry = {}

    f = open(path_to_registry, "r")
    log = f.read()
    f.close()

    for command in log.split('\n'):
        server = command.split(" ")
        if len(server) == 3:
            registry[server[0]] = (server[1], int(server[2]))

    return registry


def destination_addresses(server_name):
    other_servers = {k: v for (k, v) in server_nodes().items() if k != server_name}
    return list(other_servers.values())

def other_server_names(server_name):
    other_servers = {k: v for (k, v) in server_nodes().items() if k != server_name}
    return list(other_servers.keys())
