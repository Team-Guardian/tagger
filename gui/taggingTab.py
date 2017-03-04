from PyQt5 import QtWidgets, QtGui
from PyQt5.QtWidgets import QDialog, QTableWidgetItem

from ui.ui_taggingTab import Ui_TaggingTab
from tagDialog import TagDialog
from db.dbHelper import *
from observer import *
from utils.imageInfo import loadImageWithExif


class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab, Observable):
    def __init__(self):
        super(TaggingTab, self).__init__()
        Observable.__init__(self)

        self.currentFlight = None

        self.setupUi(self)
        self.connectButtons()

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
                count = "0"
                icon = dialog.icons.currentText()
                t = create_tag(type=tagType, subtype=subtype, symbol=icon, num_occurrences=int(count))
                self.addTagToUi(t)
                self.notifyObservers("TAG_CREATED", -1, t)

    def addTagToUi(self, tag):
        row = self.list_tags.rowCount()
        self.list_tags.insertRow(row)
        # update all columns in row with these texts
        texts = [tag.type, tag.subtype, tag.num_occurrences, tag.symbol]
        [self.list_tags.setItem(row, col, QTableWidgetItem(text)) for col, text in enumerate(texts)]

    def editTag(self):
        row = self.list_tags.currentRow()
        if row >= 0:
            tagType = self.list_tags.item(row, 0).text()
            subtype = self.list_tags.item(row, 1).text()
            count = "0"
            icon = self.list_tags.item(row, 3).text()
            dialog = TagDialog(title="Edit tag")
            dialog.tagType.setText(tagType)
            dialog.subtype.setText(subtype)
            index = dialog.icons.findText(icon)
            dialog.icons.setCurrentIndex(index)
            if dialog.exec_() == QDialog.Accepted:
                if len(dialog.subtype.text()) > 0:
                    tagType = dialog.tagType.text()
                    subtype = dialog.subtype.text()
                    count = "0"
                    icon = dialog.icons.currentText()

                    # update all columns in row with these texts
                    texts = [tagType, subtype, count, icon]
                    [self.list_tags.setItem(row, col, QTableWidgetItem(text)) for col, text in enumerate(texts)]

                    t = Tag(type=tagType, subtype=subtype, symbol=icon, num_occurrences=int(count))
                    self.notifyObservers("TAG_EDITED", row, t)

    def removeTag(self):
        row = self.list_tags.currentRow()
        if row >= 0:
            self.list_tags.removeRow(row)
            self.notifyObservers("TAG_DELETED", row, None)

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
        # TODO: copy image to flight directory
        paths = QtWidgets.QFileDialog.getOpenFileNames(self, "Select images", ".", "Images (*.jpg)")[0]
        for path in paths:
            image = loadImageWithExif(path, self.currentFlight)
            self.addImageToUi(image)
            # TODO: create in DB when create_image() is merged

    def addImageToUi(self, image):
        self.list_images.addItem(image.filename)

    def currentImageChanged(self, current, _):
        path = current.text()
        self.openImage(path, self.viewer_single)
        self.notifyObservers("CURRENT_IMG_CHANGED", None, path)

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
