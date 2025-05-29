import win32api
from typing import List
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QDoubleValidator
from LanguageManager import LanguageManager
from PyQt5.QtWidgets import QTableWidgetItem
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_JournalEntryItemView import Ui_JournalEntryItemView
from MyCustomTableCellDelegate import MyCustomTableCellDelegate

class Ui_JournalEntryItemView_Logic(QDialog):
    def __init__(self, sql_connector, journal_entry_item_id=None, journal_entry_id=None, journal_entry_currency=None, journal_entry_currency_name=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_JournalEntryItemView()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

        self.journal_entry_item_id = journal_entry_item_id
        self.journal_entry_id = journal_entry_id
        self.journal_entry_currency = journal_entry_currency
        self.journal_entry_currency_name = journal_entry_currency_name
        self.result = {}

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()
        return self.result

    def initialize(self, window):
        self.fetchAccounts()
        self.fetchCurrencies()
        self.setJournalEntryItemTypes()
        self.fetchCostCenters()
        if self.journal_entry_item_id:
            self.fetchSelectedJournalEntryItem()
            self.ui.entry_currency_checkbox.setChecked(False)
            window.setWindowTitle(self.language_manager.translate("ADD_JOURNAL_ENTRY_ITEM"))
        else:
            window.setWindowTitle(self.language_manager.translate("EDIT_JOURNAL_ENTRY_ITEM"))

        self.ui.save_btn.clicked.connect(lambda: self.addJournalEntryItem(window))

        self.ui.cancel_btn.clicked.connect(lambda: window.close())

        self.ui.journal_entry_cost_center_combobox.setDisabled(True)
        self.ui.journal_entry_item_account_combobox.setDisabled(True)
        self.ui.journal_entry_item_opposite_account_combobox.setDisabled(True)

        self.ui.value_input.setValidator(QDoubleValidator())

        self.ui.entry_currency_checkbox.clicked.connect(lambda: self.disableCurrencyCheckbox())

        self.ui.journal_entry_cost_center_combobox.currentIndexChanged.connect(lambda: self.distributiveCostCenterUiElementsEnabler())
        self.ui.journal_entry_cost_center_combobox.currentIndexChanged.connect(lambda: self.fetchDistributiveCostCenterCenters())

        self.ui.journal_entry_distributive_cost_center_accounts_table.itemChanged.connect(self.cellEdited)

        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.journal_entry_item_account_combobox))
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectOppositeAccountWindow(self.ui.journal_entry_item_opposite_account_combobox))
        self.ui.select_cost_center_btn.clicked.connect(lambda: self.openSelectCostCenterWindow(self.ui.journal_entry_cost_center_combobox))

        self.ui.journal_entry_item_account_combobox.currentIndexChanged.connect(lambda: self.fetchDefaultCostCenter())

    def uiElementsActivator(self, targets: List, state=False):
        print(targets)
        print(state)
        for ui_element in targets:
            ui_element.setEnabled(state)

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        self.ui.journal_entry_item_opposite_account_combobox.addItem(self.language_manager.translate("NONE"), [None, None, None])

        for account in accounts:
            id = account['id']
            name = account['name']
            force_cost_center = account['force_cost_center']
            default_cost_center = account['default_cost_center']

            data = [id, force_cost_center, default_cost_center]

            self.ui.journal_entry_item_account_combobox.addItem(name, data)
            self.ui.journal_entry_item_opposite_account_combobox.addItem(name, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            self.ui.journal_entry_item_currency_combobox.addItem(display_text, id)

    def fetchCostCenters(self):
        self.ui.journal_entry_cost_center_combobox.clear()
        self.ui.journal_entry_cost_center_combobox.addItem(self.language_manager.translate("NONE"), [None, None])
        cost_centers = self.database_operations.fetchCostCenters(['normal', 'distributor'])  # arabic should be removed after translation is done
        for cost_centers in cost_centers:
            # notes = cost_centers[2]
            # Ascending = cost_centers[4]
            # parent = cost_centers[5]
            # changable_division_factors = cost_centers[6]
            # date = cost_centers[7]
            id = cost_centers[0]
            name = cost_centers[1]
            type = cost_centers[3]
            data = [id, type]
            self.ui.journal_entry_cost_center_combobox.addItem(name, data)

    def fetchDefaultCostCenter(self):
        account_data = self.ui.journal_entry_item_account_combobox.currentData()
        force_cost_center = account_data[1]
        default_cost_center = account_data[2]
        if default_cost_center:
            for i in range(self.ui.journal_entry_cost_center_combobox.count()):
                if self.ui.journal_entry_cost_center_combobox.itemData(i)[0] == default_cost_center:
                    self.ui.journal_entry_cost_center_combobox.setCurrentIndex(i)
                    break
            if force_cost_center:
                self.ui.select_cost_center_btn.setEnabled(False)

    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='accounts')
        result = data_picker.showUi()
        if result is not None:
            for i in range(combobox.count()):
                if combobox.itemData(i)[0] == result['id']:
                    combobox.setCurrentIndex(i)
                    break

    def openSelectOppositeAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(combobox.count()):
                if combobox.itemData(i)[0] == result['id']:
                    combobox.setCurrentIndex(i)
                    break

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

    def disableCurrencyCheckbox(self):
        if self.ui.entry_currency_checkbox.isChecked():
            self.ui.journal_entry_item_currency_combobox.setEnabled(False)
        else:
            self.ui.journal_entry_item_currency_combobox.setEnabled(True)

    def fetchSelectedJournalEntryItem(self):
        """Retrieves data of the selected journal entry item from the table and UI elements."""

        journal_entry_item_id = self.journal_entry_item_id

        # Fetch the full entry data from the database
        entry_data = self.database_operations.fetchSelectedJournalEntryItem(journal_entry_item_id)

        if entry_data:
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
            for i in range(self.ui.journal_entry_item_account_combobox.count()):
                item_data = self.ui.journal_entry_item_account_combobox.itemData(i)
                if item_data:
                    if item_data[0] == account_id:
                        self.ui.journal_entry_item_account_combobox.setCurrentIndex(i)
                        break

            # Opposite Account Combobox
            for i in range(self.ui.journal_entry_item_opposite_account_combobox.count()):
                item_data = self.ui.journal_entry_item_opposite_account_combobox.itemData(i)
                if item_data:
                    if item_data[0] == opposite_account_id:
                        self.ui.journal_entry_item_opposite_account_combobox.setCurrentIndex(i)
                        break

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
                

    def setJournalEntryItemTypes(self):
        types = {"debtor": self.language_manager.translate("DEBITOR"), "creditor": self.language_manager.translate("CREDITOR")}
        for key, value in types.items():
            self.ui.journal_entry_item_type_combobox.addItem(value, key)

    def fetchDistributiveCostCenterCenters(self):
        if self.journal_entry_item_id:
            journal_entry_item_id = self.journal_entry_item_id
            selected_cost_center = self.ui.journal_entry_cost_center_combobox.currentData()
            journal_entry_item_value = float(self.ui.value_input.text()) if self.ui.value_input.text() else 0  # Reading value_input from QLineEdit
            if selected_cost_center:
                cost_center_id = selected_cost_center[0]

                # cost_center_type = selected_cost_center[1]
                self.ui.journal_entry_distributive_cost_center_accounts_table.setRowCount(0)
                delegate = MyCustomTableCellDelegate(col=3, row=None)
                self.ui.journal_entry_distributive_cost_center_accounts_table.setItemDelegate(delegate)

                division_factors_sum = 0
                journal_entry_distributive_cost_center_centers = self.database_operations.fetchCostCenterAggregationsDistributives(cost_center_id, check_for_modified_values=True, journal_entry_item_id=journal_entry_item_id)
                if journal_entry_distributive_cost_center_centers:
                    for journal_entry_distributive_cost_center_account in journal_entry_distributive_cost_center_centers:
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
    
    def addJournalEntryItem(self, window):
        type = self.ui.journal_entry_item_type_combobox.currentData()
        statement = self.ui.journal_entry_item_statement_input.toPlainText()
        account = self.ui.journal_entry_item_account_combobox.currentData()
        opposite_account = self.ui.journal_entry_item_opposite_account_combobox.currentData()
        value = self.ui.value_input.text()

        if value == '':
            win32api.MessageBox(0, self.language_manager.translate("ENTRY_VALUE_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"), 0x40 | 0x0)
            return

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

        currency = None
        currency_name = None
        if self.ui.entry_currency_checkbox.isChecked():
            currency = self.journal_entry_currency
            currency_name = self.journal_entry_currency_name
        else:
            currency = self.ui.journal_entry_item_currency_combobox.currentData()
            currency_name = self.ui.journal_entry_item_currency_combobox.currentText()

        account_id = account[0]
        opposite_account_id = opposite_account[0]
        account_name = self.ui.journal_entry_item_account_combobox.currentText()
        opposite_account_name = self.ui.journal_entry_item_opposite_account_combobox.currentText()
    
        self.result = {'journal_entry_id': self.journal_entry_id, 'account_id': account_id, 'account_name': account_name, 'opposite_account_id': opposite_account_id, 'opposite_account_name': opposite_account_name, 'value': value, 'currency': currency, 'currency_name': currency_name, 'type': type, 'statement': statement, 'cost_center_id': cost_center_id, 'distributive_cost_center_distributed_values': distributive_cost_center_distributed_values}

        window.accept()