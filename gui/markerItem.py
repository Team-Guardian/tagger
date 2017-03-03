from PyQt5 import QtCore, QtGui, QtWidgets
from observer import *


# This sub-class is used to display markers for targets.
class MarkerItem(QtWidgets.QGraphicsPixmapItem, Observable):
    def __init__(self, parent=None):
        super(MarkerItem, self).__init__(parent)
        Observable.__init__(self)

        self.context_menu = QtWidgets.QMenu()
        self.delete_marker_handle = self.context_menu.addAction("Delete Marker")

        pixMap = QtGui.QPixmap('gui/star_markers/blue.png') # Fixed for now
        pixMap = pixMap.scaledToWidth(150)
        self.setPixmap(pixMap)

    def notify(self, event, id, data):
        for observer in self.observers:
            observer.notify(event, id, data)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print "Left Button"
        elif event.button() == QtCore.Qt.RightButton:
            action = self.context_menu.exec_(QtCore.QPoint(event.screenPos().x(), event.screenPos().y()))
            if action == self.delete_marker_handle:
                self.notify("MARKER_DELETE", 0, self)