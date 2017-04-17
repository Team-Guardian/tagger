from PyQt5 import QtCore, QtWidgets, QtGui

# utility class to hold and access current image corner coordinates in pixel frame
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
        self.setPolygonStyle()

    def updatePolygon(self):
        self.deleteOldPointsFromPolygon()
        self.addNewPointsToPolygon()

    def deleteOldPointsFromPolygon(self):
        self._polygon.clear()

    def addNewPointsToPolygon(self):
        self._polygon.append(self._topLeft)
        self._polygon.append(self._topRight)
        self._polygon.append(self._bottomRight)
        self._polygon.append(self._bottomLeft)
        self._polygon.append(self._topLeft) # Close the polygon
        self.setPolygon(self._polygon)

    def setPolygonStyle(self):
        # Configure pen
        contour_pen = QtGui.QPen()
        contour_pen.setColor(QtCore.Qt.red)
        contour_pen.setWidth(2)
        self.setPen(contour_pen)

        # Configure brush
        contour_brush = QtGui.QBrush()
        contour_brush.setColor(QtCore.Qt.red)
        contour_brush.setStyle(QtCore.Qt.Dense3Pattern)
        self.setBrush(contour_brush)

    def highlightPolygon(self):
        current_pen = self.pen()
        current_brush = self.brush()
        current_brush.setColor(QtCore.Qt.darkGreen)
        current_pen.setColor(QtCore.Qt.darkGreen)
        self.setBrush(current_brush)
        self.setPen(current_pen)

    def removePolygonHighlight(self):
        current_pen = self.pen()
        current_brush = self.brush()
        current_brush.setColor(QtCore.Qt.red)
        current_pen.setColor(QtCore.Qt.red)
        self.setBrush(current_brush)
        self.setPen(current_pen)

    def clearPolygonPoints(self):
        self._topLeft = QtCore.QPointF()
        self._topRight = QtCore.QPointF()
        self._bottomRight = QtCore.QPointF()
        self._bottomLeft = QtCore.QPointF()

    def reset(self):
        self.clearPolygonPoints()
        self.deleteOldPointsFromPolygon()
