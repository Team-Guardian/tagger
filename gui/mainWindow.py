# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QShortcut
from PyQt5.QtGui import QKeySequence

from gui.ui.ui_mainWindow import Ui_MainWindow
from mapTab import MapTab
from setupTab import SetupTab
from taggingTab import TaggingTab
from targetsTab import TargetsTab
from observer import *
from utils.geolocate import geolocateLatLonFromPixel

TAB_INDICES = {'TAB_SETUP': 0, 'TAB_TAGGING': 1, 'TAB_TARGETS': 2, 'TAB_MAP': 3}


class MainWindow(QtWidgets.QMainWindow, Observable):
    def __init__(self):
        super(MainWindow, self).__init__()
        Observable.__init__(self)

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.setupTab = SetupTab()
        self.ui.tabWidget.addTab(self.setupTab, "Setup")

        self.taggingTab = TaggingTab()
        self.taggingTab.addObserver(self)
        self.taggingTab.viewer_single.viewport().installEventFilter(self)
        self.ui.tabWidget.addTab(self.taggingTab, "Tagging")

        self.targetsTab = TargetsTab()
        self.ui.tabWidget.addTab(self.targetsTab, "Targets")

        self.mapTab = MapTab()
        self.mapTab.viewer_map.viewport().installEventFilter(self)
        self.ui.tabWidget.addTab(self.mapTab, "Map")

        # connect menu bar items to functions
        self.ui.actionReset.triggered.connect(self.resetGui)
        self.ui.actionSaveImage.triggered.connect(self.saveImage)
        self.ui.actionSaveImage.setShortcut(QKeySequence.Save)
        self.ui.actionSaveImage.setShortcutContext(QtCore.Qt.WidgetShortcut)
        self.ui.actionSaveImage.setDisabled(True)
        self.saveImageShortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        self.saveImageShortcut.activated.connect(self.saveImage)

        self.ui.tabWidget.currentChanged.connect(self.tabChangeHandler)

    def notify(self, event, id, data):
        if event is "CURRENT_IMG_CHANGED":
            self.ui.actionSaveImage.setEnabled(True)

    # handles events from widgets we have registered with
    # use installEventFilter() on a widget to register
    def eventFilter(self, source, event):
        if event.type() == QtCore.QEvent.MouseMove and event.buttons() == QtCore.Qt.NoButton:
            if source is self.taggingTab.viewer_single.viewport():
                if not self.taggingTab.viewer_single.isImageNull():
                    point = self.taggingTab.viewer_single.mapToScene(event.pos())
                    image = self.taggingTab.getCurrentImage()
                    site_elevation = self.taggingTab.getCurrentFlight().reference_altitude
                    if image:
                        lat, lon = geolocateLatLonFromPixel(image, site_elevation, point.x(), point.y())
                        self.ui.statusbar.showMessage(
                            'x: %4d, y: %4d, lat: %-3.6f, lon: %-3.6f, alt (MSL): %3.1f, alt (AGL): %3.1f, pitch: %2.3f, roll: %2.3f, yaw: %2.3f' % \
                            (round(point.x()), round(point.y()), lat, lon, image.altitude,
                             image.altitude - site_elevation, image.pitch, image.roll, image.yaw))
            elif source is self.mapTab.viewer_map.viewport():
                if not self.mapTab.viewer_map.isImageNull():
                    point = self.mapTab.viewer_map.mapToScene(event.pos())
                    image = self.mapTab.getCurrentImage()
                    lat, lon = self.mapTab.geolocatePoint(point.x(), point.y())
                    site_elevation = self.mapTab.getCurrentFlight().reference_altitude
                    self.ui.statusbar.showMessage('x: %4d, y: %4d, lat: %-3.6f, lon: %-3.6f' % \
                                          (round(point.x()), round(point.y()), lat, lon))

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

    def tabChangeHandler(self):
        currentTabIndex = self.ui.tabWidget.currentIndex()
        if currentTabIndex == TAB_INDICES['TAB_MAP']:
            self.mapTab.viewer_map.fitInView()
        if currentTabIndex != TAB_INDICES['TAB_TAGGING']:
            self.ui.actionSaveImage.setDisabled(True)
        else:
            if self.taggingTab.currentImage != None:
                self.ui.actionSaveImage.setEnabled(True)

    def resetGui(self):
        self.notifyObservers("RESET", None, None)

    def resetTabs(self):
        for tabIndex in range(self.ui.tabWidget.count()): # iterate over each tab
            currentTab = self.ui.tabWidget.widget(tabIndex)
            currentTab.resetTab()
        self.ui.tabWidget.setCurrentIndex(TAB_INDICES['TAB_SETUP'])

    def saveImage(self):
        if self.ui.tabWidget.currentIndex() == TAB_INDICES['TAB_TAGGING']:
            self.taggingTab.saveImage()
