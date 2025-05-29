import win32api
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView
from win32con import IDCANCEL, MB_OKCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Expenses import Ui_Expenses
from Ui_ExpensesSettings_Logic import Ui_ExpensesSettings_Logic
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Expenses_Logic(QDialog):
    database_operations = ''
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations=DatabaseOperations(sqlconnector)
        self.ui = Ui_Expenses()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_expenses = QDialog()
        window_expenses.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_expenses)
        window_expenses.setWindowIcon(QIcon('icons/coin_dollar _silver.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_expenses)
        window_expenses.exec()

    def initialize(self):
        self.ui.expenses_input.setValidator(QDoubleValidator())

        for i in range (2000,3001):
            self.ui.expense_year_combobox.addItem(str(i), i)
        for i in range (1,13):
            self.ui.expense_month_combobox.addItem(str(i), i)

        self.ui.time_slot_combobox.addItem("شهرية", "month")
        self.ui.time_slot_combobox.addItem("سنوية", "year")

        self.ui.save_btn.clicked.connect(lambda: self.saveExpenses())
        self.ui.save_btn.clicked.connect(lambda: self.fetchExpenses())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteExpense())
        self.ui.delete_btn.clicked.connect(lambda: self.fetchExpenses())
        self.ui.expenses_settings_btn.clicked.connect(lambda: self.openAdvancedExpensesSettings())
        self.ui.expenses_settings_btn.clicked.connect(lambda: self.fetchExpenses())
        self.ui.time_slot_combobox.currentIndexChanged.connect(lambda: self.enableMonthlyExpenses())

        self.enableMonthlyExpenses()
        self.fetchExpenses()
        self.fetchCurrencies()
        self.fetchExpensesTypes()

        self.ui.select_expense_btn.clicked.connect(lambda: self.openExpensesTypesWindow())

    def openExpensesTypesWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'expenses_types')
        result = data_picker.showUi()
        if result:
            self.ui.expense_type_combobox.setCurrentIndex(self.ui.expense_type_combobox.findData(result['id']))

    def fetchExpensesTypes(self):
        expenses_types = self.database_operations.fetchExpensesTypes()
        for expense_type in expenses_types:
            id = expense_type[0]
            name = expense_type[1]
            account_id = expense_type[2]
            opposite_account_id = expense_type[3]
            calculated_in_manufacture = expense_type[4]
            account_name = expense_type[5]
            opposite_account_name = expense_type[6]
            self.ui.expense_type_combobox.addItem(name, id)

    def enableMonthlyExpenses(self):
        time_slot = self.ui.time_slot_combobox.currentData()
        if str(time_slot).lower().strip()=='month':
            self.ui.expense_month_combobox.setEnabled(True)
        else:
            self.ui.expense_month_combobox.setDisabled(True)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            display_text = currency[1]
            data = id
            self.ui.currency_combobox.addItem(display_text, data)

    def fetchExpenses(self):
        self.ui.expenses_table.setRowCount(0)
        expenses = self.database_operations.fetchExpenses()
        for expense in expenses:
            id = expense[0]
            time_slot = expense[1]
            value = expense[2]
            year = expense[3]
            month = expense[4]
            expense_type = expense[5]
            currency_id = expense[6]
            calculated_in_manufacture = expense[7]
            currency_name = expense[8]
            expense_name = expense[9]

            numRows = self.ui.expenses_table.rowCount()
            self.ui.expenses_table.insertRow(numRows)
            # Add text to the row
            self.ui.expenses_table.setItem(numRows, 0, QTableWidgetItem(str(id), id))
            self.ui.expenses_table.setItem(numRows, 1, QTableWidgetItem(str(expense_name)))
            self.ui.expenses_table.setItem(numRows, 2, QTableWidgetItem(str(time_slot)))
            self.ui.expenses_table.setItem(numRows, 3, MyTableWidgetItem(str(value), value))
            self.ui.expenses_table.setItem(numRows, 4, QTableWidgetItem(str(currency_id)))
            self.ui.expenses_table.setItem(numRows, 5, QTableWidgetItem(str(currency_name)))
            self.ui.expenses_table.setItem(numRows, 6, MyTableWidgetItem(str(year), year))
            self.ui.expenses_table.setItem(numRows, 7, MyTableWidgetItem(str(month), month))

    def saveExpenses(self):
        expenses = self.ui.expenses_input.text()
        currency = self.ui.currency_combobox.currentData()
        month = self.ui.expense_month_combobox.currentData()
        year = self.ui.expense_year_combobox.currentData()
        time_slot = self.ui.time_slot_combobox.currentData()
        expense_type = self.ui.expense_type_combobox.currentData()

        if str(time_slot).lower().strip() == 'year':
            month = ''

        if expense_type:
            if (str(expenses).strip()):
                self.database_operations.addExpenses(expenses, currency, month, year, time_slot, expense_type)
                self.ui.expenses_input.clear()
                self.ui.currency_combobox.setCurrentIndex(self.ui.currency_combobox.findData(0))
                self.ui.expense_type_combobox.setCurrentIndex(self.ui.expense_type_combobox.findData(0))
                self.ui.expense_month_combobox.setCurrentIndex(self.ui.expense_month_combobox.findData(0))
                self.ui.expense_year_combobox.setCurrentIndex(self.ui.expense_year_combobox.findData(0))
                self.ui.time_slot_combobox.setCurrentIndex(self.ui.time_slot_combobox.findData(0))
            else:
                win32api.MessageBox(0, 'يرجى ادخال قيمة المصاريف', 'خطأ')
        else:
            win32api.MessageBox(0, 'يرجى تحديد نوع المصروف', 'خطأ')

    def deleteExpense(self):
        table_row = self.ui.expenses_table.item(self.ui.expenses_table.currentRow(), 0)
        if table_row:
            confirm = win32api.MessageBox(0, "هل تريد بالتأكيد حذف المصروف؟", " ", MB_OKCANCEL)
            if confirm == IDCANCEL:
                pass
            else:
                if (str(type(table_row)) == "<class 'NoneType'>"):
                    pass
                else:
                    exchange_id = table_row.text()
                    self.database_operations.removeExpenses(exchange_id)

    def openAdvancedExpensesSettings(self):
        Ui_ExpensesSettings_Logic(self.sqlconnector).showUi()
        self.fetchExpensesTypes()
