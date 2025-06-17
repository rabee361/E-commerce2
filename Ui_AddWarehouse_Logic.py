import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_AddWarehouse import Ui_AddWarehouse
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QPushButton, QComboBox


class Ui_AddWarehouse_Logic(QDialog):
    def __init__(self, sql_connector, independent=False):
        super().__init__()
        self.sql_connector = sql_connector
        self.independent = independent
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AddWarehouse()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)   
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchWarehouses()
        self.fetchUnits()
        self.ui.save_btn.clicked.connect(lambda: self.save(window))
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.account_combobox))
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())
        self.ui.account_combobox.setEnabled(False)
        self.ui.parent_combobox.setEnabled(False)
        self.ui.capacity_input.setValidator(QDoubleValidator())
        # Disable all account-related widgets in independent mode
        if self.independent:
            for widget in self.window.findChildren(QPushButton):
                if 'account' in widget.objectName().lower():
                    widget.setEnabled(False)
            
            for widget in self.window.findChildren(QComboBox):
                if 'account' in widget.objectName().lower():
                    widget.setEnabled(False)



    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit['id']
            name = unit['name']
            self.ui.capacity_unit_combobox.addItem(name, id)


    def fetchAccounts(self):
        data = None
        view_name = "لا يوجد"
        self.ui.account_combobox.addItem(view_name, data)

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account['id']
            name = account['name']
            code = account['code']
            
            data = id
            view_name = code + " - " + name
            self.ui.account_combobox.addItem(view_name, data)

    def openSelectParentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def fetchWarehouses(self):
        data = None
        view_name = "لا يوجد"
        self.ui.parent_combobox.addItem(view_name, data)

        accounts = self.database_operations.fetchWarehouses()
        for account in accounts:
            id = account['id']
            name = account['name']
            code = account['code']

            data = id
            view_name = str(code) + " - " + str(name)
            self.ui.parent_combobox.addItem(view_name, data)

    def save(self, window):
        name = self.ui.name_input.text()
        code = self.ui.code_input.text()
        parent = self.ui.parent_combobox.currentData() 
        account = self.ui.account_combobox.currentData()
        address = self.ui.address_input.text()
        manager = self.ui.manager_input.text()
        capacity = self.ui.capacity_input.text()
        capacity_unit = self.ui.capacity_unit_combobox.currentData() or ''
        notes = self.ui.notes_input.text()

        if not name or str(str(name).replace(" ",""))=='':
            win32api.MessageBox(0,self.language_manager.translate("NAME_CANNOT_BE_NONE"),self.language_manager.translate("ERROR"))
            return
        if capacity and not capacity_unit:
            win32api.MessageBox(0,self.language_manager.translate("ALERT_SELECT_CAPACITY_UNIT"),self.language_manager.translate("ERROR"))
            return

        warehouses = self.database_operations.fetchWarehouses()
        # Check if name already exists in warehouses
        for warehouse in warehouses:
            if (warehouse['name'].lower() == name.lower() or warehouse['codename'].lower() == code.lower()):
                win32api.MessageBox(0, self.language_manager.translate("ALERT_WAREHOUSE_ALREADY_EXISTS"), self.language_manager.translate("ERROR")) 
                return

        else:
            self.database_operations.addWarehouse(name, code, parent, account, address, manager, capacity, capacity_unit, notes)
            window.accept()
