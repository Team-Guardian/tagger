from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtGui import QIcon, QPixmap
import os


ICON_DIRECTORY = 'gui/pin_markers/'
PLACEHOLDER_MARKER_NAME = '_placeholder_'

class TagDialog(QDialog):
    def __init__(self, parent=None):
        super(TagDialog, self).__init__(parent)

        self.form = QtWidgets.QFormLayout(self)
        self.tagType = QtWidgets.QLineEdit()
        self.form.addRow(QtWidgets.QLabel("Type"), self.tagType)
        self.subtype = QtWidgets.QLineEdit()
        self.form.addRow(QtWidgets.QLabel("Subtype"), self.subtype)

        self.used_marker_icon_list = []
        self.marker_icon_list = []
        for fName in os.listdir(ICON_DIRECTORY):
            if fName.endswith('.png'):
                self.marker_icon_list.append(fName)

        self.icons = QtWidgets.QComboBox()
        for fName in self.marker_icon_list:
            self.icons.addItem(QIcon(ICON_DIRECTORY + fName), fName[:-4])
        self.form.addRow(QtWidgets.QLabel("Icon"), self.icons)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def addIcon(self, icon):
        if icon != PLACEHOLDER_MARKER_NAME:
            self.used_marker_icon_list.remove(icon)
            self.icons.addItem(QIcon(ICON_DIRECTORY + icon), icon)

    def removeIcon(self, icon):
        if icon != PLACEHOLDER_MARKER_NAME:
            for index in range(self.icons.count()):
                if self.icons.itemText(index) == icon:
                    self.icons.removeItem(index)

            self.used_marker_icon_list.append(icon)

