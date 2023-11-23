try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

import cv2
import numpy
from PIL import Image, ImageChops

from cfg import cnf

from .system import SysUtils


class ImageUtils(SysUtils):
    def resize_image(self, img: Literal["cv2 image"], wid_w: int, wid_h: int,
                     is_thumb: bool) -> Literal["cv2 image"]:
        h, w = img.shape[:2]
        aspect = w/h
        if is_thumb:
            if aspect > 1:
                new_h, new_w = wid_h, round(wid_h*aspect)
            elif aspect < 1:
                new_h, new_w = round(wid_w/aspect), wid_w
            elif aspect == 1:
                new_h, new_w = wid_h, wid_h
        else:
            f1 = wid_w / w
            f2 = wid_h / h
            f = f2
            new_w, new_h = (int(w * f), int(h * f))

        return cv2.resize(img, (new_w, new_h), interpolation=cv2.INTER_AREA)


    def replace_bg(self, img: Literal["cv2 image"], color: str) -> Literal["cv2 image"]:
        try:
            trans_mask = img[:,:,3 ] == 0
            color = color.replace("#", "")
            bg_color = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
            img[trans_mask] = [*bg_color, 255]
        except IndexError:
            self.print_err()
            return img
        return img


    def encode_image(self, src: Literal["file path"]) -> Literal["cv2 image"]:
        image = cv2.imread(src, cv2.IMREAD_UNCHANGED)

        if src.endswith((".png", ".PNG")):
            image = self.replace_bg(image, cnf.bg_color)

        try:
            resized = self.resize_image(image, cnf.thumbsize, cnf.thumbsize, True)
            return cv2.imencode(".jpg", resized)[1].tobytes()

        except (cv2.error, UnboundLocalError, AttributeError) as e:
            self.print_err()
            image = cv2.imread("thumb.jpg", cv2.IMREAD_UNCHANGED)
            return cv2.imencode(".jpg", image)[1].tobytes()


    def decode_image(self, img: bytes) -> Literal["cv2 image"]:
        try:
            nparr = numpy.frombuffer(img, numpy.byte)
            return cv2.imdecode(nparr, cv2.IMREAD_ANYCOLOR)
        except TypeError:
            self.print_err()
            return self.decode_image(self.encode_image(cnf.thumb_err))


    def convert_to_rgb(self, img: Literal["cv2 image"]) -> Image:
        # convert cv2 color to rgb
        image_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        # load numpy array image
        return Image.fromarray(image_rgb)


    def crop_image(self, img: Literal["cv2 image"]) -> Literal["cv2 image"]:
        width, height = img.shape[1], img.shape[0]
        if height >= width:
            delta = (height-width)//2
            cropped = img[delta:height-delta, 0:width]
        else:
            delta = (width-height)//2
            cropped = img[0:height, delta:width-delta]
        return cropped[0:cnf.thumbsize, 0:cnf.thumbsize]


    def black_borders(self, img: Image) -> Image:
        try:
            bg = Image.new(img.mode, img.size, img.getpixel((0,0)))
            diff = ImageChops.difference(img, bg)
            diff = ImageChops.add(diff, diff, 2.0, -100)
            bbox = diff.getbbox()

            if bbox:
                img = img.crop(bbox)

            return img

        except Exception as e:
            self.print_err()
            return img



