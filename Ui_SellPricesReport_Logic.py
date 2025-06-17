import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt , QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_MaterialMoveReport import Ui_MaterialMoveReport
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color ,black
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32con 
from PyQt5.QtGui import QIcon


class Ui_ProductProfitReport_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_MaterialMoveReport()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_sell_prices_report = QDialog()
        window_sell_prices_report.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window_sell_prices_report.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window_sell_prices_report)
        window_sell_prices_report.setWindowIcon(QIcon('icons/motion_path.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_sell_prices_report)
        window_sell_prices_report.exec()

    def initialize(self):
        self.ui.show_btn.clicked.connect(self.showChart)
        self.fetchChartTypes()
    
    def fetchChartTypes(self):
        chart_types = [
            ("BAR_CHART", "bar"),
            ("LINE_CHART", "line"),
            ("PIE_CHART", "pie"),
            ("SCATTER_PLOT", "scatter"),
            ("AREA_CHART", "area")
        ]
        for label, value in chart_types:
            self.ui.chart_combobox.addItem(self.language_manager.translate(label), value)

    def showChart(self):
        chart_type = self.ui.chart_combobox.currentData()
        self.database_operations.showChart(chart_type)
