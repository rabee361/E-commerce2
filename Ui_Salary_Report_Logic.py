import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Salary_Report import Ui_Salary_Report
from PyQt5.QtWidgets import  QDialog
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color, black
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32con 
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class Ui_Salary_Report_Logic(object):
    def __init__(self, sqlconnector, position_id=None):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Salary_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.position_id = position_id

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/hr.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        pass
