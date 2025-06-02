import os
import win32api
import win32con
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QProgressBar, QProgressDialog, QApplication
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
from datetime import datetime
from PyQt5.QtCore import QCoreApplication
from win32con import MB_YESNO, IDYES, IDNO
from LanguageManager import LanguageManager 
from PyQt5.QtWidgets import QLabel
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import QTimer
from DatabaseOperations import DatabaseOperations
from Ui_Currencies_Logic import Ui_Currencies_Logic
from Ui_Settings import Ui_Settings
from Ui_ExpensesSettings_Logic import Ui_ExpensesSettings_Logic
from Ui_InvoicesSettings_Logic import Ui_InvoicesSettings_Logic
from Ui_WarehouseVariables_Logic import Ui_WarehouseVariables_Logic
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_ShortCutSettings_Logic import Ui_ShortCutSettings_Logic
from Ui_FloatPointSettings_Logic import Ui_FloatPointSettings_Logic
from Ui_Synchronization_Settings_Logic import Ui_Synchronization_Settings_Logic
from Ui_Media_Logic import Ui_Media_Logic
from Ui_ApiKeys_Logic import Ui_ApiKeys_Logic
from ProgressBar import ProgressBar
from PyQt5.QtCore import QTranslator
from LoadingOverlay import LoadingOverlay


