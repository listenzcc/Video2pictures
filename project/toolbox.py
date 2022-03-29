# %%
import cv2
import numpy as np

from onstart import LOGGER, CFG

# %%


def _bytes(string, coding=CFG['TCP']['coding']):
    '''
    Code the string into bytes

    Args:
        - buf: The input buf, if it is string, it will be converted to bytes; if it is bytes, it will be left no changed.
        - coding: The coding to use, it has default value.

    Output:
        Return the bytes of coding.
    '''
    return bytes(string, coding)

# %%


def _pic_encoder(img):
    '''
    Encode image into bytes, using .png format

    Args:
        - img: The input image, shape is (width, height, 3), dtype is uint8.

    Output:
        - bytes: The image coding bytes.
    '''
    assert(img.dtype == np.uint8)
    assert(len(img.shape) == 3)
    assert(img.shape[2] == 3)

    success, arr = cv2.imencode('.png', img)

    bytes = arr.tobytes()

    return bytes

# %%


def _pic_decoder(bytes):
    '''
    Decode image from bytes, using default method

    Args:
        - bytes: The bytes to decode.

    Output:
        - img: The decoded image, shape is (width, height, 3), dtype is uint8.
        - Return None if it fails on decoding.
    '''
    assert(isinstance(bytes, type(b'a')))

    try:
        arr = np.frombuffer(bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    except:
        LOGGER.error('Image decode failed')
        return None

    return img

# %%


if __name__ == '__main__':
    img = np.random.randint(0, 255, size=(10, 20, 3), dtype=np.uint8)

    _img = _pic_decoder(_pic_encoder(img))

    LOGGER.info('Toolbox self-check,')
    LOGGER.info('It should be two zeros: {}, {}'.format(np.max(img-_img),
                                                        np.min(img-_img)))
