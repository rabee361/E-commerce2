import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from PyQt5.QtCore import QDate , QTranslator    

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from LanguageManager import LanguageManager

from Colors import blue_sky_color, light_green_color, light_red_color, light_yellow_color, white_color
from Ui_ProductSales import Ui_ProductSales
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTranslator    

class Ui_ProductSales_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_ProductSales()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_product_sales = QDialog()
        window_product_sales.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_product_sales)
        window_product_sales.setWindowIcon(QIcon('icons/money_bag.png'))
        self.language_manager.load_translated_ui(self.ui, window_product_sales)
        self.initialize()
        window_product_sales.exec()

    def initialize(self):
        self.ui.from_date_input.setDisplayFormat("yyyy-MM-dd")
        self.ui.to_date_input.setDate(QDate.currentDate())
        self.ui.to_date_input.setDisplayFormat("yyyy-MM-dd")

        self.ui.sales_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.sales_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.sales_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

        self.ui.products_combobox.setEnabled(False)
        self.ui.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.sales_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.sales_table.verticalHeader().hide()
        self.ui.sales_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.sales_table.setSortingEnabled(True)

        self.fetchProducts()
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())
        self.ui.products_btn.clicked.connect(lambda: self.openSelectProductWindow())

        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.clearSalesTable())
        self.ui.from_date_input.dateChanged.connect(lambda: self.clearSalesTable())
        self.ui.to_date_input.dateChanged.connect(lambda: self.clearSalesTable())

    def openSelectProductWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.products_combobox.count()):
                if self.ui.products_combobox.itemData(i)[0] == result['id']:
                    self.ui.products_combobox.setCurrentIndex(i)
                    break


    def clearSalesTable(self):
        self.ui.sales_table.setRowCount(0)

    def fetchProducts(self):
        products = self.database_operations.fetchGrouppedMaterials()
        for product in products:
            id = product['id']
            name = product['name']
            work_hours = product['work_hours']
            code = product['code']

            data = [id, name, code]
            view_name = name + " (" + code + ")"
            self.ui.products_combobox.addItem(view_name, data)

    def calculate(self):
        self.ui.sales_table.setRowCount(0)

        product_id = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())[0]
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)
        invoice_sell_id = self.database_operations.fetchInvoiceTypes(name='sell')[0]['id']
        sales = self.database_operations.fetchSalesInvoices(product_id, from_date, to_date, invoice_sell_id)
        counter = 0
        for sale in sales:
            id = sale['id']
            number = sale['number']
            type_col = sale['type_col']
            paid = self.language_manager.translate("YES") if sale['paid'] else self.language_manager.translate("NO")
            date_col = sale['date_col']
            quantity = sale['quantity1']
            unit = sale['unit1']
            discount = sale['discount']
            addition = sale['addition']
            price = sale['price']
            currency = sale['currency']
            client_name = sale['client_name']
            final_price = price + addition - discount

            quantity = round(float(quantity),3)

            if number=='':
                number=0

            if discount=='':
                discount=0

            if type=='direct':
                bg = light_green_color
                type_string = self.language_manager.translate("DIRECT_SALES")

            elif type=='gifts':
                bg = light_red_color
                type_string = self.language_manager.translate("GIFTS")

            elif type=='ready':
                bg = blue_sky_color
                type_string = self.language_manager.translate("READY_PRODUCTS")

            elif type=='returns':
                bg = light_yellow_color
                type_string = self.language_manager.translate("RETURNS")

            else:
                bg = white_color
                type_string = self.language_manager.translate("SAMPLES")

            counter += 1
            rows = self.ui.sales_table.rowCount()
            self.ui.sales_table.insertRow(rows)
            self.ui.sales_table.setItem(rows, 0, QTableWidgetItem(str(counter), int(counter)))
            self.ui.sales_table.setItem(rows, 1, QTableWidgetItem(str(number)))
            self.ui.sales_table.setItem(rows, 2, QTableWidgetItem(str(date_col)))
            self.ui.sales_table.setItem(rows, 3, QTableWidgetItem(str(client_name)))
            self.ui.sales_table.setItem(rows, 4, QTableWidgetItem(str(type_col)))
            self.ui.sales_table.setItem(rows, 5, QTableWidgetItem(str(quantity)))
            self.ui.sales_table.setItem(rows, 6, QTableWidgetItem(str(unit)))
            self.ui.sales_table.setItem(rows, 7, QTableWidgetItem(str(price),float(price)))
            self.ui.sales_table.setItem(rows, 8, QTableWidgetItem(str(currency),float(currency)))
            self.ui.sales_table.setItem(rows, 9, QTableWidgetItem(str(discount),float(discount)))
            self.ui.sales_table.setItem(rows, 10, QTableWidgetItem(str(addition),float(addition)))
            self.ui.sales_table.setItem(rows, 11, QTableWidgetItem(str(final_price),float(final_price)))
            self.ui.sales_table.setItem(rows, 12, QTableWidgetItem(str(currency),float(currency)))
            self.ui.sales_table.setItem(rows, 13, QTableWidgetItem(str(paid)))


            self.ui.sales_table.item(rows, 0).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 1).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 2).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 3).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 4).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 5).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 6).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 7).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 8).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 9).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 10).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 11).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 12).setBackground(QtGui.QColor(bg))
            self.ui.sales_table.item(rows, 13).setBackground(QtGui.QColor(bg))

    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        bold_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'})

        yellow_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#000000',
            'color': 'yellow'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'green'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'red'})

        center_format = workbook.add_format({
            'align': 'right'
        })

        worksheet = workbook._add_sheet("Sales")
        worksheet.set_column(0, 23, 15, center_format)  # A:X columns with width 15
        worksheet.set_column(1, 1, 35)  # Column B with width 35
        worksheet.right_to_left()
        
        # Write headers
        worksheet.write("A1", "#", bold_format)
        worksheet.write("B1", self.language_manager.translate("INVOICE_NUMBER"), bold_format)
        worksheet.write("C1", self.language_manager.translate("DATE"), bold_format)
        worksheet.write("D1", self.language_manager.translate("CLIENT"), bold_format)
        worksheet.write("E1", self.language_manager.translate("TYPE"), bold_format)
        worksheet.write("F1", self.language_manager.translate("QUANTITY"), bold_format)
        worksheet.write("G1", self.language_manager.translate("UNIT"), bold_format)
        worksheet.write("H1", self.language_manager.translate("PRICE"), bold_format)
        worksheet.write("I1", self.language_manager.translate("CURRENCY"), bold_format)
        worksheet.write("J1", self.language_manager.translate("DISCOUNT"), bold_format)
        worksheet.write("K1", self.language_manager.translate("ADDITION"), bold_format)
        worksheet.write("L1", self.language_manager.translate("FINAL_PRICE"), bold_format)
        worksheet.write("M1", self.language_manager.translate("CURRENCY"), bold_format)
        worksheet.write("N1", self.language_manager.translate("PAID"), bold_format)

        # Write data
        rowCount = self.ui.sales_table.rowCount()
        for row in range(0, rowCount):
            for col in range(14):
                worksheet.write(row + 1, col, self.ui.sales_table.item(row, col).text())

        workbook.close()
