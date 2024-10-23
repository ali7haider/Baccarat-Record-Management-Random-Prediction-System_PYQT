import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QWidget, QVBoxLayout,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5 import uic  # Import the uic module to load the .ui file dynamically
from qtwidgets import AnimatedToggle
import resources_rc
class MainWindow(QMainWindow):
    def __init__(self, login_screen=None, db_manager=None, user=None):
        super(MainWindow, self).__init__()

        # Load the .ui file directly
        uic.loadUi('main.ui', self)

        self.login_screen = login_screen
        self.db_manager = db_manager
        self.user = user

        # Set flags to remove the default title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

        # Connect window control buttons
        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_window)
        self.closeAppBtn.clicked.connect(self.close)
        self.minimizeAppBtn.clicked.connect(self.showMinimized)

        # Initialize the grid
        self.initGrid()

        # Add the AnimatedToggle to toggleFrame and connect it to a function
        self.initToggle()

        # Connect the player, tie, bank, and back buttons
        self.btnPlayer.clicked.connect(self.update_player_result)
        self.btnTie.clicked.connect(self.update_tie_result)
        self.btnBank.clicked.connect(self.update_bank_result)
        self.btnBack.clicked.connect(self.remove_last_result)  # Connect btnBack
        self.btnReset.clicked.connect(self.reset_records)
        # Variables to keep track of the current row for each column
        self.current_row = [0] * 16  # Assuming there are 16 columns
        self.results_history = []  # To keep track of results added
        self.labels_history = []  # To track QLabel instances for removal

    def initGrid(self):
        # Create a QGridLayout to add to the gridFrame
        self.grid_layout = QGridLayout()
        rows = 6
        columns = 16

        # Set margins and spacing
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

        # Populate the grid with empty labels
        self.grid_cells = [[None for _ in range(columns)] for _ in range(rows)]
        for row in range(rows):
            for col in range(columns):
                label = QLabel("")
                label.setAlignment(Qt.AlignCenter)
                label.setStyleSheet(""" 
                    background-color: white; 
                    color: black; 
                    border: 1px solid #D5D5D5; 
                    margin: 0px; 
                    padding: 0px; 
                """)
                self.grid_cells[row][col] = label
                self.grid_layout.addWidget(label, row, col)

        # Set the grid layout to the gridFrame
        self.gridFrame.setLayout(self.grid_layout)

    def initToggle(self):
        if hasattr(self, 'toggleFrame'):
            layout = QVBoxLayout(self.toggleFrame)
            layout.setSpacing(2)

            label = QLabel("Budget Tracking")
            label.setAlignment(Qt.AlignLeft)
            label.setStyleSheet(""" 
                font-family: 'MS Shell Dlg 2'; 
                font-size: 13px; 
                font-weight: bold; 
                color: white; 
            """)
            toggle = AnimatedToggle(checked_color="#93C47D", pulse_checked_color="#44FFB000")
            toggle.setFixedSize(80, 50)
            toggle.stateChanged.connect(self.on_toggle_change)

            layout.addWidget(label)
            layout.addWidget(toggle)
        else:
            print("toggleFrame not found")

    def on_toggle_change(self, state):
        if state == Qt.Checked:
            print("Toggle ON")
        else:
            print("Toggle OFF")

    def update_player_result(self):
        self.add_result_to_grid("Player")

    def update_tie_result(self):
        self.add_result_to_grid("Tie")

    def update_bank_result(self):
        self.add_result_to_grid("Bank")

    def add_result_to_grid(self, result):
        # Find the next available column and row
        col = 0
        while col < len(self.current_row) and self.current_row[col] >= len(self.grid_cells):
            col += 1

        # If we have filled up all columns, do nothing
        if col >= len(self.current_row):
            return

        row = self.current_row[col]

        if row < len(self.grid_cells):
            # Create a new label for the result
            new_label = QLabel("")
            new_label.setAlignment(Qt.AlignCenter)

            # Store the result and corresponding cell position for later removal
            self.results_history.append((result, row, col))
            self.labels_history.append(new_label)  # Track the QLabel instance

            # Set styles and text based on the result
            if result == "Player":
                self.setup_label(new_label, "P", "#3E8AEF")
            elif result == "Tie":
                self.setup_label(new_label, "T", "#29BE66")
            elif result == "Bank":
                self.setup_label(new_label, "B", "#FF0000")

            # Add the new label to the grid layout
            self.grid_layout.addWidget(new_label, row, col)

            # Move to the next row in the column
            self.current_row[col] += 1

    def setup_label(self, label, text, color):
        label.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 15px; 
            color: white; 
            margin: 5px; 
        """)
        label.setText(text)
    def reset_records(self):
        # Ask for confirmation before resetting
        reply = QMessageBox.question(self, 'Reset Records',
                                    'Are you sure you want to reset all records?',
                                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            # Clear all results and reset the UI
            self.results_history.clear()
            self.labels_history.clear()
            self.current_row = [0] * 16  # Reset row trackers

            # Clear the grid layout and delete all labels
            for row in range(len(self.grid_cells)):
                for col in range(len(self.grid_cells[row])):
                    # Clear the label from the layout
                    if self.grid_cells[row][col]:
                        self.grid_layout.removeWidget(self.grid_cells[row][col])  # Remove the widget
                        self.grid_cells[row][col].deleteLater()  # Properly delete the widget
                        self.grid_cells[row][col].setText("")  # Clear the cell text
                        self.grid_cells[row][col].setStyleSheet(""" 
                            background-color: white; 
                            color: black; 
                            border: 1px solid #D5D5D5; 
                            margin: 0px; 
                            padding: 0px; 
                        """)

            # Re-populate grid_cells with empty labels after clearing
            self.grid_cells = [[None for _ in range(16)] for _ in range(6)]
            for row in range(6):
                for col in range(16):
                    label = QLabel("")
                    label.setAlignment(Qt.AlignCenter)
                    label.setStyleSheet(""" 
                        background-color: white; 
                        color: black; 
                        border: 1px solid #D5D5D5; 
                        margin: 0px; 
                        padding: 0px; 
                    """)
                    self.grid_cells[row][col] = label
                    self.grid_layout.addWidget(label, row, col)



    def remove_last_result(self):
        # Remove the last result if there are any results to remove
        if self.results_history and self.labels_history:
            last_result, row, col = self.results_history.pop()  # Get the last result
            last_label = self.labels_history.pop()  # Get the last QLabel instance

            # Remove the label from the grid layout
            self.grid_layout.removeWidget(last_label)
            last_label.deleteLater()  # Properly delete the widget
            
            # Move back the row pointer for that column
            if self.current_row[col] > 0:  # Prevent underflow
                self.current_row[col] -= 1
            
            # Reset the last label cell back to empty
            self.grid_cells[row][col].setText("")  # Clear the cell
            self.grid_cells[row][col].setStyleSheet(""" 
                background-color: white; 
                color: black; 
                border: 1px solid #D5D5D5; 
                margin: 0px; 
                padding: 0px; 
            """)

    def get_result_letter(self, result):
        if result == "Player":
            return "P"
        elif result == "Tie":
            return "T"
        elif result == "Bank":
            return "B"
        return ""

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
