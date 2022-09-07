"""
* create_thumb
* my_copy
* my_paste
* SmbChecker
* MyButton
* MyFrame
* MyLabel
"""

import os
import subprocess
import tkinter

import cfg
import cv2
from skimage.metrics import structural_similarity
import numpy as np


def create_thumb(src):
    """
    Returns list of img objects with sizes: 150, 200, 250, 300
    """
    img = cv2.imread(src)
    width, height = img.shape[1], img.shape[0]

    if height >= width:
        delta = (height-width)//2
        new_img = img[delta:height-delta, 0:width]

    else:
        delta = (width-height)//2
        new_img = img[0:height, delta:width-delta]

    resized = []

    for size in [(150, 150), (200, 200), (250, 250), (300, 300)]:
        newsize = cv2.resize(
            new_img, size, interpolation = cv2.INTER_AREA)
        encoded = cv2.imencode('.jpg', newsize)[1].tobytes()
        resized.append(encoded)

    return resized


def my_copy(output):
    """
    Custom copy to clipboard with subprocess
    """
    process = subprocess.Popen(
        'pbcopy', env={'LANG': 'en_US.UTF-8'}, stdin=subprocess.PIPE)
    process.communicate(output.encode('utf-8'))
    print('copied')


def my_paste():
    """
    Custom paste from clipboard with subprocess
    """
    print('pasted')
    return subprocess.check_output(
        'pbpaste', env={'LANG': 'en_US.UTF-8'}).decode('utf-8')


class SmbChecker(tkinter.Toplevel):
    """
    Checks smb disk availability with `cfg.PHOTO_DIR` os.exists method.
    * Returns `False` if `cfg.PHOTO_DIR` not exists
    * Shows gui with error if `cfg.PHOTO_DIR` not exists
    * `cfg.PHOTO_DIR` can be changed in cfg.json or in settings
    """
    def __init__(self):
        tkinter.Toplevel.__init__(
            self, cfg.ROOT, bg=cfg.BGCOLOR, padx=10, pady=10)
        self.withdraw()
        self.check()

    def check(self):
        """
        Same as `SmbChecker.__doc__`
        """
        if not os.path.exists(os.path.join(os.sep, *cfg.PHOTO_DIR.split('/'))):
            self.gui()
            return False
        self.destroy()
        return True

    def gui(self):
        """
        SmbChecker's gui
        """
        self.focus_force()
        self.title('Нет подключения')
        self.resizable(0,0)

        txt = 'Нет подключения к сетевому диску Miuz. '
        title_lbl = MyLabel(
            self, text=txt, font=('Arial', 22, 'bold'), wraplength=350)
        title_lbl.pack(pady=(10, 20), padx=20)

        txt2 =(
            '- Проверьте подключение к интернету. '
            '\n\n- Откройте любую папку на сетевом диске,'
            '\nвведите логин и пароль, если требуется'
            '\n\n- Откройте настройки > дополнительно, введите'
            '\nправильный путь до галерии изображений'
            '\nи перезапустите приложение.'
            '\n\nПоддержка: loshkarev@miuz.ru'
            '\nTelegram: evlosh'
            )
        descr_lbl = MyLabel(self, text=txt2, justify=tkinter.LEFT)
        descr_lbl.pack(padx=15, pady=(0, 15))

        cls_btn = MyButton(self, text='Закрыть')
        cls_btn.cmd(lambda e: self.destroy())
        cls_btn.pack()

        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.deiconify()
        self.grab_set()


class MyButton(tkinter.Label):
    """
    Tkinter Label with custom style.
    * method `cmd`: bind function to mouse left click
    * method `press`: simulate button press with button's bg color
    """

    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(
            bg=cfg.BGBUTTON, fg=cfg.FONTCOLOR,
            width=17, height=2)

    def cmd(self, cmd):
        """
        Binds tkinter label to mouse left click.
        * param `cmd`: lambda e: some_function()
        """
        self.bind('<Button-1>', cmd)

    def press(self):
        """
        Simulates button press with button's bg color
        """
        self.configure(bg=cfg.BGPRESSED)
        cfg.ROOT.after(100, lambda: self.configure(bg=cfg.BGBUTTON))


class MyFrame(tkinter.Frame):
    """
    Tkinter Frame with custom style.
    """
    def __init__(self, master, **kwargs):
        tkinter.Frame.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR)


class MyLabel(tkinter.Label):
    """
    Tkinter Label with custom style.
    """
    def __init__(self, master, **kwargs):
        tkinter.Label.__init__(self, master, **kwargs)
        self.configure(bg=cfg.BGCOLOR, fg=cfg.FONTCOLOR)


class Scrollable(tkinter.Frame):
    """
    Example scrollable frame.
    """
    def __init__(self, master):
        tkinter.Frame.__init__(self, master)

        canvas = tkinter.Canvas(
            self, bg=cfg.BGCOLOR, highlightbackground=cfg.BGCOLOR)

        scrollbar = tkinter.Scrollbar(
            self, width=12, orient='vertical', command=canvas.yview)

        scrollable = tkinter.Frame(canvas)

        scrollable.bind("<Configure>", lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")))

        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(
            -1*(e.delta), "units"))
            # lambda e: canvas.yview_scroll(-1*(e.delta/120), "units")

        canvas.create_window((0,0), window=scrollable, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        self.pack(fill=tkinter.BOTH, expand=True)
        canvas.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)
        scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)


class Compare(list):
    def __init__(self):
        images = list(cfg.IMAGES_COMPARE)
        print(images)
        before = cv2.imread(images[0])
        after = cv2.imread(images[1])

        # Convert images to grayscale
        before_gray = cv2.cvtColor(before, cv2.COLOR_BGR2GRAY)
        after_gray = cv2.cvtColor(after, cv2.COLOR_BGR2GRAY)

        # Compute SSIM between the two images
        (score, diff) = structural_similarity(before_gray, after_gray, full=True)
        print("Image Similarity: {:.4f}%".format(score * 100))

        # The diff image contains the actual image differences between the two images
        # and is represented as a floating point data type in the range [0,1] 
        # so we must convert the array to 8-bit unsigned integers in the range
        # [0,255] before we can use it with OpenCV
        diff = (diff * 255).astype("uint8")
        diff_box = cv2.merge([diff, diff, diff])

        # Threshold the difference image, followed by finding contours to
        # obtain the regions of the two input images that differ
        thresh = cv2.threshold(diff, 0, 255, cv2.THRESH_BINARY_INV | cv2.THRESH_OTSU)[1]
        contours = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = contours[0] if len(contours) == 2 else contours[1]

        mask = np.zeros(before.shape, dtype='uint8')
        filled_after = after.copy()

        for c in contours:
            area = cv2.contourArea(c)
            if area > 40:
                x,y,w,h = cv2.boundingRect(c)
                cv2.rectangle(before, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.rectangle(after, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.rectangle(diff_box, (x, y), (x + w, y + h), (36,255,12), 2)
                cv2.drawContours(mask, [c], 0, (255,255,255), -1)
                cv2.drawContours(filled_after, [c], 0, (0,255,0), -1)
        
        cv2.imshow('before', before)
        cv2.imshow('after', after)
        cv2.waitKey()
