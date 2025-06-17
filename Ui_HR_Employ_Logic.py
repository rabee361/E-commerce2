from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_HR_Employ import Ui_HR_Employ
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
import win32api
from LanguageManager import LanguageManager
from PyQt5.QtWidgets import QComboBox, QPushButton
from PyQt5.QtCore import QTranslator

class Ui_HR_Employ_Logic(QDialog):
    def __init__(self, sql_connector, employment_request_id, independent=False):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_HR_Employ()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)
        self.employment_request_id = employment_request_id
        self.independent = independent

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        if self.independent:
            self.DisableAccountInputs()
        window.exec()


    def DisableAccountInputs(self):
        # Find and disable all comboboxes and buttons containing "account" in their name
        for widget in self.ui.__dict__.values():
            if isinstance(widget, (QComboBox, QPushButton)) and "account" in widget.objectName().lower():
                if isinstance(widget, QComboBox):
                    widget.clear()  # Clear the combobox items before disabling
                widget.setEnabled(False)


    def initialize(self,window):
        self.ui.start_date_input.setDate(QDate.currentDate())
        self.ui.select_salary_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.salary_account_combobox))
        self.ui.select_salary_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.salary_opposite_account_combobox))
        self.fetchDepartments()
        self.fetchPositions()
        self.fetchAccounts()
        self.ui.employ_btn.clicked.connect(lambda: self.employ(window))

    def openSelectAccountWindow(self, combobox):
        # Update accounts combobox
        self.fetchAccounts()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            self.ui.salary_account_combobox.addItem(display_text, id)
            self.ui.salary_opposite_account_combobox.addItem(display_text, id)

    def employ(self, window):
        department = self.ui.departments_combobox.currentData()
        position = self.ui.positions_combobox.currentData()
        if department and position:
            start_date = self.ui.start_date_input.date().toString(Qt.ISODate)
            salary_account = self.ui.salary_account_combobox.currentData()
            salary_opposite_account = self.ui.salary_opposite_account_combobox.currentData()
            self.database_operations.employ(self.employment_request_id, department, position, start_date, salary_account, salary_opposite_account)
            window.accept()
        else:
            msg = self.language_manager.translate('HR_DEPARTMENT_AND_POSITION_MUST_BE_SELECTED')
            win32api.MessageBox(0, msg, "تنبيه")
            return


    def fetchDepartments(self):
        dapartments = self.database_operations.fetchDepartments()
        for dapartment in dapartments:
            id = dapartment[0]
            name = dapartment[1]
            account_id = dapartment[2]
            opposite_account_id = dapartment[3]
            notes = dapartment[4]

            self.ui.departments_combobox.addItem(name, id)

    def fetchPositions(self):
        positions = self.database_operations.fetchPositions()
        for position in positions:
            id = position[0]
            position_name = position[1]
            salary = position[2]
            currency_id = position[3]
            notes = position[4]
            self.ui.positions_combobox.addItem(position_name, id)


