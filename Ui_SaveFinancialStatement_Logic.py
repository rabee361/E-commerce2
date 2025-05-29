import sys

import win32api
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_SaveFinancialStatement import Ui_SaveFinancialStatement
from Ui_SelectFinalFinancialStatement_Logic import Ui_SelectFinalFinancialStatement_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_SaveFinancialStatement_Logic(QDialog):
    def __init__(self, sql_connector, financial_statement_id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.final_financial_statement_id = None
        self.financial_statement_id = financial_statement_id
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_SaveFinancialStatement()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        if self.financial_statement_id:    # Editing process
            financial_statement = self.database_operations.fetchFinancialStatement(self.financial_statement_id)
            financial_statement_name = financial_statement[1]
            self.ui.financial_statement_name.setText(financial_statement_name)

        self.fetchFinalFinancialStatement()

        self.ui.save_btn.clicked.connect(lambda: self.saveFinancialStatement(window))
        self.ui.edit_final_financial_statement_btn.clicked.connect(lambda : self.selectFinalFinancialStatement())

    def fetchFinalFinancialStatement(self):
        if self.financial_statement_id:
            financial_statement = self.database_operations.fetchFinancialStatement(self.financial_statement_id)
            final_financial_statement_id = financial_statement[2]
            if final_financial_statement_id:
                final_financial_statement = self.database_operations.fetchFinancialStatement(final_financial_statement_id)
                self.ui.final_financial_statement_name.setText(str(final_financial_statement[1]))
            else:
                self.ui.final_financial_statement_name.setText(str('لا يوجد'))
        else:
            self.ui.final_financial_statement_name.setText(str('لا يوجد'))

    def saveFinancialStatement(self, window):
        financial_statement_name = self.ui.financial_statement_name.text()
        if financial_statement_name:
            if self.financial_statement_id:    # Editing process
                self.database_operations.updateFinancialStatement(self.financial_statement_id, financial_statement_name, self.final_financial_statement_id)
            else:   # Adding process
                self.database_operations.addFinancialStatement(financial_statement_name, self.final_financial_statement_id)
            window.accept()     # Close Ui after completing the process
        else:
            win32api.MessageBox(0, "يرجى ملء الحقل.", "خطأ")

    def selectFinalFinancialStatement(self):
        if self.financial_statement_id:  # Editing process
            final_financial_statement_id, final_financial_statement_name = Ui_SelectFinalFinancialStatement_Logic(self.sql_connector, self.financial_statement_id).showUi()
        else:
            final_financial_statement_id, final_financial_statement_name = Ui_SelectFinalFinancialStatement_Logic(self.sql_connector).showUi()
        if final_financial_statement_id:    # A Final Financial Statement has been selected:
            self.final_financial_statement_id = final_financial_statement_id
            self.ui.final_financial_statement_name.setText(final_financial_statement_name)
        else:
            self.ui.final_financial_statement_name.setText(str('لا يوجد'))

