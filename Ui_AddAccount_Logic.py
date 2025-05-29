import win32api
from PyQt5 import QtCore, Qt
from PyQt5.QtWidgets import QDialog, QLabel, QComboBox
from PyQt5.QtGui import QDoubleValidator
from DatabaseOperations import DatabaseOperations
from Ui_AddAccount import Ui_AddAccount
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_AddAccount_Logic(QDialog):
    def __init__(self, sql_connector, parent_account_id=None, parent_account_name=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_AddAccount()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


        # This dictionary will store Ui elements for Financial Statements and its Blocks so we can access them later
        #    Key: financial_statement_id,  Value: financial_statement_blocks_combobox
        self.financial_statements_ui_elements = {}

        # If the account is added as a child of another account, we need to know the parent account id
        self.parent_account_id = parent_account_id
        self.parent_account_name = parent_account_name


    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.setAccountTypes()
        self.fetchCostCenters()
        # self.fetchAccounts()  # No need to do this anymore
        self.fetchFinancialStatements()
        self.ui.budget_exchange_input.setValidator(QDoubleValidator())
        self.ui.budget_value_input.setValidator(QDoubleValidator())
        self.ui.tax_default_value_input.setValidator(QDoubleValidator())
        self.ui.save_btn.clicked.connect(lambda: self.save(window))
        self.ui.account_type_combobox.currentIndexChanged.connect(lambda: self.enableFinalAccountProperties())

        self.ui.select_parent_account_btn.clicked.connect(lambda: self.openSelectParentAccountWindow())
        self.ui.select_final_account_btn.clicked.connect(lambda: self.openSelectFinalAccountWindow())

        # Parent account is None by default
        self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.parent_combobox.setCurrentIndex(0)

        self.ui.financial_statements_combobox.setDisabled(True)
        self.ui.select_financial_statement_btn.setDisabled(True)
        self.ui.select_financial_statement_btn.clicked.connect(lambda: self.openSelectFinancialStatementWindow())

        if self.parent_account_id:
            self.ui.parent_combobox.clear()
            self.ui.parent_combobox.addItem(self.parent_account_name, self.parent_account_id)
            self.ui.parent_combobox.setCurrentIndex(0)

            self.enableFinalAccountSuggestion()

    def fetchCostCenters(self):
        self.ui.cost_center_combobox.addItem(self.language_manager.translate("NONE"), None)
        cost_centers = self.database_operations.fetchCostCenters()
        for cost_center in cost_centers:
            self.ui.cost_center_combobox.addItem(cost_center['name'], cost_center['id'])

    def openSelectParentAccountWindow(self):
        account_type = self.ui.account_type_combobox.currentData()

        # Create a list of excluded accounts
        excluded_accounts_type = 'normal' if account_type == 'final' else 'final'
        excluded_accounts = self.database_operations.fetchAccounts(type=excluded_accounts_type)
        excluded_accounts_ids = [account[0] for account in excluded_accounts]   # List contains ids only

        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True,
                                          exclusions=excluded_accounts_ids)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.clear()
            self.ui.parent_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.parent_combobox.setCurrentIndex(0)

            self.enableFinalAccountSuggestion()

    def openSelectFinalAccountWindow(self):
        # Create a list of excluded accounts
        excluded_accounts_type = 'normal'
        excluded_accounts = self.database_operations.fetchAccounts(type=excluded_accounts_type)
        excluded_accounts_ids = [account[0] for account in excluded_accounts]   # List contains ids only
    
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', exclusions=excluded_accounts_ids)
        result = data_picker.showUi()
        if result is not None:
            self.ui.final_account_combobox.clear()
            self.ui.final_account_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.final_account_combobox.setCurrentIndex(0)

            self.enableFinancialStatementsBlocksProperties()

    def openSelectFinancialStatementWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'financial_statements', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.financial_statements_combobox.setCurrentIndex(self.ui.financial_statements_combobox.findData(result['id']))

    def setAccountTypes(self):
        accounts_types = {self.language_manager.translate("NORMAL"): "normal", self.language_manager.translate("FINAL"): "final"}
        for key, value in accounts_types.items():
            self.ui.account_type_combobox.addItem(key, value)

    def enableFinalAccountProperties(self):
        account_type = self.ui.account_type_combobox.currentData()
        if str(account_type).lower() == 'final':
            self.ui.final_account_combobox.clear()
            self.ui.final_account_combobox.addItem(self.language_manager.translate("NONE"), None)
            self.ui.final_account_combobox.setCurrentIndex(0)
            self.ui.select_final_account_btn.setDisabled(True)
            self.ui.select_financial_statement_btn.setEnabled(True)
        else:
            self.ui.select_final_account_btn.setEnabled(True)
            self.ui.select_financial_statement_btn.setDisabled(True)

        # Reset parent account combobox
        self.ui.parent_combobox.clear()

    def enableFinalAccountSuggestion(self):
        parent_id = self.ui.parent_combobox.currentData()
        if str(type(parent_id)) == "<class 'NoneType'>":
            self.ui.final_account_combobox.clear()
            self.ui.final_account_combobox.addItem(self.language_manager.translate("NONE"), None)
            self.ui.final_account_combobox.setCurrentIndex(0)
        else:
            account_type = self.ui.account_type_combobox.currentData()
            if str(account_type).lower() == 'normal':  # Only normal accounts can choose a final account
                # Get the final account used by the parent
                parent_account = self.database_operations.fetchAccount(parent_id)
                final_account_id = parent_account[7]
                if final_account_id:
                    final_account = self.database_operations.fetchAccount(final_account_id)
                    final_account_name = final_account[1]
                    self.ui.final_account_combobox.clear()
                    self.ui.final_account_combobox.addItem(final_account_name, final_account_id)
                    self.ui.final_account_combobox.setCurrentIndex(0)

    def enableFinancialStatementsBlocksProperties(self):
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

    def save(self, window):
        name = self.ui.name_input.text()
        details = self.ui.details_input.toPlainText()
        parent_id = self.ui.parent_combobox.currentData()
        final_account = self.ui.final_account_combobox.currentData()
        account_type = self.ui.account_type_combobox.currentData()
        financial_statement = self.ui.financial_statements_combobox.currentData()
        financial_statement_block = ''

        force_cost_center = self.ui.force_cost_center_checkbox.isChecked()
        cost_center = self.ui.cost_center_combobox.currentData()

        if str(name) == "":
            win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ALERT"))
        else:

            if str(details).lower() == 'none':
                details = ''
            if str(parent_id).lower() == 'none':
                parent_id = ''
            if str(financial_statement).lower() == 'none':
                financial_statement = ''
            if str(final_account).lower() == 'none':
                final_account = ''
            if str(cost_center).lower() == 'none':
                cost_center = ''
                
            else:
                if final_account:
                    final_account_info = self.database_operations.fetchAccount(final_account)
                    final_account_financial_statement = final_account_info[8]
                    for key, value in self.financial_statements_ui_elements.items():
                        if key == final_account_financial_statement:
                            financial_statement_block = value.currentData()
                            if str(type(financial_statement_block)) == "<class 'NoneType'>":
                                financial_statement_block = ''

            if final_account or (str(account_type) == 'final'):
                new_account_id = self.database_operations.addAccount(name, details, parent_id, account_type,final_account, financial_statement, financial_statement_block, force_cost_center, cost_center)
                window.accept()

            else:
                message = self.language_manager.translate("FINAL_ACCOUNT_MUST_BE_SELECTED")
                win32api.MessageBox(0, message, self.language_manager.translate("ALERT"))

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

                    financial_statement_blocks_combobox.addItem(financial_statement_block_name,
                                                                financial_statement_block_id)

            # Add Ui elements
            self.ui.gridLayout_9.addWidget(financial_statement_label, counter, 0, 1, 1)
            self.ui.gridLayout_9.addWidget(financial_statement_blocks_combobox, counter, 2, 1, 1)

            # Save Ui comboboxes
            self.financial_statements_ui_elements[financial_statement_id] = financial_statement_blocks_combobox
