import win32api
import win32con
from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QSizePolicy
from DatabaseOperations import DatabaseOperations
from Ui_InvoicesList import Ui_InvoicesList
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
from LanguageManager import LanguageManager

class Ui_InvoicesList_Logic(QDialog):
    def __init__(self, sql_connector, windows_manager):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_InvoicesList()
        self.windows_manager = windows_manager
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        self.window = QDialog()
        self.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.window.setWindowState(Qt.WindowMaximized)
        self.window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(self.window)
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.initialize(self.window)
        self.window.show()

    def initialize(self, window):
        self.ui.filter_by_type_checkbox.clicked.connect(lambda: self.enableInvoiceTypeCombobox())
        self.ui.filter_by_date_checkbox.clicked.connect(lambda: self.fetchInvoices())
        self.ui.filter_by_type_checkbox.clicked.connect(lambda: self.fetchInvoices())
        self.ui.filter_by_client_checkbox.clicked.connect(lambda: self.fetchInvoices())
        self.ui.calendar.clicked.connect(lambda: self.fetchInvoices())
        self.ui.clients_table.cellClicked.connect(lambda: self.fetchInvoices())
        self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.fetchInvoices())
        self.ui.invoices_table.cellDoubleClicked.connect(lambda: self.openInvoiceViewWindow())
        self.ui.details_btn.clicked.connect(lambda: self.openInvoiceViewWindow())
        self.ui.delete_btn.clicked.connect(lambda: self.removeInvoice())

        # Set equal column widths for invoices table header
        header = self.ui.invoices_table.horizontalHeader()
        for column in range(self.ui.invoices_table.columnCount()):
            header.setSectionResizeMode(column, header.Stretch)

        self.fetchInvoices()
        self.fetchClients()
        self.fetchInvoicesTypes()

    def enableInvoiceTypeCombobox(self):
        if self.ui.filter_by_type_checkbox.isChecked():
            self.ui.invoice_type_combobox.setDisabled(False)
        else:
            self.ui.invoice_type_combobox.setDisabled(True)

    def fetchClients(self):
        clients = self.database_operations.fetchClients()
        for client in clients:
            id = client['id']
            name = client['name']
            numRows = self.ui.clients_table.rowCount()
            self.ui.clients_table.insertRow(numRows)
            # Add text to the row
            self.ui.clients_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.clients_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def fetchInvoicesTypes(self):
        invoices_types = self.database_operations.fetchInvoiceTypes()
        for invoice_type in invoices_types:
            name = invoice_type['name']
            id = str(invoice_type['id'])
            self.ui.invoice_type_combobox.addItem(name, [id, name])

    def fetchInvoices(self):
        calendar = self.ui.calendar
        date_filter = ''
        client_filter = ''
        type_filter = ''

        if self.ui.filter_by_date_checkbox.isChecked():
            date_filter = calendar.selectedDate().toString(Qt.ISODate)

        if self.ui.filter_by_client_checkbox.isChecked():
            selected_row = self.ui.clients_table.currentRow()
            if selected_row >= 0:
                client_filter = self.ui.clients_table.item(selected_row, 0).text()

        if self.ui.filter_by_type_checkbox.isChecked():
            current_item = self.ui.invoice_type_combobox.currentData()
            if current_item:
                type_filter = current_item[0]

        invoices = self.database_operations.fetchAllInvoices(date_filter, client_filter, type_filter)
        self.ui.invoices_table.setRowCount(0)
        for invoice in invoices:
            row_position = self.ui.invoices_table.rowCount()
            self.ui.invoices_table.insertRow(row_position)
            self.ui.invoices_table.setItem(row_position, 0, QTableWidgetItem(str(invoice['id'])))
            self.ui.invoices_table.setItem(row_position, 1, QTableWidgetItem(str(invoice['type_col'])))
            self.ui.invoices_table.setItem(row_position, 2, QTableWidgetItem(str(invoice['number'])))
            self.ui.invoices_table.setItem(row_position, 3, QTableWidgetItem(str(invoice['name'])))
            self.ui.invoices_table.setItem(row_position, 4, QTableWidgetItem(str(invoice['date_col'])))

    def openInvoiceViewWindow(self):
        selected_row = self.ui.invoices_table.currentRow()
        if selected_row >= 0:
            invoice_id = self.ui.invoices_table.item(selected_row, 0).text()
            invoice_number = self.ui.invoices_table.item(selected_row, 2).text()
            if self.windows_manager.checkIfWindowIsOpen(f'InvoiceView_{invoice_number}Window'): 
                self.windows_manager.raiseWindow(f'InvoiceView_{invoice_number}Window')
            else:
                Ui_InvoiceView_Logic(self.sql_connector, invoice_id, invoice_number).showUi()
                self.fetchInvoices()

    def removeInvoice(self):
        selected_row = self.ui.invoices_table.currentRow()
        if selected_row >= 0:
            try:
                if win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), win32con.MB_YESNO) == win32con.IDYES:
                    invoice_id = self.ui.invoices_table.item(selected_row, 0).text()
                    self.database_operations.removeInvoice(invoice_id, commit=False)
                    self.database_operations.deleteJournalEntry(origin_id=invoice_id)
                    self.fetchInvoices()
            except Exception as e:
                print(e)
                win32api.MessageBox(0, self.language_manager.translate('INVOICE_DELETE_ERROR'), self.language_manager.translate('ERROR'))
