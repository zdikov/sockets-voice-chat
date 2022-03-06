#!/usr/bin/python3

import socket
import threading

from constants import INT_SIZE


class Server:
    def __init__(self):
        self.ip = socket.gethostbyname(socket.gethostname())
        while 1:
            try:
                self.port = int(input('Enter port number to run on --> '))

                self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.s.bind((self.ip, self.port))

                break
            except Exception as e:
                print("Couldn't bind to that port, exception:", e)

        self.connections = []
        self.accept_connections()

    def accept_connections(self):
        self.s.listen(100)

        print('Running on IP: ' + self.ip)
        print('Running on port: ' + str(self.port))

        while True:
            c, addr = self.s.accept()

            self.connections.append(c)

            length = int.from_bytes(c.recv(INT_SIZE), 'big', signed=False)
            print(f'length={length}')
            username = c.recv(length).decode()
            print(f'{username} connected')

            threading.Thread(target=self.handle_client, args=(c, addr,)).start()

    def broadcast(self, sock, data):
        for client in self.connections:
            if client != self.s:  # and client != sock:
                try:
                    client.send(data)
                except:
                    pass

    def handle_client(self, c, addr):
        while 1:
            try:
                data = c.recv(1024)
                self.broadcast(c, data)

            except socket.error:
                c.close()


server = Server()
