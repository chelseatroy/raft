import socket

from src.message_pass import *


class Client:
    def __init__(self, server_port=10000):
        self.server_port = server_port

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        server_address = ('localhost', self.server_port)
        print(f"connecting to {server_address[0]} port {server_address[1]}")
        self.sock.connect(server_address)

        running = True
        while running:
            try:
                message = input("Type your message:\n")
                print(f"sending {message}")

                send_message(self.sock, message.encode('utf-8'))

                data = receive_message(self.sock)
                print(f"received {data}")
            except:
                print(f"closing socket")
                self.sock.close()
                running = False
