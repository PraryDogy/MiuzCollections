import cfg
from Gallery.main_gui import MainGui
from Utils.Splashscreen import SplashScreen


def LoadAll():

    SplashScreen()
    MainGui()

    cfg.ROOT.deiconify()

cfg.ROOT.after(1, LoadAll)
cfg.ROOT.mainloop()
