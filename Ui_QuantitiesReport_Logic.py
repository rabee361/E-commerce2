from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtWidgets import QDialog, QVBoxLayout
from PyQt5.QtCore import QCoreApplication, QTranslator
from PyQt5.QtGui import QPainter
from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
from Ui_DataPicker_Logic import Ui_DataPicker_Logic

from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_QuantitiesReport import Ui_QuantitiesReport
from LanguageManager import LanguageManager
import datetime

class Ui_QuantitiesReport_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_QuantitiesReport()
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
        self.ui.calculate_btn.clicked.connect(self.showQuantitiesChart)
        self.ui.select_product_btn.clicked.connect(self.openSelectMaterialWindow)
        self.ui.product_combobox.currentIndexChanged.connect(self.showQuantitiesChart)
        self.fechProducts()
        
    def fechProducts(self):
        # Fetch products from database and populate the combobox
        products = self.database_operations.fetchMaterials()
        self.ui.product_combobox.clear()
        
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
        product_index = self.ui.product_combobox.currentIndex()
        if product_index < 0:
            return
        
        product_id = self.ui.product_combobox.itemData(product_index)
        product_name = self.ui.product_combobox.itemText(product_index)
        
        # Fetch warehouses containing this material
        warehouses_data = self.database_operations.fetchMaterialWarehouses(product_id)
        
        material_info = self.database_operations.fetchMaterial(product_id)
        material_unit = material_info.get('unit_name', '')
        
        # Create chart
        self.create_warehouse_chart(warehouses_data, product_name, material_unit)

    def create_warehouse_chart(self, warehouses_data, product_name, material_unit=''):
        # Clear previous chart if any
        if self.ui.chart_groupbox.layout():
            # Clear previous layout
            while self.ui.chart_groupbox.layout().count():
                item = self.ui.chart_groupbox.layout().takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
        else:
            # Create layout if it doesn't exist
            self.ui.chart_groupbox.setLayout(QVBoxLayout())
        
        # Create chart
        chart = QChart()
        chart.setTitle(f"{self.language_manager.translate('QUANTITIES_BY_WAREHOUSE')}: {product_name}")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create a bar set for the chart
        bar_set = QBarSet(product_name)
        
        # Create lists to store warehouse names and their quantities
        warehouse_names = []
        warehouse_quantities = {}
        
        # Process data from all warehouses if available
        if warehouses_data:
            for warehouse_id, items in warehouses_data.items():
                if not items:
                    continue
                
                # Get warehouse name from the first item
                warehouse_name = items[0].get('warehouse_name', f'Warehouse {warehouse_id}')
                warehouse_names.append(warehouse_name)
                
                # Calculate total quantity for this warehouse
                total_quantity = sum(float(item.get('quantity', 0)) for item in items)
                warehouse_quantities[warehouse_name] = total_quantity
        
            # Sort warehouse names for consistent display
            warehouse_names.sort()
        
        # If no warehouse names, add a placeholder to show empty chart
        if not warehouse_names:
            warehouse_names = [""]
        
        # Add quantities to bar set in the same order as warehouse names
        for name in warehouse_names:
            bar_set.append(warehouse_quantities.get(name, 0))
        
        # Create bar series and add the bar set
        series = QBarSeries()
        series.append(bar_set)
        
        # Add series to chart
        chart.addSeries(series)
        
        # Set up the axes
        axisX = QBarCategoryAxis()
        axisX.append(warehouse_names)
        axisX.setTitleText(self.language_manager.translate("WAREHOUSE"))
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        
        axisY = QValueAxis()
        axisY.setLabelFormat("%.2f")
        
        # Set Y-axis title to include the material's unit
        if material_unit:
            axisY.setTitleText(f"{self.language_manager.translate('QUANTITY')} ({material_unit})")
        else:
            axisY.setTitleText(self.language_manager.translate("QUANTITY"))
        
        # Set a reasonable range for Y-axis even when no data
        if not warehouses_data or all(q == 0 for q in warehouse_quantities.values()):
            axisY.setRange(0, 10)  # Default range when no data
        
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        
        # Create chart view
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        # Add chart view to layout
        self.ui.chart_groupbox.layout().addWidget(chartView)
