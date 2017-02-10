# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from tagger import Ui_MainWindow


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.connectButtons()
        self.ui.viewer_single.viewport().installEventFilter(self)

    def connectButtons(self):
        self.ui.button_addTag.clicked.connect(self.addTag)

        self.ui.list_images.currentItemChanged.connect(self.currentImageChanged)
        self.ui.button_toggleReviewed.clicked.connect(self.toggleImageReviewed)
        self.ui.button_previous.clicked.connect(self.previousImage)
        self.ui.button_next.clicked.connect(self.nextImage)

    def addTag(self):
        dialog = QDialog()
        form = QtWidgets.QFormLayout(dialog)
        form.addRow(QtWidgets.QLabel("Create tag"))
        tagType = QtWidgets.QLineEdit()
        form.addRow(QtWidgets.QLabel("Type"), tagType)
        name = QtWidgets.QLineEdit()
        form.addRow(QtWidgets.QLabel("Name"), name)
        combo = QtWidgets.QComboBox()
        combo.addItems(["a", "b", "c"])
        form.addRow(QtWidgets.QLabel("Icon"), combo)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        form.addRow(buttons)

        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)

        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            if len(name.text()) > 0:
                self.ui.list_tags.addItem(name.text())

    def toggleImageReviewed(self):
        item = self.ui.list_images.currentItem()
        if item:
            font = item.font()
            font.setBold(not font.bold())
            item.setFont(font)

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

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and
                source is self.ui.viewer_single.viewport()):
            if event.buttons() == QtCore.Qt.NoButton:
                if not self.ui.viewer_single.isImageNull():
                    point = self.ui.viewer_single.mapToScene(event.pos())
                    self.ui.statusbar.showMessage('x: %d, y: %d' % (round(point.x()), round(point.y())))

        return QtWidgets.QWidget.eventFilter(self, source, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec_())