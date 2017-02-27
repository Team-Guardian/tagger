from PyQt5 import QtCore, QtGui, QtWidgets

import utils.georef
from observer import *
from db.models import *

class MiniMap(QtWidgets.QGraphicsView, Observer):
	def __init__(self, parent):
		super(MiniMap, self).__init__(parent)

		# get current flight information

		# initialize objects
		self._scene = QtWidgets.QGraphicsScene(self)
		self._map = QtWidgets.QGraphicsPixmapItem()
		self._scene.addItem(self._map)
		self.setScene(self._scene)

		# configure MiniMap to be an observer of TaggingTab
		self.window().addObserver(self)

		# create null objects
		self._current_area_map = None
		self._current_flight = None

	# show the original minimap after flight has been selected
	def setMinimap(self, flight):
		self._current_flight = flight
		self._current_area_map = flight.area_map

		self._map_full_filepath = flight.img_path + flight.area_map.filename
		self._original_pixmap = QtGui.QPixmap(self._map_full_filepath)
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()

	def notify(self, event, id, data):
		if event is "CURRENT_IMG_CHANGED":
			if self._current_area_map is not None:
				# retrieve full image object from DB
				img = Image.objects.filter(filename=data).last()
				rect = QtCore.QRect(self.parent().parent().getSelectedImageSize())

				(img_upper_left_lat, img_upper_left_lon) = utils.georef.georectify(img, 0, 0)
				(img_lower_right_lat, img_lower_right_lon) = utils.georef.georectify(img, rect.width(), rect.height())

				# interpolate the location of the image on the minimap (in px)
				topLeftX = ((img_upper_left_lon - self._current_area_map.ul_lon)/(self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * rect.width()
				topLeftY = ((img_upper_left_lat - self._current_area_map.ul_lat)/(self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * rect.height()

				bottomRightX = ((img_lower_right_lon - self._current_area_map.ul_lon)/(self._current_area_map.lr_lon - self._current_area_map.ul_lon)) * rect.width()
				bottomRightY = ((img_lower_right_lat - self._current_area_map.ul_lat)/(self._current_area_map.lr_lat - self._current_area_map.ul_lat)) * rect.height()

				contour_coordinates = QtCore.QRect(QtCore.QPoint(topLeftX, topLeftY), QtCore.QPoint(bottomRightX, bottomRightY))

				self.showImageContourOnMinimap(img, contour_coordinates)

	def restoreOriginalPixmap(self):
		self._map.setPixmap(self._original_pixmap)
		self.fitInView()

	def fitInView(self):
		rect = QtCore.QRectF(self._map.pixmap().rect())
		if not rect.isNull():
			viewrect = self.viewport().rect()
			self._map.setPixmap(self._map.pixmap().scaled(viewrect.width(), viewrect.height(), QtCore.Qt.KeepAspectRatio))
			self.centerOn(self._map.pixmap().rect().center())

			return self._map.pixmap() # optional return for when one needs to continue working with this pixmap (such as drawing on top of it)

	# placeholder for the actual function that will be used - overlay funcs below are for testing
	def showImageContourOnMinimap(self, current_image, contour_coords):
		pixmap_marked_copy = QtGui.QPixmap(self._map_full_filepath)
		self._map.setPixmap(pixmap_marked_copy)
		scaled_pixmap_copy = self.fitInView()

		painter = QtGui.QPainter()
		has_painter_started = painter.begin(scaled_pixmap_copy)
		if not has_painter_started:
			pass
		else:
			painter.setPen(QtGui.QColor("red"))
			painter.drawRect(contour_coords)
			painter.end()
		self._map.setPixmap(scaled_pixmap_copy)