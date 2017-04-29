from PyQt5 import QtWidgets
from db.models import Tag

class TagContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, title=""):
        super(TagContextMenu, self).__init__(parent)

        # add default action
        self.default_action_handle = self.resetAndSetDefaultActionHandle()
        self.action_message_dict = {}
        self.action_data_dict = {}

        self.pixel_x_invocation_coord = None
        self.pixel_y_invocation_coord = None

    def addTagToContextMenu(self, new_tag):
        new_action = self.addAction('{}, {}'.format(new_tag.type, new_tag.subtype))
        self.action_data_dict[new_action] = new_tag
        self.action_message_dict[new_action] = "MARKER_CREATE"
        if len(self.actions()) > 1:
            self.default_action_handle.setVisible(False)

    def updateTagItem(self, tag_to_update):
        for action, tag in self.action_data_dict.iteritems():
            if tag == tag_to_update:
                action.setText('{}, {}'.format(tag.type, tag.subtype))

    def removeTagItem(self, tag_to_remove):
        action_to_remove = None
        for action, tag in self.action_data_dict.iteritems():
            if tag == tag_to_remove:
                action_to_remove = action
        if action_to_remove is not None:
            del self.action_data_dict[action_to_remove]
            del self.action_message_dict[action_to_remove]
            self.removeAction(action_to_remove)

        if len(self.actions()) == 1:
            self.default_action_handle.setVisible(True)

    def update_action_tuples(self):
        updated_action_tuples = []
        self.clearOnUpdate()
        for _tag, _action in self.tag_action_tuples:
            _tag = Tag.objects.get(pk=_tag.pk)
            updated_action_tuples.append((_tag, self.addAction(_tag.type + ", " + _tag.subtype)))
        if len(self.actions()) > 1:
            self.defaultActionHandle.setVisible(False)
        self.tag_action_tuples = updated_action_tuples

    def clearTagContextMenu(self):
        self.clear()
        self.default_action_handle = self.resetAndSetDefaultActionHandle()
        self.action_data_dict = {}
        self.action_message_dict = {}

    def resetAndSetDefaultActionHandle(self):
        default_action_handle = self.addAction("(No tags)")
        default_action_handle.setEnabled(False)
        return default_action_handle

    def synchronizeWithDatabase(self):
        for action, tag in self.action_data_dict.iteritems():
            updated_tag = Tag.objects.get(pk=tag.pk)
            self.action_data_dict[action] = updated_tag

    def exec_(self, position):
        self.synchronizeWithDatabase()
        return super(TagContextMenu, self).exec_(position)
