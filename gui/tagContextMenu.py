from PyQt5 import QtWidgets, QtCore


class TagContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, title=""):
        super(TagContextMenu, self).__init__(parent)

        # add default action
        self.defaultActionHandle = self.addAction("(No tags)")
        self.defaultActionHandle.setEnabled(False)
        self.tag_action_tuples = []

    def addTagToContextMenu(self, tag):
        self.tag_action_tuples.append((tag, self.addAction(tag.type + ", " + tag.subtype)))
        if len(self.actions()) > 1:
            self.defaultActionHandle.setVisible(False)

    def updateTagItem(self, _old_tag, _new_tag):
        for i, _data in enumerate(self.tag_action_tuples):
            _tag, _action = _data
            if _tag == _old_tag:
                _action.setText(_new_tag.type + ", " + _new_tag.subtype)
                self.tag_action_tuples.pop(i)
                self.tag_action_tuples.append((_new_tag, _action))

    def removeTagItem(self, _name):
        for action in self.actions():
            if action.text() == _name:
                self.removeAction(action)

        if len(self.actions()) == 1:
            self.defaultActionHandle.setVisible(True)
