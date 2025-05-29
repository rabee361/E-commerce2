from PyQt5.QtCore import Qt , QDate
from PyQt5.QtWidgets import QDialog, QSizePolicy, QTreeWidgetItem, QFrame, QVBoxLayout, QGridLayout, QCheckBox, QPushButton
from DatabaseOperations import DatabaseOperations
from Colors import colorizeTreeItems, blue_sky_color
from Ui_FinancialStatementsReports import Ui_FinancialStatementsReports
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_FinancialStatementsReports_Logic(QDialog):
    def __init__(self, sql_connector, target_statement=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_FinancialStatementsReports()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.target_statement = target_statement

        # Save selected invoices
        self.selected_invoices = {}
        self.include_invoices_payments = True

        # Avoid duplicate accounts calculations
        self.visited_accounts = []

    def showUi(self):
        window = QDialog()
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchFinancialStatements()
        self.fetchCurrencies()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.select_financial_statement_btn.clicked.connect(lambda: self.openFinancialStatementsWindow())
        self.ui.to_date_input.setDate(QDate.currentDate())
        self.ui.financial_statements_combobox.setEnabled(False)

        if self.target_statement:
            self.ui.financial_statements_combobox.setCurrentIndex(self.ui.financial_statements_combobox.findData(self.target_statement))
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


    def fetchFinancialStatements(self):
        financial_statements = self.database_operations.fetchFinancialStatements()
        for financial_statement in financial_statements:
            id = financial_statement[0]
            name = financial_statement[1]
            self.ui.financial_statements_combobox.addItem(str(name), id)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            self.ui.currency_combobox.addItem(name, id)

    def openFinancialStatementsWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'financial_statements')
        result = data_picker.showUi()
        if result:
            financial_statement_id = result['id']
            self.ui.financial_statements_combobox.setCurrentIndex(self.ui.financial_statements_combobox.findData(financial_statement_id))

    def calculate(self):
        self.visited_accounts = []
        self.ui.result_tree.clear()
        
        targeted_financial_statement_id = self.ui.financial_statements_combobox.currentData()
        targeted_financial_statement_name = self.ui.financial_statements_combobox.currentText()
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)
        distinct_currency = self.ui.distinct_currency_radio.isChecked()
        unified_currency = self.ui.unified_currency_radio.isChecked()
        targeted_currency = self.ui.currency_combobox.currentData()
        targeted_currency_name = self.ui.currency_combobox.currentText()
        unified_exchange_date = self.ui.unified_exchange_date_radio.isChecked()
        exchange_date = self.ui.exchange_date_input.date()
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

        result_dict = self.calculateLogic(targeted_financial_statement_id,
                                          targeted_financial_statement_name, from_date,
                                          to_date, distinct_currency,
                                          unified_currency, targeted_currency,
                                          targeted_currency_name,
                                          unified_exchange_date,
                                          exchange_date, data_sources)

        def populate_tree(tree_widget, result_dict):
            def get_nested_items(tree_widget, financial_statement_dict):
                items_to_add = []
                for financial_statement_block_key, financial_statement_block_value in \
                        financial_statement_dict.items():
                    if isinstance(financial_statement_block_value, list):  # So it is a financial statement that uses the targeted financial statement as its final
                        value = round(financial_statement_block_value[0], 2)
                        item = QTreeWidgetItem(
                            [" ", " ", str(financial_statement_block_key[0]),
                             str(financial_statement_block_key[1]), " ", " ",
                             str(value)])
                        items_to_add.append(item)
                        item.addChildren(get_nested_items(tree_widget, financial_statement_block_value[1]))
                    else:
                        value = round(financial_statement_block_value, 2)
                        item = QTreeWidgetItem(
                            [" ", " ", " ", " ", str(financial_statement_block_key[0]),
                             str(financial_statement_block_key[1]),
                             str(value)])
                        items_to_add.append(item)

                return items_to_add

            for currency_key, currency_value in result_dict.items():  # Currencies Level
                if isinstance(currency_key, tuple):
                    currency_id = currency_key[0]
                    currency_name = currency_key[1]
                    currency_item = QTreeWidgetItem([str(currency_id), str(currency_name)])
                    tree_widget.addTopLevelItem(currency_item)
                    for financial_statement_key, financial_statement_value in currency_value.items():  # Financial Statement Level
                        if isinstance(financial_statement_key, tuple):
                            value = round(financial_statement_value[0], 2)
                            financial_statement_item = QTreeWidgetItem(
                                [" ", " ", str(financial_statement_key[0]),
                                 str(financial_statement_key[1]), " ", " ",
                                 str(value)])
                            currency_item.addChild(financial_statement_item)
                            financial_statement_item.addChildren(get_nested_items(tree_widget, financial_statement_value[1]))

        populate_tree(self.ui.result_tree, result_dict)

    def calculateLogic(self, targeted_financial_statement_id, targeted_financial_statement_name, from_date, to_date,
                       distinct_currency,
                       unified_currency, targeted_currency, targeted_currency_name, unified_exchange_date,
                       exchange_date, data_sources):

        result_dict = {}
        financial_statement_value = 0
        financial_statement_key = (targeted_financial_statement_id, targeted_financial_statement_name)

        # Fetch financial statement blocks
        financial_statement_blocks = self.database_operations.fetchFinancialStatementBlocks(
            targeted_financial_statement_id)
        for financial_statement_block in financial_statement_blocks:
            financial_statement_block_id = financial_statement_block[0]
            financial_statement_block_name = financial_statement_block[1]
            financial_statement_block_key = (financial_statement_block_id, financial_statement_block_name)

            # Fetch accounts that use this block
            accounts = self.database_operations.fetchAccounts(financial_statement_block=financial_statement_block_id)
            
            # Calculate each account value and add it to the value of financial statement block
            for account in accounts:

                targeted_account_id = account[0]

                if targeted_account_id in self.visited_accounts:
                    continue
                else:
                    # Append children accounts
                    child_accounts = self.database_operations.fetchChildAccounts(account[0])
                    for child_account in child_accounts:
                        accounts.append(child_account)
                    # Add the account to the visited accounts list
                    self.visited_accounts.append(targeted_account_id)

                direct_journal_entry_items = self.database_operations.fetchJournalEntryItems(from_date=from_date,
                                                                                             to_date=to_date,
                                                                                             account=targeted_account_id,
                                                                                             sources=data_sources)
                opposite_journal_entry_items = self.database_operations.fetchJournalEntryItems(from_date=from_date,
                                                                                               to_date=to_date,
                                                                                               opposite_account=targeted_account_id,
                                                                                               sources=data_sources)
                journal_entry_items = direct_journal_entry_items + opposite_journal_entry_items
                
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
                            exchange_value = self.database_operations.fetchExchangeValue(currency,
                                                                                                  targeted_currency,
                                                                                                  exchange_date.toString(
                                                                                                      Qt.ISODate))
                            if exchange_value:
                                old_value = value
                                new_value = float(old_value) * float(exchange_value[0][1])
                                new_value = round(new_value, 4)
                                value = new_value
                                currency = targeted_currency
                                currency_name = targeted_currency_name
                            else:
                                continue

                    elif distinct_currency:
                        pass

                    if targeted_account_id == opposite_account_id:
                        value = value * (-1)
                    if journal_entry_type == 'debtor':
                        value = value * (-1)

                    currency_key = (currency, currency_name)
                    if currency_key in result_dict:
                        if financial_statement_block_key in result_dict[currency_key][financial_statement_key][1]:
                            # Update Financial Statement Block value
                            old_value = result_dict[currency_key][financial_statement_key][1][
                                financial_statement_block_key]
                            new_value = old_value + value
                            result_dict[currency_key][financial_statement_key][1][
                                financial_statement_block_key] = new_value
                        else:
                            result_dict[currency_key][financial_statement_key][1][financial_statement_block_key] = value
                    else:
                        result_dict[currency_key] = {financial_statement_key: [financial_statement_value,
                                                                               {financial_statement_block_key: value}]}

                    # Update Financial Statement value
                    old_value = result_dict[currency_key][financial_statement_key][0]
                    new_value = old_value + value
                    result_dict[currency_key][financial_statement_key][0] = new_value

        # Check for financial statements that use the targeted_financial_statement as its final
        financial_statements = self.database_operations.fetchFinancialStatements(
            final_financial_statement=targeted_financial_statement_id)
        for financial_statement in financial_statements:
            nested_financial_statement_id = financial_statement[0]
            nested_financial_statement_name = financial_statement[1]
            nested_financial_statement_key = (nested_financial_statement_id, nested_financial_statement_name)

            nested_financial_statement_dict = self.calculateLogic(nested_financial_statement_id,
                                                                  nested_financial_statement_name, from_date, to_date,
                                                                  distinct_currency, unified_currency,
                                                                  targeted_currency, targeted_currency_name,
                                                                  unified_exchange_date,
                                                                  exchange_date, data_sources)

            for nested_currency_key in nested_financial_statement_dict.keys():

                nested_financial_statement_value = \
                    nested_financial_statement_dict[nested_currency_key][nested_financial_statement_key][0]
                result_dict[nested_currency_key][financial_statement_key][1][
                    nested_financial_statement_key] = [nested_financial_statement_value, nested_financial_statement_dict[nested_currency_key][nested_financial_statement_key][1]]

                if nested_currency_key not in result_dict:
                    result_dict[nested_currency_key][financial_statement_key][0][
                        nested_financial_statement_key] = nested_financial_statement_value

                else:
                    # Update financial statement value
                    old_value = result_dict[nested_currency_key][financial_statement_key][0]
                    new_value = old_value + nested_financial_statement_value
                    result_dict[nested_currency_key][financial_statement_key][0] = new_value

        return result_dict
