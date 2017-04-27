# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui_targetsTab.ui'
#
# Created by: PyQt5 UI code generator 5.5.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_TargetsTab(object):
    def setupUi(self, TargetsTab):
        TargetsTab.setObjectName("TargetsTab")
        TargetsTab.resize(1214, 771)
        self.horizontalLayout = QtWidgets.QHBoxLayout(TargetsTab)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout()
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.groupBox_5 = QtWidgets.QGroupBox(TargetsTab)
        self.groupBox_5.setObjectName("groupBox_5")
        self.verticalLayout_6 = QtWidgets.QVBoxLayout(self.groupBox_5)
        self.verticalLayout_6.setObjectName("verticalLayout_6")
        self.list_tags = QtWidgets.QListWidget(self.groupBox_5)
        self.list_tags.setObjectName("list_tags")
        self.verticalLayout_6.addWidget(self.list_tags)
        self.verticalLayout_4.addWidget(self.groupBox_5)
        self.groupBox_4 = QtWidgets.QGroupBox(TargetsTab)
        self.groupBox_4.setObjectName("groupBox_4")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.groupBox_4)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.line_searchImages = QtWidgets.QLineEdit(self.groupBox_4)
        self.line_searchImages.setText("")
        self.line_searchImages.setObjectName("line_searchImages")
        self.verticalLayout_5.addWidget(self.line_searchImages)
        self.list_taggedImages = QtWidgets.QListWidget(self.groupBox_4)
        self.list_taggedImages.setObjectName("list_taggedImages")
        self.verticalLayout_5.addWidget(self.list_taggedImages)
        self.verticalLayout_4.addWidget(self.groupBox_4)
        self.verticalLayout_4.setStretch(0, 1)
        self.verticalLayout_4.setStretch(1, 2)
        self.horizontalLayout.addLayout(self.verticalLayout_4)
        self.verticalLayout_10 = QtWidgets.QVBoxLayout()
        self.verticalLayout_10.setContentsMargins(-1, -1, 0, -1)
        self.verticalLayout_10.setObjectName("verticalLayout_10")
        self.viewer_targets = PhotoViewer(TargetsTab)
        self.viewer_targets.setObjectName("viewer_targets")
        self.verticalLayout_10.addWidget(self.viewer_targets)
        self.horizontalLayout.addLayout(self.verticalLayout_10)
        self.horizontalLayout.setStretch(0, 1)
        self.horizontalLayout.setStretch(1, 3)

        self.retranslateUi(TargetsTab)
        QtCore.QMetaObject.connectSlotsByName(TargetsTab)

    def retranslateUi(self, TargetsTab):
        _translate = QtCore.QCoreApplication.translate
        TargetsTab.setWindowTitle(_translate("TargetsTab", "Form"))
        self.groupBox_5.setTitle(_translate("TargetsTab", "Select Tag"))
        self.groupBox_4.setTitle(_translate("TargetsTab", "Images with Selected Tag"))
        self.line_searchImages.setPlaceholderText(_translate("TargetsTab", "Search image by name"))

from gui.photoViewer import PhotoViewer
