from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QCoreApplication, QTranslator

from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_ReOrderMaterialReport import Ui_ReOrderMaterialReport
from LanguageManager import LanguageManager

class Ui_ReOrderMaterialReport_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_ReOrderMaterialReport()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window_activation):
        self.fetchWarehouses()
        self.ui.select_product_btn.clicked.connect(lambda: self.openSelectProduct())
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouse())
        
    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            self.ui.warehouse_combobox.addItem(str(name), id)
            
    def openSelectWarehouse(self):
        # This method will be called when the select warehouse button is clicked
        # Toggle the warehouse combobox popup
        self.ui.warehouse_combobox.showPopup()
        
    def fetchSelectedWarehouses(self):
        # Return the list of selected warehouse IDs
        return self.ui.warehouse_combobox.currentData()

    def fetchProducts(self):
        products = self.database_operations.fetchMaterials()
        for product in products:
            id = product['id']
            name = product['name']
            self.ui.product_combobox.addItem(str(name), id)

    def openSelectProduct(self):
        # This method will be called when the select product button is clicked
        # Toggle the product combobox popup
        self.ui.product_combobox.showPopup()

    def fetchSelectedProducts(self):
        pass

    def calculate(self):
        pass
        
