import win32api
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from win32con import MB_OKCANCEL, IDCANCEL

from DatabaseOperations import DatabaseOperations
from Ui_ExpensesSettings import Ui_ExpensesSettings
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_ExpensesSettings_Logic(QDialog):
    def __init__(self, sql_connector, progress=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ExpensesSettings()
        self.progress = progress
        if self.progress:   
            self.progress.show()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchExpensesTypes()
        self.fetchAccounts()
        self.ui.accounts_combobox.setEnabled(False)
        self.ui.opposite_accounts_combobox.setEnabled(False)
        self.ui.select_accounts_btn.clicked.connect(lambda: self.openSelectAccountsWindow())
        self.ui.select_opposite_accounts_btn.clicked.connect(lambda: self.openSelectOppositeAccountsWindow())
        self.ui.add_expense_btn.clicked.connect(lambda: self.saveExpenseType())
        self.ui.add_expense_btn.clicked.connect(lambda: self.fetchExpensesTypes())
        self.ui.delete_expense_btn.clicked.connect(lambda: self.deleteExpenseType())
        self.ui.delete_expense_btn.clicked.connect(lambda: self.fetchExpensesTypes())
        if self.progress:
            self.progress.close()

    def openSelectAccountsWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(result['id']))

    def openSelectOppositeAccountsWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.opposite_accounts_combobox.setCurrentIndex(self.ui.opposite_accounts_combobox.findData(result['id']))

    def fetchAccounts(self):
        # Add None options
        self.ui.accounts_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.opposite_accounts_combobox.addItem(self.language_manager.translate("NONE"), None)

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.accounts_combobox.addItem(display_text, data)
            self.ui.opposite_accounts_combobox.addItem(display_text, data)

    def saveExpenseType(self):
        name = self.ui.name_input.text()
        account_id = self.ui.accounts_combobox.currentData()
        opposite_account_id = self.ui.opposite_accounts_combobox.currentData()
        calculate_in_manufacture = int(self.ui.calculated_in_manufacture_checkbox.isChecked())

        if str(name) == "":
            win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ALERT"))

        elif account_id is None and opposite_account_id is not None or account_id is not None and opposite_account_id is None:
            win32api.MessageBox(0, self.language_manager.translate("ACCOUNT_OR_OPPOSITE_CANNOT_BE_NONE"), self.language_manager.translate("ALERT"))

        elif account_id is None and opposite_account_id is None and calculate_in_manufacture == 1:
            win32api.MessageBox(0, self.language_manager.translate("ACCOUNT_AND_OPPOSITE_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))

        else:
            self.database_operations.addExpenseType(name, account_id, opposite_account_id,
                                                    calculate_in_manufacture)
            # Clear Fields
            self.ui.name_input.clear()
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(None))
            self.ui.opposite_accounts_combobox.setCurrentIndex(
                self.ui.opposite_accounts_combobox.findData(None))

    def deleteExpenseType(self):
        table_row = self.ui.expenses_types_table.item(self.ui.expenses_types_table.currentRow(), 0)
        if table_row and table_row.text():
            if win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_OKCANCEL) == IDCANCEL:
                pass
            else:
                expense_type_id = table_row.text()
                self.database_operations.removeExpenseType(expense_type_id)
                # Clear Fields
                self.ui.name_input.clear()
                self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(None))
                self.ui.opposite_accounts_combobox.setCurrentIndex(
                    self.ui.opposite_accounts_combobox.findData(None))

    def fetchExpensesTypes(self):
        self.ui.expenses_types_table.setRowCount(0)
        expenses_types = self.database_operations.fetchExpensesTypes()
        for expense_type in expenses_types:
            id = expense_type[0]
            name = expense_type[1]
            account_id = expense_type[2]
            opposite_account_id = expense_type[3]
            calculated_in_manufacture = expense_type[4]
            account_name = expense_type[5]
            opposite_account_name = expense_type[6]

            # Create an empty row at the bottom of the table
            numRows = self.ui.expenses_types_table.rowCount()
            self.ui.expenses_types_table.insertRow(numRows)

            # Add text to the row
            self.ui.expenses_types_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.expenses_types_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
            self.ui.expenses_types_table.setItem(numRows, 2, QTableWidgetItem(str(account_id)))
            self.ui.expenses_types_table.setItem(numRows, 3, QTableWidgetItem(str(account_name)))
            self.ui.expenses_types_table.setItem(numRows, 4, QTableWidgetItem(str(opposite_account_id)))
            self.ui.expenses_types_table.setItem(numRows, 5, QTableWidgetItem(str(opposite_account_name)))

            # Display check mark or X mark based on calculated_in_manufacture value
            check_mark = QTableWidgetItem('✔') if calculated_in_manufacture == 1 else QTableWidgetItem('❌')
            self.ui.expenses_types_table.setItem(numRows, 6, check_mark)
