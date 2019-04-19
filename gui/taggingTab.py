import traceback
import requests
import json

from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QRect
from .ui.ui_taggingTab import Ui_TaggingTab
from .tagDialog import TagDialog
from db.dbHelper import *
from django.db.models import Min
from gui.interopTargetDialog import InteropTargetDialog
from gui.imageListItem import ImageListItem
from gui.tagTableItem import TagTableItem
from gui.tagContextMenu import TagContextMenu
from .markerItem import MarkerItem
from utils.imageInfo import GetDirectoryAndFilenameFromFullPath, FLIGHT_DIRECTORY
from utils.imageInfo import processNewImage
from utils.geolocate import getPixelFromLatLon
from utils.geographicUtilities import *
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox
# Measuring Shapes
import numpy as np
from numpy import linalg as LA
from .scale import Scale
import logging

# use this if you want to include modules from a subfolder
import inspect
cmd_subfolder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../../interop/client/")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
#from interop import client, types

TAG_TABLE_INDICES = {'TYPE': 0, 'SUBTYPE': 1, 'COUNT': 2, 'SYMBOL': 3}

class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab):

    # signals originating from this module
    tag_created_signal = QtCore.pyqtSignal(Tag)
    tag_edited_signal = QtCore.pyqtSignal(Tag)
    tag_deleted_signal = QtCore.pyqtSignal(Tag)
    current_image_changed_signal = QtCore.pyqtSignal()
    marker_created_signal = QtCore.pyqtSignal(Marker)
    image_manually_added_signal = QtCore.pyqtSignal(Image)
    interop_connection_error_signal = QtCore.pyqtSignal()
    three_points_acquired_signal = QtCore.pyqtSignal()
    circle_points_acquired_signal = QtCore.pyqtSignal()
    trapezoid_points_acquired_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(TaggingTab, self).__init__()

        self.currentFlight = None
        self.currentImage = None

        # target information will be sent to Interop when enabled
        self.interop_enabled = False
        self.interop_is_online = False
        self.interop_client = None

        self.setupUi(self)
        self.connectButtons()
        self.radioButton_allImages.setChecked(True)

        self.image_list_item_dict = {}
        self.tag_dialog = TagDialog()

        self.tagging_tab_context_menu = TagContextMenu()
        self.viewer_single._photo.setTabContextMenu(self.tagging_tab_context_menu)

        # retranslate radio buttons to display image count
        self.all_image_count = 0
        self.reviewed_image_count = 0
        self.not_reviewed_image_count = 0
        self.all_image_current_row = 0
        self.updateRadioButtonLabels()

        self.interop_target_dialog = InteropTargetDialog(self.enableTargetCropping)

        self.measuring_button_clicked = False
        self.num_points_needed = 0
        self.double_click_loc = []
        self.x = Scale()

        self.areaLogFmt = '%(asctime)s: %(levelname)s: %(funcName)s %(message)s'
        self.areaLogDateFmt = '%m/%d/%Y'
        logging.basicConfig(level=logging.DEBUG, filename='./areaLog.log', format=self.areaLogFmt,
                            datefmt=self.areaLogDateFmt)


    def setInteropEnabled(self):
        self.interop_enabled = True

    def setInteropDisabled(self):
        self.interop_enabled = False

    def setInteropOnline(self):
        self.interop_is_online = True

    def setInteropOffline(self):
        self.interop_is_online = False

    def processImageAdded(self, image):
        self.addImageToUi(image)

    def processCreateMarker(self, markers_tag):
        self.addMarker(markers_tag)

    def processMarkerDeleted(self, deleted_marker_item):
        self.viewer_single.getScene().removeItem(deleted_marker_item)
        marker_to_delete = deleted_marker_item.getMarker()
        marker_to_delete.tag.num_occurrences -= 1
        marker_to_delete.tag.save()
        self.updateTagMarkerCountInUi(marker_to_delete.tag)

        if self.interop_enabled:
            if marker_to_delete.interop_id != 0:
                self.interop_client.delete_target(marker_to_delete.interop_id)
        delete_marker(marker_to_delete)

    def processMarkerParentImageChange(self, image_changed_to):
        if image_changed_to in self.image_list_item_dict:
            self.list_images.setCurrentItem(self.image_list_item_dict.get(image_changed_to))

    def updateRadioButtonLabels(self):
        if self.all_image_current_row == 0:
            self.radioButton_allImages.setText('All Images (-/{})'.format(self.all_image_count))
        else:
            self.radioButton_allImages.setText('All Images ({}/{})'.format(self.all_image_current_row, self.all_image_count))
        self.radioButton_reviewed.setText('Reviewed ({})'.format(self.reviewed_image_count))
        self.radioButton_notReviewed.setText('Not Reviewed ({})'.format(self.not_reviewed_image_count))

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

        self.button_circle.clicked.connect(self.circleButtonToggled)
        self.button_parallelogram.clicked.connect(self.threePointShapeButtonToggled)
        self.button_square.clicked.connect(self.threePointShapeButtonToggled)
        self.button_trapezoid.clicked.connect(self.trapezoidButtonToggled)
        self.button_rectangle.clicked.connect(self.threePointShapeButtonToggled)

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
                tag = create_tag(type=tagType, subtype=subtype, symbol=icon, num_occurrences=int(count))
                self.addTagToUi(tag)
                self.tag_created_signal.emit(tag)

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
                    self.tag_edited_signal.emit(tag)
            else:
                self.tag_dialog.removeIcon(icon) # Remove the current symbol if it hasn't been changed

    def removeTag(self):
        if self.list_tags.rowCount() > 0:
            row = self.list_tags.currentRow()
            tag = self.list_tags.item(row, 0).getTag()

            self.attemptToDeleteTargetsFromInterop(tag)

            self.list_tags.removeRow(row)
            self.tagging_tab_context_menu.removeTagItem(tag)
            self.deleteMarkersFromUi(tag=tag)

            self.tag_dialog.addIcon(tag.symbol)
            self.tag_deleted_signal.emit(tag)

    def addMarker(self, tag):
        pu = self.tagging_tab_context_menu.pixel_x_invocation_coord
        pv = self.tagging_tab_context_menu.pixel_y_invocation_coord
        lat, lon = geolocateLatLonFromPixelOnImage(self.currentImage, self.currentFlight.reference_altitude, pu, pv)

        if self.isInteropAvailable():
            self.interop_target_dialog.lineEdit_latitude.setText('{}'.format(lat))
            self.interop_target_dialog.lineEdit_longitude.setText('{}'.format(lon))
            self.interop_target_dialog.setTargetTag(tag)
            self.interop_target_dialog.image_yaw = self.currentImage.yaw
            self.interop_target_dialog.show()
        else:
            # default value used if interop is not enabled; properly posted interop target will never have ID=0
            target_id = 0

            m = create_marker(tag=tag, image=self.currentImage, latitude=lat, longitude=lon, interop_id=target_id)
            m.tag.num_occurrences += 1
            m.tag.save()

            # update the marker count in the table
            self.updateTagMarkerCountInUi(tag)

            self.addMarkerToUi(pu, pv, m, 1.0) # 1.0 means fully opaque for markers created in current image
            self.marker_created_signal.emit(m)

    def processInteropTargetDialogAccepted(self):
        # Generate and post a target object, then extract it's Interop-assined ID
        target_id = self.createAndPostInteropTarget(self.interop_target_dialog.comboBox_targetType.currentText(),
                                                    self.interop_target_dialog.lineEdit_latitude.text(),
                                                    self.interop_target_dialog.lineEdit_longitude.text(),
                                                    self.interop_target_dialog.lineEdit_orientation.text(),
                                                    self.interop_target_dialog.comboBox_shape.currentText(),
                                                    self.interop_target_dialog.comboBox_shapeColor.currentText(),
                                                    self.interop_target_dialog.lineEdit_alphanumeric.text(),
                                                    self.interop_target_dialog.comboBox_alphanumericColor.currentText(),
                                                    self.interop_target_dialog.textEdit_description.toPlainText())

        # createAndPostInteropTarget will return ID = 0
        if target_id != 0:
            self.saveAndPostTargetImage(target_id)

            m = create_marker(tag=self.interop_target_dialog.current_target_tag, image=self.currentImage,
                              latitude=self.interop_target_dialog.lineEdit_latitude.text(),
                              longitude=self.interop_target_dialog.lineEdit_longitude.text(), interop_id=target_id)
            m.tag.num_occurrences += 1
            m.tag.save()

            # update the marker count in the table
            self.updateTagMarkerCountInUi(self.interop_target_dialog.current_target_tag)

            self.addMarkerToUi(self.tagging_tab_context_menu.pixel_x_invocation_coord, self.tagging_tab_context_menu.pixel_y_invocation_coord, m, 1.0) # 1.0 means fully opaque for markers created in current image
            self.marker_created_signal.emit(m)

            # Reset dialog window
            self.interop_target_dialog.reset()

    def processInteropTargetDialogRejected(self):
        if self.viewer_single.crop_enabled:
            self.viewer_single.crop_enabled = False
            self.list_images.setEnabled(True)

        self.interop_target_dialog.reset()

    def enableTargetCropping(self):
        self.viewer_single.crop_enabled = True
        self.interop_target_dialog.hide()
        self.interop_target_dialog.setWindowModality(QtCore.Qt.NonModal)
        self.interop_target_dialog.show()
        self.activateWindow()
        self.list_images.setEnabled(False)

    def disableTargetCropping(self):
        self.viewer_single.crop_enabled = False
        self.interop_target_dialog.hide()
        self.interop_target_dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        self.interop_target_dialog.show()
        self.interop_target_dialog.activateWindow()
        self.list_images.setEnabled(True)

    def processTargetCropped(self, cropped_rect_scene_coords):
        scene_origin_x = cropped_rect_scene_coords.x()
        scene_origin_y = cropped_rect_scene_coords.y()
        scene_width = int(cropped_rect_scene_coords.width())
        scene_height = int(cropped_rect_scene_coords.height())

        # Need to figure out which corner of the rectangle the dragging started from, and convert everything to top-left
        if scene_width < 0:
            scene_origin_x += scene_width
        if scene_height < 0:
            scene_origin_y += scene_height

        integer_cropped_rect_scene_coords = QtCore.QRect(int(scene_origin_x),
                                                         int(scene_origin_y),
                                                         abs(scene_width),
                                                         abs(scene_height))

        self.interop_target_dialog.viewer_target._scene.setSceneRect(QtCore.QRectF(0, 0, abs(scene_width), abs(scene_height)))
        cropped_target_image = self.viewer_single._photo.pixmap().copy(integer_cropped_rect_scene_coords)
        self.interop_target_dialog.setCroppedImage(cropped_target_image)
        self.interop_target_dialog.saveCroppedRect(integer_cropped_rect_scene_coords)
        self.disableTargetCropping()

    def createAndPostInteropTarget(self, target_type, latitude, longitude, orientation, shape, shape_color, alphanumeric, alphanumeric_color, description):
        if target_type == 'emergent':
            interop_target = types.Target(type=target_type,
                                           latitude=latitude,
                                           longitude=longitude,
                                           description=description)
        else:
            interop_target = types.Target(type=target_type,
                                           latitude=latitude,
                                           longitude=longitude,
                                           orientation=orientation,
                                           shape=shape,
                                           background_color=shape_color,
                                           alphanumeric=alphanumeric,
                                           alphanumeric_color=alphanumeric_color)

        if self.isInteropAvailable():
            try:
                interop_target = self.interop_client.post_target(interop_target)
                return interop_target.id
            except requests.ConnectionError:
                # Notify the user of dropped connection
                exception_notification = QtWidgets.QMessageBox()
                exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
                exception_notification.setText('Error: taggingTab.py. Cannot connect to server. Target was not posted. Reconnect manually')
                exception_notification.setWindowTitle('Error!')
                exception_notification.exec_()

                # Trigger clean disconnect routine
                self.interop_connection_error_signal.emit()

                return 0

    def saveAndPostTargetImage(self, interop_target_id):
        flight_root = QtCore.QDir(FLIGHT_DIRECTORY + '{}'.format(self.currentFlight.img_path))
        flight_root.makeAbsolute()
        abs_flight_root = flight_root
        abs_image_path = QtCore.QDir('{}/{}'.format(abs_flight_root.path(), self.currentImage.filename))
        original_pixmap = QPixmap(abs_image_path.path())
        cropped_pixmap = original_pixmap.copy(self.interop_target_dialog.current_target_cropped_rect)

        target_save_path = QtCore.QDir('{}/interop-targets/temp'.format(abs_flight_root.path()))

        if self.isInteropAvailable():
            # set path where cropped images of targets will be saved
            target_save_path = QtCore.QDir('{}/interop-targets'.format(abs_flight_root.path()))

        if not QtCore.QDir(target_save_path.path()).exists():
            target_save_path.mkpath(target_save_path.path()) # only an instance of QDir can create paths

        target_image_filepath = QtCore.QDir('{}/{}'.format(target_save_path.path(), interop_target_id))

        cropped_pixmap.save(target_image_filepath.path(), format='jpg', quality=100)

        # Open target image
        with open(target_image_filepath.path(), 'rb') as f:
            image_data = f.read()

        if self.isInteropAvailable():
            try:
                self.interop_client.post_target_image(interop_target_id, image_data)
            except requests.ConnectionError:
                # Delete interop target
                if self.interop_client is not None:
                    self.interop_client.delete_target(interop_target_id)

                # Notify the user of dropped connection
                exception_notification = QtWidgets.QMessageBox()
                exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
                exception_notification.setText('Error: taggingTab.py. Cannot connect to server. Target was not posted. Reconnect manually')
                exception_notification.setWindowTitle('Error!')
                exception_notification.exec_()

                # Trigger clean disconnect routine
                self.interop_connection_error_signal.emit()

    def addMarkerToUi(self, x, y, marker, opacity):
        # Create MarkerItem
        image_width = self.currentImage.width
        initial_zoom = self.viewer_single.zoomFactor()
        marker = MarkerItem(marker, current_image=self.currentImage, initial_zoom=initial_zoom)

        # connect signals to handlers; signals are deleted when object is deleted
        marker.setMarkerDeletedHandler(self.processMarkerDeleted)
        marker.setMarkerParentImageChangeHandler(self.processMarkerParentImageChange)

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
        sceneObjects = list(self.viewer_single.getScene().items())
        for item in sceneObjects:
            if type(item) is MarkerItem:
                if tag != None:
                    if item.getMarker().tag == tag:
                        self.viewer_single.getScene().removeItem(item)
                        marker_to_delete_from_ui = item.getMarker()
                        marker_to_delete_from_ui.tag.num_occurrences -= 1
                        marker_to_delete_from_ui.tag.save()
                else:
                    self.viewer_single.getScene().removeItem(item)

    def attemptToDeleteTargetsFromInterop(self, target_tag):
        markers_pending_delete = list(Marker.objects.filter(tag=target_tag))
        for marker in markers_pending_delete:
            if self.isInteropAvailable():
                try:
                    self.interop_client.delete_target(marker.interop_id)
                except requests.ConnectionError:
                    # Notify the user of dropped connection
                    exception_notification = QtWidgets.QMessageBox()
                    exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
                    exception_notification.setText('Error: taggingTab.py. Cannot connect to server. Target was not deleted. Reconnect manually')
                    exception_notification.setWindowTitle('Error!')
                    exception_notification.exec_()

    def isInteropAvailable(self):
        return (self.interop_client is not None and self.interop_enabled and self.interop_is_online)

    def updateImageList(self):
        for row_num in range(self.list_images.count()):
            item = self.list_images.item(row_num)
            image = item.getImage()

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

    def toggleImageReviewed(self):
        item = self.list_images.currentItem()

        try:
            image = item.getImage()
        except AttributeError:
            exception_notification = QtWidgets.QMessageBox()
            exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
            exception_notification.setText('Error: taggingTab.py. No image selected')
            exception_notification.setWindowTitle('Error!')
            exception_notification.setDetailedText('{}'.format(traceback.format_exc()))
            exception_notification.exec_()
            return

        if item:
            list_item_font = item.font()
            if image.is_reviewed:
                image.is_reviewed = False
                self.not_reviewed_image_count += 1
                self.reviewed_image_count -= 1
                self.updateRadioButtonLabels()
                list_item_font.setBold(True)
            elif not image.is_reviewed:
                image.is_reviewed = True
                self.not_reviewed_image_count -= 1
                self.reviewed_image_count += 1
                self.updateRadioButtonLabels()
                list_item_font.setBold(False)
            image.save()
            item.setFont(list_item_font)

        self.list_images.setFocus()
        self.updateList()

    def markImageAsReviewed(self):
        item = self.list_images.currentItem()
        image = item.getImage()

        if item:
            if not image.is_reviewed:
                image.is_reviewed = True
                self.reviewed_image_count += 1
                self.not_reviewed_image_count -= 1
                image.save()
                font = item.font()
                font.setBold(False)
                item.setFont(font)

        self.updateRadioButtonLabels()

    def updateList(self):
        current_button = self.image_status_buttons.checkedButton()
        current_button.click()

    def addImage(self):
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select images", ".", "Images (*.jpg)")[0]
        for path in paths:
            image = processNewImage(path, self.currentFlight)
            if image is not None:
                self.image_manually_added_signal.emit(image)

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.image_list_item_dict[image] = item
        font = item.font()
        if not image.is_reviewed:
            font.setBold(True)
            self.not_reviewed_image_count += 1
        elif image.is_reviewed:
            font.setBold(False)
            self.reviewed_image_count += 1
        item.setFont(font)
        self.list_images.addItem(item)
        self.all_image_count += 1
        self.updateRadioButtonLabels()

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

        self.all_image_current_row = self.list_images.currentRow() + 1
        self.updateRadioButtonLabels()

        # refresh image reviewed/not reviewed state
        self.updateImageList()
            
        # update widgets
        self.minimap.updateContour(self.currentImage)
        self.openImage('./flights/{}/{}'.format(self.currentFlight.img_path, self.currentImage.filename), self.viewer_single)

        self.current_image_changed_signal.emit()

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
        for image, item in self.image_list_item_dict.items():
            item_row = self.list_images.row(item)
            if image.is_reviewed:
                self.list_images.item(item_row).setHidden(False)
            else:
                self.list_images.item(item_row).setHidden(True)

    def notReviewedButtonToggled(self):
        for image, item in self.image_list_item_dict.items():
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

        # reset image count
        self.all_image_count = 0
        self.reviewed_image_count = 0
        self.not_reviewed_image_count = 0
        self.all_image_current_row = 0
        self.updateRadioButtonLabels()

    def updateOnResize(self):
        self.viewer_single.fitInView()
        self.minimap.refresh(self.currentImage)

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
            if type_subtype in tags:
                tags[type_subtype] += 1
            else:
                tags[type_subtype] = 1

        save_image_name = ''
        for key, count in tags.items():
            save_image_name += key + '_' + str(count) + '_'
        save_image_name += self.currentImage.filename.split('.')[0]
        print(save_image_name)

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

    def setButtonsDisabled(self):
        self.button_rectangle.setEnabled(False)
        self.button_square.setEnabled(False)
        self.button_parallelogram.setEnabled(False)
        self.button_circle.setEnabled(False)
        self.button_trapezoid.setEnabled(False)

    def setButtonsEnabled(self):
        self.button_rectangle.setEnabled(True)
        self.button_parallelogram.setEnabled(True)
        self.button_square.setEnabled(True)
        self.button_circle.setEnabled(True)
        self.button_trapezoid.setEnabled(True)

    def threePointShapeButtonToggled(self):
        if self.measuring_button_clicked == False:
            self.measuring_button_clicked = True
            self.setButtonsDisabled()
            self.num_points_needed = 3
            self.double_click_loc[:] = []
            self.double_click_loc.append([])
            self.double_click_loc.append([])
            self.double_click_loc.append([])

        else:
            self.measuring_button_clicked = False
            self.num_points_needed = 0
            self.double_click_loc[:] = []

    def circleButtonToggled(self):
        if self.measuring_button_clicked == False:
            self.measuring_button_clicked = True
            self.setButtonsDisabled()
            self.num_points_needed = 2
            self.double_click_loc[:] = []
            self.double_click_loc.append([])
            self.double_click_loc.append([])

        else:
            self.measuring_button_clicked = False
            self.num_points_needed = 0
            self.double_click_loc[:] = []

    def trapezoidButtonToggled(self):
        if self.measuring_button_clicked == False:
            self.measuring_button_clicked = True
            self.setButtonsDisabled()
            self.num_points_needed = 6
            self.double_click_loc[:] = []
            self.double_click_loc.append([])
            self.double_click_loc.append([])
            self.double_click_loc.append([])
            self.double_click_loc.append([])
            self.double_click_loc.append([])
            self.double_click_loc.append([])


        else:
            self.measuring_button_clicked = False
            self.num_points_needed = 0
            self.double_click_loc[:] = []


    def measureCrossProduct(self):

        P12 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[0][0], 0,
                                                        self.double_click_loc[1][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[0][1], 0,
                                                        self.double_click_loc[1][1])]
        P13 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[1][0], 0,
                                                        self.double_click_loc[2][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[1][1], 0,
                                                        self.double_click_loc[2][1])]

        crossProduct = np.cross(P12, P13)
        area = np.around(LA.norm(crossProduct), decimals=3)

        QMessageBox.about(self, 'Cross Product Result', f'Area: \n{area} m.\n')


        self.measuring_button_clicked = False
        self.setButtonsEnabled()

        logging.info(f'\nfilename: {self.currentImage.filename}'
                     '\nCross Product Area\n'f'Area: \n{area} m^2\n\n')


    def measureCircle(self):

        P12 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[0][0], 0,
                                                        self.double_click_loc[1][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[0][1], 0,
                                                        self.double_click_loc[1][1])]

        diameter = np.around(LA.norm(P12), decimals=3)
        area = np.around((3.14/4)*(diameter*diameter), decimals=3)
        circumference = np.around((3.14*diameter), decimals=3)

        QMessageBox.about(self, 'Circle Shape Result', f'Diameter: \n{diameter} m.\n 'f'Area: \n{area} m^2.\n'
                                                       f'Circumference: \n{circumference} m.')


        self.measuring_button_clicked = False
        self.setButtonsEnabled()

        logging.info(f'\nfilename: {self.currentImage.filename}'
                     '\nCircle Area\n'f'Diameter: \n{diameter} m\n'f'Area: \n{area} m^2\n'
                     f'Circumference: \n{circumference} m\n\n')


    def measureTrapezoid(self):

        P12 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[0][0], 0,
                                                        self.double_click_loc[1][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[0][1], 0,
                                                        self.double_click_loc[1][1])]


        P34 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[2][0], 0,
                                                        self.double_click_loc[3][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[2][1], 0,
                                                        self.double_click_loc[3][1])]


        P56 = [Scale.distanceBetweenGeodeticCoordinates(self.x, self.double_click_loc[4][0], 0,
                                                        self.double_click_loc[5][0], 0),
               Scale.distanceBetweenGeodeticCoordinates(self.x, 0, self.double_click_loc[4][1], 0,
                                                        self.double_click_loc[5][1])]

        first_side = np.around(LA.norm(P12), decimals=3)
        second_side = np.around(LA.norm(P34), decimals=3)
        height = np.around(LA.norm(P56), decimals=3)

        area = np.around(0.5*(first_side + second_side)*height, decimals=3)

        QMessageBox.about(self, 'Trapezoid Area Result', f'Area of Trapezoid is \n{area} m^2.\n'
                          f'Length of first side is \n{first_side} m.\n'
                          f'Length of second side is \n{second_side} m.\n'
                          f'Height is \n{height} m.')



        self.measuring_button_clicked = False
        self.setButtonsEnabled()

        logging.info(f'\nfilename: {self.currentImage.filename}'
                     '\nTrapezoid Area\n' f'Length of first side is \n{first_side} m\n'
                     f'Length of second side is \n{second_side} m\n'
                     f'Height is \n{height} m\n'f'Area: \n{area} m^2\n\n')





