import socket

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
print(f"connecting to {server_address[0]} port {server_address[1]}")
sock.connect(server_address)

while True:
    try:
        message = input("Type your message:\n")
        print(f"sending {message}")

        sock.sendall(message.encode('utf-8'))

        data = sock.recv(1024)
        print(f"received {data}")
    except:
        print(f"closing socket")
        sock.close()
