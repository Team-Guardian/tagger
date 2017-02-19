import sys
from PyQt5 import QtWidgets

from db.dbHelper import *
from gui.mainWindow import MainWindow

class Controller(object):
    def __init__(self):
        super(Controller, self).__init__()
        self.tags = get_all_tags()
        self.images = get_all_images()
        self.markers = []

        self.window = MainWindow()
        self.window.show()
        self.window.addObserver(self)

        # populate lists
        for tag in self.tags:
            self.window.taggingTab.addTagToUi(tag)

        for image in self.images:
            self.window.taggingTab.addImageToUi(image)

        print 'breakpoint'

    def notify(self, event, id, data):
        if event is "TAG_CREATED":
            self.tags.append(data)
        elif event is "TAG_EDITED":
            tag = self.tags[id]
            tag.type = data.type
            tag.subtype = data.subtype
            tag.symbol = data.symbol
            tag.num_occurrences = data.num_occurrences
            tag.save()
        elif event is "TAG_DELETED":
            tag = self.tags.pop(id)
            tag.delete()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())