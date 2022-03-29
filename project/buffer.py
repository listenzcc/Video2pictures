'''
FileName: buffer.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import numpy as np
import queue
import threading
import socket

from toolbox import _pic_decoder, _bytes
from onstart import CFG, LOGGER


# %%
def _default_img():
    return np.random.randint(0, 255, size=(100, 200, 3), dtype=np.uint8)


class Buffer(object):
    def __init__(self):
        self.queue = queue.Queue(maxsize=int(CFG['buffer']['maxSize']))
        LOGGER.info('Buffer initialized: {}'.format(self.queue.maxsize))

    def append(self, array, uid=-1):
        '''Append new item,

        Args:
            - uid: The Unique ID of the image;
            - array: The width x height x 3 sized uint8 array as an array;

        Returns:
            - success, pid, array
        '''

        try:
            self.queue.put_nowait((uid, array))
            return True, uid, array
        except queue.Full:
            pass

        LOGGER.warning('Buffer is full: {}'.format(self.queue.maxsize))

        return False, uid, array

    def get_nowait(self):
        try:
            return self.queue.get_nowait()
        except queue.Empty:
            return (-2, _default_img())


BUFFER = Buffer()


# %%


# def _append(uid, body):
#     '''
#     Append the bytes body into BUFFER,
#     it will called by the threading on new image arrives.

#     Args:
#         - uid: The Unique ID of the image;
#         - body: The bytes of an .png image;
#     '''
#     img = _pic_decoder(body)
#     if img is None:
#         return
#     BUFFER.append(np.rot90(img), uid)


# class IncomeClient(object):
#     '''
#     Handle the income TCP client.
#     '''

#     def __init__(self, client, addr):
#         self.client = client
#         self.addr = addr

#         t = threading.Thread(target=self._hello, args=(), daemon=True)
#         t.start()

#         LOGGER.info('New client is received {}, {}'.format(client, addr))
#         pass

#     def _hello(self):
#         self.client.send(_bytes(CFG['TCP']['welcomeMessage']))

#         while True:
#             try:
#                 recv = self.client.recv(1024)

#                 if recv.startswith(b'image-s') and len(recv) > (7+16+16):
#                     uid = int.from_bytes(recv[7:7+16], 'little')
#                     n_body = int.from_bytes(recv[7+16:7+16+16], 'little')
#                     body = recv[7+16+16:]
#                     remain = n_body + 7+16+16 - len(recv)
#                     print('New image received {}'.format(n_body))

#                     while remain > 0:
#                         recv = self.client.recv(min(remain, 1024))
#                         body += recv
#                         remain -= len(recv)

#                     if remain < 0:
#                         LOGGER.error(
#                             'Image transfer error, since the remain is less than 0 ({})'.format(remain))
#                         continue

#                     print('Image received {}, {}'.format(len(body), remain))
#                     t = threading.Thread(target=_append, args=(uid, body))
#                     t.start()

#                     continue

#             except ConnectionResetError:
#                 LOGGER.error('Connection reset {}, {}'.format(
#                     self.client, self.addr))
#                 break

#             if recv == b'':
#                 LOGGER.error('Connection closed {}, {}'.format(
#                     self.client, self.addr))
#                 break

#             # print('<<', recv)

#         self.client.close()
#         pass


# class TCPServer(object):
#     '''
#     TCP Server
#     '''

#     def __init__(self):
#         self.bind()
#         LOGGER.info('TCP initialized')
#         pass

#     def bind(self):
#         '''
#         Bind the host:port
#         '''
#         self.socket = socket.socket()

#         host = CFG['TCP']['host']
#         port = int(CFG['TCP']['port'])

#         self.socket.bind((host, port))

#         LOGGER.info('TCP binds on {}:{}'.format(host, port))

#     def serve(self):
#         '''
#         Start the serving
#         '''
#         t = threading.Thread(target=self.listen, args=(), daemon=True)
#         t.start()

#         LOGGER.info('TCP servers on {}'.format(self.socket))

#         pass

#     def listen(self):
#         listen = int(CFG['TCP']['listen'])
#         self.socket.listen(listen)

#         LOGGER.info('TCP listens: {}'.format(listen))

#         # !!! It listens FOREVER
#         # When new client connects,
#         # it will be handled by the IncomeClient.
#         while True:
#             client, addr = self.socket.accept()
#             LOGGER.debug('New client: {}: {}'.format(client, addr))
#             client.send(_bytes(CFG['TCP']['welcomeMessage']))

#             IncomeClient(client, addr)

#             pass


# SERVER = TCPServer()

# # %%
# if __name__ == '__main__':
#     SERVER.serve()
#     input('Enter to escape.')

# # %%
