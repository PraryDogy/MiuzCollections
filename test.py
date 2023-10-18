from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile

src = "/Volumes/Shares/Marketing/Photo/_Collections/2 Flaming Ice/1 IMG/E2018-ICE-0010_R2018-ICE-0009.psd"
src = "/Volumes/Shares/Marketing/Photo/_Collections/10 Brilliance/1 IMG/2023-10-09 22-06-29_E01-SS-35613.tif"
dest = "/Users/Loshkarev/Downloads/new.jpg"

src = "/Users/Morkowik/Downloads/E2018-ICE-0010_R2018-ICE-0009.psd"
# src = "/Users/Morkowik/Downloads/2023-10-09 22-06-29_E01-SS-35613.tif"
dest = "/Users/Morkowik/Downloads/new.jpg"

if src.endswith((".psd", ".PSD")):
    img = PSDImage.open(src)
    img.composite().save(dest)
else:
    img = tifffile.imread(src)
    img = img[:,:,:3]
    b,g,r = cv2.split(img)
    img = cv2.merge([r, g, b])
    cv2.imwrite(dest, img)
