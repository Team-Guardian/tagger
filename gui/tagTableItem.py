from PyQt5.QtWidgets import QTableWidgetItem
from db.models import Tag

class TagTableItem(QTableWidgetItem):
    def __init__(self, label, tag):
        super(TagTableItem, self).__init__()
        self.tag = None

        self.setText(label)
        self.setTag(tag)

    def getTag(self):
        self.synchronizeWithDatabase()
        return self.tag

    def setTag(self, tag):
        self.tag = tag

    def synchronizeWithDatabase(self):
        self.tag = Tag.objects.get(pk=self.tag.pk)