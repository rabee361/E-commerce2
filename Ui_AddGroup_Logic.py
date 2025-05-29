import win32api
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTranslator
from DatabaseOperations import DatabaseOperations
from Ui_AddGroup import Ui_AddGroup
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager

class Ui_AddGroup_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_AddGroup()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)  

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.ui.save_btn.clicked.connect(lambda: self.save())
        self.ui.save_btn.clicked.connect(window.accept)
        self.fetchgroups()
        self.ui.parent_combobox.setEnabled(False)
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())
        
    def fetchgroups(self):
        data = None
        view_name = self.language_manager.translate("NONE")
        self.ui.parent_combobox.addItem(view_name, data)

        groups = self.database_operations.fetchGroups()
        for group in groups:
            id = group['id']
            name = group['name']
            code = group['code']

            data = id
            view_name = code + " - " + name
            self.ui.parent_combobox.addItem(view_name, data)

    def openSelectParentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groups', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def save(self):
        name = self.ui.name_input.text()
        parent_id = self.ui.parent_combobox.itemData(self.ui.parent_combobox.currentIndex())
        if name:
            self.database_operations.addGroup(name, parent_id)
        else:
            win32api.MessageBox(0, self.language_manager.translate("INVALID_DATA"), self.language_manager.translate("ERROR"))
