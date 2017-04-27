from PyQt5 import QtWidgets

class MapContextMenu(QtWidgets.QMenu):
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
        self.action_message_dict = {}
        self.action_message_dict[self.find_images_containing_point] = "FIND_IMAGES"
        self.action_message_dict[self.copy_pixel_lat_lon] = "COPY_LAT_LON"
        self.action_message_dict[self.reset_all_filters] = "RESET_FILTERS"

        # create a dictionary of actions and data
        self.action_data_dict = {}
        self.action_data_dict[self.find_images_containing_point] = None
        self.action_data_dict[self.copy_pixel_lat_lon] = None
        self.action_data_dict[self.reset_all_filters] = None