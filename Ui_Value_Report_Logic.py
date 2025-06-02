from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Value_Report import Ui_Value_Report
from PyQt5.QtWidgets import  QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class Ui_Insurance_Report_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Value_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/hr.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        self.fetchMaterials()
        self.fetchCurrencies()
        self.fetchWarehouses()
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow)
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow)
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
 
    def calculate(self):
        material_id = self.ui.material_combobox.currentData()

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.currencies_combobox.addItem(name, id)

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.material_combobox.count()):
                if self.ui.material_combobox.itemData(i)[0] == result['id']:
                    self.ui.material_combobox.setCurrentIndex(i)
                    break

    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material['id']
            name = material['name']
            self.ui.material_combobox.addItem(name, id)

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            self.ui.warehouses_combobox.addItem(name, id)

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.warehouses_combobox.count()):
                if self.ui.warehouses_combobox.itemData(i)[0] == result['id']:
                    self.ui.warehouses_combobox.setCurrentIndex(i)
                    break
