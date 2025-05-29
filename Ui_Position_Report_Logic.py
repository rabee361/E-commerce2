import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Position_Report import Ui_Position_Report
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog, QVBoxLayout
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color, black
from PyQt5.QtGui import QPalette
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32con 
from PyQt5.QtGui import QIcon
from PyQt5.QtChart import QChart, QChartView, QBarSet, QBarSeries, QValueAxis, QBarCategoryAxis, QLineSeries, QDateTimeAxis
from PyQt5.QtCore import Qt, QDateTime, QDate
from collections import defaultdict


class Ui_Position_Report_Logic(object):
    def __init__(self, sqlconnector, position_id=None):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Position_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.position_id = position_id

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
        self.ui.from_date.setDate(QDate.currentDate())
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.select_position_btn.clicked.connect(lambda: self.openSelectPositionWindow())
        self.fetchPositions()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.fetchAvgSalary()
        self.fetchPositionInfo()
        self.fetchEmployeeNum()
        self.fetchSalaryChange()
        
    def openSelectPositionWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'positions')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.position_combobox.count()):
                if self.ui.position_combobox.itemData(i)[0] == result['id']:
                    self.ui.position_combobox.setCurrentIndex(i)
                    break

    def fetchPositions(self):
        positions = self.database_operations.fetchPositions()
        for position in positions:
            id = position[0]
            name = position[1]
            self.ui.position_combobox.addItem(name, id)

    def fetchAvgSalary(self):
        # Get position filter if selected
        position = ''
        if hasattr(self, 'position_id') and self.position_id:
            position = self.position_id
        elif self.ui.position_combobox.currentData():
            position = self.ui.position_combobox.currentData()
        
        # Get date range if specified
        from_date = self.ui.from_date.date().toString('yyyy-MM-dd') if self.ui.from_date.date() else ''
        to_date = self.ui.to_date.date().toString('yyyy-MM-dd') if self.ui.to_date.date() else ''
        
        # Fetch payroll details with filters
        payrolls = self.database_operations.fetchPayrollsDetails(from_date, to_date, position)
        
        # Group payrolls by salary block and calculate average salary for each block
        salary_blocks = defaultdict(list)
        for payroll in payrolls:
            # Assuming salary is in a specific column index, adjust if needed
            # Based on the query, we need to extract the salary value and block dates
            salary_block_id = payroll['salary_block_id']  # Assuming salary_block_id is at index 1
            salary = payroll['value_col']  # Assuming salary amount is at index 4
            from_date = payroll['from_date']  # Based on the query, from_date is 3rd from the end
            to_date = payroll['to_date']    # Based on the query, to_date is 2nd from the end
            
            # Create a key with from_date and to_date
            block_key = f"{from_date} to {to_date}"
            
            # Skip if salary is None or not a number
            if salary is not None and isinstance(salary, (int, float)):
                salary_blocks[block_key].append(salary)
        
        # Calculate average for each block
        avg_salaries = {}
        for block, salaries in salary_blocks.items():
            if salaries:  # Check if there are any salaries in this block
                avg_salaries[block] = sum(salaries) / len(salaries)
        
        # Create the chart
        self.createSalaryBarChart(avg_salaries)
    
    def createSalaryBarChart(self, avg_salaries):
        # Clear any existing layout in the chart groupbox
        if self.ui.avg_salary_chart.layout():
            # Clear old layout
            old_layout = self.ui.avg_salary_chart.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # We don't call setLayout(None) as it can cause issues
            # Instead, we'll create a new layout and replace the old one
        
        # Create a new layout
        layout = QVBoxLayout(self.ui.avg_salary_chart)
        
        # Create chart if we have data
        if not avg_salaries:
            # No data available
            self.ui.avg_salary_chart.setTitle("No salary data available")
            return
        
        # Create bar set for the chart
        bar_set = QBarSet("Average Salary")
        
        # Sort the blocks by date (assuming format is consistent)
        sorted_blocks = sorted(avg_salaries.keys())
        
        # Add data to the bar set
        for block in sorted_blocks:
            bar_set.append(avg_salaries[block])
        
        # Create bar series and add the bar set
        series = QBarSeries()
        series.append(bar_set)
        
        # Create the chart and add the series
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Average Salary by Pay Period")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create category axis for X axis (salary block dates)
        axis_x = QBarCategoryAxis()
        axis_x.append(sorted_blocks)
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Create value axis for Y axis (salary amounts)
        axis_y = QValueAxis()
        max_salary = max(avg_salaries.values()) if avg_salaries else 0
        axis_y.setRange(0, max_salary * 1.1)  # Add 10% margin at the top
        axis_y.setTitleText("Average Salary")
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Set legend visibility and position
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Create chart view and add to layout
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Add the chart view to the layout
        layout.addWidget(chart_view)
        
        # Set the layout to the groupbox
        self.ui.avg_salary_chart.setLayout(layout)
        
    def fetchPositionInfo(self):
        pass
        
    def fetchEmployeeNum(self):
        # Get position filter if selected
        position_id = ''
        if hasattr(self, 'position_id') and self.position_id:
            position_id = self.position_id
        elif self.ui.position_combobox.currentData():
            position_id = self.ui.position_combobox.currentData()
            
        # Fetch employees for the selected position
        employees = self.database_operations.fetchEmployees(position_id=position_id)
        
        # Create a timeline chart of employee count
        self.createEmployeeTimelineChart(employees)
        
    def fetchSalaryChange(self):
        pass

    def calculate(self):
        self.fetchAvgSalary()
        self.fetchPositionInfo()
        self.fetchEmployeeNum()
        self.fetchSalaryChange()
        
    def createEmployeeTimelineChart(self, employees):
        # Clear any existing layout in the chart groupbox
        if self.ui.employee_num_chart.layout():
            # Clear old layout
            old_layout = self.ui.employee_num_chart.layout()
            while old_layout.count():
                item = old_layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()
            # We don't call setLayout(None) as it can cause issues
            # Instead, we'll create a new layout and replace the old one
        
        # Create a new layout
        layout = QVBoxLayout(self.ui.employee_num_chart)
        
        # Check if we have employee data
        if not employees:
            self.ui.employee_num_chart.setTitle("No employee data available")
            return
        
        # Create a timeline of employee count changes
        # First, gather all relevant dates (start dates and resignation dates)
        all_dates = []
        
        for employee in employees:
            # Add start date
            start_date = employee['start_date']
            if start_date:
                all_dates.append((start_date, 1))  # +1 for joining
            
            # Add resignation date if exists
            resignation_date = employee['resignation_date']
            if resignation_date:
                all_dates.append((resignation_date, -1))  # -1 for leaving
        
        # Sort dates chronologically
        all_dates.sort(key=lambda x: x[0])
        
        # If no dates found, return
        if not all_dates:
            self.ui.employee_num_chart.setTitle("No employee timeline data available")
            return
        
        # Calculate running count of employees over time
        employee_count = 0
        date_counts = []
        
        for date, change in all_dates:
            employee_count += change
            date_counts.append((date, employee_count))
        
        # Create a line series for the chart
        series = QLineSeries()
        series.setName("Employee Count")
        
        # Add data points to the series
        for date, count in date_counts:
            # Convert date to QDateTime for the chart
            qdate = QDate.fromString(str(date), "yyyy-MM-dd")
            qdatetime = QDateTime(qdate)
            timestamp = qdatetime.toMSecsSinceEpoch()
            
            # Add point to series
            series.append(timestamp, count)
        
        # Create the chart
        chart = QChart()
        chart.addSeries(series)
        chart.setTitle("Employee Count Over Time")
        chart.setAnimationOptions(QChart.SeriesAnimations)
        
        # Create X axis (time)
        axis_x = QDateTimeAxis()
        axis_x.setFormat("MMM yyyy")
        axis_x.setTitleText("Date")
        chart.addAxis(axis_x, Qt.AlignBottom)
        series.attachAxis(axis_x)
        
        # Create Y axis (employee count)
        axis_y = QValueAxis()
        axis_y.setLabelFormat("%d")
        axis_y.setTitleText("Number of Employees")
        axis_y.setMin(0)
        
        # Set Y-axis range with some margin at the top
        max_count = max([count for _, count in date_counts]) if date_counts else 0
        axis_y.setMax(max(max_count + 2, 5))  # At least 5 or max+2
        
        chart.addAxis(axis_y, Qt.AlignLeft)
        series.attachAxis(axis_y)
        
        # Set legend visibility and position
        chart.legend().setVisible(True)
        chart.legend().setAlignment(Qt.AlignBottom)
        
        # Create chart view and add to layout
        chart_view = QChartView(chart)
        chart_view.setRenderHint(QPainter.Antialiasing)
        
        # Add the chart view to the layout
        layout.addWidget(chart_view)
        
        # Set the layout to the groupbox
        self.ui.employee_num_chart.setLayout(layout)
