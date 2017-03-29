from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QDialogButtonBox
from PyQt5.QtGui import QIcon, QPixmap
import os


iconDirectory = 'gui/star_markers/'
_placeholder_marker_name = '_placeholder_'

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
        for file in os.listdir(iconDirectory):
            if file.endswith('.png'):
                self.marker_icon_list.append(file)

        self.icons = QtWidgets.QComboBox()
        for file in self.marker_icon_list:
            self.icons.addItem(QIcon(iconDirectory + file), file[:-4])
        self.form.addRow(QtWidgets.QLabel("Icon"), self.icons)

        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form.addRow(self.buttons)
        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)

    def addIcon(self, icon):
        if icon != _placeholder_marker_name:
            self.used_marker_icon_list.remove(icon)
            self.icons.addItem(QIcon(iconDirectory + icon), icon)

    def removeIcon(self, icon):
        if icon != _placeholder_marker_name:
            for index in range(self.icons.count()):
                if self.icons.itemText(index) == icon:
                    self.icons.removeItem(index)

            self.used_marker_icon_list.append(icon)

