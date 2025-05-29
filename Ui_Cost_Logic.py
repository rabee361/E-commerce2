import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate
from datetime import datetime
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Cost import Ui_Cost


class Ui_Cost_Logic(object):
    database_operations = ''
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.exchange_price = 0
        self.expenses_type = 'year_no_expenses'
        self.material_pricing_method = 'avg_pullout'
        self.cost_result = []
        self.ui = Ui_Cost()

    def showUi(self):
        window_cost = QDialog()
        self.ui.setupUi(window_cost)
        self.initialize(window_cost)
        window_cost.exec()

    def initialize(self, window):
        self.ui.composition_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        # self.ui.composition_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        # self.ui.composition_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.composition_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.composition_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.composition_table.verticalHeader().hide()
        self.ui.composition_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.cost_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.ui.cost_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.cost_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.cost_table.verticalHeader().hide()
        self.ui.cost_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.cost_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.cost_date_input.setDate(QDate.currentDate())

        self.ui.pills_standard_input.setValidator(QIntValidator())
        self.ui.working_hours_standard_input.setValidator(QDoubleValidator())
        self.ui.pills_standard_input.setValidator(QDoubleValidator())
        self.ui.exchange_input.setValidator(QDoubleValidator())

        self.ui.radio_no_expenses.setEnabled(False)
        self.ui.radio_hours_expenses.setEnabled(False)
        self.ui.radio_pills_expenses.setEnabled(False)

        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.setBoxPerBatch())
        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.getComposition())
        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.setWorkingHours())
        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.setPills())
        self.ui.expenses_type_combobox.currentIndexChanged.connect(lambda: self.setExpensesType())
        self.ui.expenses_type_combobox.currentIndexChanged.connect(lambda: self.calculateExpenses())


        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.setExchangePrice())
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.getComposition())
        # self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.cost())

        self.ui.radio_invoice_avg.clicked.connect(lambda: self.setExchangePrice())
        self.ui.radio_invoice_avg.clicked.connect(lambda: self.getComposition())
        self.ui.radio_invoice_last.clicked.connect(lambda: self.setExchangePrice())
        self.ui.radio_invoice_last.clicked.connect(lambda: self.getComposition())

        self.ui.radio_no_expenses.clicked.connect(lambda: self.calculateCost())
        self.ui.radio_pills_expenses.clicked.connect(lambda: self.pillsExpenses())
        self.ui.radio_hours_expenses.clicked.connect(lambda: self.hoursExpenses())

        self.ui.radio_no_expenses.clicked.connect(lambda: self.setExpensesType())
        self.ui.radio_pills_expenses.clicked.connect(lambda: self.setExpensesType())
        self.ui.radio_hours_expenses.clicked.connect(lambda: self.setExpensesType())

        self.ui.exchange_input.textChanged.connect(lambda: self.setExchangePrice())
        self.ui.exchange_input.textChanged.connect(lambda: self.getComposition())

        self.ui.cost_btn.clicked.connect(lambda: self.calculateCost())
        self.ui.save_btn.clicked.connect(lambda: self.saveResults())
        self.ui.save_btn.clicked.connect(lambda: window.accept())

        self.fetchExchangePrices()
        self.setExchangePrice()
        self.fetchProducts()

        self.ui.radio_invoice_avg.setChecked(True)
        self.ui.radio_no_expenses.setChecked(True)
        self.getComposition()

    def fetchProducts(self):
        products = self.database_operations.fetchProducts()
        for product in products:
            id = product[0]
            name = product[1]
            name_en = product[2]
            box_per_batch = product[3]
            working_hours = product[4]
            pills = product[5]
            data = [id, box_per_batch, working_hours, pills]
            name = name + ' / ' + name_en
            self.ui.products_combobox.addItem(name, data)

    def fetchExchangePrices(self):
        exchange_prices = self.database_operations.fetchExchangePrices()
        for exchange_price in exchange_prices:
            value = exchange_price[1]
            date = exchange_price[3]
            display_string = "1$ = "+str(value)+" SP ("+str(date)+")"
            data = [value, date]
            self.ui.exchange_combobox.addItem(display_string, data)

    def setBoxPerBatch(self):
        data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        box_per_batch = data[1]
        self.ui.box_per_batch_input.setText(str(int(box_per_batch)))

    def setWorkingHours(self):
        data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        working_hours = data[2]
        self.ui.working_hours_standard_input.setText(str(working_hours))

    def setPills(self):
        data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        pills = data[3]
        self.ui.pills_standard_input.setText(str(pills))

    def setExchangePrice(self):
        explicit_exchange_price = self.ui.exchange_input.text()
        if explicit_exchange_price == '':
            exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
            self.exchange_price = exchange_data[0]
        else:
            self.exchange_price = explicit_exchange_price

    def getComposition(self):
        data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        if data is not None: #because index of exchange_combobox changes before products_combobox has elements in it
            product_id = data[0]
            materials = self.database_operations.fetchComposition(product_id)
            self.clearCompositionTable()
            for material in materials:
                material_id = material[1]
                material_code = material[5]
                material_name = material[2]
                quantity = material[3]
                unit = material[4]
                price_sp = 0
                price_usd = 0

                if self.ui.radio_invoice_avg.isChecked():
                    self.material_pricing_method = 'avg_invoice'
                    price_data = self.database_operations.fetchAverageMaterialPrice(material_id, '9999-12-12', self.exchange_price)
                    price_sp = price_data[0]
                    price_usd = price_data[1]

                if self.ui.radio_invoice_last.isChecked():
                    print("MMMMMMMMMMM")
                    print(material_id)
                    self.material_pricing_method = 'last_invoice'
                    self.setExchangePrice()
                    last_invoice_data = self.database_operations.fetchLastInvoiceOfMaterial(material_id , invoice_type='buy')
                    if last_invoice_data != False:
                        currency = str(last_invoice_data[0][6])
                        value = last_invoice_data[0][5]
                        if currency=='USD':
                            price_usd = float(last_invoice_data[0][5])
                            price_sp = float(price_usd) * float(self.exchange_price)
                            price_usd = round(price_usd,8)
                            price_sp = round(price_sp,8)
                        if currency=='SP':
                            price_sp = float(last_invoice_data[0][5])
                            price_usd = float(price_sp) / float(self.exchange_price)
                            price_usd = round(price_usd,8)
                            price_sp = round(price_sp,8)
                    else:
                        price_usd = 0
                        price_sp = 0

                # Create a empty row at bottom of table
                numRows = self.ui.composition_table.rowCount()
                self.ui.composition_table.insertRow(numRows)
                # Add text to the row
                self.ui.composition_table.setItem(numRows, 0, MyTableWidgetItem(str(material_id), material_id))
                self.ui.composition_table.setItem(numRows, 1, QTableWidgetItem(str(material_code)))
                self.ui.composition_table.setItem(numRows, 2, QTableWidgetItem(str(material_name)))
                self.ui.composition_table.setItem(numRows, 3, QTableWidgetItem(str(price_sp)))
                self.ui.composition_table.setItem(numRows, 4, QTableWidgetItem(str(price_usd)))
                self.ui.composition_table.setItem(numRows, 5, QTableWidgetItem(str(quantity)))
                self.ui.composition_table.setItem(numRows, 6, QTableWidgetItem(str(unit)))

    def clearCompositionTable(self):
        self.ui.composition_table.setRowCount(0)

    def calculateCost(self):
        self.clearCostTable()
        cost_date = self.ui.cost_date_input.text()
        box_per_batch = self.ui.pills_standard_input.text()
        if (box_per_batch == ''):
            print ("ERROR: Box per batch="+str(box_per_batch))
        else:
            raw_materials_cost_sp = 0
            raw_materials_cost_usd = 0
            for row in range(self.ui.composition_table.rowCount()):
                material_id = self.ui.composition_table.item(row, 0).text()
                quantity = self.ui.composition_table.item(row, 5).text()

                if self.ui.radio_invoice_avg.isChecked():
                    material_avg_price_data = self.database_operations.fetchAverageMaterialPrice(material_id, '9999-12-12',self.exchange_price)
                    material_avg_price_sp = material_avg_price_data[0]
                    material_avg_price_usd = material_avg_price_data[1]

                if self.ui.radio_invoice_last.isChecked():
                    last_invoice_data = self.database_operations.fetchLastInvoiceOfMaterial(material_id)
                    if last_invoice_data != False:
                        currency = str(last_invoice_data[0][6])
                        if currency == 'USD':
                            material_avg_price_usd = float(last_invoice_data[0][5])
                            material_avg_price_sp = float(material_avg_price_usd) * float(self.exchange_price)
                            material_avg_price_usd = round(material_avg_price_usd, 8)
                            material_avg_price_sp = round(material_avg_price_sp, 8)
                        if currency == 'SP':
                            material_avg_price_sp = float(last_invoice_data[0][5])
                            material_avg_price_usd = float(material_avg_price_sp) / float(self.exchange_price)
                            material_avg_price_usd = round(material_avg_price_usd, 8)
                            material_avg_price_sp = round(material_avg_price_sp, 8)
                    else:
                        material_avg_price_usd = 0
                        material_avg_price_sp = 0

                required_material_avg_price_sp = float(material_avg_price_sp) * float(quantity)
                required_material_avg_price_usd = float(material_avg_price_usd) * float(quantity)
                raw_materials_cost_sp = float(raw_materials_cost_sp) + float(required_material_avg_price_sp)
                raw_materials_cost_usd = float(raw_materials_cost_usd) + float(required_material_avg_price_usd)

            unit_price_sp = float(raw_materials_cost_sp) / float(box_per_batch)
            unit_price_usd = float(raw_materials_cost_usd) / float(box_per_batch)

            raw_materials_cost_sp = round(raw_materials_cost_sp, 8)
            raw_materials_cost_usd = round(raw_materials_cost_usd, 8)
            unit_price_sp = round(unit_price_sp, 8)
            unit_price_usd = round(unit_price_usd, 8)

            self.cost_result.append(str(self.ui.products_combobox.currentText()))
            self.cost_result.append(str(box_per_batch))
            self.cost_result.append(str(unit_price_sp))
            self.cost_result.append(str(unit_price_usd))
            self.cost_result.append(str(raw_materials_cost_sp))
            self.cost_result.append(str(raw_materials_cost_usd))

            numRows = self.ui.cost_table.rowCount()
            self.ui.cost_table.insertRow(numRows)
            self.ui.cost_table.setItem(numRows, 0, QTableWidgetItem(str(self.ui.products_combobox.currentText())))
            self.ui.cost_table.setItem(numRows, 1, QTableWidgetItem(str(box_per_batch)))
            self.ui.cost_table.setItem(numRows, 2, QTableWidgetItem(str(unit_price_sp)))
            self.ui.cost_table.setItem(numRows, 3, QTableWidgetItem(str(unit_price_usd)))
            self.ui.cost_table.setItem(numRows, 4, QTableWidgetItem(str(raw_materials_cost_sp)))
            self.ui.cost_table.setItem(numRows, 5, QTableWidgetItem(str(raw_materials_cost_usd)))

            self.ui.radio_no_expenses.setEnabled(True)
            self.ui.radio_pills_expenses.setEnabled(True)
            self.ui.radio_hours_expenses.setEnabled(True)
            self.ui.expenses_type_combobox.setEnabled(True)
            self.ui.radio_no_expenses.setChecked(True)
            self.setExpensesType()

    def setExpensesType(self):
        time_slot_input = self.ui.expenses_type_combobox.currentText()
        if time_slot_input == 'شهرية':
            time_slot='month'
        elif time_slot_input == 'سنوية':
            time_slot='year'
        else:
            time_slot=''

        if self.ui.radio_no_expenses.isChecked():
            method='no_expenses'
        elif self.ui.radio_pills_expenses.isChecked():
            method='pills'
        elif self.ui.radio_hours_expenses.isChecked():
            method='hours'
        else:
            method=''

        self.expenses_type=time_slot+"_"+method

    def calculateExpenses(self):
        if 'no_expenses' in self.expenses_type:
            self.clearCostTable()
            self.calculateCost()
            self.ui.radio_no_expenses.setChecked(True)
        elif 'pills' in self.expenses_type:
            self.clearCostTable()
            self.calculateCost()
            self.pillsExpenses()
            self.ui.radio_pills_expenses.setChecked(True)
        elif 'hours' in self.expenses_type:
            self.clearCostTable()
            self.calculateCost()
            self.hoursExpenses()
            self.ui.radio_hours_expenses.setChecked(True)

    def pillsExpenses(self):

        cost_date = self.ui.cost_date_input.text()
        cost_date_object = datetime.strptime(cost_date, '%Y-%m-%d')

        year = str(cost_date_object.year)
        month = str(cost_date_object.month)

        pills_in_year = self.database_operations.fetchPillsInYear(year)
        expenses_in_year = self.database_operations.fetchManufactureExpensesInYear(year)

        pills_in_month = self.database_operations.fetchPillsInMonth(year, month)
        expenses_in_month = self.database_operations.fetchManufactureExpensesInMonth(year, month)

        if pills_in_year != 0:
            total_expenses_in_year = float(expenses_in_year)/float(pills_in_year)
        else:
            total_expenses_in_year = 0

        if pills_in_month != 0:
            total_expenses_in_month = float(expenses_in_month)/float(pills_in_month)
        else:
            total_expenses_in_month = 0

        if 'year' in self.expenses_type:
            expenses = total_expenses_in_year
        elif 'month' in self.expenses_type:
            expenses = total_expenses_in_month
        else:
            expenses = 0
            print("Expenses type set error.")

        for row in range(self.ui.cost_table.rowCount()):
            quantity = self.cost_result[1]
            unit_price_sp = self.cost_result[2]
            unit_price_usd = self.cost_result[3]

            # exchange_value_data = self.database_operations.fetchExchangePrice(cost_date)
            # exchange_value = exchange_value_data[0][1]
            # exchange_date = exchange_value_data[0][3]
            exchange_value = self.exchange_price

            unit_price_sp_with_expenses = float(unit_price_sp)+float(expenses)
            unit_price_usd_with_expenses = float(unit_price_sp_with_expenses)/float(exchange_value)
            total_price_sp_with_expenses = float(unit_price_sp_with_expenses)*float(quantity)
            total_price_usd_with_expenses = float(unit_price_usd_with_expenses)*float(quantity)

            unit_price_sp_with_expenses = round(unit_price_sp_with_expenses,8)
            unit_price_usd_with_expenses = round(unit_price_usd_with_expenses,8)
            total_price_sp_with_expenses = round(total_price_sp_with_expenses,8)
            total_price_usd_with_expenses = round(total_price_usd_with_expenses,8)

            self.ui.cost_table.setItem(row, 2, QTableWidgetItem(str(unit_price_sp_with_expenses)))
            self.ui.cost_table.setItem(row, 3, QTableWidgetItem(str(unit_price_usd_with_expenses)))
            self.ui.cost_table.setItem(row, 4, QTableWidgetItem(str(total_price_sp_with_expenses)))
            self.ui.cost_table.setItem(row, 5, QTableWidgetItem(str(total_price_usd_with_expenses)))

    def hoursExpenses(self):
        cost_date = self.ui.cost_date_input.text()
        cost_date_object = datetime.strptime(cost_date, '%Y-%m-%d')
        year = str(cost_date_object.year)
        month = str(cost_date_object.month)

        hours_in_year = self.database_operations.fetchHoursInYear(year)
        expenses_in_year = self.database_operations.fetchManufactureExpensesInYear(year)

        hours_in_month = self.database_operations.fetchHoursInMonth(year, month)
        expenses_in_month = self.database_operations.fetchManufactureExpensesInMonth(year, month)

        if hours_in_year != 0:
            total_expenses_in_year = float(expenses_in_year)/float(hours_in_year)
        else:
            total_expenses_in_year = 0

        if hours_in_month != 0:
            total_expenses_in_month = float(expenses_in_month)/float(hours_in_month)
        else:
            total_expenses_in_month = 0


        if 'year' in self.expenses_type:
            expenses = total_expenses_in_year
        elif 'month' in self.expenses_type:
            expenses = total_expenses_in_month
        else:
            expenses = 0
            print("Expenses type set error.")

        for row in range(self.ui.cost_table.rowCount()):
            quantity = self.cost_result[1]
            unit_price_sp = self.cost_result[2]
            unit_price_usd = self.cost_result[3]

            # exchange_value_data = self.database_operations.fetchExchangePrice(cost_date)
            # exchange_value = exchange_value_data[0][1]
            # exchange_date = exchange_value_data[0][3]
            exchange_value = self.exchange_price

            unit_price_sp_with_expenses = float(unit_price_sp)+float(expenses)
            unit_price_usd_with_expenses = float(unit_price_sp_with_expenses)/float(exchange_value)
            total_price_sp_with_expenses = float(unit_price_sp_with_expenses)*float(quantity)
            total_price_usd_with_expenses = float(unit_price_usd_with_expenses)*float(quantity)

            unit_price_sp_with_expenses = round(unit_price_sp_with_expenses,8)
            unit_price_usd_with_expenses = round(unit_price_usd_with_expenses,8)
            total_price_sp_with_expenses = round(total_price_sp_with_expenses,8)
            total_price_usd_with_expenses = round(total_price_usd_with_expenses,8)

            self.ui.cost_table.setItem(row, 2, QTableWidgetItem(str(unit_price_sp_with_expenses)))
            self.ui.cost_table.setItem(row, 3, QTableWidgetItem(str(unit_price_usd_with_expenses)))
            self.ui.cost_table.setItem(row, 4, QTableWidgetItem(str(total_price_sp_with_expenses)))
            self.ui.cost_table.setItem(row, 5, QTableWidgetItem(str(total_price_usd_with_expenses)))

    def clearCostTable(self):
        self.ui.cost_table.setRowCount(0)

    def saveResults(self):
        quantity = self.ui.pills_standard_input.text()
        cost_result_table_row = self.ui.cost_table.rowCount()
        if (quantity == '' or cost_result_table_row <= 0):
            win32api.MessageBox(0, "لم يتم تحديد الكمية المراد تصنيعها", "خطأ")
        else:
            working_hours = self.ui.working_hours_standard_input.text()

            pills = self.ui.pills_standard_input.text()


            cost_date = self.ui.cost_date_input.text()
            product_data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
            product_id = product_data[0]

            unit_cost_sp = self.ui.cost_table.item(0,2).text()
            unit_cost_usd = self.ui.cost_table.item(0,3).text()
            total_cost_sp = self.ui.cost_table.item(0,4).text()
            total_cost_usd = self.ui.cost_table.item(0,5).text()

            process_id = self.database_operations.saveCostProcessData(product_id, quantity, working_hours, pills, cost_date, self.exchange_price, unit_cost_sp, unit_cost_usd, total_cost_sp, total_cost_usd, self.expenses_type, self.material_pricing_method)

            for row in range(self.ui.composition_table.rowCount()):
                material_id = self.ui.composition_table.item(row,0).text()
                price_sp = self.ui.composition_table.item(row, 3).text()
                price_usd = self.ui.composition_table.item(row, 4).text()
                standard_quantity = self.ui.composition_table.item(row, 5).text()
                unit = self.ui.composition_table.item(row, 6).text()

                self.database_operations.saveCostProcessMaterial(process_id, material_id, price_sp, price_usd, standard_quantity, unit)

