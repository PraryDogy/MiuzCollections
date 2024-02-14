import os
import threading
import time
from time import sleep

import sqlalchemy
from PIL import Image, UnidentifiedImageError
from watchdog.events import FileSystemEventHandler
from watchdog.observers.polling import PollingObserver

from cfg import cnf
from database import Dbase, ThumbsMd

from .system import CreateThumb, SysUtils, UndefinedThumb

__all__ = ("Watcher", )


class WatcherManager:
    task = False
    watchdog_wait_time = 10
    img_wait_time = 5
    img_timeout = 300


class WaitWriteFinish:

    def __init__(self, src: str):
        file = None
        current_timeout = 0

        while not file:
            try:
                file = Image.open(src)
                file.close()
                current_timeout = 0

            except Exception:
                file = None
                sleep(WatcherManager.img_wait_time)
                current_timeout += 1

                if current_timeout == WatcherManager.img_timeout:
                    return
                else:
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
        try:
            data = {"img150": CreateThumb(src=src).getvalue(),
                    "src": src,
                    "size": int(os.path.getsize(filename=src)),
                    "created": int(os.stat(path=src).st_birthtime),
                    "modified": int(os.stat(path=src).st_mtime),
                    "collection": self.get_coll_name(src=src)}

        except (UnidentifiedImageError, FileNotFoundError):
            data = {"img150": UndefinedThumb().getvalue(),
                    "src": src,
                    "size": 66666,
                    "created": 66666,
                    "modified": 66666,
                    "collection": str(66666)}

        q = (sqlalchemy.insert(ThumbsMd).values(data))
        Dbase.conn.execute(q)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                WaitWriteFinish(src=event.src_path)
                NewFile(src=event.src_path)
                ReloadGui()

    def on_deleted(self, event):
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                DeletedFile(src=event.src_path)
                ReloadGui()

    def on_moved(self, event):
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                MovedFile(src=event.src_path, dest=event.dest_path)
                ReloadGui()


class WatcherBase:
    observer = None

    def __init__(self):
        __class__.observer = PollingObserver()
        __class__.observer.schedule(Handler(), path=cnf.coll_folder,
                                    recursive=True)
        __class__.observer.start()

        try:
            while True:
                time.sleep(WatcherManager.watchdog_wait_time)
        except KeyboardInterrupt:
            __class__.observer.stop()
        __class__.observer.join()


class Watcher(WatcherBase, SysUtils):
    def __init__(self):
        if WatcherManager.task:
            cnf.root.after_cancel(WatcherManager.task)

        if self.smb_check():
            t1 = threading.Thread(target=WatcherBase, daemon=True)
            t1.start()
            WatcherManager.task = cnf.root.after(ms=900000, func=__class__)
        else:
            WatcherManager.task = cnf.root.after(ms=15000, func=__class__)
