import psd_tools
import tifffile
from PIL import Image, ImageChops
import cv2


img_src = "/Users/evlosh/Downloads/black.tif"
dest = "/Users/evlosh/Downloads/new.jpg"


if img_src.endswith((".psd", ".PSD", ".psb", ".PSB")):

    try:
        img = psd_tools.PSDImage.open(img_src).composite()
    except Exception:
        try:
            img = Image.open(img_src)
        except Exception:
            print(f"utils > fullsize psd open > {img_src}")

    try:
        bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
        diff = ImageChops.difference(img, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            img = img.crop(bbox)
    except Exception as e:
        print("utils > can't crop PSD")
        print(e)

    try:
        img = img.convert("RGB", colors=8)
        img.save(dest)
    except Exception:
        print(f"utils > fullsize psd save > {img_src}")

else:
    try:
        img = tifffile.imread(img_src)[:,:,:3]

        if str(img.dtype) == "uint16":
            img = (img/256).astype('uint8')

        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray,1,255,cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(
            thresh,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE
            )
        cnt = contours[0]
        x,y,w,h = cv2.boundingRect(cnt)
        img = img[y:y+h,x:x+w]

        img = Image.fromarray(img.astype('uint8'), 'RGB')
        img.save(dest)

    except Exception as e:
        print(f"utils > fullsize tiff > {img_src}")
        print(e)