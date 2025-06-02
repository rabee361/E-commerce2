from locale import currency
from math import e
from pickle import NONE
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from win32con import IDYES, IDNO, MB_YESNO
from PyQt5.QtWidgets import QTableWidgetItem
from DatabaseOperations import DatabaseOperations
from Ui_JournalVoucher import Ui_JournalVoucher
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_JournalVoucher_Logic(QDialog):
    def __init__(self, sql_connector, payment_type):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.payment_type = payment_type
        self.ui = Ui_JournalVoucher()
        self.journal = None
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.entry_id = None

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        window_name = self.language_manager.translate("PAYMENTS_VOUCHERS") if self.payment_type == 'payment' else self.language_manager.translate("RECEIPTS_VOUCHERS")
        window.setObjectName(window_name)
        window.setWindowTitle(window_name)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchCurrencies()
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectOppositeAccountWindow())
        self.ui.add_journal_entry_item.clicked.connect(lambda: self.addJournalEntryItem())

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            name = account[1]
            self.ui.account_combobox.addItem(str(name), id)
            self.ui.opposite_account_combobox.addItem(str(name), id)

    def fetchCostCenters(self):
        cost_centers = self.database_operations.fetchCostCenters()
        for cost_center in cost_centers:
            id = cost_center['id']
            name = cost_center['name']
            self.ui.journal_entry_cost_center_combobox.addItem(name, id)

    def fetchCurrencies(self):
        self.ui.currency_combobox.clear()
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.currency_combobox.addItem(name, id)

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(result['id']))

    def openSelectOppositeAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.opposite_account_combobox.setCurrentIndex(self.ui.opposite_account_combobox.findData(result['id']))

    def addJournalEntryItem(self):
        payment_type = self.payment_type
        type_col = 'debtor' if payment_type == 'payment' else 'creditor'
        currency = self.ui.currency_combobox.currentData()
        currency_name = self.ui.currency_combobox.currentText()
        statement = self.ui.journal_entry_item_statement_input.toPlainText()
        account = self.ui.account_combobox.currentData()
        account_name = self.ui.account_combobox.currentText()
        opposite_account = self.ui.opposite_account_combobox.currentData()
        opposite_account_name = self.ui.opposite_account_combobox.currentText()
        amount = self.ui.value_input.text()
        date_col = self.ui.date_input.text()
        cost_center_id = self.ui.journal_entry_cost_center_combobox.currentData()
        if self.ui.journal_entry_items_table.rowCount() > 0:
            self.database_operations.addJournalEntryItem(self.entry_id, currency, type_col, statement, account, opposite_account, amount, cost_center_id)
        else:
            entry_id = self.database_operations.addJournalEntry(date_col, currency)
            self.entry_id = entry_id
            self.database_operations.addJournalEntryItem(entry_id, currency, type_col, statement, account, opposite_account, amount, cost_center_id)
            
        # Add the new entry to the journal_entry_items_table
        row_position = self.ui.journal_entry_items_table.rowCount()
        self.ui.journal_entry_items_table.insertRow(row_position)
        
        # Populate the new row with entry data
        self.ui.journal_entry_items_table.setItem(row_position, 0, QTableWidgetItem(str(account_name)))
        self.ui.journal_entry_items_table.setItem(row_position, 1, QTableWidgetItem(str(opposite_account_name)))
        self.ui.journal_entry_items_table.setItem(row_position, 2, QTableWidgetItem(str(currency_name)))
        self.ui.journal_entry_items_table.setItem(row_position, 3, QTableWidgetItem(str(amount)))
