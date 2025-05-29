from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from DatabaseOperations import DatabaseOperations
from Ui_InvoicePicker import Ui_InvoicePicker

class Ui_InvoicePicker_Logic(QDialog):
    def __init__(self, sql_connector, pick_invoice=False, pick_invoice_item=True):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_InvoicePicker()
        self.pick_invoice = pick_invoice
        self.pick_invoice_item = pick_invoice_item

    
    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.returned_value = None
        window.exec()

    def initialize(self, window):
        self.fetchInvoices()
        self.ui.invoices_table.itemSelectionChanged.connect(lambda: self.fetchInvoiceItems())
        if self.pick_invoice:
            self.ui.pick_invoice_btn.setEnabled(True)
        if self.pick_invoice_item:
            self.ui.pick_invoice_item_btn.setEnabled(True)
        self.ui.pick_invoice_btn.clicked.connect(lambda: self.returnInvoice(window))
        self.ui.pick_invoice_item_btn.clicked.connect(lambda: self.returnInvoiceItem(window))

    def fetchInvoices(self):
        self.ui.invoices_table.setRowCount(0)
        invoices = self.database_operations.fetchAllInvoices()
        for invoice in invoices:
            id = invoice[0]
            date = invoice[1]
            paid = invoice[2]
            number = invoice[3]
            currency = invoice[4]
            invoice_currency_name = invoice[5]
            name = invoice[6]
            client_id = invoice[7]
            invoice_value = invoice[8]
            paid_ammount = invoice[9]

            num_row = self.ui.invoices_table.rowCount()
            self.ui.invoices_table.insertRow(num_row)
            self.ui.invoices_table.setItem(num_row, 0, QTableWidgetItem(str(id)))
            self.ui.invoices_table.setItem(num_row, 1, QTableWidgetItem(str(client_id)))
            self.ui.invoices_table.setItem(num_row, 2, QTableWidgetItem(str(name)))
            self.ui.invoices_table.setItem(num_row, 3, QTableWidgetItem(str(date)))

    def fetchInvoiceItems(self):
        self.ui.invoice_items_table.setRowCount(0)

        invoice_id=None
        current_row = self.ui.invoices_table.currentRow()
        if current_row:
            item =self.ui.invoices_table.item(current_row, 0)
            if item is not None:
                invoice_id = item.text()

        if invoice_id:
            invoice_items = self.database_operations.fetchInvoiceItems(invoice_id)
            for invoice_item in invoice_items:
                id = invoice_item['id']
                material_id = invoice_item['material_id']
                name = invoice_item['name']
                unit_price = invoice_item['unit_price']
                quantity1 = invoice_item['quantity1']
                unit1_id = invoice_item['unit1_id']
                unit_name = invoice_item['unit_name']

                num_row = self.ui.invoice_items_table.rowCount()
                self.ui.invoice_items_table.insertRow(num_row)
                self.ui.invoice_items_table.setItem(num_row, 0, QTableWidgetItem(str(id)))
                self.ui.invoice_items_table.setItem(num_row, 1, QTableWidgetItem(str(material_id)))
                self.ui.invoice_items_table.setItem(num_row, 2, QTableWidgetItem(str(name)))
                self.ui.invoice_items_table.setItem(num_row, 3, QTableWidgetItem(str(unit_price)))
                self.ui.invoice_items_table.setItem(num_row, 4, QTableWidgetItem(str(quantity1)))
                self.ui.invoice_items_table.setItem(num_row, 5, QTableWidgetItem(str(unit1_id)))
                self.ui.invoice_items_table.setItem(num_row, 6, QTableWidgetItem(str(unit_name)))

    def returnInvoice(self, window):
        invoice_id=None
        current_row = self.ui.invoices_table.currentRow()
        if str(current_row)!='' and str(current_row).lower()!='none':
            item =self.ui.invoices_table.item(current_row, 0)
            if item is not None:
                invoice_id = item.text()
                self.returned_value = invoice_id
                window.accept()

    def returnInvoiceItem(self, window):
        invoice_item_id=None
        current_row = self.ui.invoice_items_table.currentRow()
        if str(current_row)!='' and str(current_row).lower()!='none':
            item =self.ui.invoice_items_table.item(current_row, 0)
            if item is not None:
                invoice_item_id = item.text()
                self.returned_value=invoice_item_id
                window.accept()

    def returnInvoiceResult(self, invoice_id):
        self.parent.invoice_id = invoice_id