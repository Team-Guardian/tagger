# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui/ui_setupTab.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_SetupTab(object):
    def setupUi(self, SetupTab):
        SetupTab.setObjectName("SetupTab")
        SetupTab.resize(831, 638)
        self.horizontalLayout = QtWidgets.QHBoxLayout(SetupTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.groupBox = QtWidgets.QGroupBox(SetupTab)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.groupBox)
        self.verticalLayout.setObjectName("verticalLayout")
        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        self.line_sessionDirectory = QtWidgets.QLineEdit(self.groupBox)
        self.line_sessionDirectory.setObjectName("line_sessionDirectory")
        self.gridLayout.addWidget(self.line_sessionDirectory, 2, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 1)
        self.button_sessionDirectory = QtWidgets.QPushButton(self.groupBox)
        self.button_sessionDirectory.setObjectName("button_sessionDirectory")
        self.gridLayout.addWidget(self.button_sessionDirectory, 2, 2, 1, 1)
        self.line_sessionName = QtWidgets.QLineEdit(self.groupBox)
        self.line_sessionName.setObjectName("line_sessionName")
        self.gridLayout.addWidget(self.line_sessionName, 0, 1, 1, 2)
        self.verticalLayout.addLayout(self.gridLayout)
        self.horizontalLayout.addWidget(self.groupBox)

        self.retranslateUi(SetupTab)
        QtCore.QMetaObject.connectSlotsByName(SetupTab)

    def retranslateUi(self, SetupTab):
        _translate = QtCore.QCoreApplication.translate
        SetupTab.setWindowTitle(_translate("SetupTab", "Form"))
        self.groupBox.setTitle(_translate("SetupTab", "Session"))
        self.label.setText(_translate("SetupTab", "Working Directory:"))
        self.label_2.setText(_translate("SetupTab", "Name:"))
        self.button_sessionDirectory.setText(_translate("SetupTab", "Browse..."))

