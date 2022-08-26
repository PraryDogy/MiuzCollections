import tkinter

from PIL import Image, ImageOps, ImageTk


class OpenImage(tkinter.Frame):
    def __init__(self, master, src):
        super().__init__(master)

        self.image = Image.open(src)
        self.img_copy= self.image.copy()

        self.image = ImageOps.contain(self.img_copy, (500,500))
        
        self.background_image = ImageTk.PhotoImage(self.image)

        self.background = tkinter.Label(self, image=self.background_image)
        self.background.pack(fill='both', expand=True)
        self.background.bind('<Configure>', self._resize_image)


    def _resize_image(self,event):

        new_width = event.width
        new_height = event.height

        self.image = ImageOps.contain(self.img_copy, (new_width,new_height))

        self.background_image = ImageTk.PhotoImage(self.image)
        self.background.configure(image =  self.background_image)
