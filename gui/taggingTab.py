from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect

from ui.ui_taggingTab import Ui_TaggingTab
from tagDialog import TagDialog
from db.dbHelper import *
from observer import *
from utils.imageInfo import processNewImage
from utils.geolocate import geolocateLatLonFromPixel, getPixelFromLatLon
from utils.geographicUtilities import *
from gui.imageListItem import ImageListItem
from gui.tagTableItem import TagTableItem
from markerItem import MarkerItem

from utils.imageInfo import FLIGHT_DIRECTORY
TAG_TABLE_INDICES = {'TYPE': 0, 'SUBTYPE': 1, 'COUNT': 2, 'SYMBOL': 3}
image_status_tabs_TAB_INDICES = {'REVIEWED': 0, 'NOT_REVIEWED': 1, 'ALL_IMAGES': 2}

class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab, Observable):
    def __init__(self):
        super(TaggingTab, self).__init__()
        Observable.__init__(self)

        self.currentFlight = None
        self.currentImage = None

        self.setupUi(self)
        self.connectButtons()

        self.image_list_item_dict = {}
        self.tag_dialog = TagDialog()

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

        self.images_list.currentItemChanged.connect(self.currentImageChanged)
        self.radioButton_allImages.toggled.connect(self.allImagesButtonToggled)
        self.radioButton_reviewed.toggled.connect(self.reviewedButtonToggled)
        self.radioButton_notReviewed.toggled.connect(self.notReviewedButtonToggled)

        self.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.button_previous.clicked.connect(self.previousImage)
        self.button_next.clicked.connect(self.nextImage)
        self.button_addImage.clicked.connect(self.addImage)

    def addTag(self):
        self.tag_dialog.setWindowTitle("Create tag")
        self.tag_dialog.tagType.setText('')
        self.tag_dialog.subtype.setText('')
        self.tag_dialog.icons.setCurrentIndex(0)
        if self.tag_dialog.exec_() == QDialog.Accepted:
            if len(self.tag_dialog.tagType.text()) > 0 and len(self.tag_dialog.subtype.text()) > 0:
                tagType = self.tag_dialog.tagType.text()
                subtype = self.tag_dialog.subtype.text()
                count = "0"
                icon = self.tag_dialog.icons.currentText()
                t = create_tag(type=tagType, subtype=subtype, symbol=icon, num_occurrences=int(count))
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

        # Update the drop-down menu for adding/editing tags
        self.tag_dialog.removeIcon(tag.symbol)

    def editTag(self):
        row = self.list_tags.currentRow()
        if row >= 0:
            tag = self.list_tags.item(row, 0).getTag()
            tagType = tag.type
            subtype = tag.subtype
            icon = tag.symbol
            self.tag_dialog.setWindowTitle("Edit tag")
            self.tag_dialog.tagType.setText(tagType)
            self.tag_dialog.subtype.setText(subtype)
            self.tag_dialog.addIcon(icon) # Show the current symbol in the list
            index = self.tag_dialog.icons.findText(icon)
            self.tag_dialog.icons.setCurrentIndex(index)
            if self.tag_dialog.exec_() == QDialog.Accepted:
                if len(self.tag_dialog.tagType.text()) > 0 and len(self.tag_dialog.subtype.text()) > 0:
                    tag.type = self.tag_dialog.tagType.text()
                    tag.subtype = self.tag_dialog.subtype.text()
                    tag.num_occurrences = -1
                    tag.symbol = self.tag_dialog.icons.currentText()
                    tag.save()

                    # If the icon has been changed, update the icons in the drop-down menu and all markers
                    if icon != tag.symbol:
                        self.tag_dialog.removeIcon(tag.symbol)

                        if self.currentImage != None:
                            self.deleteMarkersFromUi(tag=tag)
                            image_width = self.currentImage.width
                            image_height = self.currentImage.height
                            reference_altitude = self.currentFlight.reference_altitude
                            marker_list = self.getMarkersForImage()
                            for marker in marker_list:
                                x, y = getPixelFromLatLon(self.currentImage, image_width, image_height, reference_altitude, \
                                                          marker.latitude, marker.longitude)
                                opacity = 1.0
                                if marker.image != self.currentImage:
                                    opacity = 0.5
                                self.addMarkerToUi(x, y, marker, opacity)
                    else:
                        self.tag_dialog.removeIcon(icon) # Remove the current symbol if it hasn't been changed

                    # update all columns in row with these texts
                    texts = [tag.type, tag.subtype, str(tag.num_occurrences), tag.symbol]
                    [self.list_tags.setItem(row, col, TagTableItem(text, tag)) for col, text in enumerate(texts)]

                    # update tag in context menu
                    self.viewer_single.getPhotoItem().context_menu.updateTagItem(tag)

                    self.notifyObservers("TAG_EDITED", None, tag)
            else:
                self.tag_dialog.removeIcon(icon) # Remove the current symbol if it hasn't been changed

    def removeTag(self):
        row = self.list_tags.currentRow()
        tag = self.list_tags.item(row, 0).getTag()
        if row >= 0:
            self.list_tags.removeRow(row)
            self.viewer_single.getPhotoItem().context_menu.removeTagItem(tag)
            self.deleteMarkersFromUi(tag=tag)
            self.tag_dialog.addIcon(tag.symbol)
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
        item = self.images_list.currentItem()
        if item:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)
            item.getImage().is_reviewed = False

            # image was marked as reviewed
            if not font.bold():
                item.getImage().is_reviewed = True
                self.nextImage()

            item.getImage().save()

    def addImage(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select images", ".", "Images (*.jpg)")[0]
        for path in paths:
            image = processNewImage(path, self.currentFlight)
            self.notifyObservers("IMAGE_ADDED", None, image)

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.images_list.addItem(item)
        self.image_list_item_dict[image] = item

    def currentImageChanged(self, current, _):
        # Clear the scene
        self.deleteMarkersFromUi()

        self.currentImage = current.getImage()

        self.minimap.updateContourOnImageChange(self.currentImage)
        self.openImage('./flights/{}/{}'.format(self.currentFlight.img_path, self.currentImage.filename), self.viewer_single)

        # Display markers for this image
        image_width = self.currentImage.width
        image_height = self.currentImage.height
        marker_list = self.getMarkersForImage()
        reference_altitude = self.currentFlight.reference_altitude
        for marker in marker_list:
            x, y = getPixelFromLatLon(self.currentImage, image_width, image_height, reference_altitude, marker.latitude, marker.longitude)
            opacity = 1.0
            if marker.image != self.currentImage:
                opacity = 0.5
            self.addMarkerToUi(x, y, marker, opacity)

    def allImagesButtonToggled(self):
        for row_num in range(self.images_list.count()):
            self.images_list.item(row_num).setHidden(False)

    def reviewedButtonToggled(self):
        for image, item in self.image_list_item_dict.iteritems():
            item_row = self.images_list.row(item)
            if image.is_reviewed:
                self.images_list.item(item_row).setHidden(False)
            else:
                self.images_list.item(item_row).setHidden(True)

    def notReviewedButtonToggled(self):
        for image, item in self.image_list_item_dict.iteritems():
            item_row = self.images_list.row(item)
            if not image.is_reviewed:
                self.images_list.item(item_row).setHidden(False)
            else:
                self.images_list.item(item_row).setHidden(True)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def previousImage(self):
        next_row = self.images_list.currentRow() - 1
        self.setImageRow(next_row)

    def nextImage(self):
        next_row = self.images_list.currentRow() + 1
        self.setImageRow(next_row)

    def setImageRow(self, row):
        if 0 <= row < self.images_list.count():
            self.images_list.setCurrentRow(row)

    def getSelectedImageSize(self):
        return self.viewer_single.getImageSize()

    def getCurrentImage(self):
        return self.currentImage

    def getCurrentFlight(self):
        return self.currentFlight

    def getMarkersForImage(self):
        image = self.currentImage
        _list = list(Marker.objects.filter(image=image)) # Convert QuerySet to a list

        for m in Marker.objects.filter(image__flight=self.currentFlight).exclude(image=image):
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
        self.images_list.clear()
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
        self.images_list.currentItemChanged.disconnect(self.currentImageChanged)

    def enableCurrentItemChangedEvent(self):
        self.images_list.currentItemChanged.connect(self.currentImageChanged)

    def saveImage(self):
        scene_width = self.viewer_single.viewport().rect().width()
        scene_height = self.viewer_single.viewport().rect().height()
        imageTopLeftPixel = self.viewer_single.mapToScene(0, 0) # Currently displayed top left pixel
        imageBottomRightPixel = self.viewer_single.mapToScene(scene_width, scene_height) # Currently displayed bottom right pixel
        if self.currentImage != None:
            image_path = FLIGHT_DIRECTORY + '{}/{}'.format(self.currentFlight.img_path, self.currentImage.filename)
            pixmap = QPixmap(image_path)
            fileSaveDialog = QtWidgets.QFileDialog()
            fileSaveDialog.setWindowTitle('Save Image')
            fileSaveDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            fileSaveDialog.setNameFilter('Images (*.jpg)')
            fileSaveDialog.setDefaultSuffix('.jpg')
            if fileSaveDialog.exec_() == QtWidgets.QFileDialog.Accepted:
                fName = fileSaveDialog.selectedFiles()[0]
                if self.viewer_single.zoomFactor() == 0: # This means that the image is fully zoomed out
                    pixmap.save(fName, format='jpg', quality=100)
                else:
                    save_image_width = imageBottomRightPixel.x() - imageTopLeftPixel.x()
                    save_image_height = imageBottomRightPixel.y() - imageTopLeftPixel.y()
                    cropping_rect = QRect(imageTopLeftPixel.x(), imageTopLeftPixel.y(), \
                                          save_image_width, save_image_height)
                    cropped_pixmap = pixmap.copy(cropping_rect)
                    cropped_pixmap.save(fName, format='jpg', quality=100)

