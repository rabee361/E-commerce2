from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_ProductionLines import Ui_ProductionLines
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_ProductionLines_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ProductionLines()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        pass