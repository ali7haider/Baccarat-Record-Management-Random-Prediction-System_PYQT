import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QMessageBox, QPushButton,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5 import uic
from qtwidgets import AnimatedToggle
import random

class MainWindow(QMainWindow):
    def __init__(self, login_screen=None, db_manager=None, user=None):
        super(MainWindow, self).__init__()

        # Load the .ui file directly
        uic.loadUi('main.ui', self)
        self.login_screen = login_screen
        self.db_manager = db_manager
        self.user = user
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.maximizeRestoreAppBtn.clicked.connect(self.maximize_window)
        self.closeAppBtn.clicked.connect(self.close)
        self.minimizeAppBtn.clicked.connect(self.showMinimized)
        
        # Initialize the grid
        self.initGrid()
        # Add the AnimatedToggle to toggleFrame
        self.initToggle()

        # Connect buttons for results and reset
        self.btnPlayer.clicked.connect(self.update_player_result)
        self.btnTie.clicked.connect(self.update_tie_result)
        self.btnBank.clicked.connect(self.update_bank_result)
        self.btnBack.clicked.connect(self.remove_last_result)
        self.btnReset.clicked.connect(self.reset_records)

        # Initialize row tracker and history
        self.current_row = [0] * 16
        self.results_history = []
        self.labels_history = []

        # Connect Predict button
        self.btnPredict.clicked.connect(self.predict_outcome)

        # Initialize the progress bar
        self.progressBarAIAnalysis.setValue(0)

        # Cache for last prediction
        self.last_prediction = None
        self.last_winning_rate = None
        self.last_bet_amount = None
        self.prediction_history_size = 0  # Stores size of history when prediction was last made


    def initGrid(self):
        self.grid_layout = QGridLayout()
        rows = 6
        columns = 16
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(0)

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

        self.gridFrame.setLayout(self.grid_layout)

    def update_player_result(self):
        self.add_result_to_grid("Player")

    def update_tie_result(self):
        self.add_result_to_grid("Tie")

    def update_bank_result(self):
        self.add_result_to_grid("Bank")

    def add_result_to_grid(self, result):
        col = 0
        while col < len(self.current_row) and self.current_row[col] >= len(self.grid_cells):
            col += 1

        if col >= len(self.current_row):
            return

        row = self.current_row[col]
        if row < len(self.grid_cells):
            new_label = QLabel("")
            new_label.setAlignment(Qt.AlignCenter)
            self.results_history.append((result, row, col))
            self.labels_history.append(new_label)

            if result == "Player":
                self.setup_label(new_label, "P", "#3E8AEF")
            elif result == "Tie":
                self.setup_label(new_label, "T", "#29BE66")
            elif result == "Bank":
                self.setup_label(new_label, "B", "#FF0000")

            self.grid_layout.addWidget(new_label, row, col)
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
        reply = QMessageBox.question(self, 'Reset Records',
                                     'Are you sure you want to reset all records?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.results_history.clear()
            self.labels_history.clear()
            self.current_row = [0] * 16

            # Clear the grid
            for row in range(len(self.grid_cells)):
                for col in range(len(self.grid_cells[row])):
                    if self.grid_cells[row][col]:
                        self.grid_layout.removeWidget(self.grid_cells[row][col])
                        self.grid_cells[row][col].deleteLater()

            # Re-populate grid_cells with empty labels
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
        if self.results_history and self.labels_history:
            last_result, row, col = self.results_history.pop()
            last_label = self.labels_history.pop()

            self.grid_layout.removeWidget(last_label)
            last_label.deleteLater()

            if self.current_row[col] > 0:
                self.current_row[col] -= 1

    def predict_outcome(self):
        if len(self.results_history) <= 15:
            QMessageBox.warning(self, 'Insufficient Data', 'Insufficient data for analysis.')
            return

        # Check if there are no new records since the last prediction
        if self.prediction_history_size == len(self.results_history) and self.last_prediction:
            self.display_prediction(self.last_prediction, self.last_winning_rate, self.last_bet_amount)
            return

        # Run prediction analysis if new records are added
        self.progressBarAIAnalysis.setValue(0)
        self.prediction_thread = PredictionThread()
        self.prediction_thread.update_progress.connect(self.progressBarAIAnalysis.setValue)
        self.prediction_thread.prediction_ready.connect(self.cache_and_display_prediction)
        self.prediction_thread.start()

    def cache_and_display_prediction(self, predicted_outcome, winning_rate, bet_amount):
        # Cache the results of the prediction
        self.last_prediction = predicted_outcome
        self.last_winning_rate = winning_rate
        self.last_bet_amount = bet_amount
        self.prediction_history_size = len(self.results_history)  # Update history size at prediction time
        # Display the prediction
        self.display_prediction(predicted_outcome, winning_rate, bet_amount)

    def display_prediction(self, predicted_outcome, winning_rate, bet_amount):
        self.labelPredictionOutcome.setText(f"Prediction: {predicted_outcome[0]}")  # 'P' or 'B'
        self.labelWinningRate.setText(f"Winning Rate: {winning_rate}%")
        self.labelBetAmount.setText(f"Bet Amount: ${bet_amount:.2f}")

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

    def on_toggle_change(self, state):
        if state == Qt.Checked:
            print("Toggle ON")
        else:
            print("Toggle OFF")
    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

from PyQt5.QtCore import QThread, pyqtSignal

class PredictionThread(QThread):
    update_progress = pyqtSignal(int)
    prediction_ready = pyqtSignal(str, float, float)

    def run(self):
        duration = random.randint(1300, 1700)
        steps = 100
        interval = duration // steps

        for i in range(steps + 1):
            self.update_progress.emit(i)
            self.msleep(interval)

        predicted_outcome = random.choice(['Player', 'Banker'])
        winning_rate = round(random.uniform(53.0, 59.0), 1)
        bet_amount = 10

        self.prediction_ready.emit(predicted_outcome, winning_rate, bet_amount)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
