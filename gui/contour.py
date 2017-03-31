from PyQt5 import QtCore, QtWidgets, QtGui

# utility class to hold and access current image corner coordinates in a
class Contour(QtWidgets.QGraphicsPolygonItem):
    def __init__(self):
        super(Contour, self).__init__()

        # Create QPointF objects to hold corner coordinates
        self._topLeft = QtCore.QPointF()
        self._topRight = QtCore.QPointF()
        self._bottomRight = QtCore.QPointF()
        self._bottomLeft = QtCore.QPointF()

        # Create a polygon object that will change depending on the selected image
        self._polygon = QtGui.QPolygonF()

    def updatePolygon(self):
        self.eraseOldPolygon()
        self.createNewPolygon()

    def eraseOldPolygon(self):
        self._polygon = QtGui.QPolygonF() # TODO

    def createNewPolygon(self):
        self._polygon.append(self._topLeft)
        self._polygon.append(self._topRight)
        self._polygon.append(self._bottomRight)
        self._polygon.append(self._bottomLeft)
        self._polygon.append(self._topLeft) # Close the polygon

    def stylePolygon(self):
        pen = QtGui.QPen()
        pen.setColor(QtCore.Qt.red)
        pen.setWidth(2)