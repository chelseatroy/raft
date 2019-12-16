import socket
from message_pass import *

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_address = ('localhost', 10000)
print(f"connecting to {server_address[0]} port {server_address[1]}")
sock.connect(server_address)

while True:
    try:
        message = input("Type your message:\n")
        print(f"sending {message}")

        send_message(sock, message.encode('utf-8'))

        data = receive_message(sock)
        print(f"received {data}")
    except:
        print(f"closing socket")
        sock.close()
