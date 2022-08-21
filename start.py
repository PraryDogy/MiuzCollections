import cfg
from DbChecker.DbCheck import Check as DbCheck
from Gallery.Gui import Create as MainGui
from NetChecker.NetworkCheck import Check as NetwotkCheck
from SmbChecker.Gui import Create as SmbGui
from SmbChecker.SmbCheck import Check as SmbCheck   
from SplashScreen.Gui import Create as SplashScreen


def LoadAll():
    cfg.ROOT.withdraw()

    if not NetwotkCheck():
        return

    DbCheck()
    SmbGui() if not SmbCheck() else SplashScreen()    
    MainGui()
    cfg.ROOT.deiconify()


cfg.ROOT.after(1, LoadAll)
cfg.ROOT.mainloop()