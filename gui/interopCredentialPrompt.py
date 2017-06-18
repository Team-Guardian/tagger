# Qt library modules
from PyQt5 import QtWidgets, QtCore

# Custom modules
from gui.ui.ui_interopCredentialPrompt import Ui_Dialog

class InteropCredentialPrompt(QtWidgets.QDialog, Ui_Dialog):

    # signals originating from this module
    dialog_accepted = QtCore.pyqtSignal(str, str, str, str)
    dialog_rejected = QtCore.pyqtSignal()

    def __init__(self):
        super(InteropCredentialPrompt, self).__init__()
        self.setupUi(self)

        self.accepted.connect(self.acceptedEventHandler)
        self.rejected.connect(self.rejectedEventHandler)

    def acceptedEventHandler(self):
        self.dialog_accepted.emit(self.lineEdit_ipAddress.text(), self.lineEdit_port.text(),
                                            self.lineEdit_username.text(), self.lineEdit_password.text())

    def rejectedEventHandler(self):
        self.dialog_rejected.emit()