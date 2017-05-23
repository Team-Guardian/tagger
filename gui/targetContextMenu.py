from PyQt5 import QtCore, QtWidgets

class TargetContextMenu(QtWidgets.QMenu):

    go_to_image_in_tagging_tab_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, title=""):
        super(TargetContextMenu, self).__init__(parent)

        self.pixel_x_invocation_coord = None
        self.pixel_y_invocation_coord = None

        # create a dictionary of actions and messages
        self.action_signal_dict = {}
        self.action_data_dict = {}

    # TODO: what does this function do?
    def setTargetContextMenu(self):
        # add actions to the context menu
        self.go_to_image_in_tagging_tab = self.addAction("Go to image in Tagging Tab")

        # update dictionaries
        self.action_signal_dict[self.go_to_image_in_tagging_tab] = self.go_to_image_in_tagging_tab_signal
        self.action_data_dict[self.go_to_image_in_tagging_tab] = None

    def clearTargetContextMenu(self):
        self.clear()
        self.pixel_x_invocation_coord = None
        self.pixel_x_invocation_coord = None
        self.action_signal_dict = {}
        self.action_data_dict = {}