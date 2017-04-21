from PyQt5 import QtWidgets

class TargetContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, title=""):
        super(TargetContextMenu, self).__init__(parent)

        # add actions to the context menu
        self.go_to_image_in_tagging_tab = self.addAction("Go to image in Tagging Tab")

        # create a dictionary of actions and messages
        self.target_action_dict = {}
        self.target_action_dict[self.go_to_image_in_tagging_tab] = "GO_TO_IMG_IN_TAGGING_TAB"