# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'gui/ui/ui_mapTab.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MapTab(object):
    def setupUi(self, MapTab):
        MapTab.setObjectName("MapTab")
        MapTab.resize(1143, 892)
        self.horizontalLayout = QtWidgets.QHBoxLayout(MapTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.layout_allImages = QtWidgets.QVBoxLayout()
        self.layout_allImages.setContentsMargins(0, 0, -1, -1)
        self.layout_allImages.setObjectName("layout_allImages")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setContentsMargins(-1, 0, -1, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.lineEdit_3 = QtWidgets.QLineEdit(MapTab)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.horizontalLayout_2.addWidget(self.lineEdit_3)
        self.lineEdit_2 = QtWidgets.QLineEdit(MapTab)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout_2.addWidget(self.lineEdit_2)
        self.pushButton_8 = QtWidgets.QPushButton(MapTab)
        self.pushButton_8.setObjectName("pushButton_8")
        self.horizontalLayout_2.addWidget(self.pushButton_8)
        self.layout_allImages.addLayout(self.horizontalLayout_2)
        self.groupBox_6 = QtWidgets.QGroupBox(MapTab)
        self.groupBox_6.setObjectName("groupBox_6")
        self.verticalLayout_7 = QtWidgets.QVBoxLayout(self.groupBox_6)
        self.verticalLayout_7.setObjectName("verticalLayout_7")
        self.list_allImages = QtWidgets.QListWidget(self.groupBox_6)
        self.list_allImages.setObjectName("list_allImages")
        self.verticalLayout_7.addWidget(self.list_allImages)
        self.layout_allImages.addWidget(self.groupBox_6)
        self.horizontalLayout.addLayout(self.layout_allImages)
        self.viewer_map = PhotoViewer(MapTab)
        self.viewer_map.setObjectName("viewer_map")
        self.horizontalLayout.addWidget(self.viewer_map)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)

        self.retranslateUi(MapTab)
        QtCore.QMetaObject.connectSlotsByName(MapTab)

    def retranslateUi(self, MapTab):
        _translate = QtCore.QCoreApplication.translate
        MapTab.setWindowTitle(_translate("MapTab", "Form"))
        self.lineEdit_3.setPlaceholderText(_translate("MapTab", "latitude"))
        self.lineEdit_2.setPlaceholderText(_translate("MapTab", "longitude"))
        self.pushButton_8.setText(_translate("MapTab", "Search"))
        self.groupBox_6.setTitle(_translate("MapTab", "List of Images"))

from gui.photoViewer import PhotoViewer
