import socket
import threading
import json

import constants


class Room:
    def __init__(self, id):
        self.id = id
        self.connections = []
        self.users = []


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

        self.id_to_room = {}
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

            room_id = int.from_bytes(client.recv(constants.INT_SIZE), 'big', signed=False)

            if room_id not in self.id_to_room:
                self.id_to_room[room_id] = Room(room_id)

            room = self.id_to_room[room_id]

            print(f'{username} connected to room {room_id}')

            participants_bytes = json.dumps(room.users).encode()
            client.send(len(participants_bytes).to_bytes(constants.INT_SIZE, 'big', signed=False))
            client.sendall(participants_bytes)

            for c in room.connections:
                c.send(constants.CODE_CONNECT.to_bytes(constants.INT_SIZE, 'big', signed=False))
                c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                c.send(username.encode())

            room.users.append(username)
            room.connections.append(client)
            threading.Thread(target=self.handle_client, args=(room, client, username, echo_enabled)).start()

    def broadcast(self, room, sock, data, echo_mode):
        for client in room.connections:
            if client != sock or echo_mode:
                client.send(constants.CODE_DATA.to_bytes(constants.INT_SIZE, 'big', signed=False))
                client.send(data)

    def handle_client(self, room, client, username, echo_mode):
        while True:
            try:
                code = int.from_bytes(client.recv(constants.INT_SIZE), 'big', signed=False)
                if code == constants.CODE_DATA:
                    data = client.recv(constants.CHUNK_SIZE)
                    self.broadcast(room, client, data, echo_mode)
                elif code == constants.CODE_DISCONNECT:
                    client.send(constants.CODE_DISCONNECT.to_bytes(constants.INT_SIZE, 'big', signed=False))
                elif code in (constants.CODE_MUTE, constants.CODE_UNMUTE):
                    print(username, constants.print_status(code))
                    for c in room.connections:
                        if c != client:
                            c.send(code.to_bytes(constants.INT_SIZE, 'big', signed=False))
                            c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                            c.send(username.encode())

            except socket.error:
                client.close()
                print(f'{username} disconnected from room {room.id}')
                room.connections.remove(client)
                room.users.remove(username)

                for c in room.connections:
                    c.send(constants.CODE_DISCONNECT_OTHER.to_bytes(constants.INT_SIZE, 'big', signed=False))
                    c.send(len(username.encode()).to_bytes(constants.INT_SIZE, 'big', signed=False))
                    c.send(username.encode())
                break


server = Server()
