# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

from PyQt5 import QtWidgets, QtCore

from gui.ui.ui_mainWindow import Ui_MainWindow
from mapTab import MapTab
from setupTab import SetupTab
from taggingTab import TaggingTab
from targetsTab import TargetsTab
from observer import *
from utils.geolocate import geolocateLatLonFromPixel


class MainWindow(QtWidgets.QMainWindow, Observable):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setupTab = SetupTab()
        self.ui.tabWidget.addTab(self.setupTab, "Setup")


        self.taggingTab = TaggingTab()
        self.taggingTab.viewer_single.viewport().installEventFilter(self)
        self.ui.tabWidget.addTab(self.taggingTab, "Tagging")

        self.targetsTab = TargetsTab()
        self.ui.tabWidget.addTab(self.targetsTab, "Targets")

        self.mapTab = MapTab()
        self.ui.tabWidget.addTab(self.mapTab, "Map")

        # connect menu bar items to functions
        self.ui.actionReset.triggered.connect(self.resetGui)

    # handles events from widgets we have registered with
    # use installEventFilter() on a widget to register
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and
                source is self.taggingTab.viewer_single.viewport()):
            if event.buttons() == QtCore.Qt.NoButton:
                if not self.taggingTab.viewer_single.isImageNull():
                    point = self.taggingTab.viewer_single.mapToScene(event.pos())
                    image = self.taggingTab.getCurrentImage()
                    site_elevation = self.taggingTab.getCurrentFlight().reference_altitude
                    lat, lon = geolocateLatLonFromPixel(image, site_elevation, point.y(), point.x())
                    self.ui.statusbar.showMessage('x: %4d, y: %4d, lat: %-3.6f, lon: %-3.6f, alt (MSL): %3.1f, alt (AGL): %3.1f, pitch: %2.3f, roll: %2.3f, yaw: %2.3f' % \
                                                  (round(point.x()), round(point.y()), lat, lon, image.altitude, image.altitude - site_elevation, image.pitch, image.roll, image.yaw))

        return QtWidgets.QWidget.eventFilter(self, source, event)

    def resizeEvent(self, resizeEvent):
        openedTab = self.ui.tabWidget.currentWidget()
        imageViewers = openedTab.findChildren(QtWidgets.QGraphicsView)
    
        # if no PhotoViewers exist in current tab, do nothing
        if imageViewers == None:
            pass
        else:
            for imgViewer in imageViewers:
                imgViewer.fitInView()

    def resetGui(self):
        for tabIndex in range(self.ui.tabWidget.count()): # iterate over each tab
            currentTab = self.ui.tabWidget.widget(tabIndex)
            currentTab.resetTab()