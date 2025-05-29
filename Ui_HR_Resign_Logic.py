from PyQt5.QtWidgets import QDialog
from Ui_HR_Resign import Ui_HR_Resign
from PyQt5.QtCore import QObject, QDate, Qt
from DatabaseOperations import DatabaseOperations
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
class Ui_HR_Resign_Logic(QObject):
    def __init__(self, sql_connector, employee_id):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.employee_id = employee_id
        self.ui = Ui_HR_Resign()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()
    
    def initialize(self, window):
        self.ui.dateEdit.setDate(QDate.currentDate())
        self.ui.resign_btn.clicked.connect(lambda: self.resign(window))
        self.ui.cancel_btn.clicked.connect(lambda: window.close())

    def resign(self, window):
        date = self.ui.dateEdit.date().toString(Qt.ISODate)
        self.database_operations.resign(self.employee_id, date)
        window.accept()