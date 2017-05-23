from PyQt5 import QtCore, QtGui, QtWidgets
from tagDialog import ICON_DIRECTORY
from db.models import Marker, Image

# This sub-class is used to display markers for targets.
class MarkerItem(QtWidgets.QGraphicsPixmapItem):

    def __init__(self, marker, current_image, initial_zoom, parent=None):
        super(MarkerItem, self).__init__(parent)

        self.marker = marker
        self.context_menu = QtWidgets.QMenu()
        self.delete_marker_handle = self.context_menu.addAction("Delete Marker")
        self.go_to_parent_image_handle = None

        # pseudo-slots because QGraphicsPixmapItem is not a QObject and does not have signals
        self.marker_deleted_handler = None
        self.marker_parent_image_change_handler = None

        if marker.image != current_image:
            self.go_to_parent_image_handle = self.context_menu.addAction("Go To Parent Image")

        pixMap = QtGui.QPixmap(ICON_DIRECTORY + marker.tag.symbol)

        initial_zoom_level = 1
        for index in range(initial_zoom):
            initial_zoom_level = initial_zoom_level * 0.8 # Look at photoViewer.py to see why 0.8

        pixMap = pixMap.scaledToWidth(0.035*current_image.width)
        self.setPixmap(pixMap)
        self.setScale(initial_zoom_level)

    def setMarkerDeletedHandler(self, handler_function):
        self.marker_deleted_handler = handler_function

    def setMarkerParentImageChangeHandler(self, handler_function):
        self.marker_parent_image_change_handler = handler_function

    def notify(self, event, id, data):
        if event is "SCENE_ZOOM" :
            self.setScale(self.scale()*data)
        elif event is "SCENE_RESET":
            self.setScale(1.0)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.RightButton:
            action = self.context_menu.exec_(event.screenPos())
            if action == self.delete_marker_handle:
                self.marker = self.getMarker()
                self.marker_deleted_handler(self)
            elif action == self.go_to_parent_image_handle:
                self.marker_parent_image_change_handler(self.marker.image)

    def getMarker(self):
        self.synchronizeWithDatabase()
        return self.marker

    def synchronizeWithDatabase(self):
        self.marker = Marker.objects.get(pk=self.marker.pk)
