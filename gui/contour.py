from PyQt5 import QtCore, QtWidgets, QtGui

# utility class to hold and access current image corner coordinates in a
class Contour(QtWidgets.QGraphicsPolygonItem):
    def __init__(self, parent):
        super(Contour, self).__init__(parent)

        # Create QPointF objects to hold corner coordinates
        self._topLeft = QtCore.QPointF()
        self._topRight = QtCore.QPointF()
        self._bottomRight = QtCore.QPointF()
        self._bottomLeft = QtCore.QPointF()

        # Create a polygon object that will change depending on the selected image
        self._polygon = QtGui.QPolygonF()

        # Set polygon style
        self.stylePolygon()

    def updatePolygon(self):
        self.eraseOldPolygon()
        self.createNewPolygon()

    def eraseOldPolygon(self):
        self._polygon.clear()

    def createNewPolygon(self):
        self._polygon.append(self._topLeft)
        self._polygon.append(self._topRight)
        self._polygon.append(self._bottomRight)
        self._polygon.append(self._bottomLeft)
        self._polygon.append(self._topLeft) # Close the polygon
        self.setPolygon(self._polygon)

    def stylePolygon(self):
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        pen.setWidth(2)
        self.setPen(pen)
