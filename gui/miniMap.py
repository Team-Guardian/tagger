from PyQt5 import QtCore, QtGui, QtWidgets
from db.models import *

class MiniMap(QtWidgets.QGraphicsView):
	def __init__(self, parent):
		super(MiniMap, self).__init__(parent)

		self._minimap_path = "./gui/minimap_img.png"

		self._pixmap = QtGui.QPixmap(self._minimap_path)
		viewrect = self.viewport().rect() # get the current size of the window viewport
		self._pixmapScaledDown = self._pixmap.scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio)

		self._map = QtWidgets.QGraphicsPixmapItem()
		self._map.setPixmap(self._pixmapScaledDown)

		# configure MiniMap to be an observer of TaggingTab
		self.parent().parent().addObserver(self)
		
		self._scene = QtWidgets.QGraphicsScene(self)
		self._scene.addItem(self._map)
		self.setScene(self._scene)

	def notify(self, event, _, data):
		if event is "CURRENT_IMG_CHANGED":
			# Todo: implement search DB for the image with filename
			img = Image.objects.filter(filename='').last()



			if data == '20160430_111051_217148.jpg':
				self.overlayCoordinates1(self._minimap_path)

			elif data == '20160430_111116_587485.jpg':
				self.overlayCoordinates2(self._minimap_path)

	# in the future, this function is going to accept four pairs of geodetic
	# coordinates from an image that's selected from the "Images" panel and
	# draw a rectangle to show where this image is on the global map
	def overlayCoordinates1(self, minimap_path):
		labelled_minimap = QtGui.QPixmap(minimap_path)
		viewrect = self.viewport().rect()  # get the current size of the window viewport
		labelled_minimap_scaled = labelled_minimap.scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio)

		rectangle = QtCore.QRect(10, 10, 100, 60)
		painter = QtGui.QPainter(labelled_minimap_scaled)
		painter.setPen(QtGui.QColor("black"))
		painter.drawRect(rectangle)
		painter.end()

		# re-render the pixmap
		self._map.setPixmap(labelled_minimap_scaled)


	def overlayCoordinates2(self, minimap_path):
		labelled_minimap = QtGui.QPixmap(minimap_path)
		viewrect = self.viewport().rect()  # get the current size of the window viewport
		labelled_minimap_scaled = labelled_minimap.scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio)

		rectangle = QtCore.QRect(50, 100, 100, 60)
		painter = QtGui.QPainter(labelled_minimap_scaled)
		painter.setPen(QtGui.QColor("black"))
		painter.drawRect(rectangle)
		painter.end()

		# re-render the pixmap
		self._map.setPixmap(labelled_minimap_scaled)