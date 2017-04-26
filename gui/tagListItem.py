from PyQt5.QtWidgets import QListWidgetItem

class TagListItem(QListWidgetItem):
    def __init__(self, label, tag):
        super(TagListItem, self).__init__()
        self.tag = None

        self.setText(label)
        self.setTag(tag)

    def getTag(self):
        return self.tag

    def setTag(self, tag):
        self.tag = tag