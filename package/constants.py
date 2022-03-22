# %%
import sys
import pygame

# %%
CAPTION = 'Image Project of PyGame'

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

# %%
pygame.init()
FONT = pygame.font.Font('freesansbold.ttf', 32)

# %%


def QUIT_PYGAME():
    pygame.quit()
    sys.exit()

# %%
