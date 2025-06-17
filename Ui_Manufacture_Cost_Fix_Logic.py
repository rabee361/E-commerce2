
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt
from DatabaseOperations import DatabaseOperations
from Ui_Manufacture_Cost_Fix import Ui_Manufacture_Cost_Fix
from PyQt5.QtGui import QIcon
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Manufacture_Cost_Fix_Logic(object):
    def __init__(self, sql_connector):
        super().__init__()
        self.ui = Ui_Manufacture_Cost_Fix()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize()
        window.setWindowIcon(QIcon('icons/equipment.png'))
        window.exec()

    def initialize(self):
        self.ui.fix_manufacture_btn.clicked.connect(lambda: self.fixManufactureProcesses())
        # self.ui.fix_cost_btn.clicked.connect(lambda: self.fixCostProcesses())
    
        self.id = ''
        self.material_id = ''
        self.quantity1 = ''
        self.quantity2 = ''
        self.quantity3 = ''
        self.working_hours = ''
        self.batch = ''
        self.pullout_date = ''
        self.date = ''
        self.referential_working_hours = ''
        self.expenses_type = ''
        self.material_pricing_method = ''
        self.material_name = ''
        self.current_date = datetime.now().strftime('%Y-%m-%d')

        # Get available currencies
        self.currencies = self.database_operations.fetchCurrencies()

        self.ui.fix_composition_checkBox.clicked.connect(lambda: self.enableExchangeCheckBox())

    def enableExchangeCheckBox(self):
        if self.ui.fix_composition_checkBox.isChecked():
            self.ui.fix_exchange_price_checkbox.setChecked(False)
            self.ui.fix_exchange_price_checkbox.setEnabled(True)
        else:
            self.ui.fix_exchange_price_checkbox.setChecked(False)
            self.ui.fix_exchange_price_checkbox.setEnabled(False)

    def fixManufactureProcesses(self):
        # Get total processes count
        processes_count = self.database_operations.fetchAllManufactureProcessesCount()
        progress = 1

        # Get manufacture processes
        manufactures = self.database_operations.fetchAllManufactureProcessesInfo()

        # For each manufacture process
        for manufacture in manufactures:
            self.ui.progress_label.setText(f"{progress}/{processes_count}")
            progress += 1

            # Get manufacture info
            self.id = manufacture['id']
            self.material_id = manufacture['material_id']
            self.quantity1 = manufacture['quantity']
            self.batch = manufacture['batch']
            self.working_hours = manufacture['working_hours']
            self.pullout_date = manufacture['pullout_date']
            self.date_col = manufacture['date_col']
            self.referential_working_hours = manufacture['referential_working_hours']
            self.expenses_type = manufacture['expenses_type']
            self.material_pricing_method = manufacture['material_pricing_method']

            # Fix composition if checked
            if self.ui.fix_composition_checkBox.isChecked():
                raw_materials_costs = {}
                # Initialize costs for each currency
                currencies = self.database_operations.fetchCurrencies()
                for currency in currencies:
                    raw_materials_costs[currency['id']] = 0

                # Fetch composition
                materials = self.database_operations.fetchComposition(self.material_id)
                
                for material in materials:
                    composition_item_id = material['composition_material_id']
                    material_composition_quantity = material['quantity']
                    unit = material['unit']
                    unit_cost = material['unit_cost']
                    pulled_quantity = material['pulled_quantity']
                    shortage = material['shortage']
                    row_type = material['row_type']
                    # currency = material['currency']
                    prices = {}

                    # Get old material data to calculate required quantity
                    old_mat_data = self.database_operations.fetchManufactureProcessMaterial(self.id, composition_item_id)
                    material_required_quantity = old_mat_data[0]['required_quantity']
                    
                    # Calculate required quantity based on composition ratio
                    fraction = float(material_required_quantity) / float(material_composition_quantity)
                    new_quantity_required = float(material_composition_quantity) * float(fraction)
                    new_quantity_required = round(new_quantity_required, 3)

                    # Calculate prices based on pricing method
                    if str(self.material_pricing_method) == 'avg_invoice':
                        prices = self.database_operations.fetchAverageMaterialPrice(composition_item_id, '9999-12-12', self.current_date)
                    
                    elif str(self.material_pricing_method) == 'avg_pullout':
                        prices = self.database_operations.fetchAverageMaterialPrice(
                            composition_item_id,
                            self.pullout_date,
                            self.current_date
                        )

                    elif str(self.material_pricing_method) == 'last_invoice':
                        last_invoice_data = self.database_operations.fetchLastInvoiceOfMaterial(composition_item_id)
                        if last_invoice_data:
                            invoice_currency = last_invoice_data[0]['currency']
                            invoice_price = float(last_invoice_data[0]['price'])
                            
                            # Convert invoice price to all currencies using current exchange rates
                            for currency in currencies:
                                if currency['id'] == invoice_currency:
                                    prices[currency['id']] = invoice_price
                                else:
                                    exchange_rate = self.database_operations.fetchExchangeValue(
                                        self.date_col, 
                                        invoice_currency,
                                        currency['id']
                                    )
                                    prices[currency['id']] = round(invoice_price * exchange_rate, 3)

                    # Update manufacture process materials
                    self.database_operations.removeManufactureProcessMaterial(old_mat_data[0]['id'])
                    self.database_operations.saveManufactureProcessMaterial(self.id, composition_item_id, material_composition_quantity, new_quantity_required, unit, unit_cost, pulled_quantity, shortage, row_type)

                    # # Calculate costs in each currency
                    # for currency in currencies:
                    #     currency_code = currency['id']
                    #     material_cost = float(prices[currency_code]) * float(new_quantity_required)
                    #     raw_materials_costs[currency_code] += material_cost

                # Calculate unit prices and total costs for each currency
                unit_prices = {}
                total_costs = {}
                for currency in currencies:
                    currency_code = currency['id']
                    unit_prices[currency_code] = round(raw_materials_costs[currency_code] / float(self.quantity1), 4)
                    total_costs[currency_code] = round(raw_materials_costs[currency_code], 4)

                costs = {
                    'unit': unit_prices,
                    'total': total_costs
                }

                self.database_operations.updateManufactureProcessData(self.id, self.working_hours, self.pullout_date, self.quantity1, self.date_col, self.referential_working_hours, self.expenses_type, self.material_pricing_method)



    # def fixCostProcesses(self):
        #get total processes count
        # processes_count = self.database_operations.fetchAllCostProcessesCount()
        # progress = 1

        # #get manufacture processes
        # costs = self.database_operations.fetchAllCostProcesses()

        # #for each manufacture process
        # for cost in costs:
        #     self.ui.progress_label.setText(str(progress)+"/"+str(processes_count))
        #     progress+=1

        #     self.cost_id = cost[0]
        #     self.cost_pid = cost[1]
        #     self.cost_unit_cost_sp = cost[2]
        #     self.cost_unit_cost_usd = cost[3]
        #     self.cost_total_cost_sp = cost[4]
        #     self.cost_total_cost_usd = cost[5]
        #     self.cost_date = cost[6]
        #     self.cost_exchange_price = cost[7]
        #     self.cost_box_per_batch = cost[8]
        #     self.cost_referential_working_hours = cost[9]
        #     self.cost_pills_standard = cost[10]
        #     self.cost_expenses_type = cost[11]
        #     self.cost_material_pricing_method = cost[12]
        #     self.cost_name = cost[13]
        #     self.cost_name_en = cost[14]

        #     #fix exchange price
        #     if self.ui.fix_exchange_price_checkbox.isChecked():
        #         new_exchange_price = self.database_operations.fetchExchangePrice(self.cost_date)[0][1]
        #         self.cost_exchange_price = new_exchange_price

        #     #fix composition if checked
        #     if self.ui.fix_composition_checkBox.isChecked():

        #         #fetch composition
        #         materials = self.database_operations.fetchComposition(self.cost_pid)
        #         raw_materials_cost_sp = 0
        #         raw_materials_cost_usd = 0

        #         for material in materials:
        #             material_id = material[1]
        #             material_composition_quantity = material[3]
        #             unit = material[4]
        #             price_sp = 0
        #             price_usd = 0

        #             old_mat_data = self.database_operations.fetchCostProcessMaterial(self.cost_id, material_id)
        #             old_mat_id = old_mat_data[0][0]


        #             #calculate price
        #             if str(self.cost_material_pricing_method) == 'avg_invoice':
        #                 price_data = self.database_operations.fetchAverageMaterialPrice(material_id, '9999-12-12', self.cost_exchange_price)
        #                 price_sp = price_data[0]
        #                 price_usd = price_data[1]


        #             if str(self.cost_material_pricing_method) == 'last_invoice':
        #                 last_invoice_data = self.database_operations.fetchLastInvoiceOfMaterial(material_id)
        #                 if last_invoice_data != False:
        #                     currency = str(last_invoice_data[0][6])
        #                     if currency == 'USD':
        #                         price_usd = float(last_invoice_data[0][5])
        #                         price_sp = float(price_usd) * float(self.cost_exchange_price)
        #                         price_usd = round(price_usd, 3)
        #                         price_sp = round(price_sp, 3)
        #                     if currency == 'SP':
        #                         price_sp = float(last_invoice_data[0][5])
        #                         price_usd = float(price_sp) / float(self.cost_exchange_price)
        #                         price_usd = round(price_usd, 3)
        #                         price_sp = round(price_sp, 3)
        #                 else:
        #                     print("NO PRICING METHOD FOUND")
        #                     price_usd = 0
        #                     price_sp = 0

        #             # clear materials of manufacture process
        #             self.database_operations.removeCostProcessMaterial(old_mat_id)
        #             self.database_operations.saveCostProcessMaterial(self.cost_id, material_id, price_sp, price_usd, material_composition_quantity, unit)

        #             required_material_avg_price_sp = float(price_sp) * float(self.cost_box_per_batch)
        #             required_material_avg_price_usd = float(price_usd) * float(self.cost_box_per_batch)
        #             raw_materials_cost_sp = float(raw_materials_cost_sp) + float(required_material_avg_price_sp)
        #             raw_materials_cost_usd = float(raw_materials_cost_usd) + float(required_material_avg_price_usd)

        #         unit_price_sp = float(raw_materials_cost_sp) / float(self.cost_box_per_batch)
        #         unit_price_usd = float(raw_materials_cost_usd) / float(self.cost_box_per_batch)

        #         raw_materials_cost_sp = round(raw_materials_cost_sp, 8)
        #         raw_materials_cost_usd = round(raw_materials_cost_usd, 8)
        #         unit_price_sp = round(unit_price_sp, 8)
        #         unit_price_usd = round(unit_price_usd, 8)

        #         self.unit_cost_sp = unit_price_sp
        #         self.unit_cost_usd = unit_price_usd
        #         self.total_cost_sp = raw_materials_cost_sp
        #         self.total_cost_usd = raw_materials_cost_usd

        #     #fix expenses
        #     if self.ui.fix_month_expenses.isChecked() and 'month' in self.cost_expenses_type:
        #         cost_process_materials = self.database_operations.fetchCostProcess(self.cost_id)
        #         raw_materials_cost_sp_with_no_expenses = 0
        #         raw_materials_cost_usd_with_no_expenses = 0
        #         boxes_required = 0
        #         for cost_process_material in cost_process_materials:
        #             price_sp_with_no_expenses = cost_process_material[18]
        #             price_usd_with_no_expenses = cost_process_material[19]
        #             required_quantity_of_material = cost_process_material[20]
        #             boxes_required = cost_process_material[8]
        #             required_material_avg_price_sp_with_no_expenses = float(price_sp_with_no_expenses)*float(required_quantity_of_material)
        #             required_material_avg_price_usd_with_no_expenses = float(price_usd_with_no_expenses)*float(required_quantity_of_material)
        #             raw_materials_cost_sp_with_no_expenses +=  required_material_avg_price_sp_with_no_expenses
        #             raw_materials_cost_usd_with_no_expenses += required_material_avg_price_usd_with_no_expenses

        #         unit_price_sp_with_no_expenses = raw_materials_cost_sp_with_no_expenses/float(boxes_required)
        #         unit_price_usd_with_no_expenses= raw_materials_cost_usd_with_no_expenses/float(boxes_required)

        #         if 'no_expenses' in self.cost_expenses_type:
        #             pass
        #         elif 'pills' in self.cost_expenses_type:
        #             cost_date = self.cost_date
        #             cost_date_object = datetime.strptime(str(cost_date), '%Y-%m-%d')

        #             year = str(cost_date_object.year)
        #             month = str(cost_date_object.month)

        #             pills_in_month = self.database_operations.fetchPillsInMonth(year, month)
        #             expenses_in_month = self.database_operations.fetchManufactureExpensesInMonth(year, month)

        #             if pills_in_month != 0:
        #                 total_expenses_in_month = float(expenses_in_month) / float(pills_in_month)
        #             else:
        #                 total_expenses_in_month = 0

        #             if total_expenses_in_month == 0:
        #                 expenses = 0
        #             else:
        #                 expenses = 0
        #                 print("Expenses type set error.")


        #             unit_price_sp_with_expenses = float(unit_price_sp_with_no_expenses) + float(expenses)
        #             unit_price_usd_with_expenses = float(unit_price_sp_with_expenses) / float(self.cost_exchange_price)
        #             total_price_sp_with_expenses = float(unit_price_sp_with_expenses) * float(boxes_required)
        #             total_price_usd_with_expenses = float(unit_price_usd_with_expenses) * float(boxes_required)

        #             unit_cost_sp = round(unit_price_sp_with_expenses, 5)
        #             unit_cost_usd = round(unit_price_usd_with_expenses, 5)
        #             total_cost_sp = round(total_price_sp_with_expenses, 5)
        #             total_cost_usd = round(total_price_usd_with_expenses, 5)

        #             self.cost_unit_cost_sp = unit_cost_sp
        #             self.cost_unit_cost_usd = unit_cost_usd
        #             self.cost_total_cost_sp = total_cost_sp
        #             self.cost_total_cost_usd = total_cost_usd
        #         elif 'hours' in self.cost_expenses_type:
        #             cost_date = self.cost_date
        #             cost_date_object = datetime.strptime(str(cost_date), '%Y-%m-%d')

        #             year = str(cost_date_object.year)
        #             month = str(cost_date_object.month)

        #             hours_in_month = self.database_operations.fetchHoursInMonth(year, month)
        #             expenses_in_month = self.database_operations.fetchManufactureExpensesInMonth(year, month)


        #             if hours_in_month != 0:
        #                 total_expenses_in_month = float(expenses_in_month) / float(hours_in_month)
        #             else:
        #                 total_expenses_in_month = 0

        #             if total_expenses_in_month == 0:
        #                 expenses = 0
        #             else:
        #                 expenses = 0
        #                 print("Expenses type set error.")


        #             unit_price_sp_with_expenses = float(unit_price_sp_with_no_expenses) + float(expenses)
        #             unit_price_usd_with_expenses = float(unit_price_sp_with_expenses) / float(self.cost_exchange_price)
        #             total_price_sp_with_expenses = float(unit_price_sp_with_expenses) * float(boxes_required)
        #             total_price_usd_with_expenses = float(unit_price_usd_with_expenses) * float(boxes_required)

        #             unit_cost_sp = round(unit_price_sp_with_expenses, 5)
        #             unit_cost_usd = round(unit_price_usd_with_expenses, 5)
        #             total_cost_sp = round(total_price_sp_with_expenses, 5)
        #             total_cost_usd = round(total_price_usd_with_expenses, 5)

        #             self.cost_unit_cost_sp = unit_cost_sp
        #             self.cost_unit_cost_usd = unit_cost_usd
        #             self.cost_total_cost_sp = total_cost_sp
        #             self.cost_total_cost_usd = total_cost_usd
        #         else:
        #             pass

        #     elif self.ui.fix_year_expenses.isChecked() and 'year' in self.cost_expenses_type:
        #         cost_process_materials = self.database_operations.fetchCostProcess(self.cost_id)
        #         raw_materials_cost_sp_with_no_expenses = 0
        #         raw_materials_cost_usd_with_no_expenses = 0
        #         boxes_required = 0
        #         for cost_process_material in cost_process_materials:
        #             price_sp_with_no_expenses = cost_process_material[18]
        #             price_usd_with_no_expenses = cost_process_material[19]
        #             required_quantity_of_material = cost_process_material[20]
        #             boxes_required = cost_process_material[2]
        #             required_material_avg_price_sp_with_no_expenses = float(price_sp_with_no_expenses)*float(required_quantity_of_material)
        #             required_material_avg_price_usd_with_no_expenses = float(price_usd_with_no_expenses)*float(required_quantity_of_material)
        #             raw_materials_cost_sp_with_no_expenses +=  required_material_avg_price_sp_with_no_expenses
        #             raw_materials_cost_usd_with_no_expenses += required_material_avg_price_usd_with_no_expenses

        #         unit_price_sp_with_no_expenses = raw_materials_cost_sp_with_no_expenses/float(boxes_required)
        #         unit_price_usd_with_no_expenses= raw_materials_cost_usd_with_no_expenses/float(boxes_required)

        #         if 'no_expenses' in self.cost_expenses_type:
        #             pass
        #         elif 'pills' in self.cost_expenses_type:
        #             cost_date = self.cost_date
        #             cost_date_object = datetime.strptime(str(cost_date), '%Y-%m-%d')

        #             year = str(cost_date_object.year)

        #             pills_in_year = self.database_operations.fetchPillsInYear(year)
        #             expenses_in_year = self.database_operations.fetchManufactureExpensesInYear(year)

        #             if pills_in_year != 0:
        #                 total_expenses_in_year = float(expenses_in_year) / float(pills_in_year)
        #             else:
        #                 total_expenses_in_year = 0

        #             if total_expenses_in_year == 0:
        #                 expenses = 0
        #             else:
        #                 expenses = 0
        #                 print("Expenses type set error.")

        #             unit_price_sp_with_expenses = float(unit_price_sp_with_no_expenses) + float(expenses)
        #             unit_price_usd_with_expenses = float(unit_price_sp_with_expenses) / float(self.cost_exchange_price)
        #             total_price_sp_with_expenses = float(unit_price_sp_with_expenses) * float(boxes_required)
        #             total_price_usd_with_expenses = float(unit_price_usd_with_expenses) * float(boxes_required)

        #             unit_cost_sp = round(unit_price_sp_with_expenses, 5)
        #             unit_cost_usd = round(unit_price_usd_with_expenses, 5)
        #             total_cost_sp = round(total_price_sp_with_expenses, 5)
        #             total_cost_usd = round(total_price_usd_with_expenses, 5)

        #             self.cost_unit_cost_sp = unit_cost_sp
        #             self.cost_unit_cost_usd = unit_cost_usd
        #             self.cost_total_cost_sp = total_cost_sp
        #             self.cost_total_cost_usd = total_cost_usd

        #         elif 'hours' in self.expenses_type:
        #             cost_date = self.cost_date
        #             cost_date_object = datetime.strptime(cost_date, '%Y-%m-%d')

        #             year = str(cost_date_object.year)
        #             month = str(cost_date_object.month)

        #             hours_in_year = self.database_operations.fetchHoursInYear(year)
        #             expenses_in_year = self.database_operations.fetchManufactureExpensesInYear(year)

        #             if hours_in_year != 0:
        #                 total_expenses_in_year = float(expenses_in_year) / float(hours_in_year)
        #             else:
        #                 total_expenses_in_year = 0

        #             if total_expenses_in_year == 0:
        #                 expenses = 0
        #             else:
        #                 expenses = 0
        #                 print("Expenses type set error.")


        #             unit_price_sp_with_expenses = float(unit_price_sp_with_no_expenses) + float(expenses)
        #             unit_price_usd_with_expenses = float(unit_price_sp_with_expenses) / float(self.cost_exchange_price)
        #             total_price_sp_with_expenses = float(unit_price_sp_with_expenses) * float(boxes_required)
        #             total_price_usd_with_expenses = float(unit_price_usd_with_expenses) * float(boxes_required)

        #             unit_cost_sp = round(unit_price_sp_with_expenses, 5)
        #             unit_cost_usd = round(unit_price_usd_with_expenses, 5)
        #             total_cost_sp = round(total_price_sp_with_expenses, 5)
        #             total_cost_usd = round(total_price_usd_with_expenses, 5)

        #             self.cost_unit_cost_sp = unit_cost_sp
        #             self.cost_unit_cost_usd = unit_cost_usd
        #             self.cost_total_cost_sp = total_cost_sp
        #             self.cost_total_cost_usd = total_cost_usd
        #         else:
        #             pass

        #     else:
        #         pass

        #     self.database_operations.updateCostProcessData(self.cost_id, self.cost_pid, self.cost_box_per_batch, self.cost_referential_working_hours, self.cost_pills_standard, self.cost_date, self.cost_exchange_price, self.cost_unit_cost_sp,self.cost_unit_cost_usd, self.cost_total_cost_sp, self.cost_total_cost_usd, self.cost_expenses_type, self.cost_material_pricing_method)
