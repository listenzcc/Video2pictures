'''
FileName: onstart.py
Author: Chuncheng
Version: V0.0
Purpose:
'''

# %%
import sys
import pygame
import logging
import configparser
from pathlib import Path

# %%
CONFIG = dict(
    short_name='R. D.',
    app_name='Rapid Displayer',
    log_folder=Path(__file__).joinpath('../../log'),
    assets_folder=Path(__file__).joinpath('../../assets'),
)

# %%
CFG = configparser.ConfigParser()
CFG.read(CONFIG['assets_folder'].joinpath('configure.cfg'))
CFG

# %%
CAPTION = CFG['UI']['caption']

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (100, 100, 100)

pygame.init()
FONT = pygame.font.Font(CFG['UI']['fontName'],
                        int(CFG['UI']['fontSize']))


def QUIT_PYGAME():
    pygame.quit()
    sys.exit()

# %%


def set_layout():
    window_size = (1800, 900)
    patch_size = (int(CFG['picture']['width']),
                  int(CFG['picture']['height']))

    center_patch = dict(
        corner=(int(CFG['centerPatch']['cornerLeft']),
                int(CFG['centerPatch']['cornerTop'])),
        size=patch_size
    )

    left_patch = dict(
        corner=(int(CFG['leftPatch']['cornerLeft']),
                int(CFG['leftPatch']['cornerTop'])),
        size=patch_size
    )

    right_patch = dict(
        corner=(int(CFG['rightPatch']['cornerLeft']),
                int(CFG['rightPatch']['cornerTop'])),
        size=patch_size
    )

    message_rect = pygame.Rect((1000, 800, 500, 32))

    return dict(
        window_size=window_size,
        center_patch=center_patch,
        left_patch=left_patch,
        right_patch=right_patch,
        message_rect=message_rect
    )


LAYOUT = set_layout()

# %%
logger_kwargs = dict(
    level_file=logging.DEBUG,
    level_console=logging.DEBUG,
    format_file='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s:%(module)s:%(funcName)s}}',
    format_console='%(asctime)s %(name)s %(levelname)-8s %(message)-40s {{%(filename)s:%(lineno)s}}'
)


def generate_logger(name, filepath, level_file, level_console, format_file, format_console):
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    file_handler = logging.FileHandler(filepath)
    file_handler.setFormatter(logging.Formatter(format_file))
    file_handler.setLevel(level_file)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(format_console))
    console_handler.setLevel(level_console)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger


LOGGER = generate_logger('RapidDisplayer', CONFIG['log_folder'].joinpath(
    'RapidDisplayer.log'), **logger_kwargs)
LOGGER.info(
    '--------------------------------------------------------------------------------')
LOGGER.info(
    '---- New Session is started ----------------------------------------------------')
LOGGER.debug('Read CFG of {}'.format([e for e in CFG]))

# %%
