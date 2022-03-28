'''
FileName: simulator.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import os
import cv2
import time
import socket

from tqdm.auto import tqdm

from toolbox import _pic_encoder
from pathlib import Path
# from onstart import CFG

# %%
file_path = Path(os.environ.get('home', None), 'Desktop', 'nba.mp4')

# !!! The CAPTURE is not closed well in the script.
CAPTURE = cv2.VideoCapture(file_path.as_posix())


def _read_frame():
    success, frame = CAPTURE.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.flip(frame, 1, frame)
    return frame


def _frame2bytes(frame):
    return _pic_encoder(frame)


def _mk_package(body, n_length=10, byteorder='little'):
    n = len(body)

    _header = [
        b'image',
        n.to_bytes(n_length, byteorder),
    ]

    header = b''.join(_header)

    return header + body


# t = time.time()
# n = 100
# for _ in range(n):
#     frame = _read_frame()

# t = time.time() - t
# print(t, t/n)


# %%
serverHost = '100.1.1.108'
serverHost = '192.168.31.38'
# serverHost = 'localhost'
serverPort = 9386


class TCPClient(object):
    def __init__(self):
        pass

    def start(self):
        self.socket = socket.socket()

        host = serverHost
        port = serverPort

        self.socket.connect((host, port))
        print(self.socket.recv(1024))

        self.socket.send(b'Client sent hello.')

        # input('Enter to start')
        for _ in tqdm(range(1000)):
            buff = _mk_package(_frame2bytes(_read_frame()))
            # print(buff[:15])
            # print(int.from_bytes(buff[5:15], 'little'))
            self.socket.send(buff)

        while True:
            inp = input('>> ')
            if inp == 'q':
                break
            self.socket.send(bytes(inp, 'utf8'))

        self.socket.close()


CLIENT = TCPClient()

# %%
if __name__ == '__main__':
    CLIENT.start()

# %%
