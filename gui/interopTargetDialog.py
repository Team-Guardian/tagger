# Qt library modules
from PyQt5 import QtWidgets, QtCore

from ui.ui_interopTarget import Ui_Dialog

class InteropTargetDialog(QtWidgets.QDialog, Ui_Dialog):
    def __init__(self):
        super(InteropTargetDialog, self).__init__()

        self.setupUi(self)

        # populate combo-boxes with allowed values
        self.comboBox_targetType.addItem('standard')
        self.comboBox_targetType.addItem('off-axis')
        self.comboBox_targetType.addItem('emergent')

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