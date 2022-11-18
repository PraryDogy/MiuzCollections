import tkinter

import cv2
from PIL import Image, ImageTk

root = tkinter.Tk()
root.configure(padx=15, pady=15)

fr = tkinter.Frame(root)
fr.pack()

lbl = tkinter.Label(fr, width=150, height=150)
img = Image.open('/Users/Loshkarev/Desktop/hor.jpg')
img_tk = ImageTk.PhotoImage(img)
lbl['image'] = img_tk
lbl.image = img_tk
lbl.pack(side=tkinter.LEFT)

lbl2 = tkinter.Label(fr, width=150, height=150)
img2 = Image.open('/Users/Loshkarev/Desktop/ver.jpg')
img_tk2 = ImageTk.PhotoImage(img2)
lbl2['image'] = img_tk2
lbl2.image = img_tk2
lbl2.pack(side=tkinter.LEFT)

root.eval(f'tk::PlaceWindow {root} center')
root.mainloop()
