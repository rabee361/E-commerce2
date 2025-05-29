import win32api
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt , QTranslator
from win32con import MB_YESNO, IDYES, IDNO
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from DatabaseOperations import DatabaseOperations
from Ui_AccountBalance import Ui_AccountBalance
from LanguageManager import LanguageManager
from Ui_FinalAccountsReports_Logic import Ui_FinalAccountsReports_Logic
import win32con

class Ui_AccountBalance_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.windows_manager = ''
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AccountBalance()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchCurrencies()
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.account_details_btn.clicked.connect(lambda: self.openAccountDetailsWindow())
        self.ui.account_combobox.currentIndexChanged.connect(lambda: self.fetchAccountBalance())

    def fetchAccounts(self):
        self.ui.account_combobox.clear()
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account['id']
            name = account['name']
            self.ui.account_combobox.addItem(name, id)

    def fetchCurrencies(self):
        self.ui.curreny_combobox.clear()
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.curreny_combobox.addItem(name, id)

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.clear()
            self.ui.account_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.account_combobox.setCurrentIndex(0)

    def openAccountDetailsWindow(self):
        selected_account_id = self.ui.account_combobox.currentData()
        if selected_account_id:
            account = self.database_operations.fetchAccount(selected_account_id)
            if account['type_col'] == 'final':
                Ui_FinalAccountsReports_Logic(self.sql_connector, selected_account_id).showUi() 
            else:
                win32api.MessageBox(0, self.language_manager.translate('ALERT_ACCOUNT_NOT_FINAL'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def fetchAccountBalance(self):
        selected_account_id = self.ui.account_combobox.currentData()
        currency_id = self.ui.curreny_combobox.currentData()
        if selected_account_id and currency_id:
            account_total_value = self.database_operations.fetchAccountValue(selected_account_id, currency_id)
            account_value = self.database_operations.fetchAccountSingleValue(selected_account_id, currency_id)
            self.ui.accounts_table.setRowCount(1)
            self.ui.accounts_table.setItem(0, 0, QTableWidgetItem(str(selected_account_id)))
            self.ui.accounts_table.setItem(0, 1, QTableWidgetItem(str(currency_id)))
            self.ui.accounts_table.setItem(0, 2, QTableWidgetItem(str(account_total_value)))
            self.ui.accounts_table.setItem(0, 3, QTableWidgetItem(str(account_value)))
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_SELECT_ACCOUNT'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)
            return
