from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QDialog

from ui.ui_taggingTab import Ui_TaggingTab
from tagDialog import TagDialog


class TaggingTab(QtWidgets.QWidget, Ui_TaggingTab):
    def __init__(self):
        super(TaggingTab, self).__init__()

        self.observers = []

        self.setupUi(self)
        self.connectButtons()

    def addObserver(self, observer):
        self.observers.append(observer)

    def notify(self, source, event, data):
        for observer in self.observers:
            observer.notify(source, event, data)

    def connectButtons(self):
        self.button_addTag.clicked.connect(self.addTag)
        self.button_editTag.clicked.connect(self.editTag)
        self.button_removeTag.clicked.connect(self.removeTag)

        self.list_images.currentItemChanged.connect(self.currentImageChanged)
        self.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.button_previous.clicked.connect(self.previousImage)
        self.button_next.clicked.connect(self.nextImage)

    def addTag(self):
        dialog = TagDialog(title="Create tag")
        if dialog.exec_() == QDialog.Accepted:
            if len(dialog.name.text()) > 0:
                self.list_tags.addItem(dialog.name.text())

    def editTag(self):
        if self.list_tags.currentRow() >= 0:
            item = self.list_tags.currentItem()
            dialog = TagDialog(title="Edit tag")
            dialog.name.setText(item.text())
            if dialog.exec_() == QDialog.Accepted:
                if len(dialog.name.text()) > 0:
                    self.list_tags.currentItem().setText(dialog.name.text())

    def removeTag(self):
        if self.list_tags.currentRow() >= 0:
            self.list_tags.takeItem(self.list_tags.currentRow())

    def toggleImageReviewed(self):
        item = self.list_images.currentItem()
        if item:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

            # image was marked as reviewed
            if not font.bold():
                self.nextImage()

    def currentImageChanged(self, current, _):
        path = current.text()
        self.openImage(path, self.viewer_single)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def previousImage(self):
        self.setImageRow(self.list_images.currentRow() - 1)

    def nextImage(self):
        self.setImageRow(self.list_images.currentRow() + 1)

    def setImageRow(self, row):
        if 0 <= row < self.list_images.count():
            self.list_images.setCurrentRow(row)
