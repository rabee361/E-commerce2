from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_WarehouseVariables import Ui_WarehouseVariables
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_WarehouseVariables_Logic(QDialog):
    def __init__(self, sql_connector, progress=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_WarehouseVariables()
        self.progress = progress
        if self.progress:
            self.progress.show()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_warehouse_variables = QDialog()
        self.ui.setupUi(window_warehouse_variables)
        self.initialize(window_warehouse_variables)
        self.language_manager.load_translated_ui(self.ui, window_warehouse_variables)
        window_warehouse_variables.exec()

    def initialize(self, ui):
        self.ui.pushButton.clicked.connect(lambda: self.saveApiPrefix())
        self.ui.pushButton.clicked.connect(ui.accept)
        self.fetchApiPrefix()
        if self.progress:
            self.progress.close()

    def fetchApiPrefix(self):
        api_prefix = self.database_operations.fetchApiPrefix()[0][2]
        print(type( self.ui.lineEdit))
        self.ui.lineEdit.setText(str(api_prefix))


    def saveApiPrefix(self):
        api_prefix = self.ui.lineEdit.text()
        self.database_operations.updateApiPrefix(str(api_prefix))
