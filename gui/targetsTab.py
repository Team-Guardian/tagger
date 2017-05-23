from PyQt5 import QtWidgets, QtGui, QtCore

from ui.ui_targetsTab import Ui_TargetsTab
from observer import Observer
from db.dbHelper import *
from db.models import Image
from gui.tagListItem import TagListItem
from gui.imageListItem import ImageListItem
from gui.targetContextMenu import TargetContextMenu
from utils.geographicUtilities import exportAllTelemetry
from utils.imageInfo import FLIGHT_DIRECTORY
from utils.geographicUtilities import getFrameBounds, Point


TAB_INDICES = {'TAB_SETUP': 0, 'TAB_TAGGING': 1, 'TAB_TARGETS': 2, 'TAB_MAP': 3}

class TargetsTab(QtWidgets.QWidget, Ui_TargetsTab, Observer):
    def __init__(self):
        super(TargetsTab, self).__init__()
        Observer.__init__(self)

        self.setupUi(self)
        self.connectButtons()

        self.current_flight = None
        self.current_image = None
        self.current_tag = None

        self.tag_list_item_dict = {}
        self.image_list_item_dict = {}

        self.targets_tab_context_menu = TargetContextMenu()
        self.viewer_targets._photo.setTabContextMenu(self.targets_tab_context_menu)
        self.button_exportTelemetry.clicked.connect(self.exportTelemetry)

    @QtCore.pyqtSlot(Image)
    def processNewImage(self, image):
        self.addImageToUi(image)

    @QtCore.pyqtSlot(Tag)
    def processTagCreated(self, new_tag):
        self.addTagToUi(new_tag)

    @QtCore.pyqtSlot(Tag)
    def processTagEdited(self, edited_tag):
        edited_tag_list_item = self.tag_list_item_dict.get(edited_tag)
        tag_name = '{}, {}'.format(edited_tag.type, edited_tag.subtype)
        edited_tag_list_item.setText(tag_name)
        self.list_tags.editItem(edited_tag_list_item)

    @QtCore.pyqtSlot(Tag)
    def processTagDeleted(self, deleted_tag):
        deleted_tag_list_item = self.tag_list_item_dict.get(deleted_tag)
        deleted_tag_list_item_row = self.list_tags.row(deleted_tag_list_item)
        self.list_tags.takeItem(deleted_tag_list_item_row)
        self.changeCurrentTagItemAfterTagDelete(deleted_tag_list_item_row)
        del self.tag_list_item_dict[deleted_tag]

    @QtCore.pyqtSlot()
    def processGoToImageInTaggingTab(self):
        main_window = QtWidgets.QApplication.activeWindow()
        main_window.taggingTab.goToImage(self.current_image)
        main_window.ui.tabWidget.setCurrentIndex(TAB_INDICES['TAB_TAGGING'])

    @QtCore.pyqtSlot(Tag)
    def processMarkerCreated(self, new_marker):
        markers_tag = new_marker.tag
        if self.current_tag == markers_tag:
            self.filterImages(markers_tag)

    @QtCore.pyqtSlot(Tag)
    def processMarkerDeleted(self, deleted_marker):
        markers_tag = deleted_marker.tag
        if self.current_tag == markers_tag:
            self.filterImages(markers_tag)

    def changeCurrentTagItemAfterTagDelete(self, deleted_row_num):
        if deleted_row_num == self.list_tags.count():
            self.list_tags.setCurrentRow(deleted_row_num - 1)
        else:
            self.list_tags.setCurrentRow(deleted_row_num)

    def connectButtons(self):
        self.list_tags.currentItemChanged.connect(self.currentTagChanged)
        self.list_taggedImages.currentItemChanged.connect(self.currentImageChanged)

    def addTagToUi(self, tag):
        tag_name = '{}, {}'.format(tag.type, tag.subtype)
        tag_list_item = TagListItem(tag_name, tag)
        self.list_tags.addItem(tag_list_item)
        self.tag_list_item_dict[tag] = tag_list_item

    def addImageToUi(self, image):
        image_list_item = ImageListItem(image.filename, image)
        self.list_taggedImages.addItem(image_list_item)
        # hide the item after it has been added to the list
        item_row = self.list_taggedImages.row(image_list_item)
        self.list_taggedImages.item(item_row).setHidden(True)
        self.image_list_item_dict[image] = image_list_item

    def hideAllImageListItems(self):
        for image, item in self.image_list_item_dict.iteritems():
            item_row = self.list_taggedImages.row(item)
            self.list_taggedImages.item(item_row).setHidden(True)

    def currentTagChanged(self, current, _):
        if current is not None:
            self.current_tag = current.getTag()
            # visually shows that a current item has been selected when the tab was switched
            self.list_tags.setCurrentRow(self.list_tags.row(current))
            self.filterImages(self.current_tag)
        else:
            self.hideAllImageListItems()

    def currentImageChanged(self, current, _):
        self.current_image = current.getImage()
        self.openImage(FLIGHT_DIRECTORY + '{}/{}'.format(self.current_flight.img_path, self.current_image.filename))

    def openImage(self, path):
        self.viewer_targets.setPhoto(QtGui.QPixmap(path))

    def filterImages(self, tag):
        self.hideAllImageListItems()
        if Marker.objects.filter(tag=tag).exists():
            for marker in Marker.objects.filter(tag=tag):
                p = Point(marker.latitude, marker.longitude)
                for i in range(self.list_taggedImages.count()):
                    item = self.list_taggedImages.item(i)
                    img = item.getImage()
                    bounds = getFrameBounds(img, self.current_flight.reference_altitude)
                    if bounds.isPointInsideBounds(p):
                        item.setHidden(False)

                # marked_image = marker.image
                # for image, item in self.image_list_item_dict.iteritems():
                #     item_row = self.list_taggedImages.row(item)
                #     if image == marked_image:
                #         self.list_taggedImages.item(item_row).setHidden(False)

    def getCurrentImage(self):
        return self.current_image

    def getCurrentFlight(self):
        return self.current_flight

    def disableCurrentImageChangedEvent(self):
        self.list_taggedImages.currentItemChanged.disconnect(self.currentImageChanged)

    def enableCurrentItemChangedEvent(self):
        self.list_taggedImages.currentItemChanged.connect(self.currentImageChanged)

    def setContextMenu(self):
        self.targets_tab_context_menu.setTargetContextMenu()

    def resetTab(self):
        self.tag_list_item_dict = {}
        self.image_list_item_dict = {}

        self.targets_tab_context_menu.clearTargetContextMenu()

        self.disableCurrentImageChangedEvent()  # disconnect signal to avoid triggering an event
        self.list_taggedImages.clear()
        self.list_tags.clear()
        self.enableCurrentItemChangedEvent()  # re-enable the event

    def updateOnResize(self):
        self.viewer_targets.fitInView()

    def exportTelemetry(self):
        filename = FLIGHT_DIRECTORY + '{}/{}'.format(self.current_flight.img_path, "gps.csv")
        exportAllTelemetry(self.current_flight, filename)
