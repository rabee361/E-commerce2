"""
Why to roviding Receipt Docs in an Accounting System

In a factory management system, the workflow for incoming materials does not include invoices directly. Instead, the sequence is as follows:
Purchase Request -> Quotation (Price Offer) -> Deal -> Receipt Document

Therefore, it is essential to transfer receipt documents to the accounting department. The accountant receives the invoice, compares it with the receipt document, and records it accordingly. This process ensures that all incoming materials are accurately tracked and accounted for, maintaining the integrity and accuracy of the financial records.
"""
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from Ui_ReceiptDocs import Ui_ReceiptDocs
from DatabaseOperations import DatabaseOperations
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from Ui_AddReceiptDocs_Logic import Ui_AddReceiptDocs_Logic
from Ui_DataPicker_Logic import Ui_DataPicker_Logic    
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
import win32api
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_ReceiptDocs_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ReceiptDocs()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.selected_invoice_id = None
        self.selected_invoice_item_id = None

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        self.ui.add_new_receipt_doc_button.clicked.connect(lambda: self.openAddReceiptDocsLogic())
        self.ui.show_invoice_btn.clicked.connect(lambda: self.openInvoiceViewWindow())
        self.ui.receipt_docs_table.itemSelectionChanged.connect(lambda: self.fetchSelectedReceiptDoc())
        self.ui.delete_receipt_doc_btn.clicked.connect(lambda: self.deleteReceiptDoc())
        self.ui.pick_invoice_btn.clicked.connect(lambda: self.openInvoicePicker()) 
        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.enableAllowedUnits())
        self.ui.save_btn.clicked.connect(lambda: self.saveReceiptDoc())
        self.fetchUnits()
        self.fetchWarehouses()
        self.fetchMaterials()
        self.fetchReceiptDocs()
        self.disableUiInputs()
        self.enableAllowedUnits()  # Ensure logic is applied when the UI is first opened

        self.ui.target_warehouse_combobox.setDisabled(True)
        self.ui.rejection_warehouse_combobox.setDisabled(True)
        self.ui.select_target_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow(self.ui.target_warehouse_combobox))
        self.ui.select_rejection_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow(self.ui.rejection_warehouse_combobox))

    def openSelectWarehouseWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def disableUiInputs(self):
        self.ui.select_target_warehouse_btn.setEnabled(False)
        self.ui.select_rejection_warehouse_btn.setEnabled(False)
        self.ui.date_dateedit.setEnabled(False)
        self.ui.quantity_input.setEnabled(False)
        self.ui.units_combobox.setEnabled(False)
        self.ui.invoice_number_input.setEnabled(False)
        self.ui.save_btn.setEnabled(False)

    def enableUiInputs(self):
        self.ui.select_target_warehouse_btn.setEnabled(True)
        self.ui.select_rejection_warehouse_btn.setEnabled(True)
        self.ui.date_dateedit.setEnabled(True)
        self.ui.quantity_input.setEnabled(True)
        self.ui.units_combobox.setEnabled(True)
        self.ui.save_btn.setEnabled(True)

    def openAddReceiptDocsLogic(self):
        add_receipt_docs_logic = Ui_AddReceiptDocs_Logic(self.sql_connector)
        add_receipt_docs_logic.showUi()
        self.fetchReceiptDocs()
        
    def openInvoiceViewWindow(self):
        if self.selected_invoice_id:
            invoice_view_window = Ui_InvoiceView_Logic(self.sql_connector, self.selected_invoice_id)
            invoice_view_window.showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate("INVOICE_ITEM_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))

    def fetchUnits(self):
        # Logic to fetch and load units into the units_combobox
        units = self.database_operations.fetchUnits()
        self.ui.units_combobox.clear()
        for unit in units:
            self.ui.units_combobox.addItem(unit[1], unit[0])

    def fetchWarehouses(self):
        # Logic to fetch and load warehouses into the target_warehouse_combobox and rejection_warehouse_combobox
        warehouses = self.database_operations.fetchWarehouses()
        self.ui.target_warehouse_combobox.clear()
        self.ui.rejection_warehouse_combobox.clear()
        for warehouse in warehouses:
            self.ui.target_warehouse_combobox.addItem(warehouse[1], warehouse[0])
            self.ui.rejection_warehouse_combobox.addItem(warehouse[1], warehouse[0])
            
    def fetchMaterials(self):
        # Logic to fetch and load materials into the materials_combobox
        materials = self.database_operations.fetchMaterials()
        self.ui.materials_combobox.clear()
        for material in materials:
            material_id = material[0]
            material_units = [material[12], material[13], material[14]]
            self.ui.materials_combobox.addItem(material[2], [material_id, material_units])
        self.enableAllowedUnits()

    def fetchReceiptDocs(self):
        # Logic to fetch and load receipt documents into the table
        receipt_docs = self.database_operations.fetchReceiptDocs()
        self.ui.receipt_docs_table.setRowCount(0)
        for doc in receipt_docs:
            row_position = self.ui.receipt_docs_table.rowCount()
            self.ui.receipt_docs_table.insertRow(row_position)
            self.ui.receipt_docs_table.setItem(row_position, 0, QtWidgets.QTableWidgetItem(str(doc[0])))
            self.ui.receipt_docs_table.setItem(row_position, 1, QtWidgets.QTableWidgetItem(doc[3].strftime('%Y-%m-%d')))
            self.ui.receipt_docs_table.setItem(row_position, 2, QtWidgets.QTableWidgetItem(str(doc[4])))
            self.ui.receipt_docs_table.setItem(row_position, 3, QtWidgets.QTableWidgetItem(doc[8]))

    def fetchSelectedReceiptDoc(self):
        # Logic to get the id of the selected receipt document and fetch its details from the database
        selected_row = self.ui.receipt_docs_table.currentRow()
        if selected_row >= 0:
            self.enableUiInputs()
            receipt_doc_id = self.ui.receipt_docs_table.item(selected_row, 0).text()
            receipt_doc_details = self.database_operations.fetchReceiptDoc(receipt_doc_id)
            if receipt_doc_details:
                self.ui.target_warehouse_combobox.setCurrentIndex(
                    self.ui.target_warehouse_combobox.findData(receipt_doc_details['target_warehouse_id'])
                )
                self.ui.rejection_warehouse_combobox.setCurrentIndex(
                    self.ui.rejection_warehouse_combobox.findData(receipt_doc_details['rejection_warehouse_id'])
                )
                self.ui.date_dateedit.setDate(receipt_doc_details['date_col'])
                material_id = receipt_doc_details['material_id']
                for index in range(self.ui.materials_combobox.count()):
                    if self.ui.materials_combobox.itemData(index)[0] == material_id:
                        self.ui.materials_combobox.setCurrentIndex(index)
                        break
                self.ui.quantity_input.setText(str(receipt_doc_details['quantity']))
                self.ui.units_combobox.setCurrentIndex(
                    self.ui.units_combobox.findData(receipt_doc_details['unit_id'])
                )
                self.selected_invoice_id = receipt_doc_details['invoice_id']
                self.selected_invoice_item_id = receipt_doc_details['invoice_item_id']
                self.ui.invoice_number_input.setText(f"{receipt_doc_details['invoice_number']} - {self.language_manager.translate('INVOICE_ITEM')}: {receipt_doc_details['invoice_item_id']}")
            return receipt_doc_details
        else:
            self.disableUiInputs()
        return None
    
    def deleteReceiptDoc(self):
        # Logic to delete the selected receipt document from the database
        selected_row = self.ui.receipt_docs_table.currentRow()
        if selected_row >= 0:
            receipt_doc_id = self.ui.receipt_docs_table.item(selected_row, 0).text()
            confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("CONFIRM"), 1)
            if confirm == 1:  # IDYES
                self.database_operations.removeReceiptDoc(receipt_doc_id)
                self.fetchReceiptDocs()
        else:
            win32api.MessageBox(0, self.language_manager.translate("RECEIPT_DOC_NOT_SELECTED"), self.language_manager.translate("ERROR"), 0)

    def openInvoicePicker(self):
        selected_row = self.ui.receipt_docs_table.currentRow()
        if selected_row >= 0:
            if self.sql_connector and self.sql_connector.is_connected_to_database:
                invoice_columns = ['id', 'client_id', 'name', 'date_col']
                invoice_items_columns = ['id', 'material_id', 'name', 'unit_price', 'quantity1', 'unit1_id', 'unit_name']

                # Create picker with column lists
                picker = Ui_DataPicker_Logic(
                    self.sql_connector,
                    table_name='invoices',
                    columns=invoice_columns,
                    linked_table='invoice_items',
                    linked_columns=invoice_items_columns,
                    search_column='name'
                )

                result = picker.showUi()

                if result:    
                    invoice_item_id = result['linked']['id']    # linked data is related to invoice_item
                    if invoice_item_id:
                        invoice_item_data_material_id = result['linked']['material_id']
                        current_material_id = self.ui.receipt_docs_table.item(self.ui.receipt_docs_table.currentRow(), 2).text()
                        if str(invoice_item_data_material_id) == str(current_material_id):
                            self.selected_invoice_id = result['primary']['id']
                            self.selected_invoice_item_id = invoice_item_id
                            invoice_number = result['primary']['number']
                            self.ui.invoice_number_input.setText(f"{invoice_number} - {self.language_manager.translate('INVOICE_ITEM')}: {invoice_item_id}")
                        else:
                            win32api.MessageBox(0, self.language_manager.translate("INVOICE_ITEM_NOT_FOR_SELECTED_MATERIAL_ERROR"), self.language_manager.translate("ERROR"))
        else:
            win32api.MessageBox(0, self.language_manager.translate("RECEIPT_DOC_NOT_SELECTED"), self.language_manager.translate("ALERT"))

    def saveReceiptDoc(self):
        selected_row = self.ui.receipt_docs_table.currentRow()
        if selected_row >= 0:
            receipt_doc_id = self.ui.receipt_docs_table.item(selected_row, 0).text()
            material_id = self.ui.materials_combobox.currentData()[0]
            target_warehouse_id = self.ui.target_warehouse_combobox.currentData()
            rejection_warehouse_id = self.ui.rejection_warehouse_combobox.currentData()
            unit_id = self.ui.units_combobox.currentData()
            quantity = self.ui.quantity_input.text()
            date = self.ui.date_dateedit.date().toString("yyyy-MM-dd")
            invoice_item_id = self.selected_invoice_item_id if self.selected_invoice_item_id else ''

            if quantity:
                self.database_operations.updateReceiptDoc(receipt_doc_id, material_id, target_warehouse_id, rejection_warehouse_id, unit_id, quantity, invoice_item_id, date)
                self.fetchReceiptDocs()

    def enableAllowedUnits(self):
        selected_material_data = self.ui.materials_combobox.currentData()
        if selected_material_data:
            allowed_units = selected_material_data[1]
            for index in range(self.ui.units_combobox.count()):
                unit_id = self.ui.units_combobox.itemData(index)
                self.ui.units_combobox.model().item(index).setEnabled(unit_id in allowed_units)
            # Select the first enabled unit
            for index in range(self.ui.units_combobox.count()):
                if self.ui.units_combobox.model().item(index).isEnabled():
                    self.ui.units_combobox.setCurrentIndex(index)
                    break
