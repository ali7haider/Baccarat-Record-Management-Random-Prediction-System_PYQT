import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget,QVBoxLayout
from PyQt5.QtCore import Qt, QUrl
from PyQt5.QtGui import QDesktopServices, QMouseEvent
from main_ui import Ui_MainWindow  # Import the generated class
from PyQt5 import uic  # Import the uic module to load the .ui file dynamically
from qtwidgets import Toggle, AnimatedToggle

class MainWindow(QMainWindow):
    def __init__(self, login_screen=None, db_manager=None, user=None):
        super(MainWindow, self).__init__()

        # Load the .ui file directly
        uic.loadUi('main.ui', self)  # Replace 'your_ui_file.ui' with the actual file name

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

        # Initialize the grid
        self.initGrid()

        # Add the AnimatedToggle to toggleFrame and connect it to a function
        self.initToggle()

    def initGrid(self):
        # Create a QGridLayout to add to the gridFrame
        grid_layout = QGridLayout()

        # Set the number of rows and columns for the grid
        rows = 6
        columns = 16

        # Set margins to zero to eliminate gaps between cells
        grid_layout.setContentsMargins(15, 15, 15, 15)  # Add margin around the grid
        grid_layout.setSpacing(0)  # Remove spacing between cells

        # Populate the grid with QLabel or QPushButton (here QLabel for now)
        for row in range(rows):
            for col in range(columns):
                # Create a QLabel to represent each cell
                label = QLabel(f"")
                label.setAlignment(Qt.AlignCenter)

                # Style the QLabel with white background, black border, and no margins
                label.setStyleSheet("""
                    background-color: white;
                    color: black;
                    border: 1px solid #D5D5D5;  /* Black border to form grid boxes */
                    margin: 0px;              /* Ensure no margin around the label */
                    padding: 0px;             /* Ensure no internal padding */
                """)
                grid_layout.addWidget(label, row, col)  # Add the label to the grid

        # Set the grid layout to the gridFrame
        self.gridFrame.setLayout(grid_layout)
    def initToggle(self):
        # Ensure toggleFrame exists
        if hasattr(self, 'toggleFrame'):
            print("toggleFrame found")
            
            # Create a layout for toggleFrame if it doesn't already have one
            layout = QVBoxLayout(self.toggleFrame)  # You can use QHBoxLayout or QVBoxLayout
            # Set the spacing between widgets in the layout to 8 pixels
            layout.setSpacing(2)
            self.toggleFrame.setLayout(layout)      # Set the layout for toggleFrame

            # Create a label for the heading
            label = QLabel("Budget Tracking")
            label.setAlignment(Qt.AlignLeft)  # Center the text
            label.setStyleSheet("""
            font-family: 'MS Shell Dlg 2'; 
            font-size: 13px; 
            font-weight: bold; 
            color: white;
        """)  # Set font to MS Shell Dlg 2 and style it

            # Create an instance of AnimatedToggle
            toggle = AnimatedToggle(
                checked_color="#93C47D",
                pulse_checked_color="#44FFB000"
            )

            # Set the toggle button size to be smaller
            toggle.setFixedSize(80, 50)  # Adjust width and height for smaller size
            
            # Connect the state change signal to a custom function
            toggle.stateChanged.connect(self.on_toggle_change)

            # Add the label and toggle button to the toggleFrame layout
            layout.addWidget(label)
            layout.addWidget(toggle)
        else:
            print("toggleFrame not found")




    def on_toggle_change(self, state):
        if state == Qt.Checked:
            print("Toggle ON")
            # Implement functionality for ON state
        else:
            print("Toggle OFF")
            # Implement functionality for OFF state


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
