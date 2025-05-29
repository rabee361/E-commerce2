import json
import os
from PyQt5.QtWidgets import QApplication
import win32api
from PyQt5.QtWidgets import QDialog
from win32con import MB_OKCANCEL, IDCANCEL

from PyQt5.QtGui import QIcon
from MysqlConnector import MysqlConnector
from UiStyles import UiStyles
from Ui_DatabaseNew_Logic import Ui_DatabaseNew_Logic
from Ui_DatabaseSettings import Ui_DatabaseSettings
from PyQt5.QtCore import QTranslator, QCoreApplication
from ProgressBar import ProgressBar
from LanguageManager import LanguageManager 
from PyQt5.QtCore import QTranslator

class Ui_DatabaseSettings_Logic(QDialog, UiStyles):
    filemanager=''
    database_name = ''
    server_address=''
    port=''
    username=''
    password=''
    mysql_path=''
    MysqlConnector= ''
    progress = ''
    translator = QTranslator()
    language_manager = LanguageManager(translator)


    def __init__(self, filemanager):
        super().__init__()
        self.filemanager=filemanager
        self.MysqlConnector = MysqlConnector(self.filemanager)
        self.ui = Ui_DatabaseSettings()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_databse_settings = QDialog()
        self.makeItBlurry(window_databse_settings)
        self.ui.setupUi(window_databse_settings)
        window_databse_settings.setWindowTitle(self.language_manager.translate("CONNECT_TO_REMOTE_DATABASE"))
        self.language_manager.load_translated_ui(self.ui, window_databse_settings)
        self.initialize(window_databse_settings)
        window_databse_settings.exec()

    def initialize(self, window):
        self.ui.connect_btn.clicked.connect(lambda: self.createDatabaseSettingsFile())
        self.ui.connect_db_btn.clicked.connect(lambda: self.connectToDatabase(window))
        self.ui.new_db_btn.clicked.connect(lambda: self.OpenCreateDatabaseWindow())
        self.ui.delete_db_btn.clicked.connect(lambda: self.removeDatabase())
        self.readDatabaseSettings()
        self.getDatabasesList()
        self.ui.password_btn.clicked.connect(self.togglePasswordVisibility)
        
        # Add double-click handler
        self.ui.databases_list.itemDoubleClicked.connect(lambda: self.connectToDatabase(window))

    def togglePasswordVisibility(self):
        if self.ui.password_input.echoMode() == self.ui.password_input.Password:
            self.ui.password_input.setEchoMode(self.ui.password_input.Normal)
            self.ui.password_btn.setIcon(QIcon("icons/eye_open.png"))
        else:
            self.ui.password_input.setEchoMode(self.ui.password_input.Password)
            self.ui.password_btn.setIcon(QIcon("icons/eye_closed.png"))

        print("Open connect to database window.")

    def readDatabaseSettings(self):
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        # Create 'epsilon' directory if it doesn't exist
        if not os.path.exists(epsilon_dir):
            os.makedirs(epsilon_dir)

        database_settings_file = os.path.join(epsilon_dir, 'dbs.dat')

        try:
            json_data = self.filemanager.readJsonFile(database_settings_file)
            self.server_address = json_data['connection_info'][0]['server']
            self.port = json_data['connection_info'][0]['port']
            self.username = json_data['connection_info'][0]['username']
            self.password = json_data['connection_info'][0]['password']
            self.mysql_path = json_data['connection_info'][0]['mysql']

            self.ui.server_input.setText(str(self.server_address))
            self.ui.port_input.setText(str(self.port))
            self.ui.username_input.setText(str(self.username))
            self.ui.password_input.setText(str(self.password))

            self.connectToServer()
            self.getDatabasesList()

        except Exception as e:
            print("Unable to read connection info data")
            self.createDatabaseSettingsFile()

    def createDatabaseSettingsFile(self):
        new_server_address = self.ui.server_input.text()
        new_port = self.ui.port_input.text()
        new_username = self.ui.username_input.text()
        new_password = self.ui.password_input.text()

        if new_server_address != '' and new_port != '' and new_username != '' and new_password != '':
            if os.name == 'nt':  # Check if running on Windows
                appdata_dir = os.getenv('APPDATA')
                epsilon_dir = os.path.join(appdata_dir, 'epsilon')
            else:
                appdata_dir = os.path.expanduser('~/.config')
                epsilon_dir = os.path.join(appdata_dir, 'epsilon')

            # Create 'epsilon' directory if it doesn't exist
            if not os.path.exists(epsilon_dir):
                os.makedirs(epsilon_dir)

            database_settings_file = os.path.join(epsilon_dir, 'dbs.dat')

            data = {}
            data["connection_info"] = []
            data["connection_info"].append({
                'server': new_server_address,
                'port': new_port,
                'username': new_username,
                'password': new_password,
                'mysql': self.mysql_path
            })
            with open(database_settings_file, 'w') as outfile:
                json.dump(data, outfile)
            self.connectToServer()
            self.getDatabasesList()
        else:
            win32api.MessageBox(0, self.language_manager.translate("SERVER_INFO_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))

    def connectToServer(self):
        self.MysqlConnector.connectToServer()

    def getDatabasesList(self):
        self.ui.databases_list.clear()
        databases = self.MysqlConnector.getDatabasesList()
        for database in databases:
            database = database.replace("(","")
            database = database.replace(")","")
            database = database.replace("'","")
            database = database.replace(",","")

            self.ui.databases_list.addItem(database)

    def connectToDatabase(self, window):
        # self.window().setEnabled(False)
        # self.window().setStyleSheet("QDialog { background-color: rgba(128, 128, 128, 0.3); }")  
        # self.progress = ProgressBar()
        # self.progress.start()
        # QApplication.processEvents() 
        database_name = self.ui.databases_list.currentItem()
        try:
            if database_name and database_name.text() != '':
                self.MysqlConnector.connectToDatabase(database_name.text())
                self.database_name = database_name.text()
                window.accept()
            else:
                win32api.MessageBox(0, self.language_manager.translate("DATABASE_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
        except Exception as e:
            win32api.MessageBox(0, self.language_manager.translate("CANNOT_CONNECT_TO_DATABASE"), self.language_manager.translate("ERROR"))

    def OpenCreateDatabaseWindow(self):
        Ui_DatabaseNew_Logic(self.MysqlConnector).showUi()
        self.getDatabasesList()

    def removeDatabase(self):
        try:
            db_name = self.ui.databases_list.currentItem().text()
            if db_name != '':
                confirm = win32api.MessageBox(0, self.language_manager.translate("DATABASE_DELETE_CONFIRMATION_1"), self.language_manager.translate("ALERT"), MB_OKCANCEL)
                if confirm == IDCANCEL:
                    pass
                else:
                    confirm2 = win32api.MessageBox(0, self.language_manager.translate("DATABASE_DELETE_CONFIRMATION_2"), self.language_manager.translate("ALERT"), MB_OKCANCEL)
                    if confirm2 == IDCANCEL:
                        pass
                    else:
                        self.MysqlConnector.deleteDatabase(db_name)
                        self.getDatabasesList()
        except:
            pass

    def getMysqlConnector(self):
        return self.MysqlConnector

    def getDatabsaeName(self):
        return self.database_name




