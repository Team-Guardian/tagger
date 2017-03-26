import ntpath
import time
import threading
import os
from observer import Observable as GuiObservable
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from utils.imageInfo import createImageWithExif

class Watcher:
    def __init__(self):
        self.observer = Observer()
        self.event_handler = None
        self.image_watcher_thread = None
        self.event_handler = FileCreatedEventHandler(self.observer)
        self.isRunning = False

    def startWatching(self, flight, watched_dir):
        self.event_handler.startEventHandler(flight, watched_dir)
        self.observer.schedule(self.event_handler, watched_dir, recursive=False)
        self.observer.start()
        self.image_watcher_thread = threading.Thread(target=self.run, args=())
        self.image_watcher_thread.daemon = True
        self.image_watcher_thread.start()
        self.isRunning = True

    def run(self):
            while True:
                time.sleep(500) # check directory twice a second


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
        def _getFileNameFromFullPath(path):
            head, tail = ntpath.split(path)
            return tail

        fileName = _getFileNameFromFullPath(path)

        if any(fileName.endswith(end) for end in ['.jpg', '.jpeg', '.JPG', '.JPEG']):
            self.processImage(fileName)
            self.observer.unschedule_all()

    def processImage(self, img_filename):
        self.ensureFlightImageDirectoryExists()
        self.moveImageToFlightDirectory(self.watched_dir, './flights/{}'.format(self.flight.img_path), img_filename)
        i = createImageWithExif(self.createPathToImage(self.flight, img_filename), self.flight)
        self.notifyObservers('IMAGE_RECEIVED', None, i)

    def ensureFlightImageDirectoryExists(self):
        flight_directory = './flights/{}'.format(self.flight.img_path)
        if not os.path.exists(flight_directory):
            os.makedirs(flight_directory)

    def createPathToImage(self, flight, img_filename):
        return './flights/{}/{}'.format(flight.img_path, img_filename)

    def moveImageToFlightDirectory(self, from_dir, to_dir, img_filename):
        old_path = '{}/{}'.format(from_dir, img_filename)
        new_path = '{}/{}'.format(to_dir, img_filename)
        os.rename(old_path, new_path)