# Man pages references: http://doc.qt.io/qt-4.8/qfiledialog.html#getOpenFileName

from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QDate
from ui.ui_setupTab import Ui_SetupTab
from observer import Observable
from utils.imageInfo import *
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
        self.button_selectAreaMap.clicked.connect(self.selectAreaMap)
        self.button_browseWatchDirectory.clicked.connect(self.selectWatchDirectory)

    def addFlightToUi(self, flight):
        self.combo_flights.addItem(flight.location + " " + str(flight.date))

    def loadFlight(self):
        self.notifyObservers("FLIGHT_LOAD", self.combo_flights.currentText(), None)

    def createFlight(self):
        location = self.line_locationName.text()
        elevation = float(self.line_siteElevation.text())
        date = self.edit_flightDate.text()
        area_map = self.line_areaMap.text()

        if AreaMap.objects.filter(name=area_map).exists():
            am = AreaMap.objects.filter(name=area_map).last()
        else:
            ul_lat, ul_lon, lr_lat, lr_lon = loadGeotiff('./area_maps/area_map')
            am = create_areamap(area_map, area_map + '.png', ul_lat, ul_lon, lr_lat, lr_lon)

        f = create_flight(location, elevation, "default.xml", date, am)
        self.notifyObservers("FLIGHT_CREATED", f.img_path, f)

    def selectAreaMap(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Select Area Map to Load", "./area_maps", "Images (*.png)")
        file_info = QtCore.QFileInfo(filepath[0])
        filename = file_info.baseName()
        self.line_areaMap.setText(filename)

    def selectWatchDirectory(self):
        filepath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory to Watch", "../vision-system/")
        self.line_watchDirectory.setText(filepath)