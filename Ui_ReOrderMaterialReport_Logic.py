from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QCoreApplication, QTranslator
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_ReOrderMaterialReport import Ui_ReOrderMaterialReport
from LanguageManager import LanguageManager
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QDoubleValidator
import win32api

class Ui_ReOrderMaterialReport_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector,filemanager=''):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_ReOrderMaterialReport()
        self.translator = QTranslator()
        self.filemanager = filemanager
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.fetchWarehouses()
        self.ui.percent_input.setValidator(QDoubleValidator())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        
    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            self.ui.warehouse_combobox.addItem(str(name), id)
         
    def openSelectWarehouseWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.warehouse_combobox.count()):
                warehouse_data = self.ui.warehouse_combobox.itemData(i)
                if warehouse_data[0] == result['id']:
                    self.ui.warehouse_combobox.setCurrentIndex(i)
                    return

    def calculate(self):
        percent = self.ui.percent_input.text()
        materials = self.database_operations.fetchMaterials()
        if percent:
            for material in materials:
                current_quantity = material['current_quantity']
                min_quantity = material['min_quantity']
                if not min_quantity:
                    continue
                calculated_quantity = min_quantity * (float(percent) / 100) + min_quantity
                # Check if total quantity exceeds capacity
                if calculated_quantity > current_quantity:
                    row = self.ui.materials_table.rowCount()
                    self.ui.materials_table.insertRow(row)
                    
                    # Set values in table
                    self.ui.materials_table.setItem(row, 0, QTableWidgetItem(str(material['id'])))  # Code column
                    self.ui.materials_table.setItem(row, 1, QTableWidgetItem(material['name']))  # 
                    self.ui.materials_table.setItem(row, 2, QTableWidgetItem(material['code']))  # 
                    self.ui.materials_table.setItem(row, 3, QTableWidgetItem(min_quantity))  # 
                    self.ui.materials_table.setItem(row, 4, QTableWidgetItem(current_quantity))  # 
        else:
            pass
