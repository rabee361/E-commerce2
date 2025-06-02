import win32api
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QHeaderView
from win32con import MB_YESNO, IDYES, IDNO, MB_OKCANCEL, IDCANCEL
from DatabaseOperations import DatabaseOperations
from Ui_AuthenticateUser import Ui_AuthenticateUser
from PyQt5 import QtCore
from cryptography.fernet import Fernet
import base64
from PyQt5.QtGui import QIcon
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

global current_user
current_user = 0

class Ui_AuthenticateUser_Logic(QDialog):
    def __init__(self, sql_connector, client_id=None, id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AuthenticateUser() 
        self.key = 'YourVerySecretKey123456789012345' # can be set to any 32 bytes string
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        # Disable the close button
        window.setWindowFlags(window.windowFlags() & ~QtCore.Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()
        return current_user

    def initialize(self, window):
        self.ui.password_input.setEchoMode(self.ui.password_input.Password)
        self.ui.login_btn.clicked.connect(lambda: self.authenticateUser(window))
        self.ui.cancel_btn.clicked.connect(lambda: self.cancelLogin(window))
        self.ui.password_btn.clicked.connect(self.togglePasswordVisibility)
        self.current_user = ''
        self.fetchUsers()
        self.ui.login_btn.setDefault(True)

    def togglePasswordVisibility(self):
        if self.ui.password_input.echoMode() == self.ui.password_input.Password:
            self.ui.password_input.setEchoMode(self.ui.password_input.Normal)
            self.ui.password_btn.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.password_input.setEchoMode(self.ui.password_input.Password)
            self.ui.password_btn.setIcon(QIcon("icons/eye_closed.png"))

    def fetchUsers(self):
        users = self.database_operations.fetchUsers()
        self.ui.user_combobox.clear()
        for user in users:
            self.ui.user_combobox.addItem(user['username'], user['id'])

    def getCurrentUser(self):
        # return the logged in user
        global current_user
        return current_user

    def cancelLogin(self, window):
        window.accept()

    def authenticateUser(self, window):
        global current_user # to access the current user in this methid and assign it
        username = self.ui.user_combobox.currentText()
        password = self.ui.password_input.text()
        # Decrypt the stored password for comparison
        user = self.database_operations.fetchUserByUsername(username)
        if user:
            try:
                key = base64.urlsafe_b64encode(self.key.encode('utf-8'))
                cipher = Fernet(key)
                # Decrypt the encrypted password from database
                decrypted_password = cipher.decrypt(user['password'].encode()).decode()
                if decrypted_password == password:
                    current_user = user['id']
                    window.accept()
                else:
                    win32api.MessageBox(0, self.language_manager.translate('INVALID_USERNAME_OR_PASSWORD_ERROR'), self.language_manager.translate('ERROR'))
            except Exception as e:
                win32api.MessageBox(0, self.language_manager.translate('CHECKING_PASSWORD_ERROR'), self.language_manager.translate('ERROR'))
