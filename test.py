from PIL import Image, UnidentifiedImageError
import psd_tools
import cv2
import tifffile
import numpy as np



img_path = "/Users/Loshkarev/Downloads/2023-10-12 18-08-57_R4192-SA2984R-EM.psd"
img_path = "/Users/evlosh/Downloads/15ch8bit.tif"
dest = "/Users/evlosh/Downloads/new.jpg"


img = tifffile.imread(img_path)[:,:,:3]

if str(img.dtype) == "uint16":
    print(123)
    img = (img/256).astype('uint8')

img = Image.fromarray(img.astype('uint8'), 'RGB')
img.save(dest)