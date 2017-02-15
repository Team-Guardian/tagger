# StackOverflow post used to receive mouseMove events - http://stackoverflow.com/questions/28080257/how-does-qgraphicsview-receive-mouse-move-events

import sys
from PyQt5 import QtWidgets

from gui.mainWindow import MainWindow

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec_())