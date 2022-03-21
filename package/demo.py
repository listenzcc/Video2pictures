# %%
import os
import cv2
import time
import numpy as np

import matplotlib.pyplot as plt

from pathlib import Path
import plotly.express as px

from capturer import Capturer

# %%


def _cap_info(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)
    frames = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    seconds = frames / fps
    minutes = seconds / 60
    hours = minutes / 60

    width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    info = dict(
        fps=fps,
        frames=frames,
        seconds=seconds,
        minutes=minutes,
        hours=hours,
        width=width,
        height=height
    )

    return info


# %%
file_path = Path(os.environ.get('home', None), 'Desktop', 'nba.mp4')
file_path

# %%
capturer = Capturer(file_path.as_posix())

image = capturer.get_frame(0)

plt.imshow(image)
plt.title('Frame 0')
plt.show()

capturer.release()

# %%
count = 10

capturer = Capturer(file_path.as_posix())

for j in np.linspace(0, capturer.info['frames'], count, endpoint=False):
    fno = int(j)

    image = capturer.get_frame(fno)

    plt.imshow(image)
    plt.title('Frame {}'.format(fno))
    plt.show()

    pass

capturer.release()

# %%
print('Done')

# %%