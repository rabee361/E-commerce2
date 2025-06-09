import datetime
from datetime import timedelta, datetime
import math
import os
import sys
from Ui_Calculator_Logic import Ui_Calculator_Logic
from Ui_Journal_Logic import Ui_Journal_Logic
from ToolbarManager import ToolbarManager
from Ui_Insurance_Report_Logic import Ui_Insurance_Report_Logic
import win32con
from Ui_Currencies_Logic import Ui_Currencies_Logic
from Ui_DBPassword_Logic import Ui_DBPassword_Logic
from Ui_Users_Logic import Ui_Users_Logic
import win32api
from win32con import MB_OK, MB_OKCANCEL, IDCANCEL
from PyQt5.QtCore import QDate, Qt, QDateTime, QTime, QObject
from PyQt5.QtGui import QColor, QBrush, QDoubleValidator , QIntValidator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QTreeWidgetItem, QLineEdit, QComboBox, QInputDialog, QCheckBox, \
    QTableWidget, QTreeWidget, QApplication, QMainWindow, QPushButton, QSizePolicy, QTabWidget, QFileDialog, QDateEdit
from PyQt5.QtGui import QPixmap
from win32con import MB_YESNO, IDYES, IDNO
from PyQt5 import QtWidgets
from Ui_AuthenticateUser_Logic import Ui_AuthenticateUser_Logic
from Colors import dark_green
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_HR import Ui_HR
from Ui_HR_Employ_Logic import Ui_HR_Employ_Logic
from Ui_Department_Report_Logic import Ui_Department_Report_Logic
from Ui_Position_Report_Logic import Ui_Position_Report_Logic
from Ui_HR_Resign_Logic import Ui_HR_Resign_Logic
from Ui_AuthenticateUser_Logic import current_user
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Course_View_Logic import Ui_Course_View_Logic
from Ui_Select_Language_Logic import Ui_Select_Language_Logic
from WindowsManager import WindowsManager
from FileManager import FileManager
from SqliteConnector import SqliteConnector
from Ui_DatabaseSettings_Logic import Ui_DatabaseSettings_Logic
from Importer import Importer
from Ui_DatabaseBackupRestore_Logic import Ui_DatabaseBackupRestore_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PIL import Image


