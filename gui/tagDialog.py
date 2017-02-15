from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog, QDialogButtonBox


class TagDialog(QDialog):
    def __init__(self, parent=None, title=""):
        super(TagDialog, self).__init__(parent)

        self.form = QtWidgets.QFormLayout(self)
        self.form.addRow(QtWidgets.QLabel(title))
        self.tagType = QtWidgets.QLineEdit()
        self.form.addRow(QtWidgets.QLabel("Type"), self.tagType)
        self.subtype = QtWidgets.QLineEdit()
        self.form.addRow(QtWidgets.QLabel("Subtype"), self.subtype)
        self.icons = QtWidgets.QComboBox()
        self.icons.addItems(["a", "b", "c"])
        self.form.addRow(QtWidgets.QLabel("Icon"), self.icons)
        self.buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.form.addRow(self.buttons)

        self.buttons.accepted.connect(self.accept)
        self.buttons.rejected.connect(self.reject)