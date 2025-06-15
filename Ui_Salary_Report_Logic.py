from tabnanny import check
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
        self.fetchDepartments()
        self.fetchPositions()
        self.fetchCurrencies()
        self.ui.salary_cycle_combobox.addItem(self.language_manager.translate("HOUR"), "hour")
        self.ui.salary_cycle_combobox.addItem(self.language_manager.translate("DAY"), "day")
        self.ui.salary_cycle_combobox.addItem(self.language_manager.translate("MONTH"), "month")
        self.ui.salary_cycle_combobox.addItem(self.language_manager.translate("YEAR"), "year")
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.select_department_btn.clicked.connect(lambda: self.openSelectDepartmentWindow())
        self.ui.select_position_btn.clicked.connect(lambda: self.openSelectPositionWindow())

    def openSelectDepartmentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'departments', checkable=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.department_combobox.count()):
                if self.ui.department_combobox.itemData(i)[0] == result['id']:
                    self.ui.department_combobox.setCurrentIndex(i)
                    break

    def openSelectPositionWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'positions', checkable=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.position_combobox.count()):
                if self.ui.position_combobox.itemData(i)[0] == result['id']:
                    self.ui.position_combobox.setCurrentIndex(i)
                    break

    def fetchDepartments(self):
        departments = self.database_operations.fetchDepartments()
        for department in departments:
            id = department['id']
            name = department['name']
            self.ui.department_combobox.addItem(name, id)

    def fetchPositions(self):
        positions = self.database_operations.fetchPositions()
        for position in positions:
            id = position['id']
            position_name = position['position_name']
            self.ui.position_combobox.addItem(position_name, id)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            display_text = str(name)
            data = id
            self.ui.currency_combobox.addItem(display_text, data)

    def calculate(self):
        department_id = self.ui.department_combobox.currentData()
        position_id = self.ui.position_combobox.currentData()
        currency_id = self.ui.currency_combobox.currentData()

        salary_blocks = self.database_operations.fetchPayrollsDetails(department=department_id, position=position_id)
        
