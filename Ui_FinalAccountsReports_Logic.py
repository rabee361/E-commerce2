from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QTableWidgetItem, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from PyQt5.QtCore import QCoreApplication , QTranslator
import win32api
import win32con
from Colors import orange, colorizeTableRow, light_red_color, light_green_color, black
from DatabaseOperations import DatabaseOperations
from Ui_FinalAccountsReports import Ui_FinalAccountsReports
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon

class Ui_FinalAccountsReports_Logic(QDialog):
    def __init__(self, sql_connector, target_account=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_FinalAccountsReports()
        self.target_account = target_account

        # Save selected invoices
        self.selected_invoices = {}
        self.include_invoices_payments = True
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/report2.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchCurrencies()
        self.setPricingMethods()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.accounts_combobox.setDisabled(True)
        self.ui.to_date_input.setDate(QDate.currentDate())
        self.ui.distinct_currency_radio.clicked.connect(self.updatePricingMethodComboboxOptionsBasedOnCurrencyRadios)
        self.ui.unified_currency_radio.clicked.connect(self.updatePricingMethodComboboxOptionsBasedOnCurrencyRadios)
        self.updatePricingMethodComboboxOptionsBasedOnCurrencyRadios()

        if self.target_account:
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(self.target_account))
            self.calculate()

        self.fetchInvoiceTypes()
        self.ui.select_invoices_btn.clicked.connect(lambda: self.openSelectInvoicesWindow())
    
    def fetchInvoiceTypes(self):
        invoice_types = self.database_operations.fetchInvoiceTypes()
        for invoice_type in invoice_types:
            self.selected_invoices[invoice_type['name']] = True

    def openSelectInvoicesWindow(self):
        # Create dialog to select invoice types
        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setWindowTitle(self.language_manager.translate("SELECT_INVOICES"))
        dialog.setFixedWidth(300)
        dialog.setModal(True)
        
        # Get invoice types from database
        invoice_types = self.database_operations.fetchInvoiceTypes()
        
        # Create checkboxes dynamically based on invoice types
        checkboxes = []
        layout = QVBoxLayout()
        
        # Create grid layout for checkboxes
        grid_layout = QGridLayout()
        row = 0
        col = 0
        for i, invoice_type in enumerate(invoice_types):
            invoice_type_name = invoice_type['name']
            checkbox = QCheckBox(invoice_type_name)
            checkbox.setChecked(True)
            if self.selected_invoices:
                if not invoice_type_name in self.selected_invoices.keys():
                    checkbox.setChecked(False)
            grid_layout.addWidget(checkbox, row, col)
            checkboxes.append(checkbox)
            col += 1
            if col == 3:  # After 3 columns, move to next row
                col = 0
                row += 1
        
        # Add grid layout to main layout
        layout.addLayout(grid_layout)

        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Add checkbox below separator
        include_payments_checkbox = QCheckBox(self.language_manager.translate("INCLUDE_INVOICES_PAYMENTS"))
        include_payments_checkbox.setChecked(True if self.include_invoices_payments else False)
        layout.addWidget(include_payments_checkbox)
            
        # Add OK button
        ok_button = QPushButton(self.language_manager.translate("OK"))
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        
        dialog.setLayout(layout)
        
        # Show dialog and get result
        if dialog.exec_() == QDialog.Accepted:
            # Clear previous selections
            self.selected_invoices = {}
            
            # Add checked invoice types to selected_invoices
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    self.selected_invoices[checkbox.text()] = True
                
            if include_payments_checkbox.isChecked():
                self.include_invoices_payments = True
            else:
                self.include_invoices_payments = False


    def openSelectAccountWindow(self):
        # Create a list of excluded accounts
        excluded_accounts_type = 'normal'
        excluded_accounts = self.database_operations.fetchAccounts(type=excluded_accounts_type)
        excluded_accounts_ids = [account[0] for account in excluded_accounts]   # List contains ids only

        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True,
                                          exclusions=excluded_accounts_ids)
        result = data_picker.showUi()
        if result is not None:
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(result['id']))

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts(type="final")
        for account in accounts:
            id = account[0]
            name = account[1]
            self.ui.accounts_combobox.addItem(str(name), id)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            self.ui.currency_combobox.addItem(name, id)

    def setPricingMethods(self):
        pricing_methods = {
            self.language_manager.translate("MEDIAN"): "median",
            self.language_manager.translate("MAX_PRICE"): "max_price",
            self.language_manager.translate("LAST_BUY"): "last_buy",
            self.language_manager.translate("LAST_BUY_WITH_DISCOUNTS_AND_ADDITIONS"): "last_buy_with_discounts_and_additions",
            self.language_manager.translate("REAL_PRICE"): "real",
        }
        for key, value in pricing_methods.items():
            self.ui.pricing_method_combobox.addItem(key, value)

    def updatePricingMethodComboboxOptionsBasedOnCurrencyRadios(self):
        distinct_currency_checked = self.ui.distinct_currency_radio.isChecked()
        unified_currency_checked = self.ui.unified_currency_radio.isChecked()
        selected_pricing_method = self.ui.pricing_method_combobox.currentData()

        disable_options = []

        if unified_currency_checked:
            disable_options.append("real")
            if selected_pricing_method=="real":
                self.ui.pricing_method_combobox.setCurrentIndex(self.ui.pricing_method_combobox.findData("median"))
        elif distinct_currency_checked:
            disable_options.append("median")
            if selected_pricing_method=="median":
                self.ui.pricing_method_combobox.setCurrentIndex(self.ui.pricing_method_combobox.findData("real"))

        for index in range(self.ui.pricing_method_combobox.count()):
            item_data = self.ui.pricing_method_combobox.itemData(index)
            if item_data in disable_options:
                self.ui.pricing_method_combobox.model().item(index).setEnabled(False)
            else:
                self.ui.pricing_method_combobox.model().item(index).setEnabled(True)

    def calculate(self):
        self.ui.result_tree.clear()
        self.ui.summerized_result_table.setRowCount(0)
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)
        targeted_account = self.ui.accounts_combobox.currentData()

        if targeted_account is None:
            win32api.MessageBox(0, self.language_manager.translate("ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"), win32con.MB_OK)
            return

        exchange_date = self.ui.exchange_date_input.date().toString(Qt.ISODate)
        distinct_currency = self.ui.distinct_currency_radio.isChecked()
        unified_currency = self.ui.unified_currency_radio.isChecked()
        unified_exchange_date = self.ui.unified_exchange_date_radio.isChecked()
        targeted_currency = self.ui.currency_combobox.currentData()
        targeted_currency_name = self.ui.currency_combobox.currentText()
        distinct_exchange_date = self.ui.distinct_exchange_date_radio.isChecked()

        data_sources = []

        # Updated checkbox names
        checkbox_names = ["source_period_start_checkbox", "source_period_start_material_checkbox",
                          "source_journal_checkbox"]

        for checkbox_name in checkbox_names:
            checkbox = getattr(self.ui, checkbox_name)
            if checkbox.isChecked():
                # Extract the relevant part of the checkbox name
                extracted_name = checkbox_name.replace("source_", "").replace("_checkbox", "")
                data_sources.append(extracted_name)

        for key, value in self.selected_invoices.items():
            if value:
                data_sources.append('invoice_' + key)

        if self.include_invoices_payments:
            data_sources.append('invoice_payment')
            data_sources.append('extra_payment')

        if self.ui.source_manufacture_checkbox.isChecked():
            data_sources.append('manufacture')
            
        if self.ui.source_loans_checkbox.isChecked():
            data_sources.append('loan_payment')
            data_sources.append('loan')

        result_accounts_dict = self.calculateLogic(from_date, to_date, targeted_account, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

        def populate_trees(nested_dict):
            def safeFloat(value, percise=50):
                try:
                    return round(float(value),percise)
                except (ValueError, TypeError) as e:
                    return 0

            def addAccount(account_data, values, parent):
                account_item = QTreeWidgetItem(parent)
                account_id = account_data[0]
                account_name = account_data[1]
                if 'value' in values:
                    value = safeFloat(values['value'], percise=5)
                if 'value' in values and 'state' in values:
                    if values['state'] == 'debtor':
                        account_item.setText(2, str(account_id))
                        account_item.setText(3, str(account_name))
                        account_item.setText(4, str(value))
                        account_item.setBackground(2, orange)
                        account_item.setBackground(3, orange)
                        account_item.setBackground(4, orange)
                    elif values['state'] == 'creditor':
                        account_item.setText(5, str(account_id))
                        account_item.setText(6, str(account_name))
                        account_item.setText(7, str(value))
                        account_item.setBackground(5, orange)
                        account_item.setBackground(6, orange)
                        account_item.setBackground(7, orange)
                for key in values:
                    if isinstance(key, tuple):
                        addAccount(key, values[key], account_item)
                    elif key=='entry':
                        d2 = values[key].items()
                        for k2, v2 in d2:
                            if k2 not in ('state', 'value'):
                                for v3 in v2:
                                    warehouse_item=QTreeWidgetItem(account_item)
                                    # journal_entry_item_id, journal_entry_id, account_id, statement, currency, opposite_account_id, journal_entry_type, value, cost_center_id, currency_name, account_name, opposite_account_name, journal_entry_date, journal_entry_origin_type, journal_entry_origin_id = journal_entry_item
                                    account_name = v3[10]
                                    opposite_account_name = v3[11]
                                    details=v3[3]
                                    v3value=v3[7]
                                    v3type = v3[6]
                                    info_string = f"{self.language_manager.translate('ACCOUNT')}: {account_name}-{self.language_manager.translate('OPPOSITE_ACCOUNT')}: {opposite_account_name}-{self.language_manager.translate('VALUE')}: {v3value}-{self.language_manager.translate('STATEMENT')}: {details}-{self.language_manager.translate('TYPE')}:{v3type}"
                                    warehouse_item.setText(8, info_string)

            for key, values in nested_dict.items():
                if isinstance(key, tuple):
                    # Currency row
                    currency_item = QTreeWidgetItem()
                    currency_id=key[0]
                    currency_name=key[1]

                    currency_item.setText(0, str(currency_id))  # Currency ID
                    currency_item.setText(1, str(currency_name))  # Currency Name

                    if ('value' in values )and ('state' in values):
                        value=safeFloat(values['value'],5)
                        if values['state']=='debtor':
                            currency_item.setBackground(2, orange)
                            currency_item.setBackground(3, orange)
                            currency_item.setBackground(4, orange)
                        elif values['state']=='creditor':
                            currency_item.setBackground(5, orange)
                            currency_item.setBackground(6, orange)
                            currency_item.setBackground(7, orange)
                    if 'credit' and 'debt' in values:
                        # Create a empty row at bottom of table
                        numRows = self.ui.summerized_result_table.rowCount()
                        self.ui.summerized_result_table.insertRow(numRows)
                        # Add text to the row
                        debt=safeFloat(values['debt'], 5)
                        credit=safeFloat(values['credit'], 5)
                        different = credit - debt
                        self.ui.summerized_result_table.setItem(numRows, 0, QTableWidgetItem(str(currency_id)))
                        self.ui.summerized_result_table.setItem(numRows, 1, QTableWidgetItem(str(currency_name)))
                        self.ui.summerized_result_table.setItem(numRows, 2, QTableWidgetItem(str(debt)))
                        self.ui.summerized_result_table.setItem(numRows, 3, QTableWidgetItem(str(credit)))
                        self.ui.summerized_result_table.setItem(numRows, 4, QTableWidgetItem(str(different)))
                        if different==0:
                            colorizeTableRow(self.ui.summerized_result_table, numRows, background_color=light_green_color, text_color=black)
                        if different<0:
                            colorizeTableRow(self.ui.summerized_result_table, numRows, background_color=light_red_color, text_color=black)


                    self.ui.result_tree.addTopLevelItem(currency_item)

                for key in values:
                    if isinstance(key, tuple):
                        addAccount(key, values[key], currency_item)

        populate_trees(result_accounts_dict)

    def calculateLogic(self, from_date, to_date, targeted_account, targeted_currency,
                       unified_currency, targeted_currency_name, unified_exchange_date, exchange_date,
                       distinct_currency, data_sources):
        account_info = self.database_operations.fetchAccount(targeted_account)
        if account_info:
            pass
        else:
            return

        debtors = {}
        creditors = {}

        # Function to find the account location and return its path
        def findAccountLocation(currency_dict, account_id, path=None):
            #return list of keys that can be used to access the value of account_id again
            if path is None:
                path = []

            for key, value in currency_dict.items():
                if key == account_id:
                    return path + [key]

                if isinstance(value, dict):
                    found_in_sub_dict = findAccountLocation(value, account_id, path + [key])
                    if found_in_sub_dict:
                        return found_in_sub_dict

            return None

        def addItemToResutlDict(result_dict, item:list):

            journal_entry_item_id, journal_entry_id, account_id, statement, currency, opposite_account_id, type, value, cost_center_id, currency_name, account_name, opposite_account_name, entry_date, origin_type, origin_id, *extra_values = item

            account_data = (account_id, account_name)
            #first, check if account is already in result tree
            location_path = findAccountLocation(result_dict, account_data)
            if location_path:
                partial_result_dict = result_dict #partian_result_dict is just a refernece (shallow-copy)
                for key in location_path:
                    partial_result_dict = partial_result_dict[key]
                entry_value = partial_result_dict.get('entry', {}) #shallow copy (lists)
                if journal_entry_id not in entry_value:
                    entry_value[journal_entry_id] = [item]
                else:
                    entry_value[journal_entry_id].append(item)
                partial_result_dict['entry'] = entry_value

            else:
                #check if any of account's ancestors is in the tree
                ancestors = self.database_operations.fetchAccountAncestors(account_id) #returned ancestors are sorted from closer one (father) to further ones
                for ancestor in ancestors:
                    location_path = findAccountLocation(result_dict, ancestor[0])
                    if location_path:
                        partial_result_dict=result_dict #shallow copy
                        for key in location_path:
                            partial_result_dict = partial_result_dict[key]

                        if account_data not in partial_result_dict:
                            partial_result_dict[account_data]={}
                        if 'entry' not in partial_result_dict[account_data]:
                            partial_result_dict[account_data]['entry']={}
                        if journal_entry_id not in partial_result_dict[account_data]['entry']:
                            partial_result_dict[account_data]['entry'][journal_entry_id]=[item]
                        else:
                            partial_result_dict[account_data]['entry'][journal_entry_id].append(item)
                        break #stop when the closest ancestor is already found
                else: #for-else
                    currency_data = (currency, currency_name)
                    if currency_data not in result_dict:
                        result_dict[currency_data] = {}
                    # Check if account_id exists in result_dict[currency]
                    if account_data not in result_dict[currency_data]:
                        result_dict[currency_data][account_data] = {}
                    if 'entry' not in result_dict[currency_data][account_data]:
                        result_dict[currency_data][account_data]['entry']={}
                    # Check if journal_entry_id exists in result_dict[currency][account_id]
                    if journal_entry_id not in result_dict[currency_data][account_data]['entry']:
                        result_dict[currency_data][account_data]['entry'][journal_entry_id] = []
                    # Check if journal_entry_item_id exists in result_dict[currency][account_id][journal_entry_id]
                    for jei in result_dict[currency_data][account_data]['entry'][journal_entry_id]:
                        if jei[0]==item[0]:
                            break
                    else:
                        result_dict[currency_data][account_data]['entry'][journal_entry_id].append(item)

                #check if any children of the added account are already in the tree, and move them under the added account
                descendants = self.database_operations.fetchAccountDescendants(account_id)
                descendants = [inner_list[0] for inner_list in descendants]

                location_path=findAccountLocation(result_dict, account_data)
                partial_result_dict=result_dict
                for key in location_path[:-1]:
                    partial_result_dict=partial_result_dict[key]
                for key, value in partial_result_dict.items():
                    if key in descendants:
                        partial_result_dict[account_data][key]=value
                        partial_result_dict.pop(key)

        def mergeDicts(dict1, dict2):
            """Merges two nested dicts with debt/credit values, ensuring both keys are present.

            Args:
                dict1: The first dict to merge (remains unmodified).
                dict2: The second dict to merge (remains unmodified).

            Returns:
                A new dict containing the merged result.
            """

            def addZeroKeys(data):
                if isinstance(data, dict):
                    if 'debt' in data and 'credit' not in data:
                        data['credit'] = 0
                    elif 'credit' in data and 'debt' not in data:
                        data['debt'] = 0

                    for key, value in data.items():
                        data[key] = addZeroKeys(value)
                elif isinstance(data, list):
                    data = [addZeroKeys(item) for item in data]

                return data

            def mergeRecursively(base_dict, merge_dict, path=None):
                """Recursively merges nested dicts, creating new dictionaries as needed."""
                if path is None:
                    path = []

                new_base_dict = base_dict.copy()  # Create a copy of the base dict at each level

                for key, value in merge_dict.items():
                    full_path = path + [key]
                    if key in new_base_dict:
                        if isinstance(value, dict) and isinstance(new_base_dict[key], dict):
                            new_base_dict[key] = mergeRecursively(new_base_dict[key], value,
                                                                   full_path)  # Corrected line
                        else:
                            new_base_dict[key] = value
                    else:
                        if isinstance(value, dict):
                            new_base_dict[key] = mergeRecursively(value, {}, full_path)  # Added line
                        else:
                            new_base_dict[key] = value
                addZeroKeys(new_base_dict)
                return new_base_dict

            # Perform the main merge, creating a new dictionary
            merged_dict = mergeRecursively(dict1.copy(), dict2.copy())
            return merged_dict

        def buildRecordsList(from_date, to_date, targeted_account, targeted_currency,
                       unified_currency, targeted_currency_name, unified_exchange_date, exchange_date,
                       distinct_currency, data_sources):
            records=[]
            # process journal entries (current account)
            journal_entry_items_direct = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, account=targeted_account, sources=data_sources)
            journal_entry_items_opposite = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, opposite_account=targeted_account, sources=data_sources)

            journal_entry_items = journal_entry_items_direct + journal_entry_items_opposite

            for journal_entry_item in journal_entry_items:
                journal_entry_item_id = journal_entry_item['id']
                journal_entry_id = journal_entry_item['journal_entry_id']
                account_id = journal_entry_item['account_id']
                statement = journal_entry_item['statement_col']
                currency = journal_entry_item['currency']
                opposite_account_id = journal_entry_item['opposite_account_id']
                journal_entry_type = journal_entry_item['type_col']
                value = journal_entry_item['value_col']
                cost_center_id = journal_entry_item['cost_center_id']
                currency_name = journal_entry_item['currency_name']
                account_name = journal_entry_item['account_name']
                opposite_account_name = journal_entry_item['opposite_account_name']
                journal_entry_date = journal_entry_item['entry_date']
                journal_entry_origin_type = journal_entry_item['origin_type']
                journal_entry_origin_id = journal_entry_item['origin_id']

                if unified_currency:
                    journal_entry_item[4] = targeted_currency
                    journal_entry_item[9] = targeted_currency_name
                    if currency == targeted_currency:
                        #value = value
                        pass
                    else:
                        if unified_exchange_date:
                            exchange_value = self.database_operations.fetchExchangeValue(
                                currency,
                                targeted_currency,
                                exchange_date)
                        else:
                            exchange_value = self.database_operations.fetchExchangeValue(
                                currency,
                                targeted_currency,
                                journal_entry_date)

                        if exchange_value:
                            value = value * float(exchange_value[0][1])
                            journal_entry_item['value_col']=value
                        else:
                            print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                            break

                records.append(journal_entry_item)
                print(records)


            # Process accounts
            # get a list of accounts that use targeted account as their final account
            accounts = self.database_operations.fetchAccounts(final_account=targeted_account)
            for account in accounts:
                journal_entry_items_direct = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, account=account[0])
                journal_entry_items_opposite = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, opposite_account=account[0])

                journal_entry_items = journal_entry_items_direct + journal_entry_items_opposite
                
                for journal_entry_item in journal_entry_items:
                    journal_entry_item=list(journal_entry_item)
                    journal_entry_item_id, journal_entry_id, account_id, statement, currency, opposite_account_id, journal_entry_type, value, cost_center_id, currency_name, account_name, opposite_account_name, journal_entry_date, journal_entry_origin_type, journal_entry_origin_id, *extra_values = journal_entry_item

                    if unified_currency:
                        journal_entry_item[4]= targeted_currency
                        journal_entry_item[9]= targeted_currency_name
                        if currency == targeted_currency:
                            # value = value
                            pass
                        else:
                            if unified_exchange_date:
                                exchange_value = self.database_operations.fetchExchangeValue(
                                    currency,
                                    targeted_currency,
                                    exchange_date)
                            else:
                                exchange_value = self.database_operations.fetchExchangeValue(
                                    currency,
                                    targeted_currency,
                                    journal_entry_date)

                            if exchange_value:
                                value = value * float(exchange_value[0][1])
                                journal_entry_item[7] = value
                            else:
                                print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                                break



                    records.append(journal_entry_item)

            # process warehouses
            pricing_method = self.ui.pricing_method_combobox.currentData()
            # fetch warehouses accounts
            warehouses_data = {}
            # Get the warehouses that use an account that use the targeted account as its final account
            warehouses1 = self.database_operations.fetchWarehouses(final_account=targeted_account)
            # Get the accounts that use the targeted account as their account
            warehouses2 = self.database_operations.fetchWarehouses(account=targeted_account)
            # Merge the results but without having duplicates
            # warehouses = set(warehouses1).union(warehouses2)

            # warehouses1_tuples = [tuple(warehouse.items()) for warehouse in warehouses1]
            # warehouses2_tuples = [tuple(warehouse.items()) for warehouse in warehouses2]
            # warehouses = list(set(warehouses1_tuples).union(warehouses2_tuples))

            warehouses1_set = {tuple(warehouse.items()) for warehouse in warehouses1}
            warehouses2_set = {tuple(warehouse.items()) for warehouse in warehouses2}

            warehouses = set(warehouses1_set).union(warehouses2_set)
            warehouses = [dict(items) for items in warehouses]


            for warehouse in warehouses: 
                warehouse_id = warehouse[0]
                # warehouse_account = warehouse[5]
                # warehouse_name = warehouse[1]
                # warehouse_code = warehouse[2]
                # warehouse_parent_id = warehouse[3]
                # warehouse_parent_name = warehouse[4]
                # warehouse_codename = warehouse[6]

                # get materials from each warehouse

                materials_in_warehouse = self.database_operations.fetchWarehouseMaterials(warehouse_id)
                for material_in_warehouse in materials_in_warehouse:
                    warehouse_entry_id = material_in_warehouse[0]
                    material_id = material_in_warehouse[1]
                    quantity = material_in_warehouse[2]
                    unit = material_in_warehouse[3]
                    production_batch_id = material_in_warehouse[4]
                    invoice_item_id = material_in_warehouse[5]
                    code = material_in_warehouse[6]
                    material_name = material_in_warehouse[7]
                    unit_name = material_in_warehouse[8]

                    # get material's default unit
                    material_details = self.database_operations.fetchMaterial(material_id)
                    material_units = {1: material_details[12], 2: material_details[13], 3: material_details[14]}
                    default_unit = material_units[material_details[15]]

                    if unit != default_unit:
                        unit_conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit, default_unit)

                        if unit_conversion_rate:
                            quantity = quantity * unit_conversion_rate
                        else:
                            quantity = 0

                    estimated_price = 0
                    if pricing_method in ('median', 'max_price', 'last_buy', 'last_buy_with_discounts_and_additions'):
                        if unified_exchange_date:
                            exchange_date = exchange_date
                        else:
                            exchange_date = to_date

                        if pricing_method == 'median':
                            average_price = self.database_operations.fetchAverageMaterialPrice(material_id, targeted_currency, currency_exchage_date=exchange_date)
                            if average_price:
                                estimated_price = float(quantity) * float(average_price)

                        if pricing_method == 'max_price':
                            max_price = self.database_operations.fetchMaximumMaterialPrice(material_id, targeted_currency, currency_exchage_date=exchange_date)
                            if max_price:
                                estimated_price = float(quantity) * float(max_price)

                        if pricing_method == 'last_buy_with_discounts_and_additions':
                            last_price = self.database_operations.fetchLastInvoiceOfMaterialWithDiscountsAndAdditions(material_id, date=to_date)
                            if last_price:
                                unit1_id = last_price['unit1_id']
                                unit_price = last_price['unit_price']
                                payment_currency = last_price['payment_currency']
                                invoice_date = last_price['date_col']
                                # quantity1 = last_price[0]
                                # quantity2 = last_price[1]
                                # quantity3 = last_price[2]
                                # unit2_id = last_price[4]
                                # unit3_id = last_price[5]
                                # equilivance_price = last_price[7]
                                # invoice_currency = last_price[9]
                                # invoice_item_id = last_price[11]
                                # invoices_id = last_price[12]

                                material_details = self.database_operations.fetchMaterial(material_id)
                                material_units = {1: material_details[12], 2: material_details[13],
                                                  3: material_details[14]}
                                default_unit = material_units[material_details[15]]

                                if unit1_id == default_unit:
                                    pass
                                else:
                                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1_id,
                                                                                                               default_unit)
                                    quantity_in_default_unit = 1 * conversion_rate
                                    unit_price = float(unit_price) / float(quantity_in_default_unit)

                                if payment_currency == targeted_currency:
                                    last_price = unit_price
                                else:
                                    if unified_exchange_date:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            payment_currency,
                                            targeted_currency,
                                            exchange_date)
                                    else:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            payment_currency,
                                            targeted_currency,
                                            invoice_date)

                                    if exchange_value:
                                        last_price = unit_price * float(exchange_value[0][1])

                                    else:
                                        print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                                        pass

                                if last_price:
                                    estimated_price = float(quantity) * float(last_price)

                        if pricing_method == 'last_buy':
                            last_price = self.database_operations.fetchLastInvoiceOfMaterial(material_id, date=to_date)
                            if last_price:
                                unit1_id = last_price[3]
                                unit_price = last_price[6]
                                payment_currency = last_price[8]
                                invoice_date = last_price[10]
                                # quantity1 = last_price[0]
                                # quantity2 = last_price[1]
                                # quantity3 = last_price[2]
                                # unit2_id = last_price[4]
                                # unit3_id = last_price[5]
                                # equilivance_price = last_price[7]
                                # invoice_currency = last_price[9]
                                # invoice_item_id = last_price[11]
                                # invoices_id = last_price[12]

                                material_details = self.database_operations.fetchMaterial(material_id)
                                material_units = {1: material_details[12], 2: material_details[13],
                                                  3: material_details[14]}
                                default_unit = material_units[material_details[15]]

                                if unit1_id == default_unit:
                                    pass
                                else:
                                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1_id,
                                                                                                               default_unit)
                                    quantity_in_default_unit = 1 * conversion_rate
                                    unit_price = float(unit_price) / float(quantity_in_default_unit)

                                if payment_currency == targeted_currency:
                                    last_price = unit_price
                                else:
                                    if unified_exchange_date:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            payment_currency,
                                            targeted_currency,
                                            exchange_date)
                                    else:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            payment_currency,
                                            targeted_currency,
                                            invoice_date)

                                    if exchange_value:
                                        last_price = unit_price * float(exchange_value[0][1])

                                    else:
                                        print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                                        pass

                                if last_price:
                                    estimated_price = float(quantity) * float(last_price)

                    elif pricing_method == 'real':
                        item_price=0
                        if invoice_item_id:
                            invoice_item_data = self.database_operations.fetchInvoiceItem(invoice_item_id)
                            unit_price = invoice_item_data['unit_price']
                            unit1_id = invoice_item_data['unit1_id']
                            currency_id = invoice_item_data['currency_id']
                            currency_name = invoice_item_data['currency_name']
                            invoice_date = invoice_item_data['date_col']
                            # id = invoice_item_data[0]
                            # material_id = invoice_item_data[1]
                            # name = invoice_item_data[2]
                            # quantity1 = invoice_item_data[4]
                            # unit_name = invoice_item_data[6]

                            material_details = self.database_operations.fetchMaterial(material_id)
                            material_units = {1: material_details[12], 2: material_details[13],
                                              3: material_details[14]}
                            default_unit = material_units[material_details[15]]

                            if unit1_id == default_unit:
                                pass
                            else:
                                conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1_id,
                                                                                                           default_unit)
                                quantity_in_default_unit = 1 * conversion_rate
                                unit_price = float(unit_price) / float(quantity_in_default_unit)

                            if unified_currency:
                                if currency_id == targeted_currency:
                                    item_price = unit_price
                                else:
                                    if unified_exchange_date:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            currency_id,
                                            targeted_currency,
                                            exchange_date)
                                    else:
                                        exchange_value = self.database_operations.fetchExchangeValue(
                                            currency_id,
                                            targeted_currency,
                                            invoice_date)

                                    if exchange_value:
                                        item_price = unit_price * float(exchange_value[0][1])

                                    else:
                                        print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                                        pass

                        elif production_batch_id:
                            production_batch_data = self.database_operations.fetchManufactureProcess(
                                production_batch_id)
                            quantity1 = production_batch_data[4]
                            unit1 = production_batch_data[5]
                            currency_id = production_batch_data[14]
                            expenses_cost = production_batch_data[15]
                            machines_operation_cost = production_batch_data[16]
                            salaries_cost = production_batch_data[17]
                            composition_materials_cost = production_batch_data[21]
                            production_date = production_batch_data[11]
                            # quantity_unit_expenses = production_batch_data[22]
                            # id = production_batch_data[0]
                            # material_id = production_batch_data[1]
                            # working_hours = production_batch_data[2]
                            # batch = production_batch_data[3]
                            # quantity2 = production_batch_data[6]
                            # unit2 = production_batch_data[7]
                            # quantity3 = production_batch_data[8]
                            # unit3 = production_batch_data[9]
                            # pullout_date = production_batch_data[10]
                            # expenses_type = production_batch_data[12]
                            # material_pricing_method = production_batch_data[13]
                            # warehouse = production_batch_data[18]
                            # mid_account = production_batch_data[19]
                            # account = production_batch_data[20]
                            # expenses_distribution = production_batch_data[23]
                            # state = production_batch_data[24]
                            # ingredients_pullout_method = production_batch_data[25]
                            # ingredients_pullout_account = production_batch_data[26]
                            # material_name = production_batch_data[27]
                            # unit1_name = production_batch_data[28]
                            # unit2_name = production_batch_data[29]
                            # unit3_name = production_batch_data[30]
                            # currency_name = production_batch_data[31]
                            # account_name = production_batch_data[32]
                            # mid_account_name = production_batch_data[33]
                            # group = production_batch_data[34]

                            total_cost = float(composition_materials_cost) + float(salaries_cost) + float(
                                machines_operation_cost) + float(expenses_cost)
                            unit_cost = total_cost / float(quantity1)

                            material_details = self.database_operations.fetchMaterial(material_id)
                            material_units = {"1": material_details[12], "2": material_details[13],
                                              "3": material_details[14]}
                            default_unit = material_units[material_details[15]]

                            if unit1 == default_unit:
                                pass
                            else:
                                conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1,
                                                                                                           default_unit)
                                quantity_in_default_unit = 1 * conversion_rate

                                unit_price = float(unit_cost) / float(quantity_in_default_unit)


                            if unified_currency:
                                if currency_id == targeted_currency:
                                    item_price = unit_price
                                else:
                                    if unified_exchange_date:
                                        exchange_value = self.database_operations.fetchExchangeValue(currency_id,
                                                                                                              targeted_currency,
                                                                                                              exchange_date)
                                    else:
                                        exchange_value = self.database_operations.fetchExchangeValue(currency_id,
                                                                                                              targeted_currency,
                                                                                                              production_date)

                                    if exchange_value:
                                        item_price = unit_price * float(exchange_value[0][1])

                                    else:
                                        print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                                        pass

                        if item_price:
                            estimated_price = float(item_price) * float(quantity)
                            targeted_currency=currency_id
                            targeted_currency_name=currency_name

                    currency_data = [targeted_currency, targeted_currency_name]
                    if warehouse_id in warehouses_data:
                        warehouses_data[warehouse_id].append([estimated_price, currency_data])
                    else:
                        warehouses_data[warehouse_id] = [[estimated_price, currency_data]]

            for warehouse_id, warehouse_entries_estimated_prices in warehouses_data.items():
                warehouse_info = self.database_operations.fetchWarehouse(warehouse_id)
                if warehouse_info:
                    warehouse_name = warehouse_info[2]
                    warehouse_account_id = warehouse_info[6]
                    warehouse_account_name = warehouse_info[11]

                    for warehouse_item in warehouse_entries_estimated_prices:
                        item_estimated_price = warehouse_item[0]
                        item_currency_id = warehouse_item[1][0]
                        item_currency_name = warehouse_item[1][1]
                        warehouse_info = str(warehouse_id)+"-"+str(warehouse_name)
                        item = [warehouse_info, 'warehouse', warehouse_account_id, None, item_currency_id, None, 'creditor', item_estimated_price, None, item_currency_name, warehouse_account_name, None, None, None, None]

                        records.append(item)


            # process sub-accounts
            child_accounts = self.database_operations.fetchChildAccounts(targeted_account, type='final') #type=final because this report calculates only final accounts (Final Accounts Report)
            for child_account in child_accounts:
                child_account_id = child_account[0]
                child_account_name = child_account[1]
                child_records= buildRecordsList(from_date, to_date, child_account_id, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)


                for child_record in child_records:
                    records.append(child_record)

            return records

        def calculateAndAppendSum(nested_dict, sum_entry_name='value'):
            total_sum = 0

            for key, value in nested_dict.items():
                if isinstance(value, dict):
                    entry_sum = 0
                    entry_dicts = {}  # Store multiple 'entry' dictionaries under the same parent
                    if 'entry' in value:
                        for sub_key, sub_value in value['entry'].items():
                            for tuple_item in sub_value:
                                entry_sum += tuple_item[7]
                            entry_dicts[sub_key] = sub_value
                        value.pop('entry')  # Remove all 'entry' keys temporarily

                    child_sum = calculateAndAppendSum(value, sum_entry_name=sum_entry_name)
                    total_sum += entry_sum + child_sum
                    if entry_dicts:  # Restore 'entry' dictionaries if they were removed
                        value['entry'] = entry_dicts
                    value[sum_entry_name] = entry_sum + child_sum

            return total_sum

        def calculateValues(data):
            def calculateValue(node):
                debt = node.get('debt', 0)
                credit = node.get('credit', 0)
                value = abs(credit - debt)
                state = ('creditor' if credit > debt else 'debtor') if credit or debt else None
                return value, state

            def traverseAndCalculate(node):
                for key, value in node.items():
                    if isinstance(value, dict):
                        traverseAndCalculate(value)
                        item_value, item_state = calculateValue(value)
                        if item_value:
                            value['value'] = item_value
                        if item_state:
                            value['state'] = item_state

            traverseAndCalculate(data)

        records=buildRecordsList(from_date, to_date, targeted_account, targeted_currency,
                       unified_currency, targeted_currency_name, unified_exchange_date, exchange_date,
                       distinct_currency, data_sources)

        for record in records:
            account_type = record['type_col']
            if (account_type=='creditor'):
                addItemToResutlDict(creditors, record)
            elif (account_type=='debtor'):
                addItemToResutlDict(debtors, record)

        # #Dummy data
        # nested_dict = {
        #     (1, 'USD'): {
        #         (361, 'a'): {
        #             'entry': {
        #                 42: [
        #                     (112, 42, 361, '', 1, 405, 'debtor', 8.0, None, 'دولار أمريكي', 'الإيرادات', 'الهدايا',
        #                      (2024, 4, 8), 'journal', None)
        #                 ],
        #                 'warehouse': [['6-a', 'warehouse', 361, None, 1, None, 'debtor', 1.935483870967742, None,
        #                                'دولار أمريكي', 'الإيرادات', None, None, None, None],
        #                               ['6-a', 'warehouse', 361, None, 1, None, 'debtor', 1000, None, 'دولار أمريكي',
        #                                'الإيرادات', None, None, None, None]]
        #             },
        #             (409, 'b'): {
        #                 'entry': {
        #                     42: [
        #                         (113, 42, 409, '', 1, 399, 'debtor', 5.0, None, 'دولار أمريكي', 'e2', 'الاضافات',
        #                          (2024, 4, 8), 'journal', None)
        #                     ]
        #                 },
        #
        #             },
        #             (555, 'c'): {
        #                 'entry': {
        #                     42: [
        #                         (114, 42, 555, '', 1, 401, 'debtor', 10.0, None, 'دولار أمريكي', 'e3', 'النفقات',
        #                          (2024, 4, 9), 'journal', None)
        #                     ]
        #                 },
        #                 (123, 'd'): {
        #                     'entry': {
        #                         101: [
        #                             (116, 101, 555, '', 1, 402, 'debtor', 20.0, None, 'دولار أمريكي', 'e5',
        #                              'المشتريات', (2024, 4, 11), 'journal', None)
        #                         ]},
        #                     (456, 'e'): {
        #                         'entry': {
        #                             201: [
        #                                 (117, 201, 555, '', 1, 403, 'debtor', 25.0, None, 'دولار أمريكي', 'e6',
        #                                  'المبيعات', (2024, 4, 12), 'journal', None)
        #                             ]
        #                         }
        #                     }
        #                 }
        #             },
        #             (777, 'f'): {
        #                 'entry': {
        #                     42: [
        #                         (115, 42, 777, '', 1, 404, 'debtor', 15.0, None, 'دولار أمريكي', 'e4', 'المصروفات',
        #                          (2024, 4, 10), 'journal', None)
        #                     ]
        #                 }
        #             }
        #         }
        #     }
        # }
        #
        # nested_dict2 = {
        #     (1, 'USD'): {
        #         (361, 'a'): {
        #             (409, 'b'): {
        #                 'entry': {
        #                     42: [
        #                         [113, 42, 409, '', 1, 399, 'creditor', 1.0, None, 'دولار أمريكي', 'e2', 'الاضافات',
        #                          (2024, 4, 8), 'journal', None]
        #                     ]
        #                 }
        #             },
        #             (777, 'f'): {
        #                 'entry': {
        #                     42: [
        #                         [115, 42, 777, '', 1, 404, 'creditor', 20.0, None, 'دولار أمريكي', 'e4', 'المصروفات',
        #                          (2024, 4, 10), 'journal', None]
        #                     ]
        #                 }
        #             },
        #             'entry': {
        #                 42: [
        #                     [112, 42, 361, '', 1, 405, 'creditor', 5.0, None, 'دولار أمريكي', 'الإيرادات', 'الهدايا',
        #                      (2024, 4, 8), 'journal', None]
        #                 ],
        #                 'warehouse': [
        #                     ['6-a', 'warehouse', 361, None, 1, None, 'creditor', 1, None, 'دولار أمريكي', 'الإيرادات',
        #                      None, None, None, None],
        #                     ['6-a', 'warehouse', 361, None, 1, None, 'creditor', 1000, None, 'دولار أمريكي',
        #                      'الإيرادات', None, None, None, None]
        #                 ]
        #             }
        #         }
        #     }
        # }

        # def convert_dict_to_json(data):
        #     if isinstance(data, dict):
        #         # Recursively convert nested dictionaries to JSON
        #         return {str(key): convert_dict_to_json(value) for key, value in data.items()}
        #     elif isinstance(data, list):
        #         # Recursively convert nested lists to JSON
        #         return [convert_dict_to_json(item) for item in data]
        #     elif isinstance(data, tuple):
        #         # Recursively convert nested tuples to JSON
        #         return tuple(convert_dict_to_json(item) for item in data)
        #     else:
        #         # Convert non-dict, non-list, non-tuple objects to JSON-serializable format
        #         return data

        calculateAndAppendSum(debtors, 'debt')
        # nested_dict_json=json.dumps(convert_dict_to_json(nested_dict), indent=4)
        # print(nested_dict_json)
        calculateAndAppendSum(creditors, 'credit')
        # nested_dict_json2=json.dumps(convert_dict_to_json(nested_dict2), indent=4)
        # print(nested_dict_json2)
        records_dict = mergeDicts(debtors, creditors)
        # records_dict_json=json.dumps(convert_dict_to_json(records_dict), indent=4)
        # print(records_dict_json)
        calculateValues(records_dict)
        #records_dict_values_json=json.dumps(convert_dict_to_json(records_dict), indent=4)
        #print(records_dict_values_json)
        return records_dict


        # print(debtors, sum_entry_name='debt')
        # print(creditors, sum_entry_name='credit')

        # if unified_currency:
        #     if unified_exchange_date:
        #         exchange_date = exchange_date
        #     else:
        #         exchange_date = None
        #
        #
        #     creditors_dict = {}
        #     for creditor in creditors:
        #         currency = creditor[3]
        #         currency_name = creditor[4]
        #         currency_data = [targeted_currency, targeted_currency_name]
        #         if int(currency) == int(targeted_currency):
        #             creditors_dict.setdefault(tuple(currency_data), []).append(creditor)
        #         else:
        #             if not exchange_date:
        #                 exchange_date = creditor[5]
        #             exchange_value = self.database_operations.fetchExchangeValue(currency, targeted_currency, exchange_date.toString(Qt.ISODate))
        #             if exchange_value:
        #                 old_value = creditor[2]
        #                 new_value = float(old_value) * float(exchange_value[0][1])
        #                 new_value = round(new_value, 4)
        #                 creditor[2] = new_value
        #                 creditor[3] = targeted_currency
        #                 creditor[4] = targeted_currency_name
        #             creditors_dict.setdefault(tuple(currency_data), []).append(creditor)
        #
        #     debtors_dict = {}
        #     for debtor in debtors:
        #         currency = debtor[3]
        #         currency_name = debtor[4]
        #         currency_data = [targeted_currency, targeted_currency_name]
        #         if int(currency) == int(targeted_currency):
        #             debtors_dict.setdefault(tuple(currency_data), []).append(debtor)
        #         else:
        #             if not exchange_date:
        #                 exchange_date = debtor[5]
        #             exchange_value = self.database_operations.fetchExchangeValue(currency, targeted_currency,
        #                                                                                   exchange_date.toString(
        #                                                                                       Qt.ISODate))
        #             if exchange_value:
        #                 old_value = debtor[2]
        #                 new_value = float(old_value) * float(exchange_value[0][1])
        #                 new_value = round(new_value, 4)
        #                 debtor[2] = new_value
        #                 debtor[3] = targeted_currency
        #                 debtor[4] = targeted_currency_name
        #             debtors_dict.setdefault(tuple(currency_data), []).append(debtor)
        #
        # elif distinct_currency:
        #     creditors_dict = {}
        #     for creditor in creditors:
        #         currency = creditor[3]
        #         currency_name = creditor[4]
        #         currency_data = [currency, currency_name]
        #         if tuple(currency_data) not in creditors_dict:
        #             creditors_dict[tuple(currency_data)] = []
        #         creditors_dict[tuple(currency_data)].append(creditor)
        #
        #     debtors_dict = {}
        #     for debtor in debtors:
        #         currency = debtor[3]
        #         currency_name = debtor[4]
        #         currency_data = [currency, currency_name]
        #         if tuple(currency_data) not in debtors_dict:
        #             debtors_dict[tuple(currency_data)] = []
        #         debtors_dict[tuple(currency_data)].append(debtor)
        #
        # else:
        #     return
        #
        # # print(debtors_dict)
        # # print(creditors_dict)
        #
        # debtors_sum = {}
        # for currency_data, journal_entry_items in debtors_dict.items():
        #     for journal_entry_item in journal_entry_items:
        #         account_id, account_name, value, currency, currency_name, journal_entry_date = journal_entry_item
        #
        #         if tuple(currency_data) in debtors_sum:
        #             debtors_sum[tuple(currency_data)] += value
        #         else:
        #             debtors_sum[tuple(currency_data)] = value
        #
        # creditors_sum = {}
        # for currency_data, journal_entry_items in creditors_dict.items():
        #     for journal_entry_item in journal_entry_items:
        #         account_id, account_name, value, currency, currency_name, journal_entry_date = journal_entry_item
        #
        #         if tuple(currency_data) in creditors_sum:
        #             creditors_sum[tuple(currency_data)] += value
        #         else:
        #             creditors_sum[tuple(currency_data)] = value
        #
        # # display results
        # win = {}
        # loss = {}
        # for currency_data in set(creditors_sum.keys()) | set(debtors_sum.keys()):
        #     debtor_value = debtors_sum.get(currency_data, 0.0)
        #     creditor_value = creditors_sum.get(currency_data, 0.0)
        #     difference = creditor_value - debtor_value
        #     if difference > 0:
        #         win[currency_data] = difference
        #     else:
        #         loss[currency_data] = abs(difference)
        #
        # return debtors, creditors, debtors_dict, creditors_dict, creditors_sum, debtors_sum, win, loss
