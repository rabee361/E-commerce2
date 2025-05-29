import win32api
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTranslator
from LanguageManager import LanguageManager
from DatabaseOperations import DatabaseOperations
from Ui_FloatPointSettings import Ui_FloatPointSettings


class Ui_FloatPointSettings_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_FloatPointSettings()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
            
    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.float_point_input.setValidator(QIntValidator())
        self.ui.save_btn.clicked.connect(lambda: self.saveFloatPointValue(window))
        self.fetchFloatPointValue()

    def fetchFloatPointValue(self):
        float_point_value = self.database_operations.fetchFloatPointValue()
        if float_point_value:
            self.ui.float_point_input.setText(str(float_point_value))
        else:
            self.ui.float_point_input.setText("")

    def saveFloatPointValue(self, window):
        float_point = self.ui.float_point_input
        if float_point:
            float_point_value = float_point.text()
            self.database_operations.updateFloatPointValue(float_point_value)  
            window.accept()
        else:
            win32api.MessageBox(0, self.language_manager.translate("FLOAT_POINT_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"), 0x00000010)
            self.ui.float_point_input.setFocus()
