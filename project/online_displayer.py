'''
FileName: online_displayer.py
Author: Chuncheng
Version: V0.0
Purpose: Displayer of RSVP controlled by online commands
'''

# %%

import parallel

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
        - body: The bytes of an .png image,
                or the list of two images;
    '''
    if isinstance(body, list):
        img1 = _pic_decoder(body[0])
        img2 = _pic_decoder(body[1])
        print(img1.shape, img2.shape)
        if img1 is None or img2 is None:
            return -1
        BUFFER.append([np.rot90(img1), np.rot90(img2)], uid)
        return 0

    img = _pic_decoder(body)
    if img is None:
        return -1
    BUFFER.append(np.rot90(img), uid)
    return 0


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

                if recv == b'command-close':
                    self.client.send(_bytes('OK') + recv)
                    DISPLAYER.timer_save()
                    DISPLAYER.set_status('idle')
                    DISPLAYER.alive = False
                    continue

                if recv == b'command-stop':
                    DISPLAYER.set_status('idle')
                    self.client.send(_bytes('OK') + recv)
                    DISPLAYER.timer_save()
                    continue

                if recv == b'command-single':
                    if DISPLAYER.get_status() == 'idle':
                        self.client.send(_bytes('OK') + recv)
                        DISPLAYER.set_status('single')
                        DISPLAYER.display_single()
                        continue
                    self.client.send(_bytes('FAIL') + recv)
                    continue

                if recv == b'command-dual':
                    if DISPLAYER.get_status() == 'idle':
                        self.client.send(_bytes('OK') + recv)
                        DISPLAYER.set_status('dual')
                        DISPLAYER.display_dual()
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
                            'Single Image transfer error, since the remain is less than 0 ({})'.format(remain))
                        continue

                    print('Single Image received {}, {}'.format(len(body), remain))
                    t = threading.Thread(target=_append, args=(uid, body))
                    t.start()

                    continue

                if recv.startswith(b'image-d') and len(recv) > (7+16+16+16):
                    uid = int.from_bytes(recv[7:7+16], 'little')
                    n_body1 = int.from_bytes(recv[7+16:7+16+16], 'little')
                    n_body2 = int.from_bytes(
                        recv[7+16+16:7+16+16+16], 'little')
                    n_body = n_body1 + n_body2
                    body = recv[7+16+16+16:]
                    remain = n_body + 7+16+16+16 - len(recv)
                    print('New image received {}'.format(n_body))

                    while remain > 0:
                        recv = self.client.recv(min(remain, 1024))
                        body += recv
                        remain -= len(recv)

                    if remain < 0:
                        LOGGER.error(
                            'Dual Images transfer error, since the remain is less than 0 ({})'.format(remain))
                        continue

                    print('Dual Images received {}({}, {}), {}'.format(
                        len(body), n_body1, n_body2, remain))
                    t = threading.Thread(target=_append, args=(
                        uid, [body[:n_body1], body[n_body1:]]))
                    t.start()

                    continue

                self.client.send(_bytes('UnDo') + recv)

            except ConnectionResetError:
                LOGGER.error('Connection reset {}, {}'.format(
                    self.client, self.addr))
                break

            # if recv == b'':
            #     LOGGER.error('Connection closed {}, {}'.format(
            #         self.client, self.addr))
            #     break

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
        Displayer.alive = True
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

    def timer_save(self):
        # !!! Change the contents_name to match the records
        fname = self.timer.save(folder='timings',
                                contents_name=['uid', 'mode'])
        LOGGER.info('Saved records into {}'.format(fname))
        return

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
        pass

    def display_dual(self):
        self.lst = []
        self.count = 0
        self.set_status('dual')
        self.timer.RESET()
        pass


DISPLAYER = Displayer()

# %%
SERVER.serve()

parallel_port_address = int(CFG['ParallelPort']['address'], 16)
print(parallel_port_address)
use_parallel_port = False
if parallel_port_address > 0:
    use_parallel_port = True
    parallel.setPortAddress(parallel_port_address)
    parallel.setData(0)


while DISPLAYER.alive:
    mode = DISPLAYER.get_status()
    if mode in ['single', 'dual']:
        if DISPLAYER.timer.check() * 10 < DISPLAYER.count:
            if use_parallel_port:
                parallel.setData(0)

            events = [e for e in pygame.event.get()]
            # print(time.time(), BUFFER.queue.qsize(), events)

            if any([e.type == pygame.QUIT for e in events]):
                DISPLAYER.timer_save()
                QUIT_PYGAME()
                pass

            if mode == 'single' and len(DISPLAYER.lst) == 0:
                DISPLAYER.lst.append(_frame_single())

            if mode == 'dual' and len(DISPLAYER.lst) == 0:
                DISPLAYER.lst.append(_frame_dual())

            continue

        uid = -1
        if mode == 'single' and len(DISPLAYER.lst) == 1:
            if len(DISPLAYER.lst[0]) != 2:
                continue
            uid, frame = DISPLAYER.lst.pop()

            if use_parallel_port:
                parallel.setData(max(0, int(uid)))

            _draw_frame_single(frame, LAYOUT['center_patch'])

        if mode == 'dual' and len(DISPLAYER.lst) == 1:
            if len(DISPLAYER.lst[0]) != 3:
                continue
            uid, frame1, frame2 = DISPLAYER.lst.pop()

            if use_parallel_port:
                parallel.setData(max(0, int(uid)))

            _draw_frame_dual(frame1, frame2,
                             LAYOUT['left_patch'], LAYOUT['right_patch'])

        pygame.display.update(update_rect)
        DISPLAYER.timer.append([uid, mode])
        DISPLAYER.count += 1

    else:
        events = [e for e in pygame.event.get()]
        # print(time.time(), BUFFER.queue.qsize(), events)

        if any([e.type == pygame.QUIT for e in events]):
            DISPLAYER.timer_save()
            if use_parallel_port:
                parallel.setData(0)
            QUIT_PYGAME()
            pass

if use_parallel_port:
    parallel.setData(0)
QUIT_PYGAME()

input('Enter to escape.')

# %%
# if __name__ == '__main__':
#     SERVER.serve()
#     input('Enter to escape.')

# %%
