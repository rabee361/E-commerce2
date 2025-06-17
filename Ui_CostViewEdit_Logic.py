from datetime import datetime

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QDialog

from DatabaseOperations import DatabaseOperations
from Ui_CostViewEdit import Ui_CostViewEdit
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_CostViewEdit_Logic(object):
    def __init__(self, sql_connector, process_id):
        super().__init__()
        self.manufacture_process_id = process_id
        self.sql_connector = sql_connector
        self.database_operations=DatabaseOperations(sql_connector)
        self.exchange_price = 0
        self.ui = Ui_CostViewEdit()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_costViewEdit = QDialog()
        self.ui.setupUi(window_costViewEdit)
        self.language_manager.load_translated_ui(self.ui, window_costViewEdit)
        self.initialize()
        window_costViewEdit.exec()

    def initialize(self):
        self.ui.cost_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.cost_date_input.setDisplayFormat("dd-MM-yyyy")

        self.ui.composition_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.composition_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.composition_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.composition_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.composition_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.composition_table.verticalHeader().hide()
        self.ui.composition_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.cost_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.cost_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.ui.cost_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.cost_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.cost_table.verticalHeader().hide()
        self.ui.cost_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.radio_no_expenses.clicked.connect(lambda: self.fetchCostData())
        self.ui.radio_pills_expenses.clicked.connect(lambda: self.pillsExpenses())
        self.ui.radio_hours_expenses.clicked.connect(lambda: self.hoursExpenses())

        self.fetchCostData()

    def fetchCostData(self):
        manufacture = self.database_operations.fetchCostProcess(self.manufacture_process_id)
        product_id = manufacture[0][1]
        #working_hours = manufacture[0][3]
        #batch = manufacture[0][4]
        #pills = manufacture[0][5]
        #raw_pullout_date = manufacture[0][6]
        unit_cost_sp = manufacture[0][2]
        unit_cost_usd = manufacture[0][3]
        total_cost_sp = manufacture[0][4]
        total_cost_usd = manufacture[0][5]

        manufacture_date = manufacture[0][6]
        exchange_price = manufacture[0][7]
        box_per_batch = manufacture[0][8]
        working_hours_standard = manufacture[0][9]
        pills_standard = manufacture[0][10]
        expenses_type = manufacture[0][11]
        material_pricing_method = manufacture[0][12]
        product_name = manufacture[0][13]
        product_name_en = manufacture[0][14]

        self.setExpenses(expenses_type)
        self.setMaterialPricingMethod(material_pricing_method)

        self.ui.product_input.setText(str(product_name+"/"+product_name_en))
        self.ui.box_per_batch_input.setText(str(box_per_batch))
        self.ui.working_hours_standard_input.setText(str(working_hours_standard))
        self.ui.pills_standard_input.setText(str(pills_standard))

        self.ui.exchange_input.setText(str(exchange_price))
        self.exchange_price = exchange_price

        cost_date_object = datetime.strptime(str(manufacture_date), '%Y-%m-%d')
        self.ui.cost_date_input.setDate(cost_date_object)

        self.ui.cost_table.setRowCount(0)
        self.ui.composition_table.setRowCount(0)

        numrows = self.ui.cost_table.rowCount()
        self.ui.cost_table.insertRow(numrows)
        self.ui.cost_table.setItem(numrows, 0, QTableWidgetItem(str(product_name)))
        self.ui.cost_table.setItem(numrows, 1, QTableWidgetItem(str(box_per_batch)))
        self.ui.cost_table.setItem(numrows, 2, QTableWidgetItem(str(unit_cost_sp)))
        self.ui.cost_table.setItem(numrows, 3, QTableWidgetItem(str(unit_cost_usd)))
        self.ui.cost_table.setItem(numrows, 4, QTableWidgetItem(str(total_cost_sp)))
        self.ui.cost_table.setItem(numrows, 5, QTableWidgetItem(str(total_cost_usd)))

        for row in manufacture:
            material_id = row[17]
            material_price_sp = row[18]
            material_price_usd = row[19]
            material_standard_quantity = row[20]
            material_unit = row[22]
            material_name = row[23]
            material_name_en = row[24]
            material_code = row[25]

            numrows = self.ui.composition_table.rowCount()
            self.ui.composition_table.insertRow(numrows)

            self.ui.composition_table.setItem(numrows, 0, QTableWidgetItem(str(material_id)))
            self.ui.composition_table.setItem(numrows, 1, QTableWidgetItem(str(material_code)))
            self.ui.composition_table.setItem(numrows, 2, QTableWidgetItem(str(material_name)+" "+str(material_name_en)))
            self.ui.composition_table.setItem(numrows, 3, QTableWidgetItem(str(material_price_sp)))
            self.ui.composition_table.setItem(numrows, 4, QTableWidgetItem(str(material_price_usd)))
            self.ui.composition_table.setItem(numrows, 5, QTableWidgetItem(str(material_standard_quantity)))
            self.ui.composition_table.setItem(numrows, 6, QTableWidgetItem(str(material_unit)))


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
