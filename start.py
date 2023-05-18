try:
    import sys
    import traceback

    import cfg
    from gui.widgets import SmbAlert
    from scaner import scaner
    from utils import smb_check

    cfg.ROOT.deiconify()

    if smb_check():
        scaner()
    else:
        SmbAlert()

    cfg.ROOT.mainloop()

except Exception as e:
    import os
    e_type, e_val, e_tb = sys.exc_info()

    path = os.path.join(
        os.path.expanduser("~"),
        "Library", "Application Support", "MiuzCollections", "log.txt"
        )

    with open(path, "w") as file:
        traceback.print_exception(e_type, e_val, e_tb, file=file)

    with open(path, "r") as file:
        print(file.read())