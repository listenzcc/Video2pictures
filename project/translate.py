# %%
import io
import cv2
from PIL import Image
import numpy as np

# %%
img = np.random.randint(0, 255, size=(10, 20, 3), dtype=np.uint8)


# %%
success, arr = cv2.imencode('.png', img)

bytes = arr.tobytes()
bytes[:10], len(bytes)

# %%
image = Image.open(io.BytesIO(bytes))
np.array(image) - cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

# %%
_arr = np.frombuffer(bytes, np.uint8)

arr - _arr

# %%
_img = cv2.imdecode(arr, cv2.IMREAD_ANYCOLOR)

img - _img


# %%
type(bytes)
# %%
# %%
