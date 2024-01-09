import os
import threading
import time
from time import sleep

import sqlalchemy
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cfg import cnf
from database import Dbase, ThumbsMd

from .scaner import ScanerGlobs
from .system import CreateThumb, SysUtils
from PIL import Image


__all__ = ("Watcher", )


class WatcherTask:
    task = False


class WaitScaner:
    def __init__(self):
        return
        while ScanerGlobs.thread.is_alive():
            cnf.root.update()


class WaitWriteFinish:
    value = 0.1

    def __init__(self, src: str):
        file = None

        while not file:
            try:
                file = Image.open(src)
                file.close()
            except Exception:
                file = None
                sleep(__class__.value)
                continue


class ReloadGui:
    task = False

    def __init__(self) -> None:
        if __class__.task:
            cnf.root.after_cancel(id=__class__.task)
        __class__.task = cnf.root.after(ms=2000, func=self.start)

    def start(self):
        cnf.reload_menu()
        cnf.reload_thumbs()


class Exts:
    lst = (".jpg", ".JPG", ".jpeg", ".JPEG", ".png", ".PNG")


class MovedFile:
    def __init__(self, src: str, dest: str) -> None:
        q = (sqlalchemy.update(ThumbsMd)
             .filter(ThumbsMd.src==src)
             .values({"src": dest}))
        Dbase.conn.execute(q)


class DeletedFile:
    def __init__(self, src: str):
        q = (sqlalchemy.delete(ThumbsMd)
             .filter(ThumbsMd.src==src))
        Dbase.conn.execute(q)


class DeleteDir:
    def __init__(self, src: str):
        q = (sqlalchemy.delete(ThumbsMd)
             .filter(ThumbsMd.src.like(f"%{src}%")))
        Dbase.conn.execute(q)


class NewFile(SysUtils):
    def __init__(self, src: str):
        q = (sqlalchemy.insert(ThumbsMd)
             .values({"img150": CreateThumb(src=src).getvalue(),
                      "src": src,
                      "size": int(os.path.getsize(filename=src)),
                      "created": int(os.stat(path=src).st_birthtime),
                      "modified": int(os.stat(path=src).st_mtime),
                      "collection": self.get_coll_name(src=src)}))

        Dbase.conn.execute(q)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                WaitWriteFinish(src=event.src_path)
                NewFile(src=event.src_path)
                ReloadGui()

    def on_deleted(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                DeletedFile(src=event.src_path)
                ReloadGui()
        else:
            DeleteDir(src=event.src_path)
            ReloadGui()

    def on_moved(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                MovedFile(src=event.src_path, dest=event.dest_path)
                ReloadGui()


class WatcherBase:
    observer = None

    def __init__(self):
        __class__.observer = Observer()
        __class__.observer.schedule(Handler(), path=cnf.coll_folder, recursive=True)
        __class__.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            __class__.observer.stop()
        __class__.observer.join()


class Watcher(WatcherBase, SysUtils):
    def __init__(self):
        if self.smb_check():
            WaitScaner()
            t1 = threading.Thread(target=WatcherBase, daemon=True)
            t1.start()
        else:
            if WatcherTask.task:
                cnf.root.after_cancel(WatcherTask.task)
            WatcherTask.task = cnf.root.after(ms=12000, func=__class__)