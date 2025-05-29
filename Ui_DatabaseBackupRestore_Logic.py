import json
import os
import pipes
import datetime
from PyQt5.QtCore import QTranslator, QCoreApplication
import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog, QLineEdit

from Ui_DatabaseBackup import Ui_DatabaseBackupRestore
from LanguageManager import LanguageManager     


class Ui_DatabaseBackupRestore_Logic(object):
    def __init__(self, sqlconnector, database_name, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_name = database_name
        self.filemanager = filemanager
        self.address=''
        self.port=''
        self.username=''
        self.password=''
        self.mysqlpath=''
        self.restorefile=''
        self.ui = Ui_DatabaseBackupRestore()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_databse_backup = QDialog()
        self.ui.setupUi(window_databse_backup)
        self.language_manager.load_translated_ui(self.ui, window_databse_backup)
        self.initialize(window_databse_backup)
        window_databse_backup.exec()

    def initialize(self, window_databse_backup):
        window_databse_backup.setWindowTitle(self.language_manager.translate("DATABASE_BACKUP_AND_RESTORE"))
        self.ui.mysqlpath_btn.clicked.connect(lambda: self.setMysqlPath())
        self.ui.backup_btn.clicked.connect(lambda: self.exportDatabase())
        self.ui.filepick_btn.clicked.connect(lambda: self.pickRestoreFile())
        self.ui.restore_btn.clicked.connect(lambda: self.importDatabase())
        self.loadSettings()

    # Load settings
    def loadSettings(self):
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
        json_data = self.filemanager.readJsonFile(database_settings_file)
        try:
            self.address = json_data['connection_info'][0]['server']
            self.port = json_data['connection_info'][0]['port']
            self.username = json_data['connection_info'][0]['username']
            self.password = json_data['connection_info'][0]['password']
            self.mysqlpath = (json_data['connection_info'][0]['mysql']) if (json_data['connection_info'][0]['mysql']) else ('' if os.path.exists('mysqldump.exe') else None)

            if self.mysqlpath == '' or not self.mysqlpath:
                self.ui.mysqlpath_input.setPlaceholderText(str('default'))
            else:
                self.ui.mysqlpath_input.setText(str(self.mysqlpath))

        except Exception as e:
            win32api.MessageBox(0,str(e))


    def exportDatabase(self):
        try:
            BACKUP_PATH = self.filemanager.getFolderPath()
            # Getting current DateTime to create the separate backup folder like "20180817-123433".
            DATETIME = datetime.datetime.now()
            DATETIME = str(DATETIME)
            DATETIME = DATETIME.replace(" ","_")
            DATETIME = DATETIME.replace(":","-")

            db = self.database_name
            mysql_dump_path = os.path.join(self.mysqlpath.strip(), "mysqldump.exe")
            dumpcmd = mysql_dump_path+ " -h " + self.address + " -P " + self.port + " -u " + self.username + " -p" + self.password + " " + db + " > " + pipes.quote(
                BACKUP_PATH) + "/" + db + "_" + DATETIME + ".sql"
            print(dumpcmd)
            os.system(dumpcmd)
        except Exception as e:
            win32api.MessageBox(0, print(e))

    def pickRestoreFile(self):
        try:
            self.restorefile = self.filemanager.openFile('sql')
            self.ui.restorefilepath_input.setText(self.restorefile)
        except Exception as e:
            win32api.MessageBox(0, print(e))

    def importDatabase(self):
        db = self.database_name
        try:
            restorecmd = self.mysqlpath + "/mysql -h " + self.address + " -P " + self.port + " -u " + self.username + " -p" + self.password + " " + db + " <" + self.restorefile
            print(restorecmd)
            os.system(restorecmd)
            win32api.MessageBox(0, self.language_manager.translate("OPERATION_SUCCESS"), self.language_manager.translate("SUCCESS"))
        except Exception as e:
            win32api.MessageBox(0,print(e))


    def setMysqlPath(self):
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        database_settings_file = os.path.join(epsilon_dir, 'dbs.dat')

        try:
            folder_path = self.filemanager.getFolderPath()

            # Check if "mysqldumb.exe" exists in the provided directory
            file_path = os.path.join(folder_path, 'mysqldump.exe')
            if os.path.exists(file_path):
                self.mysqlpath = folder_path
                self.ui.mysqlpath_input.setText(folder_path)
            else:
                self.mysqlpath = ''     # Refers to "mysqldumb.exe" in same directory
                self.ui.mysqlpath_input.setPlaceholderText(str('default'))
                win32api.MessageBox(0, 'Invalid MySQL path', '')

            data = {}
            data["connection_info"] = []
            data["connection_info"].append({
                'server': self.address,
                'port': self.port,
                'username': self.username,
                'password': self.password,
                'mysql': self.mysqlpath
            })
            with open(database_settings_file, 'w') as outfile:
                json.dump(data, outfile)
        except Exception as e:
            win32api.MessageBox(0,print(e))


