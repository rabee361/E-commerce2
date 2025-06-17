from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from Ui_DataPicker_Logic import Ui_DataPicker_Logic

from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_SalesCostReport import Ui_SalesCostReport
from LanguageManager import LanguageManager
import datetime

class Ui_SalesCostReport_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector, filemanager=''):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_SalesCostReport()
        self.translator = QTranslator()
        self.filemanager = filemanager
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window_activation):
        self.ui.calculate_btn.clicked.connect(self.showQuantitiesChart)
        self.ui.select_product_btn.clicked.connect(self.openSelectMaterialWindow)
        self.ui.product_combobox.currentIndexChanged.connect(self.showQuantitiesChart)
        self.fechProducts()
        
    def fechProducts(self):
        # Fetch products from database and populate the combobox
        products = self.database_operations.fetchMaterials()
        self.ui.product_combobox.clear()
        if products:
            for product in products:
                self.ui.product_combobox.addItem(product['name'], product['id'])
    
    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials')
        result = data_picker.showUi()
        if result:
            for i in range(self.ui.product_combobox.count()):
                if self.ui.product_combobox.itemData(i)[0] == result['id']:
                    self.ui.product_combobox.setCurrentIndex(i)
                    break
    
    def showQuantitiesChart(self):
        # Clear any existing chart
        if hasattr(self, 'chart_view'):
            self.ui.chart_groupbox.layout().removeWidget(self.chart_view)
            self.chart_view.deleteLater()
        
        # Create chart
        chart = QChart()
        chart.setTitle("Monthly Sales Invoices")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Generate last 6 months as categories
        current_date = datetime.datetime.now()
        months = []
        for i in range(5, -1, -1):
            month_date = current_date - datetime.timedelta(days=30*i)
            months.append(month_date.strftime("%b %Y"))
        
        # Create pseudo data - number of invoices per month
        # In a real implementation, you would fetch this from the database
        selected_product_id = self.ui.product_combobox.currentData()
        
        # Pseudo data - replace with actual database query
        invoice_counts = [12, 18, 15, 22, 25, 20]
        
        # Create line series
        series = QBarSeries()
        bar_set = QBarSet("Number of Invoices")
        for count in invoice_counts:
            bar_set.append(count)
        series.append(bar_set)
        chart.addSeries(series)
        
        # Set up axes
        axis_x = QBarCategoryAxis()
        axis_x.append(months)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        axis_y = QValueAxis()
        axis_y.setRange(0, max(invoice_counts) * 1.2)  # Add some headroom
        axis_y.setTitleText("Number of Invoices")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Create chart view
        self.chart_view = QChartView(chart)
        self.chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Add to layout
        if self.ui.chart_groupbox.layout() is None:
            layout = QVBoxLayout(self.ui.chart_groupbox)
        else:
            layout = self.ui.chart_groupbox.layout()
        
        layout.addWidget(self.chart_view)
        
        # Update chart title with selected product if any
        if selected_product_id:
            product_name = self.ui.product_combobox.currentText()
            chart.setTitle(f"Monthly Sales Invoices - {product_name}")
