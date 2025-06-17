import win32api
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from win32con import MB_YESNO, IDYES
from DatabaseOperations import DatabaseOperations
from Ui_Synchronization_Settings import Ui_Synchronization_Settings
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_Synchronization_Settings_Logic(QDialog):
    def __init__(self, sql_connector , progress=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Synchronization_Settings()
        self.progress = progress
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowModality(QtCore.Qt.WindowModal)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.setExpensesTypes()
        self.setPricingMethods()
        self.fetchUnits()
        self.fetchSynchronizationSettings()

        self.ui.save_btn.clicked.connect(lambda: self.saveSynchronizationSettings(window))
        self.ui.cancel_btn.clicked.connect(window.accept)

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit['id']
            name = unit['name']
            self.ui.radio_quantity_unit_expenses_combobox.addItem(name, id)

    def setPricingMethods(self):
        self.ui.material_pricing_method_combobox.addItem("Average", "average")
        self.ui.material_pricing_method_combobox.addItem("Real Price", "real_price")

    def setExpensesTypes(self):
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("MONTHLY_COSTS"), "month")
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("YEARLY_COSTS"), "year")
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("REAL_COSTS"), "real")

    def fetchSynchronizationSettings(self):
        try:

            material_pricing_method = self.database_operations.fetchSetting('material_pricing_method_sync')

            self.ui.material_pricing_method_combobox.setCurrentIndex(self.ui.material_pricing_method_combobox.findData(material_pricing_method))

            distribution_expenses = self.database_operations.fetchSetting('distribution_expenses_sync')
            self.ui.expenses_type_combobox.setCurrentIndex(self.ui.expenses_type_combobox.findData(distribution_expenses))

            expenses_type = self.database_operations.fetchSetting('distribution_expenses_type_sync')
            if expenses_type == 'no_expenses':
                self.ui.no_expenses_radio.setChecked(True)
            elif expenses_type == 'quantity_expenses':
                self.ui.quantity_expenses_radio.setChecked(True)
            elif expenses_type == 'hours_expenses':
                self.ui.hours_expenses_radio.setChecked(True)

            quantity_unit = self.database_operations.fetchSetting('expenses_quantity_unit_sync')
            self.ui.radio_quantity_unit_expenses_combobox.setCurrentIndex(self.ui.radio_quantity_unit_expenses_combobox.findData(quantity_unit))

        except Exception as e:
            print(e)

    def saveSynchronizationSettings(self, window):

        material_pricing_method = self.ui.material_pricing_method_combobox.currentData()
        if (material_pricing_method):
            self.database_operations.saveSetting('material_pricing_method_sync', material_pricing_method)
        
        distribution_expenses = self.ui.expenses_type_combobox.currentData()
        if (distribution_expenses):
            self.database_operations.saveSetting('distribution_expenses_sync', distribution_expenses)

        quantity_unit = self.ui.radio_quantity_unit_expenses_combobox.currentData()
        if (quantity_unit):
            self.database_operations.saveSetting('expenses_quantity_unit_sync', quantity_unit)

        if self.ui.no_expenses_radio.isChecked():
            self.database_operations.saveSetting('distribution_expenses_type_sync', 'no_expenses')
       
        if self.ui.quantity_expenses_radio.isChecked():
            self.database_operations.saveSetting('distribution_expenses_type_sync', 'quantity_expenses')

        if self.ui.hours_expenses_radio.isChecked():
            self.database_operations.saveSetting('distribution_expenses_type_sync', 'hours_expenses')

        window.accept()

        

        

