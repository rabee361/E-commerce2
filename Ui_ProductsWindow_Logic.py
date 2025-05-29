import win32api
import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QFont, QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QHeaderView
from win32con import IDCANCEL, MB_OKCANCEL

import Ui_ProductsWindow
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Composition_Logic import Ui_Composition_Logic
from Ui_ProductEdit_Logic import Ui_ProductEdit_Logic
from Importer import Importer


class Ui_ProductsWindow_Logic(object):
    database_operations = ''
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.filemanager = filemanager
        self.importer = Importer(sqlconnector, filemanager)
        self.ui = Ui_ProductsWindow()

    def showUi(self):
        window_product = QDialog()
        self.ui.setupUi(window_product)
        self.initialize()
        window_product.exec()

    def initialize(self):
        self.ui.products_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Stretch)
        #self.ui.products_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.ui.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.products_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.products_table.verticalHeader().hide()
        self.ui.products_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.quantity_input.setValidator(QIntValidator())
        self.ui.workhours_input.setValidator(QIntValidator())
        self.ui.pills_input.setValidator(QIntValidator())
        self.ui.year_require_input.setValidator(QIntValidator())
        self.ui.ready_input.setValidator(QIntValidator())

        self.ui.save_btn.clicked.connect(lambda: self.addNewProduct())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteProduct())
        self.ui.edit_btn.clicked.connect(lambda: self.openProductEdit())
        self.ui.composition_btn.clicked.connect(lambda: self.openCompositionWindow())
        self.ui.import_btn.clicked.connect(lambda: self.importData())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.fetchProducts()

    def addNewProduct(self):
        name = self.ui.name_input.text()
        name_en = self.ui.name_en_input.text()
        quantity = self.ui.quantity_input.text()
        working_hours = self.ui.workhours_input.text()
        pills = self.ui.pills_input.text()
        year_require = self.ui.year_require_input.text()
        ready = self.ui.ready_input.text()
        code = self.ui.code_input.text()

        if name == '' or name_en == '' or quantity == '':
            win32api.MessageBox(0, "يرجى التأكد من المعلومات", "خطأ")
        else:
            if working_hours == '':
                working_hours = 0
            else:
                if pills == '':
                    pills = 0
                else:
                    self.database_operations.addNewProduct(name, name_en, quantity, working_hours,pills, year_require, ready, code)
                    self.clearTable()
                    self.fetchProducts()

    def deleteProduct(self):
        confirm = win32api.MessageBox(0, "حذف؟", " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.products_table.item(self.ui.products_table.currentRow(), 0)
            print(str(type(table_row)))
            if (str(type(table_row)) == "<class 'NoneType'>"):
                pass
            else:
                product_id = table_row.text()
                self.database_operations.removeProduct(product_id)
                self.clearTable()
                self.fetchProducts()

    def openCompositionWindow(self):
        table_row = self.ui.products_table.item(self.ui.products_table.currentRow(), 0)
        print(str(type(table_row)))
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            product_id = table_row.text()
            window_composition = QDialog()
            Ui_composition_window = Ui_Composition_Logic(self.sqlconnector, product_id)
            Ui_composition_window.setupUi(window_composition)
            window_composition.exec()

    def openProductEdit(self):
        table_row = self.ui.products_table.item(self.ui.products_table.currentRow(), 0)
        print(str(type(table_row)))
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            product_id = table_row.text()
            window_edit = QDialog()
            Ui_edit_window = Ui_ProductEdit_Logic(self.sqlconnector, product_id)
            Ui_edit_window.setupUi(window_edit)
            window_edit.exec()
            self.clearTable()
            self.fetchProducts()

    def clearTable(self):
        self.ui.products_table.clear()
        self.ui.products_table.setRowCount(0)
        font = QFont()
        font.setBold(True)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(8, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(9, item)
        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.products_table.setHorizontalHeaderItem(10, item)

        self.ui.products_table.horizontalHeaderItem(0).setText("المعرف")
        self.ui.products_table.horizontalHeaderItem(1).setText("الرمز")
        self.ui.products_table.horizontalHeaderItem(2).setText("اسم المنتج")
        self.ui.products_table.horizontalHeaderItem(3).setText("اسم المنتج الانجليزي")
        self.ui.products_table.horizontalHeaderItem(4).setText("عدد القطع")
        self.ui.products_table.horizontalHeaderItem(5).setText("ساعات العمل المعيارية")
        self.ui.products_table.horizontalHeaderItem(6).setText("عدد الحبات")
        self.ui.products_table.horizontalHeaderItem(7).setText("المطلوب السنوي")
        self.ui.products_table.horizontalHeaderItem(8).setText("الكمية الجاهزة")
        self.ui.products_table.horizontalHeaderItem(9).setText("الفرق")
        self.ui.products_table.horizontalHeaderItem(10).setText("السعر")

    def fetchProducts(self):
        products = self.database_operations.fetchProducts()
        for product in products:
            id = product[0]
            name = product[1]
            name_en = product[2]
            quantity = product[3]
            working_hours = product[4]
            pills = product[5]
            code = product[6]
            year_require = product[7]
            ready = product[8]
            price = product[9]
            difference = int(year_require)

            # Create a empty row at bottom of table
            numRows = self.ui.products_table.rowCount()
            self.ui.products_table.insertRow(numRows)

            # Add text to the row
            self.ui.products_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.products_table.setItem(numRows, 1, QTableWidgetItem(str(code)))
            self.ui.products_table.setItem(numRows, 2, QTableWidgetItem(str(name)))
            self.ui.products_table.setItem(numRows, 3, QTableWidgetItem(str(name_en)))
            self.ui.products_table.setItem(numRows, 4, QTableWidgetItem(str(quantity)))
            self.ui.products_table.setItem(numRows, 5, QTableWidgetItem(str(working_hours)))
            self.ui.products_table.setItem(numRows, 6, QTableWidgetItem(str(pills)))
            self.ui.products_table.setItem(numRows, 7, QTableWidgetItem(str(year_require)))
            self.ui.products_table.setItem(numRows, 8, QTableWidgetItem(str(ready)))
            self.ui.products_table.setItem(numRows, 9, QTableWidgetItem(str(difference)))
            self.ui.products_table.setItem(numRows, 10, QTableWidgetItem(str(date)))

    def importData(self):
        self.importer.importProductsFromExcel()
        self.clearTable()
        self.fetchProducts()

    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        merge_format_1 = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'yellow'})

        center_format = workbook.add_format({
            'align': 'center'
        })

        products = self.database_operations.fetchProducts()

        worksheet = workbook._add_sheet("Products")
        worksheet.set_column("A:X", '', center_format)
        worksheet.set_column(1, 1, 35)
        worksheet.right_to_left()
        worksheet.set_column("A:R", 15)
        worksheet.write("A1", "رمز المنتج", merge_format_1)
        worksheet.write("B1", "اسم المنتج", merge_format_1)
        worksheet.write("C1", "القطع في الوجبة", merge_format_1)
        worksheet.write("D1", "الحاجة السنوي", merge_format_1)
        worksheet.write("E1", "مستودع الجاهز", merge_format_1)

        i = 2
        for product in products:
            product_code = product[6]
            product_name = product[1]
            product_quantity = product[3]
            year_require = product[7]
            ready = product[8]

            cell_location_code = "A" + str(i)
            cell_location_name = "B" + str(i)
            cell_location_quantity = "C" + str(i)
            cell_location_year_require = "D" + str(i)
            cell_location_ready = "E" + str(i)

            worksheet.write(cell_location_code, product_code)
            worksheet.write(cell_location_name, product_name)
            worksheet.write(cell_location_quantity, product_quantity)
            worksheet.write(cell_location_year_require, year_require)
            worksheet.write(cell_location_ready, ready)
            i = i + 1
        workbook.close()
