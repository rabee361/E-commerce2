import Colors
import win32con
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QTranslator
from Ui_Loans import Ui_Loans
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator
import win32api
from datetime import datetime
from Ui_AddLoan_Logic import Ui_AddLoan_Logic

class Ui_Loans_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Loans()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/bookkeeper.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        pass
