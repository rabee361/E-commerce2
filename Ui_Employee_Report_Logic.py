from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Employee_Report import Ui_Employee_Report
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QVBoxLayout
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color, black
from PyQt5.QtGui import QPalette
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32con 
from PyQt5.QtGui import QIcon
from CheckableComboBox import CheckableComboBox
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QValueAxis, QBarCategoryAxis, QLineSeries, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime, QDate
from collections import defaultdict


class Ui_Employee_Report_Logic(object):
    def __init__(self, sqlconnector, department_id=None):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Employee_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.department_id = department_id

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
        self.ui.from_date.setDate(QDate.currentDate())
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.select_employee_btn.clicked.connect(lambda: self.openSelectEmployeeWindow())
        self.fetchEmployees()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())

    def openSelectEmployeeWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'current_employees')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.employee_combobox.count()):
                if self.ui.employee_combobox.itemData(i)[0] == result['id']:
                    self.ui.employee_combobox.setCurrentIndex(i)
                    break

    def fetchEmployees(self):
        employees = self.database_operations.fetchEmployees(state='current')
        for employee in employees:
            id = employee['id']
            name = employee['name']
            self.ui.employee_combobox.addItem(name, id)

