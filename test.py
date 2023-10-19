from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile


src = "/Users/Loshkarev/Downloads/15ch16bit.tif"
# src = "/Users/Loshkarev/Downloads/15ch8bit.tif"
# src = "/Users/Loshkarev/Downloads/3ch16bit.tif"

dest = "/Users/Loshkarev/Downloads/new.jpg"


if src.endswith((".psd", ".PSD")):
    img = PSDImage.open(src)
    # img.composite().save(dest)
else:
    img = tifffile.imread(src)
    channels = cv2.split(img)

    ch, bit = len(cv2.split(img)), img.dtype


    print(ch, bit)

    # if len(channels) > 3:
    #     print("more than 3 channels")
    #     img = img[:,:,:3]
    #     img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    #     cv2.imwrite(dest, img)
    # else:
    #     img.shape
    #     img.dtype
    #     tifffile.imwrite(dest, img)

    tifffile.imwrite(dest, img)

    # cv2.imshow("1", img)
    # cv2.waitKey(0) 

