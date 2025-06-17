from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QHeaderView, QTreeWidgetItem

import win32api

from win32con import IDYES, MB_YESNO

from DatabaseOperations import DatabaseOperations
from Ui_FinancialStatements import Ui_FinancialStatements
from Ui_AddEditFinancialStatement_Logic import Ui_SaveFinancialStatement_Logic
from Ui_EditFinancialStatementBlock_Logic import Ui_EditFinancialStatementBlock_Logic

from MyTableWidgetItem import MyTableWidgetItem
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_FinancialStatements_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_FinancialStatements()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        # Initialize Financial Statements Tree
        self.ui.financial_statements_tree.hideColumn(1)
        self.ui.financial_statements_tree.setSortingEnabled(True)

        # Initialize Financial Statement Blocks Table
        self.ui.financial_statement_blocks_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.financial_statement_blocks_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.financial_statement_blocks_table.verticalHeader().hide()
        self.ui.financial_statement_blocks_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.financial_statement_blocks_table.setSortingEnabled(True)
        self.ui.financial_statement_blocks_table.setColumnHidden(0, True)
        self.ui.financial_statement_blocks_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Link buttons with their respective functions
        self.ui.add_financial_statement_btn.clicked.connect(lambda: self.addFinancialStatement())
        self.ui.edit_financial_statement_btn.clicked.connect(lambda: self.updateFinancialStatement())
        self.ui.delete_financial_statement_btn.clicked.connect(lambda : self.removeFinancialStatement())
        self.ui.add_financial_statement_block_btn.clicked.connect(lambda : self.addFinancialStatementBlock())
        self.ui.edit_financial_statement_block_btn.clicked.connect(lambda : self.updateFinancialStatementBlock())
        self.ui.delete_financial_statement_block_btn.clicked.connect(lambda : self.removeFinancialStatementBlock())

        # Update Final Financial Statement and Financial Statement Blocks when a financial statement is selected from the table.
        self.ui.financial_statements_tree.itemClicked.connect(lambda: self.fetchFinancialStatementBlocks())

        # Fetch All Financial Statements
        self.fetchFinancialStatements()

    def fetchFinancialStatements(self):
        # clear previous items to prevent duplications
        self.ui.financial_statements_tree.clear()

        # Fetch All Financial Statements
        financial_statements = self.database_operations.fetchFinancialStatements()
        # Add Financial Statements to the table
        for financial_statement in financial_statements:
            financial_statement_id = financial_statement[0]
            financial_statement_name = financial_statement[1]
            final_financial_statement_id = financial_statement[2]

            if final_financial_statement_id:
                final_financial_statement = self.database_operations.fetchFinancialStatement(final_financial_statement_id)
                final_financial_statement_id = final_financial_statement[0]
                final_financial_statement_name = final_financial_statement[1]

                items_already_in_tree = self.ui.financial_statements_tree.findItems(str(final_financial_statement_id), Qt.MatchExactly | Qt.MatchRecursive, 1)
                if len(items_already_in_tree) > 0:
                    # Check if the financial statement is already exists, otherwise create it
                    item_already_in_tree = self.ui.financial_statements_tree.findItems(str(financial_statement_id), Qt.MatchExactly | Qt.MatchRecursive, 1)
                    if len(item_already_in_tree) > 0:
                        self.ui.financial_statements_tree.takeTopLevelItem(self.ui.financial_statements_tree.indexOfTopLevelItem(item_already_in_tree[0]))
                        items_already_in_tree[0].addChild(item_already_in_tree[0])
                    else:
                        items_already_in_tree[0].addChild(QTreeWidgetItem([str(financial_statement_name), str(financial_statement_id)]))
                else:
                    item = QTreeWidgetItem([str(final_financial_statement_name), str(final_financial_statement_id)])
                    self.ui.financial_statements_tree.addTopLevelItem(item)
                    items_already_in_tree = self.ui.financial_statements_tree.findItems(str(financial_statement_id), Qt.MatchExactly | Qt.MatchRecursive, 1)
                    if len(items_already_in_tree) > 0:
                        self.ui.financial_statements_tree.takeTopLevelItem(self.ui.financial_statements_tree.indexOfTopLevelItem(items_already_in_tree[0]))
                        item.addChild(items_already_in_tree[0])
                    else:
                        item.addChild(QTreeWidgetItem([str(financial_statement_name), str(financial_statement_id)]))
            else:
                items_already_in_tree = self.ui.financial_statements_tree.findItems(str(financial_statement_id), Qt.MatchExactly | Qt.MatchRecursive, 1)
                if len(items_already_in_tree) == 0:
                    item = QTreeWidgetItem([str(financial_statement_name), str(financial_statement_id)])
                    self.ui.financial_statements_tree.addTopLevelItem(item)

    def fetchFinancialStatementBlocks(self):
        # clear previous items to prevent duplications
        # self.ui.financial_statement_blocks_table.clear()
        self.ui.financial_statement_blocks_table.setRowCount(0)

        selected_financial_statement = self.ui.financial_statements_tree.currentItem()

        if str(type(selected_financial_statement)) == "<class 'NoneType'>":
            pass
        else:
            financial_statement_id = selected_financial_statement.text(1)
            financial_statement_blocks = self.database_operations.fetchFinancialStatementBlocks(financial_statement_id)

            for financial_statement_block in financial_statement_blocks:
                id = financial_statement_block[0]
                name = financial_statement_block[1]

                # Create an empty row at bottom of table
                numRows = self.ui.financial_statement_blocks_table.rowCount()
                self.ui.financial_statement_blocks_table.insertRow(numRows)

                # Add text to the row
                self.ui.financial_statement_blocks_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                self.ui.financial_statement_blocks_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def addFinancialStatement(self):
        Ui_SaveFinancialStatement_Logic(self.sql_connector).showUi()
        self.fetchFinancialStatements()

    def addFinancialStatementBlock(self):
        selected_financial_statement = self.ui.financial_statements_tree.currentItem()

        if str(type(selected_financial_statement)) == "<class 'NoneType'>":
            pass
        else:
            financial_statement_id = selected_financial_statement.text(1)
            financial_statement_block_name = self.ui.block_name.text()
            if financial_statement_block_name:
                self.database_operations.addFinancialStatementBlock(financial_statement_id, financial_statement_block_name)
                self.fetchFinancialStatementBlocks()
                self.ui.block_name.clear()
            else:
                win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))

    def updateFinancialStatement(self):
        selected_financial_statement = self.ui.financial_statements_tree.currentItem()

        if str(type(selected_financial_statement)) == "<class 'NoneType'>":
            pass
        else:
            financial_statement_id = selected_financial_statement.text(1)
            Ui_SaveFinancialStatement_Logic(self.sql_connector, financial_statement_id).showUi()
            self.fetchFinancialStatements()

    def updateFinancialStatementBlock(self):
        table_row = self.ui.financial_statement_blocks_table.item(self.ui.financial_statement_blocks_table.currentRow(), 0)

        if str(type(table_row)) == "<class 'NoneType'>":
            pass
        else:
            financial_statement_block_id = self.ui.financial_statement_blocks_table.item(self.ui.financial_statement_blocks_table.currentRow(), 0).text()
            financial_statement_block_name = self.ui.financial_statement_blocks_table.item(self.ui.financial_statement_blocks_table.currentRow(), 1).text()

            Ui_EditFinancialStatementBlock_Logic(self.sql_connector, financial_statement_block_id, financial_statement_block_name).showUi()
            self.fetchFinancialStatementBlocks()

    def removeFinancialStatement(self):
        selected_financial_statement = self.ui.financial_statements_tree.currentItem()

        if str(type(selected_financial_statement)) == "<class 'NoneType'>":
            pass
        else:
            response = win32api.MessageBox(0, "Are you sure you want to delete this financial statement?", "Confirmation", MB_YESNO)
            if response == IDYES:  # Using win32con.MB_YES for 'Yes' response
                financial_statement_id = selected_financial_statement.text(1)
                deleted = self.database_operations.removeFinancialStatement(financial_statement_id)
                if deleted:
                    self.fetchFinancialStatements()
                    self.fetchFinancialStatementBlocks()
                else:
                    win32api.MessageBox(0, self.language_manager.translate("FINANCIAL_STATEMENT_DELETE_ERROR"), self.language_manager.translate("ERROR"))

    def removeFinancialStatementBlock(self):
        table_row = self.ui.financial_statement_blocks_table.item(self.ui.financial_statement_blocks_table.currentRow(), 0)

        if str(type(table_row)) == "<class 'NoneType'>":
            pass
        else:
            response = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("CONFIRM"), MB_YESNO)
            if response == IDYES:  # Using win32con.MB_YES for 'Yes' response
                financial_statement_block_id = table_row.text()
                self.database_operations.removeFinancialStatementBlock(financial_statement_block_id)
                self.fetchFinancialStatementBlocks()

