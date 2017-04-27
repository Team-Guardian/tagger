from PyQt5 import QtWidgets
from ui.ui_targetsTab import Ui_TargetsTab


class TargetsTab(QtWidgets.QWidget, Ui_TargetsTab):
    def __init__(self):
        super(TargetsTab, self).__init__()
        self.setupUi(self)

    def resetTab(self):
        pass # TODO

    def updateOnResize(self):
        self.viewer_targets.fitInView()
        # self.currentImageChanged() # TODO: merge and uncomment