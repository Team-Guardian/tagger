from PyQt5 import QtWidgets
from ui.ui_setupTab import Ui_SetupTab


class SetupTab(QtWidgets.QWidget, Ui_SetupTab):
    def __init__(self):
        super(SetupTab, self).__init__()
        self.setupUi(self)

