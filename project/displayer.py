'''
FileName: displayer.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import time
import pygame

from onstart import LOGGER, CFG
from onstart import CAPTION, WHITE, BLACK, GRAY, FONT, QUIT_PYGAME, LAYOUT

from timer import Timer
from buffer import SERVER
from buffer import BUFFER

import threading

# %%
SERVER.serve()

# %%
pygame.display.set_caption(CAPTION)
WINDOW = pygame.display.set_mode(LAYOUT['window_size'])
WINDOW.fill(GRAY)
pygame.display.update()


def _draw_message(msg, window=WINDOW, rect=LAYOUT['message_rect']):
    window.fill(BLACK, rect)
    text_surface_obj = FONT.render('-- {} --'.format(msg), True, WHITE, BLACK)
    window.blit(text_surface_obj, rect)


def _frame():
    fno, image = BUFFER.get_nowait()
    frame = pygame.surfarray.make_surface(image)
    return (fno, frame)


def _draw_image(frame, patch, window=WINDOW):
    window.blit(frame, patch['corner'])


update_rect = [
    LAYOUT['left_patch']['corner'] + LAYOUT['left_patch']['size'],
    LAYOUT['right_patch']['corner'] + LAYOUT['right_patch']['size'],
]

# %%

count = 0

TIMER = Timer()
TIMER.RESET()

lst = [_frame(), _frame()]

while True:
    if TIMER.check() * 10 < count:
        print(time.time(), BUFFER.queue.qsize())

        events = [e for e in pygame.event.get()]

        if any([e.type == pygame.QUIT for e in events]):
            TIMER.save(folder='timings',
                       contents_name=['fno1', 'fno2'])
            QUIT_PYGAME()

        # for event in pygame.event.get():
        #     print(event)
        #     _draw_message(event.dict.get('pos', 'N.A.'))
        #     # pygame.display.update()

        #     if event.type == pygame.QUIT:
        #         TIMER.save(folder='timings',
        #                    contents_name=['fno1', 'fno2'])
        #         QUIT_PYGAME()

        if len(lst) < 2:
            lst = [_frame(), _frame()]
            pass

        continue

    if len(lst) >= 2:
        fno1, frame1 = lst.pop(0)
        fno2, frame2 = lst.pop(0)

        _draw_image(frame1, LAYOUT['left_patch'])
        _draw_image(frame2, LAYOUT['right_patch'])

    pygame.display.update(update_rect)
    TIMER.append([fno1, fno2])
    count += 1

# %%
