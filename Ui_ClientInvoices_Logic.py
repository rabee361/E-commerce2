from PyQt5.QtCore import Qt
from Ui_ClientInvoices import Ui_ClientInvoices
from MyTableWidgetItem import MyTableWidgetItem
from DatabaseOperations import DatabaseOperations
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_ClientInvoices_Logic(QDialog):
    def __init__(self, sql_connector, client_type='customer'):
        super().__init__()
        self.sql_connector = sql_connector
        self.client_type = client_type
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ClientInvoices()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        if self.client_type == 'supplier':
            window.setWindowTitle(self.language_manager.translate("SUPPLIER_INVOICES"))
        window.exec()

    def initialize(self, window):

        # hide id column in clients table
        self.ui.clients_table.hideColumn(0)

        # hide columns in invoices table
        self.ui.invoices_table.hideColumn(0)
        self.ui.invoices_table.hideColumn(4)

        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.fetchInvoices())
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.fetchClientPaymentCurrencies())
        self.ui.clients_table.itemSelectionChanged.connect(lambda: self.updateClientSummary())
        self.ui.invoices_table.itemDoubleClicked.connect(lambda: self.openInvoiceViewWindow())
        self.ui.summary_currency_combobox.currentIndexChanged.connect(lambda: self.updateClientSummary())
        
        self.fetchClients()
        self.fetchCurrencies()

    def fetchClients(self):
        self.ui.clients_table.setRowCount(0)
        clients = self.database_operations.fetchClients(client_type=self.client_type)
        for client in clients:
            id = client[0]
            name = client[1]
            numRows = self.ui.clients_table.rowCount()
            self.ui.clients_table.insertRow(numRows)
            # Add text to the row
            self.ui.clients_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.clients_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def fetchCurrencies(self):
        self.ui.summary_currency_combobox.clear()
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            display_text = currency[1]
            data = id
            self.ui.summary_currency_combobox.addItem(display_text, data)

    def fetchClientPaymentCurrencies(self):
        # Populate the client summary currency combobox with the currencies that the client paid with
        selected_client = self.ui.clients_table.currentItem()
        if selected_client:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            currencies = self.database_operations.fetchClientPaymentCurrencies(client_id=client_id)
            currencies_ids = [item['currency_id'] for item in currencies]
            self.ui.summary_currency_combobox.setCurrentIndex(-1)
            for i in range(self.ui.summary_currency_combobox.count()):
                currency_id = self.ui.summary_currency_combobox.itemData(i)
                if currency_id in currencies_ids:
                    self.ui.summary_currency_combobox.model().item(i).setEnabled(True)
                else:
                    self.ui.summary_currency_combobox.model().item(i).setEnabled(False)

    def fetchInvoices(self):
        self.ui.invoices_table.setRowCount(0)
        selected_client = self.ui.clients_table.currentItem()
        if selected_client is not None:
            client_id = self.ui.clients_table.item(selected_client.row(), 0).text()
            if client_id and client_id is not None:
                invoices = self.database_operations.fetchInvoicesValues(client_id=client_id)
                for invoice in invoices:
                    id = invoice['id']
                    invoice_type = invoice['invoice_type']
                    invoice_date = invoice['date_col']
                    paid = invoice['paid']
                    invoice_number = invoice['number']
                    invoice_currency_id = invoice['currency']
                    invoice_currency_name = invoice['invoice_currency_name']
                    client_name = invoice['name']
                    invoice_value = invoice['invoice_value']
                    paid_ammount = invoice['paid_ammount']

                    paid = invoice['paid']
                    if paid == 1:
                        paid_ammount = invoice_value

                    due_ammount = float(invoice_value) - float(paid_ammount)

                    # Create a empty row at bottom of table
                    numRows = self.ui.invoices_table.rowCount()
                    self.ui.invoices_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.invoices_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.invoices_table.setItem(numRows, 1, QTableWidgetItem(str(invoice_number)))
                    self.ui.invoices_table.setItem(numRows, 2, QTableWidgetItem(str(invoice_date)))
                    self.ui.invoices_table.setItem(numRows, 3, MyTableWidgetItem(str(invoice_value), float(invoice_value)))
                    self.ui.invoices_table.setItem(numRows, 4, QTableWidgetItem(str(invoice_currency_id)))
                    self.ui.invoices_table.setItem(numRows, 5, QTableWidgetItem(str(invoice_currency_name)))
                    self.ui.invoices_table.setItem(numRows, 6, MyTableWidgetItem(str(paid_ammount), float(paid_ammount)))
                    self.ui.invoices_table.setItem(numRows, 7, MyTableWidgetItem(str(due_ammount), float(due_ammount)))

    def openInvoiceViewWindow(self):
        selected_row = self.ui.invoices_table.currentRow()
        if selected_row >= 0:
            invoice_item = self.ui.invoices_table.item(selected_row, 0)
            if invoice_item is None:
                return
            invoice_id = invoice_item.text()
            invoice_view = Ui_InvoiceView_Logic(self.sql_connector, invoice_id=int(invoice_id))
            invoice_view.showUi()

    def updateClientSummary(self):
        selected_currency_id = self.ui.summary_currency_combobox.currentData()
        invoices_table = self.ui.invoices_table
        total_invoice_amount = 0
        total_paid_amount = 0
        total_remaining_amount = 0
        unpaid_invoices = 0 #invoices with dues left

        for i in range(invoices_table.rowCount()):
            if int(invoices_table.item(i, 4).text()) == selected_currency_id:
                total_invoice_amount += float(invoices_table.item(i, 3).text())
                total_paid_amount += float(invoices_table.item(i, 6).text())
                total_remaining_amount += float(invoices_table.item(i, 7).text())

            if float(invoices_table.item(i, 7).text()) != 0:
                unpaid_invoices += 1

        total_invoices = invoices_table.rowCount()

        # Assign values to appropriate input fields
        self.ui.invoices_count_input.setText(str(total_invoices))
        self.ui.total_invoices_value.setText(str(total_invoice_amount))
        self.ui.total_paid_values.setText(str(total_paid_amount))
        self.ui.total_unpaid_value.setText(str(total_remaining_amount))
        self.ui.unpaid_invoices_count.setText(str(unpaid_invoices))

