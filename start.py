try:
    from cfg import cnf
    from gui import app

    cnf.root.mainloop()

except Exception:
    import traceback
    import os
    import subprocess

    print(traceback.format_exc())

    appname = "MiuzCollections"
    folderdir = (os.path.expanduser("~"), "Library", "Application Support", appname)
    folderdir = os.path.join(*folderdir)
    filedir = os.path.join(folderdir, "err.txt")

    os.makedirs(folderdir, exist_ok=True)

    with open(file=filedir, mode="a") as f:
        f.write("\n\n\n***\n\n\n" + traceback.format_exc())
    
    subprocess.Popen(args=["open", "-R", filedir])