from PyQt5 import QtCore, QtWidgets

class MapContextMenu(QtWidgets.QMenu):

    find_images_signal = QtCore.pyqtSignal()
    copy_latitude_longitude_signal = QtCore.pyqtSignal()
    reset_filters_signal = QtCore.pyqtSignal()

    def __init__(self, parent=None, title=""):
        super(MapContextMenu, self).__init__(parent)

        # add actions to the context menu
        self.find_images_containing_point = self.addAction("Find images containing this point")
        self.copy_pixel_lat_lon = self.addAction("Copy latitude/longitude")
        self.reset_all_filters = self.addAction("Reset all filters")

        # store pixel position where the context menu was invoked
        self.pixel_x_invocation_coord = None
        self.pixel_y_invocation_coord = None

        # create a dictionary of actions and messages
        self.action_signal_dict = {}
        self.action_signal_dict[self.find_images_containing_point] = self.find_images_signal
        self.action_signal_dict[self.copy_pixel_lat_lon] = self.copy_latitude_longitude_signal
        self.action_signal_dict[self.reset_all_filters] = self.reset_filters_signal

        # create a dictionary of actions and data
        self.action_data_dict = {}
        self.action_data_dict[self.find_images_containing_point] = None
        self.action_data_dict[self.copy_pixel_lat_lon] = None
        self.action_data_dict[self.reset_all_filters] = None