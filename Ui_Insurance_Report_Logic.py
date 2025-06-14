from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Insurance_Report import Ui_Insurance_Report
from PyQt5.QtWidgets import  QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem
from MyTableWidgetItem import MyTableWidgetItem


class Ui_Insurance_Report_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Insurance_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

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
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())

    def fetchDepartmentAvgfInsurance(self, from_date, to_date):
        insurance_info = self.database_operations.fetchDepartmentAvgfInsurance(from_date, to_date)
        self.ui.department_insurance_table.setRowCount(0)
        for insurance in insurance_info:
            position_name = insurance['position_name']
            avg = insurance['avg_insurance']
            sum = insurance['sum_insurance']
            numRows = self.ui.department_insurance_table.rowCount()
            self.ui.department_insurance_table.setItem(numRows, 0, QTableWidgetItem(str(position_name)))
            self.ui.department_insurance_table.setItem(numRows, 1, QTableWidgetItem(str(sum)))
            self.ui.department_insurance_table.setItem(numRows, 2, QTableWidgetItem(str(avg)))

    def fetchPositionAvgfInsurance(self, from_date, to_date):
        insurance_info = self.database_operations.fetchPositionAvgfInsurance(from_date, to_date)
        self.ui.positions_table.setRowCount(0)
        for insurance in insurance_info:
            avg = insurance['avg_insurance']
            sum = insurance['sum_insurance']
            numRows = self.ui.positions_table.rowCount()
            self.ui.positions_table.setItem(numRows, 1, QTableWidgetItem(str(sum)))
            self.ui.positions_table.setItem(numRows, 2, QTableWidgetItem(str(avg)))

    def fetchAvgfInsurance(self, from_date, to_date):
        insurance_info = self.database_operations.fetchAvgfInsurance(from_date, to_date)
        self.ui.insurance_table.setRowCount(0)
        for insurance in insurance_info:
            avg = insurance['avg_insurance']
            sum = insurance['sum_insurance']
            numRows = self.ui.insurance_table.rowCount()
            self.ui.insurance_table.setItem(numRows, 0, QTableWidgetItem(str(sum)))
            self.ui.insurance_table.setItem(numRows, 1, QTableWidgetItem(str(avg)))

    def calculate(self):
        from_date = self.ui.from_date.text()
        to_date = self.ui.to_date.text()
        self.fetchDepartmentAvgfInsurance(from_date, to_date)
        self.fetchPositionAvgfInsurance(from_date, to_date)
        self.fetchAvgfInsurance(from_date, to_date)

    def exportExcel(self):
        pass
