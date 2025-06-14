from PyQt5.QtCore import Qt, QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Value_Report import Ui_Value_Report
from PyQt5.QtWidgets import  QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtWidgets import QTableWidgetItem
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt


class Ui_Value_Report_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_Value_Report()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/hr.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self):
        self.fetchMaterials()
        self.fetchCurrencies()
        self.fetchWarehouses()
        self.ui.pricing_method_combobox.addItem(self.language_manager.translate("PRICING_METHOD_MEDIAN"), "avg_invoice")
        self.ui.pricing_method_combobox.addItem(self.language_manager.translate("PRICING_METHOD_LAST_BUY"), "last_invoice")
        self.ui.to_date.setDate(QDate.currentDate())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow)
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow)
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.currency_combobox.addItem(name, id)

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.material_combobox.count()):
                if self.ui.material_combobox.itemData(i)[0] == result['id']:
                    self.ui.material_combobox.setCurrentIndex(i)
                    break

    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material['id']
            name = material['name']
            self.ui.material_combobox.addItem(name, id)

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            self.ui.warehouses_combobox.addItem(name, id)

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'warehouses', checkable=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.warehouses_combobox.count()):
                if self.ui.warehouses_combobox.itemData(i)[0] == result['id']:
                    self.ui.warehouses_combobox.setCurrentIndex(i)
                    break
 
    def calculate(self):
        material_id = self.ui.material_combobox.currentData()
        pricing_method = self.ui.pricing_method_combobox.currentData()
        currency_id = self.ui.currency_combobox.currentData()
        current_date = self.ui.to_date.date().toString(Qt.ISODate)

        # 1- get the average price of the material from invoices
        if pricing_method == 'avg_invoice':
            self.material_pricing_method = 'avg_invoice'

            invoice_type = self.database_operations.fetchInvoiceTypes(name='buy')
            invoice_type=invoice_type[0]['id']

            average_price = self.database_operations.fetchAverageMaterialPrice(material_id, targeted_currency=currency_id, to_date='9999-12-12', invoice_type=invoice_type,from_date='2000-01-01', currency_exchage_date=current_date)

            self.ui.material_table.setRowCount(1)
            self.ui.material_table.setItem(0, 0, QTableWidgetItem(self.ui.material_combobox.currentText()))
            self.ui.material_table.setItem(0, 1, QTableWidgetItem(str(average_price)))


        # 2- get the last purchase price of the material from invoices
        elif pricing_method == 'last_invoice':
            self.material_pricing_method = 'last_invoice'
            manufacture_date = self.ui.manufacture_date_input.date().toString(Qt.ISODate)
            price_data = self.database_operations.fetchLastInvoiceOfMaterial(material_id)
            if price_data:
                quantity1 = price_data['quantity1']
                quantity2 = price_data['quantity2']
                quantity3 = price_data['quantity3']
                unit1_id = price_data['unit1_id']
                unit2_id = price_data['unit2_id']
                unit3_id = price_data['unit3_id']
                average_price_in_payment_currency = price_data['equilivance_price']
                average_price_in_invoice_currency = price_data['unit_price']
                payment_currency = price_data['payment_currency']
                invoice_currency = price_data['invoice_currency']
                invoice_date = price_data['date_col']
                invoice_item_id = price_data['invoice_item_id']
                invoice_id = price_data['invoices_id']

                material_move_id = self.database_operations.fetchMaterialMove(origin='invoice',origin_id=invoice_item_id)

                if material_move_id:
                    warehouse_data = self.database_operations.fetchInvoiceItemWarehouse(material_move_id['id'])
                    if warehouse_data and len(warehouse_data) > 0:
                        warehouse_quantity = warehouse_data[0]
                        warehouse_unit = warehouse_data[1]
                        warehouse_id = warehouse_data[2]
                        warehouse_name = warehouse_data[3]
                        warehouse_account_id = warehouse_data[4]

        # # 3- get the average price of the material from invoices till the pullout date
        # elif pricing_method == 'avg_pullout':


