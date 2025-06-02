from pickle import NONE
import win32api
from PyQt5.QtCore import Qt , QDate
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QToolTip
from win32con import IDYES, IDNO, MB_YESNO

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_JournalVoucher import Ui_JournalVoucher
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_JournalVoucer_Logic(QDialog):
    def __init__(self, sql_connector, payment_type):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.payment_type = payment_type
        self.ui = Ui_JournalVoucher()
        self.journal = None
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

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
        pass     
