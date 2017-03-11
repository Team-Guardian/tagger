from PyQt5.QtWidgets import QTableWidgetItem

class TagTableItem(QTableWidgetItem):
    def __init__(self, label, tag):
        super(TagTableItem, self).__init__()
        self.tag = None

        self.setText(label)
        self.setTag(tag)

    def getTag(self):
        return self.tag

    def setTag(self, tag):
        self.tag = tag