import win32api
from PyQt5.QtCore import Qt , QDate
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QToolTip
from win32con import IDYES, IDNO, MB_YESNO

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Payments import Ui_Payments
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Payments_Logic(QDialog):
    def __init__(self, sql_connector, payment_type):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.payment_type = payment_type
        self.ui = Ui_Payments()
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
        self.ui.groupBox.setTitle(self.language_manager.translate("ADD_VOUCHER") + ' ' + (self.language_manager.translate("PAYMENT") if self.payment_type == 'payment' else self.language_manager.translate("RECEIPT")))

        # Hide columns with indexes 0, 2 in clients table
        self.ui.clients_table.hideColumn(0) # id

        # Hide columns with indexes 0, 3 in payments table
        self.ui.payments_table.hideColumn(0)
        self.ui.payments_table.hideColumn(3)

        self.ui.payments_table.setColumnWidth(6, 300)
        self.ui.payment_date_input.setDate(QDate.currentDate())

        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.ui.select_invoice_btn.setEnabled(True))
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.fetchPayments())
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.fetchInvoices())
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.fetchClientPaymentCurrencies())
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.updateClientSummary())
        self.ui.invoices_combobox.currentIndexChanged.connect(lambda: self.updateInvoiceInfo())
        self.ui.invoices_combobox.currentIndexChanged.connect(lambda: self.fetchDefaultAccounts())
        self.ui.client_summary_currency_combobox.currentIndexChanged.connect(lambda: self.updateClientSummary())
        self.ui.payment_currency_combobox.currentIndexChanged.connect(lambda: self.fetchExchangeValues(
            self.ui.payment_currency_combobox.currentData(),
            self.ui.invoice_currency_combobox.currentData(),
            self.ui.exchange_combobox
        ))

        self.ui.invoice_currency_combobox.currentIndexChanged.connect(lambda: self.fetchExchangeValues(
            self.ui.payment_currency_combobox.currentData(),
            self.ui.invoice_currency_combobox.currentData(),
            self.ui.exchange_combobox
        ))
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.updateEquilivance())
        self.ui.payment_input.editingFinished.connect(lambda: self.updateEquilivance())

        self.ui.add_btn.clicked.connect(lambda: self.addNewPayment())
        # self.ui.add_btn.clicked.connect(lambda: self.fetchInvoices())
        # self.ui.add_btn.clicked.connect(lambda: self.fetchPayments())
        # self.ui.add_btn.clicked.connect(lambda: self.updateClientSummary())
        # self.ui.delete_btn.clicked.connect(lambda: self.fetchInvoices())
        # self.ui.delete_btn.clicked.connect(lambda: self.fetchPayments())
        # self.ui.delete_btn.clicked.connect(lambda: self.updateClientSummary())

        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.account_combobox))
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.opposite_account_combobox))
        self.ui.select_client_extra_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.client_extra_account_combobox))
        self.ui.select_invoice_btn.clicked.connect(lambda: self.openSelectInvoiceWindow())

        self.fetchClients()
        self.fetchAccounts()
        self.fetchCurrencies()

    def fetchDefaultAccounts(self):
        selected_invoice = self.ui.invoices_combobox.currentData()
        if selected_invoice:
            invoice_type = selected_invoice[5]
            # Fetch invoice monetary account
            setting = f"{invoice_type}_{'monetary_account'}"
            invoice_monetary_account = int(self.database_operations.fetchSetting(setting))

            # Fetch the default accounts for the selected client
            selected_client = self.ui.clients_table.currentItem()
            if selected_client:
                client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
                try:
                    client_data = self.database_operations.fetchClient(client_id)
                    client_account_id = client_data['client_account_id']
                    client_extra_account_id = client_data['extra_account_id']

                    # Set accounts
                    account = invoice_monetary_account if self.payment_type == 'payment' else client_account_id
                    opposite_account = invoice_monetary_account if self.payment_type == 'receipt' else client_account_id
                    self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(account))
                    self.ui.opposite_account_combobox.setCurrentIndex(self.ui.account_combobox.findData(opposite_account))
                    self.ui.client_extra_account_combobox.setCurrentIndex(self.ui.client_extra_account_combobox.findData(client_extra_account_id))
                except:
                    pass
        else:
            self.ui.account_combobox.setCurrentIndex(0)
            self.ui.opposite_account_combobox.setCurrentIndex(0)
            self.ui.client_extra_account_combobox.setCurrentIndex(0)

    def fetchClientPaymentCurrencies(self):
        # Populate the client summary currency combobox with the currencies that the client paid with
        selected_client = self.ui.clients_table.currentItem()
        if selected_client:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            currencies = self.database_operations.fetchClientPaymentCurrencies(client_id=client_id)
            currencies_ids = [item['currency_id'] for item in currencies]
            self.ui.client_summary_currency_combobox.setCurrentIndex(-1)
            for i in range(self.ui.client_summary_currency_combobox.count()):
                currency_id = self.ui.client_summary_currency_combobox.itemData(i)
                if currency_id in currencies_ids:
                    self.ui.client_summary_currency_combobox.model().item(i).setEnabled(True)
                else:
                    self.ui.client_summary_currency_combobox.model().item(i).setEnabled(False)

    def openSelectInvoiceWindow(self):
        selected_client = self.ui.clients_table.currentItem()
        client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
        if client_id:
            data_picker_logic = Ui_DataPicker_Logic(self.sql_connector, 'client_invoices', columns=['id', 'number', 'date_col',], include_none_option=True, client_id=client_id, criterias={'paid': 0})
            result = data_picker_logic.showUi()
            if result:
                if result['id'] == None:
                    self.ui.invoices_combobox.setCurrentIndex(0)
                else:
                    for i in range(1, self.ui.invoices_combobox.count()):
                        if self.ui.invoices_combobox.itemData(i)[0] == result['id']:
                            self.ui.invoices_combobox.setCurrentIndex(i)
                            break

    def openSelectAccountWindow(self, combobox):
        data_picker_logic = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker_logic.showUi()
        if result:
            account_id = result[0]
            combobox.setCurrentIndex(combobox.findData(account_id))

    def fetchAccounts(self):
        self.ui.account_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.opposite_account_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.client_extra_account_combobox.addItem(self.language_manager.translate("NONE"), None)
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            name = account[1]
            self.ui.account_combobox.addItem(name, id)
            self.ui.opposite_account_combobox.addItem(name, id)
            self.ui.client_extra_account_combobox.addItem(name, id)

    def fetchClients(self):
        self.ui.clients_table.setRowCount(0)
        client_type = 'supplier' if self.payment_type == 'payment' else 'customer'
        clients = self.database_operations.fetchClients(client_type=client_type)
        for client in clients:
            id = client[0]
            name = client[1]
            numRows = self.ui.clients_table.rowCount()
            self.ui.clients_table.insertRow(numRows)
            # Add text to the row
            self.ui.clients_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.clients_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def fetchPayments(self):
        self.ui.payments_table.setRowCount(0)
        selected_client = self.ui.clients_table.currentItem()

        if selected_client is not None:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            if client_id and client_id is not None:
                client_payments = []
                client_payments = self.database_operations.fetchClientPayments(client_id, include_extra_payments=True)
                    
                for client_payment in client_payments:
                    id = client_payment['id']
                    ammount = client_payment['value_col']
                    date = client_payment['entry_date']
                    currency_id = client_payment['currency']
                    currency_name = client_payment['currency_name']
                    invoice_id = client_payment['origin_id']
                    statement = client_payment['statement_col']

                    # Create a empty row at bottom of table
                    numRows = self.ui.payments_table.rowCount()
                    self.ui.payments_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.payments_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.payments_table.setItem(numRows, 1, QTableWidgetItem(str(date)))
                    self.ui.payments_table.setItem(numRows, 2, MyTableWidgetItem(str(ammount), float(ammount)))
                    self.ui.payments_table.setItem(numRows, 3, QTableWidgetItem(str(currency_id)))
                    self.ui.payments_table.setItem(numRows, 4, QTableWidgetItem(str(currency_name)))
                    self.ui.payments_table.setItem(numRows, 5, QTableWidgetItem(str(invoice_id)))
                    self.ui.payments_table.setItem(numRows, 6, QTableWidgetItem(str(statement)))

    def fetchInvoices(self):
        self.ui.invoices_combobox.clear()
        self.ui.invoice_info_input.clear()
        self.ui.invoice_info_input.setStyleSheet("background-color:white;color:black;border: 1px solid #b3b3b3;")
        selected_client = self.ui.clients_table.currentItem()
        if selected_client is not None:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            if client_id and client_id is not None:
                self.ui.invoices_combobox.addItem("لا يوجد", None)  # in this case the client is prepaying
                
                invoices = []
                invoices = self.database_operations.fetchInvoicesValues(client_id=client_id)
                
                for invoice in invoices:
                    id = invoice['id']
                    invoice_type = invoice['invoice_type']
                    date = invoice['date_col']
                    paid = invoice['paid']
                    invoice_number = invoice['number']
                    invoice_currency = invoice['currency']
                    invoice_currency_name = invoice['invoice_currency_name']
                    client_name = invoice['name']
                    invoice_value = invoice['invoice_value']
                    paid_ammount = invoice['paid_ammount']

                    if float(invoice_value) == float(paid_ammount):
                        self.database_operations.setInvoiceAsPaid(id)

                    if not paid or str(paid).lower() == 'none' or paid == '':
                        invoice_text = "(" + str(invoice_number) + ")" + str(date)
                        invoice_data = [id, invoice_value, paid_ammount, invoice_currency, invoice_number, invoice_type]
                        self.ui.invoices_combobox.addItem(invoice_text, invoice_data)

    def updateInvoiceInfo(self):
        info_input = self.ui.invoice_info_input
        info_input.setText("")
        info_input.setStyleSheet("background-color:white;color:black;border: 1px solid #b3b3b3;")
        invoice_data = self.ui.invoices_combobox.currentData()
        if invoice_data:
            invoice_value = invoice_data[1] if invoice_data[1] != '' else 'NaN'
            paid_ammount = invoice_data[2] if invoice_data[2] != '' else 'NaN'
            info_text = str(paid_ammount) + "/" + str(invoice_value)
            info_input.setText(info_text)
            if float(paid_ammount) == float(invoice_value):
                info_input.setStyleSheet("background-color: darkgreen; color: white;")
            elif float(paid_ammount) < float(invoice_value):
                info_input.setStyleSheet("background-color: red; color: white;")
            elif float(paid_ammount) > float(invoice_value):  # TODO: this should never happen
                info_input.setStyleSheet("background-color:yellow;color:black;border: 1px solid #b3b3b3;")
                invoice_currecny_id = invoice_data[3]
                self.ui.invoice_currency_combobox.setCurrentIndex(
                    self.ui.invoice_currency_combobox.findData(invoice_currecny_id))
            invoice_currency_id = invoice_data[3]
            self.ui.invoice_currency_combobox.setCurrentIndex(
                self.ui.invoice_currency_combobox.findData(invoice_currency_id))
            self.ui.payment_currency_combobox.setCurrentIndex(
                self.ui.payment_currency_combobox.findData(invoice_currency_id))
        else:
            self.ui.invoice_currency_combobox.setCurrentIndex(0)  # لا يوجد

    def fetchCurrencies(self):
        self.ui.invoice_currency_combobox.clear()
        self.ui.invoice_currency_combobox.addItem(self.language_manager.translate("NONE"), None)  # in this case the client is prepaying
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            display_text = currency[1]
            data = id
            self.ui.invoice_currency_combobox.addItem(display_text, data)
            self.ui.payment_currency_combobox.addItem(display_text, data)
            self.ui.client_summary_currency_combobox.addItem(display_text, data)

    def fetchExchangeValues(self, currency_1, currency_2, target_ui_element):
        target_ui_element.clear()
        if currency_1 is None or currency_2 is None:
            return
        elif currency_1 == currency_2:
            text_to_display = "1"
            data = [None, 1]
            target_ui_element.clear()
            target_ui_element.addItem(text_to_display, data)
            return

        exchange_values = self.database_operations.fetchExchangeValue(currency_1, currency_2)
        if exchange_values is None:
            return

        for id, exchange_value, date in exchange_values:
            text_to_display = f"{exchange_value} ({self.language_manager.translate('AT_DATE')} {date})"
            data = [id, exchange_value]
            target_ui_element.addItem(text_to_display, data)

    def updateEquilivance(self):
        invoice_id = self.ui.invoices_combobox.currentData()
        exchange_data = self.ui.exchange_combobox.currentData()
        payment = self.ui.payment_input.text()
        equilivance = ""
        if payment:
            if invoice_id:
                if exchange_data:
                    exchange_value = exchange_data[1]
                    if exchange_value:
                        equilivance = float(payment) * float(exchange_value)
            else:
                equilivance = ''

        self.ui.equilivance_input.setText(str(equilivance))

    def updateClientSummary(self):
        self.ui.client_payments_sum_input.clear()
        self.ui.client_extra_payments_sum_input.clear()
        self.ui.client_required_payments_sum_input.clear()

        selected_client = self.ui.clients_table.currentItem()
        if selected_client:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            client_data = self.database_operations.fetchClient(client_id)
            client_account_id = client_data['client_account_id']
            client_extra_account_id = client_data['extra_account_id']
            
            total_paid = 0
            total_invoices_paid = 0
            total_required = 0

            currency_id = self.ui.client_summary_currency_combobox.currentData()

            if currency_id:

                # Calculate the client total account value
                for row in range(self.ui.payments_table.rowCount()):
                    payment_currency_id = self.ui.payments_table.item(row, 3).text()
                    invoice_id = self.ui.payments_table.item(row, 5).text()
                    if int(payment_currency_id) == int(currency_id):
                        payment_amount = self.ui.payments_table.item(row, 2).text()
                        total_paid += float(payment_amount)
                        if invoice_id != 'None':
                            total_invoices_paid += float(payment_amount)


                total_required = 0
                for row in range(self.ui.invoices_combobox.count()):
                    invoice_data = self.ui.invoices_combobox.itemData(row)
                    if invoice_data:
                        invoice_value = invoice_data[1]
                        invoice_paid = invoice_data[2]
                        invoice_currency = invoice_data[3]
                        if invoice_currency == currency_id:
                            total_required += invoice_value - invoice_paid

            total_extra = self.database_operations.fetchAccountValue(client_extra_account_id, currency_id)

            self.ui.client_payments_sum_input.setText(str(total_paid))
            self.ui.client_extra_payments_sum_input.setText(str(total_extra))
            self.ui.client_required_payments_sum_input.setText(str(total_required))
            
    def addNewPayment(self):
        client_account_id = self.ui.account_combobox.currentData()
        client_opposite_account_id = self.ui.opposite_account_combobox.currentData()
        client_extra_account_id = self.ui.client_extra_account_combobox.currentData()
        if client_account_id and client_opposite_account_id and client_extra_account_id:
            exchange_data = self.ui.exchange_combobox.currentData()
            exchange_id = None
            if exchange_data:
                exchange_id = exchange_data[0]
                exchange_rate = exchange_data[1]
            payment_currency_id = self.ui.payment_currency_combobox.currentData()
            invoice_currency_id = self.ui.invoice_currency_combobox.currentData()
            invoice_currency_name = self.ui.invoice_currency_combobox.currentText()
            notes = self.ui.notes_input.text()
            payment = self.ui.payment_input.text()
            date = self.ui.payment_date_input.date().toString(Qt.ISODate)
            selected_client = self.ui.clients_table.currentItem()
            equilivance = self.ui.equilivance_input.text()
            if selected_client is not None and equilivance and equilivance != '':
                client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
                if client_id and client_id is not None:
                    invoice_data = self.ui.invoices_combobox.currentData()
                    invoice_id = None
                    difference = 0  # equilivance - due
                    if invoice_data:
                        invoice_id = invoice_data[0]
                        invoice_value = invoice_data[1]
                        paid_ammount = invoice_data[2]
                        if invoice_value and paid_ammount >= 0:
                            due = float(invoice_value) - float(paid_ammount)
                            equilivance = float(equilivance)
                            if equilivance > due:   
                                if due == 0:
                                    message_text = self.language_manager.translate('ADD_EXTRA_AMOUNT_TO_CLIENT_ACCOUNT')
                                    messagebox_result = win32api.MessageBox(None, message_text, self.language_manager.translate("ALERT"), MB_YESNO)
                                    if (messagebox_result == IDYES):
                                        invoice_id = None
                                    elif (messagebox_result == IDNO):
                                        return
                                if due != 0:
                                    difference = equilivance - due
                                    if difference > 0:
                                        if not client_extra_account_id:
                                            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("EXTRA_PAYMENTS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
                                            return
                                    equilivance = due
                                    equilivance = due
                                    payment = equilivance / exchange_rate
                                    message_text = self.language_manager.translate("EXTRA_AMOUNT_ADDED_TO_CLIENT_ACCOUNT") + " " + str(difference) + " " + str(invoice_currency_name) + " " + self.language_manager.translate("ADDED_TO_CLIENT_ACCOUNT")
                                    win32api.MessageBox(0, message_text, self.language_manager.translate("ALERT"))

                    if not invoice_id or invoice_id == None:
                        invoice_id = ''
                    if not invoice_currency_id or invoice_currency_id == None:
                        invoice_currency_id = ''
                    if not exchange_id or exchange_id == None:
                        exchange_id = ''
                    if not notes or notes == None:
                        notes = ''

                    journal_entry_item_account = self.ui.account_combobox.currentData()
                    journal_entry_item_opposite_account = self.ui.opposite_account_combobox.currentData()

                    client_name = self.ui.clients_table.item(selected_client.row(), 1).text()
                    invoice_number = invoice_data[4]

                    journal_statement = ''
                    if self.payment_type == 'payment':
                        journal_statement = self.language_manager.translate("PAYMENT_TO_CLIENT") + " " + str(client_name) + " " + self.language_manager.translate("FOR_INVOICE") + " " + str(invoice_number)
                    else:
                        journal_statement = self.language_manager.translate("PAYMENT_FROM_CLIENT") + " " + str(client_name) + " " + self.language_manager.translate("FOR_INVOICE") + " " + str(invoice_number)

                    # Add journal entry
                    journal_entry_id = self.database_operations.addJournalEntry(date, invoice_currency_id, origin_type='invoice_payment', origin_id=invoice_id, commit=False)

                    # Add journal entry item
                    self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency_id, 'creditor', journal_statement, journal_entry_item_account, journal_entry_item_opposite_account, equilivance, commit=True)

                    if float(difference):
                        difference = float(difference)
                        equilivance = difference
                        payment = difference / exchange_rate
                        notes = self.language_manager.translate("EXTRA_AMOUNT")
                        client_name = self.ui.clients_table.item(selected_client.row(), 1).text()
                        journal_statement = self.language_manager.translate("EXTRA_AMOUNT") + " " + str(client_name)

                        journal_entry_id = self.database_operations.addJournalEntry(date, invoice_currency_id, origin_type='extra_payment', origin_id=invoice_id,commit=False)
                        
                        journal_entry_item_account = self.ui.opposite_account_combobox.currentData()

                        journal_entry_item_opposite_account = self.ui.client_extra_account_combobox.currentData()
                        
                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency_id, 'creditor', journal_statement, journal_entry_item_account, journal_entry_item_opposite_account, equilivance, commit=True)

                    self.ui.payment_input.clear()
                    self.ui.equilivance_input.clear()
                    self.ui.notes_input.clear()
                    self.fetchPayments()
                    self.fetchInvoices()
                    self.updateClientSummary()
        else:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("PAYMENT_ERROR"), self.language_manager.translate("ALERT"))
        
        
