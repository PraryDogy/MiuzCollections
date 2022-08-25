import cfg
from Gallery.Gui import Create as MainGui
from Utils.Splashscreen import SplashScreen


def LoadAll():
    cfg.ROOT.withdraw()
    
    SplashScreen()
    MainGui()

    cfg.ROOT.deiconify()

cfg.ROOT.after(1, LoadAll)
cfg.ROOT.mainloop()
