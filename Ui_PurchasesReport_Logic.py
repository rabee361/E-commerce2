import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt , QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_PurchasesReport import Ui_PurchasesReport
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color ,black
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon


class Ui_PurchasesReportSalesReport_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_PurchasesReport()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/motion_path.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        self.ui.from_date_input.setDate(QDate.currentDate())
        self.ui.to_date_input.setDate(QDate.currentDate())
        self.ui.buy_manufacture_date.setDate(QDate.currentDate())
        self.fetchMaterials()
        self.fetchSuppliers()
        self.fetchCurrencies()
        self.fetchMaterials()
        self.ui.select_supplier_btn.clicked.connect(lambda: self.openSelectSupplierWindow())
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())

    def fetchMaterials(self):
        materials = self.database_operations.fetchGrouppedMaterials()
        self.ui.materials_combobox.clear()
        if materials:
            for material in materials:
                id = material['id']
                name = material['name']
                self.ui.materials_combobox.addItem(name, id)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        self.ui.currency_combobox.clear()
        if currencies:
            for currency in currencies:
                id = currency['id']
                name = currency['name']
                self.ui.currency_combobox.addItem(name, id)

    def fetchSuppliers(self):
        suppliers = self.database_operations.fetchSuppliers(client_type='supplier')
        if suppliers:
            for supplier in suppliers:
                id = supplier['id']
                name = supplier['name']
                self.ui.suppliers_combobox.addItem(name, id)

    def openSelectSupplierWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'suppliers', client_type='supplier')
        result = data_picker.showUi()
        if result:
            for i in range(self.ui.suppliers_combobox.count()):
                if self.ui.suppliers_combobox.itemData(i) == result['id']:
                    self.ui.suppliers_combobox.setCurrentIndex(i)
                    break

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'groupped_materials')
        result = data_picker.showUi()
        if result:
            for i in range(self.ui.materials_combobox.count()):
                x = self.ui.materials_combobox.itemData(i)
                if self.ui.materials_combobox.itemData(i) == result['id']:
                    self.ui.materials_combobox.setCurrentIndex(i)
                    break

    def calculate(self):
        self.ui.purchases_table.setRowCount(0)
        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)
        customer = self.ui.suppliers_combobox.itemData(self.ui.suppliers_combobox.currentIndex())
        material = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())
        currency = self.ui.currency_combobox.currentData()
        invoice_items_data = self.database_operations.fetchAllInvoiceItems(invoice_main_type='output', material=material, client=customer, from_date=from_date, to_date=to_date)

        for invoice_item in invoice_items_data:
            material_id = invoice_item['material_id']
            material_name = invoice_item['name']
            code = invoice_item['code']
            # unit_name = invoice_item['unit_name']
            currency_name = invoice_item['currency_name']
            date_col = invoice_item['date_col']
            origin = invoice_item['origin']

            if origin == 'invoice':
                material_profit = self.database_operations.fetchProductProfit(material_id, origin='invoice', currency=currency)

            elif origin == 'manufacture':
                material_profit = self.database_operations.fetchProductProfit(material_id, origin='manufacture', currency=currency)

            else:
                material_profit = 0

            numRows = self.ui.purchases_table.rowCount()
            self.ui.purchases_table.insertRow(numRows)

            self.ui.purchases_table.setItem(numRows, 0, QTableWidgetItem(material_name))
            self.ui.purchases_table.setItem(numRows, 1, QTableWidgetItem(code))
            self.ui.purchases_table.setItem(numRows, 2, QTableWidgetItem(material_profit))
            self.ui.purchases_table.setItem(numRows, 3, QTableWidgetItem(currency_name))