class Ui_Settings_Logic(QDialog):
    DatabaseOperations = ''

    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Settings()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.first_period_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.last_period_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.operations_fixation_date_input.setDisplayFormat("dd-MM-yyyy")

        self.fetchWarehouses()
        self.fetchAccounts()
        self.setWarehouseAccount()
        self.fetchManufactureHalls()
        self.fetchLanguages()
        self.fetchValues()

        self.ui.warehouses_combobox.currentIndexChanged.connect(lambda: self.setWarehouseAccount())

        self.ui.select_capital_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.default_capital_account_combobox))
        self.ui.select_period_start_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.default_period_start_account_combobox))
        self.ui.select_mid_output_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.mid_output_account))
        self.ui.select_mid_input_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.mid_input_account))
        self.ui.select_output_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.output_account))
        self.ui.select_input_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.input_account))
        self.ui.select_damaged_materials_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())

        self.ui.default_capital_account_combobox.setEnabled(False)
        self.ui.warehouses_combobox.setEnabled(False)

        self.ui.save_btn.clicked.connect(lambda: self.saveValues())
        self.ui.save_btn.clicked.connect(window.accept)
        self.ui.cancel_btn.clicked.connect(window.accept)

        self.ui.add_manufacture_hall_warehouse.clicked.connect(lambda: self.addManufactureHall())
        self.ui.add_manufacture_hall_warehouse.clicked.connect(lambda: self.fetchManufactureHalls())
        self.ui.remove_manufacture_hall_warehouse.clicked.connect(lambda: self.removeManufactureHall())
        self.ui.remove_manufacture_hall_warehouse.clicked.connect(lambda: self.fetchManufactureHalls())

        self.ui.media_btn.clicked.connect(lambda: self.openMediaWindow())
        self.ui.api_keys_btn.clicked.connect(lambda: self.openApiKeysWindow())
        self.ui.currency_management_btn.clicked.connect(lambda: self.openCurrenciesWindow())
        self.ui.invoices_settings_btn.clicked.connect(lambda: self.openInvoicesSettingsWindow())
        self.ui.expenses_types_btn.clicked.connect(lambda: self.openExpensesSettingsWindow())
        self.ui.set_warehouses_variables_btn.clicked.connect(lambda: self.openWarehousesVariablesWindow())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.shortcut_settings_btn.clicked.connect(lambda: self.openShortCutSettingsWindow())
        self.ui.float_point_setting_btn.clicked.connect(lambda: self.openFloatPointSettingsWindow())
        self.ui.synchronization_settings_btn.clicked.connect(lambda: self.openSynchronizationSettingsWindow())

    def fetchValues(self):
        first_period = self.database_operations.fetchSetting('first_period')
        last_period = self.database_operations.fetchSetting('last_period')
        operations_fixation = self.database_operations.fetchSetting('operations_fixation')
        default_currency = self.database_operations.fetchSetting('default_currency')
        capital_account = self.database_operations.fetchSetting('default_capital_account')
        default_period_start_account = self.database_operations.fetchSetting('default_period_start_account')
        inventory_type = self.database_operations.fetchSetting('inventory_type')
        mid_output_account = self.database_operations.fetchSetting('mid_output_account')
        mid_input_account = self.database_operations.fetchSetting('mid_input_account')
        output_account = self.database_operations.fetchSetting('output_account')
        input_account = self.database_operations.fetchSetting('input_account')

        current_language = self.language_manager.get_current_language()

        saved_journal_entries = self.database_operations.fetchSetting('saved_journal_entries')
        if saved_journal_entries == 'individual':
            self.ui.individual_journal_entries_radio.setChecked(True)
        elif saved_journal_entries == 'double':
            self.ui.double_journal_entries_radio.setChecked(True)

        if inventory_type == 'perpetual':
            self.ui.perpetual_option_radio.setChecked(True)
        elif inventory_type == 'periodic':
            self.ui.periodic_option_radio.setChecked(True)

        first_period = datetime.strptime(str(first_period), '%Y-%m-%d')
        last_period = datetime.strptime(str(last_period), '%Y-%m-%d')
        operations_fixation = datetime.strptime(str(operations_fixation), '%Y-%m-%d')

        self.ui.first_period_date_input.setDate(first_period)
        self.ui.last_period_date_input.setDate(last_period)
        self.ui.operations_fixation_date_input.setDate(operations_fixation)

        try:
            self.ui.language_combobox.setCurrentIndex(self.ui.language_combobox.findData(current_language))
            self.ui.default_capital_account_combobox.setCurrentIndex(self.ui.default_capital_account_combobox.findData(capital_account))
            self.ui.default_period_start_account_combobox.setCurrentIndex(self.ui.default_period_start_account_combobox.findData(default_period_start_account))
            self.ui.mid_output_account.setCurrentIndex(self.ui.mid_output_account.findData(mid_output_account))
            self.ui.mid_input_account.setCurrentIndex(self.ui.mid_input_account.findData(mid_input_account))
            self.ui.output_account.setCurrentIndex(self.ui.output_account.findData(output_account))
            self.ui.input_account.setCurrentIndex(self.ui.input_account.findData(input_account))
        except Exception as e:
            print(e)

        currencies = self.database_operations.fetchCurrencies()
        for Currency in currencies:
            id = Currency[0]
            display_text = Currency[1]
            data = id
            self.ui.currency_combobox.addItem(display_text, data)
        try:
            self.ui.currency_combobox.setCurrentIndex(self.ui.currency_combobox.findData(default_currency))
        except:
            win32api.MessageBox(0, self.language_manager.translate("DEFAULT_CURRENCY_ERROR"), self.language_manager.translate("ERROR"))

    def fetchLanguages(self):
        self.ui.language_combobox.addItem("English", "en")
        self.ui.language_combobox.addItem("عربي", "ar")

    def openMediaWindow(self):
        Ui_Media_Logic(self.sql_connector).showUi()

    def openCurrenciesWindow(self):
        Ui_Currencies_Logic(self.sql_connector).showUi()

    def openApiKeysWindow(self):
        Ui_ApiKeys_Logic(self.sql_connector).showUi()

    def openExpensesSettingsWindow(self):
        Ui_ExpensesSettings_Logic(self.sql_connector).showUi()

    def openInvoicesSettingsWindow(self):
        Ui_InvoicesSettings_Logic(self.sql_connector).showUi()

    def openWarehousesVariablesWindow(self):
        Ui_WarehouseVariables_Logic(self.sql_connector).showUi()

    def openFloatPointSettingsWindow(self):
        Ui_FloatPointSettings_Logic(self.sql_connector).showUi()

    def openShortCutSettingsWindow(self):
        Ui_ShortCutSettings_Logic(self.sql_connector).showUi()

    def openSynchronizationSettingsWindow(self):
        Ui_Synchronization_Settings_Logic(self.sql_connector).showUi()

    def saveValues(self):
        first_period = self.ui.first_period_date_input.date().toString('yyyy-MM-dd')
        last_period = self.ui.last_period_date_input.date().toString('yyyy-MM-dd')
        operations_fixation = self.ui.operations_fixation_date_input.date().toString('yyyy-MM-dd')

        language = self.ui.language_combobox.currentData()
        
        self.language_manager.set_default_language(language)

        saved_journal_entries = 'individual' if self.ui.individual_journal_entries_radio.isChecked() else 'double'
        
        default_currency = self.ui.currency_combobox.currentData()
        default_capital_account = self.ui.default_capital_account_combobox.currentData()
        default_period_start_account = self.ui.default_period_start_account_combobox.currentData()
        mid_output_account = self.ui.mid_output_account.currentData()
        mid_input_account = self.ui.mid_input_account.currentData()
        output_account = self.ui.output_account.currentData()
        input_account = self.ui.input_account.currentData()
        
        damaged_materials_warehouse = self.ui.damaged_materials_warehouse_combobox.currentData()

        if (first_period):
            self.database_operations.saveSetting('first_period', first_period)
        if (last_period):
            self.database_operations.saveSetting('last_period', last_period)
        if (operations_fixation):
            self.database_operations.saveSetting('operations_fixation', operations_fixation)
        if (saved_journal_entries):
            self.database_operations.saveSetting('saved_journal_entries', saved_journal_entries)
        if (default_currency):
            self.database_operations.saveSetting('default_currency', default_currency)
        if (default_capital_account):
            self.database_operations.saveSetting('default_capital_account', default_capital_account)
        if (default_period_start_account):
            self.database_operations.saveSetting('default_period_start_account', default_period_start_account)
        if (mid_output_account):
            self.database_operations.saveSetting('mid_output_account', mid_output_account)
        if (mid_input_account):
            self.database_operations.saveSetting('mid_input_account', mid_input_account)
        if (output_account):
            self.database_operations.saveSetting('output_account', output_account)
        if (input_account):
            self.database_operations.saveSetting('input_account', input_account)
        if (damaged_materials_warehouse):
            self.database_operations.saveSetting('damaged_materials_warehouse', damaged_materials_warehouse)

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            display_text = warehouse['name']
            account_id = warehouse['account']
            data = [id, account_id]
            self.ui.warehouses_combobox.addItem(display_text, data)

    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.warehouses_combobox.count()):
                if self.ui.warehouses_combobox.itemData(i)[0] == result['id']:
                    self.ui.warehouses_combobox.setCurrentIndex(i)
                    break

    def openSelectDamagedWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.damaged_materials_warehouse_combobox.count()):
                if self.ui.damaged_materials_warehouse_combobox.itemData(i)[0] == result['id']:
                    self.ui.damaged_materials_warehouse_combobox.setCurrentIndex(i)
                    break

    def fetchAccounts(self):
        self.ui.accounts_combobox.addItem(self.language_manager.translate("NO_ACCOUNT"), None)
        self.ui.default_capital_account_combobox.addItem(self.language_manager.translate("NO_ACCOUNT"), None)
        self.ui.default_period_start_account_combobox.addItem(self.language_manager.translate("NO_ACCOUNT"), None)
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.accounts_combobox.addItem(display_text, data)
            self.ui.default_capital_account_combobox.addItem(display_text, data)
            self.ui.default_period_start_account_combobox.addItem(display_text, data)
            self.ui.mid_output_account.addItem(display_text, data)
            self.ui.mid_input_account.addItem(display_text, data)
            self.ui.output_account.addItem(display_text, data)
            self.ui.input_account.addItem(display_text, data)

    def setWarehouseAccount(self):
        warehouse_data = self.ui.warehouses_combobox.currentData()
        
        if warehouse_data and len(warehouse_data) > 0:
            account_id = warehouse_data[1]
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(account_id))

    def addManufactureHall(self):
        warehouse = self.ui.warehouses_combobox.currentData()
        account = self.ui.accounts_combobox.currentData()
        if account:
            try:
                warehouse_id = warehouse[0]
                if warehouse_id:
                    self.database_operations.addManufactureHall(warehouse_id)
            except Exception as e:
                print("An error occurred:", str(e))
        else:
            win32api.MessageBox(0, self.language_manager.translate("WAREHOUSE_NOT_CONNECTED_TO_ACCOUNT"), self.language_manager.translate("ALERT"))
            
    def removeManufactureHall(self):
        selected_row = self.ui.manufacture_halls_table.currentRow()
        if selected_row != -1:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                id_item = self.ui.manufacture_halls_table.item(selected_row,
                                                            0)  # Assuming ID is in the first column (index 0)
                if id_item is not None:
                    hall_id = id_item.text()
                    try:
                        self.database_operations.removeManufactureHall(hall_id)
                    except Exception as e:
                        print("An error occurred while deleting the manufacture hall:", str(e))
                        win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"), win32con.MB_ICONERROR)
            elif (messagebox_result == IDNO):
                pass

    def fetchManufactureHalls(self):
        self.ui.manufacture_halls_table.setRowCount(0)
        manufacture_halls = self.database_operations.fetchManufactureHalls()
        for manufacture_hall in manufacture_halls:
            id = manufacture_hall[0]
            warehouse_id = manufacture_hall[1]
            date = manufacture_hall[2]
            name = manufacture_hall[3]
            account_id = manufacture_hall[4]
            account_name = manufacture_hall[5]

            # Create a empty row at bottom of table
            numRows = self.ui.manufacture_halls_table.rowCount()
            self.ui.manufacture_halls_table.insertRow(numRows)

            # Add text to the row
            self.ui.manufacture_halls_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.manufacture_halls_table.setItem(numRows, 1, QTableWidgetItem(str(warehouse_id)))
            self.ui.manufacture_halls_table.setItem(numRows, 2, QTableWidgetItem(str(name)))
            self.ui.manufacture_halls_table.setItem(numRows, 3, QTableWidgetItem(str(account_id)))
            self.ui.manufacture_halls_table.setItem(numRows, 4, QTableWidgetItem(str(account_name)))

