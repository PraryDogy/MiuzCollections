from database import *
import sqlalchemy
from math import ceil
from PIL import Image
from utils import decode_image, convert_to_rgb, crop_image
import os

def create(coll):
    obtravka = "Обтравка"
    q = sqlalchemy.select(Thumbs.img150)
    q = q.filter(Thumbs.collection.like("%" + coll + "%"))
    q = q.filter(Thumbs.src.not_like("%"+ "2 Model IMG" +"%"))
    q = q.filter(Thumbs.src.not_like("%"+ obtravka +"%"))
    q = q.order_by(-Thumbs.modified)

    res = Dbase.conn.execute(q).fetchall()
    images = [i[0] for i in res]

    if len(images) == 0:
        q = sqlalchemy.select(Thumbs.img150)
        q = q.filter(Thumbs.collection.like("%" + coll + "%"))
        q = q.filter(Thumbs.src.not_like("%"+ "2 Model IMG" +"%"))
        q = q.order_by(-Thumbs.modified)

    res = Dbase.conn.execute(q).fetchall()
    images = [i[0] for i in res]   


    clmns_count = 15
    if len(images) < 15 and len(images) > 0:
        clmns_count = len(images)

    size = 152

    w = size * clmns_count
    h = size * (ceil(len(images) / clmns_count))
    empty = Image.new("RGB", (w, h), color=0)
    row, clmn = 0, 0

    for x, im in enumerate(images, 1):
        im = decode_image(im)
        im = crop_image(im)
        im = convert_to_rgb(im)

        empty.paste(im, (clmn, row))

        clmn += size
        if x % clmns_count == 0:
            row += size
            clmn = 0

    try:
        empty.save("/Users/Loshkarev/Desktop/screens/" + coll + ".jpg")
    except ValueError:
        print("error write" + coll)


colls = "/Volumes/Shares/Marketing/Photo/_Collections"
colls = [i for i in os.listdir(colls)]

for i in colls:
    create(i)