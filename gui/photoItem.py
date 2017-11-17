from PyQt5 import QtCore, QtWidgets
from observer import *

TAB_INDICES = {'TAB_SETUP': 0, 'TAB_TAGGING': 1, 'TAB_TARGETS': 2, 'TAB_MAP': 3}

# The main reason for creating this sub-class is to be able to define a custom
# mousePressEvent for an image. We want to differentiate between a click on an
# image and on a marker in an image.
class PhotoItem(QtWidgets.QGraphicsPixmapItem, Observable):
    def __init__(self, parent=None):
        super(PhotoItem, self).__init__(parent)
        Observable.__init__(self)

        self.tab_context_menu = None

    def setTabContextMenu(self, context_menu):
        self.tab_context_menu = context_menu

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            event.ignore() # Need this to enable click-and-drag panning
        elif event.button() == QtCore.Qt.RightButton:
            if self.tab_context_menu is not None:
                current_action = self.tab_context_menu.exec_(event.screenPos())
                self.tab_context_menu.pixel_x_invocation_coord = event.pos().x()
                self.tab_context_menu.pixel_y_invocation_coord = event.pos().y()
                if current_action is not None:
                    message = self.tab_context_menu.action_message_dict.get(current_action)
                    data = self.tab_context_menu.action_data_dict.get(current_action)
                    self.notifyObservers(message, None, data)
            else:
                print 'Error: photoItem.py. Context menu is not set'
