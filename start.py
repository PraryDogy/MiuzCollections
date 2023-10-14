try:
    import sys
    import traceback

    from cfg import cnf
    from gui import Application

    Application()
    cnf.root.mainloop()

except Exception as e:
    import os
    e_type, e_val, e_tb = sys.exc_info()

    APP_NAME = 'MiuzCollections'

    CFG_DIR = os.path.join(
        os.path.expanduser("~"),
       f"Library/Application Support/{APP_NAME}"
        )

    if not os.path.exists(CFG_DIR):
        os.mkdir(CFG_DIR)

    if not os.path.exists(os.path.join(CFG_DIR, 'err.txt')):
        with open(os.path.join(CFG_DIR, 'err.txt'), 'w') as err_file:
            pass

    with open(os.path.join(CFG_DIR, 'err.txt'), 'r') as err_file:
        data = err_file.read()

    data = f'{data}\n\n{traceback.format_exc()}'

    with open(os.path.join(CFG_DIR, 'err.txt'), 'w') as err_file:
        print(data, file=err_file)

    print(data)