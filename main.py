import sys
import uuid
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QHBoxLayout
)
from PyQt5.QtGui import QFont
from database import create_user, login
from PyQt5.QtCore import Qt

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(500, 200, 400, 300)
        self.setStyleSheet(open('qss/style.qss').read())

        layout = QVBoxLayout()

        title = QLabel("Login")
        title.setFont(QFont('Arial', 20))
        title.setAlignment(Qt.AlignCenter)

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        login_button = QPushButton("Login")
        login_button.clicked.connect(self.login)

        switch_button = QPushButton("Register")
        switch_button.clicked.connect(self.switch_to_register)

        layout.addWidget(title)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(login_button)
        layout.addWidget(switch_button)

        self.setLayout(layout)


    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()
        print("📥 login clicked:", username)

        success, data = login(username, password)
        print("login result:", success, data)

        if success:
            try:
                print("opening MainAppWindow")
                from mainapp import MainAppWindow
                self.main_app_window = MainAppWindow(data['user_id'])
                self.main_app_window.show()
                self.close()
            except Exception as e:
                print("error opening MainApp:", e)
                QMessageBox.critical(self, "Crash", str(e))
        else:
            QMessageBox.warning(self, "Login Failed", data)



    def switch_to_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()
        self.close()


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")
        self.setGeometry(500, 200, 400, 400)
        self.setStyleSheet(open('qss/style.qss').read())

        layout = QVBoxLayout()

        title = QLabel("Register")
        title.setFont(QFont('Arial', 20))
        title.setAlignment(Qt.AlignCenter)

        self.firstname_input = QLineEdit()
        self.firstname_input.setPlaceholderText("First Name")

        self.lastname_input = QLineEdit()
        self.lastname_input.setPlaceholderText("Last Name")

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Username")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Password")
        self.password_input.setEchoMode(QLineEdit.Password)

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("Email (optional)")

        register_button = QPushButton("Register")
        register_button.clicked.connect(self.register)

        switch_button = QPushButton("Back to Login")
        switch_button.clicked.connect(self.switch_to_login)

        layout.addWidget(title)
        layout.addWidget(self.firstname_input)
        layout.addWidget(self.lastname_input)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_input)
        layout.addWidget(self.email_input)
        layout.addWidget(register_button)
        layout.addWidget(switch_button)

        self.setLayout(layout)

    def register(self):
        firstname = self.firstname_input.text()
        lastname = self.lastname_input.text()
        username = self.username_input.text()
        password = self.password_input.text()
        email = self.email_input.text()

        success, message = create_user(firstname, lastname, username, password, email)
        if success:
            QMessageBox.information(self, "Success", "Registered successfully!")
            self.switch_to_login()
        else:
            QMessageBox.warning(self, "Error", message)

    def switch_to_login(self):
        self.login_window = LoginWindow()
        self.login_window.show()
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = LoginWindow()
    window.show()
    sys.exit(app.exec_())
