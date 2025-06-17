import win32api
from PyQt5.QtWidgets import QDialog
from PyQt5 import QtWidgets

from UiStyles import UiStyles
from DatabaseOperations import DatabaseOperations
from Ui_AuthenticateUser_Logic import current_user
from Ui_DBPassword import Ui_DBPassword
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_DBPassword_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector, user_id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.ui = Ui_DBPassword()
        self.user_id = user_id
        self.database_operations = DatabaseOperations(sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_db_password = QDialog()
        self.ui.setupUi(window_db_password)
        self.language_manager.load_translated_ui(self.ui, window_db_password)
        self.initialize(window_db_password)
        return window_db_password.exec()

    def initialize(self, window):
        self.ui.password_input.setEchoMode(self.ui.password_input.Password)
        self.ui.password_toggle.clicked.connect(lambda: self.togglePasswordVisibility())
        self.ui.save_btn.clicked.connect(lambda: self.savePassword(window))

    def togglePasswordVisibility(self):
        if self.ui.password_input.echoMode() == self.ui.password_input.Password:
            self.ui.password_input.setEchoMode(self.ui.password_input.Normal)
            self.ui.password_toggle.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.password_input.setEchoMode(self.ui.password_input.Password)
            self.ui.password_toggle.setIcon(QIcon("icons/eye_closed.png"))

    def savePassword(self, window):
        global current_user
        password = self.ui.password_input.text()
        if not password:
            win32api.MessageBox(0, self.language_manager.translate("ALERT_ENTER_PASSWORD"), self.language_manager.translate("ERROR"))
            return
        
        if self.user_id:
            self.database_operations.ResetUserPassword(self.user_id, password)
        else:
            self.database_operations.createOwner(password)
        
        window.accept()
