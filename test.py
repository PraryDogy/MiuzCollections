from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile




src = "/Users/Loshkarev/Downloads/error large.psd"
dest = "/Users/Loshkarev/Downloads/new.jpg"



if src.endswith((".psd", ".PSD")):
    try:
        img = Image.open(src)

    except (UnidentifiedImageError, OverflowError):
        img = PSDImage.open(src)
        img = img.composite()
    
    img = img.convert("RGB")
    img.save(dest)


# else:
#     img = tifffile.imread(src)
#     img = img[:,:,:3]
#     tifffile.imwrite(dest, img)

    # ch, bit = len(cv2.split(img)), int(str(img.dtype)[4:])



    # if ch > 3 or bit > 8:
    #     print("more than 3 channels")
    #     img = img[:,:,:3]
    #     tifffile.imwrite(dest, img)
    # else:
    #     img.shape
    #     img.dtype
    #     tifffile.imwrite(dest, img)

    # tifffile.imwrite(dest, img)

    # cv2.imshow("1", img)
