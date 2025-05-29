import re
import win32api
from PyQt5 import QtCore
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QDialog
from win32con import MB_YESNO, IDYES
from DatabaseOperations import DatabaseOperations
from Ui_InvoicesSettings import Ui_InvoicesSettings
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_InvoicesSettings_Logic(QDialog):
    def __init__(self, sql_connector , progress=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_InvoicesSettings()
        self.progress = progress
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowModality(QtCore.Qt.WindowModal)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        # Initialize empty lists for UI elements
        self.prices_comboboxes = []
        self.accounts_comboboxes = []
        self.warehouses_comboboxes = []
        self.cost_centers_comboboxes = []
        self.currencies_comboboxes = []
        self.affects_on_warehouse_comboboxes = []
        self.ui_checkboxes = []
        
        self.fetchAccounts()
        self.fetchPrices()
        self.fetchWarehouses()
        self.fetchCurrencies()
        self.fetchCostCenters()
       # self.fetchInvoicesSettings()
        self.fetchInvoicesTypes()
        self.ui.save_btn.clicked.connect(lambda: self.saveInvoicesSettings(window))

        # The next two lines add a new tab with a "+" sign to the tab widget
        # and connect the tab bar click event to the handleTabClick method.
        self.ui.tabWidget.addTab(QtWidgets.QWidget(), "+")
        self.ui.tabWidget.tabBarClicked.connect(self.addNewInvoiceType)
        if self.progress:
            self.progress.close()

    def fetchInvoicesTypes(self):
        # Dynamic invoice types
        invoices_types = self.database_operations.fetchInvoiceTypes()
        
        for invoice_type in invoices_types:
            invoice_type_name = invoice_type['name']
            if invoice_type_name in ['sell', 'sell_return', 'buy', 'buy_return', 'input', 'output']:
                self.createInvoiceTypeTab(invoice_type_name)
            else:
                self.createInvoiceTypeTab(invoice_type_name, is_custom=True)

    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        temp = combobox.objectName()
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def createInvoiceTypeTab(self, tab_name, is_custom=False):
        # Check if tab already exists
        for i in range(self.ui.tabWidget.count()):
            if self.ui.tabWidget.tabText(i) == tab_name:
                return
                
        # Create lists for this tab
        prefix = "custom_invoice_type_" if is_custom else ""
        
        # Extend the class-level lists with new UI elements
        new_prices = [
            f"{prefix}{tab_name}_invoice_price_combobox",
            f"{prefix}{tab_name}_cost_price_combobox",
            f"{prefix}{tab_name}_gift_price_combobox"
        ]
        self.prices_comboboxes.extend([x for x in new_prices if x not in self.prices_comboboxes])
        
        new_accounts = [
            f"{prefix}{tab_name}_materials_account_combobox",
            f"{prefix}{tab_name}_discounts_account_combobox", 
            f"{prefix}{tab_name}_addition_account_combobox",
            f"{prefix}{tab_name}_monetary_account_combobox",
            f"{prefix}{tab_name}_added_value_account_combobox",
            f"{prefix}{tab_name}_cost_account_combobox",
            f"{prefix}{tab_name}_stock_account_combobox",
            f"{prefix}{tab_name}_gifts_account_combobox",
            f"{prefix}{tab_name}_gifts_opposite_account_combobox",
            f"{prefix}{tab_name}_items_discounts_account_combobox",
            f"{prefix}{tab_name}_items_additions_account_combobox"
        ]
        self.accounts_comboboxes.extend([x for x in new_accounts if x not in self.accounts_comboboxes])
        
        new_warehouses = [f"{prefix}{tab_name}_warehouse_combobox"]
        self.warehouses_comboboxes.extend([x for x in new_warehouses if x not in self.warehouses_comboboxes])
        
        new_cost_centers = [f"{prefix}{tab_name}_cost_center_combobox"]
        self.cost_centers_comboboxes.extend([x for x in new_cost_centers if x not in self.cost_centers_comboboxes])
        
        new_currencies = [f"{prefix}{tab_name}_currency_combobox"]
        self.currencies_comboboxes.extend([x for x in new_currencies if x not in self.currencies_comboboxes])

        new_affects_on_warehouse = [f"{prefix}{tab_name}_affects_on_warehouse_combobox"]
        self.affects_on_warehouse_comboboxes.extend([x for x in new_affects_on_warehouse if x not in self.affects_on_warehouse_comboboxes])
        
        new_checkboxes = [
            f"{prefix}{tab_name}_affects_materials_gain_loss_checkbox",
            f"{prefix}{tab_name}_affects_client_price_checkbox", 
            f"{prefix}{tab_name}_discounts_affects_cost_price_checkbox",
            f"{prefix}{tab_name}_discounts_affects_gain_checkbox",
            f"{prefix}{tab_name}_affects_last_buy_price_checkbox",
            f"{prefix}{tab_name}_additions_affects_cost_price_checkbox",
            f"{prefix}{tab_name}_additions_affects_gain_checkbox",
            f"{prefix}{tab_name}_affects_cost_price_checkbox"
        ]
        self.ui_checkboxes.extend([x for x in new_checkboxes if x not in self.ui_checkboxes])

        # Create new tab widget
        new_tab = QtWidgets.QWidget()
        
        # Create the three main group boxes
        default_values_group = QtWidgets.QGroupBox(self.language_manager.translate("INVOICE_SETTINGS_DEFAULT_VALUES"))
        default_values_group.setGeometry(QtCore.QRect(9, 9, 309, 309))
        
        default_accounts_group = QtWidgets.QGroupBox(self.language_manager.translate("INVOICE_SETTINGS_DEFAULT_ACCOUNTS"))
        default_accounts_group = QtWidgets.QGroupBox(self.language_manager.translate( "INVOICE_SETTINGS_DEFAULT_ACCOUNTS"))
        default_accounts_group.setGeometry(QtCore.QRect(324, 9, 309, 309))
        
        effects_group = QtWidgets.QGroupBox(self.language_manager.translate("INVOICE_SETTINGS_EFFECTS"))
        effects_group = QtWidgets.QGroupBox(self.language_manager.translate( "INVOICE_SETTINGS_EFFECTS"))
        effects_group.setGeometry(QtCore.QRect(9, 324, 624, 120))
        
        # Create layouts for each group
        default_values_layout = QtWidgets.QGridLayout(default_values_group)
        default_accounts_layout = QtWidgets.QGridLayout(default_accounts_group)
        effects_layout = QtWidgets.QGridLayout(effects_group)
        
        # Add comboboxes to default values group
        combos = [
            (f"{prefix}{tab_name}_invoice_price_combobox", "INVOICE_SETTINGS_INVOICE_PRICE", self.fetchPrices),
            (f"{prefix}{tab_name}_cost_price_combobox", "INVOICE_SETTINGS_COST_PRICE", self.fetchPrices),
            (f"{prefix}{tab_name}_gift_price_combobox", "INVOICE_SETTINGS_GIFT_PRICE", self.fetchPrices),
            (f"{prefix}{tab_name}_warehouse_combobox", "INVOICE_SETTINGS_WAREHOUSE", self.fetchWarehouses),
            (f"{prefix}{tab_name}_cost_center_combobox", "INVOICE_SETTINGS_COST_CENTER", self.fetchCostCenters),
            (f"{prefix}{tab_name}_currency_combobox", "INVOICE_SETTINGS_CURRENCY", self.fetchCurrencies)
        ]

        for i, (name, label_key, fetch_func) in enumerate(combos):
            label_widget = QtWidgets.QLabel(self.language_manager.translate(label_key))
            combo = QtWidgets.QComboBox()
            combo.setObjectName(name)
            default_values_layout.addWidget(label_widget, i, 0)
            default_values_layout.addWidget(combo, i, 1)
            fetch_func(combo)
            setattr(self.ui, name, combo)
            
            # Set value from database
            setting_name = name.replace('_combobox', '')
            value = self.database_operations.fetchSetting(setting_name)
            if value:
                combo.setCurrentIndex(combo.findData(value))

        # Add comboboxes to default accounts group
        account_combos = [
            (f"{prefix}{tab_name}_materials_account_combobox", "INVOICE_SETTINGS_MATERIALS_ACCOUNT"),
            (f"{prefix}{tab_name}_discounts_account_combobox", "INVOICE_SETTINGS_DISCOUNTS_ACCOUNT"),
            (f"{prefix}{tab_name}_addition_account_combobox", "INVOICE_SETTINGS_ADDITIONS_ACCOUNT"),
            (f"{prefix}{tab_name}_monetary_account_combobox", "INVOICE_SETTINGS_MONETARY_ACCOUNT"),
            (f"{prefix}{tab_name}_added_value_account_combobox", "INVOICE_SETTINGS_ADDED_VALUE_ACCOUNT"),
            (f"{prefix}{tab_name}_cost_account_combobox", "INVOICE_SETTINGS_COST_ACCOUNT"),
            (f"{prefix}{tab_name}_stock_account_combobox", "INVOICE_SETTINGS_STOCK_ACCOUNT"),
            (f"{prefix}{tab_name}_gifts_account_combobox", "INVOICE_SETTINGS_GIFTS_ACCOUNT"),
            (f"{prefix}{tab_name}_gifts_opposite_account_combobox", "INVOICE_SETTINGS_GIFTS_OPPOSITE_ACCOUNT"),
            (f"{prefix}{tab_name}_items_discounts_account_combobox", "INVOICE_SETTINGS_ITEMS_DISCOUNTS_ACCOUNT"),
            (f"{prefix}{tab_name}_items_additions_account_combobox", "INVOICE_SETTINGS_ITEMS_ADDITIONS_ACCOUNT")
        ]

        for i, (name, label_key) in enumerate(account_combos):
            label_widget = QtWidgets.QLabel(self.language_manager.translate( label_key))
            combo = QtWidgets.QComboBox()
            combo.setObjectName(name)
            combo.setEnabled(False)
            select_btn = QtWidgets.QPushButton(self.language_manager.translate( "INVOICE_SETTINGS_SELECT"))
            select_btn.setObjectName(f"{name}_select_btn")
            select_btn.clicked.connect(lambda checked, cb=combo: self.openSelectAccountWindow(cb))
            default_accounts_layout.addWidget(label_widget, i, 0)
            default_accounts_layout.addWidget(combo, i, 1)
            default_accounts_layout.addWidget(select_btn, i, 2)
            self.fetchAccounts(combo)
            setattr(self.ui, name, combo)
            
            # Set value from database
            setting_name = name.replace('_combobox', '')
            value = self.database_operations.fetchSetting(setting_name)
            if value:
                combo.setCurrentIndex(combo.findData(value))

        h_spacer = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        default_accounts_layout.addItem(h_spacer, 0, 2)

        # Add checkboxes to effects group
        checkboxes = [
            (f"{prefix}{tab_name}_affects_materials_gain_loss_checkbox", "INVOICE_SETTINGS_AFFECTS_MATERIALS_GAIN_LOSS", 0, 0),
            (f"{prefix}{tab_name}_affects_client_price_checkbox", "INVOICE_SETTINGS_AFFECTS_CLIENT_PRICE", 0, 1),
            (f"{prefix}{tab_name}_discounts_affects_cost_price_checkbox", "INVOICE_SETTINGS_DISCOUNTS_AFFECTS_COST_PRICE", 0, 2),
            (f"{prefix}{tab_name}_discounts_affects_gain_checkbox", "INVOICE_SETTINGS_DISCOUNTS_AFFECTS_GAIN", 1, 0),
            (f"{prefix}{tab_name}_affects_last_buy_price_checkbox", "INVOICE_SETTINGS_AFFECTS_LAST_BUY_PRICE", 1, 1),
            (f"{prefix}{tab_name}_additions_affects_cost_price_checkbox", "INVOICE_SETTINGS_ADDITIONS_AFFECTS_COST_PRICE", 1, 2),
            (f"{prefix}{tab_name}_additions_affects_gain_checkbox", "INVOICE_SETTINGS_ADDITIONS_AFFECTS_GAIN", 2, 0),
            (f"{prefix}{tab_name}_affects_cost_price_checkbox", "INVOICE_SETTINGS_AFFECTS_COST_PRICE", 2, 1)
        ]

        disabled_checkboxes = {
            'sell_return': [
                'sell_return_discounts_affects_cost_price_checkbox',
                'sell_return_additions_affects_cost_price_checkbox'
            ],
            'buy': [],
            'input': [
                'input_affects_materials_gain_loss_checkbox',
                'input_additions_affects_gain_checkbox',
                'input_discounts_affects_gain_checkbox',
                'input_discounts_affects_cost_price_checkbox',
                'input_additions_affects_cost_price_checkbox'
            ],
            'output': [
                'output_discounts_affects_cost_price_checkbox',
                'output_additions_affects_cost_price_checkbox'
            ],
            'sell': [
                'sell_affects_materials_gain_loss_checkbox',
                'sell_additions_affects_gain_checkbox',
                'sell_discounts_affects_gain_checkbox',
                'sell_discounts_affects_cost_price_checkbox',
                'sell_additions_affects_cost_price_checkbox'
            ],
            'buy_return': [
                'buy_return_discounts_affects_gain_checkbox',
                'buy_return_affects_materials_gain_loss_checkbox',
                'buy_return_additions_affects_gain_checkbox',
            ]
        }

        for name, text_key, row, col in checkboxes:
            checkbox = QtWidgets.QCheckBox(self.language_manager.translate( text_key))
            checkbox.setObjectName(name)
            effects_layout.addWidget(checkbox, row, col)
            setattr(self.ui, name, checkbox)
            
            # Set value from database
            setting_name = name.replace('_checkbox', '')
            value = self.database_operations.fetchSetting(setting_name)

            if value:
                if int(value) == 1:
                    checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)

        # Add affects on warehouse combobox
        affects_warehouse_label = QtWidgets.QLabel(self.language_manager.translate( "INVOICE_SETTINGS_AFFECTS_WAREHOUSE"))
        affects_warehouse_combobox = QtWidgets.QComboBox()
        affects_warehouse_combobox.setObjectName(f"{prefix}{tab_name}_affects_on_warehouse_combobox")
        affects_warehouse_combobox.addItem(self.language_manager.translate( "INVOICE_SETTINGS_NONE"), None)
        for value in [self.language_manager.translate( "INVOICE_TYPE_REDUCE"), self.language_manager.translate( "INVOICE_TYPE_ADD")]:
            affects_warehouse_combobox.addItem(value, value)
            
        # Add returned checkbox
        returned_checkbox = QtWidgets.QCheckBox(self.language_manager.translate("INVOICE_SETTINGS_RETURNED"))
        returned_checkbox.setObjectName(f"{prefix}{tab_name}_returned_checkbox")
        
        # Set value from database - check if this invoice type is marked as returned
        invoice_type = self.database_operations.fetchInvoiceTypes(name=tab_name)
        if invoice_type:
            if invoice_type[0]['returned'] == 1:
                returned_checkbox.setChecked(True)
            else:
                returned_checkbox.setChecked(False)
        
        setattr(self.ui, f"{prefix}{tab_name}_returned_checkbox", returned_checkbox)
        
        # Add returned_checkbox to effects_layout
        effects_layout.addWidget(returned_checkbox, 3, 0)
        
        # Set value from databases
        warehouse_effect = self.database_operations.fetchSetting(f"{prefix}{tab_name}_affects_on_warehouse")
        if warehouse_effect:
            affects_warehouse_combobox.setCurrentIndex(affects_warehouse_combobox.findData(warehouse_effect))
            
        effects_layout.addWidget(affects_warehouse_label, 2, 2)
        effects_layout.addWidget(affects_warehouse_combobox, 2, 3)
        
        setattr(self.ui, f"{prefix}{tab_name}_affects_on_warehouse_combobox", affects_warehouse_combobox)

        # Create main layout and add all widgets/layouts
        main_layout = QtWidgets.QVBoxLayout(new_tab)
        top_layout = QtWidgets.QHBoxLayout()
        top_layout.addWidget(default_values_group)
        top_layout.addWidget(default_accounts_group)
        main_layout.addLayout(top_layout)
        main_layout.addWidget(effects_group)


        if is_custom:
            h_spacer = QtWidgets.QSpacerItem(625, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
            delete_btn = QtWidgets.QPushButton(self.language_manager.translate( "INVOICE_SETTINGS_DELETE_TYPE"))
            delete_btn.setObjectName("delete_type_btn")
            delete_btn.setMaximumWidth(100)
            delete_btn.clicked.connect(lambda: self.removeInvoiceType())
            setattr(self.ui, f"{prefix}{tab_name}_delete_type_btn", delete_btn)
            
            bottom_layout = QtWidgets.QHBoxLayout()
            bottom_layout.addItem(h_spacer)
            bottom_layout.addWidget(delete_btn)
            main_layout.addLayout(bottom_layout)

        # Add the new tab
        self.ui.tabWidget.addTab(new_tab, tab_name)
    def addNewInvoiceType(self, index):
        # Only handle the "+" tab click
        if index == self.ui.tabWidget.count() - 1:
            # Remove the "+" tab temporarily
            self.ui.tabWidget.removeTab(index)
            
            # Show dialog to get tab name and type
            dialog = QtWidgets.QDialog(self.ui.tabWidget)
            dialog.setLayoutDirection(QtCore.Qt.RightToLeft)
            dialog.setWindowTitle(self.language_manager.translate( "INVOICE_SETTINGS_ADD_TAB"))
            layout = QtWidgets.QFormLayout()
            
            name_input = QtWidgets.QLineEdit()
            type_combobox = QtWidgets.QComboBox()
            type_combobox.addItems(["input", "output"])
            
            # Add returned checkbox
            returned_checkbox = QtWidgets.QCheckBox()
            
            layout.addRow(self.language_manager.translate( "INVOICE_SETTINGS_TAB_NAME"), name_input)
            layout.addRow(self.language_manager.translate( "INVOICE_SETTINGS_TAB_TYPE"), type_combobox)
            layout.addRow(self.language_manager.translate( "INVOICE_SETTINGS_RETURNED"), returned_checkbox)
            
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel
            )
            buttons = QtWidgets.QDialogButtonBox()
            buttons.addButton(self.language_manager.translate( "INVOICE_SETTINGS_CANCEL"), QtWidgets.QDialogButtonBox.RejectRole)
            buttons.addButton(self.language_manager.translate( "INVOICE_SETTINGS_SAVE"), QtWidgets.QDialogButtonBox.AcceptRole)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            
            layout.addWidget(buttons)
            dialog.setLayout(layout)
            
            ok = dialog.exec_()
            tab_name = name_input.text()
            type_col = type_combobox.currentText()
            returned = 1 if returned_checkbox.isChecked() else 0
            
            if ok and tab_name and type_col:
                # Validate tab name
                invalid_chars = r'[^a-zA-Z0-9_\u0600-\u06FF\s]'  # Allow alphanumeric, underscore, Arabic and spaces
                tab_name = re.sub(invalid_chars, '', tab_name)
                
                # List of common SQL reserved words to check against
                sql_reserved = ['select', 'insert', 'delete', 'update', 'drop', 'create', 'alter', 
                              'table', 'from', 'where', 'and', 'or', 'null', 'not', 'default']

                # Get all existing invoice type names from fetchInvoiceTypes
                invoice_types = self.database_operations.fetchInvoiceTypes()
                existing_names = [invoice_type['name'] for invoice_type in invoice_types]
                
                if (len(tab_name) > 142 or 
                    len(tab_name.strip()) == 0 or
                    tab_name.lower() in sql_reserved or
                    tab_name in existing_names):
                    QtWidgets.QMessageBox.warning(
                        self.ui.tabWidget,
                        self.language_manager.translate( "INVOICE_SETTINGS_WARNING"),
                        self.language_manager.translate( "INVOICE_SETTINGS_NAME_ERROR")
                    )
                else:
                    # Pass the returned value to addInvoiceType
                    self.database_operations.addInvoiceType(tab_name, type_col, returned)
                    self.fetchInvoicesTypes()
            # Add back the "+" tab
            self.ui.tabWidget.addTab(QtWidgets.QWidget(), "+")
    
    def fetchAccounts(self, combobox=None):
        accounts = self.database_operations.fetchAccounts()
        result = [(self.language_manager.translate("NONE"), None)]
        for account in accounts:
            id = account[0]
            name = account[1] 
            result.append((name, id))
        if combobox is not None:
            for name, id in result:
                combobox.addItem(name, id)
        return result

    def fetchPrices(self, combobox=None):
        prices = self.database_operations.fetchPrices()
        result = [(self.language_manager.translate("NONE"), None)]
        for price in prices:
            id = price[0]
            name = price[1]
            result.append((name, id))
        if combobox is not None:
            for name, id in result:
                combobox.addItem(name, id)
        return result

    def fetchWarehouses(self, combobox=None):
        warehouses = self.database_operations.fetchWarehouses()
        result = [(self.language_manager.translate("NONE"), None)]
        for warehouse in warehouses:
            id = warehouse[0]
            name = warehouse[1]
            result.append((name, id))
        if combobox is not None:
            for name, id in result:
                combobox.addItem(name, id)
        return result

    def fetchCurrencies(self, combobox=None):
        currencies = self.database_operations.fetchCurrencies()
        result = [(self.language_manager.translate("NONE"), None)]
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            result.append((name, id))
        if combobox is not None:
            for name, id in result:
                combobox.addItem(name, id)
        return result

    def fetchCostCenters(self, combobox=None):
        cost_centers = self.database_operations.fetchCostCenters()
        result = [(self.language_manager.translate("NONE"), None)]
        for cost_center in cost_centers:
            id = cost_center[0]
            name = cost_center[1]
            result.append((name, id))
        if combobox is not None:
            for name, id in result:
                combobox.addItem(name, id)
        return result

    def fetchInvoicesSettings(self):
        for invoice_setting in self.invoices_settings:
            value = self.database_operations.fetchSetting(invoice_setting)

            accounts_comboboxes = [ui_element_name for ui_element_name in self.accounts_comboboxes if
                                   invoice_setting in ui_element_name]
            prices_comboboxes = [ui_element_name for ui_element_name in self.prices_comboboxes if
                                 invoice_setting in ui_element_name]
            warehouses_comboboxes = [ui_element_name for ui_element_name in self.warehouses_comboboxes if
                                     invoice_setting in ui_element_name]
            cost_centers_combobxes = [ui_element_name for ui_element_name in self.cost_centers_comboboxes if
                                      invoice_setting in ui_element_name]
            currencies_comboboxes = [ui_element_name for ui_element_name in self.currencies_comboboxes if
                                     invoice_setting in ui_element_name]
            affects_on_warehouse_comboboxes = [ui_element_name for ui_element_name in self.affects_on_warehouse_comboboxes if
                                                invoice_setting in ui_element_name]
            checkbox = [ui_element_name for ui_element_name in self.ui_checkboxes if invoice_setting in ui_element_name]

            if len(accounts_comboboxes) > 0:
                target_ui_element = accounts_comboboxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))

            if len(prices_comboboxes) > 0:
                target_ui_element = prices_comboboxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))

            if len(warehouses_comboboxes) > 0:
                target_ui_element = warehouses_comboboxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))

            if len(cost_centers_combobxes) > 0:
                target_ui_element = cost_centers_combobxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))

            if len(currencies_comboboxes) > 0:
                target_ui_element = currencies_comboboxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))
                    
            if len(affects_on_warehouse_comboboxes) > 0:
                target_ui_element = affects_on_warehouse_comboboxes[0]
                if value:
                    self.ui.__getattribute__(target_ui_element).setCurrentIndex(
                        self.ui.__getattribute__(target_ui_element).findData(value))

            elif len(checkbox) > 0:
                target_ui_element = checkbox[0]
                if value:
                    if int(value) == 1:
                        self.ui.__getattribute__(target_ui_element).setChecked(True)
                else:
                    self.ui.__getattribute__(target_ui_element).setChecked(False)
    
    def fetchCustomInvoicesTypesSettings(self, typename):
        # Get all UI elements for this tab
        tab_accounts = [ui_element for ui_element in self.accounts_comboboxes 
                      if f"custom_invoice_type_{typename}_" in ui_element]
        tab_prices = [ui_element for ui_element in self.prices_comboboxes 
                     if f"custom_invoice_type_{typename}_" in ui_element]
        tab_warehouses = [ui_element for ui_element in self.warehouses_comboboxes 
                        if f"custom_invoice_type_{typename}_" in ui_element]
        tab_cost_centers = [ui_element for ui_element in self.cost_centers_comboboxes 
                          if f"custom_invoice_type_{typename}_" in ui_element]
        tab_currencies = [ui_element for ui_element in self.currencies_comboboxes 
                        if f"custom_invoice_type_{typename}_" in ui_element]
        tab_affects_on_warehouse = [ui_element for ui_element in self.affects_on_warehouse_comboboxes 
                                  if f"custom_invoice_type_{typename}_" in ui_element]
        tab_checkboxes = [ui_element for ui_element in self.ui_checkboxes 
                        if f"custom_invoice_type_{typename}_" in ui_element]
        
        # For each UI element, get its setting value from DB
        for ui_element in (tab_accounts + tab_prices + tab_warehouses + 
                         tab_cost_centers + tab_currencies + tab_affects_on_warehouse + tab_checkboxes):
            # Convert UI element name to setting name by removing _combobox/_checkbox suffix
            setting_name = ui_element.replace('_combobox', '').replace('_checkbox', '')
            
            # Get setting value from DB
            value = self.database_operations.fetchSetting(setting_name)
            
            if ui_element in tab_checkboxes:
                # Handle checkbox
                if value:
                    if int(value) == 1:
                        self.ui.__getattribute__(ui_element).setChecked(True)
                    else:
                        self.ui.__getattribute__(ui_element).setChecked(False)
            else:
                # Handle combobox
                if value:
                    self.ui.__getattribute__(ui_element).setCurrentIndex(
                        self.ui.__getattribute__(ui_element).findData(value))
    
    def fetchCustomInvoicesTypesNames(self):
        # Fetch all settings that start with custom_invoice_type
        settings = self.database_operations.fetchSettings('custom_invoice_type')
        
        # Set to store unique type names
        type_names = set()
        
        # Extract type names from settings
        for setting in settings:
            setting_name = setting[0]  # Get the setting name
            # Split by underscore and get the type name (4th element)
            parts = setting_name.split('_')
            if len(parts) > 4 and parts[0] == 'custom' and parts[1] == 'invoice' and parts[2] == 'type':
                type_name = parts[3]
                type_names.add(type_name)
                
        # Convert set to list and return
        return list(type_names)
        
    def saveInvoicesSettings(self, window):
        # Check if material account is selected for each invoice type
        for i in range(self.ui.tabWidget.count() - 1):  # -1 to exclude the "+" tab
            tab_name = self.ui.tabWidget.tabText(i)
            prefix = "custom_invoice_type_" if tab_name not in ['sell', 'sell_return', 'buy', 'buy_return', 'input', 'output'] else ""
            materials_account_combobox = f"{prefix}{tab_name}_materials_account_combobox"
            
            if hasattr(self.ui, materials_account_combobox):
                materials_account = self.ui.__getattribute__(materials_account_combobox).currentData()
                if materials_account is None:
                    QtWidgets.QMessageBox.warning(
                        window,
                        self.language_manager.translate("INVOICE_SETTINGS_MATERIALS_ACCOUNT_REQUIRED"),
                        self.language_manager.translate("INVOICE_SETTINGS_MATERIALS_ACCOUNT_REQUIRED_MESSAGE")
                    )
                    return
        ui_elements = self.prices_comboboxes + self.accounts_comboboxes + self.warehouses_comboboxes + self.cost_centers_comboboxes + self.currencies_comboboxes + self.affects_on_warehouse_comboboxes + self.ui_checkboxes
        
        for ui_element in ui_elements:
            # Convert UI element name to setting name by removing _combobox/_checkbox suffix
            setting_name = ui_element.replace('_combobox', '').replace('_checkbox', '')
            
            if ui_element in self.ui_checkboxes:
                value = 1 if self.ui.__getattribute__(ui_element).isChecked() else 0
            else:
                value = self.ui.__getattribute__(ui_element).currentData()
                
            self.database_operations.saveSetting(setting_name, value)

        window.accept()


    def removeInvoiceType(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate( "INVOICE_SETTINGS_DELETE_CONFIRM"), self.language_manager.translate( "INVOICE_SETTINGS_WARNING"), MB_YESNO)
        if messagebox_result == IDYES:
            # Get the currently selected tab index
            current_index = self.ui.tabWidget.currentIndex()
            
            # Get the tab name from the current index
            tab_name = self.ui.tabWidget.tabText(current_index)
            
            self.database_operations.removeInvoiceType(tab_name)
            
            # Remove the tab
            self.ui.tabWidget.removeTab(current_index)
