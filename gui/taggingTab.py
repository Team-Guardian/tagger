from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
from ui.ui_taggingTab import Ui_TaggingTab
from tagDialog import TagDialog
from db.dbHelper import *
from observer import *
from utils.geolocate import geolocateLatLonFromPixelOnImage, getPixelFromLatLon
from utils.geographicUtilities import *
from gui.imageListItem import ImageListItem
from gui.tagTableItem import TagTableItem
from gui.tagContextMenu import TagContextMenu
from markerItem import MarkerItem
from utils.imageInfo import GetDirectoryAndFilenameFromFullPath, FLIGHT_DIRECTORY
from utils.imageInfo import processNewImage
from utils.geolocate import getPixelFromLatLon
from utils.geographicUtilities import *


TAG_TABLE_INDICES = {'TYPE': 0, 'SUBTYPE': 1, 'COUNT': 2, 'SYMBOL': 3}

class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab, Observable):
    def __init__(self):
        super(TaggingTab, self).__init__()
        Observable.__init__(self)

        self.currentFlight = None
        self.currentImage = None

        self.setupUi(self)
        self.connectButtons()
        self.radioButton_allImages.setChecked(True)

        self.image_list_item_dict = {}
        self.tag_dialog = TagDialog()

        self.tagging_tab_context_menu = TagContextMenu()
        self.viewer_single._photo.setTabContextMenu(self.tagging_tab_context_menu)

        self.viewer_single.getPhotoItem().addObserver(self)

    def notify(self, event, id, data):
        if event is "MARKER_CREATE":
            self.addMarker(data)
        elif event is "MARKER_DELETED":
            self.viewer_single.getScene().removeItem(data)
            marker_to_delete = data.getMarker()
            marker_to_delete.tag.num_occurrences -= 1
            marker_to_delete.tag.save()
            self.updateTagMarkerCountInUi(marker_to_delete.tag)
            delete_marker(marker_to_delete)
            self.notifyObservers("MARKER_DELETED", None, marker_to_delete)
        elif event is "MARKER_PARENT_IMAGE_CHANGE":
            if data in self.image_list_item_dict:
                self.list_images.setCurrentItem(self.image_list_item_dict.get(data))

    def connectButtons(self):
        self.button_addTag.clicked.connect(self.addTag)
        self.button_editTag.clicked.connect(self.editTag)
        self.button_removeTag.clicked.connect(self.removeTag)

        self.list_images.currentItemChanged.connect(self.currentImageChanged)
        self.radioButton_allImages.clicked.connect(self.allImagesButtonToggled)
        self.radioButton_reviewed.clicked.connect(self.reviewedButtonToggled)
        self.radioButton_notReviewed.clicked.connect(self.notReviewedButtonToggled)

        self.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.button_addImage.clicked.connect(self.addImage)

    def addTag(self):
        self.tag_dialog.setWindowTitle("Create tag")
        self.tag_dialog.tagType.setText('')
        self.tag_dialog.tagType.setFocus()
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
        self.tagging_tab_context_menu.addTagToContextMenu(tag)

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
            self.tag_dialog.tagType.setFocus()
            self.tag_dialog.subtype.setText(subtype)
            self.tag_dialog.addIcon(icon) # Show the current symbol in the list
            index = self.tag_dialog.icons.findText(icon)
            self.tag_dialog.icons.setCurrentIndex(index)
            if self.tag_dialog.exec_() == QDialog.Accepted:
                if len(self.tag_dialog.tagType.text()) > 0 and len(self.tag_dialog.subtype.text()) > 0:
                    tag.type = self.tag_dialog.tagType.text()
                    tag.subtype = self.tag_dialog.subtype.text()
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
                    self.tagging_tab_context_menu.updateTagItem(tag)

                    self.notifyObservers("TAG_EDITED", None, tag)
            else:
                self.tag_dialog.removeIcon(icon) # Remove the current symbol if it hasn't been changed

    def removeTag(self):
        row = self.list_tags.currentRow()
        tag = self.list_tags.item(row, 0).getTag()
        if row >= 0:
            self.list_tags.removeRow(row)
            self.tagging_tab_context_menu.removeTagItem(tag)
            self.deleteMarkersFromUi(tag=tag)
            self.tag_dialog.addIcon(tag.symbol)
            self.notifyObservers("TAG_DELETED", None, tag)

    def addMarker(self, tag):
        pu = self.tagging_tab_context_menu.pixel_x_invocation_coord
        pv = self.tagging_tab_context_menu.pixel_y_invocation_coord
        lat, lon = geolocateLatLonFromPixelOnImage(self.currentImage, self.currentFlight.reference_altitude, pu, pv)
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
        markerYPos = y - marker.pixmap().size().height()  # To position w.r.t. center of pixMap
        marker.setPos(markerXPos, markerYPos)

        # The following line makes sure that the scaling happens w.r.t. center of pixMap
        marker.setTransformOriginPoint(marker.pixmap().size().width() / 2, marker.pixmap().size().height())

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
                        marker_to_delete_from_ui = item.getMarker()
                        marker_to_delete_from_ui.tag.num_occurrences -= 1
                        marker_to_delete_from_ui.tag.save()
                        self.notifyObservers("MARKER_DELETED", None, marker_to_delete_from_ui)
                else:
                    self.viewer_single.getScene().removeItem(item)

    def updateImageList(self):
        for row_num in range(self.list_images.count()):
            item = self.list_images.item(row_num)
            image = item.getImage()
            image.refresh_from_db()

            font = item.font()
            if not image.is_reviewed:
                font.setBold(True)
            else:
                font.setBold(False)

            item.setFont(font)

        if self.radioButton_allImages.isChecked():
            self.allImagesButtonToggled()
        if self.radioButton_notReviewed.isChecked():
            self.notReviewedButtonToggled()
        if self.radioButton_reviewed.isChecked():
            self.reviewedButtonToggled()

        if not image.is_reviewed:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

    def toggleImageReviewed(self):
        item = self.list_images.currentItem()
        image = item.getImage()

        if item:
            font = item.font()
            image.is_reviewed = True
            if not font.bold():
                image.is_reviewed = False
            image.save()
            font.setBold(not font.bold())
            item.setFont(font)

        self.list_images.setFocus()
        self.updateList()

    def markImageAsReviewed(self):
        item = self.list_images.currentItem()
        image = item.getImage()

        if item:
            image.is_reviewed = True
            image.save()
            font = item.font()
            font.setBold(False)
            item.setFont(font)

    def updateList(self):
        current_button = self.image_status_buttons.checkedButton()
        current_button.click()

    def addImage(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select images", ".", "Images (*.jpg)")[0]
        for path in paths:
            image = processNewImage(path, self.currentFlight)
            self.notifyObservers("IMAGE_ADDED", None, image)

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.image_list_item_dict[image] = item
        if not image.is_reviewed:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)
        self.list_images.addItem(item)
        
    def goToImage(self, selected_image):
        item = self.image_list_item_dict.get(selected_image)
        if item:
            item_row = self.list_images.row(item)
            self.list_images.setCurrentRow(item_row)
            self.list_images.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtCenter)

    def currentImageChanged(self, current, _):
        # Clear the scene
        self.deleteMarkersFromUi()

        # update current image
        self.currentImage = current.getImage()
        self.viewer_single.getScale().setCurrentImage(self.currentImage)

        # refresh image reviewed/not reviewed state
        self.updateImageList()

        # attempt to refresh tag counts
        update_num_occurrences()
        for tag in get_all_tags():
            self.updateTagMarkerCountInUi(tag)
            
        # update widgets
        self.minimap.updateContourOnImageChange(self.currentImage)
        self.openImage('./flights/{}/{}'.format(self.currentFlight.img_path, self.currentImage.filename), self.viewer_single)

        self.notifyObservers("CURRENT_IMG_CHANGED", None, None)

        # udpate scale
        self.viewer_single.updateScale()

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
        for row_num in range(self.list_images.count()):
            self.list_images.item(row_num).setHidden(False)

    def reviewedButtonToggled(self):
        for image, item in self.image_list_item_dict.iteritems():
            item_row = self.list_images.row(item)
            if image.is_reviewed:
                self.list_images.item(item_row).setHidden(False)
            else:
                self.list_images.item(item_row).setHidden(True)

    def notReviewedButtonToggled(self):
        for image, item in self.image_list_item_dict.iteritems():
            item_row = self.list_images.row(item)
            if not image.is_reviewed:
                self.list_images.item(item_row).setHidden(False)
            else:
                self.list_images.item(item_row).setHidden(True)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def previousImage(self):
        next_row = self.list_images.currentRow() - 1
        self.setImageRow(next_row)

    def nextImage(self):
        next_row = self.list_images.currentRow() + 1
        self.setImageRow(next_row)

    def setImageRow(self, row):
        if 0 <= row < self.list_images.count():
            self.list_images.setCurrentRow(row)

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
            top_left_pixel = QtCore.QPoint(0,0)
            bottom_right_pixel = QtCore.QPoint(image.width, image.height)
            if self.isMarkerInBounds(m, top_left_pixel, bottom_right_pixel):
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
        self.tagging_tab_context_menu.clearTagContextMenu() # clear tags from the context menu

        # clear all markers
        self.deleteMarkersFromUi()

        # reset area map
        self.minimap.reset()

        # clear the photo viewer
        self.viewer_single.setPhoto(None)

    def updateOnResize(self):
        self.viewer_single.fitInView()
        self.minimap.fitInView()
        self.minimap.updateContour(self.currentImage)

    def disableCurrentImageChangedEvent(self):
        self.list_images.currentItemChanged.disconnect(self.currentImageChanged)

    def enableCurrentItemChangedEvent(self):
        self.list_images.currentItemChanged.connect(self.currentImageChanged)

    def saveImage(self):
        scene_width = self.viewer_single.viewport().rect().width()
        scene_height = self.viewer_single.viewport().rect().height()
        imageTopLeftPixel = self.viewer_single.mapToScene(0, 0) # Currently displayed top left pixel
        imageBottomRightPixel = self.viewer_single.mapToScene(scene_width, scene_height) # Currently displayed bottom right pixel
        if self.currentImage != None:
            flight_root = FLIGHT_DIRECTORY + '{}'.format(self.currentFlight.img_path)
            image_path = flight_root + '/{}'.format(self.currentImage.filename)
            pixmap = QPixmap(image_path)
            fileSaveDialog = QtWidgets.QFileDialog()
            fileSaveDialog.setWindowTitle('Save Image')
            savedImagesPath = FLIGHT_DIRECTORY + '{}/saved-images'.format(self.currentFlight.img_path)
            if not os.path.exists(savedImagesPath):
                os.makedirs(savedImagesPath)
            fileSaveDialog.setDirectory(savedImagesPath)
            fileSaveDialog.selectFile(self.generateFilenameForSavedImage(imageTopLeftPixel, imageBottomRightPixel))
            fileSaveDialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
            fileSaveDialog.setNameFilter('Images (*.png)')
            fileSaveDialog.setDefaultSuffix('.png')
            if fileSaveDialog.exec_() == QtWidgets.QFileDialog.Accepted:
                target_filepath = fileSaveDialog.selectedFiles()[0]
                if self.viewer_single.zoomFactor() == 0: # This means that the image is fully zoomed out
                    pixmap.save(target_filepath, format='png', quality=100)
                    self.viewer_single.getScale().paintScaleOnSavedImage(savedImagesPath, GetDirectoryAndFilenameFromFullPath(target_filepath)[1])
                else:
                    save_image_width = imageBottomRightPixel.x() - imageTopLeftPixel.x()
                    save_image_height = imageBottomRightPixel.y() - imageTopLeftPixel.y()
                    cropping_rect = QRect(imageTopLeftPixel.x(), imageTopLeftPixel.y(), \
                                          save_image_width, save_image_height)
                    cropped_pixmap = pixmap.copy(cropping_rect)
                    cropped_pixmap.save(target_filepath, format='png', quality=100)
                    self.viewer_single.getScale().paintScaleOnSavedImage(savedImagesPath, GetDirectoryAndFilenameFromFullPath(target_filepath)[1], cropping_rect)

    def generateFilenameForSavedImage(self, top_left_pixel, bottom_right_pixel):
        tags = {}
        markers = self.getMarkersInFrame(top_left_pixel, bottom_right_pixel)
        for m in markers:
            tag = m.tag
            type_subtype = '{}_{}'.format(tag.type, tag.subtype)
            if tags.has_key(type_subtype):
                tags[type_subtype] += 1
            else:
                tags[type_subtype] = 1

        save_image_name = ''
        for key, count in tags.iteritems():
            save_image_name += key + '_' + str(count) + '_'
        save_image_name += self.currentImage.filename.split('.')[0]
        print save_image_name

        return save_image_name

    def getMarkersInFrame(self, top_left_pixel, bottom_right_pixel):
        _list = []

        for m in Marker.objects.filter(image__flight=self.currentFlight):
            if self.isMarkerInBounds(m, top_left_pixel, bottom_right_pixel):
                _list.append(m)

        return _list

    def isMarkerInBounds(self, marker, top_left_pixel, bottom_right_pixel):
        image = self.currentImage
        image_bounds = getFrameBounds(image, self.currentFlight.reference_altitude, top_left_pixel=top_left_pixel,
                                      bottom_right_pixel=bottom_right_pixel)

        marker_loc = Point(marker.latitude, marker.longitude)

        if image_bounds.isPointInsideBounds(marker_loc):
            return True
        return False
