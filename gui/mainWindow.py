# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

from PyQt5 import QtWidgets, QtCore

from gui.ui.ui_mainWindow import Ui_MainWindow
from mapTab import MapTab
from setupTab import SetupTab
from taggingTab import TaggingTab
from targetsTab import TargetsTab


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        self.observers = []

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
        self.ui.tabWidget.addTab(self.mapTab, "Map")

    def addObserver(self, observer):
        self.observers.append(observer)

    def notify(self, event, id, data):
        for observer in self.observers:
            observer.notify(event, id, data)

    # handles events from widgets we have registered with
    # use installEventFilter() on a widget to register
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and
                source is self.taggingTab.viewer_single.viewport()):
            if event.buttons() == QtCore.Qt.NoButton:
                if not self.taggingTab.viewer_single.isImageNull():
                    point = self.taggingTab.viewer_single.mapToScene(event.pos())
                    self.ui.statusbar.showMessage('x: %d, y: %d' % (round(point.x()), round(point.y())))

        return QtWidgets.QWidget.eventFilter(self, source, event)

    def resizeEvent(self, resizeEvent):
        openedTab = self.ui.tabWidget.currentWidget()
        currentPhotoViewer = openedTab.findChild(QtWidgets.QGraphicsView)

        # if no PhotoViewers exist in current tab, do nothing
        if currentPhotoViewer is None:
            pass
        else:
            currentPhotoViewer.fitInView()
