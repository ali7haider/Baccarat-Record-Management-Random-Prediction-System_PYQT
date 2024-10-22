# -*- coding: utf-8 -*-
"""
Created on Fri Jan 19 20:03:57 2024

@author: Digital Zone
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, QUrl, Qt
from PyQt5.QtGui import QIcon, QDesktopServices, QMouseEvent
from main_ui import Ui_MainWindow  # Import the generated class

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self,login_screen,db_manager, user):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated class
        self.setupUi(self)
        self.login_screen = login_screen  # Save the login screen reference
        self.db_manager = db_manager  # Store the DatabaseManager instance
        self.user = user  # Store the logged-in user data

        # Set flags to remove the default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Connect the maximizeRestoreAppBtn button to the maximize_window method
        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_window)

        # Connect the closeAppBtn button to the close method
        self.closeAppBtn.clicked.connect(self.close)

        # Connect the minimizeAppBtn button to the showMinimized method
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Connect the visitLabel to the openWebLink method
        # self.visit.linkActivated.connect(self.openWebLink)

    def openWebLink(self, link):
        # Open the web link in the default web browser
        QDesktopServices.openUrl(QUrl(link))

    # MOUSE CLICK EVENTS
    # Define the mousePressEvent method to handle mouse button press events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

    def maximize_window(self):
        # If the window is already maximized, restore it
        if self.isMaximized():
            self.showNormal()
        # Otherwise, maximize it
        else:
            self.showMaximized()

    

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
