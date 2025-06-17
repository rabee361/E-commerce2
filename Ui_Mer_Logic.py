import os
import sys
import datetime
import re
import random
from LanguageManager import LanguageManager
from Ui_DBPassword_Logic import Ui_DBPassword_Logic
from datetime import datetime

from PyQt5.QtCore import QTranslator, QCoreApplication
import locale
from PyQt5.QtGui import QKeySequence
from win32con import MB_OK
import win32con
from Ui_QuantitiesReport_Logic import Ui_QuantitiesReport_Logic
from PyQt5.QtCore import Qt
import ntplib as ntplib
from PyQt5.QtCore import QObject
from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QWidget, QPushButton, QMessageBox , QMenu
from PyQt5 import QtWidgets
from ToolbarManager import ToolbarManager
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QPixmap
from Colors import light_yellow_color
from FileManager import FileManager
from SqliteConnector import SqliteConnector
from StyleApplicator import StyleApplicator
from Ui_Account_Movements_Logic import Ui_Account_Movements_Logic
from Ui_Accounts_Logic import Ui_Accounts_Logic
from Ui_Clients_Logic import Ui_Clients_Logic
from Ui_ClientReport_Logic import Ui_ClientReport_Logic
from Ui_Configuration_Logic import Ui_Configuration_Logic
from Ui_CostCentersReport_logic import Ui_CostCentersReport_Logic
from Ui_CostCenters_Logic import Ui_CostCenters_Logic
from Ui_Insurance_Report_Logic import Ui_Insurance_Report_Logic
from Ui_Employee_Report_Logic import Ui_Employee_Report_Logic
from Ui_Salary_Report_Logic import Ui_Salary_Report_Logic
from Ui_Position_Report_Logic import Ui_Position_Report_Logic
from Ui_CostProcesses_Logic import Ui_CostProcesses_Logic
from Ui_DailyJournal_Logic import Ui_DailyJournal_Logic
from Ui_Value_Report_Logic import Ui_Value_Report_Logic
from Ui_Department_Report_Logic import Ui_Department_Report_Logic
from Ui_DatabaseBackupRestore_Logic import Ui_DatabaseBackupRestore_Logic
from Ui_DatabaseSettings_Logic import Ui_DatabaseSettings_Logic
from Ui_Users_Logic import Ui_Users_Logic
from Ui_Activation_Logic import Ui_Activation_Logic
from Ui_AccountBalance_Logic import Ui_AccountBalance_Logic
from Ui_Currencies_Logic import Ui_Currencies_Logic
from Ui_Aggregator_Logic import Ui_Aggregator_Logic
from Ui_AutoAggregator_Logic import Ui_AutoAggregator_Logic
from Ui_ClientInvoices_Logic import Ui_ClientInvoices_Logic
from Ui_Expenses_Logic import Ui_Expenses_Logic
from Ui_Export_Logic import Ui_Export_Logic
from Ui_FinalAccountsReports_Logic import Ui_FinalAccountsReports_Logic
from Ui_FinancialStatementsReports_Logic import Ui_FinancialStatementsReports_Logic
from Ui_Groups_Logic import Ui_Groups_Logic
from Ui_HR_Logic import Ui_HR_Logic
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
from Ui_SalesReport_Logic import Ui_SalesReport_Logic
from Ui_ProductProfitReport_Logic import Ui_ProductProfitReport_Logic
from Ui_InvoicesList_Logic import Ui_InvoicesList_Logic
from Ui_Journal_Logic import Ui_Journal_Logic
from Ui_Ledger_Logic import Ui_Ledger_Logic
from Ui_MachinesAndResources_Logic import Ui_MachinesAndResources_Logic
from Ui_Manufacture_Cost_Fix_Logic import Ui_Manufacture_Cost_Fix_Logic
from Ui_ManufactureProcesses_Logic import Ui_ManufactureProcesses_Logic
from Ui_Materials_Logic import Ui_Materials_Logic
from Ui_Mer import Ui_Mer
from Ui_MaterialMoveReport_Logic import Ui_MaterialMoveReport_Logic
from Ui_Payments_Logic import Ui_Payments_Logic
from Ui_PriceManagement_Logic import Ui_PricesManagement_Logic
from Ui_ProductSales_Logic import Ui_ProductSales_Logic
from Ui_NewInvoice_Logic import *
from Ui_About_Logic import Ui_About_Logic
from Ui_JournalVoucher_Logic import Ui_JournalVoucher_Logic
from Ui_Sales_Target_Logic import Ui_Sales_Target_Logic
from Ui_Sales_Target_Report_Logic import Ui_Sales_Target_Report_Logic
from Ui_Settings_Logic import Ui_Settings_Logic
from Ui_SimplePlan_Logic import Ui_SimplePlan_Logic
from Ui_ReOrderMaterialReport_Logic import Ui_ReOrderMaterialReport_Logic
from Ui_PeriodStart_Logic import Ui_PeriodStart_Logic
from Ui_PlanPercent_Logic import Ui_PlanPercent_Logic
from Ui_Synchronizer_Logic import Ui_Synchronizer_Logic
from Ui_Units_Logic import Ui_Units_Logic
from Ui_Warehouses_Logic import Ui_Warehouses_Logic
from Ui_Trial_Balance_Logic import Ui_Trial_Balance_Logic
from Ui_FinancialStatements_Logic import Ui_FinancialStatements_Logic
from Ui_ReceiptDocs_Logic import Ui_ReceiptDocs_Logic
from Ui_Loans_Logic import Ui_Loans_Logic
from mac_address import mac_address
from Importer import Importer
from Statistics import Statistics
from WindowsManager import WindowsManager
from Ui_AuthenticateUser_Logic import Ui_AuthenticateUser_Logic
from Ui_InventoryReport_Logic import Ui_InventoryReport_Logic
from Ui_AuthenticateUser_Logic import current_user
from LCDClock import DigitalDisplay
from PyQt5.QtWidgets import QDialog, QPushButton, QVBoxLayout, QApplication, QSplashScreen 
from Ui_Calculator_Logic import Ui_Calculator_Logic
# from ChatComponent import ChatComponent
# from ChatBotAdapter import ChatBotAdapter
# from chatbot import Services
# from PermissionDecoratorClass import check_permission

