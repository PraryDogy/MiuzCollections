from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile
import numpy as np



src = "/Users/Loshkarev/Downloads/2023-10-12 18-08-57_R4192-SA2984R-EM.psd"
dest = "/Users/Loshkarev/Downloads/new.jpg"



if src.endswith((".psd", ".PSD")):
    try:

    except (UnidentifiedImageError, OverflowError):
        print("err")
        img = PSDImage.open(src)
        img = img.composite()
    

img = PSDImage.open(src)
img = img.composite()
img = img.convert("RGB")
img.save(dest)
