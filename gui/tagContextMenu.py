from PyQt5 import QtWidgets, QtCore


class TagContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, title=""):
        super(TagContextMenu, self).__init__(parent)

        # add default action
        self.defaultActionHandle = self.addAction("(No tags)")
        self.defaultActionHandle.setEnabled(False)

    def addTagToContextMenu(self, _name):
        self.addAction(_name)
        if len(self.actions()) > 1:
            self.defaultActionHandle.setVisible(False)

    def updateTagItem(self, _old_name, _new_name):
        for action in self.actions():
            if action.text() == _old_name:
                action.setText(_new_name)

    def removeTagItem(self, _name):
        for action in self.actions():
            if action.text() == _name:
                self.removeAction(action)

        if len(self.actions()) == 1:
            self.defaultActionHandle.setVisible(True)
