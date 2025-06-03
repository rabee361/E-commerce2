from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_DamagedMaterial_Report import Ui_DamagedMaterial_Report
from PyQt5.QtWidgets import  QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class Ui_DamagedMaterial_Report_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_DamagedMaterial_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/hr.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        self.fetchManufactureProcesses()
        self.fetchProducts()
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectProductWindow())
        self.ui.select_manufacture_btn.clicked.connect(lambda: self.openSelectManufactureWindow())

    def fetchManufactureProcesses(self):
        pass

    def fetchProducts():
        pass

    def openSelectProductWindow(self):
        pass

    def openSelectManufactureWindow(self):
        pass