class Ui_HR_Logic(QObject):
    def __init__(self, sql_connector='', independent=False):
        super().__init__()
        self.importer = ''
        self.windows_manager = ''
        self.filemanager = ''
        self.app = ''
        self.window = ''
        self.toolbar_manager = ''
        self.current_user = ''
        self.sql_connector = sql_connector
        self.independent = independent
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        if self.sql_connector:
            self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_HR()

    def showUi(self):
        self.window = QMainWindow()
        self.window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(self.window)
        self.filemanager = FileManager()
        self.window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.window.setWindowState(Qt.WindowMaximized)
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.initialize(self.window)
        self.window.show()
        self.loan_map = {}
        self.addition_discount_map = {}
        self.department_addition_discount_map = {}
        self.position_addition_discount_map = {}
        self.extras_map = {}
        self.base_salary = {}
        self.showToolBar()

        # Disable if independent before connecting to DB
        if self.independent:
            self.DisableAccountInputs()
            self.ui.tabWidget.setEnabled(False)
        else:
            self.toolbar_manager.hideToolBar()

    def initialize(self, window):
        if self.sql_connector: # only fetch data if connected to DB
            self.fetchData()

        # employment requests
        self.ui.employment_requests_table.itemSelectionChanged.connect(lambda: self.fetchSelectedEmploymentRequest())
        self.ui.add_employment_requests.clicked.connect(lambda: self.addNewEmploymentRequest())
        self.ui.employment_request_add_certificate_btn.clicked.connect(lambda: self.addEmploymentRequestCertificate())
        # self.ui.employment_request_add_certificate_btn.clicked.connect(
            # lambda: self.fetchSelectedEmploymentRequestCertificates())
        self.ui.employment_request_national_id_input.setValidator(QIntValidator())
        self.ui.employment_request_phone_input.setValidator(QIntValidator())
        self.ui.employment_request_university_year_input.setValidator(QIntValidator())
        self.ui.employment_request_university_gpa_input.setValidator(QIntValidator())
        self.ui.employment_request_save_btn.clicked.connect(lambda: self.updateEmploymentRequest())
        self.ui.employment_request_employ_btn.clicked.connect(lambda: self.employ())

        # employees
        self.ui.employees_tree.hideColumn(0)
        self.ui.employees_tree.hideColumn(2)
        self.ui.employees_tree.hideColumn(4)

        self.ui.employee_national_id_input.setValidator(QIntValidator())
        self.ui.employee_phone_input.setValidator(QIntValidator())
        self.ui.employee_university_year_input.setValidator(QIntValidator())
        self.ui.employee_bank_account_number_input.setValidator(QIntValidator())
        self.ui.employee_salary_input.setValidator(QIntValidator())
        self.ui.employee_university_gpa_input.setValidator(QDoubleValidator())
        self.ui.employee_salary_input.setValidator(QDoubleValidator())
        self.ui.employee_course_gpa_input.setValidator(QDoubleValidator())
        self.ui.employee_start_date_input.setDate(QDate.currentDate())
        self.ui.exchange_date_input.setDate(QDate.currentDate())
        self.ui.employee_salary_start_date_input.setDate(QDate.currentDate())
        self.ui.employee_insurance_start_date_input.setDate(QDate.currentDate())

        self.ui.employment_request_delete_certificate_btn.clicked.connect(lambda: self.removeSelectedEmployeeRequest())
        self.ui.employees_tree.clicked.connect(lambda: self.fetchSelectedEmployee())
        self.ui.employee_save_btn.clicked.connect(lambda: self.saveEmployeeInfo())
        self.ui.employee_save_btn.clicked.connect(lambda: self.fetchSelectedEmployee())
        self.ui.employee_add_certificate_btn.clicked.connect(lambda: self.addEmployeeCertificate())
        self.ui.employee_delete_certificate_btn.clicked.connect(lambda: self.removeEmployeeCertificate())
        self.ui.employee_add_certificate_btn.clicked.connect(lambda: self.fetchSelectedEmployee())
        self.ui.employee_save_bank_info_btn.clicked.connect(lambda: self.saveEmployeeFinanceInfo())
        self.ui.employee_salary_currency_combobox.currentIndexChanged.connect(lambda: self.mirrorInputs(self.ui.employee_salary_currency_combobox,self.ui.employee_insurance_currency_combobox))
        self.ui.employee_insurance_currency_combobox.currentIndexChanged.connect(lambda: self.mirrorInputs(self.ui.employee_insurance_currency_combobox,self.ui.employee_salary_currency_combobox))
        self.ui.employees_current_employees.clicked.connect(lambda: self.fetchEmployees('current', self.ui.employees_tree))
        self.ui.employees_resigned_employees.clicked.connect(lambda: self.fetchEmployees('resigned', self.ui.employees_tree))
        self.ui.employee_add_course_btn.clicked.connect(lambda: self.addEmployeeCourse())
        self.ui.employee_delete_course_btn.clicked.connect(lambda: self.removeSelectedEmployeeCourse())
        self.ui.employee_salary_account_combobox.setDisabled(True)
        self.ui.employee_salary_opposite_account_combobox.setDisabled(True)
        self.ui.employee_insurance_account_combobox.setDisabled(True)
        self.ui.employee_insurance_opposite_account_combobox.setDisabled(True)
        self.ui.select_employee_salary_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.employee_salary_account_combobox))
        self.ui.select_employee_salary_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.employee_salary_opposite_account_combobox))
        self.ui.select_employee_insurance_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.employee_insurance_account_combobox))
        self.ui.select_employee_insurance_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.employee_insurance_opposite_account_combobox))
        self.ui.terminate_employee_btn.clicked.connect(lambda: self.openResignWindow())
        self.ui.employee_photo_btn.clicked.connect(lambda: self.uploadEmployeePhoto())

        # departments
        self.ui.departments_day_hours_input.setValidator(QDoubleValidator())
        self.ui.new_departments_day_hours_input.setValidator(QDoubleValidator())
        self.ui.department_additions_discounts_value_input.setValidator(QDoubleValidator())
        self.ui.department_leaves_duration_hours_input.setValidator(QDoubleValidator())
        self.ui.department_leaves_duration_days_input.setValidator(QDoubleValidator())
        self.ui.department_extra_duration_days_input.setValidator(QDoubleValidator())
        self.ui.department_extra_duration_hours_input.setValidator(QDoubleValidator())
        self.ui.department_extra_statement_input.setValidator(QDoubleValidator())
        self.ui.department_extra_date_input.setDate(QDate.currentDate())

        self.ui.department_additions_discounts_end_date_input.setDate(QDate.currentDate())
        self.ui.department_leaves_start_date_input.setDate(QDate.currentDate())
        self.ui.add_department_btn.clicked.connect(lambda: self.addNewDepartment())
        self.ui.departments_table.itemSelectionChanged.connect(lambda: self.fetchSelectedDepartment())
        self.ui.department_save_btn.clicked.connect(lambda: self.saveDepartment())
        self.ui.department_save_btn.clicked.connect(lambda: self.fetchDepartments())
        self.ui.add_departments_additions_discounts_btn.clicked.connect(lambda: self.saveDepartmentFinance())
        self.ui.add_departments_additions_discounts_btn.clicked.connect(lambda: self.fetchSelectedDepartment())
        self.ui.department_leave_cancel_btn.clicked.connect(lambda: self.removeSelectedDepartmentLeave())
        self.ui.cancel_departments_additions_discounts_btn.clicked.connect(lambda: self.removeDepartmentAdditionAndDiscount())
        self.ui.department_leaves_duration_hours_input.textEdited.connect(lambda: self.setHoursAndDays('day', self.ui.department_leaves_duration_days_input,self.ui.departments_table))
        self.ui.department_leaves_duration_days_input.textEdited.connect(lambda: self.setHoursAndDays('hour', self.ui.department_leaves_duration_hours_input, self.ui.departments_table))
        self.ui.add_departments_leaves_btn.clicked.connect(lambda: self.saveDepartmentLeave())
        self.ui.add_departments_leaves_btn.clicked.connect(lambda: self.fetchSelectedDepartment())
        self.ui.new_departments_account_combobox.setDisabled(True)
        self.ui.new_departments_opposite_account_combobox.setDisabled(True)
        self.ui.department_additions_discounts_account_combobox.setDisabled(True)
        self.ui.department_additions_discounts_opposite_account_combobox.setDisabled(True)
        self.ui.departments_account_combobox.setDisabled(True)
        self.ui.departments_opposite_account_combobox.setDisabled(True)
        self.ui.select_new_departments_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.new_departments_account_combobox))
        self.ui.select_new_departments_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.new_departments_opposite_account_combobox))
        self.ui.select_department_additions_discounts_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.department_additions_discounts_account_combobox))
        self.ui.select_department_additions_discounts_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.department_additions_discounts_opposite_account_combobox))
        self.ui.select_departments_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.departments_account_combobox))
        self.ui.select_departments_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.departments_opposite_account_combobox))
        self.ui.department_extra_delete_btn.clicked.connect(lambda: self.removeDepartmentExtra())
        self.ui.department_report_btn.clicked.connect(lambda: self.openDepartmentReportWindow())

        # positions
        self.ui.position_additions_discounts_end_date_input.setDate(QDate().currentDate())
        self.ui.position_leaves_duration_hours_input.setValidator(QDoubleValidator())
        self.ui.position_leaves_duration_days_input.setValidator(QDoubleValidator())
        self.ui.position_salary_input.setValidator(QDoubleValidator())
        self.ui.position_additions_discounts_value_input.setValidator(QDoubleValidator())
        self.ui.position_leaves_start_date_input.setDate(QDate.currentDate())

        self.ui.add_position_btn.clicked.connect(lambda: self.addNewPosition())
        self.ui.delete_position_btn.clicked.connect(lambda: self.removeSelectedPosition())
        self.ui.positions_table.itemSelectionChanged.connect(lambda: self.fetchSelectedPosition())
        self.ui.position_save_btn.clicked.connect(lambda: self.savePosition())
        self.ui.position_save_btn.clicked.connect(lambda: self.fetchPositions())
        self.ui.add_positions_additions_discounts_btn.clicked.connect(lambda: self.savePositionFinance())
        # self.ui.add_positions_additions_discounts_btn.clicked.connect(lambda: self.fetchSelectedPosition())
        self.ui.position_leaves_duration_hours_input.textEdited.connect(
            lambda: self.setHoursAndDays('day', self.ui.position_leaves_duration_days_input))
        self.ui.position_leaves_duration_days_input.textEdited.connect(
            lambda: self.setHoursAndDays('hour', self.ui.position_leaves_duration_hours_input))
        self.ui.add_positions_leaves_btn.clicked.connect(lambda: self.savePositionLeave())
        self.ui.add_positions_leaves_btn.clicked.connect(lambda: self.fetchSelectedPosition())
        self.ui.delete_positions_additions_discounts_btn.clicked.connect(lambda: self.removeSelectedPositionFinance())
        self.ui.delete_position_leave_btn.clicked.connect(lambda: self.removeSelectedPositionLeave())
        self.ui.position_additions_discounts_account_combobox.setDisabled(True)
        self.ui.position_additions_discounts_opposite_account_combobox.setDisabled(True)
        self.ui.select_position_additions_discounts_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.position_additions_discounts_account_combobox))
        self.ui.select_position_additions_discounts_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.position_additions_discounts_opposite_account_combobox))
        self.ui.position_report_btn.clicked.connect(lambda: self.openPositionReportWindow())

        # leaves
        self.ui.leave_duration_hours_input.setValidator(QDoubleValidator())
        self.ui.leave_duration_days_input.setValidator(QDoubleValidator())
        self.ui.leave_start_input.setDate(QDate.currentDate())
        self.ui.leaves_employees_tree.itemSelectionChanged.connect(lambda: self.fetchSelectedEmployeeLeaves())
        self.ui.leaves_employees_tree.itemSelectionChanged.connect(lambda: self.fetchEmployeeLeavesBalance())
        self.ui.add_leave_btn.clicked.connect(lambda: self.saveLeave())
        self.ui.add_leave_btn.clicked.connect(lambda: self.fetchSelectedEmployeeLeaves())
        self.ui.delete_leave_btn.clicked.connect(lambda: self.removeSelectedLeave())
        self.ui.leaves_current_employees.clicked.connect(
            lambda: self.fetchEmployees('current', self.ui.leaves_employees_tree))
        self.ui.leaves_resigned_employees.clicked.connect(
            lambda: self.fetchEmployees('resigned', self.ui.leaves_employees_tree))
        self.ui.leave_start_input.editingFinished.connect(lambda: self.setLeaveDays())
        self.ui.leave_duration_days_input.textEdited.connect(
            lambda: self.setHoursAndDays('hour', self.ui.leave_duration_hours_input, self.ui.leaves_employees_tree))
        self.ui.leave_duration_hours_input.textEdited.connect(
            lambda: self.setHoursAndDays('day', self.ui.leave_duration_days_input, self.ui.leaves_employees_tree))
        self.ui.leave_duration_days_input.editingFinished.connect(lambda: self.setLeaveDays())
        self.ui.leave_duration_hours_input.editingFinished.connect(lambda: self.setLeaveDays())

        self.ui.leave_type_period_combobox.clear()
        self.ui.leave_type_period_combobox.addItem(self.language_manager.translate( 'HR_LEAVE_TYPE_MONTH'), "month")
        self.ui.leave_type_period_combobox.addItem(self.language_manager.translate( 'HR_LEAVE_TYPE_YEAR'), "year")

        # courses
        self.ui.course_employee_gpa_input.setValidator(QDoubleValidator())
        self.ui.course_employees_combobox.setDisabled(True)
        self.ui.courses_table.clicked.connect(lambda: self.fetchCourseEmployees())
        self.ui.courses_table.cellDoubleClicked.connect(lambda: self.openCourseViewWindow())
        self.ui.add_course_btn.clicked.connect(lambda: self.openAddNewCourseWindow())
        self.ui.add_course_employee_btn.clicked.connect(lambda: self.addCourseEmployee())
        self.ui.add_course_employee_btn.clicked.connect(lambda: self.fetchCourseEmployees())
        self.ui.edit_course_employee_btn.clicked.connect(lambda: self.updateCourseEmployeeGpa())
        self.ui.delete_course_btn.clicked.connect(lambda: self.removeCourse())
        self.ui.edit_course_employee_btn.clicked.connect(lambda: self.fetchCourseEmployees())
        self.ui.select_course_emplyee_btn.clicked.connect(lambda: self.openSelectCourseEmployeeWindow(self.ui.course_employees_combobox))
        self.ui.delete_course_employee_btn.clicked.connect(lambda: self.removeCourseEmployee())

        # loans
        self.ui.loan_date_input.setDate(QDate.currentDate())
        self.ui.loan_value_input.setValidator(QDoubleValidator())
        self.ui.loan_subtract_value.setValidator(QDoubleValidator())
        self.ui.loan_date_input.setDate(QDate.currentDate())
        self.ui.loan_account_combobox.setEnabled(False)
        self.ui.loan_opposite_account_combobox.setEnabled(False)
        self.ui.loan_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.loan_account_combobox))
        self.ui.loan_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.loan_opposite_account_combobox))
        self.ui.loan_subtract_checkbox.clicked.connect(lambda: self.activateLoanSubtract())
        self.ui.add_loan_btn.clicked.connect(lambda: self.addLoan())
        self.ui.loans_employees_tree.itemSelectionChanged.connect(lambda: self.setEmployeeLoansDefaults())
        self.ui.loans_employees_tree.itemSelectionChanged.connect(lambda: self.fetchEmployeeLoans())
        self.ui.loans_table.itemSelectionChanged.connect(lambda: self.fetchLoanPayments())
        self.ui.loans_combobox.currentIndexChanged.connect(lambda: self.setPaymentCurrency())
        self.ui.add_loan_payemnt_btn.clicked.connect(lambda: self.addLoanPayment())
        self.ui.add_loan_payemnt_btn.clicked.connect(lambda: self.fetchEmployeeLoans())
        self.ui.delete_loan_btn.clicked.connect(lambda: self.removeLoan())
        self.ui.loans_current_employees.clicked.connect(
            lambda: self.fetchEmployees('current', self.ui.loans_employees_tree))
        self.ui.loans_resigned_employees.clicked.connect(
            lambda: self.fetchEmployees('resigned', self.ui.loans_employees_tree))

        # additional costs
        self.ui.new_additional_costs_date_input.setDate(QDate.currentDate())
        self.ui.add_additional_cost_btn.clicked.connect(lambda: self.addAditionalCosts())
        # self.ui.add_additional_cost_btn.clicked.connect(lambda: self.fetchAdditionalCosts())
        self.ui.new_additional_costs_account_combobox.setDisabled(True)
        self.ui.new_additional_costs_opposite_account_combobox.setDisabled(True)
        self.ui.select_new_additional_costs_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.new_additional_costs_account_combobox))
        self.ui.select_new_additional_costs_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.new_additional_costs_opposite_account_combobox))
        self.ui.additional_costs_cancel_btn.clicked.connect(lambda: self.removeSelectedAdditionalCost())

        # extra work
        self.setExtraTypeValue()
        self.ui.extra_duration_hours_input.setValidator(QDoubleValidator())
        self.ui.extra_duration_days_input.setValidator(QDoubleValidator())
        self.ui.extra_rate_input.setValidator(QDoubleValidator())
        self.ui.extra_value_input.setValidator(QDoubleValidator())
        self.ui.new_additional_costs_value_input.setValidator(QDoubleValidator())
        self.ui.extra_date_input.setDate(QDate.currentDate())
        self.ui.extra_opposite_account_combobox.setEnabled(False)
        self.ui.extra_account_combobox.setEnabled(False)
        self.ui.extra_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.extra_account_combobox))
        self.ui.extra_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.extra_opposite_account_combobox))
        self.ui.extras_employees_tree.itemSelectionChanged.connect(lambda: self.setExtraCurrency())
        self.ui.extra_delete_btn.clicked.connect(lambda: self.removeSelectedExtra())
        self.ui.extras_employees_tree.itemSelectionChanged.connect(lambda: self.fetchExtras())
        self.ui.extras_employees_tree.itemSelectionChanged.connect(lambda: self.setExtraValue())
        self.ui.departments_table.itemSelectionChanged.connect(lambda: self.fetchDepartmentExtras())
        self.ui.extra_duration_days_input.textEdited.connect(
            lambda: self.setHoursAndDays('hour', self.ui.extra_duration_hours_input, self.ui.extras_employees_tree))
        self.ui.extra_duration_hours_input.textEdited.connect(
            lambda: self.setHoursAndDays('day', self.ui.extra_duration_days_input, self.ui.extras_employees_tree))
        self.ui.department_extra_duration_days_input.textEdited.connect(
            lambda: self.setHoursAndDays('hour', self.ui.department_extra_duration_hours_input, self.ui.departments_table))
        self.ui.department_extra_duration_hours_input.textEdited.connect(
            lambda: self.setHoursAndDays('day', self.ui.department_extra_duration_days_input, self.ui.departments_table))
        self.ui.add_extra_btn.clicked.connect(lambda: self.addExtras())
        self.ui.department_add_extra_btn.clicked.connect(lambda: self.addDepartmentExtra())
        self.ui.add_extra_btn.clicked.connect(lambda: self.fetchExtras())
        self.ui.extra_type_combobox.currentIndexChanged.connect(lambda: self.setExtraTypeValue())
        self.ui.department_extra_type_combobox.currentIndexChanged.connect(lambda: self.setDepartmentExtraTypeValue())
        self.ui.extra_rate_input.textChanged.connect(lambda: self.setExtraValue())
        self.ui.extra_current_employees.clicked.connect(
            lambda: self.fetchEmployees('current', self.ui.extras_employees_tree))
        self.ui.extra_resigned_employees.clicked.connect(
            lambda: self.fetchEmployees('resigned', self.ui.extras_employees_tree))

        # settings
        self.ui.setting_day_hours_input.setValidator(QDoubleValidator())
        self.ui.setting_month_duration_input.setValidator(QDoubleValidator())
        self.ui.setting_extra_normal_input.setValidator(QDoubleValidator())
        self.ui.setting_extra_high_input.setValidator(QDoubleValidator())
        self.ui.leave_type_days_input.setValidator(QDoubleValidator())
        self.ui.save_settings_btn.clicked.connect(lambda: self.saveSettings())
        self.ui.add_leave_type_btn.clicked.connect(lambda: self.addLeaveType())
        self.ui.add_leave_type_btn.clicked.connect(lambda: self.fetchLeaveTypes())
        self.ui.leave_type_delete_btn.clicked.connect(lambda: self.removeSelectedLeaveType())

        self.ui.select_setting_insurance_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_insurance_opposite_account_combobox))
        self.ui.select_setting_departments_default_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_default_account_combobox))
        self.ui.select_setting_additional_costs_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_additional_costs_account_combobox))
        self.ui.select_setting_departments_additions_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_additions_opposite_account_combobox))
        self.ui.select_setting_additions_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_additions_opposite_account_combobox))
        self.ui.select_setting_salaries_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_salaries_opposite_account_combobox))
        self.ui.select_setting_departments_additions_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_additions_account_combobox))
        self.ui.select_setting_salaries_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_salaries_account_combobox))
        self.ui.select_setting_additions_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_additions_account_combobox))
        self.ui.select_setting_discounts_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_discounts_opposite_account_combobox))
        self.ui.select_setting_departments_default_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_default_opposite_account_combobox))
        self.ui.select_setting_departments_discounts_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_discounts_account_combobox))
        self.ui.select_setting_discounts_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_discounts_account_combobox))
        self.ui.select_setting_additional_costs_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_additional_costs_opposite_account_combobox))
        self.ui.select_setting_courses_costs_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_courses_costs_account_combobox))
        self.ui.select_setting_courses_costs_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_courses_costs_opposite_account_combobox))
        self.ui.select_setting_loans_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_loans_account_combobox))
        self.ui.select_setting_departments_discounts_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_departments_discounts_opposite_account_combobox))
        self.ui.select_setting_loans_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_loans_opposite_account_combobox))
        self.ui.select_setting_insurance_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_insurance_account_combobox))
        self.ui.select_setting_extra_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_extra_account_combobox))
        self.ui.select_setting_extra_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_extra_opposite_account_combobox))
        self.ui.select_setting_resource_recipients_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.setting_resource_recipients_account_combobox))

        # salary
        self.ui.salaries_discount_addition_repeatition_input.setValidator(QIntValidator())
        self.ui.salaries_discount_addition_value_input.setValidator(QIntValidator())
        self.ui.salaries_discount_addition_type_combobox.currentIndexChanged.connect(lambda: self.disableRepeatition())
        self.ui.salaries_discount_addition_start_date_input.setDate(QDate.currentDate())
        self.ui.salaries_discount_addition_account_combobox.setEnabled(False)
        self.ui.salaries_discount_addition_opposite_account_combobox.setEnabled(False)
        self.ui.salaries_discount_addition_account_btn.clicked.connect(lambda: self.openSelectSalariesDiscountAdditionAccountWindow())
        self.ui.salaries_discount_addition_opposite_account_btn.clicked.connect(lambda: self.openSelectSalariesDiscountAdditionEmployeeAccountWindow())
        self.ui.salaries_to_date_input.setDate(QDate.currentDate())
        self.ui.salaries_exchange_price_date_input.setDate(QDate.currentDate())
        self.ui.salaries_current_employees.clicked.connect(
            lambda: self.fetchEmployees('current', self.ui.salaries_employees_tree))
        self.ui.salaries_resigned_employees.clicked.connect(
            lambda: self.fetchEmployees('resigned', self.ui.salaries_employees_tree))
        self.ui.salaries_discount_addition_delete_btn.clicked.connect(lambda: self.removeSelectedSalaryAdditionAndDiscount())
        self.ui.salaries_employees_tree.itemSelectionChanged.connect(lambda: self.setSalaryAdditionsDiscountsCurrency())
        self.ui.salaries_employees_tree.itemSelectionChanged.connect(lambda: self.fetchSalaryAdditionsAndDiscounts())
        self.ui.salary_addition_discount_add_btn.clicked.connect(lambda: self.addSalaryAdditionAndDiscount())
        self.ui.salary_addition_discount_add_btn.clicked.connect(lambda: self.fetchSalaryAdditionsAndDiscounts())
        self.ui.salaries_calculate_btn.clicked.connect(lambda: self.calculateSalaries())
        self.ui.salaries_procee_payroll_btn.clicked.connect(lambda: self.processPayroll())
        self.ui.salaries_payroll_tree.clicked.connect(lambda: self.fetchPayrollDetails())


        # insurance
        self.ui.insurance_to_date_input.setDate(QDate.currentDate())
        self.ui.insurance_exchange_price_date_input.setDate(QDate.currentDate())
        self.ui.insurance_calculate_btn.clicked.connect(lambda: self.calculateInsurance())
        self.ui.insurance_process_btn.clicked.connect(lambda: self.processInsurances())
        self.ui.insurance_report.clicked.connect(lambda: self.openInsuranceReportWindow())
        self.ui.insurance_payroll_tree.clicked.connect(lambda: self.fetchInsurancePayrollDetails())

        self.setFormatDate()

        self.setSalaryCycles()
        self.setWeekDays()

        self.ui.employee_add_received_btn.clicked.connect(lambda: self.addEmployeeReceivedItem())
        self.ui.select_employee_received_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())
        self.ui.select_employee_received_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.employee_delete_received_item_btn.clicked.connect(lambda: self.removeSelectedEmployeeReceivedItem())

    # isolate the data fetching process from initilization in case HR was opened in independent mode
    def fetchData(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            self.fetchEmployees('current', self.ui.course_employees_combobox)
            self.fetchCourses()
            self.fetchDepartments()
            self.setSalaryAdditionsDiscountsTypes()
            self.fetchPositions()
            self.fetchEmploymentRequests()
            self.fetchCurrencies()
            self.fetchAccounts()
            self.setDisountsAdditionsType()
            self.fetchAdditionalCosts()
            self.fetchSettings()
            self.fetchExtrasHighAndLow()
            self.fetchExtras()
            self.fetchDepartmentExtrasHighAndLow()
            self.fetchDepartmentExtras()
            self.fetchLeaveTypes()
            self.fetchEmployees('current', self.ui.employees_tree)
            self.fetchEmployees('current', self.ui.leaves_employees_tree)
            self.fetchEmployees('current', self.ui.extras_employees_tree)
            self.fetchEmployees('current', self.ui.loans_employees_tree)
            self.fetchEmployees('current', self.ui.salaries_employees_tree)
            self.fetchPayrolls()
            self.fetchInsurancePayrolls()
            self.setPricingMethods()
            self.setPriorityCalculationMethods()
            self.fetchWarehouses()
        else:
            win32api.MessageBox(0, self.language_manager.translate('DATABASE_NOT_CONNECTED'), self.language_manager.translate('ERROR'), MB_OK)

    def setFormatDate(self):
        date_inputs = self.window.findChildren(QDateEdit)
        for date_input in date_inputs:
            date_input.setDisplayFormat("yyyy-MM-dd")


    def closeAllWindows(self, event=None):
        if self.windows_manager.checkForOpenWindows(self.window) is False:
            if event:
                event.accept()
            else:
                return True
        else:
            pass

    def showToolBar(self):
        # Initialize toolbar manager with the main window
        self.toolbar_manager = ToolbarManager(self.windows_manager, self.current_user, self.ui)

        # Map action names to their handler methods
        action_handlers = {
            "new_file": lambda: self.createFile(self.window),
            "connect_database": lambda: self.openDatabaseSettings(),
            "open_file": lambda: self.openFile(self.window),
            "calculator": lambda: self.openCalculatorWindow(),
            "users": lambda: self.openUsersWindow(),
            "refresh": lambda: self.fetchData(),
            "backup": lambda: self.openDatabaseBackup(),
            "language": lambda: self.openSelectLanguageWindow(),
            "currencies": lambda: self.openCurrenciesWindow(),
            "journal_entry": lambda: self.openJournalWindow(),
        }

        # Connect each action to its handler
        for action in self.toolbar_manager.actions:
            if action.objectName() in action_handlers:
                action.triggered.connect(action_handlers[action.objectName()])

        # Add toolbar to the main window
        self.window.addToolBar(self.toolbar_manager.toolbar)
        self.toolbar_manager.showToolBar(action_handlers)


    def openCalculatorWindow(self):
        Ui_Calculator_Logic().showUi()


    def openJournalWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
                Ui_Journal_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openCurrenciesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Currencies_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_DATABASE'), self.language_manager.translate( 'ERROR'))

    def createFile(self, MainWindow):
        global current_user
        file = self.filemanager.createEmptyFile('db')
        print(file)
        if file != "":
            if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
                self.sql_connector.disconnectDatabase()
            self.sql_connector = SqliteConnector()
            self.sql_connector.connectToDatabase(file)
            self.database_operations = DatabaseOperations(self.sql_connector)

            owner = self.database_operations.fetchOwner()
            if not owner:
                Ui_DBPassword_Logic(self.sql_connector).showUi()

            if not current_user:
                user = Ui_AuthenticateUser_Logic(self.sql_connector).showUi()
                if user:
                    current_user = user

            self.current_user = current_user
            self.database_operations.setCurrentUser(current_user)
            self.ui.tabWidget.setEnabled(True)
            self.fetchData()
        else:
            print("No File.")

    def openFile(self, MainWindow):
        global current_user
        file = self.filemanager.openFile("db")
        if file != "":
            if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
                self.sql_connector.disconnectDatabase()
                current_user = 0
            self.sql_connector = SqliteConnector()
            self.sql_connector.connectToDatabase(file)
            self.database_operations = DatabaseOperations(self.sql_connector)

            owner = self.database_operations.fetchOwner()
            if not owner:
                Ui_DBPassword_Logic(self.sql_connector).showUi()

            if not current_user:
                user = Ui_AuthenticateUser_Logic(self.sql_connector).showUi()
                if user:
                    current_user = user

            self.ui.tabWidget.setEnabled(True)
            self.fetchData()
        else:
            print("No File.")

    def openDatabaseSettings(self):
        global current_user
        db_setting_window = Ui_DatabaseSettings_Logic(self.filemanager)
        db_setting_window.showUi()
        mysql_connector = db_setting_window.getMysqlConnector()
        database_name = db_setting_window.getDatabsaeName()
        if mysql_connector.is_connected_to_database:
            if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
                self.sql_connector.disconnectDatabase()
                current_user = 0
            self.sql_connector = mysql_connector
            self.database_name = database_name
            self.database_operations = DatabaseOperations(self.sql_connector)
            owner = self.database_operations.fetchOwner()
            if not owner:
                Ui_DBPassword_Logic(self.sql_connector).showUi()

            if not current_user:
                user = Ui_AuthenticateUser_Logic(self.sql_connector).showUi()
                if user:
                    current_user = user

            self.current_user = current_user
            self.database_operations.setCurrentUser(current_user)
            self.ui.tabWidget.setEnabled(True)
            self.fetchData()

    def openDatabaseBackup(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database and str(
                type(self.sql_connector)) == "<class 'MysqlConnector.MysqlConnector'>":
            Ui_DatabaseBackupRestore_Logic(self.sql_connector, self.database_name, self.filemanager).showUi()
            self.openDatabaseSettings()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_DATABASE'), self.language_manager.translate( 'ERROR'))

    def openUsersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Users_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_FILE'), self.language_manager.translate( 'ERROR'))

    def openSelectLanguageWindow(self):
        Ui_Select_Language_Logic().showUi()
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.toolbar_manager.retranslateToolbar()

    def setPricingMethods(self):
        pricing_methods = {
            self.language_manager.translate("PRICING_METHOD_MEDIAN"): "median",
            self.language_manager.translate("PRICING_METHOD_MAX_PRICE"): "max_price",
            self.language_manager.translate("PRICING_METHOD_LAST_BUY"): "last_buy",
            self.language_manager.translate("PRICING_METHOD_LAST_BUY_WITH_DISCOUNTS_AND_ADDITIONS"): "last_buy_with_discounts_and_additions",
        }
        for key, value in pricing_methods.items():
            self.ui.pricing_method_combobox.addItem(key, value)

    def setPriorityCalculationMethods(self):
        self.ui.setting_priority_additions_salary_combobox.clear()
        self.ui.setting_priority_discount_salary_combobox.clear()
        priority_options = {
            "total_sum": self.language_manager.translate('HR_PRIORITY_TOTAL_SUM'),
            "department": self.language_manager.translate('HR_PRIORITY_DEPARTMENT'),
            "position": self.language_manager.translate('HR_PRIORITY_POSITION'),
            "employee": self.language_manager.translate('HR_PRIORITY_EMPLOYEE'),
            "max_value": self.language_manager.translate('HR_PRIORITY_MAX_VALUE'),
            "min_value": self.language_manager.translate('HR_PRIORITY_MIN_VALUE')
        }
        for data, text in priority_options.items():
            self.ui.setting_priority_additions_salary_combobox.addItem(text, data)
            self.ui.setting_priority_discount_salary_combobox.addItem(text, data)

    def openSelectAccountWindow(self, combobox):
        # Update accounts combobox
        self.fetchAccounts()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))


    def openSelectEmployeeAccountWindow(self, combobox):
        # Update accounts combobox
        self.fetchAccounts()
        selected_employee = self.ui.extras_employees_tree.currentItem()
        if selected_employee is not None:
            employee_id = selected_employee.text(4)
            employee_account = self.database_operations.fetchAccount(employee_id)
            account_id = employee_account['id']
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', default_id=account_id)
            result = data_picker.showUi()
            if result is not None:
                combobox.setCurrentIndex(combobox.findData(result['id']))


    def openResignWindow(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee is not None:
            employee_id = selected_employee.text(4)
            Ui_HR_Resign_Logic(self.sql_connector, employee_id).showUi()

    def uploadEmployeePhoto(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee is not None:
            employee_id = selected_employee.text(4)

            file_name, _ = QFileDialog.getOpenFileName(self.window, "Select Photo", "", "Image Files (*.png *.jpg *.jpeg)")
            if file_name:
                # Check file size is less than 2MB
                file_size = os.path.getsize(file_name)
                if file_size > 2 * 1024 * 1024:  # 2MB in bytes
                    win32api.MessageBox(0, self.language_manager.translate( 'HR_ALERT_IMAGE_SIZE'), self.language_manager.translate( 'ERROR'))
                    return

                # Use PIL to resize the image to 250x250
                img = Image.open(file_name)
                img = img.resize((250, 250), Image.LANCZOS)

                # Save to bytes for database
                import io
                img_byte_arr = io.BytesIO()
                img.save(img_byte_arr, format=img.format if img.format else 'JPEG')
                photo_data = img_byte_arr.getvalue()

                self.database_operations.updateEmployeePhoto(employee_id, photo_data)

                # Display in UI
                pixmap = QPixmap()
                pixmap.loadFromData(photo_data)
                self.ui.image_label.setPixmap(pixmap)

    def openSelectWarehouseWindow(self):
        # Update warehouses combobox
        self.fetchWarehouses()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.employee_received_warehouse_combobox.count()):
                warehouse_data = self.ui.employee_received_warehouse_combobox.itemData(i)
                if warehouse_data[0] == result['id']:
                    self.ui.employee_received_warehouse_combobox.setCurrentIndex(i)
                    self.fetchWarehouseMaterials()
                    self.setMaterialUnit()
                    self.setMaterialCurrencies()
                    return

    def openSelectMaterialWindow(self):
        warehouse_id = self.ui.employee_received_warehouse_combobox.currentData()[0]
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouse_materials', columns=['id', 'material_name', 'quantity'], warehouse_id=warehouse_id)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.employee_received_material_combobox.count()):
                material_data = self.ui.employee_received_material_combobox.itemData(i)
                if material_data[0] == result['material_id']:
                    self.ui.employee_received_material_combobox.setCurrentIndex(i)
                    self.setMaterialUnit()
                    self.setMaterialCurrencies()
                    return

    def fetchWarehouses(self):
        self.ui.employee_received_warehouse_combobox.clear()
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            warehouse_id = warehouse['id']
            warehouse_name = warehouse['name']
            warehouse_account_id = warehouse['account']
            data = [warehouse_id, warehouse_account_id]
            self.ui.employee_received_warehouse_combobox.addItem(warehouse_name, data)

    def fetchWarehouseMaterials(self):
        selected_warehouse = self.ui.employee_received_warehouse_combobox.currentData()[0]
        self.ui.employee_received_material_combobox.clear()
        if selected_warehouse:
            materials = self.database_operations.fetchWarehouseMaterials(selected_warehouse)
            for material in materials:
                material_id = material['material_id']
                material_name = material['material_name']
                material_unit_id = material['unit']
                material_unit_name = material['unit_name']
                material_move_id = material['material_move_id']
                data = [material_id, material_name, material_unit_id, material_unit_name, material_move_id]
                self.ui.employee_received_material_combobox.addItem(material_name, data)

    def setMaterialUnit(self):
        selected_material = self.ui.employee_received_material_combobox.currentData()
        if selected_material:
            material_unit_id = selected_material[2]
            material_unit_name = selected_material[3]
            self.ui.employee_received_unit_input.setText(material_unit_name)

    def setMaterialCurrencies(self):
        self.ui.employee_received_item_currency_combobox.clear()
        selected_material = self.ui.employee_received_material_combobox.currentData()
        if selected_material:
            material_currencies = self.database_operations.fetchMaterialCurrencies(selected_material[0])
            for material_currency in material_currencies:
                self.ui.employee_received_item_currency_combobox.addItem(material_currency[1], material_currency[0])

    def addEmployeeReceivedItem(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee is not None:
            employee_id = selected_employee.text(4)
            warehouse_id = self.ui.employee_received_warehouse_combobox.currentData()[0]
            warehouse_account_id = self.ui.employee_received_warehouse_combobox.currentData()[1]
            material_id = self.ui.employee_received_material_combobox.currentData()[0]
            material_name = self.ui.employee_received_material_combobox.currentData()[1]
            material_invoice_item_id = self.ui.employee_received_material_combobox.currentData()[4]
            unit_id = self.ui.employee_received_material_combobox.currentData()[2]
            quantity = self.ui.employee_received_quantity_input.text()
            received_date = ''
            if quantity and quantity != '':
                received_item_id = self.database_operations.addEmployeeReceivedItem(employee_id, warehouse_id, quantity, material_id, unit_id, received_date)
                if self.ui.generate_journal_entry_checkbox.isChecked():
                    self.generateReceivedItemJournalEntry(received_item_id, warehouse_account_id, material_name, material_id, quantity)
                self.fetchSelectedEmployee()
            else:
                win32api.MessageBox(0, self.language_manager.translate( 'HR_ALERT_ENTER_QUANTITY'), self.language_manager.translate( 'ERROR'))
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'HR_ALERT_SELECT_EMPLOYEE'), self.language_manager.translate( 'ERROR'))

    def generateReceivedItemJournalEntry(self, received_item_id, warehouse_account_id, material_name,   material_id, quantity ):
        date = QDate.currentDate().toString(Qt.ISODate)
        currency_id = self.ui.employee_received_item_currency_combobox.currentData()
        origin_type = self.language_manager.translate( "RECEIVED_ITEM_ORIGIN_TYPE")
        journal_entry_id = self.database_operations.addJournalEntry(date, currency_id, origin_type=origin_type, origin_id=received_item_id, commit=False)

        setting_resource_recipients_account = self.database_operations.fetchHRSetting('setting_resource_recipients_account', commit=False)
        if setting_resource_recipients_account:
            resource_recipients_account_id = setting_resource_recipients_account['value_col']
            value = self.calculateReceivedItemValue(material_id, currency_id, quantity)
            # TODO: add journal entry item when synchronized with other DBs
            # self.database_operations.addJournalEntryItem(journal_entry_id, currency_id, 'creditor', 'Receiving ' + str(material_name), warehouse_account_id, resource_recipients_account_id, value, commit=True)

    def calculateReceivedItemValue(self, material_id, currency_id, quantity):
        pricing_method = self.ui.pricing_method_combobox.currentData()
        exchange_date = self.ui.exchange_date_input.date().toString(Qt.ISODate)
        estimated_price = 0
        if pricing_method == 'median':
            average_price = self.database_operations.fetchAverageMaterialPrice(material_id, currency_id, currency_exchage_date=exchange_date)
            if average_price:
                estimated_price = float(quantity) * float(average_price)

        if pricing_method == 'max_price':
            max_price = self.database_operations.fetchMaximumMaterialPrice(material_id, currency_id, currency_exchage_date=exchange_date)
            if max_price:
                estimated_price = float(quantity) * float(max_price)

        if pricing_method == 'last_buy_with_discounts_and_additions':
            date_input = self.ui.exchange_date_input.date().toString(Qt.ISODate)
            last_price = self.database_operations.fetchLastInvoiceOfMaterialWithDiscountsAndAdditions(material_id, invoice_type='buy')
            if last_price:
                unit1_id = last_price['unit1_id']
                unit_price = last_price['unit_price']
                payment_currency = last_price['payment_currency']
                invoice_date = last_price['date_col']

                material_details = self.database_operations.fetchMaterial(material_id)
                material_units = {1: material_details[12], 2: material_details[13],
                                    3: material_details[14]}
                default_unit = material_units[material_details[15]]

                if unit1_id == default_unit:
                    pass
                else:
                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1_id,default_unit)
                    quantity_in_default_unit = 1 * conversion_rate
                    unit_price = float(unit_price) / float(quantity_in_default_unit)

                if payment_currency == currency_id:
                    last_price = unit_price
                else:
                    exchange_value = self.database_operations.fetchExchangeValue(
                        payment_currency,
                        currency_id,
                        date_input)

                    if exchange_value:
                        last_price = unit_price * float(exchange_value[0][1])

                    else:
                        last_price = 0

                if last_price:
                    estimated_price = float(quantity) * float(last_price)

        if pricing_method == 'last_buy':
            date_input = self.ui.exchange_date_input.date().toString(Qt.ISODate)
            last_price = self.database_operations.fetchLastInvoiceOfMaterial(material_id, invoice_type='buy')
            if last_price:
                unit1_id = last_price[3]
                unit_price = last_price[6]
                payment_currency = last_price[8]
                invoice_date = last_price[10]

                material_details = self.database_operations.fetchMaterial(material_id)
                material_units = {1: material_details[12], 2: material_details[13],
                                    3: material_details[14]}
                default_unit = material_units[material_details[15]]

                if unit1_id == default_unit:
                    pass
                else:
                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1_id,default_unit)
                    quantity_in_default_unit = 1 * conversion_rate
                    unit_price = float(unit_price) / float(quantity_in_default_unit)

                if payment_currency == currency_id:
                    last_price = unit_price
                else:
                    exchange_value = self.database_operations.fetchExchangeValue(
                        payment_currency,
                        currency_id,
                        date_input)

                    if exchange_value:
                        last_price = unit_price * float(exchange_value[0][1])

                    else:
                        last_price = 0

                if last_price:
                    estimated_price = float(quantity) * float(last_price)

        return estimated_price


    def removeSelectedEmployeeReceivedItem(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate( 'DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_employee_received_item = self.ui.employee_received_items_table.currentItem()
            if selected_employee_received_item is not None:
                selected_employee_received_item_id = self.ui.employee_received_items_table.item(selected_employee_received_item.row(), 0).text()
                self.database_operations.removeEmployeeReceivedItem(selected_employee_received_item_id)
                self.fetchSelectedEmployee()

    def fetchEmploymentRequests(self):
        self.ui.employment_requests_table.setRowCount(0)
        employment_requests = self.database_operations.fetchEmploymentRequests()
        for employment_request in employment_requests:
            id = employment_request['id']
            national_id = employment_request['national_id']
            phone = employment_request['phone']
            address = employment_request['address']
            name = employment_request['name']
            email = employment_request['email']
            birthdate = employment_request['birthdate']
            date = employment_request['date_col']

            # Create a empty row at bottom of table
            numRows = self.ui.employment_requests_table.rowCount()
            self.ui.employment_requests_table.insertRow(numRows)

            # Add text to the row
            self.ui.employment_requests_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
            self.ui.employment_requests_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
            self.ui.employment_requests_table.setItem(numRows, 2, QTableWidgetItem(str(date)))


    def removeSelectedEmployeeRequest(self):
        selected_employment_request_certificate = self.ui.employment_request_certificates_table.currentItem()
        if selected_employment_request_certificate is not None:
            selected_employment_request_certificate_id = self.ui.employment_request_certificates_table.item(selected_employment_request_certificate.row(), 0).text()
            self.database_operations.removeEmploymentRequestCertificate(selected_employment_request_certificate_id)
        self.fetchSelectedEmploymentRequest()


    def fetchSelectedEmploymentRequestCertificates(self):
        pass


    def addNewEmploymentRequest(self):
        name = self.ui.new_employment_request_name_input.text()
        if name and name != '':
            employment_request = self.database_operations.fetchEmploymentRequest(name=name)
            if employment_request:
                win32api.MessageBox(0, self.language_manager.translate('HR_ALERT_EMPLOYMENT_REQUEST_ALREADY_EXISTS'), self.language_manager.translate('ERROR'))
                return
            self.database_operations.addNewEmploymentRequest(name)
            self.ui.new_employment_request_name_input.clear()
            self.fetchEmploymentRequests()

    def fetchSelectedEmploymentRequest(self):
        selected_employment_request = self.ui.employment_requests_table.currentItem()
        if selected_employment_request is not None:
            selected_employment_request_id = self.ui.employment_requests_table.item(selected_employment_request.row(),0).text()
            employment_request = self.database_operations.fetchEmploymentRequest(selected_employment_request_id)
            if employment_request:
                id = employment_request['id']
                national_id = employment_request['national_id']
                phone = employment_request['phone']
                address = employment_request['address']
                name = employment_request['name']
                email = employment_request['email']
                birthdate = employment_request['birthdate']
                date = employment_request['date_col']

                # Set the fetched data to appropriate UI elements or do further processing as needed
                self.ui.employment_request_national_id_input.setText(national_id)
                self.ui.employment_request_phone_input.setText(phone)
                self.ui.employment_request_address_input.setText(address)
                self.ui.employment_request_name_input.setText(name)
                self.ui.employment_request_email_input.setText(email)
                self.ui.employment_request_birthdate_input.setDate(QDate.currentDate())

            self.ui.employment_request_certificates_table.clearContents()
            employment_request_certificates = self.database_operations.fetchEmploymentRequestsCertificates(
                selected_employment_request_id)
            # Populate the UI table with fetched data
            self.ui.employment_request_certificates_table.setRowCount(len(employment_request_certificates))
            for i, certificate in enumerate(employment_request_certificates):
                id = certificate[0]
                employment_request_id = certificate[1]
                university_name = certificate[2]
                university_specialty = certificate[3]
                university_year = certificate[4]
                university_certificate = certificate[5]
                university_gpa = certificate[6]

                # Set the fetched data to appropriate UI elements
                self.ui.employment_request_certificates_table.setItem(i, 0, QTableWidgetItem(str(id)))
                self.ui.employment_request_certificates_table.setItem(i, 1, QTableWidgetItem(str(university_certificate)))
                self.ui.employment_request_certificates_table.setItem(i, 2, QTableWidgetItem(str(university_name)))
                self.ui.employment_request_certificates_table.setItem(i, 3, QTableWidgetItem(str(university_specialty)))
                self.ui.employment_request_certificates_table.setItem(i, 4, QTableWidgetItem(str(university_year)))
                self.ui.employment_request_certificates_table.setItem(i, 5, QTableWidgetItem(str(university_gpa)))

    def addEmploymentRequestCertificate(self):
        university_name = self.ui.employment_request_university_name_input.text()
        university_certificate = self.ui.employment_request_university_certificate_input.text()
        university_year = self.ui.employment_request_university_year_input.text()
        university_specialty = self.ui.employment_request_university_specialty_input.text()
        university_gpa = self.ui.employment_request_university_gpa_input.text()
        selected_employment_request = self.ui.employment_requests_table.currentItem()
        if selected_employment_request is not None:
            selected_employment_request_id = self.ui.employment_requests_table.item(selected_employment_request.row(), 0).text()
            if university_certificate and university_certificate != '' and selected_employment_request_id and selected_employment_request_id != '':
                # Get currently selected employment request ID
                self.database_operations.addEmploymentRequestCertificate(selected_employment_request_id,university_name, university_certificate,university_year, university_specialty,university_gpa)
            self.fetchSelectedEmploymentRequest()

    def updateEmploymentRequest(self):
        selected_employment_request = self.ui.employment_requests_table.currentItem()
        if selected_employment_request is not None:
            selected_employment_request_id = self.ui.employment_requests_table.item(selected_employment_request.row(),0).text()

            # Read values from UI fields
            national_id = self.ui.employment_request_national_id_input.text()
            phone = self.ui.employment_request_phone_input.text()
            address = self.ui.employment_request_address_input.text()
            name = self.ui.employment_request_name_input.text()
            email = self.ui.employment_request_email_input.text()
            birthdate = self.ui.employment_request_birthdate_input.date().toString(Qt.ISODate)

            # Call database_operations.updateEmploymentRequest() with the read values
            self.database_operations.updateEmploymentRequest(selected_employment_request_id, national_id, phone,address, name, email, birthdate)

    def employ(self):
        selected_employment_request = self.ui.employment_requests_table.currentItem()
        if selected_employment_request is not None:
            selected_employment_request_id = self.ui.employment_requests_table.item(selected_employment_request.row(), 0).text()

            employee = self.database_operations.fetchEmployee(employment_request_id=selected_employment_request_id)
            if employee:
                resignation_date = employee['resignation_date']
                if resignation_date is None:
                    win32api.MessageBox(0, self.language_manager.translate('HR_ALERT_EMPLOYEE_ALREADY_EMPLOYED'), self.language_manager.translate('ERROR'))
                    return

            Ui_HR_Employ_Logic(self.sql_connector, selected_employment_request_id, self.independent).showUi()
            self.fetchEmployees('current', self.ui.employees_tree)
            self.fetchEmployees('current', self.ui.leaves_employees_tree)
            self.fetchEmployees('current', self.ui.extras_employees_tree)
            self.fetchEmployees('current', self.ui.loans_employees_tree)
            self.fetchEmployees('current', self.ui.salaries_employees_tree)

    def fetchEmployees(self, state, target_ui_element):
        color_light_green = QColor(204, 255, 204)
        brush_light_green = QBrush(color_light_green)
        color_light_blue = QColor(204, 229, 255)
        brush_light_blue = QBrush(color_light_blue)
        color_light_orange = QColor(255, 204, 153)
        brush_light_orange = QBrush(color_light_orange)
        target_ui_element.clear()
        employees_data = self.database_operations.fetchEmployees(state)
        if isinstance(target_ui_element, QTreeWidget):
            for employee_data in employees_data:
                position_id = employee_data['position_id']
                position_name = employee_data['position_name']
                employee_id = employee_data['id']
                employee_name = employee_data['name']
                department_id = employee_data['department_id']
                department_name = employee_data['department_name']
                department_already_in_tree = target_ui_element.findItems(str(department_id), Qt.MatchExactly | Qt.MatchRecursive, 0)  # 0 is the column index in which to search
                if not department_already_in_tree:
                    item = QTreeWidgetItem([str(department_id), str(department_name), '', '', '', '', ''])
                    for i in range(target_ui_element.columnCount()):
                        item.setBackground(i, brush_light_orange)
                    target_ui_element.addTopLevelItem(item)
                    # Get the index of the last top-level item
                    index = target_ui_element.topLevelItemCount() - 1
                    # Get the last top-level item
                    department_QTreeWidgetItem = target_ui_element.topLevelItem(index)
                    position_already_in_tree = []
                    for i in range(department_QTreeWidgetItem.childCount()):
                        child_item = department_QTreeWidgetItem.child(i)
                        if child_item.text(2) == str(position_id):
                            position_already_in_tree.append(child_item)
                    if not position_already_in_tree:
                        item = QTreeWidgetItem(['', '', str(position_id), str(position_name), '', '', ''])
                        for i in range(target_ui_element.columnCount()):
                            item.setBackground(i, brush_light_green)
                        department_QTreeWidgetItem.addChild(item)
                        position_QTreeWidgetItem = department_QTreeWidgetItem.child(
                            department_QTreeWidgetItem.childCount() - 1)
                        employee_already_in_tree = []
                        for i in range(position_QTreeWidgetItem.childCount()):
                            child_item = position_QTreeWidgetItem.child(i)
                            if child_item.text(4) == str(position_id):
                                position_already_in_tree.append(child_item)
                        if not employee_already_in_tree:
                            item = QTreeWidgetItem(['', '', '', '', str(employee_id), str(employee_name)])
                            for i in range(target_ui_element.columnCount()):
                                item.setBackground(i, brush_light_blue)
                            position_QTreeWidgetItem.addChild(item)
                    else:
                        position_QTreeWidgetItem = position_already_in_tree[0]
                        employee_already_in_tree = []
                        for i in range(position_QTreeWidgetItem.childCount()):
                            child_item = position_QTreeWidgetItem.child(i)
                            if child_item.text(4) == str(position_id):
                                position_already_in_tree.append(child_item)
                        if not employee_already_in_tree:
                            item = QTreeWidgetItem(['', '', '', '', str(employee_id), str(employee_name)])
                            for i in range(target_ui_element.columnCount()):
                                item.setBackground(i, brush_light_blue)
                            position_QTreeWidgetItem.addChild(item)
                else:
                    department_QTreeWidgetItem = department_already_in_tree[0]
                    position_already_in_tree = []
                    for i in range(department_QTreeWidgetItem.childCount()):
                        child_item = department_QTreeWidgetItem.child(i)
                        if child_item.text(2) == str(position_id):
                            position_already_in_tree.append(child_item)
                    if not position_already_in_tree:
                        item = QTreeWidgetItem(['', '', str(position_id), str(position_name), '', '', ''])
                        for i in range(target_ui_element.columnCount()):
                            item.setBackground(i, brush_light_green)
                        department_QTreeWidgetItem.addChild(item)
                        position_QTreeWidgetItem = department_QTreeWidgetItem.child(
                            department_QTreeWidgetItem.childCount() - 1)
                        employee_already_in_tree = []
                        for i in range(position_QTreeWidgetItem.childCount()):
                            child_item = position_QTreeWidgetItem.child(i)
                            if child_item.text(4) == str(position_id):
                                position_already_in_tree.append(child_item)
                        if not employee_already_in_tree:
                            item = QTreeWidgetItem(['', '', '', '', str(employee_id), str(employee_name)])
                            for i in range(target_ui_element.columnCount()):
                                item.setBackground(i, brush_light_blue)
                            position_QTreeWidgetItem.addChild(item)
                    else:
                        position_QTreeWidgetItem = position_already_in_tree[0]
                        employee_already_in_tree = []
                        for i in range(position_QTreeWidgetItem.childCount()):
                            child_item = position_QTreeWidgetItem.child(i)
                            if child_item.text(4) == str(position_id):
                                position_already_in_tree.append(child_item)
                        if not employee_already_in_tree:
                            item = QTreeWidgetItem(['', '', '', '', str(employee_id), str(employee_name)])
                            for i in range(target_ui_element.columnCount()):
                                item.setBackground(i, brush_light_blue)
                            position_QTreeWidgetItem.addChild(item)
        elif isinstance(target_ui_element, QComboBox):
            for employee_data in employees_data:
                # position_id = employee_data[0]
                # position_name = employee_data[1]
                employee_id = employee_data[2]
                employee_name = employee_data[3]
                # department_id = employee_data[4]
                # department_name = employee_data[5]
                target_ui_element.addItem(employee_name, employee_id)

    def fetchSelectedEmployee(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee is not None:
            selected_employee_id = selected_employee.text(4)
            if selected_employee_id and selected_employee_id != '':
                ### fetch employee info ###
                employee_info = self.database_operations.fetchEmployee(selected_employee_id)
                if employee_info:
                    id = employee_info['id']
                    employment_request_id = employee_info['employment_request_id']
                    national_id = employee_info['national_id']
                    phone = employee_info['phone']
                    address = employee_info['address']
                    name = employee_info['name']
                    email = employee_info['email']
                    birthdate = employee_info['birthdate']
                    start_date = employee_info['start_date']
                    resignation_date = employee_info['resignation_date']
                    bank = employee_info['bank']
                    bank_account_number = employee_info['bank_account_number']
                    bank_notes = employee_info['bank_notes']
                    position_id = employee_info['position_id']
                    position_name = employee_info['position_name']
                    department_id = employee_info['department_id']
                    department_name = employee_info['department_name']
                    photo = employee_info['photo']

                    if photo:
                        pixmap = QPixmap()
                        pixmap.loadFromData(photo)
                        self.ui.image_label.setPixmap(pixmap.scaled(self.ui.image_label.size(), Qt.KeepAspectRatio))
                    else:
                        self.ui.image_label.clear()

                    # Set values to QLineEdit widgets
                    self.ui.employee_name_input.setText(name)
                    self.ui.employee_address_input.setText(address)
                    self.ui.employee_national_id_input.setText(national_id)
                    self.ui.employee_phone_input.setText(phone)
                    self.ui.employee_email_input.setText(email)

                    # Convert string dates to QDate objects before setting them
                    if birthdate:
                        self.ui.employee_birthdate_input.setDate(QDate.fromString(str(birthdate), "yyyy-MM-dd"))
                    else:
                        self.ui.employee_birthdate_input.setDate(QDate.currentDate())

                    if start_date:
                        self.ui.employee_start_date_input.setDate(QDate.fromString(str(start_date), "yyyy-MM-dd"))
                    else:
                        self.ui.employee_start_date_input.setDate(QDate.currentDate())

                    # Set values to QComboBox widgets
                    self.ui.employee_department_combobox.setCurrentIndex(
                        self.ui.employee_department_combobox.findData(department_id))
                    self.ui.employee_position_combobox.setCurrentIndex(
                        self.ui.employee_position_combobox.findData(position_id))

                ### fetch employee transfer ###
                self.ui.employee_transfer_table.setRowCount(0)
                employee_transfers = self.database_operations.fetchEmployeeTransfers(selected_employee_id)
                for employee_transfer in employee_transfers:
                    id = employee_transfer['id']
                    date = employee_transfer['date_col']
                    position_id = employee_transfer['position_id']
                    position_name = employee_transfer['position_name']
                    department_id = employee_transfer['department_id']
                    department_name = employee_transfer['department_name']

                    # Create a empty row at bottom of table
                    numRows = self.ui.employee_transfer_table.rowCount()
                    self.ui.employee_transfer_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.employee_transfer_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.employee_transfer_table.setItem(numRows, 1, QTableWidgetItem(str(date)))
                    self.ui.employee_transfer_table.setItem(numRows, 2, QTableWidgetItem(str(department_name)))
                    self.ui.employee_transfer_table.setItem(numRows, 3, QTableWidgetItem(str(position_name)))

                ### fetch employee certificates ###
                self.ui.employee_certificates_table.setRowCount(0)
                employee_certificates = self.database_operations.fetchEmployeeCertificates(selected_employee_id)
                for certificate in employee_certificates:
                    id = certificate[0]
                    employee_id = certificate[1]
                    university_name = certificate[2]
                    university_specialty = certificate[3]
                    university_year = certificate[4]
                    university_certificate = certificate[5]
                    university_gpa = certificate[6]

                    numRows = self.ui.employee_certificates_table.rowCount()
                    self.ui.employee_certificates_table.insertRow(numRows)
                    self.ui.employee_certificates_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.employee_certificates_table.setItem(numRows, 1, QTableWidgetItem(str(university_certificate)))
                    self.ui.employee_certificates_table.setItem(numRows, 2, QTableWidgetItem(str(university_name)))
                    self.ui.employee_certificates_table.setItem(numRows, 3, QTableWidgetItem(str(university_specialty)))
                    self.ui.employee_certificates_table.setItem(numRows, 4, QTableWidgetItem(str(university_year)))
                    self.ui.employee_certificates_table.setItem(numRows, 5, QTableWidgetItem(str(university_gpa)))

                ### fetch employee course ###
                self.ui.employee_courses_table.setRowCount(0)
                employee_courses = self.database_operations.fetchEmployeeCourses(selected_employee_id)
                for course in employee_courses:
                    id = course['id']
                    title = course['title']
                    providor = course['provider']
                    date = course['date_col']
                    gpa = course['gpa']

                    numRows = self.ui.employee_courses_table.rowCount()
                    self.ui.employee_courses_table.insertRow(numRows)
                    self.ui.employee_courses_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.employee_courses_table.setItem(numRows, 1, QTableWidgetItem(str(title)))
                    self.ui.employee_courses_table.setItem(numRows, 2, QTableWidgetItem(str(providor)))
                    self.ui.employee_courses_table.setItem(numRows, 3, QTableWidgetItem(str(date)))
                    self.ui.employee_courses_table.setItem(numRows, 4, QTableWidgetItem(str(gpa)))

                ### fetch employee received items ###
                self.ui.employee_received_items_table.setRowCount(0)
                received_items = self.database_operations.fetchEmployeeReceivedItems(selected_employee_id)
                for received_item in received_items:
                    id = received_item['id']
                    employee_id = received_item['employee_id']
                    warehouse_id = received_item['warehouse_id']
                    material_id = received_item['material_id']
                    quantity = received_item['quantity']
                    unit_id = received_item['unit_id']
                    received_date = received_item['received_date']
                    employee_name = received_item['employee_name']
                    warehouse_name = received_item['warehouse_name']
                    material_name = received_item['material_name']
                    quantity = received_item['quantity']
                    unit_name = received_item['unit_name']
                    received_date = received_item['received_date']
                    received = received_item['received']

                    numRows = self.ui.employee_received_items_table.rowCount()
                    self.ui.employee_received_items_table.insertRow(numRows)
                    self.ui.employee_received_items_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.employee_received_items_table.setItem(numRows, 1, QTableWidgetItem(str(warehouse_id)))
                    self.ui.employee_received_items_table.setItem(numRows, 2, QTableWidgetItem(str(warehouse_name)))
                    self.ui.employee_received_items_table.setItem(numRows, 3, QTableWidgetItem(str(material_id)))
                    self.ui.employee_received_items_table.setItem(numRows, 4, QTableWidgetItem(str(material_name)))
                    self.ui.employee_received_items_table.setItem(numRows, 5, QTableWidgetItem(str(quantity)))
                    self.ui.employee_received_items_table.setItem(numRows, 6, QTableWidgetItem(str(unit_id)))
                    self.ui.employee_received_items_table.setItem(numRows, 7, QTableWidgetItem(str(unit_name)))
                    self.ui.employee_received_items_table.setItem(numRows, 8, QTableWidgetItem(str(received_date) if received_date is not None else ''))
                    self.ui.employee_received_items_table.setItem(numRows, 9, QTableWidgetItem('yes' if received else 'no'))

                ### fetch employee finance info ###
                self.ui.employee_bank_input.clear()
                self.ui.employee_bank_account_number_input.clear()
                self.ui.employee_bank_notes_input.clear()
                self.ui.employee_salary_input.clear()
                self.ui.employee_insurance_input.clear()
                finance_info = self.database_operations.fetchEmployeeFinanceInfo(selected_employee_id)
                if finance_info:
                    bank = finance_info['bank'] or ''
                    bank_account_number = finance_info['bank_account_number'] or ''
                    bank_notes = finance_info['bank_notes'] or ''
                    salary = finance_info['salary']
                    cycle = finance_info['salary_cycle']
                    currency = finance_info['salary_currency']
                    insurance = finance_info['insurance'] or ''
                    salary_account_id = finance_info['salary_account_id']
                    salary_opposite_account_id = finance_info['salary_opposite_account_id']
                    insurance_account_id = finance_info['insurance_account_id']
                    insurance_opposite_account_id = finance_info['insurance_opposite_account_id']
                    insurance_currency = finance_info['insurance_currency']
                    insurance_cycle = finance_info['insurance_cycle']

                    self.ui.employee_bank_input.setText(str(bank))
                    self.ui.employee_bank_account_number_input.setText(str(bank_account_number))
                    self.ui.employee_bank_notes_input.setText(str(bank_notes))
                    self.ui.employee_salary_input.setText(str(salary))
                    self.ui.employee_insurance_input.setText(str(insurance))
                    self.ui.employee_salary_currency_combobox.setCurrentIndex(
                        self.ui.employee_salary_currency_combobox.findData(currency))
                    self.ui.employee_insurance_currency_combobox.setCurrentIndex(
                        self.ui.employee_insurance_currency_combobox.findData(insurance_currency))
                    self.ui.employee_salary_cycle_combobox.setCurrentIndex(
                        self.ui.employee_salary_cycle_combobox.findData(str(cycle)))
                    self.ui.employee_salary_account_combobox.setCurrentIndex(
                        self.ui.employee_salary_account_combobox.findData(str(salary_account_id)))
                    self.ui.employee_salary_opposite_account_combobox.setCurrentIndex(
                        self.ui.employee_salary_opposite_account_combobox.findData(str(salary_opposite_account_id)))
                    self.ui.employee_insurance_account_combobox.setCurrentIndex(
                        self.ui.employee_insurance_account_combobox.findData(str(insurance_account_id)))
                    self.ui.employee_insurance_opposite_account_combobox.setCurrentIndex(
                        self.ui.employee_insurance_opposite_account_combobox.findData(str(insurance_opposite_account_id)))
                    self.ui.employee_insurance_currency_combobox.setCurrentIndex(
                        self.ui.employee_insurance_currency_combobox.findData(insurance_currency))
                    self.ui.employee_insurance_cycle_combobox.setCurrentIndex(
                        self.ui.employee_insurance_cycle_combobox.findData(insurance_cycle))

    def fetchDepartments(self):
        self.ui.employee_department_combobox.clear()
        departments = self.database_operations.fetchDepartments()
        self.ui.departments_table.setRowCount(0)
        self.ui.new_additional_costs_department_combobox.clear()
        for department in departments:
            id = department[0]
            name = department[1]
            self.ui.employee_department_combobox.addItem(name, id)

            numRows = self.ui.departments_table.rowCount()
            self.ui.departments_table.insertRow(numRows)
            self.ui.departments_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.departments_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

            self.ui.new_additional_costs_department_combobox.addItem(name, id)

    def fetchPositions(self):
        self.ui.positions_table.setRowCount(0)
        self.ui.employee_position_combobox.clear()
        positions = self.database_operations.fetchPositions()
        for position in positions:
            id = position['id']
            name = position['position_name']
            self.ui.employee_position_combobox.addItem(name, id)

            numRows = self.ui.positions_table.rowCount()
            self.ui.positions_table.insertRow(numRows)
            self.ui.positions_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.positions_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

    def fetchCurrencies(self):
        self.ui.loan_subbract_currency_combobox.addItem('%', '%')
        self.ui.salaries_discount_addition_currency_combobox.addItem('%', '%')

        currencies = self.database_operations.fetchCurrencies()
        # Clear all currency comboboxes before adding data
        self.ui.employee_salary_currency_combobox.clear()
        self.ui.employee_insurance_currency_combobox.clear()
        self.ui.department_additions_discounts_currency_combobox.clear()
        self.ui.position_additions_discounts_currency_combobox.clear()
        self.ui.position_currency_combobox.clear()
        self.ui.department_extra_currency_combobox.clear()
        self.ui.position_currency_combobox_2.clear()
        self.ui.loan_currency_combobox.clear()
        self.ui.loan_subbract_currency_combobox.clear()
        self.ui.loan_direct_pay_currency_combobox.clear()
        self.ui.new_additional_costs_currency_combobox.clear()
        self.ui.extra_currency_combobox.clear()
        self.ui.salaries_discount_addition_currency_combobox.clear()

        for currencie in currencies:
            id = currencie['id']
            display_text = currencie['name']

            # Now add the currency items to each combobox
            self.ui.employee_salary_currency_combobox.addItem(display_text, id)
            self.ui.employee_insurance_currency_combobox.addItem(display_text, id)
            self.ui.department_additions_discounts_currency_combobox.addItem(display_text, id)
            self.ui.position_additions_discounts_currency_combobox.addItem(display_text, id)
            self.ui.position_currency_combobox.addItem(display_text, id)
            self.ui.department_extra_currency_combobox.addItem(display_text, id)
            self.ui.position_currency_combobox_2.addItem(display_text, id)
            self.ui.loan_currency_combobox.addItem(display_text, id)
            self.ui.loan_subbract_currency_combobox.addItem(display_text, id)
            self.ui.loan_direct_pay_currency_combobox.addItem(display_text, id)
            self.ui.new_additional_costs_currency_combobox.addItem(display_text, id)
            self.ui.extra_currency_combobox.addItem(display_text, id)
            self.ui.salaries_discount_addition_currency_combobox.addItem(display_text, id)

    def setSalaryCycles(self):
        self.ui.employee_salary_cycle_combobox.addItem(self.language_manager.translate( 'HOUR'), "hour")
        self.ui.employee_salary_cycle_combobox.addItem(self.language_manager.translate( 'DAY'), "day")
        self.ui.employee_salary_cycle_combobox.addItem(self.language_manager.translate( 'WEEK'), "week")
        self.ui.employee_salary_cycle_combobox.addItem(self.language_manager.translate( 'MONTH'), "month")

        self.ui.employee_insurance_cycle_combobox.addItem(self.language_manager.translate( 'HOUR'), "hour")
        self.ui.employee_insurance_cycle_combobox.addItem(self.language_manager.translate( 'DAY'), "day")
        self.ui.employee_insurance_cycle_combobox.addItem(self.language_manager.translate( 'WEEK'), "week")
        self.ui.employee_insurance_cycle_combobox.addItem(self.language_manager.translate( 'MONTH'), "month")


    def setWeekDays(self):
        # Define the week days in Arabic and English
        week_days = [
            {"text": self.language_manager.translate('SUNDAY'), "value": "sunday"},
            {"text": self.language_manager.translate('MONDAY'), "value": "monday"},
            {"text": self.language_manager.translate('TUESDAY'), "value": "tuesday"},
            {"text": self.language_manager.translate('WEDNESDAY'), "value": "wednesday"},
            {"text": self.language_manager.translate('THURSDAY'), "value": "thursday"},
            {"text": self.language_manager.translate('FRIDAY'), "value": "friday"},
            {"text": self.language_manager.translate('SATURDAY'), "value": "saturday"},
        ]

        # Clear the existing items in the combo box
        self.ui.setting_week_start_day_combobox.clear()

        # Add the week days to the combo box
        for day in week_days:
            self.ui.setting_week_start_day_combobox.addItem(day["text"], day["value"])

    def saveEmployeeInfo(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee and selected_employee != '':
            # Read values from QLineEdit inputs
            employee_name = self.ui.employee_name_input.text()
            employee_email = self.ui.employee_email_input.text()
            employee_address = self.ui.employee_address_input.text()
            employee_phone = self.ui.employee_phone_input.text()
            employee_national_id = self.ui.employee_national_id_input.text()
            selected_employee_id = selected_employee.text(4)
            # Read values from QComboBoxes
            employee_position = self.ui.employee_position_combobox.currentData()
            employee_department = self.ui.employee_department_combobox.currentData()

            # Read values from QDateEdit inputs in Qt.ISODate format
            employee_birthdate = self.ui.employee_birthdate_input.date().toString(Qt.ISODate)
            employee_start_date = self.ui.employee_start_date_input.date().toString(Qt.ISODate)

            self.database_operations.saveEmployee(selected_employee_id, employee_name, employee_email, employee_address, employee_phone, employee_national_id, employee_position, employee_department, employee_birthdate, employee_start_date)

            self.fetchEmployees('current', self.ui.employees_tree)
            self.fetchEmployees('current', self.ui.leaves_employees_tree)
            self.fetchEmployees('current', self.ui.extras_employees_tree)
            self.fetchEmployees('current', self.ui.loans_employees_tree)
            self.fetchEmployees('current', self.ui.salaries_employees_tree)

    def addEmployeeCertificate(self):
        university_name = self.ui.employee_university_name_input.text()
        university_certificate = self.ui.employee_university_certificate_input.text()
        university_year = self.ui.employee_university_year_input.text()
        university_specialty = self.ui.employee_university_specialty_input.text()
        university_gpa = self.ui.employee_university_gpa_input.text()
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = selected_employee.text(4)
            if university_certificate and university_certificate != '':
                self.database_operations.addEmployeeCertificate(selected_employee_id, university_name,university_certificate,university_year, university_specialty,university_gpa)

                self.ui.employee_university_name_input.clear()
                self.ui.employee_university_certificate_input.clear()
                self.ui.employee_university_year_input.clear()
                self.ui.employee_university_specialty_input.clear()
                self.ui.employee_university_gpa_input.clear()

    def removeEmployeeCertificate(self):
        message = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message == IDYES:
            selected_employee_certificate = self.ui.employee_certificates_table.currentItem()
            if selected_employee_certificate is not None:
                selected_employee_certificate_id = self.ui.employee_certificates_table.item(selected_employee_certificate.row(), 0).text()
                self.database_operations.removeEmployeeCertificate(selected_employee_certificate_id)
                self.fetchSelectedEmployee()

    def addEmployeeCourse(self):
        selected_employee = self.ui.employees_tree.currentItem()
        gpa = self.ui.employee_course_gpa_input.text()
        course_id = self.ui.employee_course_combobox.currentData()
        if selected_employee and selected_employee != '':
            selected_employee_id = selected_employee.text(4)
            if selected_employee_id and selected_employee_id != '' and course_id and gpa and gpa != '':
                self.database_operations.addCourseEmployee(course_id, selected_employee_id, gpa)
                self.ui.employee_course_gpa_input.clear()
                self.fetchSelectedEmployee()
            else:
                win32api.MessageBox(0, self.language_manager.translate('INVALID_DATA'), self.language_manager.translate('ALERT'))

    def removeSelectedEmployeeCourse(self):
        message = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message == IDYES:
            selected_employee_course = self.ui.employee_courses_table.currentItem()
            if selected_employee_course is not None:
                selected_employee_course_id = self.ui.employee_courses_table.item(selected_employee_course.row(), 0).text()
                self.database_operations.removeCourseEmployee(selected_employee_course_id)
                self.fetchSelectedEmployee()


    def saveEmployeeFinanceInfo(self):
        selected_employee = self.ui.employees_tree.currentItem()
        if selected_employee and selected_employee != '':
            selected_employee_id = selected_employee.text(4)
            if selected_employee_id and selected_employee_id != '':
                try:
                    selected_employee_id = int(selected_employee_id)
                    employee_bank_input = self.ui.employee_bank_input.text()
                    employee_bank_account_number = self.ui.employee_bank_account_number_input.text()
                    employee_bank_notes = self.ui.employee_bank_notes_input.text()
                    employee_salary = self.ui.employee_salary_input.text()
                    employee_insurance = self.ui.employee_insurance_input.text()

                    employee_salary_currency = self.ui.employee_salary_currency_combobox.currentData()
                    employee_salary_cycle = self.ui.employee_salary_cycle_combobox.currentData()
                    employee_salary_start_date = self.ui.employee_salary_start_date_input.date().toString(Qt.ISODate)

                    employee_insurance_cycle = self.ui.employee_insurance_cycle_combobox.currentData()
                    employee_insurance_start_date = self.ui.employee_insurance_start_date_input.date().toString(Qt.ISODate)

                    employee_salary_account = self.ui.employee_salary_account_combobox.currentData()
                    employee_salary_opposite_account = self.ui.employee_salary_opposite_account_combobox.currentData()

                    employee_insurance_account = self.ui.employee_insurance_account_combobox.currentData()
                    employee_insurance_opposite_account = self.ui.employee_insurance_opposite_account_combobox.currentData()
                    self.database_operations.saveEmployeeFinanceInfo(selected_employee_id, employee_bank_input, employee_bank_account_number, employee_bank_notes, employee_salary, employee_insurance, employee_salary_currency, employee_salary_cycle, employee_salary_account, employee_salary_opposite_account, employee_insurance_account, employee_insurance_opposite_account, employee_salary_start_date, employee_insurance_cycle, employee_insurance_start_date)
                    win32api.MessageBox(0, self.language_manager.translate('SAVED_SUCCESSFULLY'), self.language_manager.translate('ALERT'))


                except Exception as e:
                    print(e)
                    win32api.MessageBox(0, self.language_manager.translate('INVALID_DATA'), self.language_manager.translate('ALERT'))


    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]

            self.ui.employee_salary_account_combobox.addItem(display_text, id)
            self.ui.employee_salary_opposite_account_combobox.addItem(display_text, id)

            self.ui.employee_insurance_account_combobox.addItem(display_text, id)
            self.ui.employee_insurance_opposite_account_combobox.addItem(display_text, id)

            self.ui.new_departments_account_combobox.addItem(display_text, id)
            self.ui.new_departments_opposite_account_combobox.addItem(display_text, id)
            self.ui.departments_account_combobox.addItem(display_text, id)
            self.ui.departments_opposite_account_combobox.addItem(display_text, id)

            self.ui.department_additions_discounts_account_combobox.addItem(display_text, id)
            self.ui.department_additions_discounts_opposite_account_combobox.addItem(display_text, id)

            self.ui.department_extra_account_combobox.addItem(display_text, id)
            self.ui.department_extra_opposite_account_combobox.addItem(display_text, id)

            self.ui.position_additions_discounts_account_combobox.addItem(display_text, id)
            self.ui.position_additions_discounts_opposite_account_combobox.addItem(display_text, id)

            self.ui.loan_account_combobox.addItem(display_text, id)
            self.ui.loan_opposite_account_combobox.addItem(display_text, id)

            self.ui.new_additional_costs_account_combobox.addItem(display_text, id)
            self.ui.new_additional_costs_opposite_account_combobox.addItem(display_text, id)

            self.ui.setting_insurance_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_default_account_combobox.addItem(display_text, id)
            self.ui.setting_additional_costs_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_additions_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_additions_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_salaries_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_additions_account_combobox.addItem(display_text, id)
            self.ui.setting_salaries_account_combobox.addItem(display_text, id)
            self.ui.setting_additions_account_combobox.addItem(display_text, id)
            self.ui.setting_discounts_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_default_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_discounts_account_combobox.addItem(display_text, id)
            self.ui.setting_discounts_account_combobox.addItem(display_text, id)
            self.ui.setting_additional_costs_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_courses_costs_account_combobox.addItem(display_text, id)
            self.ui.setting_courses_costs_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_loans_account_combobox.addItem(display_text, id)
            self.ui.setting_departments_discounts_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_loans_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_insurance_account_combobox.addItem(display_text, id)
            self.ui.setting_extra_account_combobox.addItem(display_text, id)
            self.ui.setting_extra_opposite_account_combobox.addItem(display_text, id)
            self.ui.setting_resource_recipients_account_combobox.addItem(display_text, id)

            self.ui.extra_account_combobox.addItem(display_text, id)
            self.ui.extra_opposite_account_combobox.addItem(display_text, id)

            self.ui.salaries_discount_addition_account_combobox.addItem(display_text, id)
            self.ui.salaries_discount_addition_opposite_account_combobox.addItem(display_text, id)

    def mirrorInputs(self, first_input, *inputs):
        print(type(first_input))
        for input_ in inputs:
            if isinstance(input_, QLineEdit) and isinstance(first_input, QLineEdit):
                value = first_input.text()
                input_.setText(value)
            elif isinstance(input_, QComboBox) and isinstance(first_input, QComboBox):
                input_.setCurrentIndex(input_.findData(first_input.currentData()))

    def addNewDepartment(self):
        name = self.ui.new_departments_name_input.text()
        day_hours = self.ui.new_departments_day_hours_input.text()
        account = self.ui.new_departments_account_combobox.currentData()
        opposite_account = self.ui.new_departments_opposite_account_combobox.currentData()
        notes = self.ui.new_departments_notes_input.text()

        # work_day_saturday = self.database_operations.fetchHRSetting('setting_work_day_saturday')[0]
        # work_day_sunday = self.database_operations.fetchHRSetting('setting_work_day_sunday')[0]
        # work_day_monday = self.database_operations.fetchHRSetting('setting_work_day_monday')[0]
        # work_day_tuesday = self.database_operations.fetchHRSetting('setting_work_day_tuesday')[0]
        # work_day_wednesday = self.database_operations.fetchHRSetting('setting_work_day_wednesday')[0]
        # work_day_thursday = self.database_operations.fetchHRSetting('setting_work_day_thursday')[0]
        # work_day_friday = self.database_operations.fetchHRSetting('setting_work_day_friday')[0]

        if name and name != '' and day_hours and day_hours != '':
            self.database_operations.addNewDepartment(name, day_hours, account, opposite_account, notes)
            self.fetchDepartments()
            self.ui.new_departments_name_input.clear()
            self.ui.new_departments_day_hours_input.clear()
            self.ui.new_departments_notes_input.clear()

    def fetchSelectedDepartment(self):
        self.ui.departments_name_input.clear()
        self.ui.departments_notes_input.clear()
        self.ui.departments_day_hours_input.clear()
        self.ui.department_discounts_additions_table.setRowCount(0)
        self.ui.department_leaves_table.setRowCount(0)

        selected_department = self.ui.departments_table.currentItem()
        if selected_department is not None:
            selected_department_id = self.ui.departments_table.item(selected_department.row(), 0).text()
            if selected_department_id and selected_department_id != '':
                # Fetch department info
                department_info = self.database_operations.fetchDepartment(selected_department_id)
                if department_info:
                    id = department_info['id']
                    name = department_info['name']
                    day_hours = department_info['day_hours']
                    account_id = department_info['account_id']
                    opposite_account_id = department_info['opposite_account_id']
                    notes = department_info['notes']
                    workday_saturday = department_info['work_day_saturday']
                    workday_sunday = department_info['work_day_sunday']
                    workday_monday = department_info['work_day_monday']
                    workday_tuesday = department_info['work_day_tuesday']
                    workday_wednesday = department_info['work_day_wednesday']
                    workday_thursday = department_info['work_day_thursday']
                    workday_friday = department_info['work_day_friday']

                    # Update UI elements with fetched department info
                    self.ui.departments_name_input.setText(str(name))
                    self.ui.departments_day_hours_input.setText(str(day_hours))
                    self.ui.departments_account_combobox.setCurrentIndex(
                        self.ui.departments_account_combobox.findData(account_id))
                    self.ui.departments_opposite_account_combobox.setCurrentIndex(
                        self.ui.departments_opposite_account_combobox.findData(opposite_account_id))
                    self.ui.departments_notes_input.setText(str(notes))

                    if workday_saturday:
                        self.ui.departments_work_day_saturday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_saturday_checkbox.setChecked(False)

                    if workday_sunday:
                        self.ui.departments_work_day_sunday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_sunday_checkbox.setChecked(False)

                    if workday_monday:
                        self.ui.departments_work_day_monday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_monday_checkbox.setChecked(False)

                    if workday_tuesday:
                        self.ui.departments_work_day_tuesday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_tuesday_checkbox.setChecked(False)

                    if workday_wednesday:
                        self.ui.departments_work_day_wednesday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_wednesday_checkbox.setChecked(False)

                    if workday_thursday:
                        self.ui.departments_work_day_thursday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_thursday_checkbox.setChecked(False)

                    if workday_friday:
                        self.ui.departments_work_day_friday_checkbox.setChecked(True)
                    else:
                        self.ui.departments_work_day_friday_checkbox.setChecked(False)

                department_discounts_additions = self.database_operations.fetchDepartmentDiscountsAdditions(
                    selected_department_id)
                for department_discounts_addition in department_discounts_additions:
                    id = department_discounts_addition['id']
                    department_id = department_discounts_addition['department_id']
                    statement = department_discounts_addition['statement_col']
                    type = department_discounts_addition['type_col']
                    value = department_discounts_addition['value_col']
                    currency_id = department_discounts_addition['currency_id']
                    start_date = department_discounts_addition['start_date']
                    end_date = department_discounts_addition['end_date']
                    account_id = department_discounts_addition['account_id'] or ''
                    opposite_account_id = department_discounts_addition['opposite_account_id'] or ''
                    # date = department_discounts_addition['date']
                    currency_name = department_discounts_addition['currency_name']
                    account = department_discounts_addition['account'] or ''
                    opposite_account = department_discounts_addition['opposite_account'] or ''

                    # Create a empty row at bottom of table
                    numRows = self.ui.department_discounts_additions_table.rowCount()
                    self.ui.department_discounts_additions_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.department_discounts_additions_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 1, QTableWidgetItem(str(type)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 2,MyTableWidgetItem(str(value), float(value)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 3, QTableWidgetItem(str(currency_id)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 4,QTableWidgetItem(str(currency_name)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 5, QTableWidgetItem(str(statement)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 6, QTableWidgetItem(str(start_date)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 7, QTableWidgetItem(str(end_date)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 8, QTableWidgetItem(str(account_id)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 9, QTableWidgetItem(str(account)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 10, QTableWidgetItem(str(opposite_account_id)))
                    self.ui.department_discounts_additions_table.setItem(numRows, 11, QTableWidgetItem(str(opposite_account)))
                    # self.ui.department_discounts_additions_table.setItem(numRows, 11, QTableWidgetItem(str(date)))

                department_leaves = self.database_operations.fetchDepartmentLeaves(selected_department_id)
                for department_leave in department_leaves:
                    id = department_leave[0]
                    department_id = department_leave[1]
                    statement = department_leave[2]
                    duration_in_hours = department_leave[3]
                    duration_in_days = department_leave[4]
                    start_date = department_leave[5]
                    date = department_leave[6]

                    # Create a empty row at bottom of table
                    numRows = self.ui.department_leaves_table.rowCount()
                    self.ui.department_leaves_table.insertRow(numRows)

                    self.ui.department_leaves_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                    self.ui.department_leaves_table.setItem(numRows, 1, QTableWidgetItem(str(statement)))
                    self.ui.department_leaves_table.setItem(numRows, 2, MyTableWidgetItem(str(duration_in_hours), float(duration_in_hours)))
                    self.ui.department_leaves_table.setItem(numRows, 3, MyTableWidgetItem(str(duration_in_days),float(duration_in_days)))
                    self.ui.department_leaves_table.setItem(numRows, 4, QTableWidgetItem(str(start_date)))
                    self.ui.department_leaves_table.setItem(numRows, 5, QTableWidgetItem(str(date)))

    def saveDepartment(self):
        department_name = self.ui.departments_name_input.text()
        department_day_hours = self.ui.departments_day_hours_input.text()
        department_account = self.ui.departments_account_combobox.currentData() or ''
        department_opposite_account = self.ui.departments_opposite_account_combobox.currentData() or ''
        department_notes = self.ui.departments_notes_input.text()

        departments_work_day_friday = int(self.ui.departments_work_day_friday_checkbox.isChecked())
        departments_work_day_tuesday = int(self.ui.departments_work_day_tuesday_checkbox.isChecked())
        departments_work_day_thursday = int(self.ui.departments_work_day_thursday_checkbox.isChecked())
        departments_work_day_wednesday = int(self.ui.departments_work_day_wednesday_checkbox.isChecked())
        departments_work_day_monday = int(self.ui.departments_work_day_monday_checkbox.isChecked())
        departments_work_day_sunday = int(self.ui.departments_work_day_sunday_checkbox.isChecked())
        departments_work_day_saturday = int(self.ui.departments_work_day_saturday_checkbox.isChecked())

        selected_department = self.ui.departments_table.currentItem()
        if selected_department is not None:
            selected_department_id = self.ui.departments_table.item(selected_department.row(),0).text()
            if department_name and department_name != '' and department_day_hours and department_day_hours != '' and selected_department_id and selected_department_id != '':
                # Call the saveDepartment function in database_operations module with the extracted values
                self.database_operations.saveDepartment(selected_department_id, department_name, department_day_hours,
                                                        department_account,
                                                        department_opposite_account,
                                                        department_notes, departments_work_day_friday,
                                                        departments_work_day_tuesday, departments_work_day_thursday,
                                                        departments_work_day_wednesday, departments_work_day_monday,
                                                        departments_work_day_sunday, departments_work_day_saturday)

                self.ui.departments_work_day_saturday_checkbox.setChecked(False)
                self.ui.departments_work_day_sunday_checkbox.setChecked(False)
                self.ui.departments_work_day_monday_checkbox.setChecked(False)
                self.ui.departments_work_day_tuesday_checkbox.setChecked(False)
                self.ui.departments_work_day_wednesday_checkbox.setChecked(False)
                self.ui.departments_work_day_thursday_checkbox.setChecked(False)
                self.ui.departments_work_day_friday_checkbox.setChecked(False)

    def removeSelectedDepartmentLeave(self):
        selected_department_leave = self.ui.department_leaves_table.currentItem()
        if selected_department_leave is not None:
            selected_department_leave_id = self.ui.department_leaves_table.item(selected_department_leave.row(), 0).text()
            if selected_department_leave_id and selected_department_leave_id != '':
                self.database_operations.removeDepartmentLeave(selected_department_leave_id)
                self.fetchSelectedDepartment()


    def setDisountsAdditionsType(self):
        self.ui.department_additions_discounts_type_combobox.addItem(self.language_manager.translate( "HR_DEPARTMENT_ADDITIONS_DISCOUNTS_TYPE_ADD"), 'addition')
        self.ui.department_additions_discounts_type_combobox.addItem(self.language_manager.translate( "HR_DEPARTMENT_ADDITIONS_DISCOUNTS_TYPE_REDUCE"), 'discount')
        self.ui.position_additions_discounts_type_combobox.addItem(self.language_manager.translate( "HR_POSITION_ADDITIONS_DISCOUNTS_TYPE_ADD"), 'addition')
        self.ui.position_additions_discounts_type_combobox.addItem(self.language_manager.translate( "HR_POSITION_ADDITIONS_DISCOUNTS_TYPE_REDUCE"), 'discount')

    def saveDepartmentFinance(self):
        departments_additions_discounts_currency = self.ui.department_additions_discounts_currency_combobox.currentData()
        departments_additions_discounts_statement = self.ui.department_additions_discounts_statement_input.text()
        departments_additions_discounts_value = self.ui.department_additions_discounts_value_input.text()
        departments_additions_discounts_start_date = self.ui.department_additions_discounts_start_date_input.date().toString(
            Qt.ISODate)
        departments_additions_discounts_end_date = self.ui.department_additions_discounts_end_date_input.date().toString(
            Qt.ISODate)
        departments_additions_discounts_account = self.ui.department_additions_discounts_account_combobox.currentData()
        departments_additions_discounts_opposite_account = self.ui.department_additions_discounts_opposite_account_combobox.currentData()
        departments_additions_discounts_type = self.ui.department_additions_discounts_type_combobox.currentData()

        selected_department = self.ui.departments_table.currentItem()
        if selected_department is not None:
            selected_department_id = self.ui.departments_table.item(selected_department.row(), 0).text()
            if departments_additions_discounts_value and departments_additions_discounts_value != '' and selected_department_id and selected_department_id != '':
                self.database_operations.saveDepartmentFinance(selected_department_id,departments_additions_discounts_currency,departments_additions_discounts_statement, departments_additions_discounts_value,departments_additions_discounts_start_date,departments_additions_discounts_end_date, departments_additions_discounts_type,departments_additions_discounts_account,departments_additions_discounts_opposite_account)



    def setHoursAndDays(self, target_unit, target_ui_element, conversion_value_source='default'):
        day_hours = 0
        if conversion_value_source == 'default':
            print("DEFAULT")
            day_hours_data = self.database_operations.fetchHRSetting('setting_day_hours')
            if day_hours_data:
                day_hours = day_hours_data['value_col']
            else:
                print("Unable to fetch default day hours")
                return
        else:
            if isinstance(conversion_value_source, QTableWidget):
                selected_department = conversion_value_source.currentItem()
                if selected_department:
                    selected_department_id = conversion_value_source.item(selected_department.row(), 0).text()
                    if selected_department_id:
                        department = self.database_operations.fetchDepartment(selected_department_id)
                        day_hours = department['day_hours']
                    else:
                        print("Unable to fetch department info for day/hours conversion")
                        return
            elif isinstance(conversion_value_source, QTreeWidget):
                selected_item = conversion_value_source.currentItem()
                # Traverse the tree upwards to get the root element
                if selected_item:
                    parent_item = selected_item
                    while parent_item.parent() is not None:
                        parent_item = parent_item.parent()
                    # Get the root element's text
                    selected_department_id = parent_item.text(0)
                    if selected_department_id:
                        department = self.database_operations.fetchDepartment(selected_department_id)
                        day_hours = department['day_hours']
                    else:
                        print("Unable to fetch department info for day/hours conversion")
                        return
                else:
                    print("Unable to fetch department info for day/hours conversion")
                    return
            else:
                print("Unable to set hours/days")
                return

        source = self.sender().text()
        if not day_hours:
            return
        if source and source.lower().strip() and source.isdigit():
            if target_unit == 'day':
                # Calculate days by dividing hours by day_hours, keeping the exact decimal
                target_value = float(source) / float(day_hours)
                # Round to 3 decimal places without additional rounding logic
                target_value = round(target_value, 3)

            elif target_unit == 'hour':
                # Calculate hours by multiplying days by day_hours
                target_value = float(source) * float(day_hours)
                # Round to 3 decimal places without additional rounding logic
                target_value = round(target_value, 3)
            else:
                target_value = ''

            if target_value and target_ui_element:
                target_ui_element.setText(str(target_value))

    def saveDepartmentLeave(self):
        selected_department = self.ui.departments_table.currentItem()
        if selected_department is not None:
            selected_department_id = self.ui.departments_table.item(selected_department.row(), 0).text()
            department_leave_statement = self.ui.department_leaves_statement_input.text()
            department_leave_duration_hours = float(self.ui.department_leaves_duration_hours_input.text())
            department_leave_duration_days = float(self.ui.department_leaves_duration_days_input.text())
            department_leave_start_date = self.ui.department_leaves_start_date_input.date().toString(Qt.ISODate)
            if department_leave_duration_hours:
                self.database_operations.saveDepartmentLeave(selected_department_id, department_leave_statement,
                                                             department_leave_duration_hours,
                                                             department_leave_duration_days,
                                                             department_leave_start_date)

    def removeDepartmentAdditionAndDiscount(self):
        selected_department_additions_discounts = self.ui.department_discounts_additions_table.currentItem()
        if selected_department_additions_discounts is not None:
            message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), MB_YESNO)
            if message_result == IDYES:
                selected_department_additions_discounts_id = self.ui.department_discounts_additions_table.item(selected_department_additions_discounts.row(), 0).text()
                self.database_operations.removeDepartmentAdditionAndDiscount(int(selected_department_additions_discounts_id))
                self.fetchSelectedDepartment()

    def fetchSelectedPosition(self):
        self.ui.position_name_input.clear()
        self.ui.position_notes_input.clear()
        self.ui.position_salary_input.clear()
        self.ui.position_leaves_table.setRowCount(0)
        self.ui.position_discounts_additions_table.setRowCount(0)

        selected_position = self.ui.positions_table.currentItem()
        if selected_position is not None:
            selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
            if selected_position_id and selected_position_id != '':
                # Fetch position info
                position_info = self.database_operations.fetchPosition(selected_position_id)
                if position_info:
                    id = position_info['id']
                    name = position_info['position_name']
                    salary = position_info['salary']
                    currency_id = position_info['currency_id']
                    notes = position_info['notes']
                    currency_name = position_info['currency_name']

                    # Update UI elements with fetched position info
                    self.ui.position_name_input.setText(str(name))
                    self.ui.position_salary_input.setText(str(salary))
                    self.ui.position_currency_combobox.setCurrentIndex(
                        self.ui.position_currency_combobox.findData(currency_id))
                    self.ui.position_notes_input.setText(str(notes))

                position_discounts_additions = self.database_operations.fetchPositionDiscountsAdditions(
                    selected_position_id)
                for position_discounts_addition in position_discounts_additions:
                    id = position_discounts_addition['id']
                    position_id = position_discounts_addition['position_id']
                    statement = position_discounts_addition['statement_col']
                    type = position_discounts_addition['type_col']
                    value = position_discounts_addition['value_col']
                    currency_id = position_discounts_addition['currency_id']
                    start_date = position_discounts_addition['start_date']
                    end_date = position_discounts_addition['end_date']
                    account_id = position_discounts_addition['account_id'] or ''
                    opposite_account_id = position_discounts_addition['opposite_account_id'] or ''
                    date = position_discounts_addition['date_col']
                    currency_name = position_discounts_addition['currency_name']
                    account = position_discounts_addition['account'] or ''
                    opposite_account = position_discounts_addition['opposite_account'] or ''

                    # Create a empty row at bottom of table
                    numRows = self.ui.position_discounts_additions_table.rowCount()
                    self.ui.position_discounts_additions_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.position_discounts_additions_table.setItem(numRows, 0,MyTableWidgetItem(str(id), int(id)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 1, QTableWidgetItem(str(type)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 2, MyTableWidgetItem(str(value), float(value)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 3, QTableWidgetItem(str(currency_id)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 4,QTableWidgetItem(str(currency_name)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 5, QTableWidgetItem(str(statement)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 6, QTableWidgetItem(str(start_date)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 7, QTableWidgetItem(str(end_date)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 8, QTableWidgetItem(str(account_id)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 8, QTableWidgetItem(str(account)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 9, QTableWidgetItem(str(opposite_account_id)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 10, QTableWidgetItem(str(opposite_account)))
                    self.ui.position_discounts_additions_table.setItem(numRows, 11, QTableWidgetItem(str(date)))

                    self.fetchPositionLeaves()



    def savePositionLeave(self):
        selected_position = self.ui.positions_table.currentItem()
        if selected_position is not None:
            selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
            position_leave_statement = self.ui.position_leaves_statement_input.text()
            position_leave_duration_hours = float(self.ui.position_leaves_duration_hours_input.text())
            position_leave_duration_days = float(self.ui.position_leaves_duration_days_input.text())
            position_leave_start_date = self.ui.position_leaves_start_date_input.date().toString(Qt.ISODate)
            if position_leave_duration_hours:
                self.database_operations.savePositionLeave(selected_position_id, position_leave_statement,position_leave_duration_hours,position_leave_duration_days,position_leave_start_date)
                self.fetchPositionLeaves()
                self.ui.position_additions_discounts_value_input.clear()
                self.ui.position_additions_discounts_statement_input.clear()

    def fetchPositionLeaves(self):
        self.ui.position_leaves_table.setRowCount(0)
        selected_position = self.ui.positions_table.currentItem()
        if selected_position is not None:
            selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
            position_leaves = self.database_operations.fetchPositionLeaves(selected_position_id)
            for position_leave in position_leaves:
                id = position_leave['id']
                position_id = position_leave['position_id']
                statement = position_leave['statement_col']
                duration_in_hours = position_leave['duration_in_hours']
                duration_in_days = position_leave['duration_in_days']
                start_date = position_leave['start_date']
                date = position_leave['date_col']

                numRows = self.ui.position_leaves_table.rowCount()
                self.ui.position_leaves_table.insertRow(numRows)

                self.ui.position_leaves_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.position_leaves_table.setItem(numRows, 1, QTableWidgetItem(str(statement)))
                self.ui.position_leaves_table.setItem(numRows, 2, QTableWidgetItem(str(duration_in_hours)))
                self.ui.position_leaves_table.setItem(numRows, 3, QTableWidgetItem(str(duration_in_days)))
                self.ui.position_leaves_table.setItem(numRows, 4, QTableWidgetItem(str(start_date)))
                self.ui.position_leaves_table.setItem(numRows, 5, QTableWidgetItem(str(date)))



    def savePositionFinance(self):
        positions_additions_discounts_currency = self.ui.position_additions_discounts_currency_combobox.currentData()
        positions_additions_discounts_statement = self.ui.position_additions_discounts_statement_input.text()
        positions_additions_discounts_value = self.ui.position_additions_discounts_value_input.text()
        positions_additions_discounts_start_date = self.ui.position_additions_discounts_start_date_input.date().toString(
            Qt.ISODate)
        positions_additions_discounts_end_date = self.ui.position_additions_discounts_end_date_input.date().toString(
            Qt.ISODate)
        positions_additions_discounts_account = self.ui.position_additions_discounts_account_combobox.currentData() or ''
        positions_additions_discounts_opposite_account = self.ui.position_additions_discounts_opposite_account_combobox.currentData() or ''
        positions_additions_discounts_type = self.ui.position_additions_discounts_type_combobox.currentData()

        selected_position = self.ui.positions_table.currentItem()
        if selected_position is not None:
            selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
            if positions_additions_discounts_value and positions_additions_discounts_value != '' and selected_position_id and selected_position_id != '':
                self.database_operations.savePositionFinance(selected_position_id,positions_additions_discounts_currency, positions_additions_discounts_statement,positions_additions_discounts_value,positions_additions_discounts_start_date,positions_additions_discounts_end_date,positions_additions_discounts_type,positions_additions_discounts_account,positions_additions_discounts_opposite_account)

                self.fetchSelectedPosition()


    def addNewPosition(self):
        position_name = self.ui.new_position_name_input.text()
        position_salary = self.ui.new_position_salary_input.text()
        position_salary_currency = self.ui.position_currency_combobox_2.currentData()
        position_notes = self.ui.new_position_notes_input.text()
        if position_name != '' and position_salary != '':
            self.database_operations.addNewPosition(position_name, position_salary, position_salary_currency, position_notes)
            self.ui.new_position_name_input.clear()
            self.ui.new_position_salary_input.clear()
            self.ui.new_position_notes_input.clear()
            self.fetchPositions()
        else:
            win32api.MessageBox(0, self.language_manager.translate('HR_ALERT_ENTER_POSITION_NAME_SALARY'), self.language_manager.translate('ALERT'))

    def removeSelectedPosition(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_position = self.ui.positions_table.currentItem()
            if selected_position is not None:
                selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
                self.database_operations.removePosition(int(selected_position_id))
                self.fetchPositions()

    def removeSelectedPositionFinance(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_position_additions_discounts = self.ui.position_discounts_additions_table.currentItem()
            if selected_position_additions_discounts is not None:
                selected_position_additions_discounts_id = self.ui.position_discounts_additions_table.item(selected_position_additions_discounts.row(), 0).text()
                self.database_operations.removePositionFinance(int(selected_position_additions_discounts_id))
                self.fetchSelectedPosition()

    def removeSelectedPositionLeave(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate( 'DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_position_leave = self.ui.position_leaves_table.currentItem()
            if selected_position_leave is not None:
                selected_position_leave_id = self.ui.position_leaves_table.item(selected_position_leave.row(), 0).text()
                self.database_operations.removePositionLeave(int(selected_position_leave_id))
                self.fetchSelectedPosition()

    def openPositionReportWindow(self):
        position_id = self.ui.positions_table.currentItem()
        if position_id:
            position_id = self.ui.positions_table.item(position_id.row(), 0).text()
            Ui_Position_Report_Logic(self.sql_connector, position_id).showUi()

    def savePosition(self):
        position_name = self.ui.position_name_input.text()
        position_salary = self.ui.position_salary_input.text()
        position_salary_currency = self.ui.position_currency_combobox.currentData()
        position_notes = self.ui.position_notes_input.text()

        selected_position = self.ui.positions_table.currentItem()
        if selected_position is not None:
            selected_position_id = self.ui.positions_table.item(selected_position.row(), 0).text()
            if position_name and position_name != '':
                # Call the savePosition function in database_operations module with the extracted values
                self.database_operations.savePosition(selected_position_id, position_name, position_salary,position_salary_currency, position_notes)

    def fetchSelectedEmployeeLeaves(self):
        self.ui.leaves_table.setRowCount(0)
        selected_tree_row = self.ui.leaves_employees_tree.currentItem()
        selected_employee_id = selected_tree_row.text(4)
        if selected_employee_id and selected_employee_id != '':

            employee_leave_info = self.database_operations.fetchEmployeeLeaves(selected_employee_id)
            if employee_leave_info:
                for data in employee_leave_info:
                    id = data['id']
                    employee_id = data['employee_id']
                    type = data['type_name']
                    alternative_id = data['alternative_id']
                    duration_in_hours = data['duration_in_hours']
                    duration_in_days = data['duration_in_days']
                    start_date = data['start_date']
                    date = data['date_col']
                    state = data['state_col']
                    employee_name = data['employee_name']
                    alternative_employee_name = data['alternative_employee_name']

                    # Create a empty row at bottom of table
                    numRows = self.ui.leaves_table.rowCount()
                    self.ui.leaves_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.leaves_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.leaves_table.setItem(numRows, 1, QTableWidgetItem(str(type)))
                    self.ui.leaves_table.setItem(numRows, 2, QTableWidgetItem(str(start_date)))
                    self.ui.leaves_table.setItem(numRows, 3,MyTableWidgetItem(str(duration_in_hours), float(duration_in_hours)))
                    self.ui.leaves_table.setItem(numRows, 4,MyTableWidgetItem(str(duration_in_days), float(duration_in_days)))
                    self.ui.leaves_table.setItem(numRows, 5, QTableWidgetItem(str(alternative_id)))
                    self.ui.leaves_table.setItem(numRows, 6, QTableWidgetItem(str(alternative_employee_name)))
                    self.ui.leaves_table.setItem(numRows, 7, QTableWidgetItem(str(date)))
                    self.ui.leaves_table.setItem(numRows, 8, QTableWidgetItem(str(state)))

            self.ui.leave_alternative_combobox.clear()
            employees = self.database_operations.fetchEmployees(state='current', exclude_id=selected_employee_id)
            for employee in employees:
                employee_id = employee['id']
                employee_name = employee['name']
                self.ui.leave_alternative_combobox.addItem(str(employee_name), employee_id)

    def fetchEmployeeLeavesBalance(self):
        selected_tree_row = self.ui.leaves_employees_tree.currentItem()
        selected_employee_id = selected_tree_row.text(4)
        if selected_employee_id and selected_employee_id != '':
            leaves_balance = self.database_operations.fetchEmployeeLeavesBalance(selected_employee_id)  # dictionary
            paid_balance = leaves_balance['paid_balance']
            unpaid_balance = leaves_balance['unpaid_balance']

            self.ui.paid_leave_remaining_days_balance_input.setText(str(paid_balance))
            self.ui.unpaid_leave_remaining_days_balance_input.setText(str(unpaid_balance))

    def saveLeave(self):
        selected_tree_row = self.ui.leaves_employees_tree.currentItem()
        selected_employee = selected_tree_row
        if selected_employee and selected_employee != '':
            # Get the selected leave type
            selected_employee_id = selected_employee.text(4)
            leave_type_data = self.ui.leave_type_combobox.currentData()
            alternative_id = self.ui.leave_alternative_combobox.currentData()
            if not leave_type_data or not alternative_id:
                win32api.MessageBox(0, self.language_manager.translate('INVALID_DATA'), self.language_manager.translate('ERROR'))
                return
            leave_type_id = leave_type_data[0]
            leave_type_duration = leave_type_data[1]
            leave_type_paid = leave_type_data[2]
            duration_in_hours = self.ui.actual_leave_duration_hours_input.text()
            duration_in_days = self.ui.actual_leave_duration_days_input.text()
            start_date = self.ui.leave_start_input.date().toString(Qt.ISODate)

            if duration_in_hours and duration_in_hours.strip() != '' and duration_in_days and duration_in_days.strip() != '':
                # Check for overlapping leaves
                employee_leaves = self.database_operations.fetchEmployeeLeaves(selected_employee_id)

                # Calculate end date for new leave
                new_leave_start = datetime.strptime(start_date, "%Y-%m-%d")
                new_leave_end = new_leave_start + timedelta(days=float(duration_in_days))

                # Check for overlapping leaves
                has_overlap = False
                for leave in employee_leaves:
                    existing_leave_start = datetime.strptime(str(leave['start_date']), "%Y-%m-%d")
                    existing_leave_end = existing_leave_start + timedelta(days=float(leave['duration_in_days'] - 1))

                    # Check if date ranges overlap
                    if (new_leave_start <= existing_leave_end and new_leave_end >= existing_leave_start):
                        has_overlap = True
                        break

                if has_overlap:
                    win32api.MessageBox(0, self.language_manager.translate('LEAVE_DATE_OVERLAP'),self.language_manager.translate('ERROR'))
                else:
                    self.database_operations.saveLeave(selected_employee_id, leave_type_id, alternative_id, duration_in_hours, duration_in_days, start_date)
                    self.ui.leave_duration_hours_input.clear()
                    self.ui.leave_duration_days_input.clear()
                    self.ui.actual_leave_duration_hours_input.clear()
                    self.ui.actual_leave_duration_days_input.clear()
                    self.ui.unpaid_leave_remaining_days_balance_input.clear()
                    self.ui.paid_leave_remaining_days_balance_input.clear()


    def removeSelectedLeave(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate("HR_LEAVE_DELETE"), self.language_manager.translate("ALERT"), MB_YESNO)
        if message_result == IDYES:
            selected_leave = self.ui.leaves_table.currentItem()
            if selected_leave is not None:
                selected_leave_id = self.ui.leaves_table.item(selected_leave.row(), 0).text()
                self.database_operations.removeLeave(int(selected_leave_id))
                self.fetchSelectedEmployeeLeaves()

    def fetchCourses(self):
        self.ui.employee_course_combobox.clear()
        self.ui.courses_table.setRowCount(0)
        courses = self.database_operations.fetchCourses()
        for course in courses:
            id = course[0]
            title = course[1]
            # providor = course[2]
            # account_id = course[3]
            # opposite_account_id = course[4]
            # cost = course[5]
            # currency_id = course[6]
            date = course[7]
            # location = course[8]
            # account_name = course[9]
            # opposite_account = course[10]

            # Create a empty row at bottom of table
            numRows = self.ui.courses_table.rowCount()
            self.ui.courses_table.insertRow(numRows)

            # Add text to the row
            self.ui.courses_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.courses_table.setItem(numRows, 1, QTableWidgetItem(str(title)))
            self.ui.courses_table.setItem(numRows, 2, QTableWidgetItem(str(date)))

            self.ui.employee_course_combobox.addItem(str(title), id)

    def openSelectCourseEmployeeWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'current_employees')
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def openAddNewCourseWindow(self):
        add_new_course_window = Ui_Course_View_Logic(self.sql_connector, independent=self.independent)
        add_new_course_window.showUi()
        self.fetchCourses()

    def openCourseViewWindow(self):
        selected_course = self.ui.courses_table.currentItem()
        if selected_course is not None:
            selected_course_id = self.ui.courses_table.item(selected_course.row(), 0).text()
            if selected_course_id and selected_course_id != '':
                course_view_window = Ui_Course_View_Logic(self.sql_connector, int(selected_course_id) , self.independent)
                course_view_window.showUi()
                self.fetchCourses()

    def removeCourse(self):
        selected_course = self.ui.courses_table.currentItem()
        if selected_course is not None:
            selected_course_id = self.ui.courses_table.item(selected_course.row(), 0).text()
            course_employees = self.database_operations.fetchCourseEmployees(selected_course_id)
            if course_employees:
                win32api.MessageBox(0, self.language_manager.translate('COURSE_EMPLOYEES_EXIST'), self.language_manager.translate('ERROR'))
                return
            if selected_course_id and selected_course_id != '':
                message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), MB_YESNO)
                if message_result == IDYES:
                    self.database_operations.removeCourse(int(selected_course_id))
                    self.fetchCourses()

    def addCourseEmployee(self):
        employee_id = self.ui.course_employees_combobox.currentData()
        gpa = self.ui.course_employee_gpa_input.text()
        selected_course = self.ui.courses_table.currentItem()
        if selected_course is not None:
            selected_course_id = self.ui.courses_table.item(selected_course.row(), 0).text()
            if selected_course_id and selected_course_id != '' and employee_id and gpa and gpa != '':
                self.database_operations.addCourseEmployee(selected_course_id, employee_id, gpa)
            else:
                win32api.MessageBox(0, self.language_manager.translate('INVALID_DATA'), self.language_manager.translate('ALERT'))

    def removeCourseEmployee(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_course_employee = self.ui.course_employees_table.currentItem()
            if selected_course_employee is not None:
                selected_course_employee_id = self.ui.course_employees_table.item(selected_course_employee.row(), 0).text()
                self.database_operations.removeCourseEmployee(int(selected_course_employee_id))
                self.fetchCourseEmployees()

    def fetchCourseEmployees(self):
        selected_course = self.ui.courses_table.currentItem()
        if selected_course is not None:
            selected_course_id = self.ui.courses_table.item(selected_course.row(), 0).text()
            self.ui.course_employees_table.setRowCount(0)
            course_employees = self.database_operations.fetchCourseEmployees(selected_course_id)
            for course_employees in course_employees:
                id = course_employees[0]
                course_id = course_employees[1]
                employee_id = course_employees[2]
                gpa = course_employees[3]
                employee_name = course_employees[4]

                # Create a empty row at bottom of table
                numRows = self.ui.course_employees_table.rowCount()
                self.ui.course_employees_table.insertRow(numRows)

                # Add text to the row
                self.ui.course_employees_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.course_employees_table.setItem(numRows, 1, QTableWidgetItem(str(employee_id)))
                self.ui.course_employees_table.setItem(numRows, 2, QTableWidgetItem(str(employee_name)))
                self.ui.course_employees_table.setItem(numRows, 3, MyTableWidgetItem(str(gpa), float(gpa)))

    def updateCourseEmployeeGpa(self):
        course_employee = self.ui.course_employees_table.currentItem()
        if course_employee is not None:
            course_employee_id = self.ui.course_employees_table.item(course_employee.row(), 0).text()
            old_gpa = self.ui.course_employees_table.item(course_employee.row(), 3).text()
        new_gpa, ok_pressed = QInputDialog.getDouble(None, self.language_manager.translate("HR_ENTER_NEW_GPA"), self.language_manager.translate("GPA"), value=float(old_gpa),decimals=2)
        if ok_pressed:
            if new_gpa:
                self.database_operations.updateCourseEmployeeGpa(course_employee_id, new_gpa)

    def activateLoanSubtract(self):
        if self.ui.loan_subtract_checkbox.isChecked():
            self.ui.loan_subbract_currency_combobox.setDisabled(False)
            self.ui.loan_subtract_value.setDisabled(False)
        else:
            self.ui.loan_subbract_currency_combobox.setDisabled(True)
            self.ui.loan_subtract_value.setDisabled(True)

    def setEmployeeLoansDefaults(self):
        selected_employee_id = self.ui.loans_employees_tree.currentItem().text(4)
        # check if subtracted value is less than employee's salary
        employee_finance_info = self.database_operations.fetchEmployeeFinanceInfo(selected_employee_id)
        if employee_finance_info:
            # bank = employee_finance_info[0]
            # bank_account_number = employee_finance_info[1]
            # bank_notes = employee_finance_info[2]
            salary = employee_finance_info[3]
            salary_cycle = employee_finance_info[4]
            salary_currency = employee_finance_info[5]
            # insurance = employee_finance_info[6]
            # salary_account_id = employee_finance_info[7]
            # salary_opposite_account_id = employee_finance_info[8]
            # insurance_account_id = employee_finance_info[9]
            # insurance_opposite_account_id = employee_finance_info[10]
            # insurance_currency = employee_finance_info[11]
            # insurance_cycle = employee_finance_info[12]

            if salary and salary_cycle and salary_currency:
                self.ui.add_loan_groupbox.setEnabled(True)
                for i in range(self.ui.loan_currency_combobox.count()):
                    # item_text = self.ui.loan_currency_combobox.itemText(i)
                    item_data = self.ui.loan_currency_combobox.itemData(i)
                    if str(salary_currency) != str(item_data):  # disable the item
                        self.ui.loan_currency_combobox.model().item(i).setEnabled(False)
                    else:
                        self.ui.loan_currency_combobox.model().item(i).setEnabled(True)
                        self.ui.loan_currency_combobox.setCurrentIndex(i)

                for i in range(self.ui.loan_subbract_currency_combobox.count()):
                    # item_text = self.ui.loan_currency_combobox.itemText(i)
                    item_data = self.ui.loan_subbract_currency_combobox.itemData(i)
                    if str(salary_currency) not in [str(item_data), '%']:
                        self.ui.loan_subbract_currency_combobox.model().item(i).setEnabled(False)
                    else:
                        self.ui.loan_subbract_currency_combobox.model().item(i).setEnabled(True)
                        self.ui.loan_subbract_currency_combobox.setCurrentIndex(i)

            else:
                win32api.MessageBox(0, self.language_manager.translate( 'INSURANCE_ALERT_NO_SALARY_DATA'), self.language_manager.translate( 'ALERT'))

    def addLoan(self):
        selected_employee = self.ui.loans_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = selected_employee.text(4)
            employee_name = selected_employee.text(5)
            # check if subtracted value is less than employee's salary
            employee_finance_info = self.database_operations.fetchEmployeeFinanceInfo(selected_employee_id)
            if employee_finance_info:
                # bank = employee_finance_info['bank']
                # bank_account_number = employee_finance_info['bank_account_number']
                # bank_notes = employee_finance_info['bank_notes']
                salary = employee_finance_info['salary']
                salary_cycle = employee_finance_info['salary_cycle']
                salary_currency = employee_finance_info['salary_currency']
                # insurance = employee_finance_info['insurance']
                # salary_account_id = employee_finance_info['salary_account_id']
                # salary_opposite_account_id = employee_finance_info['salary_opposite_account_id']
                # insurance_account_id = employee_finance_info['insurance_account_id']
                # insurance_opposite_account_id = employee_finance_info['insurance_opposite_account_id']
                # insurance_currency = employee_finance_info['insurance_currency']
                # insurance_cycle = employee_finance_info['insurance_cycle']

                loan_value = self.ui.loan_value_input.text()
                loan_currency = self.ui.loan_currency_combobox.currentData()
                loan_date = self.ui.loan_date_input.date().toString(Qt.ISODate)
                loan_account = self.ui.loan_account_combobox.currentData() or ''
                loan_opposite_account = self.ui.loan_opposite_account_combobox.currentData() or ''
                loan_subtract = int(self.ui.loan_subtract_checkbox.isChecked())  # casting bool to int results in 0 or 1
                loan_subtract_value = self.ui.loan_subtract_value.text()
                loan_subtract_currency = self.ui.loan_subbract_currency_combobox.currentData()

                if not selected_employee_id:
                    return
                else:
                    if not loan_value:
                        self.ui.loan_value_input.clear()
                        msg = self.language_manager.translate("HR_ENTER_LOAN_VALUE")
                        win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                        return
                    else:
                        if not loan_subtract:
                            loan_subtract_currency = loan_currency
                        else:
                            if loan_subtract_value:
                                if loan_subtract_currency == '%':  # in this case subtract currency should be null
                                    loan_subtract_currency = ''
                                    if loan_subtract_value and float(loan_subtract_value) > 100:
                                        win32api.MessageBox(0, self.language_manager.translate( 'INSURANCE_ALERT_LOAN_PERCENTAGE_GREATER_THAN_100'), self.language_manager.translate( 'ALERT'))
                                        return

                                    # check if the percentage of the salary is less than the value of the loan
                                    subtract_value_of_salary_after_percentage = float(salary) * float(loan_subtract_value) / 100
                                    if subtract_value_of_salary_after_percentage > float(loan_value):
                                        msg = "لا يمكن ان تكون قيمة الخصم اكبر من السلفة نفسها. الراتب: " + str(
                                            salary) + "قيمة الخصم:" + str(subtract_value_of_salary_after_percentage)
                                        win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                                        return

                                    loan_subtract = subtract_value_of_salary_after_percentage
                                else:
                                    if float(loan_subtract_value) > float(salary):
                                        msg = self.language_manager.translate( 'INSURANCE_ALERT_LOAN_VALUE_GREATER_THAN_SALARY')
                                        win32api.MessageBox(0, msg, self.language_manager.translate( 'ALERT'))
                                        return
                            else:
                                win32api.MessageBox(0, self.language_manager.translate( 'INSURANCE_ALERT_ENTER_LOAN_VALUE'), self.language_manager.translate( 'ALERT'))
                                return

                        loan_id = self.database_operations.addHRLoan(selected_employee_id, loan_value, loan_currency, loan_date,loan_account, loan_opposite_account, loan_subtract,loan_subtract_value, loan_subtract_currency,salary_cycle)

                        if not self.independent: # only create a journal entry if HR is NOT running independently
                            if loan_id:
                                statment = self.language_manager.translate( 'HR_LOAN_FOR_EMPLOYEE') + employee_name

                                entry_id = self.database_operations.addJournalEntry(loan_date, loan_currency, 'employee_loan', loan_id)
                                if entry_id:
                                    self.database_operations.addJournalEntryItem(entry_id, loan_currency, 'creditor',statment, loan_account, loan_opposite_account, loan_value)

            else:
                win32api.MessageBox(0, self.language_manager.translate( 'HR_ALERT_ENTER_POSITION_NAME_SALARY'), self.language_manager.translate('ALERT'))

            self.ui.loan_value_input.clear()
            self.ui.loan_subtract_value.clear()
            self.fetchEmployeeLoans()

    def fetchEmployeeLoans(self):
        selected_employee_id = self.ui.loans_employees_tree.currentItem().text(4)
        if selected_employee_id:
            employee_loans = self.database_operations.fetchLoansOfEmployee(selected_employee_id)
            self.ui.loans_table.setRowCount(len(employee_loans))
            self.ui.loans_combobox.clear()  # clear the combobox before adding new items
            for i, employee_loan in enumerate(employee_loans):
                id = employee_loan['id']
                employee_id = employee_loan['employee_id']
                value = employee_loan['value_col']
                currency = employee_loan['currency']
                date = employee_loan['date_col']
                account_id = employee_loan['account_id']
                opposite_account_id = employee_loan['opposite_account_id']
                periodically_subtract_from_salary = employee_loan['periodically_subtract_from_salary']
                subtract_currency = employee_loan['subtract_currency']
                subtract_cycle = employee_loan['subtract_cycle']
                subtract_value = employee_loan['subtract_value']
                currency_name = employee_loan['currency_name']
                account_name = employee_loan['account_name']
                opposite_account_name = employee_loan['opposite_account_name']
                total_payments = employee_loan['total_payments']
                remaining_amount = employee_loan['remaining_amount']
                subtract_currency_name = employee_loan['subtract_currency_name']

                # Add the loan to the table
                self.ui.loans_table.setItem(i, 0, QTableWidgetItem(str(id)))
                self.ui.loans_table.setItem(i, 1, QTableWidgetItem(str(date)))
                self.ui.loans_table.setItem(i, 2, QTableWidgetItem(str(value)))
                self.ui.loans_table.setItem(i, 3, QTableWidgetItem(str(currency)))
                self.ui.loans_table.setItem(i, 4, QTableWidgetItem(str(currency_name)))
                self.ui.loans_table.setItem(i, 5, QTableWidgetItem(str(account_id)))
                self.ui.loans_table.setItem(i, 6, QTableWidgetItem(str(account_name)))
                self.ui.loans_table.setItem(i, 7, QTableWidgetItem(str(opposite_account_id)))
                self.ui.loans_table.setItem(i, 8, QTableWidgetItem(str(opposite_account_name)))
                self.ui.loans_table.setItem(i, 9, QTableWidgetItem(self.language_manager.translate("YES") if periodically_subtract_from_salary else self.language_manager.translate("NO")))
                self.ui.loans_table.setItem(i, 10, QTableWidgetItem(str(subtract_cycle)))
                self.ui.loans_table.setItem(i, 11, QTableWidgetItem(str(subtract_currency_name)))
                self.ui.loans_table.setItem(i, 12, QTableWidgetItem(str(subtract_value)))
                self.ui.loans_table.setItem(i, 13, QTableWidgetItem(str(remaining_amount)))

                # Add the loan to the combobox
                loan_text = f"{date} - ({value} {currency_name})"
                loan_data = [id, value, currency, subtract_currency, subtract_currency_name, remaining_amount]
                self.ui.loans_combobox.addItem(loan_text, loan_data)

    def fetchLoanPayments(self):
        selected_row_index = self.ui.loans_table.currentRow()
        if selected_row_index >= 0:
            loan_id = int(self.ui.loans_table.item(selected_row_index, 0).text())
            loan_payments = self.database_operations.fetchHRLoanPayments(loan_id)
            self.ui.loan_payments_table.setRowCount(len(loan_payments))
            for i, loan_payment in enumerate(loan_payments):
                id = loan_payment[0]
                loan_id = loan_payment[1]
                value = loan_payment[2]
                currency = loan_payment[3]
                source = loan_payment[4]
                date = loan_payment[5]
                currency_name = loan_payment[6]
                self.ui.loan_payments_table.setItem(i, 0, QTableWidgetItem(str(id)))
                self.ui.loan_payments_table.setItem(i, 1, QTableWidgetItem(str(value)))
                self.ui.loan_payments_table.setItem(i, 2, QTableWidgetItem(currency_name))
                self.ui.loan_payments_table.setItem(i, 3, QTableWidgetItem(str(date)))
                self.ui.loan_payments_table.setItem(i, 4, QTableWidgetItem(source))
        else:
            self.ui.loan_payments_table.setRowCount(0)

    def setPaymentCurrency(self):
        # get data from loans_combobox
        data = self.ui.loans_combobox.currentData()
        if data:
            loan_currency = data[2]
            loan_subtract_currency = data[3]
            if not loan_subtract_currency:
                loan_subtract_currency = loan_currency
            # Loop through the currency combobox items and disable all except the one with the same value as currency
            for j in range(self.ui.loan_direct_pay_currency_combobox.count()):
                if self.ui.loan_direct_pay_currency_combobox.itemData(j) == loan_subtract_currency:
                    self.ui.loan_direct_pay_currency_combobox.setCurrentIndex(j)
                else:
                    self.ui.loan_direct_pay_currency_combobox.model().item(j).setEnabled(False)

    def removeLoan(self):
        selected_row_index = self.ui.loans_table.currentRow()
        if selected_row_index >= 0:
            loan_id = int(self.ui.loans_table.item(selected_row_index, 0).text())
            self.database_operations.removeHRLoan(loan_id)
            self.fetchEmployeeLoans()

    def addLoanPayment(self):
        loan_data = self.ui.loans_combobox.currentData()
        if loan_data:
            loan_id = loan_data[0]
            loan_value = loan_data[1]
            loan_currency = loan_data[2]
            subtract_currency = loan_data[3]
            subtract_currency_name = loan_data[4]
            loan_remaining_value = loan_data[5]

            date = self.ui.load_direct_pay_date_input.dateTime().toString(Qt.ISODate)
            value = self.ui.loan_direct_pay_value_input.text()
            currency = self.ui.loan_direct_pay_currency_combobox.currentData()

            if value:
                if (loan_currency == currency):

                    if float(value) <= float(
                            loan_remaining_value):  # loan_remaining_value is None means no payemnts made yet
                        self.database_operations.addHRLoanPayment(loan_id, value, currency, 'direct', date)
                        self.fetchLoanPayments()
                    else:
                        msg = "الدفعة اكبر من القيمة المتبقية للقرض. القيمة المتبقية " + str(
                            loan_remaining_value) + " " + str(subtract_currency_name)
                        win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                        return
                    self.ui.loan_direct_pay_value_input.clear()
                    self.ui.loan_direct_pay_currency_combobox.setCurrentIndex(0)
                    self.ui.load_direct_pay_date_input.setDate(QDate.currentDate())
                else:
                    return  # this should never happen
            else:
                win32api.MessageBox(0, self.language_manager.translate('INSURANCE_ALERT_ENTER_PAYMENT_VALUE'), self.language_manager.translate('ALERT'))
                return

    def fetchAdditionalCosts(self):
        self.ui.additional_costs_table.setRowCount(0)
        additional_costs = self.database_operations.fetchAdditionalCosts()
        for additional_cost in additional_costs:
            id = additional_cost['id']
            statement = additional_cost['statement_col']
            account_id = additional_cost['account_id'] or ''
            department_id = additional_cost['department_id']
            opposite_account_id = additional_cost['opposite_account_id'] or ''
            value = additional_cost['value_col']
            currency_id = additional_cost['currency_id']
            date = additional_cost['date_col']
            state = additional_cost['state_col']
            currency_name = additional_cost['currency_name']
            account_name = additional_cost['account_name'] or ''
            opposite_account_name = additional_cost['opposite_account_name'] or ''
            department_name = additional_cost['department_name'] or ''

            row_position = self.ui.additional_costs_table.rowCount()
            self.ui.additional_costs_table.insertRow(row_position)

            self.ui.additional_costs_table.setItem(row_position, 0, QTableWidgetItem(str(id)))
            self.ui.additional_costs_table.setItem(row_position, 1, QTableWidgetItem(str(date)))
            self.ui.additional_costs_table.setItem(row_position, 2, QTableWidgetItem(str(statement)))
            self.ui.additional_costs_table.setItem(row_position, 3, QTableWidgetItem(str(department_id)))
            self.ui.additional_costs_table.setItem(row_position, 4, QTableWidgetItem(str(department_name)))
            self.ui.additional_costs_table.setItem(row_position, 5, QTableWidgetItem(str(value)))
            self.ui.additional_costs_table.setItem(row_position, 6, QTableWidgetItem(str(currency_id)))
            self.ui.additional_costs_table.setItem(row_position, 7, QTableWidgetItem(str(currency_name)))
            self.ui.additional_costs_table.setItem(row_position, 8, QTableWidgetItem(str(account_id)))
            self.ui.additional_costs_table.setItem(row_position, 9, QTableWidgetItem(str(account_name)))
            self.ui.additional_costs_table.setItem(row_position, 10, QTableWidgetItem(str(opposite_account_id)))
            self.ui.additional_costs_table.setItem(row_position, 11, QTableWidgetItem(str(opposite_account_name)))
            self.ui.additional_costs_table.setItem(row_position, 12, QTableWidgetItem(str(state)))

    def addAditionalCosts(self):
        account = self.ui.new_additional_costs_account_combobox.currentData()
        opposite_account = self.ui.new_additional_costs_opposite_account_combobox.currentData()
        date = self.ui.new_additional_costs_date_input.date().toString(Qt.ISODate)
        currency = self.ui.new_additional_costs_currency_combobox.currentData()
        department = self.ui.new_additional_costs_department_combobox.currentData()
        statement = self.ui.new_additionl_costs_statemnet_input.text()
        value = self.ui.new_additional_costs_value_input.text()

        if statement and value:
            self.database_operations.addAdditionalCost(account, opposite_account, date, currency, department, statement,value)
            self.ui.new_additionl_costs_statemnet_input.clear()
            self.ui.new_additional_costs_value_input.clear()
            self.fetchAdditionalCosts()

            if not self.independent:
                entry_id = self.database_operations.addJournalEntry(entry_date=date, currency=currency, origin_type='additional_cost', origin_id=id)

                if entry_id:
                    self.database_operations.addJournalEntryItem(journal_entry_id=entry_id,currency=currency,type_col='creditor',account=account,opposite_account= opposite_account,statement= statement,value=value)



    def removeSelectedAdditionalCost(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_additional_cost = self.ui.additional_costs_table.currentItem()
            if selected_additional_cost is not None:
                selected_additional_cost_id = self.ui.additional_costs_table.item(selected_additional_cost.row(), 0).text()
                self.database_operations.removeAdditionalCost(int(selected_additional_cost_id))
                self.fetchAdditionalCosts()

    def saveSettings(self):
        setting_cycle_unused_leaves = int(self.ui.setting_cycle_unused_leaves_checkbox.isChecked())
        setting_week_start_day = self.ui.setting_week_start_day_combobox.currentData()
        setting_day_hours = self.ui.setting_day_hours_input.text()

        setting_work_day_sunday = int(self.ui.setting_work_day_sunday_checkbox.isChecked())
        setting_work_day_monday = int(self.ui.setting_work_day_monday_checkbox.isChecked())
        setting_work_day_tuesday = int(self.ui.setting_work_day_tuesday_checkbox.isChecked())
        setting_work_day_wednesday = int(self.ui.setting_work_day_wednesday_checkbox.isChecked())
        setting_work_day_thursday = int(self.ui.setting_work_day_thursday_checkbox.isChecked())
        setting_work_day_friday = int(self.ui.setting_work_day_friday_checkbox.isChecked())
        setting_work_day_saturday = int(self.ui.setting_work_day_saturday_checkbox.isChecked())

        setting_insurance_opposite_account = self.ui.setting_insurance_opposite_account_combobox.currentData()
        setting_departments_default_account = self.ui.setting_departments_default_account_combobox.currentData()
        setting_additional_costs_account = self.ui.setting_additional_costs_account_combobox.currentData()
        setting_departments_additions_opposite_account = self.ui.setting_departments_additions_opposite_account_combobox.currentData()
        setting_additions_opposite_account = self.ui.setting_additions_opposite_account_combobox.currentData()
        setting_salaries_opposite_account = self.ui.setting_salaries_opposite_account_combobox.currentData()
        setting_departments_additions_account = self.ui.setting_departments_additions_account_combobox.currentData()
        setting_salaries_account = self.ui.setting_salaries_account_combobox.currentData()
        setting_additions_account = self.ui.setting_additions_account_combobox.currentData()
        setting_discounts_opposite_account = self.ui.setting_discounts_opposite_account_combobox.currentData()
        setting_departments_default_opposite_account = self.ui.setting_departments_default_opposite_account_combobox.currentData()
        setting_departments_discounts_account = self.ui.setting_departments_discounts_account_combobox.currentData()
        setting_discounts_account = self.ui.setting_discounts_account_combobox.currentData()
        setting_additional_costs_opposite_account = self.ui.setting_additional_costs_opposite_account_combobox.currentData()
        setting_courses_costs_account = self.ui.setting_courses_costs_account_combobox.currentData()
        setting_courses_costs_opposite_account = self.ui.setting_courses_costs_opposite_account_combobox.currentData()
        setting_loans_account = self.ui.setting_loans_account_combobox.currentData()
        setting_departments_discounts_opposite_account = self.ui.setting_departments_discounts_opposite_account_combobox.currentData()
        setting_priority_additions_salary = self.ui.setting_priority_additions_salary_combobox.currentData()
        setting_priority_discount_salary = self.ui.setting_priority_discount_salary_combobox.currentData()
        setting_loans_opposite_account = self.ui.setting_loans_opposite_account_combobox.currentData()
        setting_insurance_account = self.ui.setting_insurance_account_combobox.currentData()
        setting_extra_account = self.ui.setting_extra_account_combobox.currentData()
        setting_extra_opposite_account = self.ui.setting_extra_opposite_account_combobox.currentData()
        setting_resource_recipients_account = self.ui.setting_resource_recipients_account_combobox.currentData()
        setting_month_duration = self.ui.setting_month_duration_input.text()
        setting_extra_normal = self.ui.setting_extra_normal_input.text()
        setting_extra_high = self.ui.setting_extra_high_input.text()

        if setting_work_day_sunday is None or str(setting_work_day_sunday).lower() == "none":
            setting_work_day_sunday = ''
        if setting_work_day_monday is None or str(setting_work_day_monday).lower() == "none":
            setting_work_day_monday = ''
        if setting_work_day_tuesday is None or str(setting_work_day_tuesday).lower() == "none":
            setting_work_day_tuesday = ''
        if setting_work_day_wednesday is None or str(setting_work_day_wednesday).lower() == "none":
            setting_work_day_wednesday = ''
        if setting_work_day_thursday is None or str(setting_work_day_thursday).lower() == "none":
            setting_work_day_thursday = ''
        if setting_work_day_friday is None or str(setting_work_day_friday).lower() == "none":
            setting_work_day_friday = ''
        if setting_work_day_saturday is None or str(setting_work_day_saturday).lower() == "none":
            setting_work_day_saturday = ''
        if setting_cycle_unused_leaves is None or str(setting_cycle_unused_leaves).lower() == "none":
            setting_cycle_unused_leaves = ''
        if setting_day_hours is None or str(setting_day_hours).lower() == "none":
            setting_day_hours = ''
        if setting_extra_normal is None or str(setting_extra_normal).lower() == "none":
            setting_extra_normal = ''
        if setting_extra_high is None or str(setting_extra_high).lower() == "none":
            setting_extra_high = ''

        if setting_week_start_day is None or str(setting_week_start_day).lower() == "none":
            setting_week_start_day = ''
        if setting_insurance_opposite_account is None or str(setting_insurance_opposite_account).lower() == "none":
            setting_insurance_opposite_account = ''
        if setting_departments_default_account is None or str(setting_departments_default_account).lower() == "none":
            setting_departments_default_account = ''
        if setting_additional_costs_account is None or str(setting_additional_costs_account).lower() == "none":
            setting_additional_costs_account = ''
        if setting_departments_additions_opposite_account is None or str(
                setting_departments_additions_opposite_account).lower() == "none":
            setting_departments_additions_opposite_account = ''
        if setting_additions_opposite_account is None or str(setting_additions_opposite_account).lower() == "none":
            setting_additions_opposite_account = ''
        if setting_salaries_opposite_account is None or str(setting_salaries_opposite_account).lower() == "none":
            setting_salaries_opposite_account = ''
        if setting_departments_additions_account is None or str(
                setting_departments_additions_account).lower() == "none":
            setting_departments_additions_account = ''
        if setting_salaries_account is None or str(setting_salaries_account).lower() == "none":
            setting_salaries_account = ''
        if setting_additions_account is None or str(setting_additions_account).lower() == "none":
            setting_additions_account = ''
        if setting_discounts_opposite_account is None or str(setting_discounts_opposite_account).lower() == "none":
            setting_discounts_opposite_account = ''
        if setting_departments_default_opposite_account is None or str(
                setting_departments_default_opposite_account).lower() == "none":
            setting_departments_default_opposite_account = ''
        if setting_departments_discounts_account is None or str(
                setting_departments_discounts_account).lower() == "none":
            setting_departments_discounts_account = ''
        if setting_discounts_account is None or str(setting_discounts_account).lower() == "none":
            setting_discounts_account = ''
        if setting_additional_costs_opposite_account is None or str(
                setting_additional_costs_opposite_account).lower() == "none":
            setting_additional_costs_opposite_account = ''
        if setting_courses_costs_account is None or str(setting_courses_costs_account).lower() == "none":
            setting_courses_costs_account = ''
        if setting_courses_costs_opposite_account is None or str(
                setting_courses_costs_opposite_account).lower() == "none":
            setting_courses_costs_opposite_account = ''
        if setting_loans_account is None or str(setting_loans_account).lower() == "none":
            setting_loans_account = ''
        if setting_departments_discounts_opposite_account is None or str(
                setting_departments_discounts_opposite_account).lower() == "none":
            setting_departments_discounts_opposite_account = ''
        if setting_loans_opposite_account is None or str(setting_loans_opposite_account).lower() == "none":
            setting_loans_opposite_account = ''
        if setting_insurance_account is None or str(setting_insurance_account).lower() == "none":
            setting_insurance_account = ''
        if setting_month_duration is None or str(setting_month_duration).lower() == "none":
            setting_month_duration = ''
        if setting_resource_recipients_account is None or str(setting_resource_recipients_account).lower() == "none":
            setting_resource_recipients_account = ''

        self.database_operations.saveHRSetting(
            setting_work_day_sunday,
            setting_work_day_monday,
            setting_work_day_tuesday,
            setting_work_day_wednesday,
            setting_work_day_thursday,
            setting_work_day_friday,
            setting_work_day_saturday,
            setting_cycle_unused_leaves,
            setting_day_hours,
            setting_insurance_opposite_account,
            setting_departments_default_account,
            setting_additional_costs_account,
            setting_departments_additions_opposite_account,
            setting_additions_opposite_account,
            setting_salaries_opposite_account,
            setting_departments_additions_account,
            setting_salaries_account,
            setting_additions_account,
            setting_discounts_opposite_account,
            setting_departments_default_opposite_account,
            setting_departments_discounts_account,
            setting_discounts_account,
            setting_additional_costs_opposite_account,
            setting_courses_costs_account,
            setting_courses_costs_opposite_account,
            setting_loans_account,
            setting_departments_discounts_opposite_account,
            setting_loans_opposite_account,
            setting_insurance_account,
            setting_extra_account,
            setting_extra_opposite_account,
            setting_week_start_day,
            setting_extra_normal,
            setting_extra_high,
            setting_month_duration,
            setting_resource_recipients_account,
            setting_priority_additions_salary,
            setting_priority_discount_salary
        )
        win32api.MessageBox(0, self.language_manager.translate('SETTINGS_SAVED'), self.language_manager.translate('ALERT'), MB_OK)

    def fetchSettings(self):
        settings = self.database_operations.fetchHRSettings()
        for setting in settings:
            name = setting[0]
            value = setting[1]
            for attr_name in dir(self.ui):
                if name in attr_name:
                    widget = getattr(self.ui, attr_name)
                    if isinstance(widget, QComboBox):
                        widget.setCurrentIndex(widget.findData(value))
                    elif isinstance(widget, QCheckBox):
                        if int(value) == 1:
                            print(str(attr_name))
                            widget.setChecked(True)
                        else:
                            widget.setChecked(False)
                    elif isinstance(widget, QLineEdit):
                        widget.setText(str(value))

    def setExtraCurrency(self):
        # get data from loans_combobox
        selected_employee_id = self.ui.extras_employees_tree.currentItem().text(4)
        if selected_employee_id:
            employee_data = self.database_operations.fetchEmployeeFinanceInfo(selected_employee_id)
            if employee_data:
                salary = employee_data['salary']
                salary_currency = employee_data['salary_currency']
                day_hours = employee_data['day_hours']

                settings_month_duration = self.database_operations.fetchHRSetting('setting_month_duration')
                float_point_value = self.database_operations.fetchFloatPointValue()
                hours_per_month = day_hours * int(settings_month_duration[0])

                salary_per_hour = float(salary / hours_per_month)
                salary_per_hour = round(salary_per_hour, int(float_point_value))

                for i in range(self.ui.extra_currency_combobox.count()):
                    currency_id = self.ui.extra_currency_combobox.itemData(i)
                    if int(currency_id) != int(salary_currency):
                        self.ui.extra_currency_combobox.model().item(i).setEnabled(False)
                    else:
                        self.ui.extra_currency_combobox.setCurrentIndex(i)
                self.ui.extra_value_input.setProperty('salary', salary_per_hour)  # to be used later in setExtraValue()

                self.ui.add_extra_btn.setEnabled(True)
            else:
                self.ui.add_extra_btn.setDisabled(True)
                win32api.MessageBox(0, self.language_manager.translate('NO_EMPLOYEE_FINANCE_DATA'), self.language_manager.translate('ALERT'), MB_OK)


    def setDepartmentExtraCurrency(self):
        # get data from loans_combobox
        selected_department_id = self.ui.departments_table.currentItem().text(0)
        if selected_department_id:
            department_data = self.database_operations.fetchDepartmentFinanceInfo(selected_department_id)
            if department_data:
                salary = department_data['salary']
                salary_currency = department_data['salary_currency']
                day_hours = department_data['day_hours']

                settings_month_duration = self.database_operations.fetchHRSetting('setting_month_duration')
                float_point_value = self.database_operations.fetchFloatPointValue()
                hours_per_month = day_hours * int(settings_month_duration[0])

                salary_per_hour = float(salary / hours_per_month)
                salary_per_hour = round(salary_per_hour, int(float_point_value))

                for i in range(self.ui.department_extra_currency_combobox.count()):
                    currency_id = self.ui.department_extra_currency_combobox.itemData(i)
                    if int(currency_id) != int(salary_currency):
                        self.ui.department_extra_currency_combobox.model().item(i).setEnabled(False)
                    else:
                        self.ui.department_extra_currency_combobox.setCurrentIndex(i)
                self.ui.department_extra_value_input.setProperty('salary', salary_per_hour)  # to be used later in setExtraValue()

                self.ui.department_add_extra_btn.setEnabled(True)
            else:
                self.ui.department_add_extra_btn.setDisabled(True)
                win32api.MessageBox(0, self.language_manager.translate('NO_DEPARTMENT_FINANCE_DATA'), self.language_manager.translate('ALERT'), MB_OK)


    def fetchExtras(self):
        self.ui.extras_table.setRowCount(0)
        selected_employee = self.ui.extras_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = self.ui.extras_employees_tree.currentItem().text(4)
            employee_extras = self.database_operations.fetchEmployeeExtra(selected_employee_id)
            if employee_extras:
                for employee_extra in employee_extras:
                    id = employee_extra['id']
                    employee_id = employee_extra['employee_id']
                    department_id = employee_extra['department_id']
                    date = employee_extra['start_date']
                    value = employee_extra['value_col']
                    duration_in_hours = employee_extra['duration_in_hours']
                    duration_in_days = employee_extra['duration_in_days']
                    currency_id = employee_extra['currency_id']
                    statement = employee_extra['statement_col']
                    account_id = employee_extra['account_id'] or ''
                    opposite_account_id = employee_extra['opposite_account_id'] or ''
                    state = employee_extra['state_col']
                    account_name = employee_extra['account_name'] or ''
                    opposite_account_name = employee_extra['opposite_account_name'] or ''
                    currency_name = employee_extra['currency_name']

                    # Write data into the table
                    extras_table = self.ui.extras_table
                    row_count = extras_table.rowCount()
                    extras_table.setRowCount(row_count + 1)

                    extras_table.setItem(row_count, 0, QTableWidgetItem(str(id)))
                    extras_table.setItem(row_count, 1, QTableWidgetItem(str(date)))
                    extras_table.setItem(row_count, 2, QTableWidgetItem(str(statement)))
                    extras_table.setItem(row_count, 3, QTableWidgetItem(str(value)))
                    extras_table.setItem(row_count, 4, QTableWidgetItem(str(currency_id)))
                    extras_table.setItem(row_count, 5, QTableWidgetItem(str(currency_name)))
                    extras_table.setItem(row_count, 6, QTableWidgetItem(str(duration_in_hours)))
                    extras_table.setItem(row_count, 7, QTableWidgetItem(str(duration_in_days)))
                    extras_table.setItem(row_count, 8, QTableWidgetItem(str(account_id)))
                    extras_table.setItem(row_count, 9, QTableWidgetItem(str(account_name)))
                    extras_table.setItem(row_count, 10, QTableWidgetItem(str(opposite_account_id)))
                    extras_table.setItem(row_count, 11, QTableWidgetItem(str(opposite_account_name)))
                    extras_table.setItem(row_count, 12, QTableWidgetItem(str(state)))

    def fetchDepartmentExtras(self):
        self.ui.department_extras_table.setRowCount(0)
        selected_department = self.ui.departments_table.currentItem()
        if selected_department:
            selected_department_id = self.ui.departments_table.item(selected_department.row(), 0).text()
            department_extras = self.database_operations.fetchEmployeeExtra(department_id=selected_department_id)
            if department_extras:
                for department_extra in department_extras:
                    id = department_extra['id']
                    employee_id = department_extra['employee_id']
                    department_id = department_extra['department_id']
                    date = department_extra['start_date']
                    value = department_extra['value_col']
                    duration_in_hours = department_extra['duration_in_hours']
                    duration_in_days = department_extra['duration_in_days']
                    currency_id = department_extra['currency_id']
                    statement = department_extra['statement_col']
                    account_id = department_extra['account_id']
                    opposite_account_id = department_extra['opposite_account_id']
                    state = department_extra['state_col']
                    account_name = department_extra['account_name']
                    opposite_account_name = department_extra['opposite_account_name']
                    currency_name = department_extra['currency_name']

                    # Write data into the table
                    extras_table = self.ui.department_extras_table
                    row_count = extras_table.rowCount()
                    extras_table.setRowCount(row_count + 1)

                    extras_table.setItem(row_count, 0, QTableWidgetItem(str(id)))
                    extras_table.setItem(row_count, 1, QTableWidgetItem(str(date)))
                    extras_table.setItem(row_count, 2, QTableWidgetItem(str(statement)))
                    extras_table.setItem(row_count, 3, QTableWidgetItem(str(value)))
                    extras_table.setItem(row_count, 4, QTableWidgetItem(str(currency_id)))
                    extras_table.setItem(row_count, 5, QTableWidgetItem(str(currency_name)))
                    extras_table.setItem(row_count, 6, QTableWidgetItem(str(duration_in_hours)))
                    extras_table.setItem(row_count, 7, QTableWidgetItem(str(duration_in_days)))
                    extras_table.setItem(row_count, 8, QTableWidgetItem(str(account_id)))
                    extras_table.setItem(row_count, 9, QTableWidgetItem(str(account_name)))
                    extras_table.setItem(row_count, 10, QTableWidgetItem(str(opposite_account_id)))
                    extras_table.setItem(row_count, 11, QTableWidgetItem(str(opposite_account_name)))
                    extras_table.setItem(row_count, 12, QTableWidgetItem(str(state)))


    def removeDepartmentExtra(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_extra = self.ui.department_extras_table.currentItem()
            if selected_extra is not None:
                selected_extra_id = self.ui.department_extras_table.item(selected_extra.row(), 0).text()
                self.database_operations.removeExtra(int(selected_extra_id))
                self.fetchDepartmentExtras()

    def openDepartmentReportWindow(self):
        department_id = self.ui.departments_table.currentItem()
        if department_id:
            department_id = self.ui.departments_table.item(department_id.row(), 0).text()
            Ui_Department_Report_Logic(self.sql_connector, department_id).showUi()

    def setExtraTypeValue(self):
        extra_type_data = self.ui.extra_type_combobox.currentData()
        if extra_type_data:
            value = str(extra_type_data)
            if value == 'custome':
                self.ui.extra_rate_input.clear()
                self.ui.extra_rate_input.setEnabled(True)
            else:
                self.ui.extra_rate_input.setDisabled(True)
                self.ui.extra_rate_input.setText(value)

    def setDepartmentExtraTypeValue(self):
        extra_type_data = self.ui.department_extra_type_combobox.currentData()
        if extra_type_data:
            value = str(extra_type_data)
            if value == 'custome':
                self.ui.department_extra_rate_input.clear()
                self.ui.department_extra_rate_input.setEnabled(True)
            else:
                self.ui.department_extra_rate_input.setDisabled(True)
                self.ui.department_extra_rate_input.setText(value)

    def fetchExtrasHighAndLow(self):
        # set extra types
        self.ui.extra_type_combobox.clear()
        high_setting = self.database_operations.fetchHRSetting('setting_extra_high')
        normal_setting = self.database_operations.fetchHRSetting('setting_extra_normal')
        if high_setting:
            self.ui.extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_HIGH'), high_setting[0])
        if normal_setting:
            self.ui.extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_NORMAL'), normal_setting[0])
        self.ui.extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_CUSTOME'), "custome")

    def fetchDepartmentExtrasHighAndLow(self):
        # set extra types
        self.ui.department_extra_type_combobox.clear()
        high_setting = self.database_operations.fetchHRSetting('setting_extra_high')
        normal_setting = self.database_operations.fetchHRSetting('setting_extra_normal')
        if high_setting:
            self.ui.department_extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_HIGH'), high_setting[0])
        if normal_setting:
            self.ui.department_extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_NORMAL'), normal_setting[0])
        self.ui.department_extra_type_combobox.addItem(self.language_manager.translate('HR_EXTRA_CUSTOME'), "custome")

    def setExtraValue(self):
        # fetch Employee Salary
        selected_employee = self.ui.extras_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = self.ui.extras_employees_tree.currentItem().text(4)
            if selected_employee_id:
                salary = self.ui.extra_value_input.property("salary")
                extra_rate = self.ui.extra_rate_input.text()
                if salary and extra_rate:
                    value = float(salary) * float(extra_rate)
                    self.ui.extra_value_input.setText(str(value))

    def setExtraDepartmentValue(self):
        selected_department = self.ui.departments_table.currentItem()
        if selected_department:
            selected_department_id = selected_department.text()
            if selected_department_id:
                salary = self.ui.department_extra_value_input.property("salary")
                extra_rate = self.ui.department_extra_rate_input.text()
                if salary and extra_rate:
                    value = float(salary) * float(extra_rate)
                    self.ui.department_extra_value_input.setText(str(value))


    def addExtras(self):
        self.ui.extras_table.setRowCount(0)
        selected_item = self.ui.extras_employees_tree.currentItem()
        if selected_item:
            selected_employee_id = selected_item.text(4)
            # get department id
            parent_item = selected_item
            while parent_item.parent() is not None:
                parent_item = parent_item.parent()
            # Get the root element's text
            selected_department_id = parent_item.text(0)

        extra_date = self.ui.extra_date_input.dateTime().toString(Qt.ISODate)
        extra_duration_hours = self.ui.extra_duration_hours_input.text()
        extra_duration_days = self.ui.extra_duration_days_input.text()
        extra_value = self.ui.extra_value_input.text()
        extra_currency = self.ui.extra_currency_combobox.currentData()
        extra_account = self.ui.extra_account_combobox.currentData() or ''
        extra_opposite_account = self.ui.extra_opposite_account_combobox.currentData() or ''
        extra_statement_input = self.ui.extra_statement_input.text()

        if str(extra_duration_days).strip() and str(extra_duration_hours).strip() and str(extra_value).strip():
            self.database_operations.addExtras(selected_employee_id, selected_department_id, extra_date, extra_duration_hours,extra_duration_days, extra_value, extra_currency, extra_account, extra_opposite_account, extra_statement_input)

            if not self.independent:
                entry_id = self.database_operations.addJournalEntry(entry_date=extra_date, currency=extra_currency, origin_type='extra_work', origin_id=selected_employee_id)

                if entry_id:
                    self.database_operations.addJournalEntryItem(journal_entry_id=entry_id,currency=extra_currency,type_col='creditor',account=extra_account,opposite_account= extra_opposite_account,statement= extra_statement_input,value=extra_value)


    def addDepartmentExtra(self):
        self.ui.extras_table.setRowCount(0)
        selected_item = self.ui.departments_table.currentItem()
        if not selected_item:
            win32api.MessageBox(0, self.language_manager.translate('HR_ALERT_SELECT_DEPARTMENT'), self.language_manager.translate('ALERT'), MB_OK)
            return

        selected_row = selected_item.row()
        selected_department_id = self.ui.departments_table.item(selected_row, 0).text()
        department_extra_date = self.ui.department_extra_date_input.dateTime().toString(Qt.ISODate)
        department_extra_duration_hours = self.ui.department_extra_duration_hours_input.text()
        department_extra_duration_days = self.ui.department_extra_duration_days_input.text()
        department_extra_currency = self.ui.department_extra_currency_combobox.currentData()
        department_extra_account = self.ui.department_extra_account_combobox.currentData()
        department_extra_opposite_account = self.ui.department_extra_opposite_account_combobox.currentData()
        department_extra_statement_input = self.ui.department_extra_statement_input.text()
        department_extra_rate_input = self.ui.department_extra_rate_input.text()

        department_data = self.database_operations.fetchDepartment(selected_department_id)
        if department_data:
            day_hours = department_data['day_hours']
        else:
            message_result = win32api.MessageBox(0, self.language_manager.translate('HR_ALERT_SELECT_DEPARTMENT'), self.language_manager.translate('ALERT'), MB_OKCANCEL)
            if message_result == IDCANCEL:
                day_hours = 8
            else:
                return

        if str(department_extra_duration_days).strip() and str(department_extra_duration_hours).strip():
            employees = self.database_operations.fetchEmployees(department_id=selected_department_id , state='current')
            for employee in employees:
                employee_id = employee['id']
                employee_finance_data = self.database_operations.fetchEmployeeFinanceInfo(employee_id)
                if employee_finance_data:
                    employee_salary_currency = employee_finance_data['salary_currency']
                    employee_salary = employee_finance_data['salary']

                    month_duration = self.database_operations.fetchHRSetting('setting_month_duration')
                    if month_duration:
                        month_duration = month_duration['value_col']
                    else:
                        month_duration = 30
                    hourly_salary = (employee_salary / int(month_duration)) / day_hours
                    value = hourly_salary * float(department_extra_rate_input)
                    if employee_salary_currency == department_extra_currency:
                        pass
                    else:
                        exchange_rate = self.database_operations.fetchExchangeValue(employee_salary_currency, department_extra_currency,department_extra_date)
                        if exchange_rate:
                            value = float(exchange_rate[0][1]) * float(value)
                        else:
                            msg = "لا يوجد سعر صرف بين " + str(department_extra_currency) + " وعملة راتب الموظف في التاريخ المحدد"
                            win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                            return

                value = round(value, 3)
                department_extra_id = self.database_operations.addExtras(employee_id, selected_department_id, department_extra_date, department_extra_duration_hours,department_extra_duration_days, value, department_extra_currency, department_extra_account, department_extra_opposite_account, department_extra_statement_input)

                if not self.independent:
                    entry_id = self.database_operations.addJournalEntry(entry_date=department_extra_date, currency=department_extra_currency, origin_type='department_extra_work', origin_id=department_extra_id)

                    if entry_id:
                        self.database_operations.addJournalEntryItem(journal_entry_id=entry_id,currency=department_extra_currency,type_col='creditor',account=department_extra_account,opposite_account= department_extra_opposite_account,statement= department_extra_statement_input,value=value)

                self.fetchDepartmentExtras()


    def removeSelectedExtra(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate( 'DELETE_CONFIRM'), self.language_manager.translate( 'ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_extra = self.ui.extras_table.currentItem()
            if selected_extra is not None:
                selected_extra_id = self.ui.extras_table.item(selected_extra.row(), 0).text()
                self.database_operations.removeExtra(int(selected_extra_id))
                self.fetchExtras()

    def setSalaryAdditionsDiscountsTypes(self):
        types = [{"text": "HR_PERMANENT_ADDITION", "value": "permenant addition"},
                 {"text": "HR_TEMPORARY_ADDITION", "value": "temporary addition"},
                 {"text": "HR_PERMANENT_DISCOUNT", "value": "permenant discount"},
                 {"text": "HR_TEMPORARY_DISCOUNT", "value": "temporary discount"}]
        for type in types:
            self.ui.salaries_discount_addition_type_combobox.addItem(self.language_manager.translate(type["text"]), type["value"])

    def openSelectSalariesDiscountAdditionAccountWindow(self):
        # Update accounts combobox
        self.fetchAccounts()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.salaries_discount_addition_account_combobox.count()):
                if self.ui.salaries_discount_addition_account_combobox.itemData(i) == result[0]:
                    self.ui.salaries_discount_addition_account_combobox.setCurrentIndex(i)
                    break


    def openSelectSalariesDiscountAdditionEmployeeAccountWindow(self):
        # Update accounts combobox
        self.fetchAccounts()
        selected_employee = self.ui.salaries_employees_tree.currentItem()
        if selected_employee is not None:
            employee_id = selected_employee.text(4)
            employee_finance = self.database_operations.fetchEmployeeFinanceInfo(employee_id)
            account_id = employee_finance['salary_account_id']
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', default_id=account_id)
            result = data_picker.showUi()
            if result is not None:
                for i in range(self.ui.salaries_discount_addition_opposite_account_combobox.count()):
                    if self.ui.salaries_discount_addition_opposite_account_combobox.itemData(i) == result[0]:
                        self.ui.salaries_discount_addition_opposite_account_combobox.setCurrentIndex(i)
                        break


    def setSalaryAdditionsDiscountsCurrency(self):
        selected_employee = self.ui.salaries_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = self.ui.salaries_employees_tree.currentItem().text(4)
            if selected_employee_id:
                employee_data = self.database_operations.fetchEmployeeFinanceInfo(selected_employee_id)
                if employee_data:
                    # bank = employee_data[0]
                    # bank_account_number = employee_data[1]
                    # bank_notes = employee_data[2]
                    # salary = employee_data[3]
                    # salary_cycle = employee_data[4]
                    salary_currency = employee_data[5]
                    # insurance = employee_data[6]
                    # salary_account_id = employee_data[7]
                    # salary_opposite_account_id = employee_data[8]
                    # insurance_account_id = employee_data[9]
                    # insurance_opposite_account_id = employee_data[10]
                    # insurance_currency = employee_data[11]
                    # insurance_cycle = employee_data[12]

                    for i in range(self.ui.salaries_discount_addition_currency_combobox.count()):
                        item_data = self.ui.salaries_discount_addition_currency_combobox.itemData(i)
                        if str(salary_currency) not in [str(item_data), '%']:
                            self.ui.salaries_discount_addition_currency_combobox.model().item(i).setEnabled(False)
                        else:
                            self.ui.salaries_discount_addition_currency_combobox.model().item(i).setEnabled(True)
                            self.ui.salaries_discount_addition_currency_combobox.setCurrentIndex(i)

    def addSalaryAdditionAndDiscount(self):
        selected_employee = self.ui.salaries_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = selected_employee.text(4)
            if selected_employee_id:
                type = self.ui.salaries_discount_addition_type_combobox.currentData()
                start_date = self.ui.salaries_discount_addition_start_date_input.date().toString(Qt.ISODate)
                repeatition = self.ui.salaries_discount_addition_repeatition_input.text()
                value = self.ui.salaries_discount_addition_value_input.text()
                account = self.ui.salaries_discount_addition_account_combobox.currentData()
                opposite_account = self.ui.salaries_discount_addition_opposite_account_combobox.currentData()
                statement = self.ui.salaries_discount_addition_statement.text()
                currency = self.ui.salaries_discount_addition_currency_combobox.currentData()

                if str(value).strip():
                    self.database_operations.addSalaryAdditionAndDiscount(selected_employee_id, type, start_date,repeatition,value, account, opposite_account,statement, currency)



    def disableRepeatition(self):
        data = self.ui.salaries_discount_addition_type_combobox.currentData()
        if data == 'permenant addition' or data == 'permenant discount':
            self.ui.salaries_discount_addition_repeatition_input.setDisabled(True)
        else:
            self.ui.salaries_discount_addition_repeatition_input.setDisabled(False)


    def removeSelectedSalaryAdditionAndDiscount(self):
        selected_salary_addition_and_discount = self.ui.salaries_discounts_additions_table.currentItem()
        if selected_salary_addition_and_discount is not None:
            message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), MB_YESNO)
            if message_result == IDYES:
                selected_salary_addition_and_discount_id = self.ui.salaries_discounts_additions_table.item(selected_salary_addition_and_discount.row(), 0).text()
                payments = self.database_operations.fetchSalaryAdditionsAndDiscountPayments(selected_salary_addition_and_discount_id)
                if not payments:
                    self.database_operations.removeSalaryAdditionAndDiscount(selected_salary_addition_and_discount_id)
                    self.fetchSalaryAdditionsAndDiscounts()
                else:
                    win32api.MessageBox(0, self.language_manager.translate('THAT_SALARY_ADDITION_AND_DISCOUNT_HAS_PAYMENTS'), self.language_manager.translate('ALERT'), MB_OK)


    def fetchSalaryAdditionsAndDiscounts(self):
        self.ui.salaries_discounts_additions_table.setRowCount(0)
        selected_employee = self.ui.salaries_employees_tree.currentItem()
        if selected_employee:
            selected_employee_id = self.ui.salaries_employees_tree.currentItem().text(4)
            if selected_employee_id:
                rows = self.database_operations.fetchSalaryAdditionsAndDiscounts(selected_employee_id)
                # Loop over rows and add them to the table
                for row in rows:
                    id = row['id']
                    employee_id = row['employee_id']
                    type = row['type_col']
                    start_date = row['start_date']
                    repeatition = row['repeatition']
                    value = row['value_col']
                    account_id = row['account_id']
                    opposite_account_id = row['opposite_account_id']
                    statement = row['statement_col']
                    currency_id = row['currency_id']
                    state = row['state_col']
                    currency_name = row['currency_name']
                    account_name = row['account_name']
                    opposite_account_name = row['opposite_account_name']
                    num_payments = row['num_payments']

                    # Add a new row to the table
                    row_num = self.ui.salaries_discounts_additions_table.rowCount()
                    self.ui.salaries_discounts_additions_table.insertRow(row_num)

                    # Set the values for the columns in the new row
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 0, QTableWidgetItem(str(id)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 1, QTableWidgetItem(str(type)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 2, QTableWidgetItem(str(value)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 3,QTableWidgetItem(str(currency_id)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 4, QTableWidgetItem(str(currency_name)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 5, QTableWidgetItem(str(start_date)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 6, QTableWidgetItem(str(repeatition)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 7,QTableWidgetItem(str(account_id)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 8, QTableWidgetItem(str(account_name)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 9, QTableWidgetItem(str(opposite_account_id)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 10,QTableWidgetItem(str(opposite_account_name)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 11, QTableWidgetItem(str(statement)))
                    self.ui.salaries_discounts_additions_table.setItem(row_num, 12, QTableWidgetItem(str(state)))

    def addLeaveType(self):
        name = self.ui.leave_type_name_input.text()
        days = self.ui.leave_type_days_input.text()
        period = self.ui.leave_type_period_combobox.currentData()
        paid = int(self.ui.leave_type_paid_checkbox.isChecked())

        if name and name.strip() != '' and days and period:
            self.database_operations.addLeaveType(name, days, period, paid)
            self.fetchLeaveTypes()
        else:
            win32api.MessageBox(0, self.language_manager.translate('INVALID_DATA'), self.language_manager.translate( 'ERROR'))

    def removeSelectedLeaveType(self):
        message_result = win32api.MessageBox(0, self.language_manager.translate('DELETE_CONFIRM'), self.language_manager.translate('ALERT'), MB_YESNO)
        if message_result == IDYES:
            selected_leave_type = self.ui.leave_types_table.currentItem()
            if selected_leave_type is not None:
                selected_leave_type_id = self.ui.leave_types_table.item(selected_leave_type.row(), 0).text()
                try:
                    self.database_operations.removeLeaveType(int(selected_leave_type_id))
                    self.fetchLeaveTypes()
                except Exception as e:
                    win32api.MessageBox(0, self.language_manager.translate('ALERT_DELETE_RESTRICTED'), self.language_manager.translate('ERROR'))

    def fetchLeaveTypes(self):
        # clear the table
        self.ui.leave_types_table.setRowCount(0)

        # clear the combobox
        self.ui.leave_type_combobox.clear()

        # get leave types from database
        leave_types = self.database_operations.fetchLeaveTypes()

        for leave_type in leave_types:
            id = leave_type['id']
            name = leave_type['name']
            days = leave_type['days']
            period = leave_type['period']
            date = leave_type['date_added']
            paid = leave_type['paid']

            numRows = self.ui.leave_types_table.rowCount()
            self.ui.leave_types_table.insertRow(numRows)

            self.ui.leave_types_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.leave_types_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
            self.ui.leave_types_table.setItem(numRows, 2, QTableWidgetItem(str(days)))
            self.ui.leave_types_table.setItem(numRows, 3, QTableWidgetItem(str(period)))
            self.ui.leave_types_table.setItem(numRows, 4, QTableWidgetItem("✅" if paid else "❌"))
            self.ui.leave_types_table.setItem(numRows, 5, QTableWidgetItem(str(date)))

            self.ui.leave_type_combobox.addItem(name, [id, days, period, paid])

    def setLeaveDays(self):
        print("SET")
        leave_start_date = self.ui.leave_start_input.dateTime()
        leave_duration_days = self.ui.leave_duration_days_input.text()
        if leave_start_date and leave_duration_days:
            leave_start_date_year = leave_start_date.date().year()
            last_day_of_year = QDateTime(QDate(leave_start_date_year, 12, 31), QTime(23, 59, 59))
            days_remaining_in_year = leave_start_date.daysTo(last_day_of_year)
            days_remaining_in_year += 1  # because leave_start_date day is counted
            if float(days_remaining_in_year) < float(leave_duration_days):
                leave_duration_days = days_remaining_in_year

            leave_duration_days_int = round(float(leave_duration_days), 2)
            leave_end_date = QDateTime.toPyDateTime(leave_start_date) + timedelta(days=leave_duration_days_int)

            # fetch department off days, and subtract them from leave_days_duration
            off_days = []
            selected_item = self.ui.leaves_employees_tree.currentItem()
            # Traverse the tree upwards to get the root element
            if selected_item:
                parent_item = selected_item
                while parent_item.parent() is not None:
                    parent_item = parent_item.parent()
                # Get the root element's text
                selected_department_id = parent_item.text(0)
                if selected_department_id:
                    department = self.database_operations.fetchDepartment(selected_department_id)
                    day_hours = department['day_hours']
                    work_day_saturday = department['work_day_saturday']
                    if not work_day_saturday:
                        off_days.append("saturday")
                    work_day_sunday = department['work_day_sunday']
                    if not work_day_sunday:
                        off_days.append("sunday")
                    work_day_monday = department['work_day_monday']
                    if not work_day_monday:
                        off_days.append("monday")
                    work_day_tuesday = department['work_day_tuesday']
                    if not work_day_tuesday:
                        off_days.append("tuesday")
                    work_day_wednesday = department['work_day_wednesday']
                    if not work_day_wednesday:
                        off_days.append("wednesdy")
                    work_day_thursday = department['work_day_thursday']
                    if not work_day_thursday:
                        off_days.append("thursday")
                    work_day_friday = department['work_day_friday']
                    if not work_day_friday:
                        off_days.append("friday")

                    off_days_count = 0
                    curr_date = leave_start_date.date()

                    while curr_date < leave_end_date.date():
                        curr_datetime = QDateTime(curr_date, QTime(0, 0, 0))
                        print(curr_datetime)
                        if curr_datetime.toString("dddd").lower() in off_days:
                            off_days_count += 1
                            print("OK=" + str(off_days_count))
                        curr_date = curr_date.addDays(1)

                    leave_duration_days = float(leave_duration_days) - float(off_days_count)
                if int(leave_duration_days) < 0:
                    leave_duration_days = 0
                leave_duration_hours = leave_duration_days * float(day_hours)
                self.ui.actual_leave_duration_days_input.setText(str(leave_duration_days))
                self.ui.actual_leave_duration_hours_input.setText(str(leave_duration_hours))

    def calculateSalaries(self):
        self.ui.salaries_result_tree.clear()
        salaries_from_date = self.ui.salaries_from_date_input.date()
        salaries_to_date = self.ui.salaries_to_date_input.date()
        exchange_price_date = self.ui.salaries_exchange_price_date_input.date().toString(Qt.ISODate)
        employees_finance_info = self.database_operations.fetchEmployeesFinanceInfo(from_date=salaries_from_date.toString(Qt.ISODate), to_date=salaries_to_date.toString(Qt.ISODate))

        default_day_hours_setting = self.database_operations.fetchHRSetting('setting_day_hours')
        default_day_hours = default_day_hours_setting[0] if default_day_hours_setting else 8

        result = [[]]

        # calculate salary duration
        salary_delta = (salaries_from_date.daysTo(salaries_to_date)) + 1
        month_duration_setting = self.database_operations.fetchHRSetting('setting_month_duration')
        if not month_duration_setting:
            win32api.MessageBox(0, "لم يتم تحديد عدد ايام شهر العمل", self.language_manager.translate("ALERT"))
            return
        month_duration = month_duration_setting[0]
        salary_duration_days = salary_delta
        salary_duration_month = float(salary_duration_days) / float(month_duration)

        for data in employees_finance_info:
            base_salary = 0
            depratment_additions = 0
            department_discounts = 0
            position_additions = 0
            position_discounts = 0
            leaves_discounts = 0
            extras_additions = 0
            loans_subtraction = 0
            salary_discounts = 0
            salary_additions = 0
            cycles = []

            employee_id = data['employee_id']
            employee_name = data['name']
            position_id = data['position_id']
            position_name = data['position_name']
            department_id = data['department_id']
            department_name = data['department_name']
            name = data['name']
            bank = data['bank']
            bank_account_number = data['bank_account_number']
            bank_notes = data['bank_notes']
            salary = data['salary']
            salary_cycle = data['salary_cycle']
            salary_currency = data['salary_currency']
            insurance = data['insurance']
            salary_account_id = data['salary_account_id']
            salary_account_name = data['salary_account_name']
            salary_opposite_account_id = data['salary_opposite_account_id']
            salary_opposite_account_name = data['salary_opposite_account_name']
            insurance_account_id = data['insurance_account_id']
            insurance_opposite_account_id = data['insurance_opposite_account_id']
            insurance_currency = data['insurance_currency']
            insurance_cycle = data['insurance_cycle']
            salary_currency_name = data['salary_currency_name']
            insurance_currency_name = data['insurance_currency_name']

            employee_dict = {}  # a tree to hold employee date, and will be later added to result



            print("************** Emp=" + str(employee_id) + "**************")
            # 0-Calculate base salary

            if not salary_account_id or not salary_opposite_account_id and not self.independent:
                msg = self.language_manager.translate("HR_SALARY_ACCOUNT_NOT_SET") + str(employee_id)
                win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                return

            if not salary:
                msg = "لم يتم تحديد راتب الموظف  " + str(employee_id) +  " سيتم استخدام الراتب الافتراضي للمنصب الوظيفي الخاص به"
                message_result = win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"), MB_YESNO)
                if message_result == IDNO:
                    return
                else:
                    position = self.database_operations.fetchPosition(position_id)
                    salary = position['salary']

            if salary_cycle == 'day':
                if self.ui.deparetment_days_checkbox.isChecked():
                    department = self.database_operations.fetchDepartment(department_id)
                    if department:
                        department_work_day_saturday = department['work_day_saturday']
                        department_work_day_sunday = department['work_day_sunday']
                        department_work_day_monday = department['work_day_monday']
                        department_work_day_tuesday = department['work_day_tuesday']
                        department_work_day_wednesday = department['work_day_wednesday']
                        department_work_day_thursday = department['work_day_thursday']
                        department_work_day_friday = department['work_day_friday']

                        # Get work day settings from system settings
                        work_day_saturday = self.database_operations.fetchHRSetting('setting_work_day_saturday')[0]
                        work_day_sunday = self.database_operations.fetchHRSetting('setting_work_day_sunday')[0]
                        work_day_monday = self.database_operations.fetchHRSetting('setting_work_day_monday')[0]
                        work_day_tuesday = self.database_operations.fetchHRSetting('setting_work_day_tuesday')[0]
                        work_day_wednesday = self.database_operations.fetchHRSetting('setting_work_day_wednesday')[0]
                        work_day_thursday = self.database_operations.fetchHRSetting('setting_work_day_thursday')[0]
                        work_day_friday = self.database_operations.fetchHRSetting('setting_work_day_friday')[0]

                        # Map Python's weekday to our system's work day settings
                        # Python weekday: Monday=0, Tuesday=1, ..., Sunday=6
                        work_days_map = {
                            0: department_work_day_monday and work_day_monday,       # Monday
                            1: department_work_day_tuesday and work_day_tuesday,     # Tuesday
                            2: department_work_day_wednesday and work_day_wednesday, # Wednesday
                            3: department_work_day_thursday and work_day_thursday,   # Thursday
                            4: department_work_day_friday and work_day_friday,       # Friday
                            5: department_work_day_saturday and work_day_saturday,   # Saturday
                            6: department_work_day_sunday and work_day_sunday        # Sunday
                        }

                        # Count actual working days in the period
                        working_days = 0
                        current_date = salaries_from_date.toPyDate()
                        end_date = salaries_to_date.toPyDate()

                        while current_date <= end_date:
                            weekday = current_date.weekday()  # Get Python's weekday (0-6)
                            if work_days_map[weekday]:
                                working_days += 1
                            current_date += timedelta(days=1)

                        cycles_count = working_days
                        # Add full day cycles
                        for i in range(working_days):
                            cycles.append(salary)

                        if working_days == 0:
                            msg = self.language_manager.translate("HR_NO_WORKING_DAYS_IN_PERIOD") + str(employee_id)
                            win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                            return
                else:
                    cycles_count = salary_duration_days
                    for i in range(1, salary_duration_days + 1):
                        cycles.append(salary)
                    salary_duration_days_decimals = salary_duration_days % 1
                    if salary_duration_days_decimals:
                        partial_salary = salary_duration_days_decimals * salary
                        cycles.append(partial_salary)

            if salary_cycle == 'month':
                month_days_count_setting = self.database_operations.fetchHRSetting('setting_month_duration')
                if month_days_count_setting:
                    month_days_count = month_days_count_setting[0]
                    salary_duration_month = float(salary_duration_days) / float(month_days_count)
                    cycles_count = salary_duration_month
                    x = int(salary_duration_month)
                    print(x)
                    for i in range(1, (int(salary_duration_month) + 1)):
                        cycles.append(salary)
                    salary_duration_month_decimals = salary_duration_month % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                    if salary_duration_month_decimals:
                        partial_salary = salary_duration_month_decimals * salary
                        cycles.append(partial_salary)
                else:
                    win32api.MessageBox(0, self.language_manager.translate('INSURANCE_ALERT_NO_WORK_DAYS_MONTH'), self.language_manager.translate('ALERT'))
                    return

            if salary_cycle == 'week':
                department = self.database_operations.fetchDepartment(department_id)
                if department:
                    department_id = department['id']
                    department_name = department['name']
                    department_day_hours = department['day_hours']
                    department_account_id = department['account_id']
                    department_opposite_account_id = department['opposite_account_id']
                    department_notes = department['notes']
                    department_work_day_saturday = department['work_day_saturday']
                    department_work_day_sunday = department['work_day_sunday']
                    department_work_day_monday = department['work_day_monday']
                    department_work_day_tuesday = department['work_day_tuesday']
                    department_work_day_wednesday = department['work_day_wednesday']
                    department_work_day_thursday = department['work_day_thursday']
                    department_work_day_friday = department['work_day_friday']
                    week_days_count = 0

                    for d in [department_work_day_saturday,department_work_day_sunday,department_work_day_monday,department_work_day_tuesday,department_work_day_wednesday,department_work_day_thursday,department_work_day_friday]:
                        if d:
                            week_days_count += 1

                    if week_days_count:
                        salary_duration_week = salary_duration_days / week_days_count
                        cycles_count = salary_duration_week
                        for i in range(1, (int(salary_duration_week) + 1)):
                            cycles.append(salary)
                        salary_duration_week_decimals = salary_duration_week % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                        if salary_duration_week_decimals:
                            partial_salary = salary_duration_week_decimals * salary
                            cycles.append(partial_salary)
                    else:
                        msg = self.language_manager.translate("HR_NO_WORK_DAYS_WEEK") + str(employee_id)
                        win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                        return

            if salary_cycle == 'hour':
                department = self.database_operations.fetchDepartment(department_id)
                if department:
                    department_id = department['id']
                    department_name = department['name']
                    department_day_hours = department['day_hours']
                    department_account_id = department['account_id']
                    department_opposite_account_id = department['opposite_account_id']
                    department_notes = department['notes']
                    department_work_day_saturday = department['work_day_saturday']
                    department_work_day_sunday = department['work_day_sunday']
                    department_work_day_monday = department['work_day_monday']
                    department_work_day_tuesday = department['work_day_tuesday']
                    department_work_day_wednesday = department['work_day_wednesday']
                    department_work_day_thursday = department['work_day_thursday']
                    department_work_day_friday = department['work_day_friday']

                if department_day_hours:
                    salary_duration_hours = salary_duration_days * department_day_hours
                    cycles_count = salary_duration_hours
                    for i in range(1, (int(salary_duration_hours) + 1)):
                        cycles.append(salary)
                    salary_duration_hours_decimals = salary_duration_hours % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                    if salary_duration_hours_decimals:
                        partial_salary = salary_duration_hours_decimals * salary
                        cycles.append(partial_salary)
                else:
                    msg = self.language_manager.translate("HR_NO_WORK_DAYS_HOURS") + str(department_name)
                    win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                    return



            if len(cycles) > 0:
                base_salary = sum(cycles)

            # 1-Departments additions and discounts:
            if self.ui.salaries_include_departments_additions_discounts.isChecked():
                department_additions_and_discounts_data = self.database_operations.fetchDepartmentDiscountsAdditions(
                    department_id, salaries_from_date.toString(Qt.ISODate), salaries_to_date.toString(Qt.ISODate))
                for data in department_additions_and_discounts_data:
                    id = data['id']
                    department_id = data['department_id']
                    statement = data['statement_col']
                    type = data['type_col']
                    value = data['value_col']
                    currency_id = data['currency_id']
                    start_date = data['start_date']
                    end_date = data['end_date']
                    account_id = data['account_id']
                    opposite_account_id = data['opposite_account_id']
                    date = data['date_col']
                    currency_name = data['currency_name']
                    account = data['account']
                    opposite_account = data['opposite_account']

                    start_date = QDate(start_date.year, start_date.month, start_date.day)
                    end_date = QDate(end_date.year, end_date.month, end_date.day)
                    if start_date < salaries_from_date:
                        start_date = salaries_from_date
                    if end_date > salaries_to_date:
                        end_date = salaries_to_date

                    department_additions_and_discounts_delta = (start_date.daysTo(end_date)) + 1
                    department_additions_and_discounts_cycles = float(cycles_count) * float(
                        department_additions_and_discounts_delta) / float(salary_duration_days)
                    value = float(value) * department_additions_and_discounts_cycles
                    if currency_id == salary_currency:
                        pass
                    else:
                        exchange_rate = self.database_operations.fetchExchangeValue(currency_id, salary_currency,exchange_price_date)
                        if exchange_rate:
                            value = float(exchange_rate[0][1]) * float(value)
                        else:
                            msg = "لا يوجد سعر صرف بين " + currency_name + " وعملة راتب الموظف في التاريخ المحدد"
                            win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                            return

                    if type == 'addition':
                        depratment_additions += value
                        total_cycles = float(cycles_count)
                        complete_cycles = math.floor(total_cycles)
                        incomplete_cycle = total_cycles - complete_cycles
                        for i in range(complete_cycles):
                            if incomplete_cycle > 0:
                                value_per_cycle = value / incomplete_cycle
                            else:
                                value_per_cycle = value / complete_cycles
                            self.department_addition_discount_map[f"{id}_{i}"] = {
                                'id': id,
                                'employee_id': employee_id,
                                'currency_id': currency_id,
                                'statement_col': "department_addition_payroll",
                                'type_col': type,
                                'action_type': 'addition',
                                'value_col': value_per_cycle,
                                'account_id': account_id,
                                'opposite_account_id': opposite_account_id,
                                'date_col': salaries_from_date.toString(Qt.ISODate),
                            }

                    elif type == 'discount':
                        department_discounts += value
                        total_cycles = float(cycles_count)
                        complete_cycles = math.floor(total_cycles)
                        incomplete_cycle = total_cycles - complete_cycles
                        for i in range(complete_cycles):
                            if incomplete_cycle > 0:
                                value_per_cycle = value / incomplete_cycle
                            else:
                                value_per_cycle = value / complete_cycles
                            self.department_addition_discount_map[f"{id}_{i}"] = {
                                'id': id,
                                'employee_id': employee_id,
                                'currency_id': currency_id,
                                'statement_col': "department_discount_payroll",
                                'type_col': type,
                                'action_type': 'discount',
                                'value_col': value_per_cycle,
                                'account_id': account_id,
                                'opposite_account_id': opposite_account_id,
                                'date_col': salaries_from_date.toString(Qt.ISODate),
                            }

                    # print("**********CYC*********"+str(department_additions_and_discounts_cycles))
                    # print("**********ADD*********" + str(depratment_additions))
                    # print("**********DIS*********" + str(department_discounts))


            # # 2-positions additions and discounts
            if self.ui.salaries_include_positions_additions_discounts.isChecked():
                position_additions_and_discounts_data = self.database_operations.fetchPositionDiscountsAdditions(
                    position_id, salaries_from_date.toString(Qt.ISODate), salaries_to_date.toString(Qt.ISODate))
                for data in position_additions_and_discounts_data:
                    id = data['id']
                    position_id = data['position_id']
                    statement = data['statement_col']
                    type = data['type_col']
                    value = data['value_col']
                    currency_id = data['currency_id']
                    start_date = data['start_date']
                    end_date = data['end_date']
                    account_id = data['account_id']
                    opposite_account_id = data['opposite_account_id']
                    date = data['date_col']
                    currency_name = data['currency_name']
                    account = data['account']
                    opposite_account = data['opposite_account']

                    start_date = QDate(start_date.year, start_date.month, start_date.day)
                    end_date = QDate(end_date.year, end_date.month, end_date.day)
                    if start_date < salaries_from_date:
                        start_date = salaries_from_date
                    if end_date > salaries_to_date:
                        end_date = salaries_to_date

                    position_additions_and_discounts_delta = (start_date.daysTo(end_date)) + 1
                    position_additions_and_discounts_cycles = float(cycles_count) * float(
                        position_additions_and_discounts_delta) / float(salary_duration_days)
                    total_value = float(value) * position_additions_and_discounts_cycles

                    if currency_id == salary_currency:
                        pass
                    else:
                        exchange_rate = self.database_operations.fetchExchangeValue(currency_id, salary_currency, exchange_price_date)
                        if exchange_rate:
                            total_value = float(exchange_rate[0][1]) * float(total_value)
                        else:
                            msg = "لا يوجد سعر صرف بين " + currency_name + " وعملة راتب الموظف في التاريخ المحدد"
                            win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                            break

                    if type == 'addition':
                        position_additions += float(total_value)
                        total_cycles = float(cycles_count)
                        complete_cycles = math.floor(total_cycles)
                        incomplete_cycle = total_cycles - complete_cycles
                        for i in range(complete_cycles):
                            if incomplete_cycle > 0:
                                value_per_cycle = value
                            else:
                                value_per_cycle = value
                            self.position_addition_discount_map[f"{id}_{i}"] = {
                                'id': id,
                                'employee_id': employee_id,
                                'currency_id': currency_id,
                                'statement_col': "position_addition_payroll",
                                'type_col': type,
                                'action_type': 'addition',
                                'value_col': value_per_cycle,
                                'account_id': account_id,
                                'opposite_account_id': opposite_account_id,
                                'date_col': salaries_from_date.toString(Qt.ISODate),
                            }

                    elif type == 'discount':
                        position_discounts += float(total_value)
                        total_cycles = float(cycles_count)
                        complete_cycles = math.floor(total_cycles)
                        incomplete_cycle = total_cycles - complete_cycles
                        for i in range(complete_cycles):
                            if incomplete_cycle > 0:
                                value_per_cycle = value / incomplete_cycle
                            else:
                                value_per_cycle = value
                            self.position_addition_discount_map[f"{id}_{i}"] = {
                                'id': id,
                                'employee_id': employee_id,
                                'currency_id': currency_id,
                                'statement_col': "position_discount_payroll",
                                'type_col': type,
                                'action_type': 'discount',
                                'value_col': value_per_cycle,
                                'account_id': account_id,
                                'opposite_account_id': opposite_account_id,
                                'date_col': salaries_from_date.toString(Qt.ISODate),
                            }


                # print("**********ADD*********"+str(position_additions))
                # print("**********DIS*********"+str(position_discounts))


            # # 3-leaves
            if self.ui.salaries_include_leaves.isChecked():
                leaves = self.database_operations.fetchEmployeeLeaves(employee_id,salaries_from_date.toString(Qt.ISODate), 'active',False)
                for data in leaves:
                    id = data['id']
                    employee_id = data['employee_id']
                    leave_type_id = data['leave_type_id']
                    alternative_id = data['alternative_id']
                    duration_in_hours = data['duration_in_hours']
                    duration_in_days = data['duration_in_days']
                    leave_start_date = data['start_date']
                    date = data['date_col']
                    state = data['state_col']
                    employee_name = data['employee_name']
                    alternative_employee_name = data['alternative_employee_name']

                    leave_end_date = leave_start_date + timedelta(days=int(duration_in_days))

                    range_start = salaries_from_date.toPyDate() if leave_start_date < salaries_from_date.toPyDate() else leave_start_date
                    if leave_end_date > salaries_to_date.toPyDate():
                        range_end = salaries_to_date.toPyDate()
                        duration_in_days = (range_end - range_start).days + 1
                    else:
                        range_end = leave_end_date
                        duration_in_date_decimals = float(duration_in_days) % 1
                        duration_in_days = float((range_end - range_start).days) + duration_in_date_decimals

                    if salary_cycle == 'month':
                        month_duration_setting = self.database_operations.fetchHRSetting('setting_month_duration')
                        if month_duration_setting:
                            month_duration = month_duration_setting[0]
                            # print("month_duration="+str(month_duration))
                        else:
                            month_duration = 28
                        daily_salary = float(salary) / float(month_duration)
                    elif salary_cycle == 'hour':
                        department = self.database_operations.fetchDepartment(department_id)
                        if department:
                            day_hours = department[2]
                        else:
                            if default_day_hours:
                                day_hours = default_day_hours
                            else:
                                win32api.MessageBox(0, self.language_manager.translate('INSURANCE_ALERT_NO_WORK_DAYS_HOURS'), self.language_manager.translate('ERROR'))
                                return
                        daily_salary = salary * day_hours
                    elif salary_cycle == 'day':
                        daily_salary = salary
                    elif salary_cycle == 'week':
                        daily_salary = salary / 7

                    current_leave_discount = daily_salary * duration_in_days
                    leaves_discounts += current_leave_discount

                    # print("daily salary="+str(daily_salary))
                    # print("duration in days="+str(duration_in_days))
                    # print("leave discounts="+str(current_leave_discount))

            # # 4- extras
            if self.ui.salaries_include_extras.isChecked():
                extras = self.database_operations.fetchEmployeeExtra(employee_id, salaries_from_date.toString(Qt.ISODate))
                for data in extras:
                    id = data['id']
                    employee_id = data['employee_id']
                    department_id = data['department_id']
                    extra_start_date = data['start_date']
                    value = data['value_col']
                    duration_in_hours = data['duration_in_hours']
                    duration_in_days = data['duration_in_days']
                    currency_id = data['currency_id']
                    statement = data['statement_col']
                    account_id = data['account_id']
                    opposite_account_id = data['opposite_account_id']
                    state = data['state_col']


                    department_day_hours = self.database_operations.fetchDepartment(id=department_id)
                    if not department_day_hours:
                        department_day_hours = default_day_hours
                    else:
                        department_day_hours = department_day_hours['day_hours']

                    employee_data = self.database_operations.fetchEmployee(employee_id)
                    if employee_data:
                        employee_department_id = employee_data['department_id']
                    else:
                        employee_department_id = 0

                    if employee_department_id and department_id != employee_department_id:
                        extra_from_date = extra_start_date
                        extra_to_date = extra_start_date + timedelta(days=int(duration_in_days))
                        employee_transfers = self.database_operations.fetchEmployeeTransfers(employee_id, extra_from_date, extra_to_date)
                        latest_transfer = employee_transfers[0]
                        if latest_transfer:
                            extra_end_date = latest_transfer['date_col']
                            # Convert extra_to_date to date if it's a datetime to avoid type error
                            if isinstance(extra_end_date, datetime):
                                extra_end_date = extra_end_date.date()
                            if isinstance(extra_start_date, datetime):
                                extra_start_date = extra_start_date.date()
                            duration_in_days = (extra_end_date - extra_start_date).days



                    if not department_day_hours:
                        department_day_hours = default_day_hours

                    # Convert extra_start_date from string to datetime if it's a string
                    if isinstance(extra_start_date, str):
                        # Handle ISO format with time component (e.g., "2023-01-01T00:00:00")
                        if 'T' in extra_start_date:
                            extra_start_date = datetime.strptime(extra_start_date.split('T')[0], "%Y-%m-%d").date()
                        else:
                            extra_start_date = datetime.strptime(extra_start_date, "%Y-%m-%d").date()
                    extra_end_date = extra_start_date + timedelta(days=int(duration_in_days))
                    range_start = salaries_from_date.toPyDate() if extra_start_date < salaries_from_date.toPyDate() else extra_start_date
                    if extra_end_date > salaries_to_date.toPyDate():
                        range_end = salaries_to_date.toPyDate()
                        duration_in_days = (range_end - range_start).days + 1
                        # print("range_start="+str(range_start))

                    else:
                        range_end = extra_end_date
                        duration_in_date_decimals = float(duration_in_days) % 1
                        duration_in_days = float((range_end - range_start).days) + duration_in_date_decimals

                    current_extra_discount = value * float(department_day_hours) * duration_in_days
                    extras_additions += current_extra_discount

                    self.extras_map[id] = {
                        'id': id,
                        'employee_id': employee_id,
                        'date_col': extra_start_date,
                        'value_col': current_extra_discount,
                        'currency_id': currency_id,
                        'statement_col': "extra_work_payroll",
                        'account_id': account_id,
                        'opposite_account_id': opposite_account_id,
                    }
                    # print("daily salary="+str(daily_salary))
                    # print("duration in days="+str(duration_in_days))
                    # print("extra additions="+str(current_extra_discount))


            # 5-loans
            if self.ui.salaries_include_loans.isChecked():
                loans = self.database_operations.fetchLoansOfEmployee(employee_id)
                for data in loans:
                    id = data['id']
                    employee_id = data['employee_id']
                    value_col = data['value_col']
                    currency = data['currency']
                    date_col = data['date_col']
                    account_id = data['account_id']
                    opposite_account_id = data['opposite_account_id']
                    periodically_subtract_from_salary = data['periodically_subtract_from_salary']
                    subtract_currency = data['subtract_currency']
                    subtract_cycle = data['subtract_cycle']
                    subtract_value = data['subtract_value']
                    currency_name = data['currency_name']
                    account_name = data['account_name']
                    opposite_account_name = data['opposite_account_name']
                    total_payments = data['total_payments']
                    remaining_amount = data['remaining_amount']
                    subtract_currency_name = data['subtract_currency_name']

                    if not subtract_value:
                        subtract_value = float(periodically_subtract_from_salary)

                    if remaining_amount and periodically_subtract_from_salary:

                        subtract_currency_to_salary_currency_rate = None
                        loan_currency_to_salary_currency_rate = None
                        if subtract_currency and subtract_currency != salary_currency:
                            subtract_currency_to_salary_currency_rate = self.database_operations.fetchExchangeValue(
                                subtract_currency, salary_currency, exchange_price_date)
                            if not subtract_currency_to_salary_currency_rate:
                                msg = "لا يوجد سعر صرف بين " + subtract_currency_name + " وعملة راتب الموظف في التاريخ المحدد"
                                win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                                return
                        if currency != salary_currency:
                            loan_currency_to_salary_currency_rate = self.database_operations.fetchExchangeValue(
                                subtract_currency, salary_currency, exchange_price_date)
                            if not loan_currency_to_salary_currency_rate:
                                msg = "لا يوجد سعر صرف بين " + currency_name + " وعملة راتب الموظف في التاريخ المحدد"
                                win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                                return

                        if loan_currency_to_salary_currency_rate:
                            remaining_amount = float(remaining_amount) * float(loan_currency_to_salary_currency_rate)
                        if subtract_currency_to_salary_currency_rate:
                            subtract_value = float(subtract_currency_to_salary_currency_rate) * float(subtract_value)

                        subtracted_value = 0
                        for i in range(1, (int(cycles_count) + 1)):
                            if not currency:
                                subtract_value = salary * subtract_value / 100
                            if 0 < remaining_amount < subtract_value:
                                subtract_value = remaining_amount
                            subtracted_value += subtract_value
                            remaining_amount -= subtract_value
                            self.loan_map[f"{id}_{i}"] = {
                                'action_type': 'discount',
                                'id': id,
                                'employee_id': employee_id,
                                'value_col': subtract_value,
                                'account_id': account_id,
                                'statement_col': 'hr_loan_payment',
                                'opposite_account_id': opposite_account_id,
                                'currency_id': currency,
                                'source': 'loan',
                                'date_col': date_col,
                                'employee_id': employee_id,
                            }

                        loans_subtraction += subtracted_value
                        print("Loans Subtraction=" + str(loans_subtraction))


            # 6-Salary additions and discounts
            if self.ui.salaries_include_employee_additions_discounts.isChecked():
                salary_additions_discounts = self.database_operations.fetchSalaryAdditionsAndDiscounts(employee_id,'active')
                for data in salary_additions_discounts:
                    id = data['id']
                    employee_id = data['employee_id']
                    type = data['type_col']
                    start_date = data['start_date']
                    repeatition = data['repeatition']
                    value = data['value_col']
                    account_id = data['account_id']
                    opposite_account_id = data['opposite_account_id']
                    statement = data['statement_col']
                    currency_id = data['currency_id']
                    state = data['state_col']
                    currency_name = data['currency_name']
                    account_name = data['account_name']
                    opposite_account_name = data['opposite_account_name']
                    num_payments = data['num_payments']

                    valid = False
                    if type == "permenant addition":
                        valid = True
                    if type == "temporary addition":
                        if num_payments < repeatition:
                            valid = True
                    if type == "permenant discount":
                        valid = True
                    if type == "temporary discount":
                        if num_payments < repeatition:
                            valid = True

                    if valid:
                        entry_currency_to_salary_currency_rate = None
                        if currency_id != salary_currency:
                            entry_currency_to_salary_currency_rate = self.database_operations.fetchExchangeValue(
                                subtract_currency, salary_currency, exchange_price_date)
                            if not entry_currency_to_salary_currency_rate:
                                msg = "لا يوجد سعر صرف بين " + currency_name + " وعملة راتب الموظف في التاريخ المحدد"
                                win32api.MessageBox(0, msg, self.language_manager.translate("ALERT"))
                                return
                        if entry_currency_to_salary_currency_rate:
                            value = float(value) * float(entry_currency_to_salary_currency_rate)

                        for i, cycle_value in enumerate(cycles):
                            if not currency_id:  # the value is a percent
                                value = salary * value / 100
                            if "addition" in str(type).lower():
                                if "permenant" in str(type).lower() or num_payments < repeatition:
                                    salary_additions += value
                                    num_payments += 1
                                    self.addition_discount_map[f"{id}_{i}"] = {
                                        'action_type': 'addition',
                                        'id': id,
                                        'value_col': value,
                                        'account_id': account_id,
                                        'opposite_account_id': opposite_account_id,
                                        'currency_id': currency_id,
                                        'date_col': start_date,
                                        'employee_id': employee_id,
                                        'statement_col': 'employee_addition_payroll',
                                    }
                            if "discount" in str(type).lower():
                                if "permenant" in str(type).lower() or num_payments < repeatition:
                                    if cycle_value < value:
                                        value = cycle_value
                                    salary_discounts += value
                                    num_payments += 1
                                    self.addition_discount_map[f"{id}_{i}"] = {
                                        'action_type': 'discount',
                                        'id': id,
                                        'value_col': value,
                                        'account_id': account_id,
                                        'opposite_account_id': opposite_account_id,
                                        'currency_id': currency_id,
                                        'date_col': start_date,
                                        'employee_id': employee_id,
                                        'statement_col': 'employee_discount_payroll',
                                    }

                        # print("Salary additions=" + str(salary_additions))
                        # print("Salary discounts=" + str(salary_discounts))




            # aggregate results in employee's dictionary
            employee_dict['employee_id'] = employee_id
            employee_dict['employee_name'] = employee_name
            employee_dict['depratment_additions'] = depratment_additions
            employee_dict['department_discounts'] = department_discounts
            employee_dict['position_additions'] = position_additions
            employee_dict['position_discounts'] = position_discounts
            employee_dict['leaves_discounts'] = leaves_discounts
            employee_dict['extras_additions'] = extras_additions
            employee_dict['loans_subtraction'] = loans_subtraction
            employee_dict['salary_discounts'] = salary_discounts
            employee_dict['salary_additions'] = salary_additions
            employee_dict['cycles'] = cycles_count
            employee_dict['base_salary'] = base_salary

            self.base_salary[f'{employee_id}'] = base_salary - leaves_discounts

            priority = self.database_operations.fetchHRSetting('setting_priority_calculate_salary')


            if priority == 'total_sum':
                employee_pay_value = base_salary - leaves_discounts + depratment_additions - department_discounts + position_additions - position_discounts + extras_additions - loans_subtraction - salary_discounts + salary_additions
            elif priority == 'department':
                employee_pay_value = base_salary - leaves_discounts + depratment_additions - department_discounts + extras_additions - loans_subtraction - salary_discounts + salary_additions

            elif priority == 'position':
                employee_pay_value = base_salary - leaves_discounts + position_additions - position_discounts + extras_additions - loans_subtraction - salary_discounts + salary_additions

            elif priority == 'employee':
                employee_pay_value = base_salary

            else:
                employee_pay_value = base_salary - leaves_discounts + depratment_additions - department_discounts + position_additions - position_discounts + extras_additions - loans_subtraction - salary_discounts + salary_additions

            employee_dict['pay_value'] = employee_pay_value

            result[0].append(employee_dict)

        color_light_blue = QColor(204, 229, 255)
        brush_light_blue = QBrush(color_light_blue)
        color_medium_blue = QColor(102, 178, 255)
        brush_medium_blue = QBrush(color_medium_blue)
        color_dark_blue = QColor(0, 128, 255)
        brush_dark_blue = QBrush(color_dark_blue)
        brush_white = QBrush(Qt.white)

        salary_block = str(str(salaries_from_date.toString(Qt.ISODate) + " - " + salaries_to_date.toString(Qt.ISODate)))
        root_item = QTreeWidgetItem([salary_block, '', '', '', '', '', '', '', ''])
        for i in range(self.ui.salaries_result_tree.columnCount()):
            root_item.setBackground(i, brush_dark_blue)
            root_item.setForeground(i, brush_white)

        for employee_dict in result[0]:
            employee_id = employee_dict['employee_id']
            employee_name = employee_dict['employee_name']
            pay_value = employee_dict['pay_value']
            cycles = employee_dict['cycles']

            pay_value = round(pay_value, 4)
            cycles = round(cycles, 4)
            employee_root_item = QTreeWidgetItem(
                ['', str(employee_id), str(employee_name), str(cycles), str(salary_account_id), str(salary_opposite_account_id), '', str(pay_value), str(salary_currency),
                 str(salary_currency_name)])
            employee_root_item.setCheckState(0, Qt.Checked)
            for i in range(self.ui.salaries_result_tree.columnCount()):
                employee_root_item.setBackground(i, brush_medium_blue)
            root_item.addChild(employee_root_item)
            for key, value in employee_dict.items():
                if key not in ['employee_id', 'employee_name', 'cycles', 'pay_value']:
                    value = round(value, 4)
                    details_item = QTreeWidgetItem(
                        ['', '', '', '',  '', '', str(key), str(value), str(salary_currency), str(salary_currency_name)])
                    employee_root_item.addChild(details_item)
                    for i in range(self.ui.salaries_result_tree.columnCount()):
                        details_item.setBackground(i, brush_light_blue)

        self.ui.salaries_result_tree.addTopLevelItem(root_item)

    def processPayroll(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate("INSURANCE_ALERT_MULTIPLE_JOURNAL_ENTRIES"), self.language_manager.translate("ALERT"), MB_YESNO)
        if (messagebox_result == IDYES):

            default_salary_account = self.database_operations.fetchHRSetting('setting_salaries_account')
            if not default_salary_account:
                win32api.MessageBox(None, self.language_manager.translate("DEFAULT_SALARY_ACCOUNT_ID_NOT_SET"), self.language_manager.translate("ERROR"), MB_OK)
                return
            default_salary_account_id = default_salary_account['value_col']


            # get the dates
            try:
                first_item = self.ui.salaries_result_tree.topLevelItem(0)
                date_range = first_item.text(0)
                salaries_from_date, salaries_to_date = date_range.split(' - ')
            except:
                print("Error parsing from_date to_date")
                return

            # check for any overlaping
            previous_payrolls = self.database_operations.fetchPayrolls()
            salaries_from_date_dateObject = datetime.strptime(salaries_from_date, '%Y-%m-%d').date()
            salaries_to_date_dateObject = datetime.strptime(salaries_to_date, '%Y-%m-%d').date()
            for payroll in previous_payrolls:
                id = payroll[0]
                from_date = payroll[1]
                to_date = payroll[2]
                date_col = payroll[3]

                if (from_date <= salaries_from_date_dateObject <= to_date) or (
                        from_date <= salaries_to_date_dateObject <= to_date):
                    messagebox_result = win32api.MessageBox(None,self.language_manager.translate("INSURANCE_ALERT_BLOCKS"), self.language_manager.translate("ALERT"), MB_YESNO)

                    if (messagebox_result == IDYES):
                        break
                    elif (messagebox_result == IDNO):
                        return

            salaries_block_id = self.database_operations.addSalariesBlock(salaries_from_date, salaries_to_date)

            # Get the root item of the tree widget
            root_item = self.ui.salaries_result_tree.topLevelItem(0)
            if root_item:
                # Loop through only the first level children of the root
                for i in range(root_item.childCount()):
                    row = root_item.child(i)
                    period = row.text(0)
                    employee_id = row.text(1)
                    employee_name = row.text(2)
                    cycles = row.text(3)
                    salary_account_id = row.text(4)
                    salary_opposite_account_id = row.text(5)
                    paid_value = row.text(7)
                    statement = row.text(8)
                    currency_id = row.text(8)
                    currency = row.text(9)

                    if not employee_id:
                        if row.parent():
                            if row.parent().checkState(0) == Qt.Checked:
                                employee_id = row.parent().text(1)
                            else:
                                continue  # proceed to the next loop. Ignore the current employee because it is unchecked
                        else:  # if there's no parent, this is the root element.
                            pass
                    else:
                        if row.checkState(0) != Qt.Checked:
                            continue  # proceed to the next loop. Ignore the current employee because it is unchecked

                    if employee_id:
                        # Check if we have a valid account_id
                        if salaries_block_id:
                            if cycles:
                                self.database_operations.addSalariesBlockEntry(salaries_block_id, employee_id, "cycles",cycles, '')
                                if paid_value:
                                    self.database_operations.addSalariesBlockEntry(salaries_block_id, employee_id, "paid_value",paid_value, currency_id)
                        else:
                            pass

                        if self.ui.salaries_include_loans.isChecked():
                            for key, value in self.loan_map.items():
                                loan_payment_id = self.database_operations.addHRLoanPayment(value['id'], value['value_col'], value['currency_id'], 'salary_payment ', value['date_col'])
                                if not self.independent:
                                    if loan_payment_id:
                                        self.generateJournalEntryItems(loan_payment_id, value['employee_id'], value['currency_id'], value['statement_col'], salary_account_id, default_salary_account_id, value['date_col'] , value['value_col'])

                        if self.ui.salaries_include_employee_additions_discounts.isChecked():
                            for key, value in self.addition_discount_map.items():
                                if value['action_type'] == 'addition':
                                    entry_id = self.database_operations.addSalaryAdditionAndDiscountPayment(value['id'], value['date_col'])
                                    self.generateJournalEntryItems(entry_id, value['employee_id'], value['currency_id'], value['statement_col'], value['account_id'], salary_account_id, value['date_col'] , value['value_col'])
                                elif value['action_type'] == 'discount':
                                    entry_id = self.database_operations.addSalaryAdditionAndDiscountPayment(value['id'], value['date_col'])
                                    self.generateJournalEntryItems(entry_id, value['employee_id'], value['currency_id'], value['statement_col'], salary_account_id, value['account_id'], value['date_col'] , value['value_col'])
                                else:
                                    pass

                        if not self.independent:
                            if self.ui.salaries_include_extras.isChecked():
                                for key, value in self.extras_map.items():
                                    self.generateJournalEntryItems(value['id'], value['employee_id'], value['currency_id'], value['statement_col'], default_salary_account_id, salary_account_id, value['date_col'] , value['value_col'])

                            if self.ui.salaries_include_departments_additions_discounts.isChecked():
                                for key, value in self.department_addition_discount_map.items():
                                    if value['action_type'] == 'addition':
                                        self.generateJournalEntryItems(value['id'], value['employee_id'], value['currency_id'], value['statement_col'], value['account_id'], salary_account_id, value['date_col'] , value['value_col'])
                                    elif value['action_type'] == 'discount':
                                        self.generateJournalEntryItems(value['id'], value['employee_id'], value['currency_id'], value['statement_col'], salary_account_id, value['account_id'], value['date_col'] , value['value_col'])
                                    else:
                                        pass

                            if self.ui.salaries_include_positions_additions_discounts.isChecked():
                                for key, value in self.position_addition_discount_map.items():
                                    if value['action_type'] == 'addition':
                                        self.generateJournalEntryItems(value['id'], value['employee_id'], value['currency_id'], value['statement_col'], value['account_id'], salary_account_id, value['date_col'] , value['value_col'])
                                    elif value['action_type'] == 'discount':
                                        self.generateJournalEntryItems(value['id'], value['employee_id'], value['currency_id'], value['statement_col'], salary_account_id, value['account_id'], value['date_col'] , value['value_col'])
                                    else:
                                        pass


                        if not self.independent:
                            if employee_id:
                                entry_id = self.database_operations.addJournalEntry(datetime.today().strftime('%Y-%m-%d'), currency_id, 'base_salary' , salaries_block_id)

                                if entry_id:
                                    self.database_operations.addJournalEntryItem(entry_id,currency_id, 'creditor', 'base_salary', salary_account_id, salary_opposite_account_id, self.base_salary[employee_id])



        elif (messagebox_result == IDNO):
            pass

    def fetchPayrolls(self):
        payrolls = self.database_operations.fetchPayrolls()
        for payroll in payrolls:
            id = payroll['id']
            from_date = payroll['from_date']
            to_date = payroll['to_date']
            date = payroll['date_col']
            year = to_date.strftime('%Y')

            year_already_in_tree = self.ui.salaries_payroll_tree.findItems(str(year), Qt.MatchExactly | Qt.MatchRecursive,0)  # 0 is the column index in which to search
            if not year_already_in_tree:
                item = QTreeWidgetItem([str(year), '', ''])
                self.ui.salaries_payroll_tree.addTopLevelItem(item)
                # Get the index of the last top-level item
                index = self.ui.salaries_payroll_tree.topLevelItemCount() - 1
                # Get the last top-level item
                year_QTreeWidgetItem = self.ui.salaries_payroll_tree.topLevelItem(index)
                text = str(from_date) + "-" + str(to_date)
                item = QTreeWidgetItem(['', str(id), text])
                year_QTreeWidgetItem.addChild(item)
            else:
                years_already_in_tree = self.ui.salaries_payroll_tree.findItems(str(year),Qt.MatchExactly | Qt.MatchRecursive, 0)
                if (len(years_already_in_tree) > 0):  # Group already exists in tree, so append its child
                    year_QTreeWidgetItem = years_already_in_tree[0]  # only one would exist because we search using ID
                    text = str(from_date) + "-" + str(to_date)
                    item = QTreeWidgetItem(['', str(id), text])
                    year_QTreeWidgetItem.addChild(item)

    def fetchPayrollDetails(self):
        color_light_blue = QColor(204, 229, 255)
        brush_light_blue = QBrush(color_light_blue)
        color_medium_blue = QColor(102, 178, 255)
        brush_medium_blue = QBrush(color_medium_blue)

        self.ui.salaries_payroll_details_tree.clear()
        payroll_id = self.ui.salaries_payroll_tree.currentItem().text(1)
        if payroll_id and payroll_id != '':
            payroll_details = self.database_operations.fetchPayrollDetails(payroll_id)
            for data in payroll_details:
                id = data['id']
                salary_block_id = data['salary_block_id']
                employee_id = data['employee_id']
                statement = data['statement_col']
                value = data['value_col']
                currency = data['currency']
                name = data['name']
                currency_name = data['currency_name']
                from_date = data['from_date']
                to_date = data['to_date']

                employees_already_in_tree = self.ui.salaries_payroll_details_tree.findItems(str(employee_id),Qt.MatchExactly | Qt.MatchRecursive,0)
                if not employees_already_in_tree:
                    employee_item = QTreeWidgetItem([str(employee_id), str(name), '', '', '', '', '', ''])
                    for i in range(self.ui.salaries_payroll_details_tree.columnCount()):
                        employee_item.setBackground(i, brush_medium_blue)
                    self.ui.salaries_payroll_details_tree.addTopLevelItem(employee_item)
                    # Get the index of the last top-level item
                    index = self.ui.salaries_payroll_details_tree.topLevelItemCount() - 1
                    if statement == 'cycles':
                        added_employee = self.ui.salaries_payroll_details_tree.topLevelItem(index)
                        added_employee.setText(2, str(value))
                        self.ui.salaries_payroll_details_tree.update()
                    elif statement == 'paid_value':
                        added_employee = self.ui.salaries_payroll_details_tree.topLevelItem(index)
                        added_employee.setText(3, str(value))
                        self.ui.salaries_payroll_details_tree.update()
                    else:
                        item = QTreeWidgetItem(
                            ['', '', '', '', str(statement), str(value), str(currency), str(currency_name)])
                        for i in range(self.ui.salaries_payroll_details_tree.columnCount()):
                            item.setBackground(i, brush_light_blue)
                        employee_item.addChild(item)
                else:
                    if (len(employees_already_in_tree) > 0):  # Group already exists in tree, so append its child
                        employee_item = employees_already_in_tree[0]  # only one would exist because we search using ID
                        if statement == 'cycles':
                            employee_item.setText(2, str(value))
                            self.ui.salaries_payroll_details_tree.update()
                        elif statement == 'paid_value':
                            employee_item.setText(3, str(value))
                        else:
                            item = QTreeWidgetItem(
                                ['', '', '', '', str(statement), str(value), str(currency), str(currency_name)])
                            for i in range(self.ui.salaries_payroll_details_tree.columnCount()):
                                item.setBackground(i, brush_light_blue)
                            employee_item.addChild(item)

    def calculateInsurance(self):
        self.ui.insurance_result_tree.clear()
        insurance_from_date = self.ui.insurance_from_date_input.date()
        insurance_to_date = self.ui.insurance_to_date_input.date()
        exchange_price_date = self.ui.insurance_exchange_price_date_input.date().toString(Qt.ISODate)
        employees_finance_info = self.database_operations.fetchEmployeesFinanceInfo()

        result = []

        color_medium_blue = QColor(102, 178, 255)
        brush_medium_blue = QBrush(color_medium_blue)
        color_dark_blue = QColor(0, 128, 255)
        brush_dark_blue = QBrush(color_dark_blue)
        brush_white = QBrush(Qt.white)


        insurnace_delta = (insurance_from_date.daysTo(insurance_to_date)) + 1
        insurance_duration_days = insurnace_delta
        for data in employees_finance_info:
            insurance_value = 0
            cycles = []

            employee_id = data['employee_id']
            employee_name = data['name']
            position_id = data['position_id']
            position_name = data['position_name']
            department_id = data['department_id']
            department_name = data['department_name']
            bank = data['bank']
            bank_account_number = data['bank_account_number']
            bank_notes = data['bank_notes']
            salary = data['salary']
            salary_cycle = data['salary_cycle']
            salary_currency = data['salary_currency']
            insurance = data['insurance']
            salary_account_id = data['salary_account_id']
            salary_opposite_account_id = data['salary_opposite_account_id']
            insurance_account_id = data['insurance_account_id']
            insurance_opposite_account_id = data['insurance_opposite_account_id']
            insurance_currency = data['insurance_currency']
            insurance_cycle = data['insurance_cycle']
            salary_currency_name = data['salary_currency_name']
            insurance_currency_name = data['insurance_currency_name']

            employee_dict = {}  # a tree to hold employee date, and will be later added to result

            print("************** Emp=" + str(employee_id) + " **************")

            if insurance and insurance_currency and insurance_cycle:
                if insurance_cycle == 'day':
                    cycles_count = insurance_duration_days
                    for i in range(1, insurance_duration_days + 1):
                        cycles.append(insurance)
                    insurance_duration_days_decimals = insurance_duration_days % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                    if insurance_duration_days_decimals:
                        partial_insurance = insurance_duration_days_decimals * insurance
                        cycles.append(partial_insurance)
                if insurance_cycle == 'month':
                    month_days_count_setting = self.database_operations.fetchHRSetting('setting_month_duration')
                    if month_days_count_setting:
                        month_days_count = month_days_count_setting[0]
                        insurance_duration_month = float(insurance_duration_days) / float(month_days_count)
                        cycles_count = insurance_duration_month
                        for i in range(1, (int(insurance_duration_month) + 1)):
                            cycles.append(insurance)
                        insurance_duration_month_decimals = insurance_duration_month % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                        if insurance_duration_month_decimals:
                            partial_insurance = insurance_duration_month_decimals * insurance
                            cycles.append(partial_insurance)
                    else:
                        win32api.MessageBox(0, self.language_manager.translate("HR_NO_WORK_DAYS_MONTH"), self.language_manager.translate("ALERT"))
                        return
                if insurance_cycle == 'week':
                    department = self.database_operations.fetchDepartment(department_id)
                    if department:
                        department_id = department[0]
                        department_name = department[1]
                        department_day_hours = department[2]
                        department_account_id = department[3]
                        department_opposite_account_id = department[4]
                        department_notes = department[5]
                        department_work_day_saturday = department['department_work_day_saturday']
                        department_work_day_sunday = department['department_work_day_sunday']
                        department_work_day_monday = department['department_work_day_monday']
                        department_work_day_tuesday = department['department_work_day_tuesday']
                        department_work_day_wednesday = department['department_work_day_wednesday']
                        department_work_day_thursday = department['department_work_day_thursday']
                        department_work_day_friday = department['department_work_day_friday']
                        week_days_count = 0
                        for d in [department_work_day_saturday, department_work_day_sunday,
                                  department_work_day_monday, department_work_day_tuesday,
                                  department_work_day_wednesday, department_work_day_thursday,
                                  department_work_day_friday]:
                            if d:
                                week_days_count += 1
                        if week_days_count:
                            insurance_duration_week = insurance_duration_days / week_days_count
                            cycles_count = insurance_duration_week
                            for i in range(1, (int(insurance_duration_week) + 1)):
                                cycles.append(insurance)
                            insurance_duration_week_decimals = insurance_duration_week % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                            if insurance_duration_week_decimals:
                                partial_insurance = insurance_duration_week_decimals * salary
                                cycles.append(partial_insurance)
                        else:
                            msg = self.language_manager.translate('INSURANCE_ALERT_NO_WORK_DAYS') + str(employee_id)
                            win32api.MessageBox(0, msg, self.language_manager.translate('ALERT'))
                            return
                if insurance_cycle == 'hour':
                    department = self.database_operations.fetchDepartment(department_id)
                    if department:
                        # department_id = department[0]
                        department_name = department[1]
                        department_day_hours = department[2]
                        # department_account_id = department[3]
                        # department_opposite_account_id = department[4]
                        # department_notes = department[5]
                        # department_work_day_saturday = department[6]
                        # department_work_day_sunday = department[7]
                        # department_work_day_monday = department[8]
                        # department_work_day_tuesday = department[9]
                        # department_work_day_wednesday = department[10]
                        # department_work_day_thursday = department[11]
                        # department_work_day_friday = department[12]

                    if department_day_hours:
                        insurance_duration_hours = insurance_duration_days * department_day_hours
                        cycles_count = insurance_duration_hours
                        for i in range(1, (int(insurance_duration_hours) + 1)):
                            cycles.append(salary)
                        insurance_duration_hours_decimals = insurance_duration_hours % 1  # sometimes the duration is not a perfect days count. eg. salary_duration_days=1.5, one and a half day
                        if insurance_duration_hours_decimals:
                            partial_insurance = insurance_duration_hours_decimals * insurance
                            cycles.append(partial_insurance)
                    else:
                        msg = self.language_manager.translate('INSURANCE_ALERT_NO_WORK_HOURS') + str(department_name)
                        win32api.MessageBox(0, msg, self.language_manager.translate('ALERT'))
                        return

                if len(cycles) > 0:
                    insurance_value = sum(cycles)
                    insurance_value=round(insurance_value, 3)
                    cycles_count=round(cycles_count, 3)
                employee_dict['employee_id'] = employee_id
                employee_dict['employee_name'] = employee_name
                employee_dict['cycles'] = cycles_count
                employee_dict['insurance_value'] = insurance_value

                result.append(employee_dict)



        insurance_block = str(str(insurance_from_date.toString(Qt.ISODate) + " - " + insurance_to_date.toString(Qt.ISODate)))
        root_item = QTreeWidgetItem([insurance_block, '', '', '', '', '', ''])
        for i in range(self.ui.insurance_result_tree.columnCount()): #coloring
            root_item.setBackground(i, brush_dark_blue)
            root_item.setForeground(i, brush_white)

        for employee_dict in result:
            employee_id = employee_dict['employee_id']
            employee_name = employee_dict['employee_name']
            insurance_value = employee_dict['insurance_value']
            cycles = employee_dict['cycles']

            cycles = round(cycles, 3)
            employee_root_item = QTreeWidgetItem(
                ['', str(employee_id), str(employee_name), str(cycles), str(insurance_value), str(insurance_currency),
                    str(insurance_currency_name)])
            employee_root_item.setCheckState(0, Qt.Checked)
            for i in range(self.ui.insurance_result_tree.columnCount()):
                employee_root_item.setBackground(i, brush_medium_blue)
            root_item.addChild(employee_root_item)

        self.ui.insurance_result_tree.addTopLevelItem(root_item)

    def openInsuranceReportWindow(self):
        Ui_Insurance_Report_Logic(self.sql_connector).showUi()

    def processInsurances(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate('INSURANCE_ALERT_MULTIPLE_JOURNAL_ENTRIES'), self.language_manager.translate('ALERT'), MB_YESNO)
        if (messagebox_result == IDYES):
            # get the dates
            try:
                first_item = self.ui.insurance_result_tree.topLevelItem(0)
                date_range = first_item.text(0)
                insurance_from_date, insurance_to_date = date_range.split(' - ')
            except:
                print("Error parsing from_date to_date")
                return

            # check for any overlaping
            previous_insurance_payrolls = self.database_operations.fetchInsurancePayrolls()
            insurance_from_date_dateObject = datetime.strptime(insurance_from_date, '%Y-%m-%d').date()
            insurance_to_date_dateObject = datetime.strptime(insurance_to_date, '%Y-%m-%d').date()
            for insurance_payroll in previous_insurance_payrolls:
                id = insurance_payroll['id']
                # from_date = datetime.strptime(insurance_payroll['from_date'], '%Y-%m-%d').date()
                # to_date = datetime.strptime(insurance_payroll['to_date'], '%Y-%m-%d').date()
                from_date = insurance_payroll['from_date']
                to_date = insurance_payroll['to_date']
                date = insurance_payroll['date_col']

                if (from_date <= insurance_from_date_dateObject <= to_date) or (
                        from_date <= insurance_to_date_dateObject <= to_date):
                    messagebox_result = win32api.MessageBox(None, self.language_manager.translate( 'INSURANCE_ALERT_BLOCKS'),self.language_manager.translate('ALERT'), MB_YESNO)
                    if (messagebox_result == IDYES):
                        break
                    elif (messagebox_result == IDNO):
                        return

            # Get the root item of the tree widget
            for row in self.ui.insurance_result_tree.findItems("*", Qt.MatchWrap | Qt.MatchWildcard | Qt.MatchRecursive):
                period = row.text(0)
                employee_id = row.text(1)
                employee_name = row.text(2)
                cycles = row.text(3)
                paid_value = row.text(4)
                currency_id = row.text(5)
                currency = row.text(6)

                if not employee_id:
                    if row.parent():
                        if row.parent().checkState(0) == Qt.Checked:
                            employee_id = row.parent().text(1)
                        else:
                            continue  # proceed to the next loop. Ignore the current employee because it is unchecked
                    else:  # if there's no parent, this is the root element.
                        pass
                else:
                    if row.checkState(0) != Qt.Checked:
                        continue  # proceed to the next loop. Ignore the current employee because it is unchecked
                    employee_info = self.database_operations.fetchEmployeeFinanceInfo(employee_id)
                    insurance_account_id = employee_info['insurance_account_id']
                    insurance_opposite_account_id = employee_info['insurance_opposite_account_id']

                if period:
                    insurance_block_id = self.database_operations.addInsuranceBlock(insurance_from_date,
                    insurance_to_date)

                else:
                    if insurance_block_id:
                        if cycles and paid_value:
                            paid_value = round(float(paid_value), 3)
                            cycles = round(float(cycles), 3)
                            self.database_operations.addInsuranceBlockEntry(insurance_block_id, employee_id, cycles, paid_value, currency_id)
                        journal_entry_id = None

                        if not self.independent:
                            statment = self.language_manager.translate('INSURANCE_STATEMENT') + ' ' + employee_name
                            current_date = QDate.currentDate().toString(Qt.ISODate)
                            journal_entry_id = self.database_operations.addJournalEntry(current_date, currency_id, 'insurance', insurance_block_id)

                            if journal_entry_id:
                                self.database_operations.addJournalEntryItem(journal_entry_id, int(currency_id), 'creditor', statment, insurance_account_id, insurance_opposite_account_id, paid_value)
                                self.ui.insurance_result_tree.takeTopLevelItem(0)

            self.fetchInsurancePayrolls()

        elif (messagebox_result == IDNO):
            pass


    def fetchInsurancePayrolls(self):
        # clear the tree
        self.ui.insurance_payroll_tree.clear()

        payrolls = self.database_operations.fetchInsurancePayrolls()
        for payroll in payrolls:
            id = payroll['id']
            from_date = payroll['from_date']
            to_date = payroll['to_date']
            date = payroll['date_col']
            to_date_datetime = datetime.strptime(str(to_date), '%Y-%m-%d')
            year = to_date_datetime.year

            year_already_in_tree = self.ui.insurance_payroll_tree.findItems(str(year),Qt.MatchExactly | Qt.MatchRecursive,0)  # 0 is the column index in which to search
            if not year_already_in_tree:
                item = QTreeWidgetItem([str(year), '', ''])
                self.ui.insurance_payroll_tree.addTopLevelItem(item)
                # Get the index of the last top-level item
                index = self.ui.insurance_payroll_tree.topLevelItemCount() - 1
                # Get the last top-level item
                year_QTreeWidgetItem = self.ui.insurance_payroll_tree.topLevelItem(index)
                text = str(from_date) + "-" + str(to_date)
                item = QTreeWidgetItem(['', str(id), text])
                year_QTreeWidgetItem.addChild(item)
            else:
                years_already_in_tree = self.ui.insurance_payroll_tree.findItems(str(year), Qt.MatchExactly | Qt.MatchRecursive, 0)
                # print("L=" + str(len(groups_already_in_tree)))
                if (len(years_already_in_tree) > 0):  # Group already exists in tree, so append its child
                    year_QTreeWidgetItem = years_already_in_tree[0]  # only one would exist because we search using ID
                    text = str(from_date) + "-" + str(to_date)
                    item = QTreeWidgetItem(['', str(id), text])
                    year_QTreeWidgetItem.addChild(item)


    def fetchInsurancePayrollDetails(self):
        color_dark_blue = QColor(0, 128, 255)
        brush_dark_blue = QBrush(color_dark_blue)
        brush_white = QBrush(Qt.white)


        self.ui.insurance_payroll_details_tree.clear()
        insurance_payroll_id = self.ui.insurance_payroll_tree.currentItem().text(1)
        if insurance_payroll_id and insurance_payroll_id != '':
            insurance_payroll_details = self.database_operations.fetchInsurancePayrollDetails(insurance_payroll_id)
            for data in insurance_payroll_details:
                id = data[0]
                insurance_block_id = data[1]
                employee_id = data[2]
                cycles = data[3]
                value = data[4]
                currency = data[5]
                name = data[6]
                currency_name = data[7]
                from_date = data[8]
                to_date = data[9]

                employee_item = QTreeWidgetItem([str(employee_id), str(name), str(cycles), str(value), str(currency), str(currency_name)])

                for i in range(self.ui.insurance_payroll_details_tree.columnCount()):
                    employee_item.setBackground(i, brush_dark_blue)
                    employee_item.setForeground(i, brush_white)

                self.ui.insurance_payroll_details_tree.addTopLevelItem(employee_item)


    def generateJournalEntryItems(self, id, employee_id, currency_id, statement, account_id, opposite_account_id, date_col, value):
        if employee_id:
            entry_id = self.database_operations.addJournalEntry(date_col, currency_id, origin_type=statement , origin_id=id)

            if entry_id:
                self.database_operations.addJournalEntryItem(entry_id,currency_id, 'creditor', statement, account_id, opposite_account_id, value)



    def DisableAccountInputs(self):
        # Find and disable all comboboxes and buttons containing "account" in their name
        for widget in self.ui.__dict__.values():
            if isinstance(widget, (QComboBox, QPushButton)) and "account" in widget.objectName().lower():
                if isinstance(widget, QComboBox):
                    widget.clear()  # Clear the combobox items before disabling
                    self.ui.employee_salary_account_combobox.clear()
                widget.setEnabled(False)



if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    hr_logic = Ui_HR_Logic(independent=True)
    hr_logic.showUi()
    sys.exit(app.exec_())
