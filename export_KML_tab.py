# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'export_KML_tab.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!

import os
import selenium
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
import time
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(344, 256)
        font = QtGui.QFont()
        font.setPointSize(18)
        font.setItalic(True)
        MainWindow.setFont(font)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(80, 110, 171, 51))
        self.pushButton.setObjectName("pushButton")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(110, 30, 131, 51))
        self.label.setObjectName("label")
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 344, 33))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.pushButton.clicked.connect(export)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.pushButton.setToolTip(_translate("MainWindow", "<html><head/><body><p><a href=\"https://www.google.com/maps/d/u/0/edit?mid=10mRYAJjYF6AoQz2hDhpD6yI9lSxmSS51&amp;ll=49.16314987502436%2C-122.96579394999998&amp;z=11\"><span style=\" text-decoration: underline; color:#0000ff;\">google_map</span></a></p></body></html>"))
        self.pushButton.setText(_translate("MainWindow", "Export KML"))
        self.label.setText(_translate("MainWindow", "Welcome!"))

def export():
        # Build tuple of (class, file) to import
	# Users need to change the directory below into their own directory where the KML file is saved
        submission_dir = '/home/henry/my_directory'
        dir_list = list(os.listdir(submission_dir))
        for directory in dir_list:
            file_list = list(os.listdir(os.path.join(submission_dir, directory)))
            if len(file_list) != 0:
                file_tup = (directory, file_list[0])
            print(file_tup)
        folder = file_tup[0]
        file_name = file_tup[1]
            
        
        # Using Chrome to access web

        driver = webdriver.Chrome(ChromeDriverManager().install())
        # Open the website
        driver.get('https://www.gpsvisualizer.com/')
        time.sleep(2)

        # Find "choose file" button
        choose_file = driver.find_element_by_name('uploaded_file_1')

        # Send the name of the file to the button
        file_location = os.path.join(submission_dir, folder, file_name)
        choose_file.send_keys(file_location)

        #click the "map it" button
        map_it = driver.find_element_by_id('homepage_submit')
        map_it.click()


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
