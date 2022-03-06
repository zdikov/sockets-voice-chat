INT_SIZE = 4
CHUNK_SIZE = 4096

CODE_DATA = 0
CODE_MUTE = 1
CODE_UNMUTE = 2
CODE_CONNECT = 3
CODE_DISCONNECT = 4
CODE_DISCONNECT_OTHER = 5


def print_status(code):
    if code == CODE_MUTE:
        return 'muted'
    elif code == CODE_UNMUTE:
        return 'unmuted'
    elif code == CODE_CONNECT:
        return 'connected'
    elif code == CODE_DISCONNECT_OTHER:
        return 'disconnected'
