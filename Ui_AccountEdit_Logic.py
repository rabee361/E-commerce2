import win32api
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox

from DatabaseOperations import DatabaseOperations
from Ui_AccountEdit import Ui_AccountEdit
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_AccountEdit_Logic(QDialog):
    def __init__(self, sql_connector, id):
        super().__init__()
        self.id = id
        self.account_type = None
        self.parent_account = None
        self.final_account = None
        self.account_financial_statement = None
        self.account_financial_statement_block = None
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_AccountEdit()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


        # This dictionary will store Ui elements for Financial Statements and its Blocks so we can access them later
        #    Key: financial_statement_id,  Value: financial_statement_blocks_combobox
        self.financial_statements_ui_elements = {}

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.parent_combobox.setDisabled(True)
        self.ui.final_account_combobox.setDisabled(True)
        self.ui.financial_statements_combobox.setDisabled(True)
        self.fetchCostCenters()
        self.fetchAccount()     # Display the already saved info of current account
        self.fetchAccounts()    # To add them to the parent_account combobox
        self.fetchFinancialStatements()
        self.ui.save_btn.clicked.connect(lambda: self.saveAccountInfo(window))
        self.ui.final_account_combobox.currentIndexChanged.connect(lambda: self.enableFinancialStatementsBlocksProperies())
        self.ui.select_parent_account_btn.clicked.connect(lambda: self.openSelectParentAccountWindow(self.ui.parent_combobox))
        self.ui.select_final_account_btn.clicked.connect(lambda: self.openSelectFinalAccountWindow(self.ui.final_account_combobox))
        self.ui.select_financial_statement_btn.clicked.connect(lambda: self.openSelectFinancialStatementWindow(self.ui.financial_statements_combobox))

    def openSelectParentAccountWindow(self, combobox):
        exclusions = []
        excluded_type = 'normal' if self.account_type == 'final' else 'final'
        excluded_accounts = self.database_operations.fetchAccounts(type=excluded_type)
        for account in excluded_accounts:
            exclusions.append(account['id'])
        exclusions.append(int(self.id))
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True, exclusions=exclusions)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openSelectFinalAccountWindow(self, combobox):
        exclusions = []
        excluded_accounts = self.database_operations.fetchAccounts(type='normal')
        for account in excluded_accounts:
            exclusions.append(account['id'])
        exclusions.append(int(self.id))
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', exclusions=exclusions)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openSelectFinancialStatementWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'financial_statements', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def fetchAccounts(self):
        self.ui.parent_combobox.clear()     # Clear previous data
        self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)
        accounts = self.database_operations.fetchAccounts(type=self.account_type)
        for account in accounts:
            if int(account[0]) != int(self.id):  # Exclude the account being edited
                id = account[0]
                name = account[1]
                code = account[2]

                data = id
                view_name = code + " - " + name
                self.ui.parent_combobox.addItem(view_name, data)

        self.ui.final_account_combobox.clear()     # Clear previous data
        final_accounts = self.database_operations.fetchAccounts(type="final")
        for account in final_accounts:
            if account['id'] != self.id:  # Exclude the account being edited
                id = account['id']
                name = account['name']
                code = account['code']

                data = id
                view_name = code + " - " + name
                self.ui.final_account_combobox.addItem(view_name, data)

        self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(self.parent_account))
        ff = self.ui.final_account_combobox.findData(self.final_account)
        self.ui.final_account_combobox.setCurrentIndex(ff)

    def fetchCostCenters(self):
        self.ui.cost_center_combobox.addItem(self.language_manager.translate("NONE"), None)
        cost_centers = self.database_operations.fetchCostCenters()
        for cost_center in cost_centers:
            self.ui.cost_center_combobox.addItem(cost_center['name'], cost_center['id'])

    def fetchAccount(self):
        account = self.database_operations.fetchAccount(self.id)
        id = account['id']
        name = account['name'] 
        code = account['code']
        details = account['details']
        parent_account = account['parent_account']
        date = account['date_col']
        account_type = account['type_col']
        final_account = account['final_account']
        financial_statement = account['financial_statement']
        financial_statement_block = account['financial_statement_block']
        force_cost_center = account['force_cost_center']
        default_cost_center = account['default_cost_center']

        self.parent_account = parent_account
        self.account_type = account_type
        self.final_account = final_account
        self.account_financial_statement = financial_statement
        self.account_financial_statement_block = financial_statement_block

        self.ui.name_input.setText(str(name))
        self.ui.account_code_input.setText(str(code))
        self.ui.details_input.setText("" if str(details).lower() == "none" else str(details))
        self.ui.date_input.setText(str(date))
        self.ui.cost_center_combobox.setCurrentIndex(self.ui.cost_center_combobox.findData(default_cost_center))
        if force_cost_center:
            self.ui.force_cost_center_checkbox.setChecked(True)
        else:
            self.ui.force_cost_center_checkbox.setChecked(False)

    def fetchFinancialStatements(self):
        _translate = QtCore.QCoreApplication.translate

        financial_statements = self.database_operations.fetchFinancialStatements()

        # Add None option for Financial Statement Combobox
        self.ui.financial_statements_combobox.addItem(self.language_manager.translate("NONE"), None)

        for counter, financial_statement in enumerate(financial_statements):
            financial_statement_id = financial_statement[0]
            financial_statement_name = financial_statement[1]

            # Initializing Ui elements:

            # Add Financial Statements to Ui Financial Statement Combobox
            self.ui.financial_statements_combobox.addItem(financial_statement_name, financial_statement_id)

            # Add Financial Statements Blocks to Ui
            # Label
            financial_statement_label = QLabel(self.ui.groupBox_4)
            financial_statement_label.setMaximumSize(QtCore.QSize(100, 16777215))
            financial_statement_label.setObjectName(f"{financial_statement_name}_label")
            financial_statement_label.setText(_translate("AddAccount", f"{financial_statement_name}:"))
            # Combobox
            financial_statement_blocks_combobox = QComboBox(self.ui.groupBox_4)
            financial_statement_blocks_combobox.setDisabled(True)
            financial_statement_blocks_combobox.setObjectName(f"{financial_statement_name}_combobox")

            financial_statement_blocks = self.database_operations.fetchFinancialStatementBlocks(financial_statement_id)
            financial_statement_blocks_combobox.addItem(self.language_manager.translate("NONE"), None)
            if financial_statement_blocks:
                for financial_statement_block in financial_statement_blocks:
                    financial_statement_block_id = financial_statement_block[0]
                    financial_statement_block_name = financial_statement_block[1]

                    financial_statement_blocks_combobox.addItem(financial_statement_block_name, financial_statement_block_id)

            # Add Ui elements
            self.ui.gridLayout_9.addWidget(financial_statement_label, counter, 0, 1, 1)
            self.ui.gridLayout_9.addWidget(financial_statement_blocks_combobox, counter, 2, 1, 1)

            # Save Ui comboboxes
            self.financial_statements_ui_elements[financial_statement_id] = financial_statement_blocks_combobox

        if self.account_type == 'final':
            self.ui.groupBox_7.setVisible(False)    # Hide financial statements blocks groupbox
            self.ui.select_final_account_btn.setDisabled(True)
            self.ui.financial_statements_combobox.setCurrentIndex(self.ui.financial_statements_combobox.findData(self.account_financial_statement))

        if self.account_type == 'normal':
            self.ui.groupBox_4.setVisible(False)    # Hide financial statement groupbox
            id = self.ui.final_account_combobox.currentData()
            final_account_info = self.database_operations.fetchAccount(id) if id else None

            # Get the financial statement that is used by the final account
            if final_account_info:
                final_account_financial_statement = final_account_info[8]
                if final_account_financial_statement is not None:
                    financial_statement_blocks_combobox = self.financial_statements_ui_elements[
                        final_account_financial_statement]
                    financial_statement_blocks_combobox.setEnabled(True)
                    financial_statement_blocks_combobox.setCurrentIndex(financial_statement_blocks_combobox.findData(self.account_financial_statement_block))

    def enableFinancialStatementsBlocksProperies(self):
        # Disable Financial Statements Blocks Comboboxes
        for key, value in self.financial_statements_ui_elements.items():
            value.setDisabled(True)

        final_account = self.ui.final_account_combobox.currentData()
        if str(type(final_account)) == "<class 'NoneType'>":
            pass
        else:
            final_account_info = self.database_operations.fetchAccount(final_account)

            # Get the financial statement that is used by the final account
            final_account_financial_statement = final_account_info[8]
            if final_account_financial_statement is not None:
                financial_statement_blocks_combobox = self.financial_statements_ui_elements[
                    final_account_financial_statement]
                financial_statement_blocks_combobox.setEnabled(True)

    def saveAccountInfo(self, window):
        name = self.ui.name_input.text()
        details = self.ui.details_input.toPlainText()
        code = self.ui.account_code_input.text()
        parent_id = self.ui.parent_combobox.currentData()
        final_account = self.ui.final_account_combobox.currentData()
        financial_statement = ''
        financial_statement_block = ''
        force_cost_center = self.ui.force_cost_center_checkbox.isChecked()
        default_cost_center = self.ui.cost_center_combobox.currentData()

        if force_cost_center and default_cost_center is None:
            win32api.MessageBox(0, self.language_manager.translate("COST_CENTER_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if str(name) == "":
            win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ALERT"))
        else:
            if str(details).lower()=='none':
                details=''
            if str(parent_id).lower()=='none':
                parent_id=''
            if str(final_account).lower()=='none':
                final_account=''
            if str(default_cost_center).lower()=='none':
                default_cost_center=''
            if force_cost_center:
                force_cost_center=1
            else:
                force_cost_center=0

            if self.account_type == 'final':
                financial_statement = self.ui.financial_statements_combobox.currentData()
                if str(type(financial_statement)) == "<class 'NoneType'>":
                    financial_statement = ''
            else:
                if final_account != '':
                    final_account_info = self.database_operations.fetchAccount(final_account)
                    final_account_financial_statement = final_account_info[8]
                    for key, value in self.financial_statements_ui_elements.items():
                        if key == final_account_financial_statement:
                            financial_statement_block = value.currentData()
                            if str(type(financial_statement_block)) == "<class 'NoneType'>":
                                financial_statement_block = ''

            self.database_operations.updateAccount(self.id, name, code, details, parent_id, final_account, financial_statement, financial_statement_block, force_cost_center, default_cost_center)
            window.accept()

