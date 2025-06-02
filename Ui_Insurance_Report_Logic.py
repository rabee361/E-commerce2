from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Insurance_Report import Ui_Insurance_Report
from PyQt5.QtWidgets import  QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


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
        self.ui.filter_combobox.addItem(self.language_manager.translate("DATE"), "date")
        self.ui.filter_combobox.addItem(self.language_manager.translate("SALARY_BLOCK"), "salary_block")
        self.ui.filter_combobox.currentIndexChanged.connect(lambda: self.setFilterType())
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())

    def setFilterType(self):
        filter_type = self.ui.filter_combobox.currentData()
        if filter_type == "date":
            self.ui.salary_block_combobox.setDisabled(True)
            self.ui.from_date.setDisabled(False)
            self.ui.to_date.setDisabled(False)
        elif filter_type == "salary_block":
            self.ui.salary_block_combobox.setDisabled(False)
            self.ui.from_date.setDisabled(True)
            self.ui.to_date.setDisabled(True)

    def fetchInsuranceBlocks(self):
        salary_blocks = self.database_operations.fetchInsurancePayrollsDetails()
        for salary_block in salary_blocks:
            self.ui.salary_block_combobox.addItem(salary_block[1], salary_block[0])

    def fetchPositionPayrolls(self):
        from_date = self.ui.from_date.text()
        to_date = self.ui.to_date.text()
        salary_block_id = self.ui.salary_block_combobox.currentData()
        if from_date and to_date:
            payrolls = self.database_operations.fetchPositionPayrolls(from_date, to_date)
        elif salary_block_id:
            payrolls = self.database_operations.fetchPositionPayrollsBySalaryBlock(salary_block_id)
        
    def fetchDepartmentPayrolls(self):
        pass

    def calculate(self):
        insurance_blocks = self.database_operations.fetchInsurancePayrollsDetails()

