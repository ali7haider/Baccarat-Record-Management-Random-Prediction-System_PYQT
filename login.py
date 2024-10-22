from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.Qt import QDesktopServices
from login_ui import Ui_MainWindow  # Import the generated class
import sqlite3
from databaseManager import DatabaseManager

import sys

class MainWindow(QMainWindow, Ui_MainWindow):  # Inherit from the generated class
    def __init__(self):
        super(MainWindow, self).__init__()

        # Set up the user interface from the generated class
        self.setupUi(self)

        # Set flags to remove the default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.db_manager = DatabaseManager("data.db")  # Initialize DatabaseManager
        self.db_manager.create_table()  # Ensure table is created

        if not self.db_manager.insert_user("", "", isActive=1):
            print("Failed to insert user: Username already exists.")        # Connect login button click event to the login function
        self.btnLogIn.clicked.connect(self.check_credentials)

        # Connect the closeAppBtn button to the close method
        self.closeAppBtn.clicked.connect(self.close)

        # Connect the minimizeAppBtn button to the showMinimized method
        self.minimizeAppBtn.clicked.connect(self.showMinimized)
        
        # self.visit.linkActivated.connect(self.openWebLink)

    def check_credentials(self):
        # Get username and password input from the UI
        username = self.txtUsername.text()
        password = self.txtPassword.text()

        # Query the database for the entered username and password
        user = self.db_manager.get_user_by_credentials(username, password)

        if user:  # If user is found in the database
            from main import MainWindow  # Import here to avoid circular import
            self.main = MainWindow(self,self.db_manager, user)  # Pass DatabaseManager and user data
            self.main.show()
            self.close()
        else:
            self.lblError.setText("Invalid username or password")
    
    
    
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
