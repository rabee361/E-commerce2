from Ui_Add_Maintenance_Operation import Ui_Add_Maintenance_Operation
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtCore import QDate
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator    

class Ui_Add_Maintenance_Operation_Logic(QDialog):
    def __init__(self, sql_connector,machine_id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.machine_id = machine_id
        self.ui = Ui_Add_Maintenance_Operation()
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui.setupUi(self)
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)
        

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()
        
    def initialize(self ,window):
        self.ui.start_period.setDate(QDate.currentDate())
        self.ui.end_period.setDate(QDate.currentDate())
        self.ui.cost_input.setValidator(QDoubleValidator())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectOppositeAccountWindow())
        self.ui.account_combobox.setEnabled(False)
        self.ui.opposite_account_combobox.setEnabled(False)
        self.ui.save_btn.clicked.connect(lambda: self.addMaintenanceOperation(window))

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.clear()
            self.ui.account_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.account_combobox.setCurrentIndex(0)

    def openSelectOppositeAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.opposite_account_combobox.clear()
            self.ui.opposite_account_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.opposite_account_combobox.setCurrentIndex(0)

    def addMaintenanceOperation(self , window):
        name = self.ui.name_input.text()
        account = self.ui.account_combobox.currentText()
        opposite_account = self.ui.opposite_account_combobox.currentText()
        start_period = self.ui.start_period.text()
        end_period = self.ui.end_period.text()
        cost = self.ui.cost_input.text()
        statment_col = self.ui.notes_input.text()
        self.database_operations.addMaintenanceOperation(name=name, machine_id=self.machine_id, account=account, opposite_account=opposite_account, start_period=start_period, end_period=end_period, cost=cost, statment_col=statment_col)
        window.accept()

