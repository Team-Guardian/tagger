from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QDate
from ui.ui_setupTab import Ui_SetupTab
from observer import Observable
from db.dbHelper import *


class SetupTab(QtWidgets.QWidget, Ui_SetupTab, Observable):
    def __init__(self):
        super(SetupTab, self).__init__()
        Observable.__init__(self)

        self.setupUi(self)
        self.connectButtons()
        self.edit_flightDate.setDate(QDate.currentDate())

    def connectButtons(self):
        self.button_loadFlight.clicked.connect(self.loadFlight)
        self.button_createFlight.clicked.connect(self.createFlight)

    def addFlightToUi(self, flight):
        self.combo_flights.addItem(flight.location + " " + str(flight.date))

    def loadFlight(self):
        self.notifyObservers("FLIGHT_LOAD", self.combo_flights.currentText(), None)

    def createFlight(self):
        location = self.line_locationName.text()
        elevation = float(self.line_siteElevation.text())
        date = self.edit_flightDate.text()
        f = create_flight(location, elevation, "default.xml", date)
        self.notifyObservers("FLIGHT_CREATED", f.location + " " + str(f.date), f)
