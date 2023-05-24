import tkinter as tk
from PIL import Image as Image, ImageTk
from database import Dbase, Thumbs
import sqlalchemy
from utils import *
import numpy
from random import randint
import cfg
import tkmacosx

q = sqlalchemy.select(Thumbs.img150, Thumbs.src, Thumbs.modified).limit(20)
res = Dbase.conn.execute(q).fetchall()

root = cfg.ROOT
root.deiconify()

scrollable = tkmacosx.SFrame(root)
scrollable.pack(expand=True, fill="both")

images = []

for blob, src, modified in res:
    decoded = decode_image(blob)
    cropped = crop_image(decoded)
    rgb = convert_to_rgb(cropped)
    images.append(rgb)

clmns = 5
pad = 2
size = cfg.THUMB_SIZE + pad

new = Image.new("RGBA", (size * 4, size * 5), color=cfg.BG)

row, clmn = 0, 0
for num, im in enumerate(images, 1):

    new.paste(im, (row, clmn))

    clmn += size
    if num % clmns == 0:
        row += size
        clmn = 0


img = ImageTk.PhotoImage(new)
lbl = tk.Label(scrollable, image=img)
lbl.pack()
lbl.image_names = img


def click(event: tk.Event):
    x, y = event.x, event.y
    row = (y//size) + 1
    clmn = (x//size) + 1

    print(row, clmn)

lbl.bind('<Button-1>', click)
root.mainloop()
