from PIL import Image, UnidentifiedImageError
import psd_tools
import cv2
import tifffile
import numpy as np



img_path = "/Users/Loshkarev/Downloads/2023-10-12 18-08-57_R4192-SA2984R-EM.psd"
img_path = "/Users/Morkowik/Downloads/1.psb"
dest = "/Users/Morkowik/Downloads/new.jpg"


if img_path.endswith((".psd", ".PSD", ".psb", ".PSB")):
    try:
        img = psd_tools.PSDImage.open(img_path)
        img = img.composite()
    except (UnidentifiedImageError, OSError, OverflowError, ValueError):
        print(f"{img_path}")
        img = Image.open(img_path)

    img = img.convert("RGB")
    img.save(dest)