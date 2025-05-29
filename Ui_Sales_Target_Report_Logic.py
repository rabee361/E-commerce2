import datetime

import xlsxwriter
from PyQt5 import QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView, QTableWidgetItem

from Colors import light_red_color, light_green_color
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Sales_Target_Report import Ui_Sales_Target_Report
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_Sales_Target_Report_Logic(object):
    def __init__(self, sql_connector, file_manager):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.filemanager = file_manager
        self.ui = Ui_Sales_Target_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        dialog = QDialog()
        dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(dialog)
        dialog.setWindowIcon(QIcon('icons/project.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, dialog)
        dialog.exec()

    def initialize(self):
        self.ui.comparison_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.comparison_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.comparison_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.comparison_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.clients_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.clients_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.clients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.clients_table.verticalHeader().hide()

        self.ui.governorates_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.governorates_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.governorates_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.governorates_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.governorates_table.verticalHeader().hide()

        self.ui.products_combobox.setEnabled(False)
        self.ui.products_btn.clicked.connect(lambda: self.openSelectProductWindow())

        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.fetchProducts()
        self.setYears()

        now = datetime.datetime.now()
        year = now.year
        self.ui.year_combobox.setCurrentText(str(year))

        self.calculate()

    def openSelectProductWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.products_combobox.count()):
                if self.ui.products_combobox.itemData(i)[0] == result['id']:
                    self.ui.products_combobox.setCurrentIndex(i)
                    break

    def calculate(self):
        self.clearAllTables()

        product = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        year = self.ui.year_combobox.itemText(self.ui.year_combobox.currentIndex())
        sold_targets = self.database_operations.fetchSoldVsTargets(product, year)

        ### targets comparison
        for item in sold_targets:
            month = item['month_col']
            sold = item['sold']
            target = item['target']

            if int(sold) < int(target):
                bg = light_red_color
            else:
                bg = light_green_color
            row = int(int(str(month)) - 1)
            self.ui.comparison_table.setItem(row, 0, QTableWidgetItem(str(sold)))
            self.ui.comparison_table.item(row, 0).setBackground(QtGui.QColor(bg))
            self.ui.comparison_table.setItem(row, 1, QTableWidgetItem(str(target)))
            self.ui.comparison_table.item(row, 1).setBackground(QtGui.QColor(bg))

        ### clients sales
        clients_sales_per_month = self.database_operations.fetchClientsProductSalesPerMonth(product, year)
        for item in clients_sales_per_month:
            month = item['month_col']
            sold = item['sold']
            name = item['name']
            location = item['governorate']

            numrow = self.ui.clients_table.rowCount()
            self.ui.clients_table.insertRow(numrow)
            self.ui.clients_table.setItem(numrow, 0, QTableWidgetItem(str(name)))
            self.ui.clients_table.setItem(numrow, 1, QTableWidgetItem(str(location)))
            self.ui.clients_table.setItem(numrow, 2, MyTableWidgetItem(str(sold),int(sold)))
            self.ui.clients_table.setItem(numrow, 3, QTableWidgetItem(str(month)))

        ###governorates sales
        governorates_sales_per_month = self.database_operations.fetchGovernoratesProductSalesPerMonth(product, year)
        for item in governorates_sales_per_month:
            month = item['month_col']
            location = item['location']
            target = item['target']
            sold = item['sold']

            numrow = self.ui.governorates_table.rowCount()
            self.ui.governorates_table.insertRow(numrow)
            self.ui.governorates_table.setItem(numrow, 0, QTableWidgetItem(str(location)))
            self.ui.governorates_table.setItem(numrow, 1, QTableWidgetItem(str(sold)))
            self.ui.governorates_table.setItem(numrow, 2, MyTableWidgetItem(str(target), int(target)))


    def fetchProducts(self):
        products = self.database_operations.fetchGrouppedMaterials()
        for product in products:
            id = product['id']
            name = product['name']
            data = [id]
            self.ui.products_combobox.addItem(name, data)

    def setYears(self):
        for i in range(2000,3000):
            self.ui.year_combobox.addItem(str(i))

    def clearAllTables(self):
        self.ui.clients_table.setRowCount(0)
        self.ui.governorates_table.setRowCount(0)

        for row in range(self.ui.comparison_table.rowCount()):
            self.ui.comparison_table.setItem(row, 0, QTableWidgetItem(""))
            self.ui.comparison_table.setItem(row, 1, QTableWidgetItem(""))

    def exportToExcel(self):
        if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
            file_name = self.filemanager.createEmptyFile('xlsx')
            if file_name != '':
                workbook = xlsxwriter.Workbook(file_name)

                merge_format_1 = workbook.add_format({
                    'bold': True,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'fg_color': 'yellow'})

                merge_format_2 = workbook.add_format({
                    'bold': True,
                    'border': 1,
                    'align': 'center',
                    'valign': 'vcenter',
                    'color': 'white',
                    'fg_color': 'green'})

                center_format = workbook.add_format({
                    'align': 'center'
                })

                product = self.ui.products_combobox.itemText(self.ui.products_combobox.currentIndex())
                year = self.ui.year_combobox.itemText(self.ui.year_combobox.currentIndex())

                worksheet = workbook.add_worksheet("Sales")
                worksheet.set_column("A:X", 15, center_format)  # Set width as integer 15 instead of empty string
                worksheet.set_column(1, 1, 25)
                worksheet.right_to_left()

                worksheet.write("A1", str(product), merge_format_1)
                worksheet.write("A2", str(year), merge_format_1)

                worksheet.write("A4", self.language_manager.translate("SOLD_QUANTITY"), merge_format_2)
                worksheet.write("B4", self.language_manager.translate("TARGET_QUANTITY"), merge_format_2)

                x = 5

                for i in range(0, self.ui.comparison_table.rowCount()):
                    sold_cell = self.ui.comparison_table.item(i, 0)
                    target_cell = self.ui.comparison_table.item(i, 1)
                    try:
                        sold = sold_cell.text()
                        worksheet.write("A"+str(x), sold)

                        target = target_cell.text()
                        worksheet.write("B"+str(x), target)
                        x+=1
                    except:
                        pass

                worksheet.write("A"+str(x), self.language_manager.translate("CLIENT"), merge_format_2)
                worksheet.write("B"+str(x), self.language_manager.translate("GOVERNORATE"), merge_format_2)
                worksheet.write("C"+str(x), self.language_manager.translate("QUANTITY"), merge_format_2)
                worksheet.write("D"+str(x), self.language_manager.translate("MONTH"), merge_format_2)
                x += 1

                for i in range(0, self.ui.clients_table.rowCount()):
                    client_cell = self.ui.clients_table.item(i, 0)
                    governorate_cell = self.ui.clients_table.item(i, 1)
                    quantity_cell = self.ui.clients_table.item(i, 2)
                    month_cell = self.ui.clients_table.item(i, 3)
                    try:
                        client = client_cell.text()
                        governorate = governorate_cell.text()
                        quantity = quantity_cell.text()
                        month = month_cell.text()

                        worksheet.write("A" + str(x), client)
                        worksheet.write("B" + str(x), governorate)
                        worksheet.write("C" + str(x), quantity)
                        worksheet.write("D" + str(x), month)
                        x += 1
                    except:
                        pass

                worksheet.write("A"+str(x), self.language_manager.translate("GOVERNORATE"), merge_format_2)
                worksheet.write("B"+str(x), self.language_manager.translate("QUANTITY"), merge_format_2)
                worksheet.write("C"+str(x), self.language_manager.translate("TARGET"), merge_format_2)
                x += 1

                for i in range(0, self.ui.governorates_table.rowCount()):
                    governorate_cell = self.ui.governorates_table.item(i, 0)
                    quantity_cell = self.ui.governorates_table.item(i, 1)
                    target_cell= self.ui.governorates_table.item(i, 2)
                    try:
                        governorate= governorate_cell.text()
                        quantity= quantity_cell.text()
                        target= target_cell.text()

                        worksheet.write("A" + str(x), governorate)
                        worksheet.write("B" + str(x), quantity)
                        worksheet.write("C" + str(x), target)
                        x += 1
                    except:
                        pass

                workbook.close()
