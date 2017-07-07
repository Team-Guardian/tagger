# Other modules
import math

# Qt library modules
from PyQt5 import QtWidgets, QtCore

from ui.ui_interopTarget import Ui_Dialog

class InteropTargetDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self, enable_target_cropping_handler):
        super(InteropTargetDialog, self).__init__()

        self.setupUi(self)

        self.current_target_tag = None
        self.current_target_image = None
        self.current_target_cropped_rect = None

        self.image_yaw = None

        self.button_cropTarget.clicked.connect(enable_target_cropping_handler)

        # populate combo-boxes with allowed values
        self.populateComboBoxes()


        self.installEventFilter(self)
        self.lineEdit_latitude.installEventFilter(self)
        self.lineEdit_longitude.installEventFilter(self)

        self.button_orientation.clicked.connect(self.startDrawingOrientation)

        self.comboBox_targetType.currentIndexChanged.connect(self.processComboboxTargetTypeCurrentIndexChanged)

        self.viewer_target.orientation_defined_signal.connect(self.processOrientationDefined)

    def setTargetTag(self, tag):
        self.current_target_tag = tag

    def populateComboBoxes(self):
        self.populateTargetTypeOptions()
        self.populateShapeOptions()
        self.populateShapeColorOptions()
        self.populateAlphanumericColorOptions()

    def populateTargetTypeOptions(self):
        self.comboBox_targetType.addItem('standard')
        self.comboBox_targetType.addItem('off-axis')
        self.comboBox_targetType.addItem('emergent')

    def populateShapeOptions(self):
        self.comboBox_shape.addItem('circle')
        self.comboBox_shape.addItem('semicircle')
        self.comboBox_shape.addItem('quarter_circle')
        self.comboBox_shape.addItem('triangle')
        self.comboBox_shape.addItem('square')
        self.comboBox_shape.addItem('rectangle')
        self.comboBox_shape.addItem('trapezoid')
        self.comboBox_shape.addItem('pentagon')
        self.comboBox_shape.addItem('hexagon')
        self.comboBox_shape.addItem('heptagon')
        self.comboBox_shape.addItem('octagon')
        self.comboBox_shape.addItem('star')
        self.comboBox_shape.addItem('cross')

    def populateShapeColorOptions(self):
        self.comboBox_shapeColor.addItem('white')
        self.comboBox_shapeColor.addItem('black')
        self.comboBox_shapeColor.addItem('gray')
        self.comboBox_shapeColor.addItem('red')
        self.comboBox_shapeColor.addItem('blue')
        self.comboBox_shapeColor.addItem('green')
        self.comboBox_shapeColor.addItem('yellow')
        self.comboBox_shapeColor.addItem('purple')
        self.comboBox_shapeColor.addItem('brown')
        self.comboBox_shapeColor.addItem('orange')

    def populateAlphanumericColorOptions(self):
        self.comboBox_alphanumericColor.addItem('white')
        self.comboBox_alphanumericColor.addItem('black')
        self.comboBox_alphanumericColor.addItem('gray')
        self.comboBox_alphanumericColor.addItem('red')
        self.comboBox_alphanumericColor.addItem('blue')
        self.comboBox_alphanumericColor.addItem('green')
        self.comboBox_alphanumericColor.addItem('yellow')
        self.comboBox_alphanumericColor.addItem('purple')
        self.comboBox_alphanumericColor.addItem('brown')
        self.comboBox_alphanumericColor.addItem('orange')

    def setCroppedImage(self, cropped_image):
        self.viewer_target.setPhoto(cropped_image)

    def saveCroppedRect(self, cropped_rect):
        self.current_target_cropped_rect = cropped_rect

    def startDrawingOrientation(self):
        self.viewer_target.is_orientation_drawing_in_progress = True

    @QtCore.pyqtSlot(float)
    def processOrientationDefined(self, relative_orientation):
        absolute_orientation = (self.image_yaw + relative_orientation) % 360 # can't be more than 360 degrees, loops around if more

        # convert direction in degrees to compass direction
        compass_sector_index = int(math.floor((absolute_orientation / 45) + 0.5))
        compass_sectors = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        self.lineEdit_orientation.setText(compass_sectors[compass_sector_index])

    def processComboboxTargetTypeCurrentIndexChanged(self):
        if self.comboBox_targetType.currentText() == 'emergent':
            self.configureFormForEmergentTarget()
        else:
            self.configureFormForStandardAndOffAxisTarget()

    def eventFilter(self, QObject, QEvent):
        if QObject == self.lineEdit_longitude and QEvent.type() == QtCore.QEvent.MouseButtonDblClick:
            self.lineEdit_longitude.setEnabled(True)
        elif QObject == self.lineEdit_latitude and QEvent.type() == QtCore.QEvent.MouseButtonDblClick:
            self.lineEdit_latitude.setEnabled(True)

        return QtWidgets.QWidget.eventFilter(self, QObject, QEvent)

    def configureFormForStandardAndOffAxisTarget(self):
        self.comboBox_shape.setEnabled(True)
        self.comboBox_shapeColor.setEnabled(True)
        self.lineEdit_orientation.setEnabled(True)
        self.lineEdit_alphanumeric.setEnabled(True)
        self.comboBox_alphanumericColor.setEnabled(True)
        self.textEdit_description.setEnabled(False)

    def configureFormForEmergentTarget(self):
        self.comboBox_shape.setEnabled(False)
        self.comboBox_shapeColor.setEnabled(False)
        self.lineEdit_orientation.setEnabled(False)
        self.lineEdit_alphanumeric.setEnabled(False)
        self.comboBox_alphanumericColor.setEnabled(False)
        self.textEdit_description.setEnabled(True)

    def reset(self):
        self.lineEdit_alphanumeric.clear()
        self.lineEdit_latitude.clear()
        self.lineEdit_longitude.clear()
        self.lineEdit_orientation.clear()
        self.viewer_target.setPhoto(None)
