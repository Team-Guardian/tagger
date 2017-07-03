# StackOverflow for the win! http://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview

from PyQt5 import QtCore, QtGui, QtWidgets
from photoItem import PhotoItem
from markerItem import MarkerItem
from scale import Scale


class PhotoViewer(QtWidgets.QGraphicsView):

    target_cropped_signal = QtCore.pyqtSignal(QtCore.QRectF)
    target_crop_cancel_signal = QtCore.pyqtSignal()

    def __init__(self, parent):
        super(PhotoViewer, self).__init__(parent)
        self._zoom = 0
        self._scene = QtWidgets.QGraphicsScene(self)
        self._photo = PhotoItem()
        self._scale = Scale()
        self._scene.addItem(self._photo)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setBackgroundBrush(QtGui.QBrush(QtGui.QColor(30, 30, 30)))
        self.setFrameShape(QtWidgets.QFrame.NoFrame)

        self._scale.setGraphicsView(self)

        self.rubber_band = None
        self.rubber_band_initial_point = 0
        self.rubber_band_end_point = 0
        self.crop_enabled = False

        self.viewport().installEventFilter(self)

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
            self.centerOn(rect.center())
            self._zoom = 0

    def setPhoto(self, pixmap=None):
        self._zoom = 0
        if pixmap and not pixmap.isNull():
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)
            self._photo.setPixmap(pixmap)
            self.fitInView()
        else:
            self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
            self._photo.setPixmap(QtGui.QPixmap())

    def zoomFactor(self):
        return self._zoom

    def wheelEvent(self, event):
        marker_items = [] # List of all marker items in the current _scene
        for item in self._scene.items():
            if type(item) == MarkerItem:
                marker_items.append(item)

        if not self._photo.pixmap().isNull():
            if event.angleDelta().y() > 0:
                factor = 1.25
                self._zoom += 1
            else:
                factor = 0.8
                self._zoom -= 1

            if self._zoom > 0:
                self.scale(factor, factor)

                for item in marker_items:
                    if event.angleDelta().y() > 0:
                        item.notify("SCENE_ZOOM", None, 0.8)
                    else:
                        item.notify("SCENE_ZOOM", None, 1.25)
            elif self._zoom == 0:
                self.fitInView()

                for item in marker_items:
                    item.notify("SCENE_RESET", None, factor)
            else:
                self._zoom = 0

            self.updateScale()

    def eventFilter(self, QObject, QEvent):
        # print QEvent.type()
        if QEvent.type() == QtCore.QEvent.MouseButtonPress and QEvent.modifiers() == QtCore.Qt.ControlModifier and self.crop_enabled:
            if not self.isImageNull() and not self.rubber_band:
                self.rubber_band_initial_point = self.mapToGlobal(QEvent.pos())
                self.rubber_band_end_point = self.mapToGlobal(QEvent.pos())
                self.rubber_band = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle)
                self.rubber_band.setGeometry(QtCore.QRect(self.rubber_band_initial_point, self.rubber_band_end_point))
                self.rubber_band.show()
        elif QEvent.type() == QtCore.QEvent.MouseMove and self.crop_enabled:
            if self.rubber_band:
                self.setDragMode(QtWidgets.QGraphicsView.NoDrag)
                self.rubber_band_end_point = self.mapToGlobal(QEvent.pos())
                x = QEvent.pos().x()
                y = QEvent.pos().y()
                if x >= self.viewport().rect().width():
                    x = self.viewport().rect().width()
                if y >= self.viewport().rect().height():
                    y = self.viewport().rect().height()
                self.rubber_band_end_point = self.mapToGlobal(QtCore.QPoint(x, y))
                self.rubber_band.setGeometry(QtCore.QRect(self.rubber_band_initial_point, self.rubber_band_end_point))
        elif QEvent.type() == QtCore.QEvent.MouseButtonRelease and self.crop_enabled:
            if self.rubber_band:
                self.rubber_band_end_point = self.mapToGlobal(QEvent.pos())
                self.rubber_band.hide()
                scene_rubber_top_left_coordinates = self.mapToScene(self.mapFromGlobal(self.rubber_band_initial_point))
                scene_rubber_bot_right_coordinates = self.mapToScene(self.mapFromGlobal(self.rubber_band_end_point))
                cropping_rect = QtCore.QRectF(scene_rubber_top_left_coordinates,scene_rubber_bot_right_coordinates)
                self.target_cropped_signal.emit(cropping_rect)
                self.rubber_band = None
            self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)

        elif QEvent.type() == QtCore.QEvent.KeyPress and QEvent.key() == QtCore.Qt.Key_Escape and self.crop_enabled:
            print 'here'
            self.target_crop_cancel_signal.emit()

        return QtWidgets.QWidget.eventFilter(self, QObject, QEvent)

    def updateScale(self):
        self._scale.updateScale()

    def isImageNull(self):
        return self._photo.pixmap().isNull()

    def getImageSize(self):
        return self._photo.pixmap().rect()

    def getScale(self):
        return self._scale

    def getScene(self):
        return self._scene

    def getPhotoItem(self):
        return self._photo
