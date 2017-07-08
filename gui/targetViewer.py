# StackOverflow for the win! http://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview

from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np

class TargetViewer(QtWidgets.QGraphicsView):

    orientation_defined_signal = QtCore.pyqtSignal(float)

    def __init__(self, parent):
        super(TargetViewer, self).__init__(parent)
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = QtWidgets.QGraphicsPixmapItem()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self.is_orientation_drawing_in_progress = False
        self.relative_orientation = None

        # Configure ellipse pen
        self.ellipse_pen = QtGui.QPen()
        self.ellipse_pen.setColor(QtCore.Qt.red)
        self.ellipse_pen.setWidth(3)

        # Configure arc pen
        self.arc_pen = QtGui.QPen()
        self.arc_pen.setColor(QtCore.Qt.black)
        self.arc_pen.setWidth(3)

        # Configure ellipse brush
        self.brush = QtGui.QBrush()
        self.brush.setColor(QtCore.Qt.red)
        self.brush.setStyle(QtCore.Qt.NoBrush)

        # Configure line pen
        self.line_pen = QtGui.QPen()
        self.line_pen.setColor(QtCore.Qt.black)
        self.line_pen.setWidth(3)

        # Scaling factor for proportionally sizing Qt elements based on the pixel size of the pixmap
        self.scaling_factor = 1

    def fitInView(self):
        rect = QtCore.QRectF(self._photo.pixmap().rect())
        if not rect.isNull():
            unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
            self.scale(1 / unity.width(), 1 / unity.height())
            viewrect = self.viewport().rect()
            scenerect = self.transform().mapRect(rect)
            factor = min(viewrect.width() / scenerect.width(),
                         viewrect.height() / scenerect.height())
            self.scale(factor, factor)

    def setPhoto(self, pixmap=None):
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    # Absorb wheel event
    def wheelEvent(self, QWheelEvent):
        QWheelEvent.accept()

    def viewportEvent(self, QEvent):
        if QEvent.type() == QtCore.QEvent.MouseButtonPress and QEvent.buttons() == QtCore.Qt.LeftButton and self.is_orientation_drawing_in_progress:
            self.startDrawing(QEvent.pos())
            self.drawing_started = True
        elif QEvent.type() == QtCore.QEvent.MouseMove and QEvent.buttons() == QtCore.Qt.LeftButton and self.is_orientation_drawing_in_progress and self.drawing_started:
            self.updateOrientation(QEvent.pos())
        elif QEvent.type() == QtCore.QEvent.MouseButtonRelease and self.is_orientation_drawing_in_progress:
            self.is_orientation_drawing_in_progress = False
            self.drawing_started = False
            self.submitOrientation(QEvent.pos())

        return QtWidgets.QGraphicsView.viewportEvent(self, QEvent)

    def startDrawing(self, event_position):
        # find the scaling factors to correctly size the elements
        width_scaling_factor = self._scene.sceneRect().width() / self.viewport().rect().width()
        height_scaling_factor = self._scene.sceneRect().height() / self.viewport().rect().height()
        self.scaling_factor = width_scaling_factor if (width_scaling_factor > height_scaling_factor) else height_scaling_factor

        # adjust pen thickness for better visibility
        self.line_pen.setWidth(3*self.scaling_factor)
        self.ellipse_pen.setWidth(3*self.scaling_factor)
        self.arc_pen.setWidth(3*self.scaling_factor)

        # Draw center and cursor ellipses
        viewport_center = self.mapToScene(self.viewport().rect().center())
        center_ellipse_bounding_rect = QtCore.QRectF(viewport_center.x()-10*self.scaling_factor,
                                                     viewport_center.y()-10*self.scaling_factor,
                                                     20*self.scaling_factor, 20*self.scaling_factor)

        event_position_center = self.mapToScene(event_position)
        cursor_ellipse_bounding_rect = QtCore.QRectF(event_position_center.x()-10*self.scaling_factor,
                                                     event_position_center.y()-10*self.scaling_factor,
                                                     20*self.scaling_factor, 20*self.scaling_factor)

        self.center_ellipse = self._scene.addEllipse(center_ellipse_bounding_rect, self.ellipse_pen, self.brush)
        self.cursor_ellipse= self._scene.addEllipse(cursor_ellipse_bounding_rect, self.ellipse_pen, self.brush)

        # Draw vertical reference and cursor lines
        self.vertical_reference_line = self._scene.addLine(viewport_center.x(), 0, viewport_center.x(), viewport_center.y()*2, self.line_pen)
        self.cursor_line = self._scene.addLine(viewport_center.x(), viewport_center.y(), event_position_center.x(), event_position_center.y(), self.line_pen)

        # Draw angle between reference and cursor lines
        arc_ellipse_bounding_rect = QtCore.QRectF(viewport_center.x() - 40*self.scaling_factor,
                                                  viewport_center.y() - 40*self.scaling_factor,
                                                  80*self.scaling_factor, 80*self.scaling_factor)
        self.angle_arc = QtWidgets.QGraphicsEllipseItem(arc_ellipse_bounding_rect)
        self.angle_arc.setStartAngle(90*16)
        top_middle_point = (viewport_center.x(), 0)
        center_point = (viewport_center.x(), viewport_center.y())
        cursor_point = (event_position_center.x(), event_position_center.y())
        self.arc_span_angle = self.angleBetween(top_middle_point, center_point, cursor_point)
        self.angle_arc.setSpanAngle(-16 * self.arc_span_angle)

        # Style the arc and add item to the scene for it to show
        self.angle_arc.setPen(self.arc_pen)
        self._scene.addItem(self.angle_arc)

        # Add angle text
        # text box to show distance that scale represents
        self.distance_text_box = QtWidgets.QGraphicsTextItem()
        text_font = QtGui.QFont()
        text_font.setPointSize(25*self.scaling_factor)
        self.distance_text_box.setDefaultTextColor(QtCore.Qt.red)
        self.distance_text_box.setFont(text_font)
        self.distance_text_box.setPos(viewport_center.x()+50*self.scaling_factor, viewport_center.y()-50*self.scaling_factor)
        self.distance_text_box.setHtml('{:7.2f} deg'.format(round(-(self.arc_span_angle/16), 2)))
        self._scene.addItem(self.distance_text_box)


    def updateOrientation(self, event_position):
        self.deleteDynamicElementsFromScene()

        viewport_center = self.mapToScene(self.viewport().rect().center())
        event_position_center = self.mapToScene(event_position)
        cursor_ellipse_bounding_rect = QtCore.QRectF(event_position_center.x()-10*self.scaling_factor,
                                                     event_position_center.y()-10*self.scaling_factor,
                                                     20*self.scaling_factor, 20*self.scaling_factor)

        self.cursor_ellipse= self._scene.addEllipse(cursor_ellipse_bounding_rect, self.ellipse_pen, self.brush)

        self.cursor_line = self._scene.addLine(viewport_center.x(), viewport_center.y(), event_position_center.x(),
                                               event_position_center.y(), self.line_pen)

        # Note: when drawing ellipses, the resolution of the drawing tool is 1/16th of a degree

        # Align 0 degrees with vertical direction
        self.angle_arc.setStartAngle(90*16)

        # define points that will define the vertex and the vertex angle
        top_middle_point = (viewport_center.x(), 0)
        center_point = (viewport_center.x(), viewport_center.y())
        cursor_point = (event_position_center.x(), event_position_center.y())

        self.arc_span_angle = self.angleBetween(top_middle_point, center_point, cursor_point)
        # convert to degrees relative to vertical, cw positive
        self.angle_arc.setSpanAngle(-16*self.arc_span_angle)

        self._scene.addItem(self.angle_arc)

        # Add angle text
        # text box to show distance that scale represents
        self.distance_text_box = QtWidgets.QGraphicsTextItem()
        text_font = QtGui.QFont()
        text_font.setPointSize(25*self.scaling_factor)
        self.distance_text_box.setDefaultTextColor(QtCore.Qt.red)
        self.distance_text_box.setFont(text_font)
        self.distance_text_box.setPos(viewport_center.x() + 50*self.scaling_factor, viewport_center.y() - 50*self.scaling_factor)
        self.distance_text_box.setHtml('{:7.2f} deg'.format(round(self.arc_span_angle, 2)))
        self._scene.addItem(self.distance_text_box)

    def submitOrientation(self, event_position):
        self.relative_orientation = self.arc_span_angle
        self.orientation_defined_signal.emit(self.relative_orientation)

        for item in self._scene.items():
            if item == self.center_ellipse or item == self.cursor_ellipse or item == self.vertical_reference_line or item == self.cursor_line or item == self.angle_arc or item == self.distance_text_box:
                self._scene.removeItem(item)

    def deleteDynamicElementsFromScene(self):
        for item in self._scene.items():
            if item == self.cursor_ellipse or item == self.cursor_line or item == self.angle_arc or item == self.distance_text_box:
                self._scene.removeItem(item)

    def angleBetween(self, p1, p2, p3):
        a = np.array([p1[0], p1[1]])
        b = np.array([p2[0], p2[1]])
        c = np.array([p3[0], p3[1]])

        ba = a - b
        bc = c - b

        cosine_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
        angle = np.arccos(cosine_angle)

        # Adjust angle
        if p3[0] < p2[0]:
            angle = (2*np.pi - angle)

        return float(np.degrees(angle))

    def isImageNull(self):
        return self._photo.pixmap().isNull()

    def getImageSize(self):
        return self._photo.pixmap().rect()

    def getScene(self):
        return self._scene

    def getPhotoItem(self):
        return self._photo
