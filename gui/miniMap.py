from PyQt5 import QtCore, QtGui, QtWidgets
from db.models import *

class MiniMap(QtWidgets.QGraphicsView):
	def __init__(self, parent):
		super(MiniMap, self).__init__(parent)

		# initialize objects
		self._scene = QtWidgets.QGraphicsScene(self)
		self._map = QtWidgets.QGraphicsPixmapItem()
		self._scene.addItem(self._map)
		self.setScene(self._scene)
		
		# configure MiniMap to be an observer of TaggingTab
		self.parent().parent().addObserver(self)
		
		# todo: add a db interface which would find the map for a particular flight
		# display the original pixmap on startup
		self._map_filepath = "./gui/minimap_img.png"

		self._original_pixmap = QtGui.QPixmap(self._map_filepath)
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()
		

	def notify(self, event, _, data):
		if event is "CURRENT_IMG_CHANGED":
			# retrieve full image object from DB
			img = Image.objects.filter(filename=data).last()

			self.showImageContourOnMinimap()

			if data == '20160430_111051_217148.jpg':
				self.overlayCoordinates1(self._map_filepath)

			elif data == '20160430_111116_587485.jpg':
				self.overlayCoordinates2(self._map_filepath)

	def restoreOriginalPixmap(self):
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()

	def fitInView(self):
		rect = QtCore.QRectF(self._map.pixmap().rect())
		if not rect.isNull():
			unity = self.transform().mapRect(QtCore.QRectF(0, 0, 1, 1))
			self.scale(1 / unity.width(), 1 / unity.height())
			viewrect = self.viewport().rect()
			scenerect = self.transform().mapRect(rect)
			factor = min(viewrect.width() / scenerect.width(),
						 viewrect.height() / scenerect.height())
			self.scale(factor, factor)
			self.centerOn(rect.center())

	def showImageContourOnMinimap(self):
		pass

	# in the future, this function is going to accept four pairs of geodetic
	# coordinates from an image that's selected from the "Images" panel and
	# draw a rectangle to show where this image is on the global map
	def overlayCoordinates1(self, pixmap_filepath):
		pixmap_marked_copy = QtGui.QPixmap(pixmap_filepath)
		# self._map.setPixmap(pixmap_marked_copy)
		# self.fitInView()

		painter = QtGui.QPainter(pixmap_marked_copy)
		painter.setPen(QtGui.QColor("red"))
		painter.drawRect(100, 100, 100, 100)
		painter.end()

		self._map.setPixmap(pixmap_marked_copy)
		self.fitInView()

	def overlayCoordinates2(self, pixmap_filepath):
		pixmap_marked_copy = QtGui.QPixmap(pixmap_filepath)		
		self._map.setPixmap(pixmap_marked_copy)
		self.fitInView()

		painter = QtGui.QPainter(pixmap_marked_copy)
		painter.setPen(QtGui.QColor("red"))
		painter.drawRect(100, 100, 100, 100)
		painter.end()

		self._map.setPixmap(pixmap_marked_copy)
		# self.fitInView()
		