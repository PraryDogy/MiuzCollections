import os
import threading
import time

import sqlalchemy
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cfg import cnf
from database import Dbase, ThumbsMd

from .scaner import ScanerGlobs
from .system import CreateThumb, SysUtils

__all__ = ("Watcher", )


class WaitScaner:
    def __init__(self):
        while ScanerGlobs.thread.is_alive():
            cnf.root.update()


class ReloadGui:
    def __init__(self) -> None:
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


class NewFile(SysUtils):
    def __init__(self, src: str):
        thumb = CreateThumb(src=src).getvalue()
        size = int(os.path.getsize(filename=src))
        birth = int(os.stat(path=src).st_birthtime)
        mod = int(os.stat(path=src).st_mtime)

        q = (sqlalchemy.insert(ThumbsMd)
             .values({"img150": thumb,
                      "src": src,
                      "size": size,
                      "created": birth,
                      "modified": mod,
                      "collection": self.get_coll_name(src=src)}))

        Dbase.conn.execute(q)


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                NewFile(src=event.src_path.strip())
                print("done")
                cnf.root.after(ms=100, func=ReloadGui)

    def on_deleted(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                DeletedFile(src=event.src_path.strip())
                print("done")
                cnf.root.after(ms=100, func=ReloadGui)

    def on_moved(self, event):
        WaitScaner()
        if not event.is_directory:
            if event.src_path.endswith(Exts.lst):
                MovedFile(src=event.src_path.strip(),
                          dest=event.dest_path.strip())
                print("done")
                cnf.root.after(ms=100, func=ReloadGui)


class WatcherBase:
    def __init__(self):
        observer = Observer()
        observer.schedule(Handler(), path=cnf.coll_folder, recursive=True)
        observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            observer.stop()
        observer.join()


class Watcher:
    def __init__(self):
        WaitScaner()
        t1 = threading.Thread(target=WatcherBase, daemon=True)
        t1.start()
