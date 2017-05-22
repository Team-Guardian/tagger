import sys
from PyQt5 import QtWidgets, QtCore

from db.dbHelper import *
from gui.mainWindow import MainWindow, TAB_INDICES
from observer import *
from watcher import Watcher


class Controller(Observer):
    def __init__(self):
        super(Controller, self).__init__()
        self.flights = get_all_flights()
        self.currentFlight = None
        self.imageWatcher = Watcher()
        self.tags = []
        self.images = []

        self.window = MainWindow()
        self.window.addObserver(self)
        self.window.show()
        self.window.setupTab.addObserver(self)
        self.window.taggingTab.addObserver(self)
        self.imageWatcher.event_handler.addObserver(self)

        # populate lists
        for flight in self.flights.values():
            self.window.setupTab.addFlightToUi(flight)

        # connect signals
        # Main Window
        self.window.image_added_signal.connect(self.window.taggingTab.processNewImage)
        self.window.image_added_signal.connect(self.window.targetsTab.processNewImage)
        self.window.image_added_signal.connect(self.window.mapTab.processNewImage)
        self.window.reset_application_signal.connect(self.processReset)
        # from Setup Tab
        self.window.setupTab.flight_load_signal.connect(self.processFlightLoad)
        self.window.setupTab.flight_create_signal.connect(self.processFlightCreated)
        # from Tagging Tab

        # from Targets Tab

        # from Map Tab

    def notify(self, event, id, data):
        if event is "TAG_CREATED":
            self.tags.append(data)
        elif event is "TAG_DELETED":
            self.tags.remove(data)
            delete_tag(data) # This also deletes all the markers associated with this tag (Cascaded delete)
        elif event is "IMAGE_ADDED":
            new_image = data
            self.images.append(new_image)
            self.window.image_added_signal.emit(new_image)
            # self.window.taggingTab.addImageToUi(new_image)
            # self.window.targetsTab.addImageToUi(new_image)
            # self.window.mapTab.addImageToUi(new_image)

    @QtCore.pyqtSlot(str)
    def processFlightLoad(self, flight_id):
        self.resetWatcher()
        self.window.taggingTab.resetTab()
        self.window.targetsTab.resetTab()
        self.window.mapTab.resetTab()
        self.loadFlight(flight_id)

    @QtCore.pyqtSlot(str, Flight)
    def processFlightCreated(self, flight_id, flight):
        self.flights[flight_id] = flight
        self.window.setupTab.addFlightToUi(flight)
        self.loadFlight(flight_id)

    @QtCore.pyqtSlot(None)
    def processReset(self):
        self.resetWatcher()
        self.window.resetTabs()

    def loadFlight(self, id): # TODO: this function does more than the name implies
        self.currentFlight = self.flights[id]
        self.imageWatcher.startWatching(self.currentFlight, self.window.setupTab.line_watchDirectory.text())
        self.loadTags()
        self.loadMap(self.currentFlight)
        self.window.taggingTab.currentFlight = self.currentFlight
        self.window.mapTab.currentFlight = self.currentFlight
        self.window.targetsTab.current_flight = self.currentFlight
        self.window.targetsTab.setContextMenu()
        self.window.ui.tabWidget.setCurrentIndex(TAB_INDICES['TAB_TAGGING'])
        self.loadImages() # Keep this sequentially after the setCurrentTab call. This is a workaround for a \
                          # Qt bug: https://goo.gl/gWXA9Q

    def loadTags(self):
        self.tags = get_all_tags()
        for tag in self.tags:
            self.window.targetsTab.addTagToUi(tag)
            self.window.taggingTab.addTagToUi(tag)

    def loadMap(self, flight):
        self.window.taggingTab.minimap.setMinimap(flight)
        self.window.mapTab.setMap(flight)

    def loadImages(self):
        self.images = get_all_images_for_flight(self.currentFlight)
        for i in self.images:
            self.window.taggingTab.addImageToUi(i)
            self.window.targetsTab.addImageToUi(i)
            self.window.mapTab.addImageToUi(i)

    def resetWatcher(self):
        self.imageWatcher.stopAndReset()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())