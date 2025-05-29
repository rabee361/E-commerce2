import win32api
from typing import List
from Ui_Journal import Ui_Journal
from PyQt5.QtGui import QDoubleValidator
from win32con import IDYES, MB_YESNO, IDNO
from Ui_Accounts_Logic import Ui_Accounts_Logic
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QItemSelectionModel , QDate
from Ui_JournalEntryItemView_Logic import Ui_JournalEntryItemView_Logic
from PyQt5.QtWidgets import QDialog, QSizePolicy, QTreeWidgetItem, QTableWidgetItem, QTableWidget, QDateEdit, QComboBox, QPushButton
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_Journal_Logic(QDialog):
    def __init__(self, sql_connector, origin_type=''):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Journal()
        self.origin_type = origin_type
        self.entries_edited = False
        self.temp_journal_entries = {}
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/grades_report.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.journals_entries_table.hideColumn(0)
        self.ui.journals_entries_table.hideColumn(3)

        self.ui.journal_entries_items_table.hideColumn(0)
        self.ui.journal_entries_items_table.hideColumn(1)
        self.ui.journal_entries_items_table.hideColumn(2)
        self.ui.journal_entries_items_table.hideColumn(3)
        self.ui.journal_entries_items_table.hideColumn(4)
        self.ui.journal_entries_items_table.hideColumn(5)
        self.ui.journal_entries_items_table.hideColumn(6)

        self.fetchAccounts()
        self.fetchJournalEntries()

        self.ui.filter_by_date_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_by_account_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_debtor_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.filter_creditor_checkbox.clicked.connect(lambda: self.fetchJournalEntries())
        self.ui.accounts_tree.itemSelectionChanged.connect(lambda: self.fetchJournalEntries())
        self.ui.calendar.clicked.connect(lambda: self.fetchJournalEntries())

        self.ui.journals_entries_table.itemSelectionChanged.connect(lambda: self.fetchJournalEntryItems())

        # self.ui.journals_entries_table.cellChanged.connect(lambda r, c: self.updateStorageDict(r, c))

        self.ui.filter_by_date_checkbox.clicked.connect(
            lambda: self.uiElementsActivator([self.ui.calendar], int(self.ui.filter_by_date_checkbox.isChecked())))
        self.ui.filter_by_account_checkbox.clicked.connect(lambda: self.uiElementsActivator(
            [self.ui.filter_debtor_checkbox, self.ui.filter_creditor_checkbox, self.ui.accounts_tree],
            int(self.ui.filter_by_account_checkbox.isChecked())))

        self.ui.delete_journal_entry_btn.clicked.connect(lambda: self.deleteJournalEntry())

        self.ui.delete_journal_entry_item_btn.clicked.connect(lambda: self.deleteJournalEntryItem())

        self.ui.add_journal_entry_item_btn.clicked.connect(lambda: self.openJournalEntryItemViewWindow(add_new_item=True))
        self.ui.journal_entries_items_table.itemDoubleClicked.connect(lambda: self.openJournalEntryItemViewWindow())
        
        self.ui.save_btn.clicked.connect(lambda: self.save(window))

        self.ui.manage_accounts_btn.clicked.connect(lambda: self.openManageAccountsWindow())

    def uiElementsActivator(self, targets: List, state=False):
        print(targets)
        print(state)
        for ui_element in targets:
            ui_element.setEnabled(state)

    def updateStorageDict(self, row):
        self.ui.journals_entries_table.blockSignals(True)

        self.temp_journal_entries[row]['edited'] = True

        currency = self.ui.journals_entries_table.cellWidget(row, 4).currentData()
        self.temp_journal_entries[row]['currency'] = currency

        currency_name = self.ui.journals_entries_table.cellWidget(row, 4).currentText()
        self.temp_journal_entries[row]['currency_name'] = currency_name

        entry_date = self.ui.journals_entries_table.cellWidget(row, 5).date().toString(Qt.ISODate)
        self.temp_journal_entries[row]['entry_date'] = entry_date

        # Update currency in table
        self.ui.journals_entries_table.setItem(row, 3, QTableWidgetItem(str(currency)))

        self.ui.journals_entries_table.blockSignals(False)

    def openManageAccountsWindow(self):
        Ui_Accounts_Logic(self.sql_connector).showUi()
        self.fetchAccounts()

    def openJournalEntryItemViewWindow(self, add_new_item=False):
        journal_entry_row = self.ui.journals_entries_table.currentRow()
        if journal_entry_row == -1:
            win32api.MessageBox(0, self.language_manager.translate("JOURNAL_ENTRY_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"), 0x40 | 0x0)
            return
        
        journal_entry_item_id = None
        journal_entry_item_row = None
        journal_entry_item_ui = None

        if add_new_item:
            journal_entry_item_id = '#'
            journal_entry_item_row = self.ui.journal_entries_items_table.rowCount()

            journal_entry_id = self.temp_journal_entries[journal_entry_row].get('id')
            journal_entry_currency = self.temp_journal_entries[journal_entry_row].get('currency')
            journal_entry_currency_name = self.temp_journal_entries[journal_entry_row].get('currency_name')

            journal_entry_item_ui = Ui_JournalEntryItemView_Logic(self.sql_connector, journal_entry_id=journal_entry_id, journal_entry_currency=journal_entry_currency, journal_entry_currency_name=journal_entry_currency_name)

        else:
            selected_row = self.ui.journal_entries_items_table.currentRow()
            if selected_row >= 0:
                item = self.ui.journal_entries_items_table.item(selected_row, 0)  # Assuming ID is in the first column
                if item is not None:
                    entry_id = item.text()
                    if entry_id != '#':
                        journal_entry_item_id = int(entry_id)
                        journal_entry_item_row = selected_row
                        journal_entry_item_ui = Ui_JournalEntryItemView_Logic(self.sql_connector, journal_entry_item_id=entry_id)

        if journal_entry_item_ui:
            result = journal_entry_item_ui.showUi()
            if result != {}:
                if add_new_item:
                    self.ui.journal_entries_items_table.insertRow(journal_entry_item_row)
                journal_entry_id = result['journal_entry_id']
                account_id = result['account_id']
                account_name = result['account_name']
                opposite_account_id = result['opposite_account_id']
                opposite_account_name = result['opposite_account_name']
                value = result['value']
                currency = result['currency']
                currency_name = result['currency_name']
                type = result['type']
                statement = result['statement']
                cost_center_id = result['cost_center_id']
                distributive_cost_center_distributed_values = result['distributive_cost_center_distributed_values']

                creditor = ''
                debtor = ''
                if opposite_account_id is None:
                    if str(type).lower() == 'creditor':
                        creditor = account_name
                    elif str(type).lower() == 'debtor':
                        debtor = account_name
                else:
                    if str(type).lower() == 'creditor':
                        creditor = account_name
                        debtor = opposite_account_name
                    elif str(type).lower() == 'debtor':
                        creditor = opposite_account_name
                        debtor = account_name

                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 0, QTableWidgetItem(str('#')))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 1, QTableWidgetItem(str(journal_entry_id)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 2, QTableWidgetItem(str(account_id)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 3, QTableWidgetItem(str(opposite_account_id)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 4, QTableWidgetItem(str(cost_center_id)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 5, QTableWidgetItem(str(currency)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 6, QTableWidgetItem(str(type)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 7, QTableWidgetItem(str(debtor)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 8, QTableWidgetItem(str(creditor)))

                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 9, QTableWidgetItem(str(value)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 10, QTableWidgetItem(str(currency_name)))
                self.ui.journal_entries_items_table.setItem(journal_entry_item_row, 11, QTableWidgetItem(str(statement)))
             
                # Mark the journal entry as edited
                self.temp_journal_entries[journal_entry_row]['edited'] = True

                item_dict = {'id': journal_entry_item_id, 'journal_entry_id': journal_entry_id, 'account_id': account_id, 'account_name': account_name, 'opposite_account_id': opposite_account_id, 'opposite_account_name': opposite_account_name, 'value_col': value, 'currency': currency, 'currency_name': currency_name, 'type_col': type, 'statement_col': statement, 'cost_center_id': cost_center_id, 'distributive_cost_center_distributed_values': distributive_cost_center_distributed_values}

                # Add item to temporary storage
                if add_new_item:
                    self.temp_journal_entries[journal_entry_row]['items'].append(item_dict)
                else:
                    # Find and replace existing entry with same ID
                    for i in range(len(self.temp_journal_entries[journal_entry_row]['items'])):
                        if self.temp_journal_entries[journal_entry_row]['items'][i]['id'] == journal_entry_item_id:
                            self.temp_journal_entries[journal_entry_row]['items'][i] = item_dict
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

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(code), str(name), str(id)])
                self.ui.accounts_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id),
                                                                        Qt.MatchExactly | Qt.MatchRecursive, 2)

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

                items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id),Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)
                            print("DELETED")

    def fetchJournalEntries(self):
        self.temp_journal_entries = {}
        calendar = self.ui.calendar
        date_filter = ''
        account_filter = ''
        type_filter = ''
        numRows = 0

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
        journal_entries = self.database_operations.fetchJournalEntries(date_filter=date_filter, account=account_filter,type_filter=type_filter, origin_type=self.origin_type)
        for entry in journal_entries:
            id = entry['id']
            journal_entry_currency_id = entry['currency']
            date = entry['date_col']
            entry_date = entry['entry_date']
            origin_type = entry['origin_type']
            origin_id = entry['origin_id']
            journal_entry_currency_name = entry['currency_name']
            
            numRows = self.ui.journals_entries_table.rowCount()
            self.ui.journals_entries_table.insertRow(numRows)

            # Store existing entry in temporary storage
            self.temp_journal_entries[numRows] = {
                'id': id,
                'is_new': False,
                'edited': False,
                'deleted': False,
                'date': date,
                'origin_type': origin_type,
                'entry_date': entry_date,
                'currency': journal_entry_currency_id,
                'items': [],
            }

            self.ui.journals_entries_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.journals_entries_table.setItem(numRows, 1, QTableWidgetItem(str(date)))
            self.ui.journals_entries_table.setItem(numRows, 2, QTableWidgetItem(str(origin_type)))
            self.ui.journals_entries_table.setItem(numRows, 3, QTableWidgetItem(str(journal_entry_currency_id)))

            currency_combo = QComboBox()
            currencies = self.database_operations.fetchCurrencies()
            for currency in currencies:
                currency_combo.addItem(currency['name'], currency['id'])
            currency_combo.setCurrentIndex(currency_combo.findData(journal_entry_currency_id))
            currency_combo.currentIndexChanged.connect(lambda checked, r=numRows: self.updateStorageDict(r))
            self.ui.journals_entries_table.setCellWidget(numRows, 4, currency_combo)

            entry_date_picker = QDateEdit()
            entry_date_picker.setDate(QDate.fromString(str(entry_date), Qt.ISODate))
            entry_date_picker.setDisplayFormat("yyyy-MM-dd")
            entry_date_picker.setCalendarPopup(True)
            entry_date_picker.editingFinished.connect(lambda r=numRows: self.updateStorageDict(r))
            self.ui.journals_entries_table.setCellWidget(numRows, 5, entry_date_picker)

        # Add plus button to the new row
        numRows = self.ui.journals_entries_table.rowCount()
        self.ui.journals_entries_table.insertRow(numRows)
        plus_btn = QPushButton("+")
        plus_btn.clicked.connect(self.addEmptyJournalEntry)
        self.ui.journals_entries_table.setCellWidget(numRows, 0, plus_btn)
        self.ui.journals_entries_table.setSpan(numRows, 0, 1, 6)
        
    def addEmptyJournalEntry(self):
        numRows = self.ui.journals_entries_table.rowCount()
        targeted_row = numRows - 1

        # Remove plus button from last row
        self.ui.journals_entries_table.removeRow(targeted_row)
        # Add new row
        self.ui.journals_entries_table.insertRow(targeted_row)

        self.ui.journals_entries_table.setItem(targeted_row, 1, QTableWidgetItem(QDate.currentDate().toString(Qt.ISODate)))
        
        # Create and set up currency combobox
        currency_combo = QComboBox()
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            currency_combo.addItem(currency['name'], currency['id'])
        currency_combo.currentIndexChanged.connect(lambda checked, r=targeted_row: self.updateStorageDict(r))
        self.ui.journals_entries_table.setCellWidget(targeted_row, 4, currency_combo)

        # Create and set up date picker
        entry_date_picker = QDateEdit()
        entry_date_picker.setDisplayFormat("yyyy-MM-dd")
        entry_date_picker.setCalendarPopup(True)
        entry_date_picker.setDate(QDate.currentDate())
        entry_date_picker.editingFinished.connect(lambda r=targeted_row: self.updateStorageDict(r))
        self.ui.journals_entries_table.setCellWidget(targeted_row, 5, entry_date_picker)

        # Store existing entry in temporary storage
        self.temp_journal_entries[targeted_row] = {
            'id': '#',
            'is_new': True,
            'edited': True,
            'deleted': False,
            'date': entry_date_picker.date().toString(Qt.ISODate),
            'entry_date': entry_date_picker.date().toString(Qt.ISODate),
            'currency': currency_combo.currentData(),
            'currency_name': currency_combo.currentText(),
            'items': [],
        }

        # Add plus button to the new row
        self.ui.journals_entries_table.insertRow(targeted_row + 1)
        plus_btn = QPushButton("+")
        plus_btn.clicked.connect(self.addEmptyJournalEntry)
        self.ui.journals_entries_table.setCellWidget(targeted_row + 1, 0, plus_btn)
        self.ui.journals_entries_table.setSpan(targeted_row + 1, 0, 1, 6)
        
    def fetchJournalEntryItems(self):
        self.ui.journal_entries_items_table.setRowCount(0)
        selected_row = self.ui.journals_entries_table.currentRow()

        numRows = self.ui.journals_entries_table.rowCount()
        if selected_row >= 0 and selected_row != numRows - 1:   # Check if the selected journal entry is not the plus button
            entries = []
            # Check if the selected journal entry is edited
            if self.temp_journal_entries[selected_row].get('edited', False):
                # Get entries from temp storage instead of database
                entries = self.temp_journal_entries[selected_row]['items']
            else:
                item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
                journal_entry_id = item.text()
                entries = self.database_operations.fetchJournalEntryItems(journal_entry=journal_entry_id)

            for entry in entries:
                id = entry['id']
                journal_entry_id = entry['journal_entry_id']
                account_id = entry['account_id']
                account_name = entry['account_name']
                statement = entry['statement_col']
                currency = entry['currency']
                currency_name = entry['currency_name']
                opposite_account_id = entry['opposite_account_id']
                opposite_account_name = entry['opposite_account_name']
                type = entry['type_col']
                value = entry['value_col']
                cost_center_id = entry['cost_center_id']

                # Add item to temporary storage if not already present
                if entry not in self.temp_journal_entries.get(selected_row, {}).get('items', []):
                    if selected_row not in self.temp_journal_entries:
                        self.temp_journal_entries[selected_row] = {'items': []}
                    self.temp_journal_entries[selected_row]['items'].append(entry)

                numRows = self.ui.journal_entries_items_table.rowCount()
                self.ui.journal_entries_items_table.insertRow(numRows)

                creditor = ''
                debtor = ''
                if opposite_account_id is None:
                    if str(type).lower() == 'creditor':
                        creditor = account_name
                    elif str(type).lower() == 'debtor':
                        debtor = account_name
                else:
                    if str(type).lower() == 'creditor':
                        creditor = account_name
                        debtor = opposite_account_name
                    elif str(type).lower() == 'debtor':
                        creditor = opposite_account_name
                        debtor = account_name

                self.ui.journal_entries_items_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.journal_entries_items_table.setItem(numRows, 1, QTableWidgetItem(str(journal_entry_id)))
                self.ui.journal_entries_items_table.setItem(numRows, 2, QTableWidgetItem(str(account_id)))
                self.ui.journal_entries_items_table.setItem(numRows, 3, QTableWidgetItem(str(opposite_account_id)))
                self.ui.journal_entries_items_table.setItem(numRows, 4, QTableWidgetItem(str(cost_center_id)))
                self.ui.journal_entries_items_table.setItem(numRows, 5, QTableWidgetItem(str(currency)))
                self.ui.journal_entries_items_table.setItem(numRows, 6, QTableWidgetItem(str(type)))
                self.ui.journal_entries_items_table.setItem(numRows, 7, QTableWidgetItem(str(creditor)))
                self.ui.journal_entries_items_table.setItem(numRows, 8, QTableWidgetItem(str(debtor)))

                self.ui.journal_entries_items_table.setItem(numRows, 9, QTableWidgetItem(str(value)))
                self.ui.journal_entries_items_table.setItem(numRows, 10, QTableWidgetItem(str(currency_name)))
                self.ui.journal_entries_items_table.setItem(numRows, 11, QTableWidgetItem(str(statement)))
                
    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            self.ui.journal_entry_currency_combobox.addItem(display_text, id)

    def deleteJournalEntry(self):
        selected_row = self.ui.journals_entries_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journals_entries_table.item(selected_row, 0)  # Assuming ID is in the first column
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                if item is not None:
                    self.entries_edited = True
                    self.temp_journal_entries[selected_row]['deleted'] = True

                    # Disable the row by making all cells non-editable and non-selectable
                    for col in range(self.ui.journals_entries_table.columnCount()):
                        item = self.ui.journals_entries_table.item(selected_row, col)
                        if item:
                            item.setFlags(item.flags() & ~Qt.ItemIsEnabled & ~Qt.ItemIsSelectable)
                    # Disable currency combobox and date picker for the selected row
                    currency_combobox = self.ui.journals_entries_table.cellWidget(selected_row, 3)
                    if currency_combobox:
                        currency_combobox.setEnabled(False)
                    
                    date_picker = self.ui.journals_entries_table.cellWidget(selected_row, 4) 
                    if date_picker:
                        date_picker.setEnabled(False)
                        
                else:
                    pass
            elif (messagebox_result == IDNO):
                pass

    def deleteJournalEntryItem(self):
        selected_row = self.ui.journal_entries_items_table.currentRow()
        if selected_row >= 0:
            item = self.ui.journal_entries_items_table.item(selected_row, 0)  # Assuming ID is in the first column
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                if item is not None:
                    item_id = item.text()
                    self.database_operations.deleteJournalEntryItem(item_id)
                self.ui.journal_entries_items_table.removeRow(selected_row)
            elif (messagebox_result == IDNO):
                pass

    def save(self, window):

        # Iterate through edited journal entries items
        for row in self.temp_journal_entries:
            if self.temp_journal_entries[row].get('edited'):
                self.entries_edited = True
                total_creditor = 0
                total_debtor = 0
                for item in self.temp_journal_entries[row]['items']:
                    # Get opposite account ID to check if single or double entry
                    opposite_account_id = item.get('opposite_account_id')
                    
                    # Only process single entries (where opposite_account_id is None)
                    if opposite_account_id is None or opposite_account_id == 'None':
                        entry_type = item.get('type_col')
                        entry_value = float(item.get('value_col'))
                        
                        # Add value to appropriate total based on entry type
                        if entry_type == 'creditor':
                            total_creditor += entry_value
                        elif entry_type == 'debtor':
                            total_debtor += entry_value

                # Check if totals match
                if total_creditor != total_debtor:
                    win32api.MessageBox(0, self.language_manager.translate("CREDITOR_DEBTOR_MISMATCH_ERROR"), self.language_manager.translate("ERROR"), 0x40 | 0x0)
                    return False

        if self.entries_edited:
            for row in self.temp_journal_entries:
                journal_entry_id = None

                if self.temp_journal_entries[row].get('deleted'):
                    journal_entry_id = self.temp_journal_entries[row].get('id')
                    if journal_entry_id != '#':
                        self.database_operations.deleteJournalEntry(journal_entry_id)
                    continue

                if self.temp_journal_entries[row].get('edited'):
                    
                    if self.temp_journal_entries[row].get('is_new'):
                        origin_type = 'journal' if self.origin_type == '' else self.origin_type
                        journal_entry_id = self.database_operations.addJournalEntry(self.temp_journal_entries[row].get('entry_date'), self.temp_journal_entries[row].get('currency'), origin_type=origin_type, commit=False)

                    else:
                        journal_entry_id = self.temp_journal_entries[row].get('id')
                        entry_date = self.temp_journal_entries[row].get('entry_date')
                        currency = self.temp_journal_entries[row].get('currency')
                        # Update journal entry date and currency
                        self.database_operations.updateJournalEntry(journal_entry_id, entry_date, currency)
                        # Delete all journal entry items, then re-generate new ones for same journal entry
                        self.database_operations.removeJournalEntriesItems(journal_entry_id, commit=False)

                    # Add new journal entry items
                    for item in self.temp_journal_entries[row]['items']:
                        item_id = item.get('id')
                        account_id = item.get('account_id')
                        opposite_account_id = item.get('opposite_account_id')
                        cost_center_id = item.get('cost_center_id')
                        currency = item.get('currency')
                        type = item.get('type_col')
                        value = item.get('value_col')
                        statement = item.get('statement_col')
                        distributive_cost_center_distributed_values = item.get('distributive_cost_center_distributed_values')

                        if str(opposite_account_id).lower() == 'none':
                            opposite_account_id = None

                        if str(cost_center_id).lower() == 'none':
                            cost_center_id = None
                    
                        if item_id == '#': # Add new journal entry item
                            self.database_operations.addJournalEntryItem(journal_entry_id, currency, type, statement, account_id, opposite_account_id, value, cost_center_id, distributive_cost_center_distributed_values, commit=False)

                        else: # Update existing journal entry item
                            self.database_operations.updateJournalEntryItem(item_id, currency, type, statement, account_id, opposite_account_id, value, cost_center_id, distributive_cost_center_distributed_values, commit=False)

            self.sql_connector.conn.commit()

        window.accept()
