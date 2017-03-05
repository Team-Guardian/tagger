from PyQt5 import QtCore, QtGui, QtWidgets
from observer import *


# This sub-class is used to display markers for targets.
class MarkerItem(QtWidgets.QGraphicsPixmapItem, Observable):
    def __init__(self, marker, image_width, initial_zoom, parent=None):
        super(MarkerItem, self).__init__(parent)
        Observable.__init__(self)

        self.marker = marker
        self.context_menu = QtWidgets.QMenu()
        self.delete_marker_handle = self.context_menu.addAction("Delete Marker")

        pixMap = QtGui.QPixmap('gui/star_markers/magenta.png') # Fixed for now

        initial_zoom_level = 1
        for index in range(initial_zoom):
            initial_zoom_level = initial_zoom_level * 0.8

        pixMap = pixMap.scaledToWidth(0.025*image_width)
        self.setPixmap(pixMap)
        self.setScale(initial_zoom_level)

    def notify(self, event, id, data):
        if event is "SCENE_ZOOM" :
            self.setScale(self.scale()*data)
        elif event is "SCENE_RESET":
            self.setScale(1.0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            action = self.context_menu.exec_(QtCore.QPoint(event.screenPos().x(), event.screenPos().y()))
            if action == self.delete_marker_handle:
                self.notifyObservers("MARKER_DELETED", None, self)

    def getMarker(self):
        return self.marker
