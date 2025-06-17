import Colors
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QTranslator
from Ui_AddLoan import Ui_AddLoan
from PyQt5.QtGui import QDoubleValidator
import win32api
from datetime import datetime

class Ui_AddLoan_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AddLoan()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        self.window = QDialog()
        self.ui.setupUi(self.window)
        self.window.setWindowIcon(QIcon('icons/bookkeeper.png'))
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.initialize(self.window)
        self.window.exec()

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchCurrencies()
        self.ui.loan_interest_input.setValidator(QDoubleValidator())
        self.ui.loan_amount_input.setValidator(QDoubleValidator())
        self.ui.loan_date_input.setDate(QDate.currentDate())
        self.ui.add_loan_btn.clicked.connect(lambda: self.addLoan())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.account_combobox))    
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.opposite_account_combobox))
        
        self.ui.loan_cycle_combobox.addItem('يومي', 'daily')
        self.ui.loan_cycle_combobox.addItem('أسبوعي', 'weekly')
        self.ui.loan_cycle_combobox.addItem('شهري', 'monthly')
        self.ui.loan_cycle_combobox.addItem('سنوي', 'yearly')
    
    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        self.ui.currency_combobox.clear()
        for currency in currencies:
            self.ui.currency_combobox.addItem(currency['name'], currency['id'])

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        self.ui.account_combobox.clear()
        self.ui.account_combobox.addItem('لا يوجد', 0)
        self.ui.opposite_account_combobox.clear()
        self.ui.opposite_account_combobox.addItem('لا يوجد', 0)
        for account in accounts:
            self.ui.account_combobox.addItem(account['name'], account['id'])
            self.ui.opposite_account_combobox.addItem(account['name'], account['id'])

    def openSelectAccountWindow(self, combobox):
        data_picker_logic = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker_logic.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))


    def openSelectOppositeAccountWindow(self):
        self.data_picker_logic = Ui_DataPicker_Logic(self.sql_connector)
        self.data_picker_logic.showUi()

    def addLoan(self):
        try:
            name = self.ui.loan_name_input.text()
            amount = self.ui.loan_amount_input.text()
            currency = self.ui.currency_combobox.currentData()
            date = self.ui.loan_date_input.date().toString('yyyy-MM-dd')
            account_id = self.ui.account_combobox.currentData()
            opposite_account_id = self.ui.opposite_account_combobox.currentData()
            cycle = self.ui.loan_cycle_combobox.currentData()
            interest = self.ui.loan_interest_input.text()
            statement = 'loan payment'

            loan_id = self.database_operations.addLoan(name, amount, date, account_id, opposite_account_id, cycle, currency, interest)

            self.addLoanJournalEntry(loan_id)
            self.window.accept()

        except Exception as e:
            win32api.MessageBox(0, self.language_manager.translate("ERROR"), self.language_manager.translate("ERROR"), 0)


    def addLoanJournalEntry(self, loan_id):
        try:
            account_id = self.ui.account_combobox.currentData()
            opposite_account_id = self.ui.opposite_account_combobox.currentData()
            currency = self.ui.currency_combobox.currentData()
            statment = 'loan'
            date_col = datetime.now().strftime('%Y-%m-%d')
            amount = self.ui.loan_amount_input.text()
            entry_id = self.database_operations.addJournalEntry(date_col, currency, 'loan', loan_id)
            if entry_id:
                self.database_operations.addJournalEntryItem(entry_id, currency, 'creditor', statment, account_id, opposite_account_id, amount)
        except:
            pass