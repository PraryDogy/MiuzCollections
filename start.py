try:
    import sys
    import traceback

    from cfg import cnf
    from gui import app

    cnf.root.mainloop()

except Exception:
    print(traceback.format_exc())

    import os
    appname = "MiuzCollections"
    cfg_dir = os.path.join(os.path.expanduser("~"),
                           "Library/Application Support", appname)

    with open(os.path.join(cnf.cfg_dir, "err.txt"), "a") as f:
        f.write("\n\n\n***\n\n\n" + traceback.format_exc())