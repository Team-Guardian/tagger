from PyQt5 import QtCore, QtGui, QtWidgets
from tagContextMenu import TagContextMenu


class PhotoItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(PhotoItem, self).__init__(parent)

        self.context_menu = TagContextMenu()

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print "Left Button"
        elif event.button() == QtCore.Qt.RightButton:
            current_action = self.context_menu.exec_(QtCore.QPoint(event.screenPos().x(), event.screenPos().y()))
            for action in self.context_menu.actions():
                if current_action == action:
                    scenePoint = event.scenePos()
                    print action.text(), round(scenePoint.x()), round(scenePoint.y()) # For debugging