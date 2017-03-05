import sys
from PyQt5 import QtWidgets

from db.dbHelper import *
from gui.mainWindow import MainWindow
from observer import *
from gui.markerItem import MarkerItem


class Controller(Observer):
    def __init__(self):
        super(Controller, self).__init__()
        self.flights = get_all_flights()
        self.currentFlight = None
        self.tags = []
        self.images = []
        self.markers = []

        self.window = MainWindow()
        self.window.show()
        self.window.setupTab.addObserver(self)
        self.window.taggingTab.addObserver(self)

        # populate lists
        for flight in self.flights.values():
            self.window.setupTab.addFlightToUi(flight)


    def notify(self, event, id, data):
        if event is "FLIGHT_LOAD":
            self.loadFlight(id)
        elif event is "FLIGHT_CREATED":
            self.flights[id] = data
            self.loadFlight(id)
        elif event is "TAG_CREATED":
            self.tags.append(data)
        elif event is "TAG_DELETED":
            self.tags.remove(data)
            data.delete()
        elif event is "MARKER_CREATE":
            print "Marker Created:", data[1].text()
            self.addTaggingContextMenuItem(data)
        elif event is "TAG_EDITED":
            tag = self.tags[id]
            old_tag = tag

            tag.type = data.type
            tag.subtype = data.subtype
            tag.symbol = data.symbol
            tag.num_occurrences = data.num_occurrences
            tag.save()

            self.updateTaggingContextMenuItem(old_tag, tag)
        elif event is "MARKER_DELETED":
            print "Marker Deleted:", data.getParentTag().type, data.getParentTag().subtype

    def addTaggingContextMenuItem(self, tag):
        self.window.taggingTab.viewer_single.getPhotoItem().context_menu.addTagToContextMenu(tag)

    def updateTaggingContextMenuItem(self, old_tag, tag):
        self.window.taggingTab.viewer_single.getPhotoItem().context_menu.updateTagItem(old_tag, tag)

    def loadFlight(self, id):
        self.currentFlight = self.flights[id]
        self.loadTags()
        self.loadMap(self.currentFlight)
        self.window.taggingTab.currentFlight = self.currentFlight
        self.loadImages()

    def loadTags(self):
        self.tags = get_all_tags()
        for tag in self.tags:
            self.window.taggingTab.addTagToUi(tag)

    def deleteTaggingContextMenuItem(self, tag):
        self.window.taggingTab.viewer_single.getPhotoItem().context_menu.removeTagItem(tag)

    def deleteTagMarkers(self, tag):
        sceneObjects = self.window.taggingTab.viewer_single.getScene().items()
        for item in sceneObjects:
            if type(item) is MarkerItem:
                if item.getParentTag() is tag:
                    self.window.taggingTab.viewer_single.getScene().removeItem(item)
                    #TODO - Add DB integration here

    def loadMap(self, flight):
        self.window.taggingTab.minimap.setMinimap(flight)

    def loadImages(self):
        self.images = get_all_images_for_flight(self.currentFlight)
        for i in self.images:
            self.window.taggingTab.addImageToUi(i)


if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())