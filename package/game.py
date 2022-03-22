# %%
import os
import pygame
import numpy as np

from pathlib import Path

from constants import *
from timer import Timer
from capturer import Capturer

# %%
TIMER = Timer()

file_path = Path(os.environ.get('home', None), 'Desktop', 'nba.mp4')
CAPTURER = Capturer(file_path.as_posix())


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
    image = CAPTURER.get_frame(fno)
    frame = pygame.surfarray.make_surface(np.rot90(image))
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
                CAPTURER.release()
                QUIT_PYGAME()

        if len(lst) < 2:
            fno1 = np.random.randint(0, 1000000)
            fno2 = np.random.randint(0, 1000000)
            lst = [_frame(fno1), _frame(fno2)]

        continue

    fno1, frame1 = lst.pop(0)
    fno2, frame2 = lst.pop(0)

    _draw_image(frame1, layout.get('left_patch'))
    _draw_image(frame2, layout.get('right_patch'))

    pygame.display.update()
    TIMER.append([fno1, fno2])
    count += 1

CAPTURER.release()
# %%
