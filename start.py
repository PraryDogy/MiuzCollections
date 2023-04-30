try:
    import sys
    import traceback

    import cfg
    from gui import Gui
    from gui.widgets import SmbAlert
    from scaner import scaner
    from utils import smb_check


    def load_all():
        Gui()
        cfg.ROOT.deiconify()
        if smb_check():
            scaner()
        else:
            SmbAlert()

    cfg.ROOT.after(1, load_all)
    cfg.ROOT.mainloop()

except Exception as e:
    e_type, e_val, e_tb = sys.exc_info()
    with open(f"{cfg.CFG_DIR}/log.txt", "w") as file:
        traceback.print_exception(e_type, e_val, e_tb, file = file)

    with open(f"{cfg.CFG_DIR}/log.txt", "r") as file:
        print(file.read())