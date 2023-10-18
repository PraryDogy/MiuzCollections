from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile
import imageio.v3 as iio
import numpy as np


src = "/Volumes/Shares/Marketing/Photo/_Collections/2 Flaming Ice/1 IMG/E2018-ICE-0010_R2018-ICE-0009.psd"
src = "/Volumes/Shares/Marketing/Photo/_Collections/10 Brilliance/1 IMG/2023-10-09 22-06-29_E01-SS-35613.tif"
dest = "/Users/Loshkarev/Downloads/new.jpg"

if src.split("/")[-1].split(".")[-1] in ("psd", "PSD"):
    img = PSDImage.open(src)
    img = img.composite().save(dest)
else:
    # img = tifffile.TiffFile(src)
    # tifffile.imsave(dest, src, compression = "jpeg")
    # img = iio.imread(src)
    # img = iio.imwrite(dest, src, compression="jpeg")
    im = np.asarray(Image.open(src))
