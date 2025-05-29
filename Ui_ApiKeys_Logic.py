from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_ApiKeys import Ui_ApiKeys
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_ApiKeys_Logic(QDialog):
    def __init__(self, sql_connector , progress=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ApiKeys()
        self.progress = progress
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowModality(QtCore.Qt.WindowModal)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.ui.save_btn.clicked.connect(lambda: self.saveApiKey(window))
    
    def saveApiKey(self, window):
        key_name = self.ui.key_name_input.text()
        key_value = self.ui.key_value_input.text()
        key_name = key_name.replace(' ', '_').lstrip()
        key_name = "setting_" + key_name
        self.database_operations.saveSetting(key_name, key_value)
        window.close()
