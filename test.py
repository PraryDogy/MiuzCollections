import tkinter as tk
# Uses Python Imaging Library.
from PIL import Image as ImagePIL, ImageTk

root = tk.Tk()
canvas = tk.Canvas(root, height=500, width=500, highlightthickness=0)
canvas.pack()
images = dict()
for name in ['up', 'down']:
    im = ImagePIL.open('im_{}.png'.format(name))
    # Resize the image to 10 pixels square.
    im = im.resize((30, 30), ImagePIL.Resampling.LANCZOS)
    images[name] = ImageTk.PhotoImage(im, name=name)

def set_cell_image(coord, image):
    # Get position of centre of cell.
    x, y = ((p + 0.5) * 30 for p in coord)
    canvas.create_image(x, y, image=image)

for i in range(10):
    for j in range(10):
        set_cell_image((i, j), images['up'])

def click(event):
    coord = tuple(getattr(event, p)/10 for p in ['x', 'y'])
    set_cell_image(coord, images['down'])
    print(coord)


canvas.bind('<Button-1>', click)
root.mainloop()