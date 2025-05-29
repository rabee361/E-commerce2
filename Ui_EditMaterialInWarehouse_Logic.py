from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_EditMaterialInWarehouse import Ui_EditMaterialInWarehouse

class Ui_EditMaterialInWarehouse_Logic(QDialog):
    def __init__(self, sql_connector, warehouse_id, warehouse_entry_id):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_EditMaterialInWarehouse()
        self.warehouse_entry_id = warehouse_entry_id
        self.warehouse_id = warehouse_id

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.quantity_input.setValidator(QDoubleValidator())
        self.fetchMaterial(self.warehouse_entry_id, self.warehouse_id)
        self.ui.save_btn.clicked.connect(lambda: self.save(window))

    def fetchMaterial(self, warehouse_entry_id, warehouse_id):

        warehouse_entry = self.database_operations.fetchWarehouseEntry(warehouse_entry_id, warehouse_id)
        id = warehouse_entry[0]
        material_id = warehouse_entry[1]
        quantity = warehouse_entry[2]
        unit = warehouse_entry[3]
        production_batch_id = warehouse_entry[4]
        invoice_item_id = warehouse_entry[5]
        code = warehouse_entry[6]
        name = warehouse_entry[7]

        material = self.database_operations.fetchMaterial(material_id)
        unit1_name = material['unit1_name']
        unit2_name = material['unit2_name']
        unit3_name = material['unit3_name']
        unit1_id = material['unit1']
        unit2_id = material['unit2']
        unit3_id = material['unit3']


        self.ui.units_combobox.addItem(unit1_name, unit1_id)
        self.ui.units_combobox.addItem(unit2_name, unit2_id)
        self.ui.units_combobox.addItem(unit3_name, unit3_id)

        self.ui.name_input.setText(name)
        self.ui.quantity_input.setText(str(quantity))
        self.ui.units_combobox.setCurrentIndex(self.ui.units_combobox.findData(unit))

    def save(self, window):
        quantity = self.ui.quantity_input.text()
        unit = self.ui.units_combobox.currentData()
        if not unit or str(unit).replace(" ","")=="":
            unit=""
        if quantity:
            self.database_operations.updateMaterialInWarehouse(self.warehouse_entry_id, self.warehouse_id, quantity, unit)
            window.accept()