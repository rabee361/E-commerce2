from PyQt5.QtCore import Qt , QDate
from DatabaseOperations import DatabaseOperations
from Ui_CostCentersReport import Ui_CostCentersReport
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QTableWidgetItem, QSizePolicy, QCheckBox, QPushButton, QFrame, QVBoxLayout, QGridLayout
from PyQt5.QtCore import QCoreApplication , QTranslator
from LanguageManager import LanguageManager
from PyQt5.QtGui import QIcon

class Ui_CostCentersReport_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_CostCentersReport()

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
        window.setWindowIcon(QIcon(':/icons/dispatch_order.png'))
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.fetchCostCenters()
        self.fetchCurrencies()
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

    def fetchCostCenters(self):
        cost_centers = self.database_operations.fetchCostCenters()
        children_queue = []
        for cost_center in cost_centers:
            id = cost_center[0]
            name = cost_center[1]
            parent_id = cost_center[4]

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(name), str(id)])
                self.ui.cost_centers_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.cost_centers_tree.findItems(str(parent_id),
                                                                            Qt.MatchExactly | Qt.MatchRecursive, 1)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(1)

                        child_item = QTreeWidgetItem([str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(cost_center)

        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                parent_id = child[4]

                items_already_in_tree = self.ui.cost_centers_tree.findItems(str(parent_id),
                                                                            Qt.MatchExactly | Qt.MatchRecursive, 1)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(1)

                        child_item = QTreeWidgetItem([str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            self.ui.currency_combobox.addItem(name, id)

    def calculate(self, sub_account=None, targeted_currency=None, from_date=None, to_date=None):
        self.ui.debtor_accounts_tree.clear()
        self.ui.creditor_accounts_tree.clear()
        self.ui.debtor_sum_table.setRowCount(0)
        self.ui.creditor_sum_table.setRowCount(0)
        self.ui.result_win_table.setRowCount(0)
        self.ui.result_loss_table.setRowCount(0)
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)
        targeted_cost_center = self.ui.cost_centers_tree.currentItem().text(1)
        unified_currency = self.ui.unified_currency_radio.isChecked()
        unified_exchange_date = self.ui.unified_exchange_date_radio.isChecked()
        targeted_currency = self.ui.currency_combobox.currentData()
        targeted_currency_name = self.ui.currency_combobox.currentText()
        exchange_date = self.ui.exchange_date_input.date()
        distinct_currency = self.ui.distinct_currency_radio.isChecked()
        debtors, creditors, debtors_dict, creditors_dict, creditors_sum, debtors_sum, win, loss = self.calculateLogic(from_date, to_date, targeted_cost_center, targeted_currency, unified_currency, targeted_currency_name,unified_exchange_date, exchange_date, distinct_currency)

        for currency_data, journal_entry_items in debtors_dict.items():
            currency = currency_data[0]
            currency_name = currency_data[1]

            root_item = QTreeWidgetItem([str(currency), str(currency_name), "", "", ""])
            for journal_entry_item in journal_entry_items:
                account_id, account_name, value, currency, currency_name, journal_entry_date, statement = journal_entry_item
                child_item = QTreeWidgetItem(["", "", str(account_id), str(account_name), str(value), str(statement)])
                root_item.addChild(child_item)
                if not sub_account:
                    self.ui.debtor_accounts_tree.addTopLevelItem(root_item)
        for currency_data, journal_entry_items in creditors_dict.items():
            currency = currency_data[0]
            currency_name = currency_data[1]
            root_item = QTreeWidgetItem([str(currency), str(currency_name), "", "", ""])
            for journal_entry_item in journal_entry_items:
                account_id, account_name, value, currency, currency_name, journal_entry_date, statement = journal_entry_item
                child_item = QTreeWidgetItem(["", "", str(account_id), str(account_name), str(value), str(statement)])
                root_item.addChild(child_item)
                if not sub_account:
                    self.ui.creditor_accounts_tree.addTopLevelItem(root_item)
        for currency_data, value in creditors_sum.items():
            currency = currency_data[0]
            currency_name = currency_data[1]
            numRows = self.ui.creditor_sum_table.rowCount()
            self.ui.creditor_sum_table.insertRow(numRows)
            self.ui.creditor_sum_table.setItem(numRows, 0, QTableWidgetItem(str(currency)))
            self.ui.creditor_sum_table.setItem(numRows, 1, QTableWidgetItem(str(currency_name)))
            self.ui.creditor_sum_table.setItem(numRows, 2, QTableWidgetItem(str(value)))
        for currency_data, value in debtors_sum.items():
            currency = currency_data[0]
            currency_name = currency_data[1]
            numRows = self.ui.debtor_sum_table.rowCount()
            self.ui.debtor_sum_table.insertRow(numRows)
            self.ui.debtor_sum_table.setItem(numRows, 0, QTableWidgetItem(str(currency)))
            self.ui.debtor_sum_table.setItem(numRows, 1, QTableWidgetItem(str(currency_name)))
            self.ui.debtor_sum_table.setItem(numRows, 2, QTableWidgetItem(str(value)))
        for currency_data, value in win.items():
            currency = currency_data[0]
            currency_name = currency_data[1]
            numRows = self.ui.result_win_table.rowCount()
            self.ui.result_win_table.insertRow(numRows)
            self.ui.result_win_table.setItem(numRows, 0, QTableWidgetItem(str(currency)))
            self.ui.result_win_table.setItem(numRows, 1, QTableWidgetItem(str(currency_name)))
            self.ui.result_win_table.setItem(numRows, 2, QTableWidgetItem(str(value)))
        for currency_data, value in loss.items():
            currency = currency_data[0]
            currency_name = currency_data[1]
            numRows = self.ui.result_loss_table.rowCount()
            self.ui.result_loss_table.insertRow(numRows)
            self.ui.result_loss_table.setItem(numRows, 0, QTableWidgetItem(str(currency)))
            self.ui.result_loss_table.setItem(numRows, 1, QTableWidgetItem(str(currency_name)))
            self.ui.result_loss_table.setItem(numRows, 2, QTableWidgetItem(str(value)))

    def calculateLogic(self, from_date, to_date, targeted_cost_center, targeted_currency,
                       unified_currency, targeted_currency_name, unified_exchange_date, exchange_date,
                       distinct_currency):
        cost_center_info = self.database_operations.fetchCostCenter(targeted_cost_center)
        if cost_center_info:
            print(cost_center_info)
            # targeted_cost_center_id = cost_center_info['targeted_cost_center_id']
            # targeted_cost_center_name = cost_center_info['targeted_cost_center_name']
            # targeted_cost_center_notes = cost_center_info['targeted_cost_center_notes']
            # targeted_cost_center_type = cost_center_info['targeted_cost_center_type']
            # targeted_cost_center_parent = cost_center_info['targeted_cost_center_parent']
            # targeted_cost_center_changable_division_factors = cost_center_info['targeted_cost_center_changable_division_factors']
            # targeted_cost_center_date = cost_center_info['targeted_cost_center_date']

        else:
            return

        debtors = []
        creditors = []
        # process journal entries


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

        journal_entry_items = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date,
                                                                              cost_center_id=targeted_cost_center,
                                                                              sources=data_sources)
    
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

            if str(journal_entry_type).lower() == 'creditor':
                creditors.append([account_id, account_name, value, currency, currency_name, journal_entry_date, statement])

            elif str(journal_entry_type).lower() == 'debtor':
                debtors.append([account_id, account_name, value, currency, currency_name, journal_entry_date, statement])

        if unified_currency:
            if unified_exchange_date:
                exchange_date = exchange_date
            else:
                exchange_date = None

            creditors_dict = {}
            for creditor in creditors:
                currency = creditor[3]
                currency_name = creditor[4]
                curreny_data = [targeted_currency, targeted_currency_name]
                if int(currency) == int(targeted_currency):
                    creditors_dict.setdefault(tuple(curreny_data), []).append(creditor)
                else:
                    if not exchange_date:
                        exchange_date = creditor[5]
                        # change the date to QDate (datetime.date will cause an error)
                        entry_date = QDate(creditor[5].year, creditor[5].month, creditor[5].day)
                        exchange_date = entry_date

                    exchange_value = self.database_operations.fetchExchangeValue(currency, targeted_currency,
                                                                                          exchange_date.toString(
                                                                                              Qt.ISODate))
                    if exchange_value:
                        old_value = creditor[2]
                        new_value = float(old_value) * float(exchange_value[0][1])
                        new_value = round(new_value, 4)
                        creditor[2] = new_value
                    creditors_dict.setdefault(tuple(curreny_data), []).append(creditor)

            debtors_dict = {}
            for debtor in debtors:
                currency = debtor[3]
                currency_name = debtor[4]
                curreny_data = [targeted_currency, targeted_currency_name]
                if int(currency) == int(targeted_currency):
                    debtors_dict.setdefault(tuple(curreny_data), []).append(debtor)
                else:
                    if not exchange_date:
                        exchange_date = debtor[5]
                    exchange_value = self.database_operations.fetchExchangeValue(currency, targeted_currency,
                                                                                          exchange_date.toString(
                                                                                              Qt.ISODate))
                    if exchange_value:
                        old_value = debtor[2]
                        new_value = float(old_value) * float(exchange_value[0][1])
                        new_value = round(new_value, 4)
                        debtor[2] = new_value
                    debtors_dict.setdefault(tuple(curreny_data), []).append(debtor)

        elif distinct_currency:
            creditors_dict = {}
            for creditor in creditors:
                currency = creditor[3]
                currency_name = creditor[4]
                currency_data = [currency, currency_name]
                if tuple(currency_data) not in creditors_dict:
                    creditors_dict[tuple(currency_data)] = []
                creditors_dict[tuple(currency_data)].append(creditor)

            debtors_dict = {}
            for debtor in debtors:
                currency = debtor[3]
                currency_name = debtor[4]
                currency_data = [currency, currency_name]
                if tuple(currency_data) not in debtors_dict:
                    debtors_dict[tuple(currency_data)] = []
                debtors_dict[tuple(currency_data)].append(debtor)



        else:
            return
        debtors_sum = {}
        for currency_data, journal_entry_items in debtors_dict.items():
            for journal_entry_item in journal_entry_items:
                account_id, account_name, value, currency, currency_name, journal_entry_date, statement = journal_entry_item

                if tuple(currency_data) in debtors_sum:
                    debtors_sum[tuple(currency_data)] += value
                else:
                    debtors_sum[tuple(currency_data)] = value

        creditors_sum = {}
        for currency_data, journal_entry_items in creditors_dict.items():
            for journal_entry_item in journal_entry_items:
                account_id, account_name, value, currency, currency_name, journal_entry_date, statement = journal_entry_item

                if tuple(currency_data) in creditors_sum:
                    creditors_sum[tuple(currency_data)] += value
                else:
                    creditors_sum[tuple(currency_data)] = value

        # display results
        win = {}
        loss = {}
        for currency_data in set(creditors_sum.keys()) | set(debtors_sum.keys()):
            debtor_value = debtors_sum.get(currency_data, 0.0)
            creditor_value = creditors_sum.get(currency_data, 0.0)
            difference = creditor_value - debtor_value
            if difference > 0:
                win[currency_data] = difference
            else:
                loss[currency_data] = abs(difference)

        return debtors, creditors, debtors_dict, creditors_dict, creditors_sum, debtors_sum, win, loss
