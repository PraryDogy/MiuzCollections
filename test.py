from PIL import Image, UnidentifiedImageError
from psd_tools import PSDImage
import cv2
import tifffile


# src = "/Volumes/Shares/Marketing/Photo/_Collections/10 Brilliance/1 IMG/2023-10-09 22-06-29_E01-SS-35613.tif" # 15
src = "/Users/Loshkarev/Downloads/DSC0499.tif" #15
# src = "/Users/Loshkarev/Downloads/2023-10-17 16-43-44.tif" #3

dest = "/Users/Loshkarev/Downloads/new.jpg"

# src = "/Users/Morkowik/Downloads/E2018-ICE-0010_R2018-ICE-0009.psd"
# src = "/Users/Morkowik/Downloads/2023-10-09 22-06-29_E01-SS-35613.tif"
# dest = "/Users/Morkowik/Downloads/new.jpg"

if src.endswith((".psd", ".PSD")):
    img = PSDImage.open(src)
    # img.composite().save(dest)
else:
    img = tifffile.imread(src)
    channels = cv2.split(img)

    if len(channels) > 3:
        # img = img[:,:,::-1]
        print("more")
        img = img[:3]

    # cv2.imshow("1", img)
    # img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    # cv2.waitKey(0) 

    cv2.imwrite(dest, img)
