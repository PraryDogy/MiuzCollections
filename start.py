try:
    import sys
    import traceback

    from cfg import cnf
    from gui import app

    cnf.root.mainloop()

except Exception as e:
    import os
    e_type, e_val, e_tb = sys.exc_info()

    cfg_dir = os.path.join(
        os.path.expanduser("~"),
       f"Library/Application Support/{'MiuzCollections'}"
        )

    file = os.path.join(cfg_dir, "err.txt")

    if not os.path.exists(cfg_dir):
        os.mkdir(cfg_dir)

    if not os.path.exists(file):
        with open(file, "w") as err_file:
            pass

    with open(file, "r") as err_file:
        data = err_file.read()

    data = f"{data}\n\n{traceback.format_exc()}"

    with open(file, "w") as err_file:
        print(data, file=err_file)

    print(data)