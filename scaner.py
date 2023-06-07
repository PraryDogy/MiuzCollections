import os
import threading

import sqlalchemy

from cfg import conf
from database import Dbase, Thumbs
from utils import encode_image, get_coll_name, smb_check


__all__ = (
    "scaner",
    "auto_scan",
    "cancel_scan",
    )

UPDATE_THUMBNAILS = False


def change_live_lvl(text):
    conf.live_text = text


def st_bar_btn(text: str, color: str):
    from gui.st_bar import StBar
    btn = StBar.btn_change()
    btn.configure(text=text, bg=color)
    return


def update_collections():
    global UPDATE_THUMBNAILS

    change_live_lvl(conf.lang.scaner_prepare)

    db_images = Dbase.conn.execute(
        sqlalchemy.select(
        Thumbs.src, Thumbs.size, Thumbs.created, Thumbs.modified
        )
        ).fetchall()

    exts = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")

    collections = [
        os.path.join(conf.coll_folder, i)
        for i in os.listdir(conf.coll_folder)
        if not i.startswith((".", "_"))
        ]

    ln = len(collections)

    new_images = []
    found_images = []

    for x, collection in enumerate(collections, 1):
        change_live_lvl(
            f"{conf.lang.live_scan} {x} {conf.lang.live_from} {ln} {conf.lang.live_collections}."
            )

        for root, dirs, files in os.walk(collection):

            if not conf.flag:
                return

            for file in files:

                if not conf.flag:
                    return

                if file.endswith(exts):
                    src = os.path.join(root, file)
                    data = (
                        src,
                        int(os.path.getsize(src)),
                        int(os.stat(src).st_birthtime),
                        int(os.stat(src).st_mtime)
                        )
                    found_images.append(data)

                    if data not in db_images:
                        new_images.append(data)

    if new_images:
        UPDATE_THUMBNAILS = True
        ln = len(new_images)

        values = [
            {
            "b_img150": encode_image(src),
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            "b_collection": get_coll_name(src),
            "temp": change_live_lvl(
                f"{conf.lang.live_added} {x} {conf.lang.live_from} {ln} {conf.lang.live_newphoto}."
                )
                }
            for x, (src, size, created, modified) in enumerate(new_images, 1)
            if conf.flag
            ]

        limit = 300
        values = [
            values[i:i+limit]
            for i in range(0, len(values), limit)
            ]

        for vals in values:
            
            if not conf.flag:
                return

            q = sqlalchemy.insert(Thumbs).values(
                {
                    "img150": sqlalchemy.bindparam("b_img150"),
                    "src": sqlalchemy.bindparam("b_src"),
                    "size": sqlalchemy.bindparam("b_size"),
                    "created": sqlalchemy.bindparam("b_created"),
                    "modified": sqlalchemy.bindparam("b_modified"),
                    "collection": sqlalchemy.bindparam("b_collection")
                    })
            Dbase.conn.execute(q, vals)

    remove_images = []

    for src, size, created, modified in db_images:
        if not conf.flag:
            return

        if (src, size, created, modified) not in found_images:
            remove_images.append((src, size, created, modified))

    if remove_images:

        change_live_lvl(conf.lang.live_finish)
        UPDATE_THUMBNAILS = True

        values = [
            {
            "b_src": src,
            "b_size": size,
            "b_created": created,
            "b_modified": modified,
            }
            for src, size, created, modified in remove_images
            if conf.flag
            ]

        limit = 300
        values = [
            values[i:i+limit]
            for i in range(0, len(values), limit)
            ]

        for vals in values:

            if not conf.flag:
                return

            q = sqlalchemy.delete(Thumbs).filter(
                Thumbs.src == sqlalchemy.bindparam("b_src"),
                Thumbs.size == sqlalchemy.bindparam("b_size"),
                Thumbs.created == sqlalchemy.bindparam("b_created"),
                Thumbs.modified == sqlalchemy.bindparam("b_modified")
                )
            Dbase.conn.execute(q, vals)


def scaner():
    global UPDATE_THUMBNAILS

    conf.flag = True
    st_bar_btn(conf.lang.live_updating, conf.sel_color)

    conf.scaner_task = threading.Thread(target=update_collections, daemon=True)
    conf.scaner_task.start()

    while conf.scaner_task.is_alive():
        conf.root.update()

    conf.live_text = ""

    if UPDATE_THUMBNAILS:
        from gui.thumbnails import Thumbnails
        from gui.menu import Menu
        Thumbnails.reload_without_scroll()
        Menu.reload_menu()
        UPDATE_THUMBNAILS = False

    conf.flag = False
    st_bar_btn(conf.lang.upd_btn, conf.btn_color)


def cancel_scan():
    conf.flag = False
    if conf.scaner_task:
        while conf.scaner_task.is_alive():
            conf.root.update()
    return True


def auto_scan():
    cancel_scan()
    if smb_check():
        scaner()
    ms = conf.autoscan_time*60000
    conf.root.after(ms, auto_scan)
