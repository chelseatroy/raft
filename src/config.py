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


