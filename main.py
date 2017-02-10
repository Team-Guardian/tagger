# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from tagger import Ui_MainWindow


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.taggableImage.viewport().installEventFilter(self)

    def eventFilter(self, source, event):
        if (event.type() == QtCore.QEvent.MouseMove and
                source is self.ui.taggableImage.viewport()):
            if event.buttons() == QtCore.Qt.NoButton:
                if not self.ui.taggableImage.isImageNull():
                    point = self.ui.taggableImage.mapToScene(event.pos())
                    self.ui.statusbar.showMessage('x: %d, y: %d' % (round(point.x()), round(point.y())))

        return QtWidgets.QWidget.eventFilter(self, source, event)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = Window()
    window.show()

    window.ui.taggableImage.setPhoto(QtGui.QPixmap("20160430_111051_217148.jpg"))

    sys.exit(app.exec_())