from PyQt5 import QtCore, QtGui, QtWidgets

import utils.georef
from db.models import *

class MiniMap(QtWidgets.QGraphicsView):
	def __init__(self, parent):
		super(MiniMap, self).__init__(parent)

		# get current flight information
		# flight = Flight.objects.filter(location=loc).last()

		# initialize objects
		self._scene = QtWidgets.QGraphicsScene(self)
		self._map = QtWidgets.QGraphicsPixmapItem()
		self._scene.addItem(self._map)
		self.setScene(self._scene)

		# configure MiniMap to be an observer of TaggingTab
		self.parent().parent().addObserver(self)

		# display the original pixmap on startup
		# self._map_filepath = flight.img_path # not used until flights are added
		self._map_filepath = self.selectMinimap()

		self._original_pixmap = QtGui.QPixmap(self._map_filepath)
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()

		# enter geodetic coordinates of the corner points
		self._ul_lat, self._ul_lon = 49.912669, -98.301569
		self._ur_lat, self._ur_lon = 49.912669, -98.238935
		self._lr_lat, self._lr_lon = 49.893954, -98.238935
		self._ll_lat, self._ll_lon = 49.893954, -98.301569

	def selectMinimap(self):
		# current_flight = Flight.objects.filter(location=loc).last()
		minimap_img_path = "./gui/minimap_img.png"
		return minimap_img_path

	def notify(self, event, _, data):
		if event is "CURRENT_IMG_CHANGED":
			# retrieve full image object from DB
			img = Image.objects.filter(filename=data).last()
			rect = QtCore.QRect(self.parent().parent().getSelectedImageSize())

			(img_upper_left_lat, img_upper_left_lon) = utils.georef.georectify(img, 0, 0)
			(img_lower_right_lat, img_lower_right_lon) = utils.georef.georectify(img, rect.width(), rect.height())

			# interpolate the location of the image on the minimap (in px)
			topLeftX = ((img_upper_left_lon - self._ul_lon)/(self._ur_lon - self._ul_lon)) * rect.width()
			topLeftY = ((img_upper_left_lat - self._ul_lat)/(self._ll_lat - self._ul_lat)) * rect.height()

			bottomRightX = ((img_lower_right_lon - self._ul_lon)/(self._ur_lon - self._ul_lon)) * rect.width()
			bottomRightY = ((img_lower_right_lat - self._ul_lat)/(self._ll_lat - self._ul_lat)) * rect.height()

			contour_coordinates = QtCore.QRect(QtCore.QPoint(topLeftX, topLeftY), QtCore.QPoint(bottomRightX, bottomRightY))

			self.showImageContourOnMinimap(img, contour_coordinates)

			# if data == '20160430_111051_217148.jpg':
			# 	self.overlayCoordinates1(self._map_filepath)

			# elif data == '20160430_111116_587485.jpg':
			# 	self.overlayCoordinates2(self._map_filepath)

	def restoreOriginalPixmap(self):
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()

	def fitInView(self):
		rect = QtCore.QRectF(self._map.pixmap().rect())
		if not rect.isNull():
			viewrect = self.viewport().rect()
			self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
			self.centerOn(self._map.pixmap().rect().center())

			return self._map.pixmap() # optioal return for when one needs to continue working with this pixmap

	# placeholder for the actual function that will be used - overlay funcs below are for testing
	def showImageContourOnMinimap(self, current_image, contour_coords):
		pixmap_marked_copy = QtGui.QPixmap(self._map_filepath)
		self._map.setPixmap(pixmap_marked_copy)
		scaled_pixmap_copy = self.fitInView()

		painter = QtGui.QPainter()
		current_pxmp = self._map.pixmap()
		has_painter_started = painter.begin(scaled_pixmap_copy)
		if not has_painter_started:
			pass
		else:
			painter.setPen(QtGui.QColor("red"))
			painter.drawRect(contour_coords)
			painter.end()

		self._map.setPixmap(scaled_pixmap_copy)