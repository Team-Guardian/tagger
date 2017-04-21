from PyQt5 import QtWidgets, QtGui

from ui.ui_targetsTab import Ui_TargetsTab
from observer import Observer
from db.dbHelper import *
from gui.tagListItem import TagListItem
from gui.imageListItem import ImageListItem

TAB_INDICES = {'TAB_SETUP': 0, 'TAB_TAGGING': 1, 'TAB_TARGETS': 2, 'TAB_MAP': 3}

class TargetsTab(QtWidgets.QWidget, Ui_TargetsTab, Observer):
    def __init__(self):
        super(TargetsTab, self).__init__()
        Observer.__init__(self)

        self.setupUi(self)
        self.connectButtons()

        self.current_flight = None
        self.current_image = None

        self.tag_list_item_dict = {}
        self.image_list_item_dict = {}

        self.viewer_targets.getPhotoItem().addObserver(self)

    def notify(self, event, id, data):
        if event is "TAG_CREATED":
            self.addTagToUi(data)
        elif event is "TAG_EDITED":
            edited_tag_list_item = self.tag_list_item_dict.get(data)
            tag_name = '{}, {}'.format(data.type, data.subtype)
            edited_tag_list_item.setText(tag_name)
            self.list_tags.editItem(edited_tag_list_item)
        elif event is "TAG_DELETED":
            deleted_tag_list_item = self.tag_list_item_dict.get(data)
            deleted_tag_list_item_row = self.list_tags.row(deleted_tag_list_item)
            self.list_tags.takeItem(deleted_tag_list_item_row)
            self.changeCurrentTagItemAfterTagDelete(deleted_tag_list_item_row)
            del self.tag_list_item_dict[data]
        elif event is "GO_TO_IMG_IN_TAGGING_TAB":
            main_window = QtWidgets.QApplication.activeWindow()
            main_window.taggingTab.goToImage(self.current_image)
            main_window.ui.tabWidget.setCurrentIndex(TAB_INDICES['TAB_TAGGING'])

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
            current_tag = current.getTag()
            # visually shows that a current item has been selected when the tab was switched
            self.list_tags.setCurrentRow(self.list_tags.row(current))
            self.sortImages(current_tag)
        else:
            self.hideAllImageListItems()

    def currentImageChanged(self, current, _):
        self.current_image = current.getImage()
        self.openImage('./flights/{}/{}'.format(self.current_flight.img_path, self.current_image.filename))

    def openImage(self, path):
        self.viewer_targets.setPhoto(QtGui.QPixmap(path))

    def sortImages(self, current_tag):
        if Marker.objects.filter(tag=current_tag).exists():
            for marker in Marker.objects.filter(tag=current_tag):
                marked_image = marker.image
                for image, item in self.image_list_item_dict.iteritems():
                    item_row = self.list_taggedImages.row(item)
                    if image == marked_image:
                        self.list_taggedImages.item(item_row).setHidden(False)
                    else:
                        self.list_taggedImages.item(item_row).setHidden(True)
        else:
            self.hideAllImageListItems()

    def getCurrentImage(self):
        return self.current_image

    def getCurrentFlight(self):
        return self.current_flight

    def resetTab(self):
        pass # TODO