import win32api
from PyQt5.QtWidgets import QDialog

from UiStyles import UiStyles
from DatabaseOperations import DatabaseOperations
from Ui_ResetPassword import Ui_ResetPassword
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_ResetPassword_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector , user_id):
        super().__init__()
        self.sql_connector = sql_connector
        self.ui = Ui_ResetPassword()
        self.user_id = user_id
        self.database_operations = DatabaseOperations(sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_reset_password = QDialog()
        self.ui.setupUi(window_reset_password)
        self.initialize(window_reset_password)
        self.language_manager.load_translated_ui(self.ui, window_reset_password)
        window_reset_password.exec()

    def initialize(self, window):
        self.ui.password_input.setEchoMode(self.ui.password_input.Password)
        self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Password)
        self.ui.password_toggle.clicked.connect(lambda: self.togglePasswordVisibility())
        self.ui.confirm_password_toggle.clicked.connect(lambda: self.toggleConfirmPasswordVisibility())
        self.ui.save_btn.clicked.connect(lambda: self.resetPassword(window))


    def togglePasswordVisibility(self):
        if self.ui.password_input.echoMode() == self.ui.password_input.Password:
            self.ui.password_input.setEchoMode(self.ui.confirm_password_input.Normal)
            self.ui.password_toggle.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.password_input.setEchoMode(self.ui.confirm_password_input.Password)
            self.ui.password_toggle.setIcon(QIcon("icons/eye_closed.png"))


    def toggleConfirmPasswordVisibility(self):
        if self.ui.confirm_password_input.echoMode() == self.ui.confirm_password_input.Password:
            self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Normal)
            self.ui.confirm_password_toggle.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.confirm_password_input.setEchoMode(self.ui.confirm_password_input.Password)
            self.ui.confirm_password_toggle.setIcon(QIcon("icons/eye_closed.png"))


    def resetPassword(self,window):
        password = self.ui.password_input.text()
        confirm_password = self.ui.confirm_password_input.text()
        if password != confirm_password:
            win32api.MessageBox(0, self.language_manager.translate("PASSWORDS_NOT_MATCH"), self.language_manager.translate("ERROR"))
            return
        
        self.database_operations.ResetUserPassword(self.user_id, password)
        window.accept()




