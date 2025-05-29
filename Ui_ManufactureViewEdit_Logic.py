
from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QHeaderView, QAbstractItemView, QTableWidgetItem

from DatabaseOperations import DatabaseOperations
from Ui_ManufactureViewEdit import Ui_ManufactureViewEdit


class Ui_ManufactureViewEdit_Logic(QDialog):
    def __init__(self, sql_connector, process_id):
        super().__init__()
        self.manufacture_process_id = process_id
        self.sql_connector = sql_connector
        self.database_operations=DatabaseOperations(sql_connector)
        self.exchange_price = 0
        self.ui = Ui_ManufactureViewEdit()

    def showUi(self):
        window_manuViewEdit = QDialog()
        self.ui.setupUi(window_manuViewEdit)
        self.initialize()
        window_manuViewEdit.exec()

    def initialize(self):
        self.ui.raw_pullout_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.manufacture_date_input.setDisplayFormat("dd-MM-yyyy")

        self.ui.composition_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.composition_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.composition_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.composition_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.composition_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.composition_table.verticalHeader().hide()
        self.ui.composition_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.manufacture_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.manufacture_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.manufacture_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.manufacture_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.manufacture_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.ui.manufacture_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.manufacture_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.manufacture_table.verticalHeader().hide()
        self.ui.manufacture_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.radio_no_expenses.clicked.connect(lambda: self.fetchManufactureData())
        self.ui.radio_pills_expenses.clicked.connect(lambda: self.pillsExpenses())
        self.ui.radio_hours_expenses.clicked.connect(lambda: self.hoursExpenses())

        self.fetchManufactureData()

    def fetchManufactureData(self):
        manufacture = self.database_operations.fetchManufactureProcess(self.manufacture_process_id)
        product_id = manufacture[0][1]
        quantity = manufacture[0][2]
        working_hours = manufacture[0][3]
        batch = manufacture[0][4]
        pills = manufacture[0][5]
        raw_pullout_date = manufacture[0][6]
        unit_cost_sp = manufacture[0][7]
        unit_cost_usd = manufacture[0][8]
        total_cost_sp = manufacture[0][9]
        total_cost_usd = manufacture[0][10]
        manufacture_date = manufacture[0][11]
        box_per_batch = manufacture[0][13]
        working_hours_standard = manufacture[0][14]
        pills_standard = manufacture[0][15]
        exchange_price = manufacture[0][12]
        product_name = manufacture[0][18]


        expenses_type = manufacture[0][16]
        material_pricing_method = manufacture[0][17]

        self.setExpenses(expenses_type)
        self.setMaterialPricingMethod(material_pricing_method)

        self.ui.product_input.setText(str(product_name))
        self.ui.box_per_batch_input.setText(str(box_per_batch))
        self.ui.working_hours_standard_input.setText(str(working_hours_standard))
        self.ui.pills_standard_input.setText(str(pills_standard))
        self.ui.box_required_input.setText(str(quantity))
        self.ui.working_hours_input.setText(str(working_hours))
        self.ui.batch_input.setText(str(batch))
        self.ui.pills_input.setText(str(pills))
        self.ui.exchange_input.setText(str(exchange_price))
        self.exchange_price = exchange_price

        manufacture_date_object = datetime.strptime(str(manufacture_date), '%Y-%m-%d')
        self.ui.manufacture_date_input.setDate(manufacture_date_object)
        materials_pullout_date_object = datetime.strptime(str(raw_pullout_date), '%Y-%m-%d')
        self.ui.raw_pullout_date_input.setDate(materials_pullout_date_object)

        self.ui.manufacture_table.setRowCount(0)
        self.ui.composition_table.setRowCount(0)

        numrows = self.ui.manufacture_table.rowCount()
        self.ui.manufacture_table.insertRow(numrows)
        self.ui.manufacture_table.setItem(numrows, 0, QTableWidgetItem(str(product_name)))
        self.ui.manufacture_table.setItem(numrows, 1, QTableWidgetItem(str(quantity)))
        self.ui.manufacture_table.setItem(numrows, 2, QTableWidgetItem(str(unit_cost_sp)))
        self.ui.manufacture_table.setItem(numrows, 3, QTableWidgetItem(str(unit_cost_usd)))
        self.ui.manufacture_table.setItem(numrows, 4, QTableWidgetItem(str(total_cost_sp)))
        self.ui.manufacture_table.setItem(numrows, 5, QTableWidgetItem(str(total_cost_usd)))

        for row in manufacture:
            material_id = row[21]
            material_price_sp = row[22]
            material_price_usd = row[23]
            material_standard_quantity = row[24]
            material_required_quantity = row[25]
            material_unit = row[26]
            material_name = row[29]
            material_name_en = row[30]
            material_code = row[28]

            numrows = self.ui.composition_table.rowCount()
            self.ui.composition_table.insertRow(numrows)

            self.ui.composition_table.setItem(numrows, 0, QTableWidgetItem(str(material_id)))
            self.ui.composition_table.setItem(numrows, 1, QTableWidgetItem(str(material_code)))
            self.ui.composition_table.setItem(numrows, 2, QTableWidgetItem(str(material_name)+" "+str(material_name_en)))
            self.ui.composition_table.setItem(numrows, 3, QTableWidgetItem(str(material_price_sp)))
            self.ui.composition_table.setItem(numrows, 4, QTableWidgetItem(str(material_price_usd)))
            self.ui.composition_table.setItem(numrows, 5, QTableWidgetItem(str(material_standard_quantity)))
            self.ui.composition_table.setItem(numrows, 6, QTableWidgetItem(str(material_required_quantity)))
            self.ui.composition_table.setItem(numrows, 7, QTableWidgetItem(str(material_unit)))

    def setExpenses(self, expenses_type):
        print (expenses_type)
        if "year" in expenses_type:
            self.ui.expenses_type_combobox.setCurrentText("سنوية")
        elif "month" in expenses_type:
            self.ui.expenses_type_combobox.setCurrentText("شهرية")
        else:
            pass

        if "no_expenses" in expenses_type:
            self.ui.radio_no_expenses.setChecked(True)
        elif "pills" in expenses_type:
            self.ui.radio_pills_expenses.setChecked(True)
        elif "hours" in expenses_type:
            self.ui.radio_hours_expenses.setChecked(True)
        else:
            pass

    def setMaterialPricingMethod(self, material_pricing_method):

        if "avg_invoice" in material_pricing_method:
            self.ui.radio_invoice_avg.setChecked(True)
        elif "avg_pullout" in material_pricing_method:
            self.ui.radio_invoice_avg_pullout.setChecked(True)
        elif "last_invoice" in material_pricing_method:
            self.ui.radio_invoice_last.setChecked(True)
        else:
            pass
