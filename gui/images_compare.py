import subprocess
import tkinter

import cfg
from utils import MyButton, MyFrame, MyLabel, my_copy, place_center
from .ask_exit import AskExit
import os

vars = {
    'img1': (tkinter.Label, tkinter.Label, tkinter.Label),
    'img2': (tkinter.Label, tkinter.Label, tkinter.Label),
    'curr_img': 'img1 or img2',
    'img_frame': tkinter.Label,
    'img_info': tkinter.Label,
    }


def get_all_windows():
    return tuple(v for k, v in cfg.ROOT.children.items() if "preview" in k)


def on_closing(obj: tkinter.Toplevel):
    """
    Destroys current tkinter toplevel.
    Clears `cfg.IMAGES_COMPARE` list.
    * param `obj`: tkinter toplevel
    """
    cfg.STATUSBAR_NORMAL()
    for i in cfg.THUMBS:
        if (
            i['text'] == vars['img1']['src'] or
            i['text'] == vars['img2']['src']):
            i.configure(bg=cfg.BGCOLOR)
            break
    [i.destroy() for i in get_all_windows()]
    obj.destroy()
    cfg.COMPARE = False
    cfg.ROOT.focus_force()


class ImagesCompare(tkinter.Toplevel):
    """
    A new tkinter window containing two images and
    a button with an image switch.
    You can click the toggle button to see the difference between similar
    images
    """
    def __init__(self):
        tkinter.Toplevel.__init__(self, bg=cfg.BGCOLOR, padx=15, pady=15)
        cfg.ROOT.eval(f'tk::PlaceWindow {self} center')
        self.withdraw()

        self.title('Сравнение')

        self.protocol("WM_DELETE_WINDOW", lambda: on_closing(self))
        self.bind('<Command-w>', lambda e: on_closing(self))
        self.bind('<Escape>', lambda e: on_closing(self))
        self.bind('<Command-q>', lambda e: AskExit(cfg.ROOT))

        self.resizable(0,0)
        side = int(cfg.ROOT.winfo_screenheight()*0.8)
        self.geometry(f'{side}x{side}')
        cfg.ROOT.update_idletasks()

        prevs = get_all_windows()
        img1_info = tuple(prevs[0].children.values())
        img2_info = tuple(prevs[1].children.values())
        
        # prev item is toplevel window with image preview
        # prev item 0 = image source text
        # prev item 1 = tkinter label with image
        # prev item 3 = tkinter frame with labels, img info is label with
        # image info
        
        vars['img1'] = {
            'src': img1_info[0]['text'],
            'image': img1_info[1]['image'],
            'info': img1_info[3].children['!imginfo']['text'],
            }

        vars['img2'] = {
            'src': img2_info[0]['text'],
            'image': img2_info[1]['image'],
            'info': img2_info[3].children['!imginfo']['text'],
            }

        vars['curr_img'] = vars['img1']

        image_frame = ImageFrame(self)
        image_frame.pack(expand=True, fill=tkinter.BOTH)

        left_frame = MyFrame(self)
        left_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)
        FakeBtn(left_frame).pack(expand=True, fill=tkinter.X)

        center_frame = MyFrame(self)
        center_frame.pack(side=tkinter.LEFT, fill=tkinter.X)

        ImgButtons(center_frame).pack(pady=(15, 15))
        ImgInfo(center_frame).pack(
            pady=(0, 15), padx=15, fill=tkinter.Y, expand=True)
        CloseBtn(center_frame).pack()

        right_frame = MyFrame(self)
        right_frame.pack(side=tkinter.LEFT, expand=True, fill=tkinter.X)
        FakeBtn(right_frame).pack(expand=True, fill=tkinter.X)

        image_frame.set_size()
        place_center(self)
        self.deiconify()
        self.grab_set()

def switch_image():
    """
    Switches between two images from cfg.IMAGES_COMPARE set.
    """
    for i in [vars['img1'], vars['img2']]:
        if vars['curr_img'] != i:
            vars['curr_img'] = i
            vars['img_frame']['image'] = vars['curr_img']['image']
            vars['img_info']['text'] = vars['curr_img']['info']
            return


class ImageFrame(MyLabel):
    """
    Creates tkinter label with image.
    * param `master`: tkinter toplevel.
    """
    def __init__(self, master):
        MyLabel.__init__(self, master, borderwidth=0)
        self['bg']='black'
        self['image'] = vars['curr_img']['image']
        vars['img_frame'] = self
        self.bind('<ButtonRelease-1>', lambda e: switch_image())

    def set_size(self):
        cfg.ROOT.update_idletasks()

        win_h = self.winfo_toplevel().winfo_height()
        win_w = self.winfo_toplevel().winfo_width()

        widgets = tuple(self.winfo_toplevel().children.values())[2:]
        widgets_h = sum(i.winfo_reqheight() for i in widgets)
        
        new_h = win_h-widgets_h
        self.configure(height=new_h, width=win_w)


class FakeBtn(MyButton):
    def __init__(self, master):
        MyButton.__init__(self, master)
        self.configure(bg=cfg.BGCOLOR, text='•', font=('Arial', 22, 'bold'))
        self.cmd(lambda e: switch_image())
        self.unbind('<Enter>')
        self.unbind('<Leave>')


class ImgButtons(MyFrame):
    """
    Tkinter frame with buttons:
    * copy image name
    * open image folder
    * switch to second image
    """
    def __init__(self, master):
        MyFrame.__init__(self, master)
        b_wight = 13

        copy_btn = MyButton(self, text='Копировать имя')
        copy_btn.configure(height=1, width=b_wight)
        copy_btn.cmd(lambda e: self.copy_name(copy_btn))
        copy_btn.pack(side=tkinter.LEFT, padx=(0, 15))

        open_btn = MyButton(self, text='Папка с фото')
        open_btn.configure(height=1, width=b_wight)
        open_btn.cmd(lambda e: self.open_folder(open_btn))
        open_btn.pack(side=tkinter.LEFT, padx=(0, 15))

    def copy_name(self, btn: MyButton):
        """
        Copies path to folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        get_name = vars['curr_img']['src'].split(os.sep)[-1].split('.')[0]
        my_copy(get_name)

    def open_folder(self, btn: MyButton):
        """
        Opens folder with image.
        Simulates button press with color.
        * param `btn`: current tkinter button.
        """
        btn.press()
        path = os.sep.join(vars['curr_img']['src'].split(os.sep)[:-1])
        subprocess.check_output(["/usr/bin/open", path])


class ImgInfo(MyLabel):
    """
    Creates tkinter frame with image info.
    * param `master`: tkinter top level.
    """
    def __init__(self, master):
        MyLabel.__init__(
            self, master, anchor=tkinter.W, justify=tkinter.LEFT,
            text=vars['curr_img']['info'], width=43)
        vars['img_info'] = self


class CloseBtn(MyButton):
    """
    Creates tkinter frame for open and close buttons.
    * param `master`: tkinter frame.
    """
    def __init__(self, master):
        MyButton.__init__(self, master, text='Закрыть')
        self.configure(height=1, width=13)
        self.cmd(lambda e: on_closing(self.winfo_toplevel()))
