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
        # Connect buttons to their respective functions
        self.ui.calc_btn.clicked.connect(self.show_quantities_chart)
        self.ui.select_product_btn.clicked.connect(self.openSelectProductWindow)
        
        # Connect combobox change to show chart automatically
        self.ui.product_combobox.currentIndexChanged.connect(self.show_quantities_chart)
        
        # Load products into combobox
        self.load_products()
        
    def load_products(self):
        # Fetch products from database and populate the combobox
        products = self.database_operations.fetchMaterials()
        self.ui.product_combobox.clear()
        
        for product in products:
            self.ui.product_combobox.addItem(product['name'], product['id'])
    
    def openSelectProductWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.product_combobox.count()):
                if self.ui.product_combobox.itemData(i)[0] == result['id']:
                    self.ui.product_combobox.setCurrentIndex(i)
                    break
    
    def show_quantities_chart(self):
        # Get selected product ID
        product_index = self.ui.product_combobox.currentIndex()
        if product_index < 0:
            return
            
        product_id = self.ui.product_combobox.itemData(product_index)
        product_name = self.ui.product_combobox.itemText(product_index)
        
        # Fetch material quantities from warehouses
        warehouses_data = self.database_operations.fetchMaterialWarehouses(product_id)
        
        # Get material unit
        material_info = self.database_operations.fetchMaterial(product_id)
        material_unit = material_info.get('unit_name', '')
        
        # Create chart
        self.create_chart(warehouses_data, product_name, material_unit)
    
    def create_chart(self, warehouses_data, product_name, material_unit=''):
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
        chart.setTitle(f"{self.language_manager.translate('QUANTITIES_OVER_TIME')}: {product_name}")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create a dictionary to track total quantity by date
        quantities_by_date = {}
        
        # Process data from all warehouses
        for warehouse_id, entries in warehouses_data.items():
            for entry in entries:
                # Get date from either invoice_date or manufacture_date
                entry_date = None
                if entry.get('invoice_date'):
                    entry_date = entry['invoice_date']
                elif entry.get('manufacture_date'):
                    entry_date = entry['manufacture_date']
                
                if entry_date:
                    # Convert to datetime if it's a string
                    if isinstance(entry_date, str):
                        try:
                            entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d %H:%M:%S')
                        except ValueError:
                            try:
                                entry_date = datetime.datetime.strptime(entry_date, '%Y-%m-%d')
                            except ValueError:
                                continue
                    
                    # Format date as string for dictionary key
                    date_key = entry_date.strftime('%Y-%m-%d')
                    
                    # Add quantity to total for this date
                    if date_key not in quantities_by_date:
                        quantities_by_date[date_key] = 0
                    
                    # Add the quantity (assuming it's in the 'quantity' field)
                    quantity = float(entry.get('quantity', 0))
                    quantities_by_date[date_key] += quantity
        
        # Sort dates and calculate quantities
        sorted_dates = sorted(quantities_by_date.keys())
        
        # No data to display
        if not sorted_dates:
            return
            
        # Create a bar set for the chart
        bar_set = QBarSet(product_name)
        
        # Create a list to store all dates including those with no movements
        # This ensures we have consistent bars even on days with no activity
        if len(sorted_dates) > 1:
            start_date = datetime.datetime.strptime(sorted_dates[0], '%Y-%m-%d')
            end_date = datetime.datetime.strptime(sorted_dates[-1], '%Y-%m-%d')
            date_range = []
            
            # Generate all dates in the range
            current_date = start_date
            while current_date <= end_date:
                date_range.append(current_date.strftime('%Y-%m-%d'))
                current_date += datetime.timedelta(days=1)
                
            # Use the complete date range instead of just dates with movements
            sorted_dates = date_range
        
        # Calculate cumulative quantities for all dates
        cumulative_quantity = 0
        date_to_quantity = {}
        
        # First pass: calculate cumulative quantities for dates with movements
        for date_str in sorted(quantities_by_date.keys()):
            cumulative_quantity += quantities_by_date[date_str]
            date_to_quantity[date_str] = cumulative_quantity
        
        # Second pass: fill in all dates in our range with the appropriate cumulative value
        for date_str in sorted_dates:
            # If this date had a movement, we already have its value
            if date_str in date_to_quantity:
                bar_set.append(date_to_quantity[date_str])
            else:
                # For dates with no movement, find the most recent previous date with a value
                previous_dates = [d for d in sorted(date_to_quantity.keys()) if d < date_str]
                
                if previous_dates:
                    # Use the most recent previous date's value
                    most_recent = max(previous_dates)
                    bar_set.append(date_to_quantity[most_recent])
                else:
                    # If no previous date, start at 0
                    bar_set.append(0)
        
        # Create bar series and add the bar set
        series = QBarSeries()
        series.append(bar_set)
        
        # Add series to chart
        chart.addSeries(series)
        
        # Set up the axes
        axisX = QBarCategoryAxis()
        axisX.append(sorted_dates)
        axisX.setTitleText(self.language_manager.translate("DATE"))
        chart.addAxis(axisX, Qt.AlignBottom)
        series.attachAxis(axisX)
        
        axisY = QValueAxis()
        axisY.setLabelFormat("%.2f")
        
        # Set Y-axis title to include the material's unit
        if material_unit:
            axisY.setTitleText(f"{self.language_manager.translate('AMOUNT')} ({material_unit})")
        else:
            axisY.setTitleText(self.language_manager.translate("AMOUNT"))
            
        chart.addAxis(axisY, Qt.AlignLeft)
        series.attachAxis(axisY)
        
        # Create chart view
        chartView = QChartView(chart)
        chartView.setRenderHint(QPainter.Antialiasing)
        
        # Add chart view to layout
        self.ui.chart_groupbox.layout().addWidget(chartView)
