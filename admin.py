import os

import yadisk

import cfg
import database


def upload_db():
    """Uploads database file to yandex disk.
    """

    yandex = yadisk.YaDisk(token=cfg.YADISK_TOKEN)
    db_path = os.path.join(cfg.DB_DIR, cfg.DB_NAME)

    with open(db_path, "rb") as f:
        yandex.upload(f, os.path.join(cfg.YADISK_DIR, cfg.DB_NAME))


def print_alive(name_func='', what_print=''):
    """Prints output:
    function name, sometext.
    Needs for debug

    Args:
        name_func (str): class.__name__,
        what_print (str): text.
    """

    # print(name_func, what_print)
    return


def clear_db():
    """
    Just clears database, create new one and fills created tables.
    """

    database.Utils().create()
    database.Utils().fill_config()
