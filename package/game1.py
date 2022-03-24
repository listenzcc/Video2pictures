
# %%
import os
import time
import pygame
import numpy as np

from pathlib import Path

from constants import *
from timer import Timer

import threading
from pool import Pool
import queue

# %%


def _rnd_image():
    image = np.random.randint(0, 255, size=(800, 400, 3), dtype=np.uint8)
    return image


POOL = Pool()
QUEUE = queue.Queue()
QUEUE.maxsize = 100


def _update():
    while True:
        # if POOL.length() < 10:
        #     POOL.append(_rnd_image())
        if QUEUE.not_full:
            try:
                QUEUE.put_nowait(_rnd_image())
            except queue.Full:
                continue
            continue
        pass


t = threading.Thread(target=_update, args={}, daemon=True)
t.start()

# %%
TIMER = Timer()

# %%
pygame.display.set_caption(CAPTION)

# %%


def set_layout():
    window_size = (1800, 900)
    patch_size = (800, 600)

    left_patch = dict(
        corner=(0+10, 0+20),
        size=patch_size,
    )

    right_patch = dict(
        corner=(900+10, 0+20),
        size=patch_size,
    )

    message_rect = pygame.Rect((1000, 800, 500, 32))

    return dict(
        window_size=window_size,
        left_patch=left_patch,
        right_patch=right_patch,
        message_rect=message_rect
    )


layout = set_layout()

# %%
main_canvas = pygame.display.set_mode(layout.get('window_size'))

main_canvas.fill(GRAY)
pygame.display.update()

fontObj = pygame.font.Font('freesansbold.ttf', 20)
textSurfaceObj = FONT.render('Hello world!', True, WHITE, BLACK)


def _draw_message(msg, canvas=main_canvas, rect=layout.get('message_rect')):
    canvas.fill(BLACK, rect)
    text_surface_obj = FONT.render('-- {} --'.format(msg), True, WHITE, BLACK)
    canvas.blit(text_surface_obj, rect)


def _frame(fno):
    # image = _rnd_image()
    # image = POOL.pop()
    image = QUEUE.get_nowait()
    frame = pygame.surfarray.make_surface(image)
    return (fno, frame)


def _draw_image(frame, patch, canvas=main_canvas):
    canvas.blit(frame, patch.get('corner'))


# %%
count = 0
TIMER.RESET()

fno1 = np.random.randint(0, 1000000)
fno2 = np.random.randint(0, 1000000)
lst = [_frame(fno1), _frame(fno2)]


while True:
    if TIMER.check() * 10 < count:
        for event in pygame.event.get():
            print(event)
            _draw_message(event.dict.get('pos', 'N.A.'))
            # pygame.display.update()
            if event.type == pygame.QUIT:
                TIMER.save(folder='timings', contents_name=['fno1', 'fno2'])
                # CAPTURER.release()
                QUIT_PYGAME()

        # CAPTURER.skip = False

        if len(lst) == 0:
            fno1 = np.random.randint(0, 1000000)
            fno2 = np.random.randint(0, 1000000)
            lst = [_frame(fno1), _frame(fno2)]

        continue

    if len(lst) == 2:
        fno1, frame1 = lst.pop()
        fno2, frame2 = lst.pop()

        _draw_image(frame1, layout.get('left_patch'))
        _draw_image(frame2, layout.get('right_patch'))

    pygame.display.update()
    TIMER.append([fno1, fno2])
    count += 1

CAPTURER.release()
# %%
