# %%
import cv2

import queue
import threading
import numpy as np

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


class Capturer(object):
    def __init__(self, file_path):
        cap = cv2.VideoCapture(file_path)
        info = _cap_info(cap)

        self.cap = cap
        self.info = info
        self.queue = queue.Queue(maxsize=100)

        print('D: Capture is initialized: {}'.format(info))

    def get_frame(self, fno, cvtColor=cv2.COLOR_BGR2RGB):
        fno %= self.info['frames']
        fno = int(fno)

        # self.cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
        grabbed, frame = self.cap.read()

        cv2.flip(frame, 1, frame)  # mirror the image
        if cvtColor is not None:
            frame = cv2.cvtColor(frame, cvtColor)

        frame = np.rot90(frame)

        return frame

    def update_queue(self):
        t = threading.Thread(target=self._update, args={}, daemon=True)
        t.start()

    def _update(self):
        self.keep_update = True
        while self.keep_update:
            if self.queue.not_full:
                try:
                    fno = np.random.randint(0, 100000)
                    frame = self.get_frame(fno)
                    self.queue.put_nowait((fno, frame))
                except queue.Full:
                    continue
                continue
            pass

    def release(self):
        self.cap.release()
        print('D: Capture is released.')
