from PIL import Image, ImageDraw
import cfg
import os
from random import randint

def create_images():
    name = "667 Others"

    os.mkdir(f"{cfg.config['COLL_FOLDER']}/{name}")
    path = f"{cfg.config['COLL_FOLDER']}/{name}"

    count = 0
    for i in range(1, 600):
        new = Image.new("RGB", (150, 150), color=(randint(1, 254),randint(1, 254),randint(1, 254)))

        new.save(f"{path}/image {count}.jpg")
        count += 1

# create_images()
