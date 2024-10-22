import sqlite3

class DatabaseManager:
    def __init__(self, db_file="data.db"):
        try:
            self.conn = sqlite3.connect(db_file)  # Connect to the SQLite database
            self.cursor = self.conn.cursor()  # Create a cursor object to execute SQL commands
        except sqlite3.Error as e:
            raise Exception(f"Error connecting to database: {e}")

    def create_table(self):
        try:
            # Create a new users table if it doesn't exist
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    password TEXT NOT NULL,
                    isActive INTEGER DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )''')
            self.conn.commit()  # Commit the transaction to save changes to the database
        except sqlite3.Error as e:
            raise Exception(f"Error creating table: {e}")
    def check_username_exists(self, username):
        try:
            # Check if a user with the given username already exists
            self.cursor.execute('''SELECT * FROM users WHERE username = ? AND isActive = 1''', (username,))
            return self.cursor.fetchone() is not None  # Return True if user exists, False otherwise
        except sqlite3.Error as e:
            raise Exception(f"Error checking username: {e}")
    def insert_user(self, username, password, isActive=1):
            try:
                # First, check if the username already exists
                if self.check_username_exists(username):
                    print(f"Error: Username '{username}' already exists.")
                    return False  # Return False indicating that the user was not inserted

                # Insert a new user into the database
                self.cursor.execute('''
                    INSERT INTO users (username, password, isActive)
                    VALUES (?, ?, ?)
                ''', (username, password, isActive))
                
                self.conn.commit()  # Commit the transaction to save the new user in the database
                print(f"User '{username}' inserted successfully.")
                return True  # Return True indicating that the user was inserted
            except sqlite3.Error as e:
                raise Exception(f"Error inserting user: {e}")
    def get_user_by_credentials(self, username, password):
        try:
            # Query the database for a user with matching username and password
            self.cursor.execute('''SELECT * FROM users WHERE username = ? AND password = ? AND isActive = 1''', (username, password))
            user = self.cursor.fetchone()  # Fetch one result (user data)
            return user  # Return user data or None if no match found
        except sqlite3.Error as e:
            raise Exception(f"Error retrieving user by credentials: {e}")