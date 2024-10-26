import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QLabel, QMessageBox, QPushButton,QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from PyQt5 import uic
from qtwidgets import AnimatedToggle
import random
import resources_rc
from datetime import datetime
# def check_expiration():
#     expiration_date = datetime(2024, 10, 27)
#     if datetime.now() > expiration_date:
#         QMessageBox.warning(None, "Expired", "The program has expired!")
#         sys.exit()
class MainWindow(QMainWindow):
    def __init__(self, login_screen=None, db_manager=None, user=None):
        super(MainWindow, self).__init__()
        # Check if the program has expired
        # check_expiration()
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

        # Budget-related attributes
        self.budget_tracking_enabled = False  # By default, tracking is off
        self.budget = 0  # Initial budget
        self.bet_amount = 10  # Default bet amount, can be adjusted
        self.budgetDisplay.setText(f"Budget: ${self.budget:.2f}")
        # List to track budget history
        self.budget_history = []  # List of tuples (new_budget, change)
        self.total_profit = 0
        self.initial_budget=0



        # Connect Predict button
        self.btnPredict.clicked.connect(self.predict_outcome)

        self.btnSetBudget.clicked.connect(self.set_budget)
        # Connect btnResetLogs to reset_logs method
        self.btnResetLogs.clicked.connect(self.reset_logs)
        # Initialize the progress bar
        self.progressBarAIAnalysis.setValue(0)

        # Cache for last prediction
        self.last_prediction = None
        self.last_winning_rate = None
        self.last_bet_amount = None
        self.prediction_history_size = 0  # Stores size of history when prediction was last made

        # Initialize betting system state
        self.oscar_unit = 0.05  # Oscar's Grind: 5% of total bankroll
        self.oscar_bet = self.oscar_unit  # Start bet = 1 unit
        self.oscar_profit = 0  # Track profit for the cycle
        
        self.labouchere_list = [self.budget * 0.01 for _ in range(10)]  # 10% of bankroll divided into 10 parts
        self.labouchere_index = 0  # Track current position in the list

        self.sequence_1324 = [self.budget * 0.01, self.budget * 0.03, self.budget * 0.02, self.budget * 0.04]  # 1%, 3%, 2%, 4% of bankroll
        self.sequence_1324_index = 0  # Track index in the sequence

        self.current_bet_round = 0  # Track which betting system to use

        
    
    def calculate_bet_amount(self):
        # Use the initial budget instead of the current budget for calculations
        total_bankroll = self.initial_budget

        # Rotate betting system by incrementing the bet round
        self.current_bet_round += 1

        if self.current_bet_round % 3 == 1:  # Oscar's Grind
            bet_amount = self.oscar_bet
            self.last_bet_amount = bet_amount  # Track the last bet amount
            print(f"Oscar's Grind bet: ${bet_amount:.2f}")
            return bet_amount

        elif self.current_bet_round % 3 == 2:  # Labouchere
            if len(self.labouchere_list) > 1:
                bet_amount = self.labouchere_list[0] + self.labouchere_list[-1]
            else:
                bet_amount = self.labouchere_list[0]
            self.last_bet_amount = bet_amount
            print(f"Labouchere bet: ${bet_amount:.2f}")
            print("Labouchere list: ",self.labouchere_list," len: ",len(self.labouchere_list))
            return bet_amount

        elif self.current_bet_round % 3 == 0:  # 1324 system
            bet_amount = self.sequence_1324[self.sequence_1324_index]
            self.last_bet_amount = bet_amount
            print(f"1324 system bet: ${bet_amount:.2f}")
            return bet_amount

    def update_betting_system(self, outcome):
        # Oscar's Grind update
        print("Updating Betting System - Current Bet Round:", self.current_bet_round)
        print("Outcome Comparison:", self.last_prediction, "vs", outcome)

        if self.current_bet_round % 3 == 1:  # Oscar's Grind betting system
            print("Oscar's Grind Current Bet:", self.oscar_bet)
            print("Oscar's Grind Profit:", self.oscar_profit)
            print("Oscar's Grind Target Unit (5% of initial budget):", self.oscar_unit)

            if self.last_prediction == outcome:  # Win
                self.oscar_profit += self.oscar_bet
                print("Win! New Oscar Profit:", self.oscar_profit)

                if self.oscar_profit <= self.oscar_unit:  # Still below goal
                    self.oscar_bet += self.oscar_unit  # Increase bet by 1 unit
                    print("Bet increased by 1 unit. New Oscar's Grind Bet:", self.oscar_bet)
                else:  # Goal reached or exceeded
                    self.oscar_bet = self.initial_budget * 0.05  # Reset to 1 unit
                    self.oscar_profit = 0  # Start a new cycle
                    print("Goal achieved! Resetting Oscar's Grind bet to 1 unit:", self.oscar_bet)
                    print("Oscar's Grind profit reset for new cycle.")

            else:  # Loss case
                print("Loss. Oscar's Grind Bet remains the same:", self.oscar_bet)
            # Loss case: continue with the same bet
        # Labouchere update
        elif self.current_bet_round % 3 == 2:
            if self.last_prediction == outcome:  # Win
                if len(self.labouchere_list) > 1:
                    self.labouchere_list.pop(0)
                    self.labouchere_list.pop(-1)
                if not self.labouchere_list:  # Reset cycle if all numbers removed
                    self.labouchere_list = [self.initial_budget * 0.01 for _ in range(10)]
            else:  # Loss
                lost_amount = self.labouchere_list[0] + self.labouchere_list[-1]
                self.labouchere_list.append(lost_amount)  # Add lost amount to the end

        # 1324 system update
        elif self.current_bet_round % 3 == 0:
            if self.last_prediction == outcome:  # Win
                if self.sequence_1324_index == len(self.sequence_1324) - 1:
                    self.sequence_1324_index = 0  # Reset to start after full cycle
                else:
                    self.sequence_1324_index += 1  # Advance in sequence
            else:  # Loss
                self.sequence_1324_index = 0  # Reset to first unit


    def set_budget(self):
        budget_text = self.budgetInput.text()
        
        try:
            budget = float(budget_text)

            if budget <= 0:
                QMessageBox.warning(self, 'Invalid Budget', 'Budget must be greater than zero.')
                return

            # Set initial and current budget
            self.budget = budget
            self.initial_budget = budget  # Store initial budget separately
            self.budgetDisplay.setText(f"Budget: ${self.budget:.2f}")

            # Reset budget history and total profit
            self.budget_history = [(self.budget, 0)]  # Start with initial budget and no change
            self.total_profit = 0

            # Initialize/reset betting systems based on initial budget
            self.oscar_unit = self.initial_budget * 0.05  # 5% of initial budget as 1 unit
            self.oscar_bet = self.oscar_unit  # Start with 1 unit
            self.oscar_profit = 0  # Reset profit tracker

            self.labouchere_list = [self.initial_budget * 0.01 for _ in range(10)]  # 10% of initial budget split
            self.sequence_1324 = [self.initial_budget * 0.01, self.initial_budget * 0.03,
                                self.initial_budget * 0.02, self.initial_budget * 0.04]
            self.sequence_1324_index = 0  # Start at first in sequence

            print(f"Initial Budget set to: ${self.initial_budget:.2f}")
            self.budgetInput.clear()
            self.update_budget_display()  # Display the new initial budget in the log

        except ValueError:
            QMessageBox.warning(self, 'Invalid Input', 'Please enter a valid number for the budget.')

    def update_budget(self, outcome):
        # Ensure budget tracking is enabled
        if self.budget_tracking_enabled:
            
            bet_amount = self.last_bet_amount if self.last_bet_amount else 1  # Use last bet amount
            previous_budget = self.budget
            change = bet_amount if self.last_prediction == outcome else -bet_amount

            # Update budget and record change
            self.budget += change
            self.total_profit += change
            self.budget_history.append((self.budget, change))
            self.update_betting_system(outcome)
            self.update_budget_display()  # Display the updated budget   
    def update_budget_display(self):
        # Clear the text area first
        self.budgetDisplay.clear()

        # Log the initial budget with comma formatting
        initial_budget = f"{self.budget_history[0][0]:,.2f}"
        self.budgetDisplay.append(f"Initial Budget: ${initial_budget}")

        # Log all changes in budget with color and comma formatting
        for new_budget, change in self.budget_history[1:]:  # Skip the initial budget
            sign = "+" if change >= 0 else ""
            color = "#3C7ADA" if change >= 0 else "#FE0009"  # Blue for profit, red for loss
            new_budget_formatted = f"{new_budget:,.2f}"
            change_formatted = f"{change:,.2f}"
            
            # Apply color styling to the change amount
            self.budgetDisplay.append(
                f"{new_budget_formatted} ...... <span style='color:{color};'>{sign}{change_formatted}</span>"
            )

        # Log the total profit with comma formatting
        total_profit_formatted = f"{self.total_profit:,.2f}"
        self.budgetDisplay.append(f"\nTotal Profit: ${total_profit_formatted}")

    




    
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
            # Now update the budget after the result is logged
            if self.last_prediction is not None:
                self.update_budget(result)


    def setup_label(self, label, text, color):
        label.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 17px; 
            color: white; 
            margin: 5px; 
            min-height:34px;
            min-width:34px;
            max-height:34px;
            max-width:34px;
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

        # Reset the prediction cache
        self.last_prediction = None
        self.last_winning_rate = None
        self.last_bet_amount = None
        self.prediction_history_size = 0

        # Reset the progress bar
        self.progressBarAIAnalysis.setValue(0)
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
        # Cache the prediction results
        if predicted_outcome=='Banker':
            predicted_outcome='Bank'
        self.last_prediction = predicted_outcome
        self.last_winning_rate = winning_rate
        self.prediction_history_size = len(self.results_history)

        # Calculate the bet amount based on the current betting system
        self.last_bet_amount = self.calculate_bet_amount()

        

        # Display the prediction
        self.display_prediction(predicted_outcome, winning_rate, self.last_bet_amount)



    

    def display_prediction(self, predicted_outcome, winning_rate, bet_amount):
    # Ensure the predictionOutcomeFrame has a layout
        if not self.predictionOutcomeFrame.layout():
            self.predictionOutcomeFrame.setLayout(QVBoxLayout())

        # Clear the existing prediction outcome frame
        layout = self.predictionOutcomeFrame.layout()
        if layout:  # Check if layout exists
            for i in reversed(range(layout.count())): 
                widget = layout.itemAt(i).widget() 
                if widget is not None: 
                    widget.deleteLater()  # Properly delete the widget

        # Create a label for the prediction outcome
        labelPredictionOutcome = QLabel("")
        labelPredictionOutcome.setAlignment(Qt.AlignCenter)

        # Set the proper color and text based on the predicted outcome
        if predicted_outcome == "Player":
            self.setup_label_prediction(labelPredictionOutcome, "P", "#3E8AEF")  # Blue for Player
        elif predicted_outcome == "Tie":
            self.setup_label_prediction(labelPredictionOutcome, "T", "#29BE66")  # Green for Tie
        elif predicted_outcome == "Bank":
            self.setup_label_prediction(labelPredictionOutcome, "B", "#FF0000")  # Red for Banker

        # Add the new prediction label to the layout
        layout.addWidget(labelPredictionOutcome)

        # Set winning rate and bet amount text
        self.labelWinningRate.setText(f"Winning Rate: {winning_rate}%")
        self.labelBetAmount.setText(f"Bet Amount: ${bet_amount:.2f}")

    def remove_last_result(self):
        if self.results_history and self.labels_history:
            last_result, row, col = self.results_history.pop()
            last_label = self.labels_history.pop()

            self.grid_layout.removeWidget(last_label)
            last_label.deleteLater()

            if self.current_row[col] > 0:
                self.current_row[col] -= 1

    def reset_logs(self):
        # Clear the QTextEdit for budget logs
        self.budgetDisplay.clear()

        # Optionally, reset the budget history and total profit as well
        self.budget_history = []
        self.total_profit = 0
        self.budgetDisplay.setText(f"Budget: $0")

    def setup_label_prediction(self, label, text, color):
        label.setStyleSheet(f"""
            background-color: {color}; 
            border-radius: 25px; 
            color: white; 
            min-width:50px;
            max-width:50px;
            min-height:50px;
            max-height:50px;            
        """)
        label.setText(text)

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
            self.budget_tracking_enabled = True
            print("Budget tracking ON")
        else:
            self.budget_tracking_enabled = False
            print("Budget tracking OFF")

    def maximize_window(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()
    # Define the mousePressEvent method to handle mouse button press events
    def mousePressEvent(self, event: QMouseEvent) -> None:
        if event.button() == Qt.LeftButton:
            self.dragPos = event.globalPos() - self.pos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent) -> None:
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPos)
            event.accept()

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
