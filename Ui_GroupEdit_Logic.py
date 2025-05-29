import win32api
from PyQt5.QtWidgets import QDialog

from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_GroupEdit import Ui_GroupEdit
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_GroupEdit_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector, id):
        super().__init__()
        self.id = id
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_GroupEdit()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.makeItBlurry(window)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.save_btn.clicked.connect(lambda: self.save())
        self.ui.save_btn.clicked.connect(window.accept)
        self.ui.parent_combobox.setEnabled(False)
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())

        self.fetchGroups() #To add them to the parent_group combobox
        self.fetchGroup() #Display the already saved info of current group

    def fetchGroups(self): #To add them to the parent_group combobox
        data = None
        view_name = self.language_manager.translate("NONE")
        self.ui.parent_combobox.addItem(view_name, data)

        groups = self.database_operations.fetchGroups()
        for group in groups:
            id=group[0]
            name=group[1]
            code=group[2]

            data=id
            text = str(name) + " " + str(code)
            if (int(id) != int(self.id)):
                self.ui.parent_combobox.addItem(text, data)

    def fetchGroup(self):
        group = self.database_operations.fetchGroup(self.id)
        #id = group[0]
        name = group[1]
        #code = group[2]

        parent_group = group[3]
        date = group[4]

        self.ui.name_input.setText(str(name))


        self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(parent_group))
        self.ui.date_input.setText(str(date))

    def openSelectParentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groups', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def save(self):
        name = self.ui.name_input.text()
        parent_id = self.ui.parent_combobox.itemData(self.ui.parent_combobox.currentIndex())
        if name:
            self.database_operations.updateGroup(self.id, name, parent_id)
        else:
            win32api.MessageBox(0, self.language_manager.translate("INVALID_DATA"), self.language_manager.translate("ERROR"))
