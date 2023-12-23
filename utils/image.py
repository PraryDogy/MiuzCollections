try:
    from typing_extensions import Literal
except ImportError:
    from typing import Literal

import io

from PIL import Image, ImageChops, ImageEnhance, ImageOps

from .system import SysUtils


class ImageUtils(SysUtils):
    ww = 150
    
    def fit_thumb(self, img: Image, w: int, h: int) -> Image:
        imw, imh = img.size
        delta = imw/imh

        if delta > 1:
            neww, newh = int(h*delta), h
        else:
            neww, newh = w, int(w/delta)
        return img.resize((neww, newh))

    def encode_image(self, src: Literal["file path"]) -> bytes:
        img = Image.open(src)
        img = ImageOps.exif_transpose(image=img)
        img = self.fit_thumb(img=img, w=__class__.ww, h=__class__.ww)
        img = img.convert('RGB')
        img_byte_arr = io.BytesIO()
        img.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def decode_image(self, img: bytes) -> Image:
        return Image.open(fp=io.BytesIO(img))

    def crop_image(self, img: Image) -> Image:
        width, height = img.size   # Get dimensions
        left = (width - __class__.ww)/2
        top = (height - __class__.ww)/2
        right = (width + __class__.ww)/2
        bottom = (height + __class__.ww)/2
        return img.crop((left, top, right, bottom))
    
    def resize_forgrid(self, img: Image, size: int) -> Image:
        return img.resize((size, size))
    
    def add_sharp(self, img: Literal["PIL img"], factor: int) -> Literal["PIL img"]:
        return ImageEnhance.Sharpness(image=img).enhance(factor=factor)

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



