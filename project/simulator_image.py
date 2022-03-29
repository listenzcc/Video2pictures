'''
FileName: simulator_image.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import os
import cv2
import socket

from tqdm.auto import tqdm

from toolbox import _pic_encoder
from pathlib import Path

# %%
file_path = Path(os.environ.get('home', None), 'Desktop', 'nba.mp4')

# !!! The CAPTURE is not closed well in the script.
CAPTURE = cv2.VideoCapture(file_path.as_posix())
_tmp_count = [0]


def _read_frame():
    success, frame = CAPTURE.read()
    _tmp_count[0] += 1
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    cv2.flip(frame, 1, frame)
    return frame


def _frame2bytes(frame):
    return _pic_encoder(frame[::2, ::2])


def _mk_package(frame_bytes, uid=0, uid_length=16, n_length=16, byteorder='little'):
    # Single channel mode
    if isinstance(frame_bytes, type(b'a')):
        n = len(frame_bytes)
        _header = [
            b'image-s',
            uid.to_bytes(uid_length, byteorder),
            n.to_bytes(n_length, byteorder),
        ]
        header = b''.join(_header)
        return header + frame_bytes

    # Dual channels mode
    if isinstance(frame_bytes, list):
        n1 = len(frame_bytes[0])
        n2 = len(frame_bytes[1])
        _header = [
            b'image-d',
            uid.to_bytes(uid_length, byteorder),
            n1.to_bytes(n_length, byteorder),
            n2.to_bytes(n_length, byteorder),
        ]
        header = b''.join(_header)
        return header + frame_bytes[0] + frame_bytes[1]


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
        for _ in tqdm(range(10000)):
            buff = _mk_package(_frame2bytes(_read_frame()), _tmp_count[0])
            # print(buff[:15])
            # print(int.from_bytes(buff[5:15], 'little'))
            self.socket.send(buff)

        self.socket.close()


CLIENT = TCPClient()

# %%
if __name__ == '__main__':
    CLIENT.start()

# %%
