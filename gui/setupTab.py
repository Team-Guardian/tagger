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
        self.button_selectIntrinsicMatrix.clicked.connect(self.selectIntrinsicMatrix)

    def addFlightToUi(self, flight):
        self.combo_flights.addItem(flight.location + " " + str(flight.date))

    def loadFlight(self):
        self.notifyObservers("FLIGHT_LOAD", self.combo_flights.currentText(), None)

    def createFlight(self):
        location = self.line_locationName.text()
        elevation = float(self.line_siteElevation.text())
        date = self.edit_flightDate.text()
        area_map = self.line_areaMap.text()
        intrinsic_matrix = self.line_IntrinsicMatrix.text()

        if AreaMap.objects.filter(name=area_map).exists():
            am = AreaMap.objects.filter(name=area_map).last()
        else:
            corners_geo = loadGeotiff('./area_maps/' + area_map)
            am = create_areamap(area_map, area_map + '.png', corners_geo[0][1], corners_geo[0][0],
                                                             corners_geo[1][1], corners_geo[1][0],
                                                             corners_geo[2][1], corners_geo[2][0],
                                                             corners_geo[3][1], corners_geo[3][0])

        f = create_flight(location, elevation, intrinsic_matrix + '.xml', date, am)
        self.notifyObservers("FLIGHT_CREATED", f.img_path, f)

    def selectAreaMap(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Select Area Map to Load", "./area_maps",
                                                         "Images (*.png)")
        file_info = QtCore.QFileInfo(filepath[0])
        filename = file_info.baseName()
        self.line_areaMap.setText(filename)

    def selectIntrinsicMatrix(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Select Intrinsic Matrix to Load", "./intrinsic_matrices",
                                                         "XML Files (*.xml)")
        file_info = QtCore.QFileInfo(filepath[0])
        filename = file_info.baseName()
        self.line_IntrinsicMatrix.setText(filename)

    def resetTab(self):
        pass