# %%
import cv2
import numpy as np

# %%


def _pic_encoder(img):
    assert(img.dtype == np.uint8)
    assert(len(img.shape) == 3)
    assert(img.shape[2] == 3)

    success, arr = cv2.imencode('.png', img)

    bytes = arr.tobytes()

    return bytes

# %%


def _pic_decoder(bytes):
    assert(isinstance(bytes, type(b'a')))

    try:
        arr = np.frombuffer(bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except:
        return None

    return img

# %%


if __name__ == '__main__':
    img = np.random.randint(0, 255, size=(10, 20, 3), dtype=np.uint8)

    _img = _pic_decoder(_pic_encoder(img))

    print('It should be two zeros:', np.max(img-_img), np.min(img-_img))
