from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_AddReceiptDocs import Ui_AddReceiptDocs
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
import win32api
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_AddReceiptDocs_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AddReceiptDocs()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.selected_invoice_id = None
        self.selected_invoice_item_id = None

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        from PyQt5.QtCore import QDate
        current_date = QDate.currentDate()
        self.ui.date_input.setDate(current_date)
        self.fetchMaterials()
        self.fetchWarehouses()
        self.fetchUnits()
        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.enableAllowedUnits())
        self.enableAllowedUnits()  # Ensure logic is applied when the UI is first opened
        self.ui.pick_invoice_btn.clicked.connect(lambda: self.openInvoicePicker())  # Link the button to the picker
        self.ui.save_btn.clicked.connect(lambda: self.save(window))  # Link the save button to the save method
        self.ui.show_invoice_btn.clicked.connect(lambda: self.openInvoiceViewWindow())

        self.ui.target_warehouse_combobox.setDisabled(True)
        self.ui.rejection_warehouse_combobox.setDisabled(True)
        self.ui.select_target_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow(self.ui.target_warehouse_combobox))
        self.ui.select_rejection_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow(self.ui.rejection_warehouse_combobox))
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())

    def openSelectWarehouseWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials')
        result = data_picker.showUi()
        if result:
            for i in range(self.ui.materials_combobox.count()):
                if self.ui.materials_combobox.itemData(i)[0] == result['id']:
                    self.ui.materials_combobox.setCurrentIndex(i)
                    break

    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        self.ui.materials_combobox.clear()
        for material in materials:
            material_id = material[0]
            material_units = [material[12], material[13], material[14]]
            self.ui.materials_combobox.addItem(material[2], [material_id, material_units])

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        self.ui.target_warehouse_combobox.clear()
        self.ui.rejection_warehouse_combobox.clear()
        for warehouse in warehouses:
            self.ui.target_warehouse_combobox.addItem(warehouse[1], warehouse[0])
            self.ui.rejection_warehouse_combobox.addItem(warehouse[1], warehouse[0])

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        self.ui.units_combobox.clear()
        for unit in units:
            self.ui.units_combobox.addItem(unit[1], unit[0])

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

    def openInvoicePicker(self):
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
                    current_material_id = self.ui.materials_combobox.currentData()[0]
                    if str(invoice_item_data_material_id) == str(current_material_id):
                        self.selected_invoice_id = result['primary']['id']
                        self.selected_invoice_item_id = invoice_item_id
                        invoice_number = result['primary']['number']
                        self.ui.invoice_number_input.setText(f"{invoice_number} - {self.language_manager.translate('INVOICE_ITEM')}: {invoice_item_id}")
                    else:
                        win32api.MessageBox(0, self.language_manager.translate("INVOICE_ITEM_NOT_FOR_SELECTED_MATERIAL_ERROR"), self.language_manager.translate("ALERT"))

    def openInvoiceViewWindow(self):
        if self.selected_invoice_id:
            invoice_view_window = Ui_InvoiceView_Logic(self.sql_connector, self.selected_invoice_id)
            invoice_view_window.showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate("INVOICE_ITEM_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))

    def save(self, window):
        material_id = self.ui.materials_combobox.currentData()[0]
        target_warehouse_id = self.ui.target_warehouse_combobox.currentData()
        rejection_warehouse_id = self.ui.rejection_warehouse_combobox.currentData()
        unit_id = self.ui.units_combobox.currentData()
        quantity = self.ui.quantity_input.text()
        date = self.ui.date_input.date().toString("yyyy-MM-dd")
        invoice_item_id = self.selected_invoice_item_id

        if invoice_item_id:
            if quantity:
                self.database_operations.addReceiptDoc(material_id, target_warehouse_id, rejection_warehouse_id, unit_id, quantity, invoice_item_id, date)
                window.accept()
            else:
                win32api.MessageBox(0, self.language_manager.translate("QUANTITY_MUST_BE_ENTERED"), self.language_manager.translate("ALERT"))
        else:
            win32api.MessageBox(0, self.language_manager.translate("INVOICE_ITEM_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))