import socket
import threading
import json

import constants


class Server:
    def __init__(self):
        self.ip = '0.0.0.0'
        while True:
            try:
                self.port = int(input('Enter port number to run on --> '))
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server.bind((self.ip, self.port))
                break
            except Exception as e:
                print("Couldn't bind to that port, exception:", e)

        self.connections = []
        self.users = []
        self.accept_connections()

    def accept_connections(self):
        self.server.listen(100)

        print('Running on IP:', self.ip)
        print('Running on port:', str(self.port))

        while True:
            client, _ = self.server.accept()

            echo_enabled = bool(int.from_bytes(client.recv(constants.INT_SIZE), 'big', signed=False))
            length = int.from_bytes(client.recv(constants.INT_SIZE), 'big', signed=False)
            username = client.recv(length).decode()
            print(f'{username} connected')
            participants_bytes = json.dumps(self.users).encode()
            client.send(len(participants_bytes).to_bytes(constants.INT_SIZE, 'big', signed=False))
            client.sendall(participants_bytes)

            for c in self.connections:
                c.send(constants.CODE_CONNECT.to_bytes(constants.INT_SIZE, 'big', signed=False))
                c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                c.send(username.encode())

            self.users.append(username)
            self.connections.append(client)
            threading.Thread(target=self.handle_client, args=(client, username, echo_enabled)).start()

    def broadcast(self, sock, data, echo_mode):
        for client in self.connections:
            if client != sock or echo_mode:
                client.send(constants.CODE_DATA.to_bytes(constants.INT_SIZE, 'big', signed=False))
                client.send(data)

    def handle_client(self, client, username, echo_mode):
        while True:
            try:
                code = int.from_bytes(client.recv(constants.INT_SIZE), 'big', signed=False)
                if code == constants.CODE_DATA:
                    data = client.recv(constants.CHUNK_SIZE)
                    self.broadcast(client, data, echo_mode)
                elif code == constants.CODE_DISCONNECT:
                    client.send(constants.CODE_DISCONNECT.to_bytes(constants.INT_SIZE, 'big', signed=False))
                elif code in (constants.CODE_MUTE, constants.CODE_UNMUTE):
                    print(username, code)
                    for c in self.connections:
                        if c != client:
                            c.send(code.to_bytes(constants.INT_SIZE, 'big', signed=False))
                            c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                            c.send(username.encode())

            except socket.error:
                client.close()
                print(f'{username} disconnected')
                self.connections.remove(client)
                self.users.remove(username)

                for c in self.connections:
                    c.send(constants.CODE_DISCONNECT_OTHER.to_bytes(constants.INT_SIZE, 'big', signed=False))
                    c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                    c.send(username.encode())
                break


server = Server()
