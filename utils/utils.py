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
import sqlalchemy
import database
import json

def save_size():
    cfg.ROOT.update_idletasks()
    w, h = cfg.ROOT.winfo_width(), cfg.ROOT.winfo_height()
    x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()

    cfg.config['ROOT_SIZE'] = f'{w}x{h}'
    cfg.config['ROOT_POS'] = f'+{x}+{y}'

    with open(os.path.join(cfg.DB_DIR, 'cfg.json'), 'w') as file:
        json.dump(cfg.config, file, indent=4,)


def place_center(top_level=tkinter.Toplevel):
    """
    Place new tkinter window to center relavive main window.
    * param `top_level`: tkinter.TopLevel
    """
    cfg.ROOT.update_idletasks()
    x, y = cfg.ROOT.winfo_x(), cfg.ROOT.winfo_y()
    xx = x + cfg.ROOT.winfo_width()//2 - top_level.winfo_width()//2
    yy = y + cfg.ROOT.winfo_height()//2 - top_level.winfo_height()//2

    top_level.geometry(f'+{xx}+{yy}')


def create_thumb(src):
    """
    Returns list of img objects with sizes: 150
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

    for size in [(150, 150)]:
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

    def check(self):
        """
        Same as `SmbChecker.__doc__`
        """
        if not os.path.exists(
            os.path.join(os.sep, *cfg.config['PHOTO_DIR'].split('/'))):
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


    def image_resize(self, image, width = None, height = None, inter = cv2.INTER_AREA):
        # initialize the dimensions of the image to be resized and
        # grab the image size
        image = cv2.imread(image)
        dim = None
        (h, w) = image.shape[:2]

        # if both the width and height are None, then return the
        # original image
        if width is None and height is None:
            return image

        # check to see if the width is None
        if width is None:
            # calculate the ratio of the height and construct the
            # dimensions
            r = height / float(h)
            dim = (int(w * r), height)

        # otherwise, the height is None
        else:
            # calculate the ratio of the width and construct the
            # dimensions
            r = width / float(w)
            dim = (width, int(h * r))

        # resize the image
        resized = cv2.resize(image, dim, interpolation = inter)

        # return the resized image
        return resized

def get_coll_name(src):
    """
    Returns collection name.
    Returns `noCollection` if name not found.

    Looking for collection name in path like object.
    Name of collection must be follow next to `cfg.COLL_FOLDER`

    # Example
    ```
    cfg.COLL_FOLDER = "collection"
    collection_path = /path/to/collection/any_collection_name
    print(get_coll_name(collection_path))
    > any_collection_name

    cfg.COLL_FOLDER = "collection"
    collection_path = /some/path/without/coll_folder
    print(get_coll_name(collection_path))
    > noCollection
    ```
    """
    coll_name = 'noCollection'
    if cfg.config['COLL_FOLDER'] in src:
        coll_name = src.split(cfg.config['COLL_FOLDER'])[-1].split(os.sep)[1]
    return coll_name


def insert_row(**kw):
    """
    Adds new line to Database > Thumbs with new thumbnails.
    Creates thumbnails with `create_thumb` method from `utils`
    * param `src`: Image's path
    * param `size`: Image's size `int`
    * param `birth`: Image's date created `int`
    * param `mod`: Date last modified of image `int`
    * param `coll`: name of collection created with `get_coll_name`
    """

    img150 = create_thumb(kw['src'])[0]

    values = {
        'img150': img150, 
        'src':kw['src'], 'size':kw['size'],
        'created':kw['birth'], 'modified':kw['mod'],
        'collection':kw['coll']}

    database.Dbase.conn.execute(sqlalchemy.insert(
        database.Thumbs).values(values))
