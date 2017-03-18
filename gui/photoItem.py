from PyQt5 import QtCore, QtGui, QtWidgets
from tagContextMenu import TagContextMenu
from observer import *


# The main reason for creating this sub-class is to be able to define a custom
# mousePressEvent for an image. We want to differentiate between a click on an
# image and on a marker in an image.
class PhotoItem(QtWidgets.QGraphicsPixmapItem, Observable):
    def __init__(self, parent=None):
        super(PhotoItem, self).__init__(parent)
        Observable.__init__(self)

        self.context_menu = TagContextMenu()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.ignore() # Need this to enable click-and-drag panning
        elif event.button() == QtCore.Qt.RightButton:
            current_action = self.context_menu.exec_(event.screenPos())
            for _tag, _action in self.context_menu.tag_action_tuples:
                if current_action == _action:
                    self.notifyObservers("MARKER_CREATE", None, [event, _tag])