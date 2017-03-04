import sys
from PyQt5 import QtWidgets

from db.dbHelper import *
from gui.mainWindow import MainWindow
from observer import *


class Controller(Observer):
    def __init__(self):
        super(Controller, self).__init__()
        self.flights = get_all_flights()
        self.currentFlight = None
        self.tags = get_all_tags()
        self.images = []
        self.markers = []

        self.window = MainWindow()
        self.window.show()
        self.window.setupTab.addObserver(self)
        self.window.taggingTab.addObserver(self)

        # populate lists
        for flight in self.flights.values():
            self.window.setupTab.addFlightToUi(flight)

        for tag in self.tags:
            self.window.taggingTab.addTagToUi(tag)

    def notify(self, event, id, data):
        if event is "FLIGHT_LOAD":
            self.currentFlight = self.flights[id]
            self.loadMap(self.currentFlight)
        elif event is "FLIGHT_CREATED":
            self.flights[id] = data
        elif event is "TAG_CREATED":
            self.tags.append(data)
        elif event is "TAG_EDITED":
            tag = self.tags[id]
            tag.type = data.type
            tag.subtype = data.subtype
            tag.symbol = data.symbol
            tag.num_occurrences = data.num_occurrences
            tag.save()
        elif event is "TAG_DELETED":
            tag = self.tags.pop(id)
            tag.delete()

    def loadMap(self, flight):
        self.window.taggingTab.minimap.setMinimap(flight)

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())