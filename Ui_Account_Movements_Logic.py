import Colors
import datetime
from DatabaseOperations import DatabaseOperations
from Ui_Account_Movements import Ui_Account_Movements
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem , QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from Colors import light_red_color, white_color, colorizeTreeItems
from PyQt5.QtCore import Qt , QDate
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon


class Ui_Account_Movements_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Account_Movements()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

        # Avoid duplicate accounts calculations
        self.visited_accounts = []

        # Save selected invoices
        self.selected_invoices = {}
        self.include_invoices_payments = True
    
    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/move.png'))
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.accounts_combobox.setEnabled(False)
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.fetchCurrencies()
        self.fetchAccounts()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.to_date_input.setDate(QDate.currentDate())

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
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.accounts_combobox.setCurrentIndex(self.ui.accounts_combobox.findData(result['id']))

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
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

    def calculate(self, targeted_currency=None, from_date=None, to_date=None):
        self.ui.results_tree.clear()
        self.visited_accounts = []

        targeted_account = self.ui.accounts_combobox.currentData()
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)

        unified_currency = self.ui.unified_currency_radio.isChecked()
        unified_exchange_date = self.ui.unified_exchange_date_radio.isChecked()
        targeted_currency = self.ui.currency_combobox.currentData()
        targeted_currency_name = self.ui.currency_combobox.currentText()
        exchange_date = self.ui.exchange_date_input.date()
        distinct_currency = self.ui.distinct_currency_radio.isChecked()

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

        result_dict = self.calculateLogic(targeted_account, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)


        def find_items_in_tree(parent_item=self.ui.results_tree.invisibleRootItem(), account_id=None, date=None, currency_id=None):
            matching_items = []

            for i in range(parent_item.childCount()):
                child_item = parent_item.child(i)
                if account_id and child_item.text(0)==str(account_id):
                    if date:
                        for j in range(child_item.childCount()):
                            child2_item=child_item.child(j)
                            if child2_item.text(2) == str(date):
                                if currency_id:
                                    for k in range(child2_item.childCount()):
                                        child3_item=child2_item.child(k)
                                        if child3_item.text(3) == str(currency_id):
                                            matching_items.append(child3_item)
                                else:
                                    matching_items.append(child2_item)
                    else:
                        matching_items.append(child_item)



            return matching_items

        def addDataToTable(dictionary, root_item=None): #inner function
            tree_items_dict={}
            if root_item==None:
                root_item = self.ui.results_tree.invisibleRootItem()
            for key, values in dictionary.items():
                account_id = key[0]
                account_name = key[1]
                for value in values:
                    if isinstance(value, list):
                        creditors_dict, debtors_dict = value
                        for date, creditors_values in creditors_dict.items():
                            for currency_data, value in creditors_values.items():

                                if account_id not in tree_items_dict:
                                    tree_items_dict[account_id] = {}
                                if date not in tree_items_dict[account_id]:
                                    tree_items_dict[account_id][date] = {}
                                if currency_data not in tree_items_dict[account_id][date]:
                                    tree_items_dict[account_id][date][currency_data] = [0, 0]

                                tree_items_dict[account_id][date][currency_data][0]=value

                        for date, debtors_values in debtors_dict.items():
                            for currency_data, value in debtors_values.items():

                                if account_id not in tree_items_dict:
                                    tree_items_dict[account_id] = {}
                                if date not in tree_items_dict[account_id]:
                                    tree_items_dict[account_id][date] = {}
                                if currency_data not in tree_items_dict[account_id][date]:
                                    tree_items_dict[account_id][date][currency_data] = [0, 0]

                                tree_items_dict[account_id][date][currency_data][1]=value

                        for account_id, account_data in tree_items_dict.items():
                            accounts_already_in_tree = find_items_in_tree(account_id=account_id)
                            account_tree_item = QTreeWidgetItem([str(account_id), str(account_name), "", "", "", "", "",""])
                            if len(accounts_already_in_tree)>0:
                                parent_item=accounts_already_in_tree[0]
                                parent_item.addChild(account_tree_item)

                            for date, date_data in account_data.items():
                                dates_already_in_tree = find_items_in_tree(account_id=account_id, date=date)
                                if len(dates_already_in_tree) > 0:
                                    date_tree_item = dates_already_in_tree[0]
                                else:
                                    date_tree_item = QTreeWidgetItem(["", "", str(date), "", "", "", "",""])
                                    account_tree_item.addChild(date_tree_item)

                                for currency_data, value in date_data.items():
                                    currency_id = currency_data[0]
                                    currency_name = currency_data[1]
                                    creditors_value, debtors_value = value
                                    currencies_already_in_tree = find_items_in_tree(account_id=account_id, date=date,currency_id=currency_id)
                                    if len(currencies_already_in_tree) > 0:
                                        currency_tree_item=currencies_already_in_tree[0]
                                    else:
                                        currency_tree_item = QTreeWidgetItem(["", "", "", str(currency_id), str(currency_name), "", "",""])
                                        date_tree_item.addChild(currency_tree_item)

                                    difference = float(debtors_value)-float(creditors_value)
                                    result_tree_item = QTreeWidgetItem(["", "", "", "", "", str(round(float(debtors_value), 2)), str(round(float(creditors_value), 2)), str(round(float(difference), 2))])
                                    if float(debtors_value)!=float(creditors_value):
                                        result_tree_item.setBackground(5, Colors.light_red_color)
                                        result_tree_item.setBackground(6, Colors.light_red_color)
                                        result_tree_item.setBackground(7, Colors.light_red_color)
                                    currency_tree_item.addChild(result_tree_item)

                            if root_item is None:
                                self.ui.results_tree.addTopLevelItem(account_tree_item)
                            else:
                                root_item.addChild(account_tree_item)

                            root_item=account_tree_item

                    elif isinstance(value, dict):
                        addDataToTable(value, root_item)

        print(result_dict)
        addDataToTable(result_dict)
        colorizeTreeItems(self.ui.results_tree, Colors.blue)
   
    def calculateLogic(self, targeted_account, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources):

        if unified_currency:
            if unified_exchange_date:
                exchange_date = exchange_date
            else:
                exchange_date = None

        account_info = self.database_operations.fetchAccount(targeted_account)
        if account_info:
            targeted_account_id = account_info['id']
            targeted_account_name = account_info['name']
            targeted_account_code = account_info['code']
            targeted_account_details = account_info['details']
            targeted_account_parent_account = account_info['parent_account']
            targeted_account_financial_statement_block = account_info['financial_statement_block']
            targeted_account_date = account_info['date_col']
            targeted_account_type = account_info['type_col']
            targeted_account_final_account = account_info['final_account']
        else:
            return


        journal_entry_items_direct = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, account=targeted_account, sources=data_sources)
        journal_entry_items_opposite = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date, opposite_account=targeted_account, sources=data_sources)
        
        journal_entry_items = journal_entry_items_direct + journal_entry_items_opposite

        result_dict = {}
        debtors_dict = {}
        creditors_dict = {}

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
            origin_type = journal_entry_item['origin_type']
            origin_id = journal_entry_item['origin_id']

            if unified_currency:
                currency = currency
                currency_name = currency_name
                if int(currency) == int(targeted_currency):
                    pass
                else:
                    if not exchange_date:
                        exchange_date = journal_entry_date
                    exchange_value = self.database_operations.fetchExchangeValue(currency, targeted_currency, exchange_date.toString(Qt.ISODate))
                    if exchange_value:
                        old_value = value
                        new_value = float(old_value) * float(exchange_value[0][1])
                        new_value = round(new_value, 4)
                        value = new_value
                        currency = targeted_currency
                        currency_name = targeted_currency_name
            elif distinct_currency:
                pass

            currency_key = (currency, currency_name) #tuple

            if isinstance(journal_entry_date, str):
                journal_entry_date = datetime.datetime.strptime(journal_entry_date, '%Y-%m-%d')
            month_key = journal_entry_date.strftime("%b")  # Assuming you want abbreviated month names as keys

            print(journal_entry_type)

            if journal_entry_type == 'debtor':
                if month_key in debtors_dict and currency_key in debtors_dict[month_key]:
                    debtors_dict[month_key][currency_key] += value
                else:
                    if month_key not in debtors_dict:
                        debtors_dict[month_key] = {}
                    debtors_dict[month_key][currency_key] = value

            elif journal_entry_type == 'creditor':
                if month_key in creditors_dict and currency_key in creditors_dict[month_key]:
                    creditors_dict[month_key][currency_key] += value
                else:
                    if month_key not in creditors_dict:
                        creditors_dict[month_key] = {}
                    creditors_dict[month_key][currency_key] = value

        key = (targeted_account_id, targeted_account_name)  # tuple
        result_dict[key]=[[creditors_dict, debtors_dict]]

        # child_accounts = []
        child_accounts = self.database_operations.fetchChildAccounts(targeted_account)
        for child_account in child_accounts:
            child_account_id = child_account[0]
            child_account_name = child_account[1]
            if child_account_id in self.visited_accounts:
                continue
            self.visited_accounts.append(child_account_id)
            child_result_dict = self.calculateLogic(child_account_id, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

            if child_result_dict:
                if key in result_dict:
                    result_dict[key].append(child_result_dict)
                else: #in case parent doesn't have journal entry items of its own, but it children have
                    result_dict[key] = [child_result_dict]

            for child_key, child_values in child_result_dict.items():
                for child_value in child_values:
                    if isinstance(child_value, list):
                        child_creditors_dict, child_debtors_dict=child_value

                        for child_debtors_month_key, child_debtors_currency_keys in child_debtors_dict.items():
                            for child_debtors_currency_key, child_journal_entry_item_value in child_debtors_currency_keys.items():
                                if child_debtors_month_key in debtors_dict and child_debtors_currency_key in debtors_dict[child_debtors_month_key]:
                                    debtors_dict[child_debtors_month_key][child_debtors_currency_key] += child_journal_entry_item_value
                                else:
                                    if child_debtors_month_key not in debtors_dict:
                                        debtors_dict[child_debtors_month_key] = {}
                                    debtors_dict[child_debtors_month_key][child_debtors_currency_key] = child_journal_entry_item_value


                        for child_creditors_month_key, child_creditors_currency_keys in child_creditors_dict.items():
                            for child_creditors_currency_key, child_journal_entry_item_value in child_creditors_currency_keys.items():
                                if child_creditors_month_key in creditors_dict and child_creditors_currency_key in creditors_dict[child_creditors_month_key]:
                                    creditors_dict[child_creditors_month_key][child_creditors_currency_key] += child_journal_entry_item_value
                                else:
                                    if child_creditors_month_key not in creditors_dict:
                                        creditors_dict[child_creditors_month_key] = {}
                                    creditors_dict[child_creditors_month_key][child_creditors_currency_key] = child_journal_entry_item_value

            for k,v in result_dict:
                if isinstance(v,list):
                    v[0]=creditors_dict
                    v[1]=debtors_dict
    

        accounts_with_final_account = self.database_operations.fetchAccounts(type='all', final_account=targeted_account)
        for child_account in accounts_with_final_account:
            child_account_id = child_account[0]
            child_account_name = child_account[1]
            if child_account_id in self.visited_accounts:
                continue
            self.visited_accounts.append(child_account_id)
            child_result_dict = self.calculateLogic(child_account_id, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

            if child_result_dict:
                if key in result_dict:
                    result_dict[key].append(child_result_dict)
                else: #in case parent doesn't have journal entry items of its own, but it children have
                    result_dict[key] = [child_result_dict]

            for child_key, child_values in child_result_dict.items():
                for child_value in child_values:
                    if isinstance(child_value, list):
                        child_creditors_dict, child_debtors_dict=child_value

                        for child_debtors_month_key, child_debtors_currency_keys in child_debtors_dict.items():
                            for child_debtors_currency_key, child_journal_entry_item_value in child_debtors_currency_keys.items():
                                if child_debtors_month_key in debtors_dict and child_debtors_currency_key in debtors_dict[child_debtors_month_key]:
                                    debtors_dict[child_debtors_month_key][child_debtors_currency_key] += child_journal_entry_item_value
                                else:
                                    if child_debtors_month_key not in debtors_dict:
                                        debtors_dict[child_debtors_month_key] = {}
                                    debtors_dict[child_debtors_month_key][child_debtors_currency_key] = child_journal_entry_item_value


                        for child_creditors_month_key, child_creditors_currency_keys in child_creditors_dict.items():
                            for child_creditors_currency_key, child_journal_entry_item_value in child_creditors_currency_keys.items():
                                if child_creditors_month_key in creditors_dict and child_creditors_currency_key in creditors_dict[child_creditors_month_key]:
                                    creditors_dict[child_creditors_month_key][child_creditors_currency_key] += child_journal_entry_item_value
                                else:
                                    if child_creditors_month_key not in creditors_dict:
                                        creditors_dict[child_creditors_month_key] = {}
                                    creditors_dict[child_creditors_month_key][child_creditors_currency_key] = child_journal_entry_item_value

            for k,v in result_dict:
                if isinstance(v,list):
                    v[0]=creditors_dict
                    v[1]=debtors_dict

        return result_dict
