import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor, QPainter
from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Department_Report import Ui_Department_Report
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


class Ui_Department_Report_Logic(object):
    def __init__(self, sqlconnector, department_id=None):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Department_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.department_id = department_id

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
        self.ui.select_department_btn.clicked.connect(lambda: self.openSelectDepartmentWindow())
        self.fetchDepartments()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        # self.fetchAvgSalary()
        self.fetchDepartmentInfo()
        self.fetchSalaryChange()
        self.fetchEmployeeCount()
        
    def openSelectDepartmentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'departments')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.department_combobox.count()):
                if self.ui.department_combobox.itemData(i)[0] == result['id']:
                    self.ui.department_combobox.setCurrentIndex(i)
                    self.department_id = result['id']
                    break

    def fetchDepartments(self):
        dapartments = self.database_operations.fetchDepartments()
        for dapartment in dapartments:
            id = dapartment[0]
            name = dapartment[1]
            self.ui.department_combobox.addItem(name, id)

    def fetchAvgSalary(self):
        department = self.department_id
        
        from_date = self.ui.from_date.date().toString('yyyy-MM-dd') if self.ui.from_date.date() else ''
        to_date = self.ui.to_date.date().toString('yyyy-MM-dd') if self.ui.to_date.date() else ''
        
        # Fetch payroll details with filters
        salary_blocks = self.database_operations.fetchPayrollsDetails(from_date, to_date, department)
        
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
        
    def fetchDepartmentInfo(self):
        employees = self.database_operations.fetchEmployees(self.department_id)
        loans = self.database_operations.fetchHRLoans(department_id=self.department_id)
        self.ui.total_hr_loans.setText(str(loans[0]['total_loans_value']))
        
    def fetchSalaryChange(self):
        pass

    def fetchEmployeeCount(self):
        employees_count_data = self.database_operations.fetchEmployeesCount()
        current_count = employees_count_data['current_count']
        resigned_count = employees_count_data['resigned_count']
        self.ui.new_employees.setText(str(current_count))
        self.ui.resigned_employees.setText(str(resigned_count))

    def calculate(self):
        # self.fetchAvgSalary()
        self.fetchDepartmentInfo()
        self.fetchEmployeeCount()
        self.fetchSalaryChange()
