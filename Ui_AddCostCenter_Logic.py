from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_AddCostCenter import Ui_AddCostCenter
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_AddCostCenter_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AddCostCenter()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.addCostCenterTypes()
        self.fetchCostCenters()
        self.setParentComboboxState()
        self.ui.parent_combobox.setEnabled(False)
        self.ui.save_btn.clicked.connect(lambda: self.save(window))
        self.ui.type_combobox.currentIndexChanged.connect(lambda: self.setParentComboboxState())
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())

    def addCostCenterTypes(self):
        self.ui.type_combobox.addItem(self.language_manager.translate("NORMAL"), "normal")
        self.ui.type_combobox.addItem(self.language_manager.translate("AGGREGATOR"), "aggregator")
        self.ui.type_combobox.addItem(self.language_manager.translate("DISTRIBUTOR"), "distributor")

    def openSelectParentWindow(self):
        exclusions = []
        cost_centers = self.database_operations.fetchCostCenters(cost_center_type=['distributor', 'aggregator'])
        for cost_center in cost_centers:
            exclusions.append(cost_center[0])
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True, exclusions=exclusions)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def fetchCostCenters(self):
        self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)
        cost_centers = self.database_operations.fetchCostCenters()
        for cost_center in cost_centers:
            id = cost_center[0]
            name = cost_center[1]
            data = id
            self.ui.parent_combobox.addItem(name, data)

    def setParentComboboxState(self):
        type = self.ui.type_combobox.currentText()
        if type == self.language_manager.translate("NORMAL"):
            self.ui.select_parent_btn.setDisabled(False)
        else:
            self.ui.parent_combobox.setCurrentIndex(0)
            self.ui.select_parent_btn.setDisabled(True)

    def save(self, window):
        name = self.ui.name_input.text()
        notes = self.ui.notes_input.text()
        type = self.ui.type_combobox.currentData()
        parent = self.ui.parent_combobox.currentData()

        if str(name).strip():
            self.database_operations.addCostCenter(name, notes, type, parent)
            window.accept()