from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog

from ui.ui_taggingTab import Ui_TaggingTab
from tagDialog import TagDialog
from db.dbHelper import *
from observer import *
from utils.imageInfo import createImageWithExif
from utils.geolocate import geolocateLatLonFromPixel, getPixelFromLatLon
from utils.geographicUtilities import *
from gui.imageListItem import ImageListItem
from gui.tagTableItem import TagTableItem
from markerItem import MarkerItem

TAG_TABLE_INDICES = {'TYPE': 0, 'SUBTYPE': 1, 'COUNT': 2, 'SYMBOL': 3}

class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab, Observable):
    def __init__(self):
        super(TaggingTab, self).__init__()
        Observable.__init__(self)

        self.currentFlight = None
        self.currentImage = None

        self.setupUi(self)
        self.connectButtons()

        self.image_list_item_dict = {}

        self.viewer_single.getPhotoItem().addObserver(self)

    def notify(self, event, id, data):
        if event is "MARKER_CREATE":
            self.addMarker(data)
        elif event is "MARKER_DELETED":
            self.viewer_single.getScene().removeItem(data)
            data.getMarker().tag.num_occurrences -= 1
            data.getMarker().tag.save()
            self.updateTagMarkerCountInUi(data.getMarker().tag)
            delete_marker(data.getMarker())
        elif event is "MARKER_PARENT_IMAGE_CHANGE":
            if data in self.image_list_item_dict:
                self.list_images.setCurrentItem(self.image_list_item_dict.get(data))

    def connectButtons(self):
        self.button_addTag.clicked.connect(self.addTag)
        self.button_editTag.clicked.connect(self.editTag)
        self.button_removeTag.clicked.connect(self.removeTag)

        self.list_images.currentItemChanged.connect(self.currentImageChanged)
        self.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.button_previous.clicked.connect(self.previousImage)
        self.button_next.clicked.connect(self.nextImage)
        self.button_addImage.clicked.connect(self.addImage)

    def addTag(self):
        dialog = TagDialog(title="Create tag")
        if dialog.exec_() == QDialog.Accepted:
            if len(dialog.subtype.text()) > 0:
                tagType = dialog.tagType.text()
                subtype = dialog.subtype.text()
                icon = dialog.icons.currentText()
                t = create_tag(type=tagType, subtype=subtype, symbol=icon)
                self.addTagToUi(t)
                self.notifyObservers("TAG_CREATED", None, t)

    def addTagToUi(self, tag):
        row = self.list_tags.rowCount()
        self.list_tags.insertRow(row)

        # update all columns in row with these texts
        texts = [tag.type, tag.subtype, str(tag.num_occurrences), tag.symbol]
        [self.list_tags.setItem(row, col, TagTableItem(text, tag)) for col, text in enumerate(texts)]

        # add tag to context menu
        self.viewer_single.getPhotoItem().context_menu.addTagToContextMenu(tag)

    def editTag(self):
        row = self.list_tags.currentRow()
        if row >= 0:
            tag = self.list_tags.item(row, 0).getTag()
            tagType = tag.type
            subtype = tag.subtype
            icon = tag.symbol
            dialog = TagDialog(title="Edit tag")
            dialog.tagType.setText(tagType)
            dialog.subtype.setText(subtype)
            index = dialog.icons.findText(icon)
            dialog.icons.setCurrentIndex(index)
            if dialog.exec_() == QDialog.Accepted:
                if len(dialog.subtype.text()) > 0:
                    tag.type = dialog.tagType.text()
                    tag.subtype = dialog.subtype.text()
                    tag.symbol = dialog.icons.currentText()
                    tag.save()

                    # update all columns in row with these texts
                    texts = [tag.type, tag.subtype, str(tag.num_occurrences), tag.symbol]
                    [self.list_tags.setItem(row, col, TagTableItem(text, tag)) for col, text in enumerate(texts)]

                    # update tag in context menu
                    self.viewer_single.getPhotoItem().context_menu.updateTagItem(tag)

                    self.notifyObservers("TAG_EDITED", None, tag)

    def removeTag(self):
        row = self.list_tags.currentRow()
        tag = self.list_tags.item(row, 0).getTag()
        if row >= 0:
            self.list_tags.removeRow(row)
            self.viewer_single.getPhotoItem().context_menu.removeTagItem(tag)
            self.deleteMarkersFromUi(tag=tag)
            self.notifyObservers("TAG_DELETED", None, tag)

    def addMarker(self, data):
        event, tag = data
        pu = event.scenePos().x()
        pv = event.scenePos().y()
        lat, lon = geolocateLatLonFromPixel(self.currentImage, self.currentFlight.reference_altitude, pu, pv)
        m = create_marker(tag=tag, image=self.currentImage, latitude=lat, longitude=lon)
        m.tag.num_occurrences += 1
        m.tag.save()

        # update the marker count in the table
        self.updateTagMarkerCountInUi(tag)

        self.addMarkerToUi(pu, pv, m, 1.0) # 1.0 means fully opaque for markers created in current image
        self.notifyObservers("MARKER_CREATED", None, m)

    def addMarkerToUi(self, x, y, marker, opacity):
        # Create MarkerItem
        image_width = self.currentImage.width
        initial_zoom = self.viewer_single.zoomFactor()
        marker = MarkerItem(marker, current_image=self.currentImage, initial_zoom=initial_zoom)
        marker.addObserver(self)

        # Correctly position the MarkerItem graphic on the UI
        markerXPos = x - marker.pixmap().size().width() / 2  # To position w.r.t. center of pixMap
        markerYPos = y - marker.pixmap().size().height() / 2  # To position w.r.t. center of pixMap
        marker.setPos(markerXPos, markerYPos)

        # The following line makes sure that the scaling happens w.r.t. center of pixMap
        marker.setTransformOriginPoint(marker.pixmap().size().width() / 2, marker.pixmap().size().height() / 2)

        # Set image opacity
        marker.setOpacity(opacity)

        self.viewer_single.getScene().addItem(marker)

    def updateTagMarkerCountInUi(self, tag):
        for rowIndex in range(self.list_tags.rowCount()):
            tableTag = self.list_tags.item(rowIndex, TAG_TABLE_INDICES['COUNT']).getTag()
            if tableTag == tag:
                self.list_tags.setItem(rowIndex, TAG_TABLE_INDICES['COUNT'], TagTableItem(str(tag.num_occurrences), tag))

    def deleteMarkersFromUi(self, tag=None):
        sceneObjects = self.viewer_single.getScene().items()
        for item in sceneObjects:
            if type(item) is MarkerItem:
                if tag != None:
                    if item.getMarker().tag == tag:
                        self.viewer_single.getScene().removeItem(item)
                        item.getMarker().tag.num_occurrences -= 1
                        item.getMarker().tag.save()
                else:
                    self.viewer_single.getScene().removeItem(item)

    def toggleImageReviewed(self):
        item = self.list_images.currentItem()
        if item:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

            # image was marked as reviewed
            if not font.bold():
                self.nextImage()

    def addImage(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select images", ".", "Images (*.jpg)")[0]
        for path in paths:
            image = createImageWithExif(path, self.currentFlight)
            self.notifyObservers("IMAGE_ADDED", None, image)
            self.addImageToUi(image)

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        font = item.font()
        font.setBold(True)
        item.setFont(font)
        self.list_images.addItem(item)
        self.image_list_item_dict[image] = item

    def currentImageChanged(self, current, _):
        # Clear the scene
        self.deleteMarkersFromUi()

        self.currentImage = current.getImage()
        self.openImage(self.currentImage.filename, self.viewer_single)
        self.minimap.updateContourOnImageChange(self.currentImage)

        # Display markers for this image
        image_width = self.currentImage.width
        image_height = self.currentImage.height
        marker_list = self.getMarkersForImage(self.currentImage)
        reference_altitude = self.currentFlight.reference_altitude
        for marker in marker_list:
            x, y = getPixelFromLatLon(self.currentImage, image_width, image_height, reference_altitude, marker.latitude, marker.longitude)
            opacity = 1.0
            if marker.image != self.currentImage:
                opacity = 0.5
            self.addMarkerToUi(x, y, marker, opacity)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def previousImage(self):
        self.setImageRow(self.list_images.currentRow() - 1)

    def nextImage(self):
        self.setImageRow(self.list_images.currentRow() + 1)

    def setImageRow(self, row):
        if 0 <= row < self.list_images.count():
            self.list_images.setCurrentRow(row)

    def getSelectedImageSize(self):
        return self.viewer_single.getImageSize()

    def getCurrentImage(self):
        return self.currentImage

    def getCurrentFlight(self):
        return self.currentFlight

    def getMarkersForImage(self, image):
        _list = list(Marker.objects.filter(image=image)) # Convert QuerySet to a list
        for m in Marker.objects.exclude(image=image):
            image_width = image.width
            image_height = image.height

            image_bounds = PolygonBounds()

            #The order of UL UR LR LL is important
            # Upper Left
            lat, lon = geolocateLatLonFromPixel(image, self.currentFlight.reference_altitude, 0, 0)
            image_bounds.addVertex(Point(lat, lon))

            # Upper Right
            lat, lon = geolocateLatLonFromPixel(image, self.currentFlight.reference_altitude, image_width, 0)
            image_bounds.addVertex(Point(lat, lon))

            # Lower Right
            lat, lon = geolocateLatLonFromPixel(image, self.currentFlight.reference_altitude, image_width, image_height)
            image_bounds.addVertex(Point(lat, lon))

            # Lower Left
            lat, lon = geolocateLatLonFromPixel(image, self.currentFlight.reference_altitude, 0, image_height)
            image_bounds.addVertex(Point(lat, lon))

            marker_loc = Point(m.latitude, m.longitude)

            if image_bounds.isPointInsideBounds(marker_loc):
                _list.append(m)

        return _list

    def resetTab(self):
        # clear all images and references to the objects
        self.image_list_item_dict = {}
        self.disableCurrentImageChangedEvent() # disconnect signal to avoid triggering an event
        self.list_images.clear()
        self.enableCurrentItemChangedEvent() # re-enable the event

        # clear all tags
        self.list_tags.setRowCount(0) # discards all rows and data stored in them
        self.viewer_single.getPhotoItem().context_menu.clearTagContextMenu() # clear tags from the context menu

        # clear all markers
        self.deleteMarkersFromUi()

        # reset area map
        self.minimap.reset()

        # clear the photo viewer
        self.viewer_single.setPhoto(None)

    def disableCurrentImageChangedEvent(self):
        self.list_images.currentItemChanged.disconnect(self.currentImageChanged)

    def enableCurrentItemChangedEvent(self):
        self.list_images.currentItemChanged.connect(self.currentImageChanged)