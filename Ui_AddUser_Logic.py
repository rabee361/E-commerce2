from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from Ui_AddUser import Ui_Dialog
import win32api
from PyQt5.QtGui import QIcon
from DatabaseOperations import DatabaseOperations
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_AddUser_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.ui.password_input.setEchoMode(self.ui.password_input.Password)
        self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Password)
        self.ui.save_btn.clicked.connect(lambda: self.addUser(window))
        self.ui.password_btn.clicked.connect(lambda: self.togglePasswordVisibility())
        self.ui.confirm_password_btn.clicked.connect(lambda: self.toggleConfirmPasswordVisibility())

    def togglePasswordVisibility(self):
        if self.ui.password_input.echoMode() == self.ui.password_input.Password:
            self.ui.password_input.setEchoMode(self.ui.password_input.Normal)
            self.ui.password_btn.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.password_input.setEchoMode(self.ui.password_input.Password)
            self.ui.password_btn.setIcon(QIcon("icons/eye_closed.png"))

    def toggleConfirmPasswordVisibility(self):
        if self.ui.confirm_password_input.echoMode() == self.ui.confirm_password_input.Password:
            self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Normal)
            self.ui.confirm_password_btn.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Password)
            self.ui.confirm_password_btn.setIcon(QIcon("icons/eye_closed.png"))


    def addUser(self, window):
        username = self.ui.username_input.text()
        password = self.ui.password_input.text()
        conform_password = self.ui.confirm_password_input.text()

        if password != conform_password:
            win32api.MessageBox(0, 'كلمة المرور و تأكيد كلمة المرور يجب أن تكون متطابقة.', "تنبيه")
            return
        
        self.database_operations.addUser(username, password=password)
        window.accept()



