from PyQt5 import QtWidgets

from ui.ui_targetsTab import Ui_TargetsTab
from db.dbHelper import *
from gui.tagListItem import TagListItem
from gui.imageListItem import ImageListItem

class TargetsTab(QtWidgets.QWidget, Ui_TargetsTab):
    def __init__(self):
        super(TargetsTab, self).__init__()
        self.setupUi(self)

        self.tag_list_item_dict = {}
        self.image_list_item_dict = {}

        self.list_tags.currentItemChanged.connect(self.currentTagChanged)
        self.list_taggedImages.currentItemChanged.connect(self.currentImageChanged)

    def addTagToUi(self, tag):
        tag_name = '{}, {}'.format(tag.type, tag.subtype)
        list_item = TagListItem(tag_name, tag)
        self.list_tags.addItem(list_item)
        self.tag_list_item_dict[tag] = list_item

    def addImageToUi(self, image):
        item = ImageListItem(image.filename, image)
        self.list_taggedImages.addItem(item)
        self.image_list_item_dict[image] = item

    def currentTagChanged(self, current, _):
        current_tag = current.getTag()
        self.sortImages(current_tag)

    def currentImageChanged(self):
        pass

    def sortImages(self, current_tag):
        for marker in Marker.objects.filter(tag=current_tag):
            marked_image = marker.image
            for image, item in self.image_list_item_dict.iteritems():
                item_row = self.list_taggedImages.row(item)
                if image == marked_image:
                    self.list_taggedImages.item(item_row).setHidden(False)
                else:
                    self.list_taggedImages.item(item_row).setHidden(True)

    def resetTab(self):
        pass # TODO