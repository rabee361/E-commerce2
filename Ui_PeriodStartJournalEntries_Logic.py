from typing import List

import win32api
from PyQt5.QtCore import Qt, QItemSelectionModel , QDate
from PyQt5.QtWidgets import QDialog, QSizePolicy, QTreeWidgetItem, QTableWidgetItem, QTableWidget
from win32con import IDYES, MB_YESNO, IDNO

from DatabaseOperations import DatabaseOperations
from MyCustomTableCellDelegate import MyCustomTableCellDelegate
from Ui_PeriodStartJournalEntries import Ui_PeriodStartJournalEntries
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QDoubleValidator

class Ui_PeriodStartJournalEntries_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_PeriodStartJournalEntries()

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.filter_by_date_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_by_account_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_debtor_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_creditor_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.accounts_tree.itemSelectionChanged.connect(lambda: self.fetchJournalEntries())
        self.ui.calendar.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.value_input.setValidator(QDoubleValidator())

        self.ui.journals_entries_table.itemSelectionChanged.connect(lambda: self.fetchJournalEntryItems())
        self.ui.journals_entries_table.itemSelectionChanged.connect(lambda: self.fetchSelectedJournalsEntry())

        self.ui.filter_by_date_checkbox.clicked.connect(
            lambda: self.uiElementsActivator([self.ui.calendar], int(self.ui.filter_by_date_checkbox.isChecked())))
        self.ui.filter_by_account_checkbox.clicked.connect(lambda: self.uiElementsActivator(
            [self.ui.filter_debtor_checkbox, self.ui.filter_creditor_checkbox, self.ui.accounts_tree],
            int(self.ui.filter_by_account_checkbox.isChecked())))

        self.ui.update_journal_entry_btn.clicked.connect(lambda: self.updateJournalEntry())
        self.ui.update_journal_entry_btn.clicked.connect(lambda: self.fetchJournalEntries())

        self.ui.delete_journal_entry_btn.clicked.connect(lambda: self.deleteJournalEntry())
        self.ui.delete_journal_entry_btn.clicked.connect(lambda: self.fetchJournalEntries())

        self.ui.add_journal_entry_btn.clicked.connect(lambda: self.addJournalEntry())
        self.ui.add_journal_entry_btn.clicked.connect(lambda: self.fetchJournalEntries())

        self.ui.journal_entries_items_table.itemSelectionChanged.connect(lambda: self.fetchSelectedJournalsEntryItem())

        self.ui.update_journal_entry_item_btn.clicked.connect(lambda: self.updateJournalEntryItem())
        self.ui.update_journal_entry_item_btn.clicked.connect(lambda: self.fetchJournalEntryItems())

        self.ui.delete_journal_entry_item_btn.clicked.connect(lambda: self.deleteJournalEntryItem())
        self.ui.delete_journal_entry_item_btn.clicked.connect(lambda: self.fetchJournalEntryItems())

        self.ui.add_journal_entry_item_btn.clicked.connect(lambda: self.addJournalEntryItem())
        self.ui.add_journal_entry_item_btn.clicked.connect(lambda: self.fetchJournalEntryItems())

        self.ui.journal_entry_cost_center_combobox.currentIndexChanged.connect(lambda: self.distributiveCostCenterUiElementsEnabler())
        self.ui.journal_entry_cost_center_combobox.currentIndexChanged.connect(lambda: self.fetchDistributiveCostCenterCenters())

        self.ui.journal_entry_distributive_cost_center_accounts_table.itemChanged.connect(self.cellEdited)
        self.ui.journal_entry_date_input.setDate(QDate.currentDate())

        self.fetchAccounts()
        self.fetchCurrencies()
        self.setJournalEntryItemTypes()
        self.fetchJournalEntries()
        self.fetchCostCenters()

        self.ui.journal_entry_cost_center_combobox.setDisabled(True)
        self.ui.journal_entry_item_account_combobox.setDisabled(True)
        self.ui.journal_entry_item_opposite_account_combobox.setDisabled(True)

        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.journal_entry_item_account_combobox))
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.journal_entry_item_opposite_account_combobox))
        self.ui.select_cost_center_btn.clicked.connect(lambda: self.openSelectCostCenterWindow(self.ui.journal_entry_cost_center_combobox))
    
    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='accounts')
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openSelectCostCenterWindow(self, combobox):
        exclusions = []
        excluded_cost_center = self.database_operations.fetchCostCenters(cost_center_type=['aggregator'])
        for cost_center in excluded_cost_center:
            exclusions.append(cost_center[0])
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='cost_centers', include_none_option=True, exclusions=exclusions)
        result = data_picker.showUi()
        if result is not None:
            for i in range(combobox.count()):
                if combobox.itemData(i)[0] == result['id']:
                    combobox.setCurrentIndex(i)
                    break
        
    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        children_queue = []
        for account in accounts:
            id = account[0]
            name = account[1]
            code = account[2]
            details = account[3]
            date = account[4]
            parent_id = account[5]
            parent_name = account[6]

            self.ui.journal_entry_item_account_combobox.addItem(name, id)
            self.ui.journal_entry_item_opposite_account_combobox.addItem(name, id)

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(code), str(name), str(id)])
                self.ui.accounts_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id), Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(account)

        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                code = child[2]
                details = child[3]
                date = child[4]
                parent_id = child[5]
                parent_name = child[6]

                items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id),
                                                                        Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)
                            print("DELETED")

    def fetchJournalEntries(self):
        calendar = self.ui.calendar
        date_filter = ''
        account_filter = ''
        type_filter = ''

        if self.ui.filter_by_date_checkbox.isChecked():
            date_filter = calendar.selectedDate().toString(Qt.ISODate)

        if self.ui.filter_by_account_checkbox.isChecked():
            current_item = self.ui.accounts_tree.currentItem()
            if current_item:
                account_filter = current_item.text(2)

        debtore_filter = self.ui.filter_debtor_checkbox.isChecked()
        creditore_filter = self.ui.filter_creditor_checkbox.isChecked()
        if debtore_filter and not creditore_filter:
            type_filter = 'debtor'
        elif not debtore_filter and creditore_filter:
            type_filter = 'creditor'

        self.ui.journals_entries_table.setRowCount(0)
        journal_entries = self.database_operations.fetchJournalEntries(date_filter, account_filter, type_filter, origin_type='period_start')
        for entry in journal_entries:
            id = entry['id']
            currency = entry['currency']
            date = entry['date_col']
            entry_date = entry['entry_date']
            origin_type = entry['origin_type']
            origin_id = entry['origin_id']
            currency_name = entry['currency_name']

            numRows = self.ui.journals_entries_table.rowCount()
            self.ui.journals_entries_table.insertRow(numRows)

            self.ui.journals_entries_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.journals_entries_table.setItem(numRows, 1, QTableWidgetItem(str(entry_date)))
            self.ui.journals_entries_table.setItem(numRows, 2, QTableWidgetItem(str(currency)))
            self.ui.journals_entries_table.setItem(numRows, 3, QTableWidgetItem(str(currency_name)))
            self.ui.journals_entries_table.setItem(numRows, 4, QTableWidgetItem(str(date)))

    def fetchJournalEntryItems(self):
        self.ui.journal_entries_items_table.setRowCount(0)
        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            if item is not None:
                entry_id = item.text()
                # Use the ID value as needed
                entries = self.database_operations.fetchJournalEntryItems(journal_entry=entry_id)
                for entry in entries:
                    id = entry[0]
                    journal_entry_id = entry[1]
                    account_id = entry[2]
                    statement = entry[3]
                    currency = entry[4]
                    opposite_account_id = entry[5]
                    type = entry[6]
                    value = entry[7]
                    currency_name = entry[8]
                    account_name = entry[9]
                    opposite_account_name = entry[10]

                    numRows = self.ui.journal_entries_items_table.rowCount()
                    self.ui.journal_entries_items_table.insertRow(numRows)

                    debtor = ''
                    creditor = ''
                    if str(type).lower() == 'debtor':
                        debtor = value
                    elif str(type).lower() == 'creditor':
                        creditor = value

                    self.ui.journal_entries_items_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.journal_entries_items_table.setItem(numRows, 1, QTableWidgetItem(str(journal_entry_id)))
                    self.ui.journal_entries_items_table.setItem(numRows, 2, QTableWidgetItem(str(account_id)))
                    self.ui.journal_entries_items_table.setItem(numRows, 3, QTableWidgetItem(str(account_name)))
                    self.ui.journal_entries_items_table.setItem(numRows, 4, QTableWidgetItem(str(debtor)))
                    self.ui.journal_entries_items_table.setItem(numRows, 5, QTableWidgetItem(str(creditor)))
                    self.ui.journal_entries_items_table.setItem(numRows, 6, QTableWidgetItem(str(statement)))
                    self.ui.journal_entries_items_table.setItem(numRows, 7, QTableWidgetItem(str(currency)))
                    self.ui.journal_entries_items_table.setItem(numRows, 8, QTableWidgetItem(str(currency_name)))
                    self.ui.journal_entries_items_table.setItem(numRows, 9, QTableWidgetItem(str(opposite_account_id)))
                    self.ui.journal_entries_items_table.setItem(numRows, 10,
                                                                QTableWidgetItem(str(opposite_account_name)))

    def uiElementsActivator(self, targets: List, state=False):
        print(targets)
        print(state)
        for ui_element in targets:
            ui_element.setEnabled(state)
    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            self.ui.journal_entry_currency_combobox.addItem(display_text, id)
            self.ui.journal_entry_item_currency_combobox.addItem(display_text, id)

    def setJournalEntryItemTypes(self):
        types = {"debtor": "مدين", "creditor": "دائن"}
        for key, value in types.items():
            self.ui.journal_entry_item_type_combobox.addItem(value, key)
            
    def fetchSelectedJournalsEntry(self):
        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            if item is not None:
                entry_id = item.text()
                entry_data = self.database_operations.fetchSelectedJournalEntry(entry_id)
                id = entry_data[0]
                currency = entry_data[1]
                date = entry_data[2]
                entry_date = entry_data[3]
                origin_type = entry_data[4]
                origin_id = entry_data[5]

                self.ui.journal_entry_date_input.setDate(entry_date)
                self.ui.journal_entry_currency_combobox.setCurrentIndex(self.ui.journal_entry_currency_combobox.findData(currency))

                self.ui.journal_entry_item_statement_input.clear()
                self.ui.value_input.clear()
                for i in range(self.ui.journal_entry_cost_center_combobox.count()):
                    item_data = self.ui.journal_entry_cost_center_combobox.itemData(i)  # Get data of each item
                    if item_data[0] == None:  # Compare first element (assumed ID)
                        self.ui.journal_entry_cost_center_combobox.setCurrentIndex(i)  # Select matching item
                        break  # Stop iterating as item found
    def updateJournalEntry(self):
        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            if item is not None:
                entry_id = item.text()
                entry_date = self.ui.journal_entry_date_input.date()
                currency = self.ui.journal_entry_currency_combobox.currentData()
                self.database_operations.updateJournalEntry(entry_id, entry_date.toString(Qt.ISODate), currency)

    def deleteJournalEntry(self):
        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            messagebox_result = win32api.MessageBox(None, "هل تريد بالتأكيد حذف القيد؟", "تنبيه", MB_YESNO);
            if (messagebox_result == IDYES):
                if item is not None:
                    entry_id = item.text()
                    self.database_operations.deleteJournalEntry(entry_id)
                else:
                    pass
            elif (messagebox_result == IDNO):
                pass

    def addJournalEntry(self):
        entry_date = self.ui.journal_entry_date_input.date()
        currency = self.ui.journal_entry_currency_combobox.currentData()
        origin_type = 'period_start'
        self.database_operations.addJournalEntry(entry_date.toString(Qt.ISODate), currency, origin_type=origin_type)

    def fetchSelectedJournalsEntryItem(self):
        """Retrieves data of the selected journal entry item from the table and UI elements."""

        selected_row = self.ui.journal_entries_items_table.currentRow()
        if selected_row >= 0:  # Check if a row is selected
            item = self.ui.journal_entries_items_table.item(selected_row,
                                                            0)  # Access item in the selected row (assuming ID is in column 0)
            if item is not None:  # Ensure item exists
                item_id = item.text()  # Get the item's ID from the table

                # Fetch the full entry data from the database
                entry_data = self.database_operations.fetchSelectedJournalEntryItem(item_id)

                # Extract individual fields from the fetched data
                id = entry_data[0]
                journal_entry_id = entry_data[1]
                account_id = entry_data[2]
                statement = entry_data[3]
                currency = entry_data[4]
                opposite_account_id = entry_data[5]
                type = entry_data[6]
                value = entry_data[7]
                cost_center_id = entry_data[8]
                currency_name = entry_data[9]
                account_name = entry_data[10]
                opposite_account_name = entry_data[11]

                # Update UI elements with the fetched data
                # Account Combobox
                self.ui.journal_entry_item_account_combobox.setCurrentIndex(
                    self.ui.journal_entry_item_account_combobox.findData(account_id))

                # Opposite Account Combobox
                self.ui.journal_entry_item_opposite_account_combobox.setCurrentIndex(
                    self.ui.journal_entry_item_opposite_account_combobox.findData(opposite_account_id))

                # Currency Combobox
                self.ui.journal_entry_item_currency_combobox.setCurrentIndex(
                    self.ui.journal_entry_item_currency_combobox.findData(currency))

                # Type Combobox
                self.ui.journal_entry_item_type_combobox.setCurrentIndex(
                    self.ui.journal_entry_item_type_combobox.findData(
                        type))

                # Statement Input
                self.ui.journal_entry_item_statement_input.setText(statement)

                # Value Input
                self.ui.value_input.setText(str(value))

                # Cost Center Combobox
                for i in range(self.ui.journal_entry_cost_center_combobox.count()):
                    item_data = self.ui.journal_entry_cost_center_combobox.itemData(i)  # Get data of each item
                    if item_data[0] == cost_center_id:  # Compare first element (assumed ID)
                        self.ui.journal_entry_cost_center_combobox.setCurrentIndex(i)  # Select matching item
                        break  # Stop iterating as item found
    def fetchCostCenters(self):
        self.ui.journal_entry_cost_center_combobox.clear()
        self.ui.journal_entry_cost_center_combobox.addItem("لا يوجد", [None, None])
        cost_centers = self.database_operations.fetchCostCenters(['normal', 'distributor'])  # arabic should be removed after translation is done
        for cost_center in cost_centers:
            # notes = cost_centers[2]
            # Ascending = cost_centers[4]
            # parent = cost_centers[5]
            # changable_division_factors = cost_centers[6]
            # date = cost_centers[7]
            id = cost_center[0]
            name = cost_center[1]
            type = cost_center[3]
            data = [id, type]
            self.ui.journal_entry_cost_center_combobox.addItem(name, data)
    def distributiveCostCenterUiElementsEnabler(self):
        selected_cost_center = self.ui.journal_entry_cost_center_combobox.currentData()
        if selected_cost_center:
            cost_center_type = selected_cost_center[1]
            if str(cost_center_type).lower() == 'distributor':  # remove the arabic after translation
                self.uiElementsActivator([self.ui.journal_entry_distributive_cost_center_accounts_table],
                                         True)
            else:
                self.uiElementsActivator([self.ui.journal_entry_distributive_cost_center_accounts_table],
                                         False)

    def fetchDistributiveCostCenterCenters(self):
        selected_journal_entry_row = self.ui.journal_entries_items_table.currentRow()
        if selected_journal_entry_row >= 0:
            journal_entry_item_id = self.ui.journal_entries_items_table.item(selected_journal_entry_row, 0)  # Assuming ID is in the first column
            if journal_entry_item_id is not None:
                journal_entry_item_id=journal_entry_item_id.text()
                selected_cost_center = self.ui.journal_entry_cost_center_combobox.currentData()
                journal_entry_item_value = float(self.ui.value_input.text()) if self.ui.value_input.text() else 0  # Reading value_input from QLineEdit
                if selected_cost_center:
                    cost_center_id = selected_cost_center[0]

                    # cost_center_type = selected_cost_center[1]
                    self.ui.journal_entry_distributive_cost_center_accounts_table.setRowCount(0)
                    delegate = MyCustomTableCellDelegate(col=3, row=None)
                    self.ui.journal_entry_distributive_cost_center_accounts_table.setItemDelegate(delegate)

                    division_factors_sum = 0
                    journal_entry_distributive_cost_center_accounts = self.database_operations.fetchCostCenterAggregationsDistributives(cost_center_id, check_for_modified_values=True, journal_entry_item_id=journal_entry_item_id)
                    if journal_entry_distributive_cost_center_accounts:
                        for journal_entry_distributive_cost_center_account in journal_entry_distributive_cost_center_accounts:
                            entry_id = journal_entry_distributive_cost_center_account[0]
                            master_cost_center_id = journal_entry_distributive_cost_center_account[1]
                            distributed_cost_center_id = journal_entry_distributive_cost_center_account[2]
                            division_factor = journal_entry_distributive_cost_center_account[3]
                            distributed_cost_center_name = journal_entry_distributive_cost_center_account[4]
                            if division_factor:
                                division_factors_sum += float(division_factor)

                            name = journal_entry_distributive_cost_center_account[4]



                            # Calculate the percentage value
                            percentage_value = journal_entry_item_value * float(division_factor) / 100  # Assuming division_factor is a percentage

                            # Set the calculated value in the 5th column



                            # Create a empty row at bottom of table
                            numRows = self.ui.journal_entry_distributive_cost_center_accounts_table.rowCount()
                            self.ui.journal_entry_distributive_cost_center_accounts_table.insertRow(numRows)
                            self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(numRows, 0, QTableWidgetItem(str(entry_id)))
                            self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(numRows, 1, QTableWidgetItem(str(distributed_cost_center_id)))
                            self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(numRows, 2, QTableWidgetItem(str(distributed_cost_center_name)))
                            self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(numRows, 3, QTableWidgetItem(str(division_factor)))
                            self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(numRows, 4, QTableWidgetItem(str(percentage_value)))

    def cellEdited(self, item): #. The item parameter in the cellEdited method should be automatically passed by the Qt framework when the itemChanged signal is emitted.
        """Calculates the sum of numbers in the 3rd column of the table and updates the total percentage input with color highlighting for exceeding or not matching 100%."""
        column = item.column()
        if column == 3:
            journal_entry_item_value = float(self.ui.value_input.text()) if self.ui.value_input.text() else 0  # Reading value_input from QLineEdit
            total_percentage = 0
            num_rows = self.ui.journal_entry_distributive_cost_center_accounts_table.rowCount()

            for row in range(num_rows):
                division_factor = self.ui.journal_entry_distributive_cost_center_accounts_table.item(row,3).text() if self.ui.journal_entry_distributive_cost_center_accounts_table.item(row,3) else 0 # Access the item in the 3rd column
                percentage_value = journal_entry_item_value * float(division_factor) / 100  # Assuming division_factor is a percentage
                self.ui.journal_entry_distributive_cost_center_accounts_table.setItem(row, 4, QTableWidgetItem(str(percentage_value)))

                if division_factor:
                    try:
                        number = float(division_factor)
                        total_percentage += number
                    except ValueError:
                        # Handle invalid input gracefully, e.g., display a warning message
                        pass

            self.ui.journal_entry_distributive_cost_center_accounts_total_percentage_input.setText(str(total_percentage))

            # Change background color and text color based on percentage
            color = "green" if total_percentage == 100 else "red"
            self.ui.journal_entry_distributive_cost_center_accounts_total_percentage_input.setStyleSheet(
                f"background-color: {color}; color: white;"
            )
    def updateJournalEntryItem(self):
        selected_row = self.ui.journal_entries_items_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journal_entries_items_table.item(selected_row, 0)  # Assuming ID is in the first column
            if item is not None:
                item_id = item.text()
                currency = self.ui.journal_entry_item_currency_combobox.currentData()
                type = self.ui.journal_entry_item_type_combobox.currentData()
                statement = self.ui.journal_entry_item_statement_input.toPlainText()
                account = self.ui.journal_entry_item_account_combobox.currentData()
                opposite_account = self.ui.journal_entry_item_opposite_account_combobox.currentData()
                value = self.ui.value_input.text()
                cost_center_id = self.ui.journal_entry_cost_center_combobox.currentData()[0]  # data=[id, type]
                cost_center_type = self.ui.journal_entry_cost_center_combobox.currentData()[1]  # data=[id, type]
                distributive_cost_center_distributed_values = []
                if str(cost_center_type).lower() == 'distributor':  # remove the arabic after translation
                    # convert the cost_center_distributives into a list
                    for row in range(self.ui.journal_entry_distributive_cost_center_accounts_table.rowCount()):
                        row_data = [
                            self.ui.journal_entry_distributive_cost_center_accounts_table.item(row, 0).text(),
                            # Get text from column with index 0 (id)
                            self.ui.journal_entry_distributive_cost_center_accounts_table.item(row, 3).text()
                            # Get text from column with index 3 (percent)
                        ]
                        distributive_cost_center_distributed_values.append(row_data)

                    total_percentage = float(self.ui.journal_entry_distributive_cost_center_accounts_total_percentage_input.text())
                    if total_percentage != 100:
                        print(
                            f"Distributive cost center percentages don't sum to 100 (got {total_percentage}), skipping insertion.")
                        return  # Do nothing and break out of the function
                else:
                    pass
                
                self.ui.journal_entry_item_statement_input.clear()
                self.ui.value_input.clear()
                self.ui.journal_entry_item_account_combobox.setCurrentIndex(0)
                self.ui.journal_entry_item_opposite_account_combobox.setCurrentIndex(0)
                self.ui.journal_entry_item_currency_combobox.setCurrentIndex(0)
                self.ui.journal_entry_cost_center_combobox.setCurrentIndex(self.ui.journal_entry_cost_center_combobox.findText("لا يوجد"))

                self.database_operations.updateJournalEntryItem(item_id, currency, type, statement, account,opposite_account, value, cost_center_id, distributive_cost_center_distributed_values)
                
    def addJournalEntryItem(self):
        currency = self.ui.journal_entry_item_currency_combobox.currentData()
        type = self.ui.journal_entry_item_type_combobox.currentData()
        statement = self.ui.journal_entry_item_statement_input.toPlainText()
        account = self.ui.journal_entry_item_account_combobox.currentData()
        opposite_account = self.ui.journal_entry_item_opposite_account_combobox.currentData()
        value = self.ui.value_input.text()

        cost_center_id = self.ui.journal_entry_cost_center_combobox.currentData()[0] #data=[id, type]
        cost_center_type = self.ui.journal_entry_cost_center_combobox.currentData()[1] #data=[id, type]
        distributive_cost_center_distributed_values = []
        if str(cost_center_type).lower() == 'distributor':  # remove the arabic after translation
            #convert the cost_center_distributives into a list
            for row in range(self.ui.journal_entry_distributive_cost_center_accounts_table.rowCount()):
                row_data = [
                    self.ui.journal_entry_distributive_cost_center_accounts_table.item(row, 0).text(),  # Get text from column with index 0
                    self.ui.journal_entry_distributive_cost_center_accounts_table.item(row, 3).text()  # Get text from column with index 3
                ]
                distributive_cost_center_distributed_values.append(row_data)

                total_percentage = float(self.ui.journal_entry_distributive_cost_center_accounts_total_percentage_input.text())

                if total_percentage != 100:
                    print(
                        f"Distributive cost center percentages don't sum to 100 (got {total_percentage}), skipping insertion.")
                    return  # Do nothing and break out of the function
        else:
            pass

        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0 and value:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            journal_entry_id = item.text()
            self.database_operations.addJournalEntryItem(journal_entry_id, currency, type, statement, account,opposite_account, value, cost_center_id, distributive_cost_center_distributed_values)
            self.ui.journal_entry_item_statement_input.clear()
            self.ui.value_input.clear()
            self.ui.journal_entry_item_account_combobox.setCurrentIndex(0)
            self.ui.journal_entry_item_opposite_account_combobox.setCurrentIndex(0)
            self.ui.journal_entry_item_currency_combobox.setCurrentIndex(0)
            self.ui.journal_entry_cost_center_combobox.setCurrentIndex(self.ui.journal_entry_cost_center_combobox.findText("لا يوجد"))
        else:
            if not value:
                message = "قيمة خاطئة"
                win32api.MessageBox(0, message, "خطأ")
    def deleteJournalEntryItem(self):
        selected_row = self.ui.journal_entries_items_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journal_entries_items_table.item(selected_row, 0)  # Assuming ID is in the first column
            messagebox_result = win32api.MessageBox(None, "هل انت متأكد؟", "تنبيه", MB_YESNO)
            if (messagebox_result == IDYES):
                if item is not None:
                    item_id = item.text()
                    self.database_operations.deleteJournalEntryItem(item_id)
                    # clear and set fields after deletion
                    self.ui.value_input.clear()
                    self.ui.journal_entry_item_statement_input.clear()
                    self.ui.journal_entry_item_account_combobox.setCurrentIndex(0)
                    self.ui.journal_entry_item_opposite_account_combobox.setCurrentIndex(0)
                    self.ui.journal_entry_item_currency_combobox.setCurrentIndex(0)
                    self.ui.journal_entry_cost_center_combobox.setCurrentIndex(self.ui.journal_entry_cost_center_combobox.findText("لا يوجد"))
            elif (messagebox_result == IDNO):
                pass