from PyQt5 import QtWidgets
from ui.ui_mapTab import Ui_MapTab


class MapTab(QtWidgets.QWidget, Ui_MapTab):
    def __init__(self):
        super(MapTab, self).__init__()
        self.setupUi(self)

