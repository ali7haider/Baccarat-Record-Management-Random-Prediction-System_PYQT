from PyQt5.QtWidgets import QApplication, QMainWindow,QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMouseEvent
from login_ui import Ui_MainWindow  # Import the generated class
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
        user_data = [
        ("tlgroup10128", "tony101"),
        ("tlgroup10228", "tony102"),
        ("tlgroup10328", "tony103"),
        ("tlgroup10428", "tony104"),
        ("tlgroup10528", "tony105"),
        ("tlgroup10628", "tony106"),
        ("tlgroup10728", "tony107"),
        ("tlgroup10828", "tony108"),
        ("tlgroup10928", "tony109"),
        ("tlgroup11028", "tony110"),
        ("tlgroup11128", "tony111"),
        ("tlgroup11228", "tony112"),
        ("tlgroup11328", "tony113"),
        ("tlgroup11428", "tony114"),
        ("tlgroup11528", "tony115"),
        ("tlgroup11628", "tony116"),
        ("tlgroup11728", "tony117"),
        ("tlgroup11828", "tony118"),
        ("tlgroup11928", "tony119"),
        ("tlgroup12028", "tony120"),
        ("tlgroup12128", "tony121"),
        ("tlgroup12228", "tony122"),
        ("tlgroup12328", "tony123"),
        ("tlgroup12428", "tony124"),
        ("tlgroup12528", "tony125"),
        ("tlgroup12628", "tony126"),
        ("tlgroup12728", "tony127"),
        ("tlgroup12828", "tony128"),
        ("tlgroup12928", "tony129"),
        ("tlgroup13028", "tony130"),
        ("tlgroup13128", "tony131"),
        ("tlgroup13228", "tony132"),
        ("tlgroup13328", "tony133"),
        ("tlgroup13428", "tony134"),
        ("tlgroup13528", "tony135"),
        ("tlgroup13628", "tony136"),
        ("tlgroup13728", "tony137"),
        ("tlgroup13828", "tony138"),
        ("tlgroup13928", "tony139"),
        ("tlgroup14028", "tony140"),
        ("tlgroup14128", "tony141"),
        ("tlgroup14228", "tony142"),
        ("tlgroup14328", "tony143"),
        ("tlgroup14428", "tony144"),
        ("tlgroup14528", "tony145"),
        ("tlgroup14628", "tony146"),
        ("tlgroup14728", "tony147"),
        ("tlgroup14828", "tony148"),
        ("tlgroup14928", "tony149"),
        ("tlgroup15028", "tony150"),
        ("tlgroup15128", "tony151"),
        ("tlgroup15228", "tony152"),
        ("tlgroup15328", "tony153"),
        ("tlgroup15428", "tony154"),
        ("tlgroup15528", "tony155"),
        ("tlgroup15628", "tony156"),
        ("tlgroup15728", "tony157"),
        ("tlgroup15828", "tony158"),
        ("tlgroup15928", "tony159"),
        ("tlgroup16028", "tony160"),
        ("tlgroup16128", "tony161"),
        ("tlgroup16228", "tony162"),
        ("tlgroup16328", "tony163"),
        ("tlgroup16428", "tony164"),
        ("tlgroup16528", "tony165"),
        ("tlgroup16628", "tony166"),
        ("tlgroup16728", "tony167"),
        ("tlgroup16828", "tony168"),
        ("tlgroup16928", "tony169"),
        ("tlgroup17028", "tony170"),
        ("tlgroup17128", "tony171"),
        ("tlgroup17228", "tony172"),
        ("tlgroup17328", "tony173"),
        ("tlgroup17428", "tony174"),
        ("tlgroup17528", "tony175"),
        ("tlgroup17628", "tony176"),
        ("tlgroup17728", "tony177"),
        ("tlgroup17828", "tony178"),
        ("tlgroup17928", "tony179"),
        ("tlgroup18028", "tony180"),
        ("tlgroup18128", "tony181"),
        ("tlgroup18228", "tony182"),
        ("tlgroup18328", "tony183"),
        ("tlgroup18428", "tony184"),
        ("tlgroup18528", "tony185"),
        ("tlgroup18628", "tony186"),
        ("tlgroup18728", "tony187"),
        ("tlgroup18828", "tony188"),
        ("tlgroup18928", "tony189"),
        ("tlgroup19028", "tony190"),
        ("tlgroup19128", "tony191"),
        ("tlgroup19228", "tony192"),
        ("tlgroup19328", "tony193"),
        ("tlgroup19428", "tony194"),
        ("tlgroup19528", "tony195"),
        ("tlgroup19628", "tony196"),
        ("tlgroup19728", "tony197"),
        ("tlgroup19828", "tony198"),
        ("tlgroup19928", "tony199"),
        ("tlgroup20028", "tony200")
    ]

        # Loop through each user and insert them into the database
        for user_id, password in user_data:
            if not self.db_manager.insert_user(user_id, password, isActive=1):
                print(f"Failed to insert user: {user_id} - Username already exists.")
            else:
                print(f"Successfully inserted user: {user_id}")    # Connect login button click event to the login function
        self.btnLogIn.clicked.connect(self.check_credentials)

        # Connect the closeAppBtn button to the close method
        self.closeAppBtn.clicked.connect(self.close)

        # Connect the minimizeAppBtn button to the showMinimized method
        self.minimizeAppBtn.clicked.connect(self.showMinimized)
        
        # self.visit.linkActivated.connect(self.openWebLink)

    def check_credentials(self):
        try:
            # Get username and password input from the UI
            username = self.txtUsername.text()
            password = self.txtPassword.text()

            # Query the database for the entered username and password
            user = self.db_manager.get_user_by_credentials(username, password)

            if user:  # If user is found in the database
                from main import MainWindow  # Import here to avoid circular import
                self.main = MainWindow(self, self.db_manager, user)  # Pass DatabaseManager and user data
                self.main.show()
                self.close()
            else:
                self.lblError.setText("Invalid username or password")

        except Exception as e:
            # Show error message in a message box
            error_message = f"An error occurred while checking credentials: {str(e)}"
            QMessageBox.critical(self, "Error", error_message)

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
