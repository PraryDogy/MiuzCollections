from .settings import Settings
from .img_compare import ImgCompare
from .img_viewer import ImgViewer
from .macosx_menu import BarMenu
from .st_bar import StatusBar
from .gallery import Gallery
from .widgets import AskExit, CSep
import tkinter
import cfg


class InitGui:
    def __init__(self):
        cfg.ROOT.title(cfg.APP_NAME)
        cfg.ROOT.configure(bg=cfg.BGCOLOR)

        cfg.ROOT.createcommand(
            'tk::mac::ReopenApplication', lambda: cfg.ROOT.deiconify())
        cfg.ROOT.createcommand("tk::mac::Quit" , AskExit)

        cfg.ROOT.bind('<Command-w>', lambda e: cfg.ROOT.iconify())

        if cfg.config['MINIMIZE'] == 1:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", lambda: cfg.ROOT.iconify())
        else:
            cfg.ROOT.protocol("WM_DELETE_WINDOW", AskExit)

        CSep(cfg.ROOT).pack(fill=tkinter.X, pady=15)

        gallery_widget = Gallery(cfg.ROOT)
        gallery_widget.pack(fill=tkinter.BOTH, expand=1)

        CSep(cfg.ROOT).pack(fill=tkinter.X, pady=10)

        stbar_widget = StatusBar(cfg.ROOT)
        stbar_widget.pack(pady=(0, 10))

        BarMenu()

        cfg.ROOT.eval(f'tk::PlaceWindow {cfg.ROOT} center')

        if cfg.config['ROOT_W'] < 50 or cfg.config['ROOT_H'] < 50:
            cfg.config['ROOT_W'], cfg.config['ROOT_H'] = 700, 500

        cfg.ROOT.geometry(
            (f"{cfg.config['ROOT_W']}x{cfg.config['ROOT_H']}"
            f"+{cfg.config['ROOT_X']}+{cfg.config['ROOT_Y']}")
            )