class Ui_Mer_Logic(QObject):
    def __init__(self):
        super().__init__()
        self.database_operations = ''
        self.importer = ''
        self.filemanager = ''
        self.sql_connector = ''
        self.isActive = False
        self.app = ''
        self.window = ''
        self.hr_window = ''
        self.memory = 0
        self.windows_manager = ''
        self.current_user = ''
        self.ui = Ui_Mer()
        self.toolbar_manager = ''
        self.digital_clock = ''
        self.digital_date = ''
        self.statistics = None
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.default_language = ''
        self.current_language = ''
        self.chat_component = None
        # self.chatbot = None

    # # Define permission as a method
    # def permission(self, criteria_name, required_type):
    #     return self.permissions.check_permission(criteria_name, required_type, self.sql_connector)
    
    def showUi(self):
        app = QApplication(sys.argv)
        window = QMainWindow()
        StyleApplicator.apply_global_style()
        self.filemanager = FileManager()
        self.app = app
        self.window = window
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize()
        window.showMaximized()
        self.windows_manager = WindowsManager(app)
        self.showToolBar()
        window.closeEvent = self.closeAllWindows
        app.installEventFilter(self)
        app.exec()

    def initialize(self):
        self.default_language = self.language_manager.load_default_language()
        self.current_language = self.default_language
        
        # Create digital displays
        self.digital_clock = DigitalDisplay(display_type='time')
        self.digital_date = DigitalDisplay(display_type='date')
        
        if hasattr(self.ui, 'clock_label'):
            # Get the parent layout of clock_label
            parent_layout = self.ui.clock_label.parent().layout()
            # Remove the old labels
            self.ui.clock_label.hide()
            if hasattr(self.ui, 'date_label'):
                self.ui.date_label.hide()
            
            # Add the new digital displays
            parent_layout.addWidget(self.digital_date)
            parent_layout.addWidget(self.digital_clock)

        self.ui.option_new.triggered.connect(lambda: self.closeAllWindows() and self.createFile(self.window))
        self.ui.option_new.setShortcut(QKeySequence("Ctrl+N"))
        self.ui.option_open.triggered.connect(lambda: self.closeAllWindows() and self.openFile(self.window))
        self.ui.option_open.setShortcut(QKeySequence("Ctrl+O"))
        self.ui.option_connect_to_database.triggered.connect(lambda: self.closeAllWindows() and self.openDatabaseSettings())
        self.ui.option_connect_to_database.setShortcut(QKeySequence("Ctrl+D"))
        self.ui.option_switch_user.triggered.connect(lambda: self.closeAllWindows() and self.openSwitchUserWindow())
        self.ui.option_switch_user.setShortcut(QKeySequence("Ctrl+1"))
        self.ui.option_users.triggered.connect(lambda: self.closeAllWindows() and self.openUsersWindow())
        self.ui.option_users.setShortcut(QKeySequence("Ctrl+U"))
        self.ui.option_exit.triggered.connect(lambda: self.closeAllWindows() and self.closeApp())
        self.ui.option_exit.setShortcut(QKeySequence("esc"))
        # self.ui.option_warehouse_variables.triggered.connect(lambda: self.openWarehouseVariablesWindow())
        self.ui.option_invoices_view.triggered.connect(lambda: self.openInvoicesListWindow())
        self.ui.option_invoices_view.setShortcut(QKeySequence("Alt+F1"))
        self.ui.option_customers.triggered.connect(lambda: self.openCustomersWindow())
        self.ui.option_customers.setShortcut(QKeySequence("Alt+F3"))
        self.ui.option_suppliers.triggered.connect(lambda: self.openSuppliersWindow())
        self.ui.option_suppliers.setShortcut(QKeySequence("Alt+F4"))
        self.ui.option_expenses.triggered.connect(lambda: self.openExpensesWindow())
        self.ui.option_expenses.setShortcut(QKeySequence("Ctrl+F9"))
        self.ui.option_invoice_receipt_vouchers.triggered.connect(lambda: self.openPaymentsWindow('receipt'))
        self.ui.option_invoice_receipt_vouchers.setShortcut(QKeySequence("Alt+F7"))
        self.ui.option_invoice_payment_vouchers.triggered.connect(lambda: self.openPaymentsWindow('payment'))
        self.ui.option_invoice_payment_vouchers.setShortcut(QKeySequence("Alt+F8"))
        self.ui.option_customers_invoices.triggered.connect(lambda: self.openClientsInvoicesWindow(client_type='customer'))
        self.ui.option_customers_invoices.setShortcut(QKeySequence("Alt+F5"))
        self.ui.option_suppliers_invoices.triggered.connect(lambda: self.openClientsInvoicesWindow(client_type='supplier'))
        self.ui.option_suppliers_invoices.setShortcut(QKeySequence("Alt+F6"))
        self.ui.option_about.triggered.connect(lambda: self.openAbout())
        self.ui.option_about.setShortcut(QKeySequence("Alt+9"))
        self.ui.option_manufacure.triggered.connect(lambda: self.openManufactureWindow())
        self.ui.option_manufacure.setShortcut(QKeySequence("Ctrl+F8"))
        self.ui.option_cost.triggered.connect(lambda: self.openCostWindow())
        self.ui.option_cost.setShortcut(QKeySequence("Ctrl+F9"))
        self.ui.option_database_backup.triggered.connect(lambda: self.closeAllWindows() and self.openDatabaseBackup())
        self.ui.option_database_backup.setShortcut(QKeySequence("Ctrl+B"))
        self.ui.option_simple_plan.triggered.connect(lambda: self.openPlanWindow())
        self.ui.option_simple_plan.setShortcut(QKeySequence("Alt+F10"))
        self.ui.option_percent_plan.triggered.connect(lambda: self.openPlanPercentWindow())
        self.ui.option_percent_plan.setShortcut(QKeySequence("Alt+F11"))
        self.ui.option_aggregator.triggered.connect(lambda: self.openAggregator())
        self.ui.option_aggregator.setShortcut(QKeySequence("Alt+1"))
        self.ui.option_auto_aggregator.triggered.connect(lambda: self.openAutoAggregator())
        self.ui.option_auto_aggregator.setShortcut(QKeySequence("Alt+2"))
        self.ui.option_material_move_report.triggered.connect(lambda: self.openMaterialMoveReportWindow())
        self.ui.option_material_move_report.setShortcut(QKeySequence("Alt+5"))
        self.ui.option_product_sales.triggered.connect(lambda: self.openProductSalesWindow())
        self.ui.option_product_sales.setShortcut(QKeySequence("Alt+3"))
        self.ui.option_sales_report.triggered.connect(lambda: self.openSalesReportWindow())
        self.ui.option_sales_report.setShortcut(QKeySequence("Alt+3"))
        self.ui.option_client_report.triggered.connect(lambda: self.openClientReportWindow())
        self.ui.option_client_report.setShortcut(QKeySequence("Alt+7"))
        self.ui.option_supplier_report.triggered.connect(lambda: self.openSupplierReportWindow())
        self.ui.option_quantities_report.setShortcut(QKeySequence("Alt+/"))
        self.ui.option_quantities_report.triggered.connect(lambda: self.openQuantitiesReportWindow())
        self.ui.option_supplier_report.setShortcut(QKeySequence("Alt+8"))
        self.ui.option_sales_plan.triggered.connect(lambda: self.openSalesTargetWindow())
        self.ui.option_sales_plan.setShortcut(QKeySequence("Alt+F12"))
        self.ui.option_sales_target.triggered.connect(lambda: self.openSalesTargetReportWindow())
        self.ui.option_sales_target.setShortcut(QKeySequence("Alt+4"))
        self.ui.option_fix.triggered.connect(lambda: self.openManufactureCostFixWindow())
        self.ui.option_fix.setShortcut(QKeySequence("Ctrl+F10"))
        self.ui.option_accounts_guide.triggered.connect(lambda: self.openAccountsGuideWindow())
        self.ui.option_accounts_guide.setShortcut(QKeySequence("F5"))
        self.ui.option_loans.triggered.connect(lambda: self.openLoansWindow())
        self.ui.option_loans.setShortcut(QKeySequence("Ctrl+F3"))
        self.ui.option_settings.triggered.connect(lambda: self.closeAllWindows() and self.openSettingsWindow())
        self.ui.option_settings.setShortcut(QKeySequence("Ctrl+S"))
        self.ui.option_groups.triggered.connect(lambda: self.openGroupsWindow())
        self.ui.option_groups.setShortcut(QKeySequence("F1"))
        self.ui.option_materials.triggered.connect(lambda: self.openMaterialsWindow())
        self.ui.option_materials.setShortcut(QKeySequence("F2"))
        self.ui.menu_warehouses.aboutToShow.connect(lambda: self.openWarehousesList())
        self.ui.option_reorder_report.setShortcut(QKeySequence("Alt+;"))
        self.ui.option_reorder_report.triggered.connect(lambda: self.openReOrderMaterialReportWindow())
        self.ui.option_department_report.triggered.connect(lambda: self.openDepartmentReportWindow())
        self.ui.option_inusrance_report.triggered.connect(lambda: self.openInsuranceReportWindow())
        self.ui.option_employee_report.triggered.connect(lambda: self.openEmployeeReportWindow())
        self.ui.option_salary_report.triggered.connect(lambda: self.openSalaryReportWindow())
        self.ui.option_position_report.triggered.connect(lambda: self.openPositionReportWindow())
        self.ui.menu_accounts.aboutToShow.connect(lambda: self.openFinalAccountsList())
        self.ui.menu_accounts.aboutToShow.connect(lambda: self.openFinancialStatementsList())
        self.ui.option_price_management.triggered.connect(lambda: self.openPriceManagementWindow())
        self.ui.option_price_management.setShortcut(QKeySequence("F3"))
        self.ui.option_units.triggered.connect(lambda: self.openUnitsWindow())
        self.ui.option_units.setShortcut(QKeySequence("F4"))
        self.ui.option_cost_centers.triggered.connect(lambda: self.openCostCentersWindow())
        self.ui.option_cost_centers.setShortcut(QKeySequence("Ctrl+F6"))
        self.ui.option_cost_centers_reports.triggered.connect(lambda: self.openCostCentersReportsWindow())
        self.ui.option_cost_centers_reports.setShortcut(QKeySequence("Ctrl+F7"))
        self.ui.option_new_invoice.triggered.connect(lambda: self.openNewInvoiceWindow())
        self.ui.option_new_invoice.setShortcut(QKeySequence("Alt+F2"))
        self.ui.option_HR.triggered.connect(lambda: self.openHRWindow())
        self.ui.option_HR.setShortcut(QKeySequence("Ctrl+Q"))
        self.ui.option_machines_and_resources.triggered.connect(lambda: self.openMachinesAndResourcesWindow())
        self.ui.option_machines_and_resources.setShortcut(QKeySequence("Ctrl+F11"))
        self.ui.option_journal.triggered.connect(lambda: self.openJournalWindow())
        self.ui.option_journal.setShortcut(QKeySequence("F6"))
        self.ui.option_receipt_vouchers.triggered.connect(lambda: self.openReceiptVouchersWindow())
        self.ui.option_receipt_vouchers.setShortcut(QKeySequence("Alt+F7"))
        self.ui.option_payment_vouchers.triggered.connect(lambda: self.openPaymentVouchersWindow())
        self.ui.option_payment_vouchers.setShortcut(QKeySequence("Alt+F8"))
        self.ui.option_account_balance.triggered.connect(lambda: self.openAccountBalanceWindow())
        # self.ui.option_account_balance.setShortcut(QKeySequence("F6"))
        self.ui.option_final_accounts.triggered.connect(lambda: self.openFinalAccountsWindow())
        self.ui.option_final_accounts.setShortcut(QKeySequence("F7"))
        self.ui.option_period_start.triggered.connect(lambda: self.openPeriodStartWindow())
        self.ui.option_period_start.setShortcut(QKeySequence("Ctrl+T"))
        self.ui.option_period_opening_journal_entry.triggered.connect(lambda: self.openPeriodOpeningJournalEntriesWindow())
        self.ui.option_period_opening_journal_entry.setShortcut(QKeySequence("F8"))
        self.ui.option_daily_journal.triggered.connect(lambda: self.openDailyJournalWindow())
        self.ui.option_daily_journal.setShortcut(QKeySequence("F9"))
        self.ui.option_ledger.triggered.connect(lambda: self.openLedgerWindow())
        self.ui.option_ledger.setShortcut(QKeySequence("F10"))
        self.ui.option_trial_balance.triggered.connect(lambda: self.openTrialBalanceWindow())
        self.ui.option_trial_balance.setShortcut(QKeySequence("F11"))
        self.ui.option_account_movements.triggered.connect(lambda: self.openAccountMovementsWindow())
        self.ui.option_account_movements.setShortcut(QKeySequence("F12"))
        self.ui.option_material_receipt_docs.triggered.connect(lambda: self.openReceiptDocsWindow())
        self.ui.option_material_receipt_docs.setShortcut(QKeySequence("Alt+F9"))
        self.ui.option_inventory.triggered.connect(lambda: self.openWarehouseMoveWindow())
        self.ui.option_inventory.setShortcut(QKeySequence("Alt+6")) 
        self.ui.option_value_report.triggered.connect(lambda: self.openValueReportWindow())
        self.ui.option_value_report.setShortcut(QKeySequence("Alt+.")) 

        self.ui.option_financial_statements_settings.triggered.connect(lambda: self.openFinancialStatementsSettingsWindow())
        self.ui.option_financial_statements_report.triggered.connect(lambda: self.openFinancialStatementsReportWindow())

        self.ui.option_synchronizer.triggered.connect(lambda: self.closeAllWindows() and self.openSyncWindow())
        self.ui.option_synchronizer.setShortcut(QKeySequence("Ctrl+A"))

        while not self.isActive:
            self.activate()


        # TODO splashscreen
        # self.splash = QSplashScreen(QPixmap('epssp.dll'))
        # self.splash.show()
        # time.sleep(5) 
        # self.splash.hide()
        #
        # #evaluation end date
        # ntp_server = 'pool.ntp.org'
        #
        # start_date = datetime(2024, 4, 1)
        # end_date = datetime(2024, 5, 1)
        #
        # client = ntplib.NTPClient()
        #
        # try:
        #     response = client.request(ntp_server)
        #     ntp_time = datetime.utcfromtimestamp(response.tx_time)
        #
        #     if start_date <= ntp_time <= end_date:
        #         days_left = (end_date - ntp_time).days
        #         message = f"There are {days_left} days left until the end of the trial period."
        #         win32api.MessageBox(0, message, "Trial Status", 0x40)
        #     else:
        #         message = "Trial ended."
        #         win32api.MessageBox(0, message, "Trial Status", 0x40)
        #         exit()
        #
        # except Exception as e:
        #     message="Unable to connect to licensing server. Please check your Internet connection."
        #     win32api.MessageBox(0, message, "Trial Status", 0x40)
        #     exit()

    def closeAllWindows(self, event=None):
        if self.windows_manager.checkForOpenWindows(self.window) is False:
            if event:
                event.accept()
            else:
                return True
        else:
            # Show warning if sub-windows are open
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Warning)
            msg.setText(self.language_manager.translate('ALERT_CLOSE_ALL_WINDOWS'))
            msg.setWindowTitle(self.language_manager.translate('ALERT'))
            msg.setStandardButtons(QMessageBox.Ok)
            msg.exec_()
            if event:
                event.ignore()
            else:
                return False

    def eventFilter(self, obj, event):
        try:
            # Check if the parent window is focused
            if self.window.isActiveWindow():  # Ensure the parent window is focused
                if event.type() == event.WindowActivate:
                    default_language = self.language_manager.get_current_language()
                    if default_language != self.current_language:
                        self.current_language = default_language
                        self.language_manager.load_translated_ui(self.ui, self.window)
                        self.toolbar_manager.retranslateToolbar()
                    if self.statistics:
                        try:
                            # self.statistics.refresh()
                            self.fetchAlerts()
                        except Exception as e:
                            print(e)
                    return True
            return super().eventFilter(obj, event)
        except Exception as e:
            print(e)
            return False  # Return False if an exception occurs
            
    def setupChatComponent(self):
            # Add stretch to push messages to the top
            self.ui.messagesLayout.addStretch()
                    
            # Create new chat component
            # self.chat_component = ChatComponent(self.ui.messagesLayout, self.ui.message_input, self.ui.messagesScrollArea)
            
            # Chat send message
            self.ui.send_message_btn.clicked.connect(lambda: self.chat_component.send_message(self.ui.message_input.text().strip()))
            self.ui.message_input.returnPressed.connect(lambda: self.chat_component.send_message(self.ui.message_input.text().strip()))

            # Connect signals
            # self.chat_component.message_sent.connect(self.handleUserMessage)
            # self.chatbot.response_ready.connect(self.handleBotResponse)
                
    def handleUserMessage(self, message):
        """Handle new message from the user"""
        # Process the message with the chatbot
        # self.chatbot.process_message(message)
        
    def handleBotResponse(self, response):
        """Handle bot response"""
        # Set the response in the chat component with a random delay between 1-3 seconds
        delay = random.randint(1000, 3000)
        # self.chat_component.set_pending_response(response, delay)

    def openSelectInventoryTypeWindow(self):
        Ui_Configuration_Logic(self.sql_connector).showUi()

    def openMaterialMoveReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_MaterialMoveReport_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openQuantitiesReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_QuantitiesReport_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openWarehouseMoveWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_InventoryReport_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openValueReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Value_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAuthenticateUserWindow(self):
        Ui_AuthenticateUser_Logic(self.sql_connector, self.filemanager).showUi()

    def openAbout(self):
        if self.windows_manager.checkIfWindowIsOpen('AboutWindow'):
            self.windows_manager.raiseWindow('AboutWindow')
        else:
            Ui_About_Logic().showUi()

    def openManufactureWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ManufactureProcessesWindow'):
                self.windows_manager.raiseWindow('ManufactureProcessesWindow')
            else:
                Ui_ManufactureProcesses_Logic(self.sql_connector, self.filemanager, self.windows_manager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'))

    def openCostWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_CostProcesses_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openInvoicesListWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('InvoicesListWindow'):
                self.windows_manager.raiseWindow('InvoicesListWindow')
            else:
                Ui_InvoicesList_Logic(self.sql_connector, self.windows_manager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openCustomersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('CustomersWindow'):
                self.windows_manager.raiseWindow('CustomersWindow')
            else:
                Ui_Clients_Logic(self.sql_connector, client_type='customer').showUi()
        else:
            self.show_no_file_error()

    def openSuppliersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('SuppliersWindow'):
                self.windows_manager.raiseWindow('SuppliersWindow')
            else:
                Ui_Clients_Logic(self.sql_connector, client_type='supplier').showUi()
        else:
            self.show_no_file_error()

    def fetchAlerts(self):
        print("Fetching alerts...")
        if not self.sql_connector or not self.sql_connector.is_connected_to_database:
            return
            
        if not self.database_operations:
            return

        try:
            # Ensure alerts widget has a layout
            if not self.ui.alerts.layout():
                main_layout = QtWidgets.QVBoxLayout()
                main_layout.setContentsMargins(0, 0, 0, 0)
                self.ui.alerts.setLayout(main_layout)

            # Clear existing alerts
            layout = self.ui.alerts.layout()
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget:
                    widget.deleteLater()

            # Create single scroll area for all alerts
            scroll_area = QtWidgets.QScrollArea(self.ui.alerts)
            scroll_area.setWidgetResizable(True)
            scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            scroll_area.setStyleSheet("""
                QScrollArea {
                    background: transparent;
                    border: none;
                }
                QScrollBar:vertical {
                    border: none;
                    background: #F0F0F0;
                    width: 10px;
                    margin: 0px;
                }
                QScrollBar::handle:vertical {
                    background: #CCCCCC;
                    min-height: 20px;
                    border-radius: 5px;
                }
                QScrollBar::add-line:vertical {
                    height: 0px;
                }
                QScrollBar::sub-line:vertical {
                    height: 0px;
                }
            """)
            
            # Create container widget for all alerts
            alerts_container = QtWidgets.QWidget()
            alerts_container.setStyleSheet("background: transparent;")
            alerts_layout = QtWidgets.QVBoxLayout(alerts_container)
            alerts_layout.setSpacing(10)  # Add gap between alerts
            alerts_layout.setContentsMargins(5, 5, 5, 5)
            alerts_container.setLayout(alerts_layout)

            # Get all warehouses
            warehouses = self.database_operations.fetchWarehouses()
            
            alert_count = 0
            
            for warehouse in warehouses:
                warehouse_id = warehouse['id']
                warehouse_name = warehouse['name']
                warehouse_capacity = warehouse['capacity']
                
                if not warehouse_capacity or not str(warehouse_capacity).replace('.','').isdigit():
                    continue
                    
                warehouse_capacity = float(warehouse_capacity)
                
                # Get materials in this warehouse
                materials = self.database_operations.fetchWarehouseMaterials(warehouse_id)
                
                total_quantity = 0
                for material in materials:
                    if material['quantity'] and str(material['quantity']).replace('.','').isdigit():
                        total_quantity += float(material['quantity'])
                
                # Check if total quantity exceeds capacity
                if total_quantity > warehouse_capacity:
                    # Create alert label
                    alert_label = QtWidgets.QLabel()
                    alert_label.setText(f"⚠️ {self.language_manager.translate('ALERT')}: {self.language_manager.translate('WAREHOUSE_EXCEEDED_CAPACITY')}\n{self.language_manager.translate('WAREHOUSE_CAPACITY')}: {warehouse_capacity}\n{self.language_manager.translate('WAREHOUSE_QUANTITY')}: {total_quantity}")
                    alert_label.setStyleSheet("""
                        QLabel {
                            background-color: #FFEB3B;
                            padding: 10px;
                            border-radius: 5px;
                            margin: 5px;
                            font-weight: bold;
                            font-size: 10px;
                            min-height: 80px;
                            max-height: 80px;
                        }
                    """)
                    alert_label.setWordWrap(True)
                    alerts_layout.addWidget(alert_label)
                    alert_count += 1
            
            # Show "no alerts" message if there are no alerts
            if alert_count == 0:
                no_alerts_label = QtWidgets.QLabel()
                no_alerts_label.setText(self.language_manager.translate('NO_ALERTS'))
                no_alerts_label.setAlignment(Qt.AlignCenter)
                no_alerts_label.setStyleSheet("""
                    QLabel {
                        font-size: 12px;
                        font-weight: bold;
                        color: #000000;
                        padding: 20px;
                        padding-top: 100px;
                    }
                """)
                alerts_layout.addWidget(no_alerts_label)
            
            # Add stretch to push alerts to the top
            alerts_layout.addStretch()
            
            # Set the container as the scroll area widget
            scroll_area.setWidget(alerts_container)
            
            # Set a fixed height for the scroll area
            scroll_area.setMinimumHeight(200)  # Adjust this value as needed
            
            # Add scroll area to the main layout
            layout.addWidget(scroll_area)

        except Exception as e:
            print(f"Error fetching alerts: {str(e)}")


    def openPlanWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('SimplePlanWindow'):
                self.windows_manager.raiseWindow('SimplePlanWindow')
            else:
                Ui_SimplePlan_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPlanPercentWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PlanPercentWindow'):
                self.windows_manager.raiseWindow('PlanPercentWindow')
            else:
                Ui_PlanPercent_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAggregator(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('AggregatorWindow'):
                self.windows_manager.raiseWindow('AggregatorWindow')
            else:
                Ui_Aggregator_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAutoAggregator(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('AutoAggregatorWindow'):
                self.windows_manager.raiseWindow('AutoAggregatorWindow')
            else:
                Ui_AutoAggregator_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openExpensesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ExpensesWindow'):
                self.windows_manager.raiseWindow('ExpensesWindow')
            else:
                Ui_Expenses_Logic(self.sql_connector).showUi()
        else:
            self.show_no_file_error()

    # def openExpensesMonthlyWindow(self):
    #     if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
    #         Ui_ExpensesMonthly_Logic(self.sql_connector).showUi()
    #     else:
    #         win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPaymentsWindow(self, payment_type):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PaymentsWindow'):
                self.windows_manager.raiseWindow('PaymentsWindow')
            else:
                Ui_Payments_Logic(self.sql_connector, payment_type).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openClientsInvoicesWindow(self, client_type='customer'):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ClientInvoicesWindow'):
                self.windows_manager.raiseWindow('ClientInvoicesWindow')
            else:
                Ui_ClientInvoices_Logic(self.sql_connector, client_type=client_type).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSalesTargetWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('Sales_TargetWindow'):
                self.windows_manager.raiseWindow('Sales_TargetWindow')
            else:
                Ui_Sales_Target_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def createFile(self, MainWindow):
        global current_user
        file = self.filemanager.createEmptyFile('db')
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

            inventory_type = self.database_operations.fetchSetting('inventory_type')
            if inventory_type is None:
                self.openSelectInventoryTypeWindow()

            user_prefrences = self.database_operations.fetchUserSettings(user_id=current_user)
            prefrences = []
            for prefrence in user_prefrences:
                prefrences.append(prefrence['name'])
            self.toolbar_manager.showActions(prefrences)
            self.window.setEnabled(True)
            self.statistics = Statistics(self.sql_connector, self.ui)
            self.importer = Importer(self.sql_connector, self.filemanager)
            self.fetchAlerts()
            self.ui.stats_groupbox.setEnabled(True)
            # Initialize chatbot with our adapter
            # ai_rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_doc.md")
            # self.chatbot = ChatBotAdapter(service=Services.MYSQL, ai_rules_path=ai_rules_path, mysql_connection=self.sql_connector)

            # Initialize chat component
            self.setupChatComponent()
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

            inventory_type = self.database_operations.fetchSetting('inventory_type')
            if inventory_type is None:
                self.openSelectInventoryTypeWindow()

            self.current_user = current_user
            self.database_operations.setCurrentUser(current_user)

            user_prefrences = self.database_operations.fetchUserSettings(user_id=current_user)
            prefrences = []
            for prefrence in user_prefrences:
                prefrences.append(prefrence['name'])
            self.toolbar_manager.showActions(prefrences)

            self.statistics = Statistics(self.sql_connector, self.ui)
            self.importer = Importer(self.sql_connector, self.filemanager)
            self.fetchAlerts()

            # Initialize chatbot with our adapter
            # ai_rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_doc.md")
            # self.chatbot = ChatBotAdapter(service=Services.MYSQL, ai_rules_path=ai_rules_path, mysql_connection=self.sql_connector)
            self.window.setEnabled(True)
            self.ui.stats_groupbox.setEnabled(True)
            # Initialize chat component
            self.setupChatComponent()

        else:
            print("No File.")


    def showToolBar(self):
        # Initialize toolbar manager with the main window
        self.toolbar_manager = ToolbarManager(self.windows_manager, current_user, self.ui)

        # Map action names to their handler methods
        action_handlers = {
            "new_file": lambda: self.closeAllWindows() and self.createFile(self.window),
            "connect_database": lambda: self.closeAllWindows() and self.openDatabaseSettings(),
            "open_file": lambda: self.closeAllWindows() and self.openFile(self.window),
            "calculator": lambda: self.openCalculatorWindow(),
            "warehouses": lambda: self.openWarehousesWindow(),
            "invoices": lambda: self.openInvoicesListWindow(),
            "units": lambda: self.openUnitsWindow(),
            "customers": lambda: self.openCustomersWindow(),
            "suppliers": lambda: self.openSuppliersWindow(),
            "currencies": lambda: self.openCurrenciesWindow(),
            "ledger": lambda: self.openLedgerWindow(),
            "daily_journal": lambda: self.openDailyJournalWindow(),
            "hr": lambda: self.openHRWindow(),
            "cost_center": lambda: self.openCostCentersWindow(),
            "material_move": lambda: self.openMaterialMoveReportWindow(),
            "manufacture": lambda: self.openManufactureWindow(),
            "materials": lambda: self.openMaterialsWindow(),
            "clients_report": lambda: self.openClientReportWindow(),
            "suppliers_report": lambda: self.openSupplierReportWindow(),
            "journal_entry": lambda: self.openJournalWindow(),
            "raw_materials_needs": lambda: self.openAggregator(),
        }
        
        # Connect each action to its handler
        for action in self.toolbar_manager.actions:
            if action.objectName() in action_handlers:
                action.triggered.connect(action_handlers[action.objectName()])
        
        # Add toolbar to the main window
        self.window.addToolBar(self.toolbar_manager.toolbar)

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

            inventory_type = self.database_operations.fetchSetting('inventory_type')
            if inventory_type is None:
                self.openSelectInventoryTypeWindow()

            user_prefrences = self.database_operations.fetchUserSettings(user_id=current_user)
            prefrences = []
            for prefrence in user_prefrences:
                prefrences.append(prefrence['name'])
            self.toolbar_manager.showActions(prefrences)
            self.statistics = Statistics(self.sql_connector, self.ui)
            self.importer = Importer(self.sql_connector, self.filemanager)
            # Ensure database_operations is initialized before fetching alerts
            self.fetchAlerts()
            self.ui.stats_groupbox.setEnabled(True)

            # Initialize chatbot with our adapter
            # ai_rules_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db_doc.md")
            # self.chatbot = ChatBotAdapter(service=Services.MYSQL, ai_rules_path=ai_rules_path, mysql_connection=self.sql_connector)

            # Initialize chat component
            self.setupChatComponent()

    def openSwitchUserWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            user = Ui_AuthenticateUser_Logic(self.sql_connector).showUi()
            if user:
                current_user = user
            self.current_user = current_user
            self.database_operations.setCurrentUser(current_user)
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'))

    def openUsersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Users_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'))

    def openDatabaseBackup(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database and str(
                type(self.sql_connector)) == "<class 'MysqlConnector.MysqlConnector'>":
            Ui_DatabaseBackupRestore_Logic(self.sql_connector, self.database_name, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_DATABASE'), self.language_manager.translate('ERROR'))

    def openCalculatorWindow(self):
        Ui_Calculator_Logic().showUi()

    def openProductSalesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ProductSalesWindow'):
                self.windows_manager.raiseWindow('ProductSalesWindow')
            else:
                Ui_ProductSales_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSalesReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('SalesReportWindow'):
                self.windows_manager.raiseWindow('SalesReportWindow')
            else:
                Ui_SalesReport_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openClientReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ClientReportWindow'):
                self.windows_manager.raiseWindow('ClientReportWindow')
            else:
                Ui_ClientReport_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSupplierReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('SupplierReportWindow'):
                self.windows_manager.raiseWindow('SupplierReportWindow')
            else:
                Ui_ClientReport_Logic(self.sql_connector, self.filemanager, client_type='supplier').showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSalesTargetReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('Sales_Target_ReportWindow'):
                self.windows_manager.raiseWindow('Sales_Target_ReportWindow')
            else:
                Ui_Sales_Target_Report_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def closeApp(self):
        quit()

    def openExportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Export_Logic(self.sql_connector, self.filemanager).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def importData(self):
        if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
            self.importer.importProductsFromExcel()
            self.fetchProducts()

    def openManufactureCostFixWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('Manufacture_Cost_FixWindow'):
                self.windows_manager.raiseWindow('Manufacture_Cost_FixWindow')
            else:
                Ui_Manufacture_Cost_Fix_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAccountsGuideWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('AccountsWindow'):
                self.windows_manager.raiseWindow('AccountsWindow')
            else:
                Ui_Accounts_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSettingsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Settings_Logic(self.sql_connector).showUi()
            self.refreshToolbar()
            # self.statistics.refresh()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def refreshToolbar(self):
        if self.current_user:
            user_prefrences = self.database_operations.fetchUserSettings(user_id=self.current_user)
            prefrences = []
            for prefrence in user_prefrences:
                prefrences.append(prefrence['name'])
            self.toolbar_manager.showActions(prefrences)

    def activate(self):
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        # Create 'epsilon' directory if it doesn't exist
        if not os.path.exists(epsilon_dir):
            os.makedirs(epsilon_dir)

        activation_file = os.path.join(epsilon_dir, 'activation.dat')

        if os.path.isfile(activation_file) and os.access(activation_file, os.R_OK):
            print("Checking activation...")
            with open(activation_file, 'r') as file:
                code_string = file.read().replace('\n', '')
            try:
                mac = mac_address.getMacAddress()
                mac_numbers = re.sub("[^0-9]", "", str(mac))

                code1_sum = 0
                for c in mac_numbers:
                    code1_sum = code1_sum + int(c)

                date = datetime.now()
                year = date.year

                c0 = int(code_string[0])
                c1 = int(code_string[1])
                c2 = int(code_string[2])
                c3 = int(code_string[3])
                c4 = int(code_string[4])
                c5 = int(code_string[5])
                c6 = int(code_string[6])
                c7 = int(code_string[7])
                c8 = int(code_string[8])
                c9 = int(code_string[9])

                p1 = c0+c1
                p2 = c2+c3
                p3 = c4+c5
                p4 = c6+c7

                code2_sum = str(p1)+str(p2)+str(p3)+str(p4)

                goal = int(code1_sum) + int(code2_sum)
                #print("c1s="+str(code1_sum))
                #print("c2s="+str(code2_sum))

                #TODO
                # if int(goal) == int(year):
                #     print("Product is active.")
                #     self.isActive = True
                # else:
                #     Ui_Activation_Logic().showUi()
                self.isActive = True
                    # window_activation.aboutToQuit.connect(lambda: self.quit())
            except Exception as e:
                #TODO
                # print(e)
                # Ui_Activation_Logic().showUi()
                self.isActive = True

        else:
            Ui_Activation_Logic().showUi()

    def openGroupsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('GroupsWindow'):
                self.windows_manager.raiseWindow('GroupsWindow')
            else:
                Ui_Groups_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openLoansWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('LoansWindow'):
                self.windows_manager.raiseWindow('LoansWindow')
            else:
                Ui_Loans_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openMaterialsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('MaterialsWindow'):
                self.windows_manager.raiseWindow('MaterialsWindow')
            else:
                Ui_Materials_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'))

    def openWarehousesList(self):
        self.ui.menu_warehouses.clear()
        warehouses_action = QAction(self.window)
        warehouses_action.setText(self.language_manager.translate("TOOLBAR_WAREHOUSES"))
        warehouses_action.setShortcut(QKeySequence("Ctrl+F4"))
        warehouses_action.setIcon(QIcon("icons/warehouse.png"))
        self.ui.menu_warehouses.addAction(warehouses_action)
        warehouses_action.triggered.connect(lambda: self.openWarehousesWindow())

        period_start_action = QAction(self.window)
        self.ui.menu_warehouses.addAction(period_start_action)
        period_start_action.setIcon(QIcon("icons/time_cycles.png"))
        period_start_action.setText(self.language_manager.translate("TOOLBAR_PERIOD_START"))
        period_start_action.setShortcut(QKeySequence("Ctrl+F5"))
        period_start_action.triggered.connect(lambda: self.openPeriodStartWindow())
        self.ui.menu_warehouses.addSeparator()
        
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            warehouses = self.database_operations.fetchWarehouses()
            if warehouses:
                # First pass - create parent warehouses
                for warehouse in warehouses:
                    parent_warehouse = warehouse['parent_id']
                    if parent_warehouse is None:
                        warehouse_id = warehouse['id']
                        warehouse_name = '...' + warehouse['name']
                        warehouse_action = QAction(warehouse_name, self.window)
                        self.ui.menu_warehouses.addAction(warehouse_action)
                        
                        # Check for children
                        has_children = False
                        for child in warehouses:
                            if child['parent_id'] == warehouse_id:
                                if not has_children:
                                    # Create submenu for first child
                                    submenu = QMenu(self.window)
                                    warehouse_action.setMenu(submenu)
                                    
                                    # Add parent warehouse action to submenu
                                    parent_action = QAction(warehouse_name, self.window)
                                    submenu.addAction(parent_action)
                                    parent_action.triggered.connect(lambda checked, wid=warehouse_id: self.openWarehouseWindow(wid))
                                    
                                    # Add separator
                                    submenu.addSeparator()
                                    
                                    has_children = True
                                
                                # Add child to submenu
                                child_name = '...' + child['name']
                                child_action = QAction(child_name, self.window)
                                submenu.addAction(child_action)
                                child_action.triggered.connect(lambda checked, wid=child['id']: self.openWarehouseWindow(wid))
                        
                        # If no children, connect parent action directly
                        if not has_children:
                            warehouse_action.triggered.connect(lambda checked, wid=warehouse_id: self.openWarehouseWindow(wid))


    def openFinalAccountsList(self):
        # Store existing actions before the separator
        original_actions = []
        y = self.ui.menu_accounts.actions()
        for action in self.ui.menu_accounts.actions():
            if action.isSeparator():
                break
            original_actions.append(action)

        # Clear the menu
        self.ui.menu_accounts.clear()

        # Restore original actions
        for action in original_actions:
            self.ui.menu_accounts.addAction(action)

        # Add separator after original actions
        self.ui.menu_accounts.addSeparator()
        
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            final_accounts = self.database_operations.fetchAccounts(type='final')
            if final_accounts:
                # Create a set to track account IDs we've already added
                added_accounts = set()
                
                for account in final_accounts:
                    account_id = account['id']
                    
                    # Skip if we've already added this account
                    if account_id in added_accounts:
                        continue
                        
                    account_name = account['name']
                    account_action = QAction(account_name, self.window)
                    self.ui.menu_accounts.addAction(account_action)
                    account_action.triggered.connect(
                        lambda checked, aid=account_id: self.openFinalAccountsWindow(target_account=aid)
                    )
                    
                    # Mark this account as added
                    added_accounts.add(account_id)



    def openFinancialStatementsList(self):
        financial_statements = self.ui.option_financial_statements
        
        # Store existing actions before the separator
        original_actions = []
        x = financial_statements.actions()
        for action in financial_statements.actions():
            if action.isSeparator():
                break
            original_actions.append(action)

        # Clear the menu
        financial_statements.clear()

        # Restore original actions
        for action in original_actions:
            financial_statements.addAction(action)

        # Add separator after original actions
        financial_statements.addSeparator()
        
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            statements = self.database_operations.fetchFinancialStatements()
            if statements:
                # Create a set to track statement IDs we've already added
                added_statements = set()
                
                for statement in statements:
                    statement_id = statement['id']
                    
                    # Skip if we've already added this statement
                    if statement_id in added_statements:
                        continue
                        
                    statement_name = statement['name']
                    statement_action = QAction(statement_name, self.window)
                    financial_statements.addAction(statement_action)
                    statement_action.triggered.connect(
                        lambda checked, sid=statement_id: self.openFinancialStatementsReportWindow(target_statement=sid)
                    )
                    
                    # Mark this statement as added
                    added_statements.add(statement_id)


    def openWarehouseWindow(self, warehouse_id):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:    
            Ui_Warehouses_Logic(self.sql_connector, warehouse_id).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)


    def openReOrderMaterialReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_ReOrderMaterialReport_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openDepartmentReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Department_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPositionReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Position_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openInsuranceReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Insurance_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openEmployeeReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Employee_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSalaryReportWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Salary_Report_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openWarehousesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('WarehousesWindow'):
                self.windows_manager.raiseWindow('WarehousesWindow')
            else:
                Ui_Warehouses_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPeriodStartWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PeriodStartWindow'):
                self.windows_manager.raiseWindow('PeriodStartWindow')
            else:
                Ui_PeriodStart_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPriceManagementWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PricesManagementWindow'):
                self.windows_manager.raiseWindow('PricesManagementWindow')
            else:
                Ui_PricesManagement_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openCurrenciesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('CurrenciesWindow'):
                self.windows_manager.raiseWindow('CurrenciesWindow')
            else:
                Ui_Currencies_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openUnitsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('UnitsWindow'):
                self.windows_manager.raiseWindow('UnitsWindow')
            else:
                Ui_Units_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openCostCentersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('CostCentersWindow'):
                self.windows_manager.raiseWindow('CostCentersWindow')
            else:
                Ui_CostCenters_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openNewInvoiceWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('InvoiceViewWindow'):
                self.windows_manager.raiseWindow('InvoiceViewWindow')
            else:
                Ui_InvoiceView_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openHRWindow(self): 
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('HRWindow'):
                self.windows_manager.raiseWindow('HRWindow')
            else:
                Ui_HR_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openMachinesAndResourcesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('MachinesAndResourcesWindow'):
                self.windows_manager.raiseWindow('MachinesAndResourcesWindow')
            else:
                Ui_MachinesAndResources_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openJournalWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('JournalWindow'):
                self.windows_manager.raiseWindow('JournalWindow')
            else:
                Ui_Journal_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openReceiptVouchersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ReceiptVouchersWindow'):
                self.windows_manager.raiseWindow('ReceiptVouchersWindow')
            else:
                Ui_JournalVoucher_Logic(self.sql_connector, 'receipt').showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openPaymentVouchersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PaymentVouchersWindow'):
                self.windows_manager.raiseWindow('PaymentVouchersWindow')
            else:
                Ui_JournalVoucher_Logic(self.sql_connector, 'payment').showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAccountBalanceWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('AccountBalanceWindow'):
                self.windows_manager.raiseWindow('AccountBalanceWindow')
            else:
                Ui_AccountBalance_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openFinalAccountsWindow(self, target_account=None):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('FinalAccountsReportsWindow'):
                self.windows_manager.raiseWindow('FinalAccountsReportsWindow')
            else:
                Ui_FinalAccountsReports_Logic(self.sql_connector, target_account).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)
            
    def openPeriodOpeningJournalEntriesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('PeriodStartJournalEntriesWindow'):
                self.windows_manager.raiseWindow('PeriodStartJournalEntriesWindow')
            else:
                Ui_Journal_Logic(self.sql_connector, origin_type='period_start').showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)
            
    def openCostCentersReportsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('CostCentersReportWindow'):
                self.windows_manager.raiseWindow('CostCentersReportWindow')
            else:
                Ui_CostCentersReport_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openDailyJournalWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('DailyJournalWindow'):
                self.windows_manager.raiseWindow('DailyJournalWindow')
            else:
                Ui_DailyJournal_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openLedgerWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('LedgerWindow'):
                self.windows_manager.raiseWindow('LedgerWindow')
            else:
                Ui_Ledger_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openTrialBalanceWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('Trial_BalanceWindow'):
                self.windows_manager.raiseWindow('Trial_BalanceWindow')
            else:
                Ui_Trial_Balance_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openAccountMovementsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('Account_MovementsWindow'):
                self.windows_manager.raiseWindow('Account_MovementsWindow')
            else:
                Ui_Account_Movements_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openFinancialStatementsSettingsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('FinancialStatementsWindow'):
                self.windows_manager.raiseWindow('FinancialStatementsWindow')
            else:
                Ui_FinancialStatements_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openFinancialStatementsReportWindow(self, target_statement=None):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('FinancialStatementsReportsWindow'):
                self.windows_manager.raiseWindow('FinancialStatementsReportsWindow')
            else:
                Ui_FinancialStatementsReports_Logic(self.sql_connector, target_statement).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSyncWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Synchronizer_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openReceiptDocsWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('ReceiptDocsWindow'):
                self.windows_manager.raiseWindow('ReceiptDocsWindow')
            else:
                Ui_ReceiptDocs_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def show_no_file_error(self):
        win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def retranslateToolbar(self):
        if hasattr(self, 'toolbar_manager'):
            for action in self.toolbar_manager.actions:
                # Get the original Arabic text and translate it
                original_text = action.text()
                translated_text = QCoreApplication.translate("MainWindow", original_text)
                action.setText(translated_text)
        
    # def fetchSystemLanguage(self):
    #     # Set the language in LanguageManager which will handle saving to file
    #     LanguageManager.set_current_language()


Ui_Mer_Logic = Ui_Mer_Logic()
Ui_Mer_Logic.showUi()

