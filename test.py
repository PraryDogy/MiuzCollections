import os
import threading
import time
from time import sleep

import sqlalchemy
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from cfg import cnf
from database import Dbase, ThumbsMd

from PIL import Image
from watchdog.observers.polling import PollingObserver


class Handler(FileSystemEventHandler):
    def on_created(self, event):
        print(event)

    def on_deleted(self, event):
        print(event)

    def on_moved(self, event):
        print(event)


class WatcherBase:
    observer = None

    def __init__(self):
        __class__.observer = PollingObserver()
        __class__.observer.schedule(Handler(), path="/Volumes/TEST", recursive=True)
        __class__.observer.start()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            __class__.observer.stop()
        __class__.observer.join()


class Watcher(WatcherBase):
    def __init__(self):
        t1 = threading.Thread(target=WatcherBase, daemon=True)
        t1.start()
