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
row, clmn = 0, 0
new = Image.new("RGBA", (150*4,150*5), color=cfg.BG)

for num, im in enumerate(images, 1):

    new.paste(im, (row, clmn))

    clmn += 150 + 2
    if num % clmns == 0:
        row += 150 + 2
        clmn = 0


img = ImageTk.PhotoImage(new)
lbl = tk.Label(scrollable, image=img)
lbl.pack()
lbl.image_names = img


def click(event: tk.Event):
    x, y = event.x, event.y
    row = (y//150) + 1
    clmn = (x//150) + 1

    print(row, clmn)

lbl.bind('<Button-1>', click)
root.mainloop()
