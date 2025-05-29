import win32api
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_EditFinancialStatementBlock import Ui_EditFinancialStatementBlock
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_EditFinancialStatementBlock_Logic(QDialog):
    def __init__(self, sql_connector, financial_statement_block_id, financial_statement_block_name):
        super().__init__()
        self.sql_connector = sql_connector
        self.financial_statement_block_id = financial_statement_block_id
        self.financial_statement_block_name = financial_statement_block_name
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_EditFinancialStatementBlock()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.block_name.setText(self.financial_statement_block_name)

        self.ui.save_btn.clicked.connect(lambda : self.updateFinancialStatementBlock(window))


    def updateFinancialStatementBlock(self, window):
        name = self.ui.block_name.text()

        if name:
            self.database_operations.updateFinancialStatementBlock(self.financial_statement_block_id, name)
            window.accept()     # Close Ui after completing the process
        else:
            win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))