from DatabaseOperations import DatabaseOperations
from PyQt5.QtWidgets import QDialog, QSizePolicy, QTableWidgetItem
from PyQt5.QtCore import Qt
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
import win32api
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from Ui_InventoryReport import Ui_InventoryReport

class Ui_InventoryReport_Logic(QDialog):
    def __init__(self, sql_connector=''):
        super().__init__()
        self.sql_connector = sql_connector
        if self.sql_connector:
            self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_InventoryReport()
        self.filemanager = ''
        self.current_user = ''
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)   
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchWarehouses()
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouse())
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            self.ui.warehouse_combobox.addItem(str(name), id)

    def openSelectWarehouse(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.warehouse_combobox.setCurrentIndex(self.ui.warehouse_combobox.findData(result['id']))

    def calculate(self):
        warehouse_id = self.ui.warehouse_combobox.currentData()
        to_date = self.ui.to_date_input.date().toString("yyyy-MM-dd")
        
        if warehouse_id:
            # Clear previous results
            self.ui.results_table.setRowCount(0)
            
            # Get all material moves for this warehouse up to the specified date
            warehouse_moves = self.database_operations.fetchWarehouseMoves(warehouse_id, to_date)
            materials = {}  # Dictionary to track materials and their quantities
            
            # Process each material move
            for material_move in warehouse_moves:
                if material_move['material_id'] and material_move['move_quantity'] and material_move['material_id'] != 0:
                    material_id = material_move['material_id']
                    
                    # Initialize material in dictionary if not exists
                    if material_id not in materials:
                        materials[material_id] = {
                            'id': material_id,
                            'name': material_move['material_name'],
                            'unit': material_move['unit_name'],
                            'quantity': 0
                        }
                    # Update quantity based on warehouse role (source or destination)
                    if material_move['source_warehouse'] == warehouse_id:
                        # Material leaving the warehouse
                        materials[material_id]['quantity'] -= material_move['move_quantity']
                    elif material_move['destination_warehouse'] == warehouse_id:
                        # Material entering the warehouse
                        materials[material_id]['quantity'] += material_move['move_quantity']
                
            # Display results in table
            for material_id, material_data in materials.items():
                row = self.ui.results_table.rowCount()
                self.ui.results_table.insertRow(row)
                
                # Set values in table
                self.ui.results_table.setItem(row, 0, QTableWidgetItem(str(material_data['id'])))  # Code column
                self.ui.results_table.setItem(row, 1, QTableWidgetItem(material_data['name']))  # Name column
                self.ui.results_table.setItem(row, 2, QTableWidgetItem(str(material_data['quantity'])))  # Total Quantity column
                self.ui.results_table.setItem(row, 3, QTableWidgetItem(material_data['unit']))  # Unit column
            
        else:
            win32api.MessageBox(0, self.language_manager.translate("MATERIAL_WAREHOUSE_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"), 0x00000040)
