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
        image = Image.open(src)
        image = ImageOps.exif_transpose(image=image)
        image = self.fit_thumb(img=image, w=150, h=150)
        image = image.convert('RGB')
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    def decode_image(self, img: bytes) -> Image:
        return Image.open(fp=io.BytesIO(img))

    def crop_image(self, img: Image) -> Image:
        width, height = img.size   # Get dimensions
        left = (width - 150)/2
        top = (height - 150)/2
        right = (width + 150)/2
        bottom = (height + 150)/2
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



