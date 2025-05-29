import Colors
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
from Ui_Ledger import Ui_Ledger
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTranslator

class Ui_Ledger_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Ledger()
        # Avoid duplicate accounts calculations
        self.visited_accounts = []
        
        # Save selected invoices
        self.selected_invoices = {}
        self.include_invoices_payments = True
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/bookkeeper.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchCurrencies()
        self.fetchAccounts()
        self.ui.accounts_combobox.setEnabled(False)
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.to_date_input.setDate(QDate.currentDate())
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)

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
        self.ui.debtors_sum_tree.clear()
        self.ui.creditors_sum_tree.clear()
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
        
        if self.ui.include_manufactures_checkbox.isChecked():
            data_sources.append('manufacture')

        if self.ui.include_loans_checkbox.isChecked():
            data_sources.append('loan')
            data_sources.append('loan_payment')

        records_dict, debtors_sum_dict, creditors_sum_dict = self.calculateLogic(targeted_account, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

        # Add debtors sum to debtors sum tree
        for (currency_id, currency_name), sum_value in debtors_sum_dict.items():
            tree_item = QTreeWidgetItem([str(currency_id), str(currency_name), str(sum_value)])
            self.ui.debtors_sum_tree.addTopLevelItem(tree_item)

        # Add creditors sum to creditors sum tree 
        for (currency_id, currency_name), sum_value in creditors_sum_dict.items():
            tree_item = QTreeWidgetItem([str(currency_id), str(currency_name), str(sum_value)])
            self.ui.creditors_sum_tree.addTopLevelItem(tree_item)


        #print(records_dict)
        def addDataToTable(dictionary, parent_account=None): #inner function
            for key, values in dictionary.items():
                    #add the key (the account) to the tree
                    items_already_in_tree = self.ui.results_tree.findItems(str(key),Qt.MatchExactly | Qt.MatchRecursive, 0)
                    if len(items_already_in_tree) > 0:
                        pass 
                    else:
                        tree_item = QTreeWidgetItem([str(key[0]), str(key[1]), "", "", "", "", "", "", "", "", "", ""])
                        if parent_account:
                            parent_account_id=parent_account[0]
                            parent_tree_items = self.ui.results_tree.findItems(str(parent_account_id),Qt.MatchExactly | Qt.MatchRecursive,0)
                            if len(parent_tree_items)>0:
                                parent_tree_item = parent_tree_items[0]
                                parent_tree_item.addChild(tree_item)
                            else:
                                pass
                        else:
                            self.ui.results_tree.addTopLevelItem(tree_item)

                    for value in values:
                        print (str(key)+"::"+str(type(value))+"::"+str(value))
                        if isinstance(value, list):
                            journal_entry_item_id, journal_entry_id, account_id, statement, currency, opposite_account_id, journal_entry_type, value, cost_center_id, currency_name, account_name, opposite_account_name, journal_entry_date, origin_type, origin_id = value

                            debtor = ''
                            creditor = ''
                            if str(journal_entry_type).lower() == 'debtor':
                                debtor = value
                            elif str(journal_entry_type).lower() == 'creditor':
                                creditor = value

                            child_item = QTreeWidgetItem([str(account_id), str(account_name), "", str(journal_entry_item_id), str(origin_type), str(debtor), str(creditor), str(currency), str(currency_name), str(statement), str(opposite_account_id), str(opposite_account_name)])
                            tree_item.addChild(child_item)

                        elif isinstance(value, dict):
                            addDataToTable(value, parent_account=key)

        addDataToTable(records_dict)


    def calculateLogic(self, targeted_account, from_date, to_date, targeted_currency, unified_currency,targeted_currency_name,unified_exchange_date, exchange_date, distinct_currency, data_sources):

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

        records_dict = {}
        key = (targeted_account_id, targeted_account_name)  # tuple
        
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
            origin_type = journal_entry_item['origin_type']
            origin_id = journal_entry_item['origin_id']

            if unified_currency:
                currency = currency
                currency_name = currency_name
                if int(currency) == int(targeted_currency):
                    pass
                else:
                    if not exchange_date:
                        # change the date to QDate (datetime.date will cause an error)
                        entry_date = QDate(journal_entry_date.year, journal_entry_date.month, journal_entry_date.day)
                        exchange_date = entry_date
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

            record = [journal_entry_item_id, journal_entry_id, account_id, statement, currency, opposite_account_id, journal_entry_type, value, cost_center_id, currency_name, account_name, opposite_account_name, journal_entry_date, origin_type, origin_id]


            if key in records_dict:
                records_dict[key].append(record)
            else:
                records_dict[key] = [record]

        # Aggregating debtor and creditor sums
        debtors_sum_dict = {}
        creditors_sum_dict = {}
        for records in records_dict.values():
            for record in records:
                if isinstance(record, list):
                    currency_key = tuple([record[4], record[9]])  # [currency_id, currency_name]
                    if record[6] == 'debtor':
                        debtors_sum_dict[currency_key] = debtors_sum_dict.get(currency_key, 0) + record[7]
                    elif record[6] == 'creditor':
                        creditors_sum_dict[currency_key] = creditors_sum_dict.get(currency_key, 0) + record[7]


        # process sub-accounts
        child_accounts = self.database_operations.fetchChildAccounts(targeted_account)
        for child_account in child_accounts:
            child_account_id = child_account[0]
            child_account_name = child_account[1]
            if child_account_id in self.visited_accounts:
                continue
            self.visited_accounts.append(child_account_id)
            child_records_dict, child_debtors_sum_dict, child_creditors_sum_dict = self.calculateLogic(child_account_id, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

            if child_records_dict:
                if key in records_dict:
                    records_dict[key].append(child_records_dict)
                else:
                    records_dict[key] = [child_records_dict]

            if child_debtors_sum_dict:
                for child_currency_key, child_currency_value in child_debtors_sum_dict.items():
                    child_currency_id = child_currency_key[0]
                    child_currency_name = child_currency_key[1]
                    if child_currency_key in debtors_sum_dict:
                        debtors_sum_dict[child_currency_key] += child_currency_value
                    else:
                        debtors_sum_dict[child_currency_key] = child_currency_value

            if child_creditors_sum_dict:
                for child_currency_key, child_currency_value in child_creditors_sum_dict.items():
                    child_currency_id = child_currency_key[0]
                    child_currency_name = child_currency_key[1]
                    if child_currency_key in creditors_sum_dict:
                        creditors_sum_dict[child_currency_key] += child_currency_value
                    else:
                        creditors_sum_dict[child_currency_key] = child_currency_value


        accounts_with_final_account = self.database_operations.fetchAccounts(type='all', final_account=targeted_account)
        for final_account in accounts_with_final_account:
            final_account_id = final_account[0]
            final_account_name = final_account[1]
            if final_account_id in self.visited_accounts:
                continue
            self.visited_accounts.append(final_account_id)
            child_records_dict, child_debtors_sum_dict, child_creditors_sum_dict = self.calculateLogic(final_account_id, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name, unified_exchange_date, exchange_date, distinct_currency, data_sources)

            if child_records_dict:
                if key in records_dict:
                    records_dict[key].append(child_records_dict)
                else:
                    records_dict[key] = [child_records_dict]

            if child_debtors_sum_dict:
                for final_account_currency_key, final_account_currency_value in child_debtors_sum_dict.items():
                    final_account_currency_id = final_account_currency_key[0]
                    final_account_currency_name = final_account_currency_key[1]
                    if final_account_currency_key in debtors_sum_dict:
                        debtors_sum_dict[final_account_currency_key] += final_account_currency_value
                    else:
                        debtors_sum_dict[final_account_currency_key] = final_account_currency_value

            if child_creditors_sum_dict:
                for final_account_currency_key, final_account_currency_value in child_creditors_sum_dict.items():
                    final_account_currency_id = final_account_currency_key[0]
                    final_account_currency_name = final_account_currency_key[1]
                    if final_account_currency_key in creditors_sum_dict:
                        creditors_sum_dict[final_account_currency_key] += final_account_currency_value
                    else:
                        creditors_sum_dict[final_account_currency_key] = final_account_currency_value

    

        return records_dict, debtors_sum_dict, creditors_sum_dict
