# Man pages references: http://doc.qt.io/qt-4.8/qfiledialog.html#getOpenFileName

# Qt library modules
from PyQt5.QtCore import QDate

# Custom modules
from ui.ui_setupTab import Ui_SetupTab
from interopCredentialPrompt import InteropCredentialPrompt
from utils.imageInfo import *
from db.dbHelper import *

class SetupTab(QtWidgets.QWidget, Ui_SetupTab):

    # signals originating from this module
    flight_load_signal = QtCore.pyqtSignal(str)
    flight_create_signal = QtCore.pyqtSignal(str, Flight)
    turn_on_watcher_signal = QtCore.pyqtSignal()
    turn_off_watcher_signal = QtCore.pyqtSignal()
    interop_connect_signal = QtCore.pyqtSignal(str, str, str, str)
    interop_disconnect_signal = QtCore.pyqtSignal()
    interop_enable_signal = QtCore.pyqtSignal()
    interop_disable_signal = QtCore.pyqtSignal()

    def __init__(self):
        super(SetupTab, self).__init__()

        self.setupUi(self)
        self.connectButtons()

        self.checkbox_folderWatcher.setCheckState(QtCore.Qt.Checked)
        self.checkbox_interopSupport.setCheckState(QtCore.Qt.Unchecked)
        self.connectCheckboxes()

        self.edit_flightDate.setDate(QDate.currentDate())

        self.interop_credentials_prompt = InteropCredentialPrompt()
        self.interop_credentials_prompt.dialog_accepted.connect(self.processDialogAcceptedEvent)
        self.interop_credentials_prompt.dialog_rejected.connect(self.processDialogRejectedEvent)

    def connectButtons(self):
        self.button_loadFlight.clicked.connect(self.loadFlight)
        self.button_createFlight.clicked.connect(self.createFlight)
        self.button_selectAreaMap.clicked.connect(self.selectAreaMap)
        self.button_browseWatchDirectory.clicked.connect(self.selectWatchDirectory)
        self.button_selectIntrinsicMatrix.clicked.connect(self.selectIntrinsicMatrix)

        self.button_interopConnect.clicked.connect(self.connectToInterop)
        self.button_interopDisconnect.clicked.connect(self.disconnectFromInterop)

    def connectCheckboxes(self):
        self.checkbox_folderWatcher.stateChanged.connect(self.folderWatcherCheckboxPressed)
        self.checkbox_interopSupport.stateChanged.connect(self.interopSupportCheckboxPressed)

    def enableSelectingAndCreatingFlights(self):
        self.group_openExistingFlight.setEnabled(True)
        self.group_createNewFlight.setEnabled(True)

    def disableSelectingAndCreatingFlights(self):
        self.group_openExistingFlight.setEnabled(False)
        self.group_createNewFlight.setEnabled(False)

    def enableSelectingWatcherFolder(self):
        self.button_browseWatchDirectory.setEnabled(True)

    def disableSelectingWatcherFolder(self):
        self.button_browseWatchDirectory.setEnabled(False)

    def addFlightToUi(self, flight):
        self.combo_flights.addItem(flight.location + " " + str(flight.date))

    def loadFlight(self):
        self.flight_load_signal.emit(self.combo_flights.currentText())

    def createFlight(self):
        location = self.line_locationName.text()
        try:
            elevation = float(self.line_siteElevation.text())
        except ValueError:
            exception_notification = QtWidgets.QMessageBox()
            exception_notification.setIcon(QtWidgets.QMessageBox.Warning)
            exception_notification.setText('Error: setupTab.py. Invalid elevation value; no flight created')
            exception_notification.setWindowTitle('Error!')
            exception_notification.setDetailedText('{}'.format(traceback.format_exc()))
            exception_notification.exec_()
            return
        date_string = self.edit_flightDate.text()
        date = datetime.datetime.strptime(date_string, '%Y-%m-%d').date()
        area_map = self.line_areaMap.text()
        intrinsic_matrix = self.line_intrinsicMatrix.text()

        if AreaMap.objects.filter(name=area_map).exists(): # TODO: change this DB call
            am = AreaMap.objects.filter(name=area_map).last()
        else:
            corners_geo = loadGeotiff('./area_maps/{}'.format(area_map))
            am = create_areamap(area_map, '{}.png'.format(area_map), corners_geo[0][1], corners_geo[0][0],
                                                             corners_geo[1][1], corners_geo[1][0],
                                                             corners_geo[2][1], corners_geo[2][0],
                                                             corners_geo[3][1], corners_geo[3][0])

        f = create_flight(location, elevation, intrinsic_matrix + '.xml', date, am)
        flight_list_id = '{} {}'.format(f.location, str(f.date))
        self.flight_create_signal.emit(flight_list_id, f)

    def selectAreaMap(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Select Area Map to Load", "./area_maps",
                                                         "Images (*.png)")
        file_info = QtCore.QFileInfo(filepath[0])
        filename = file_info.baseName()
        self.line_areaMap.setText(filename)

    def selectWatchDirectory(self):
        filepath = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory to Watch", "../vision-system/")
        if not filepath:
            return
        self.line_watchDirectory.setText(filepath)
        self.enableSelectingAndCreatingFlights()

    def selectIntrinsicMatrix(self):
        filepath = QtWidgets.QFileDialog.getOpenFileName(self, "Select Intrinsic Matrix to Load", "./intrinsic_matrices",
                                                         "XML Files (*.xml)")
        file_info = QtCore.QFileInfo(filepath[0])
        filename = file_info.baseName()
        self.line_intrinsicMatrix.setText(filename)

    def folderWatcherCheckboxPressed(self):
        folder_watcher_checkbox_state = self.checkbox_folderWatcher.checkState()
        if folder_watcher_checkbox_state == QtCore.Qt.Checked:
            self.disableSelectingAndCreatingFlights()
            self.enableSelectingWatcherFolder()
            self.turn_on_watcher_signal.emit()
        elif folder_watcher_checkbox_state == QtCore.Qt.Unchecked:
            self.line_watchDirectory.setText('')
            self.enableSelectingAndCreatingFlights()
            self.disableSelectingWatcherFolder()
            self.turn_off_watcher_signal.emit()

    def interopSupportCheckboxPressed(self):
        interop_enable_checkbox_state = self.checkbox_interopSupport.checkState()
        if interop_enable_checkbox_state == QtCore.Qt.Checked:
            self.button_interopConnect.setEnabled(True)
            self.interop_enable_signal.emit()
        elif interop_enable_checkbox_state == QtCore.Qt.Unchecked:
            self.button_interopConnect.setEnabled(False)
            self.button_interopDisconnect.setEnabled(False)
            self.interop_disable_signal.emit()

    def connectToInterop(self):
        self.interop_credentials_prompt.exec_()

    def disconnectFromInterop(self):
        self.interop_disconnect_signal.emit()

    @QtCore.pyqtSlot(str, str, str, str)
    def processDialogAcceptedEvent(self, ip_address, port_number, username, password):
        # forward the information from the dialog window to the Controller to attempt Interop connection
        self.interop_connect_signal.emit(ip_address, port_number, username, password)

    @QtCore.pyqtSlot()
    def processDialogRejectedEvent(self):
        self.interop_disconnect_signal.emit()

    @QtCore.pyqtSlot()
    def processInteropConnectionError(self):
        self.disconnectFromInterop()

    def resetTab(self):
        self.group_createNewFlight.setEnabled(False)
        self.group_openExistingFlight.setEnabled(False)
        self.line_watchDirectory.setText("")

    def updateOnResize(self):
        pass # nothing to do here
