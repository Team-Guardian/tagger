from PyQt5.QtWidgets import QListWidgetItem

class ImageListItem(QListWidgetItem):
    def __init__(self, label, image):
        super(ImageListItem, self).__init__()
        self.image = None

        self.setText(label)
        self.setImage(image)

    def getImage(self):
        return self.image

    def setImage(self, image):
        self.image = image