import sys
import traceback
from PyQt5 import QtWidgets, QtCore

from db.dbHelper import *
from gui.mainWindow import MainWindow, TAB_INDICES
from watcher import Watcher
from utils.imageInfo import processNewImage

# use this if you want to include modules from a subfolder
import inspect
cmd_subfolder = os.path.realpath(
    os.path.abspath(os.path.join(os.path.split(inspect.getfile(inspect.currentframe()))[0], "../interop/client/")))
if cmd_subfolder not in sys.path:
    sys.path.insert(0, cmd_subfolder)
from interop import client, types


class Controller():
    def __init__(self):
        self.flights = get_all_flights()

        self.interop_client = None
        self.currentFlight = None

        self.imageWatcher = Watcher()
        self.tags = []
        self.images = []

        self.window = MainWindow()
        self.window.show()
        self.imageWatcher.event_handler.setNewImageAddedHandler(self.postNewImageDiscoveredByWatcherSignal)

        # populate lists
        for flight in self.flights.values():
            self.window.setupTab.addFlightToUi(flight)

        # All the signals are connected through the Controller class that acts as a hub

        # from Main Window
        self.window.reset_application_signal.connect(self.processReset)
        self.window.new_image_discovered_by_watcher_signal.connect(self.processNewImageInWatchedFolder,
                                                                     type=QtCore.Qt.QueuedConnection)

        self.window.image_added_signal.connect(self.window.taggingTab.processImageAdded)
        self.window.image_added_signal.connect(self.window.targetsTab.processImageAdded)
        self.window.image_added_signal.connect(self.window.mapTab.processImageAdded)

        # from Setup Tab
        self.window.setupTab.flight_load_signal.connect(self.processFlightLoad)
        self.window.setupTab.flight_create_signal.connect(self.processFlightCreated)

        self.window.setupTab.turn_off_watcher_signal.connect(self.processDisableWatcher)
        self.window.setupTab.turn_on_watcher_signal.connect(self.processEnableWatcher, type=QtCore.Qt.QueuedConnection)

        self.window.setupTab.interop_credentials_entered_signal.connect(self.processInteropCredentialsEntered)
        self.window.setupTab.interop_disable_signal.connect(self.processInteropDisable)

        # from Tagging Tab
        self.window.taggingTab.tagging_tab_context_menu.create_marker_signal.connect(self.window.taggingTab.processCreateMarker)
        self.window.taggingTab.marker_created_signal.connect(self.window.targetsTab.processMarkerCreated)

        self.window.taggingTab.tag_created_signal.connect(self.processTagCreated)
        self.window.taggingTab.tag_created_signal.connect(self.window.targetsTab.processTagCreated)

        self.window.taggingTab.tag_edited_signal.connect(self.window.targetsTab.processTagEdited)

        self.window.taggingTab.tag_deleted_signal.connect(self.window.targetsTab.processTagDeleted)

        self.window.taggingTab.image_manually_added_signal.connect(self.processImageAdded)
        # Note: processTagDeleted in Controller MUST be invoked after all other handlers have finished processing the event
        #       This ensures that the object exists while references are made to it. Registering slots in this order ensures that
        self.window.taggingTab.tag_deleted_signal.connect(self.processTagDeleted)

        # from Targets Tab
        self.window.targetsTab.targets_tab_context_menu.go_to_image_in_tagging_tab_signal.connect(self.window.targetsTab.processGoToImageInTaggingTab)

        # from Map Tab
        self.window.mapTab.map_context_menu.find_images_signal.connect(self.window.mapTab.processFindImages)
        self.window.mapTab.map_context_menu.copy_latitude_longitude_signal.connect(self.window.mapTab.processCopyLatLon)
        self.window.mapTab.map_context_menu.reset_filters_signal.connect(self.window.mapTab.processResetFilters)

    # pseudo-slot since non-QObject types cannot have signals and slots
    def processImageAdded(self, new_image):
        self.images.append(new_image)
        self.window.image_added_signal.emit(new_image)

    # Thread-safe way of notifying the main Qt thread that a watcher discovered a new image
    def postNewImageDiscoveredByWatcherSignal(self, path_to_image):
        self.window.new_image_discovered_by_watcher_signal.emit(path_to_image)

    # Handles image discovered event once the program enters the main thread
    @QtCore.pyqtSlot(str)
    def processNewImageInWatchedFolder(self, path_to_image):
        image = processNewImage(path_to_image, self.currentFlight)
        if image is not None:
            self.processImageAdded(image)

    @QtCore.pyqtSlot(str)
    def processFlightLoad(self, flight_id):
        self.resetWatcher()
        self.window.taggingTab.resetTab()
        self.window.targetsTab.resetTab()
        self.window.mapTab.resetTab()
        self.loadFlight(flight_id)

    @QtCore.pyqtSlot(str, Flight)
    def processFlightCreated(self, flight_id, flight):
        self.flights[flight_id] = flight
        self.window.setupTab.addFlightToUi(flight)
        self.processFlightLoad(flight_id)

    @QtCore.pyqtSlot()
    def processReset(self):
        self.resetWatcher()
        self.window.resetTabs()

    @QtCore.pyqtSlot(Tag)
    def processTagCreated(self, new_tag):
        self.tags.append(new_tag)

    @QtCore.pyqtSlot(Tag)
    def processTagDeleted(self, deleted_tag):
        self.tags.remove(deleted_tag)
        delete_tag(deleted_tag)  # This also deletes all the markers associated with this tag (Cascaded delete)

    @QtCore.pyqtSlot()
    def processEnableWatcher(self):
        if self.currentFlight is not None:
            self.window.setupTab.button_browseWatchDirectory.click()
            self.startWatcher()

    @QtCore.pyqtSlot()
    def processDisableWatcher(self):
        self.resetWatcher()


    @QtCore.pyqtSlot(str, str, str, str)
    def processInteropCredentialsEntered(self, ip_address, port_number, username, password):
        server = '{}:{}'.format(ip_address, port_number)
        self.interop_client = client.Client(server, username, password)
        self.window.taggingTab.interop_enabled = True
        self.window.taggingTab.interop_client = self.interop_client

    @QtCore.pyqtSlot()
    def processInteropDisable(self):
        if self.interop_client is not None:
            # delete the reference to the Client object to "close" the connection
            del self.interop_client

    def loadFlight(self, id): # TODO: this function does more than the name implies
        self.currentFlight = self.flights[id]
        self.startWatcher()
        self.loadTags()
        self.loadMap(self.currentFlight)
        self.window.taggingTab.currentFlight = self.currentFlight
        self.window.mapTab.currentFlight = self.currentFlight
        self.window.targetsTab.current_flight = self.currentFlight
        self.window.targetsTab.setContextMenu()
        self.window.ui.tabWidget.setCurrentIndex(TAB_INDICES['TAB_TAGGING'])
        self.loadImages() # Keep this sequentially after the setCurrentTab call. This is a workaround for a \
                          # Qt bug: https://goo.gl/gWXA9Q

    def startWatcher(self):
        try:
            self.imageWatcher.startWatching(self.currentFlight, self.window.setupTab.line_watchDirectory.text())
        except OSError:
            exception_notification = QtWidgets.QMessageBox()
            exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
            exception_notification.setText('Error: main.py. Invalid watch directory')
            exception_notification.setWindowTitle('Error!')
            exception_notification.setDetailedText('{}'.format(traceback.format_exc()))
            exception_notification.exec_()

    def loadTags(self):
        self.tags = get_all_tags()
        for tag in self.tags:
            self.window.targetsTab.addTagToUi(tag)
            self.window.taggingTab.addTagToUi(tag)

    def loadMap(self, flight):
        self.window.taggingTab.minimap.setMinimap(flight)
        self.window.mapTab.setMap(flight)

    def loadImages(self):
        self.images = get_all_images_for_flight(self.currentFlight)
        for i in self.images:
            self.window.taggingTab.addImageToUi(i)
            self.window.targetsTab.addImageToUi(i)
            self.window.mapTab.addImageToUi(i)

    def resetWatcher(self):
        self.imageWatcher.stopAndReset()

if __name__ == '__main__':

    app = QtWidgets.QApplication(sys.argv)

    controller = Controller()

    sys.exit(app.exec_())