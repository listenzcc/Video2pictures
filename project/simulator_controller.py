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
    single=['command-single', '[S]ingle'],
    dual=['command-dual', '[D]ual'],
    stop=['command-stop', 's[T]op'],
    close=['command-close', '[C]lose'],
)


def _mk_package(cmd):
    assert(cmd in cmd_dict)
    _bytes = bytes(cmd_dict[cmd][0], encoding='utf8')
    return _bytes


# %%
# serverHost = '100.1.1.100'
serverHost = 'localhost'
serverPort = 9386


class TCPClient(object):
    def __init__(self):
        self.socket = socket.socket()
        pass

    def _listen(self):
        while True:
            print('<<', self.socket.recv(1024))

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

            if inp == '':
                for e in cmd_dict:
                    print(e, cmd_dict[e])

            if inp == 't':
                self.socket.send(_mk_package('stop'))
                continue

            if inp == 's':
                self.socket.send(_mk_package('single'))
                continue

            if inp == 'd':
                self.socket.send(_mk_package('dual'))
                continue

            if inp == 'c':
                self.socket.send(_mk_package('close'))
                continue

            self.socket.send(bytes(inp, 'utf8'))
            continue

        self.socket.close()


CLIENT = TCPClient()

# %%
if __name__ == '__main__':
    CLIENT.start()

# %%
