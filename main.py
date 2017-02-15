import sys
from PyQt5 import QtWidgets

from db.dbHelper import *
from gui.mainWindow import MainWindow

class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self.tags = {}
        self.images = {}
        self.markers = {}

        self.window = MainWindow()
        self.window.show()

        self.window.addObserver(self)

    def notify(self, source, event, data):
        pass

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())