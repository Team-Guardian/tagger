from PyQt5 import QtWidgets, QtGui, QtCore

from PyQt5.QtWidgets import QDialog

from tagDialog import TagDialog
from tagger import Ui_MainWindow


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectButtons()
        self.ui.viewer_single.viewport().installEventFilter(self)

    def connectButtons(self):
        self.ui.button_addTag.clicked.connect(self.addTag)
        self.ui.button_editTag.clicked.connect(self.editTag)
        self.ui.button_removeTag.clicked.connect(self.removeTag)

        self.ui.list_images.currentItemChanged.connect(self.currentImageChanged)
        self.ui.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.ui.button_previous.clicked.connect(self.previousImage)
        self.ui.button_next.clicked.connect(self.nextImage)

    def addTag(self):
        dialog = TagDialog(title="Create tag")
        if dialog.exec_() == QDialog.Accepted:
            if len(dialog.name.text()) > 0:
                self.ui.list_tags.addItem(dialog.name.text())

    def editTag(self):
        if self.ui.list_tags.currentRow() >= 0:
            item = self.ui.list_tags.currentItem()
            dialog = TagDialog(title="Edit tag")
            dialog.name.setText(item.text())
            if dialog.exec_() == QDialog.Accepted:
                if len(dialog.name.text()) > 0:
                    self.ui.list_tags.currentItem().setText(dialog.name.text())

    def removeTag(self):
        if self.ui.list_tags.currentRow() >= 0:
            self.ui.list_tags.takeItem(self.ui.list_tags.currentRow())

    def toggleImageReviewed(self):
        item = self.ui.list_images.currentItem()
        if item:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

            # image was marked as reviewed
            if not font.bold():
                self.nextImage()

    # opens image an item is clicked in any of the image lists
    # single = tagging tab, targets = target tab, map = map tab
    def currentImageChanged(self, current, _):
        viewer = self.ui.viewer_single
        listName = current.listWidget().objectName()
        if listName == "list_taggedImages":
            viewer = self.ui.viewer_targets
        elif listName == "list_allImages":
            viewer = self.ui.viewer_map

        path = current.text()
        self.openImage(path, viewer)

    def openImage(self, path, viewer):
        viewer.setPhoto(QtGui.QPixmap(path))

    def previousImage(self):
        self.setImageRow(self.ui.list_images.currentRow() - 1)

    def nextImage(self):
        self.setImageRow(self.ui.list_images.currentRow() + 1)

    def setImageRow(self, row):
        if 0 <= row < self.ui.list_images.count():
            self.ui.list_images.setCurrentRow(row)

    # handles events from widgets we have registered with
    # use installEventFilter() on a widget to register
    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and
                source is self.ui.viewer_single.viewport()):
            if event.buttons() == QtCore.Qt.NoButton:
                if not self.ui.viewer_single.isImageNull():
                    point = self.ui.viewer_single.mapToScene(event.pos())
                    self.ui.statusbar.showMessage('x: %d, y: %d' % (round(point.x()), round(point.y())))

        return QtWidgets.QWidget.eventFilter(self, source, event)