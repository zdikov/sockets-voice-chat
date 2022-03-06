import socket
import threading
import pyaudio
from pynput import keyboard

import constants


class Client:
    def __init__(self):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serve = True
        self.send = False

        self.target_ip = input('Enter IP address of server --> ')
        self.target_port = int(input('Enter target port of server --> '))
        self.username = input('Enter username --> ')

        while True:
            enable_echo_ch = input('Enable echo? [y/n] --> ')
            if enable_echo_ch == 'y':
                enable_echo = True
            elif enable_echo_ch == 'n':
                enable_echo = False
            else:
                print("Please, enter 'y' or 'n'")
                continue
            break

        self.s.connect((self.target_ip, self.target_port))
        if enable_echo:
            self.s.send(int(1).to_bytes(constants.INT_SIZE, 'big', signed=False))
        else:
            self.s.send(int(0).to_bytes(constants.INT_SIZE, 'big', signed=False))

        username_bytes = self.username.encode()
        self.s.send(len(username_bytes).to_bytes(constants.INT_SIZE, 'big', signed=False))
        self.s.send(username_bytes)

        audio_format = pyaudio.paInt16
        channels = 1
        rate = 20000

        # initialise microphone recording
        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=audio_format, channels=channels, rate=rate, output=True,
                                          frames_per_buffer=constants.CHUNK_SIZE)
        self.recording_stream = self.p.open(format=audio_format, channels=channels, rate=rate, input=True,
                                            frames_per_buffer=constants.CHUNK_SIZE)

        print("Connected to Server")
        print("Press 'h' to unmute, press 'q' to quite")

        # start threads
        listener = keyboard.Listener(on_press=self.on_press)
        listener.start()
        receive_thread = threading.Thread(target=self.receive_server_data)
        receive_thread.start()
        self.send_data_to_server()
        listener.join()
        receive_thread.join()

    def on_press(self, key):
        try:
            k = key.char
        except:
            k = key.name

        if k == 'q':
            self.serve = False
            return False
        elif k == 'h':
            if self.send:
                print("Press 'h' to unmute")
                self.send = False
            else:
                print("Press 'h' to mute")
                self.send = True

    def receive_server_data(self):
        while self.serve:
            try:
                code = int.from_bytes(self.s.recv(constants.INT_SIZE), 'big', signed=False)
                if code == constants.CODE_DATA:
                    data = self.s.recv(constants.CHUNK_SIZE)
                    self.playing_stream.write(data)
                elif code == constants.CODE_DISCONNECT:
                    break

            except Exception as e:
                print(e)

    def send_data_to_server(self):
        while self.serve:
            try:
                data = self.recording_stream.read(constants.CHUNK_SIZE)
                if self.send:
                    self.s.send(constants.CODE_DATA.to_bytes(constants.INT_SIZE, 'big', signed=False))
                    self.s.sendall(data)
            except Exception as e:
                print(e)
        self.s.send(constants.CODE_DISCONNECT.to_bytes(constants.INT_SIZE, 'big', signed=False))




client = Client()
