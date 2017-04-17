from PyQt5 import QtCore, QtWidgets
from tagContextMenu import TagContextMenu
from mapContextMenu import MapContextMenu
from observer import *

TAB_INDICES = {'TAB_SETUP': 0, 'TAB_TAGGING': 1, 'TAB_TARGETS': 2, 'TAB_MAP': 3}

# The main reason for creating this sub-class is to be able to define a custom
# mousePressEvent for an image. We want to differentiate between a click on an
# image and on a marker in an image.
class PhotoItem(QtWidgets.QGraphicsPixmapItem, Observable):
    def __init__(self, parent=None):
        super(PhotoItem, self).__init__(parent)
        Observable.__init__(self)

        self.tag_context_menu = TagContextMenu()
        self.map_context_menu = MapContextMenu()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.ignore() # Need this to enable click-and-drag panning
        elif event.button() == QtCore.Qt.RightButton:
            current_tab_index = QtWidgets.QApplication.activeWindow().ui.tabWidget.currentIndex()
            if current_tab_index == TAB_INDICES['TAB_TAGGING']:
                current_action = self.tag_context_menu.exec_(event.screenPos())
                for _tag, _action in self.tag_context_menu.tag_action_tuples:
                    if current_action == _action:
                        self.notifyObservers("MARKER_CREATE", None, [event, _tag])
            elif current_tab_index == TAB_INDICES['TAB_MAP']:
                current_action = self.map_context_menu.exec_(event.screenPos())
                self.map_context_menu.pixel_x_invocation_coord = event.screenPos().x()
                self.map_context_menu.pixel_y_invocation_coord = event.screenPos().y()
                message = self.map_context_menu.map_action_dict[current_action]
                self.notifyObservers(message, None, None)