import Colors
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtCore import QTranslator
from Ui_Loans import Ui_Loans
from PyQt5.QtGui import QDoubleValidator
import win32api
from datetime import datetime
from Ui_AddLoan_Logic import Ui_AddLoan_Logic

class Ui_Loans_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Loans()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/bookkeeper.png'))
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.fetchLoans()
        self.fetchAccounts()
        self.fetchCurrencies()
        self.ui.loan_interest_input.setValidator(QDoubleValidator())
        self.ui.loan_amount_input.setValidator(QDoubleValidator())
        self.ui.payment_amount_input.setValidator(QDoubleValidator())
        self.ui.loan_date_input.setDate(QDate.currentDate())
        self.ui.payment_date_input.setDate(QDate.currentDate())
        self.ui.add_loan_btn.clicked.connect(lambda: self.addLoan())
        self.ui.save_loan_btn.clicked.connect(lambda: self.updateLoan())
        self.ui.loans_table.itemSelectionChanged.connect(lambda: self.fetchSelectedLoan())
        self.ui.remove_loan_btn.clicked.connect(lambda: self.removeLoan())
        self.ui.add_loan_payment_btn.clicked.connect(lambda: self.addLoanPayment())
        self.ui.remove_loan_payment_btn.clicked.connect(lambda: self.removeLoanPayment())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.account_combobox))    
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.opposite_account_combobox))
        self.ui.loans_table.hideColumn(7)
        self.ui.loans_table.hideColumn(9)
        
        self.ui.loan_cycle_combobox.addItem(self.language_manager.translate('DAILY'), 'daily')
        self.ui.loan_cycle_combobox.addItem(self.language_manager.translate('WEEKLY'), 'weekly')
        self.ui.loan_cycle_combobox.addItem(self.language_manager.translate('MONTHLY'), 'monthly')
        self.ui.loan_cycle_combobox.addItem(self.language_manager.translate('YEARLY'), 'yearly')
    

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        self.ui.currency_combobox.clear()
        for currency in currencies:
            self.ui.currency_combobox.addItem(currency['name'], currency['id'])
            self.ui.payment_currency_combobox.addItem(currency['name'], currency['id'])

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        self.ui.account_combobox.clear()
        self.ui.account_combobox.addItem(self.language_manager.translate('NONE'), 0)
        self.ui.opposite_account_combobox.clear()
        self.ui.opposite_account_combobox.addItem(self.language_manager.translate('NONE'), 0)
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
        add_loan_logic = Ui_AddLoan_Logic(self.sql_connector)
        add_loan_logic.showUi()
        self.fetchLoans()

    def fetchLoans(self):
        loans = self.database_operations.fetchLoans()
        self.ui.loans_table.setRowCount(0)
        for loan in loans:
            id = loan['id']
            name = loan['name']
            amount = loan['amount']
            date_col = loan['date_col']
            interest = loan['interest']
            currency = loan['currency']
            currency_name = loan['currency_name']
            interest = loan['interest']
            cycle = loan['cycle']
            account_id = loan['account_id']
            account_name = loan['account_name']
            opposite_account_id = loan['opposite_account_id']
            opposite_account_name = loan['opposite_account_name']
            currency_id = loan['currency']

            loan_payments = self.database_operations.fetchLoanPayments(id)
            paid = 0
            remaining = 0
            for payment in loan_payments:
                paid += payment['amount']
            remaining = amount - paid

            # Fix: Use QTableWidgetItem instead of QTreeWidgetItem since we're working with a table
            row = self.ui.loans_table.rowCount()
            self.ui.loans_table.insertRow(row)
            self.ui.loans_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.ui.loans_table.setItem(row, 1, QTableWidgetItem(str(name)))
            self.ui.loans_table.setItem(row, 2, QTableWidgetItem(str(amount)))
            self.ui.loans_table.setItem(row, 3, QTableWidgetItem(str(currency_id)))
            self.ui.loans_table.setItem(row, 4, QTableWidgetItem(str(currency_name)))
            self.ui.loans_table.setItem(row, 5, QTableWidgetItem(str(date_col)))
            self.ui.loans_table.setItem(row, 6, QTableWidgetItem(str(account_name)))
            self.ui.loans_table.setItem(row, 7, QTableWidgetItem(str(account_id)))
            self.ui.loans_table.setItem(row, 8, QTableWidgetItem(str(opposite_account_name)))
            self.ui.loans_table.setItem(row, 9, QTableWidgetItem(str(opposite_account_id)))
            self.ui.loans_table.setItem(row, 10, QTableWidgetItem(str(cycle)))
            self.ui.loans_table.setItem(row, 11, QTableWidgetItem(str(interest)))
            self.ui.loans_table.setItem(row, 12, QTableWidgetItem(str(paid)))
            self.ui.loans_table.setItem(row, 13, QTableWidgetItem(str(remaining)))

    def fetchSelectedLoan(self):
        loan = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 0)
        if loan:
            loan_id = loan.text()
            loan_info = self.database_operations.fetchLoan(loan_id)
            loan_name = loan_info['name']
            loan_amount = loan_info['amount']
            loan_currency = loan_info['currency']
            loan_date = loan_info['date_col']
            loan_account = loan_info['account_id']
            loan_opposite_account = loan_info['opposite_account_id']
            loan_cycle = loan_info['cycle']
            loan_interest = loan_info['interest']

            self.ui.loan_name_input.setText(loan_name)
            self.ui.loan_amount_input.setText(str(loan_amount))
            self.ui.currency_combobox.setCurrentIndex(self.ui.currency_combobox.findData(loan_currency))
            # If loan_date is already a string, use it directly
            # If it's a datetime, convert it to string
            loan_date_str = loan_date if isinstance(loan_date, str) else loan_date.strftime('%Y-%m-%d')
            self.ui.loan_date_input.setDate(QDate.fromString(loan_date_str, 'yyyy-MM-dd'))
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(loan_account))
            self.ui.opposite_account_combobox.setCurrentIndex(self.ui.opposite_account_combobox.findData(loan_opposite_account))
            self.ui.loan_cycle_combobox.setCurrentIndex(self.ui.loan_cycle_combobox.findData(loan_cycle))
            self.ui.loan_interest_input.setText(str(loan_interest))

            payments = self.database_operations.fetchLoanPayments(loan_id)
            self.ui.payments_table.setRowCount(0)
            for payment in payments:
                id = payment['id']
                date_col = payment['date_col']
                amount = payment['amount']
                currency = payment['currency']
                row = self.ui.payments_table.rowCount()
                self.ui.payments_table.insertRow(row)
                self.ui.payments_table.setItem(row, 0, QTableWidgetItem(str(id)))
                self.ui.payments_table.setItem(row, 1, QTableWidgetItem(str(amount)))
                self.ui.payments_table.setItem(row, 2, QTableWidgetItem(str(currency)))
                self.ui.payments_table.setItem(row, 3, QTableWidgetItem(str(loan_id)))
                self.ui.payments_table.setItem(row, 4, QTableWidgetItem(str(date_col)))

    def removeLoan(self):
        loan = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 0).text()
        if loan:
            win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"))
            self.database_operations.removeLoan(loan)
            self.fetchLoans()

        else:
            pass

    def updateLoan(self):
        loan_id = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 0).text()
        name = self.ui.loan_name_input.text()
        amount = self.ui.loan_amount_input.text() 
        date = self.ui.loan_date_input.text()
        account_id = self.ui.account_combobox.currentData()
        opposite_account_id = self.ui.opposite_account_combobox.currentData()
        currency_id = self.ui.currency_combobox.currentData()
        cycle = self.ui.loan_cycle_combobox.currentData()
        interest = self.ui.loan_interest_input.text()

        self.database_operations.updateLoan(loan_id, name, amount, date, account_id, opposite_account_id, cycle, currency_id, interest)
        try:
            journal_entry = self.database_operations.fetchJournalEntries(origin_type="loan", origin_id=loan_id)
            if journal_entry:
                self.database_operations.removeJournalEntriesItems(journal_entry[0]['id'])
                self.database_operations.removeJournalEntry(journal_entry[0]['id'])
        except:
            pass

        self.addLoanJournalEntry(loan_id)
        self.fetchLoans() 

    def addLoanPayment(self):
        loan_id = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 0).text()
        currency = self.ui.payment_currency_combobox.currentData()
        date_col = self.ui.payment_date_input.date().toString('yyyy-MM-dd')
        amount = self.ui.payment_amount_input.text()
        if loan_id:
            payment_id = self.database_operations.addLoanPayment(loan_id, date_col, amount, currency)
            self.fetchLoanPayments()
            self.addPaymentJournalEntry(payment_id)
        else:
            pass


    def fetchLoanPayments(self):
        loan_id = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 0).text()
        payments = self.database_operations.fetchLoanPayments(loan_id)
        self.ui.payments_table.setRowCount(0)
        for payment in payments:
            row = self.ui.payments_table.rowCount()
            self.ui.payments_table.insertRow(row)
            self.ui.payments_table.setItem(row, 0, QTableWidgetItem(str(payment['id'])))
            self.ui.payments_table.setItem(row, 1, QTableWidgetItem(str(payment['amount'])))
            self.ui.payments_table.setItem(row, 2, QTableWidgetItem(str(payment['loan_id'])))
            self.ui.payments_table.setItem(row, 3, QTableWidgetItem(str(payment['date_col'])))


    def removeLoanPayment(self):
        payment = self.ui.payments_table.item(self.ui.payments_table.currentRow(), 0)
        if payment:
            win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"))
            payment_id = payment.text()
            self.database_operations.removeLoanPayment(payment_id)
            self.fetchLoanPayments()
        else:
            pass


    def updateLoanPayment(self):
        payment = self.ui.payments_table.item(self.ui.payments_table.currentRow(), 0)
        if payment:
            payment_id = payment.text()
            currency = self.ui.payment_currency_combobox.currentData()
            date = self.ui.payment_date_input.date().toString('yyyy-MM-dd')
            amount = self.ui.payment_amount_input.text()
            self.database_operations.updateLoanPayment(payment_id, amount, currency, date)
            try:
                journal_entry = self.database_operations.fetchJournalEntries(origin_type="loan_payment", origin_id=payment_id)
                if journal_entry:
                    self.database_operations.removeJournalEntriesItems(journal_entry[0]['id'])
                    self.database_operations.removeJournalEntry(journal_entry[0]['id'])
            except:
                pass
            self.addPaymentJournalEntry(payment_id)
            self.fetchLoanPayments()


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

    def addPaymentJournalEntry(self, payment_id):
        try:
            account_id = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 7).text()
            opposite_account_id = self.ui.loans_table.item(self.ui.loans_table.currentRow(), 9).text()
            currency = self.ui.currency_combobox.currentData()
            statment = 'loan'
            date_col = datetime.now().strftime('%Y-%m-%d')
            amount = self.ui.payment_amount_input.text()
            entry_id = self.database_operations.addJournalEntry(date_col, currency, 'loan_payment', payment_id)
            if entry_id:
                self.database_operations.addJournalEntryItem(entry_id, currency, 'creditor', statment, account_id, opposite_account_id, amount)
        except:
            win32api.MessageBox(0, "ERROR", "ERROR", 0)
