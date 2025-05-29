import win32api
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView, QTableWidgetItem
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_SelectFinalFinancialStatement import Ui_SelectFinalFinancialStatement
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_SelectFinalFinancialStatement_Logic(QDialog):
    def __init__(self, sql_connector, financial_statement_id=-1):
        super().__init__()
        self.sql_connector = sql_connector
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

        self.financial_statement_id = financial_statement_id    # We will use this to exclude it from the displayed FSs

        # This variables will store the id and name of FFS to be returned then
        self.final_financial_statement_id = None
        self.final_financial_statement_name = None

        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_SelectFinalFinancialStatement()
    
    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()
        return self.final_financial_statement_id, self.final_financial_statement_name  # Return the FFS id and name to the Add/Edit FS Ui

    def initialize(self, window):
        # Initialize Financial Statements Table
        self.ui.financial_statement_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.financial_statement_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.financial_statement_table.verticalHeader().hide()
        self.ui.financial_statement_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.financial_statement_table.setSortingEnabled(True)
        self.ui.financial_statement_table.setColumnHidden(0, True)
        self.ui.financial_statement_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # Link Save button with its respective function
        self.ui.cancel_btn.clicked.connect(lambda : self.cancelSelectionProcess(window))
        self.ui.search_financial_statement_btn.clicked.connect(lambda : self.filterFinancialStatements())
        self.ui.save_final_financial_statement_btn.clicked.connect(lambda : self.selectFinalFinancialStatement(window))

        # Fetch All Financial Statements
        self.fetchFinancialStatements()

    def fetchFinancialStatements(self):
        # clear previous items to prevent duplications
        self.ui.financial_statement_table.clear()
        self.ui.financial_statement_table.setRowCount(0)

        # Fetch All Financial Statements
        financial_statements = self.database_operations.fetchFinancialStatements()

        self.ui.financial_statement_table.insertRow(0)
        self.ui.financial_statement_table.setItem(0, 0, QTableWidgetItem(str(-1)))  # -1 is a unique id for 'None' option
        self.ui.financial_statement_table.setItem(0, 1, QTableWidgetItem(self.language_manager.translate("NONE")))
        # Add Financial Statements to the table
        for financial_statement in financial_statements:
            id = financial_statement[0]

            if str(id) != str(self.financial_statement_id):
                name = financial_statement[1]

                # Create a empty row at bottom of table
                numRows = self.ui.financial_statement_table.rowCount()
                self.ui.financial_statement_table.insertRow(numRows)

                # Add text to the row
                self.ui.financial_statement_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                self.ui.financial_statement_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def filterFinancialStatements(self):
        # clear previous items to prevent duplications
        self.ui.financial_statement_table.clear()
        self.ui.financial_statement_table.setRowCount(0)

        financial_statement_name_input = self.ui.financial_statement_name_input.text()
        financial_statements = self.database_operations.filterFinancialStatements(financial_statement_name_input)
        if financial_statements:
            # Add Financial Statements to the table
            for financial_statement in financial_statements:
                id = financial_statement[0]

                if str(id) != str(self.financial_statement_id):
                    name = financial_statement[1]

                    # Create a empty row at bottom of table
                    numRows = self.ui.financial_statement_table.rowCount()
                    self.ui.financial_statement_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.financial_statement_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.financial_statement_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
        else:
            self.ui.financial_statement_table.insertRow(0)
            self.ui.financial_statement_table.setItem(0, 0, QTableWidgetItem(str(-1)))  # -1 is a unique id for 'None' option
            self.ui.financial_statement_table.setItem(0, 1, QTableWidgetItem(self.language_manager.translate("NONE")))

    def selectFinalFinancialStatement(self, window):
        table_row = self.ui.financial_statement_table.item(self.ui.financial_statement_table.currentRow(), 0)

        if str(type(table_row)) == "<class 'NoneType'>":
            pass
        else:
            selected_financial_statement_id = table_row.text()
            if selected_financial_statement_id != '-1':
                table_row_name = self.ui.financial_statement_table.item(self.ui.financial_statement_table.currentRow(), 1)
                selected_financial_statement_name = table_row_name.text()
                self.final_financial_statement_id = selected_financial_statement_id
                self.final_financial_statement_name = selected_financial_statement_name
            window.accept()

    def cancelSelectionProcess(self, window):
        window.accept()
        return None, None

