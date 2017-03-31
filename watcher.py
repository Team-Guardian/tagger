import ntpath
import time
import threading
import os
from observer import Observable as GuiObservable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.imageInfo import processNewImage, GetDirectoryAndFilenameFromFullPath

STOPPING_CONDITION_CHECK_INTERVAL = 500

class Watcher:
    def __init__(self):
        self.observer = Observer()
        self.event_handler = None
        self.image_watcher_thread = None
        self.event_handler = FileCreatedEventHandler(self.observer)
        self.stopCommand = False;

    def startWatching(self, flight, watched_dir):
        self.event_handler.startEventHandler(flight, watched_dir)
        self.observer.schedule(self.event_handler, watched_dir, recursive=False)
        self.observer.start()
        self.image_watcher_thread = threading.Thread(target=self.run, args=())
        self.image_watcher_thread.daemon = True
        self.image_watcher_thread.start()

    def stopAndReset(self):
        self.stopCommand = True
        if self.observer.is_alive():
            self.observer.stop()
            self.observer.join()
            self.observer = Observer()

    def run(self):
            while not self.stopCommand:
                time.sleep(STOPPING_CONDITION_CHECK_INTERVAL) # check for stopping condition twice per second


class FileCreatedEventHandler(FileSystemEventHandler, GuiObservable):
    def __init__(self, observer):
        super(FileSystemEventHandler, self).__init__()
        super(GuiObservable, self).__init__()
        self.observer = observer
        self.watched_dir = None
        self.flight = None

    def startEventHandler(self, flight, watched_dir):
        self.watched_dir = watched_dir
        self.flight = flight

    def changeTargetFlight(self, new_flight):
        self.flight = new_flight

    def on_created(self, event):
        path = event.src_path

        directory, fileName = GetDirectoryAndFilenameFromFullPath(path)

        if any(fileName.endswith(end) for end in ['.jpg', '.jpeg', '.JPG', '.JPEG']):
            i = processNewImage(path, self.flight)
            self.notifyObservers('IMAGE_ADDED', None, i)
