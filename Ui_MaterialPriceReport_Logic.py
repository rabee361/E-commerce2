from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_MaterialPriceReport import Ui_MaterialPriceReport
from LanguageManager import LanguageManager
import datetime

class Ui_MaterialPriceReport_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_MaterialPriceReport()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window_activation):
        # Connect buttons to their respective functions
        self.ui.calc_btn.clicked.connect(self.calculate())
        self.ui.select_material_btn.clicked.connect(self.openSelectMaterialWindow())
        
        # Connect combobox change to show chart automatically
        self.ui.material_combobox.currentIndexChanged.connect()
        
    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            # Find the index where the material ID matches in the combobox
            for i in range(self.ui.material_combobox.count()):
                if self.ui.material_combobox.itemData(i)[0] == result['id']:
                    self.ui.material_combobox.setCurrentIndex(i)
                    break

    def calculate(self):
        pass
