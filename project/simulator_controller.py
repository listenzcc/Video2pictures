'''
FileName: simulator_controller.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import socket

import threading

# %%

cmd_dict = dict(
    single=b'command-single',
    dual=b'command-dual',
    stop=b'command-stop'
)


def _mk_package(cmd):
    assert(cmd in cmd_dict)
    bytes = cmd_dict[cmd]
    return bytes


# %%
serverHost = '100.1.1.108'
serverHost = '192.168.31.38'
# serverHost = 'localhost'
serverPort = 9386


class TCPClient(object):
    def __init__(self):
        self.socket = socket.socket()
        pass

    def _listen(self):
        while True:
            print(self.socket.recv(1024))

    def start(self):
        host = serverHost
        port = serverPort

        self.socket.connect((host, port))
        self.socket.send(b'Client sent hello.')

        t = threading.Thread(target=self._listen, args=(), daemon=True)
        t.start()

        while True:
            inp = input('>> ')
            if inp == 'q':
                break

            if inp == 'p':
                self.socket.send(_mk_package('stop'))
                continue

            if inp == 's':
                self.socket.send(_mk_package('single'))
                continue

            if inp == 'd':
                self.socket.send(_mk_package('dual'))
                continue

            self.socket.send(bytes(inp, 'utf8'))
            continue

        self.socket.close()


CLIENT = TCPClient()

# %%
if __name__ == '__main__':
    CLIENT.start()

# %%
