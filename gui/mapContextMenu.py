from PyQt5 import QtWidgets

class MapContextMenu(QtWidgets.QMenu):
    def __init__(self, parent=None, title=""):
        super(MapContextMenu, self).__init__(parent)

        # add actions to the context menu
        self.find_images_containing_point = self.addAction("Find images containing this point")
        self.addSeparator()
        self.copy_pixel_lat_lon = self.addAction("Copy latitude/longitude")
        self.addSeparator()
        self.reset_all_filters = self.addAction("Reset all filters")

        # store pixel position where the context menu was invoked
        self.pixel_x_invocation_coord = None
        self.pixel_y_invocation_coord = None

        # create a tuple of actions and messages
        self.map_action_tuples = []
        self.map_action_tuples.append(("FIND_IMAGES", self.find_images_containing_point))
        self.map_action_tuples.append(("COPY_LAT_LON", self.copy_pixel_lat_lon))
        self.map_action_tuples.append(("RESET_FILTERS", self.reset_all_filters))