from PyQt5.QtWidgets import QDialog

from UiStyles import UiStyles
from DatabaseOperations import DatabaseOperations
from Ui_Configuration import Ui_Configuration
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from manuals.dat_reader import DatReader
from manuals.account_importer import import_accounts


class Ui_Configuration_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.ui = Ui_Configuration()
        self.database_operations = DatabaseOperations(sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.dat_reader = DatReader()

    def showUi(self):
        window_configuration = QDialog()
        self.ui.setupUi(window_configuration)
        self.initialize(window_configuration)
        self.language_manager.load_translated_ui(self.ui, window_configuration)
        window_configuration.exec()

    def initialize(self, window):
        self.fetchManuals()
        self.ui.ok_button.clicked.connect(lambda: self.saveConfiguration(window))

    def fetchManuals(self):
        manuals = self.database_operations.fetchManuals()
        for manual in manuals:
            self.ui.manuals_combobox.addItem(manual[1])

    def saveConfiguration(self, window):
        manual_name = self.ui.manuals_combobox.currentText()
        self.database_operations.saveSetting('selected_manual', manual_name)
        inventory_type = "periodic" if self.ui.periodic_radio.isChecked() else "perpetual"
        self.database_operations.saveSetting('inventory_type', inventory_type)
        
        # Import accounts from the DAT file if available
        try:
            dat_file_path = f'manuals/encrypted/direct_test.dat'
            
            # Import accounts from the DAT file using updated importer
            imported_count = import_accounts(self.sql_connector, dat_file_path)
            print(f"Successfully imported {imported_count} accounts from {dat_file_path}")
        except Exception as e:
            print(f"Error importing accounts: {str(e)}")
        
        window.accept()


