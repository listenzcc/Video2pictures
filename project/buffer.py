'''
FileName: buffer.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import queue
import threading
import socket

from onstart import CFG, LOGGER


# %%


class Buffer(object):
    def __init__(self):
        self.queue = queue.Queue(maxsize=int(CFG['buffer']['maxSize']))
        LOGGER.info('Buffer initialized: {}'.format(self.queue.maxsize))

    def append(self, pid, array):
        '''Append new item,

        Args:
            - pid: The ID of the picture;
            - array: The width x height x 3 sized uint8 array as an array;

        Returns:
            - success, pid, array
        '''

        if self.queue.not_full:
            self.queue.put_nowait((pid, array))
            return True, pid, array
        LOGGER.warning('Buffer is full: {}'.format(self.queue.maxsize))
        return False, pid, array


BUFFER = Buffer()


# %%
def _bytes(buf, coding=CFG['TCP']['coding']):
    return bytes(buf, coding)


class IncomeClient(object):
    def __init__(self, client, addr):
        self.client = client
        self.addr = addr

        t = threading.Thread(target=self._hello, args=(), daemon=True)
        t.start()

        LOGGER.info('New client is received {}, {}'.format(client, addr))
        pass

    def _hello(self):
        self.client.send(_bytes(CFG['TCP']['welcomeMessage']))

        while True:
            try:
                recv = self.client.recv(1024)
                if recv.startswith(b'image') and len(recv) > 15:
                    n_body = int.from_bytes(recv[5:15], 'little')
                    body = recv[15:]
                    remain = n_body + 15 - 1024
                    print('New image received {}'.format(n_body))
                    while remain > 0:
                        recv = self.client.recv(min(remain, 1024))
                        body += recv
                        remain -= len(recv)

                    if remain < 0:
                        LOGGER.error(
                            'Image transfer error, since the remain is less than 0 ({})'.format(remain))
                        continue

                    print('Image received {}'.format(len(body)))
                    continue

            except ConnectionResetError:
                LOGGER.error('Connection reset {}, {}'.format(
                    self.client, self.addr))
                break

            if recv == b'':
                LOGGER.error('Connection closed {}, {}'.format(
                    self.client, self.addr))
                break

            print('<<', recv)

        self.client.close()
        pass


class TCPServer(object):
    def __init__(self):
        self.start()

        t = threading.Thread(target=self.listen, args=(), daemon=True)
        t.start()

        LOGGER.info('TCP initialized')
        pass

    def start(self):
        self.socket = socket.socket()

        host = CFG['TCP']['host']
        port = int(CFG['TCP']['port'])

        self.socket.bind((host, port))

        LOGGER.info('TCP serves on {}:{}'.format(host, port))

    def listen(self):
        listen = int(CFG['TCP']['listen'])
        self.socket.listen(listen)

        LOGGER.info('TCP listens: {}'.format(listen))

        while True:
            client, addr = self.socket.accept()
            LOGGER.debug('New client: {}: {}'.format(client, addr))
            client.send(_bytes(CFG['TCP']['welcomeMessage']))

            IncomeClient(client, addr)

            # print('>>', client.recv(1024))
            # print('>>', client.recv(1024))

            # client.close()


# %%
if __name__ == '__main__':
    SERVER = TCPServer()
    input('Enter to escape.')

# %%
