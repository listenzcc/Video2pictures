'''
FileName: online_displayer.py
Author: Chuncheng
Version: V0.0
Purpose: Displayer of RSVP controlled by online commands
'''

# %%
import time
import pygame

import socket
import threading
import numpy as np

from timer import Timer
from buffer import BUFFER
from toolbox import _pic_decoder, _bytes
from onstart import CFG, LOGGER
from onstart import CAPTION, WHITE, BLACK, GRAY, FONT, QUIT_PYGAME, LAYOUT

# %%


def _append(uid, body):
    '''
    Append the bytes body into BUFFER,
    it will called by the threading on new image arrives.

    Args:
        - uid: The Unique ID of the image;
        - body: The bytes of an .png image;
    '''
    img = _pic_decoder(body)
    if img is None:
        return
    BUFFER.append(np.rot90(img), uid)


class IncomeClient(object):
    '''
    Handle the income TCP client.
    '''

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

                if recv == b'command-stop':
                    DISPLAYER.set_status('idle')
                    self.client.send(_bytes('OK') + recv)
                    continue

                if recv == b'command-single':
                    if DISPLAYER.get_status() == 'idle':
                        self.client.send(_bytes('OK') + recv)
                        DISPLAYER.set_status('single')
                        # t = threading.Thread(target=DISPLAYER.display_single,
                        #                      args=(),
                        #                      daemon=True)
                        # t.start()
                        DISPLAYER.display_single()
                        continue
                    self.client.send(_bytes('FAIL') + recv)
                    continue

                if recv.startswith(b'image-s') and len(recv) > (7+16+16):
                    uid = int.from_bytes(recv[7:7+16], 'little')
                    n_body = int.from_bytes(recv[7+16:7+16+16], 'little')
                    body = recv[7+16+16:]
                    remain = n_body + 7+16+16 - len(recv)
                    print('New image received {}'.format(n_body))

                    while remain > 0:
                        recv = self.client.recv(min(remain, 1024))
                        body += recv
                        remain -= len(recv)

                    if remain < 0:
                        LOGGER.error(
                            'Image transfer error, since the remain is less than 0 ({})'.format(remain))
                        continue

                    print('Image received {}, {}'.format(len(body), remain))
                    t = threading.Thread(target=_append, args=(uid, body))
                    t.start()

                    continue

                self.client.send(_bytes('UnDo') + recv)

            except ConnectionResetError:
                LOGGER.error('Connection reset {}, {}'.format(
                    self.client, self.addr))
                break

            if recv == b'':
                LOGGER.error('Connection closed {}, {}'.format(
                    self.client, self.addr))
                break

            # print('<<', recv)

        self.client.close()
        pass


class TCPServer(object):
    '''
    TCP Server
    '''

    def __init__(self):
        self.bind()
        LOGGER.info('TCP initialized')
        pass

    def bind(self):
        '''
        Bind the host:port
        '''
        self.socket = socket.socket()

        host = CFG['TCP']['host']
        port = int(CFG['TCP']['port'])

        self.socket.bind((host, port))

        LOGGER.info('TCP binds on {}:{}'.format(host, port))

    def serve(self):
        '''
        Start the serving
        '''
        t = threading.Thread(target=self.listen, args=(), daemon=True)
        t.start()

        LOGGER.info('TCP servers on {}'.format(self.socket))

        pass

    def listen(self):
        listen = int(CFG['TCP']['listen'])
        self.socket.listen(listen)

        LOGGER.info('TCP listens: {}'.format(listen))

        # !!! It listens FOREVER
        # When new client connects,
        # it will be handled by the IncomeClient.
        while True:
            client, addr = self.socket.accept()
            LOGGER.debug('New client: {}: {}'.format(client, addr))
            client.send(_bytes(CFG['TCP']['welcomeMessage']))

            IncomeClient(client, addr)

            pass


SERVER = TCPServer()

# %%
pygame.display.set_caption(CAPTION)
WINDOW = pygame.display.set_mode(LAYOUT['window_size'])
WINDOW.fill(GRAY)
pygame.display.update()


def _frame_single():
    uid, image = BUFFER.get_nowait()
    frame = pygame.surfarray.make_surface(image)
    return uid, frame


def _frame_dual():
    uid, images = BUFFER.get_nowait()
    frame1 = pygame.surfarray.make_surface(images[0])
    frame2 = pygame.surfarray.make_surface(images[1])
    return uid, frame1, frame2


def _draw_frame_single(frame, patch):
    frame = pygame.transform.scale(frame, patch['size'])
    WINDOW.blit(frame, patch['corner'])


def _draw_frame_dual(frame1, frame2, patch1, patch2):
    frame1 = pygame.transform.scale(frame1, patch1['size'])
    frame2 = pygame.transform.scale(frame2, patch2['size'])
    WINDOW.blit(frame1, patch1['corner'])
    WINDOW.blit(frame2, patch2['corner'])


update_rect = [
    LAYOUT['center_patch']['corner'] + LAYOUT['center_patch']['size'],
    LAYOUT['left_patch']['corner'] + LAYOUT['left_patch']['size'],
    LAYOUT['right_patch']['corner'] + LAYOUT['right_patch']['size'],
]


class Displayer(object):
    def __init__(self):
        self.timer = Timer()
        self.status = 'idle'
        self.valid_status = dict(
            idle='Doing nothing and ready to display',
            single='Displaying in single-channel mode',
            dual='Displaying in dual-channels mode'
        )
        self.count = -1
        self.lst = []
        LOGGER.info('Displayer is initialized.')
        pass

    def set_status(self, status):
        s = self.status
        self.status = status
        LOGGER.debug('Displayer changes status: {}, {}'.format(s, status))
        return self.status

    def get_status(self):
        return self.status

    def display_single(self):
        self.lst = []
        self.count = 0
        self.set_status('single')
        self.timer.RESET()

        # lst = []
        # while self.get_status() == 'single':
        #     events = [e for e in pygame.event.get()]
        #     print(time.time(), BUFFER.queue.qsize(), events)

        #     if self.timer.check() * 10 < count:
        #         if len(lst) < 1:
        #             lst = [_frame_single()]
        #         continue

        #     uid = -1
        #     if len(lst) == 1:
        #         print(lst)
        #         uid, frame = lst.pop()
        #         _draw_frame_single(frame, LAYOUT['center_patch'])

        #     pygame.display.update(update_rect)
        #     self.timer.append([uid])
        #     count += 1

        pass


DISPLAYER = Displayer()

# %%
SERVER.serve()

while True:
    if DISPLAYER.get_status() == 'single':
        if DISPLAYER.timer.check() * 10 < DISPLAYER.count:
            events = [e for e in pygame.event.get()]
            # print(time.time(), BUFFER.queue.qsize(), events)

            if any([e.type == pygame.QUIT for e in events]):
                DISPLAYER.timer.save(folder='timings',
                                     contents_name=['uid'])
                QUIT_PYGAME()
                pass

            if len(DISPLAYER.lst) == 0:
                DISPLAYER.lst.append(_frame_single())
            continue

        uid = -1
        if len(DISPLAYER.lst) == 1:
            uid, frame = DISPLAYER.lst.pop()
            _draw_frame_single(frame, LAYOUT['center_patch'])

        pygame.display.update(update_rect)
        DISPLAYER.timer.append([uid])
        DISPLAYER.count += 1


input('Enter to escape.')

# %%
# if __name__ == '__main__':
#     SERVER.serve()
#     input('Enter to escape.')

# %%
