from PyQt5 import QtCore, QtGui, QtWidgets


class MarkerItem(QtWidgets.QGraphicsPixmapItem):
    def __init__(self, parent=None):
        super(MarkerItem, self).__init__(parent)

        self.observers = []
        self.context_menu = QtWidgets.QMenu()
        self.delete_marker_handle = self.context_menu.addAction("Delete Marker")

        pixMap = QtGui.QPixmap('/home/siddhant/team-guardian/tagger/gui/star_markers/blue.png') # Fixed for now
        pixMap = pixMap.scaledToWidth(150)
        self.setPixmap(pixMap)

    def addObserver(self, observer):
        self.observers.append(observer)

    def notify(self, event, id, data):
        for observer in self.observers:
            observer.notify(event, id, data)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print "Left Button"
        elif event.button() == QtCore.Qt.RightButton:
            action = self.context_menu.exec_(QtCore.QPoint(event.screenPos().x(), event.screenPos().y()))
            event_name = "MARKER_CONTEXT_MENU_TRIGGERED"
            if action == self.delete_marker_handle:
                event_name = "MARKER_DELETE"
            self.notify(event_name, 0, self)