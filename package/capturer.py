# %%
import cv2

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

        self.grabbed, self.frame = self.cap.read()

        self.info = info

        print('D: Capture is initialized: {}'.format(info))

    def get_frame(self, fno, cvtColor=cv2.COLOR_BGR2RGB):
        fno %= self.info['frames']
        fno = int(fno)

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, fno)
        self.grabbed, self.frame = self.cap.read()

        if cvtColor is not None:
            self.frame = cv2.cvtColor(self.frame, cvtColor)

        return self.frame

    # def stop(self):
    #     self.stopped = True

    def release(self):
        self.cap.release()
        print('D: Capture is released.')
