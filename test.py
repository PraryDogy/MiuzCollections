import psd_tools
import tifffile
from PIL import Image, ImageChops
import cv2


img_src = "/Users/evlosh/Downloads/15ch16bit.tif"
dest = "/Users/evlosh/Downloads/new.jpg"



img = tifffile.imread(img_src)[:,:,:3]
img = (img/256).astype('uint8')

img = Image.fromarray(img.astype(img.dtype), 'RGB')

img = img.convert("RGB", colors=8)
img.save(dest)

