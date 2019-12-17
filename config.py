
def server_nodes():
    registry = {}

    f = open("server_registry.txt", "r")
    log = f.read()
    f.close()

    for command in log.split('\n'):
        print(command)
        server = command.split(" ")
        if len(server) == 3:
            registry[server[0]] = (server[1], server[2])

    return registry
