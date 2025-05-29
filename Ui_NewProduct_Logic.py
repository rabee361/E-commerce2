import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QIcon, QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from TypeChecker import isfloat
from Ui_NewProduct import Ui_NewProduct
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_NewProduct_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_NewProduct()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_add_new_product = QDialog()
        self.ui.setupUi(window_add_new_product)
        self.initialize(window_add_new_product)
        self.language_manager.load_translated_ui(self.ui, window_add_new_product)
        window_add_new_product.exec()

    def initialize(self, window):
        self.ui.workhours_input.setValidator(QIntValidator())
        self.ui.year_require_input.setValidator(QIntValidator())
        self.ui.ready_input.setValidator(QIntValidator())
        self.ui.pills_input.setValidator(QIntValidator())
        self.ui.quantity_input.setValidator(QIntValidator())
        self.ui.price_input.setValidator(QDoubleValidator())
        self.ui.price_input_usd.setValidator(QDoubleValidator())
        self.ui.discount_1_input.setValidator(QDoubleValidator())

        self.ui.discount_1_result_sp.setValidator(QDoubleValidator())

        self.ui.price_input.textChanged.connect(lambda: self.calculateDiscounts())
        self.ui.price_input.textChanged.connect(lambda: self.calculateUSDPrices())

        self.ui.price_input_usd.editingFinished.connect(lambda: self.calculateDiscounts())
        self.ui.price_input_usd.editingFinished.connect(lambda: self.calculateSPPrices())

        self.ui.discount_1_input.textChanged.connect(lambda: self.calculateDiscounts())
        self.ui.discount_1_input.textChanged.connect(lambda: self.calculateUSDPrices())


        self.ui.save_btn.clicked.connect(lambda: self.saveProductData(window))

        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.calculateDiscounts())
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.calculateUSDPrices())

        self.fetchExchangePrices()



    def fetchExchangePrices(self):
        exchange_prices = self.database_operations.fetchExchangePrices()
        for exchange_price in exchange_prices:
            id = exchange_price[0]
            usd = exchange_price[1]
            date = exchange_price[3]
            data = [id, usd, date]
            print("Aaa = "+str(data[1]))
            name = str(date) + ' / 1 s.p=' + str(usd) + 'usd'
            self.ui.exchange_combobox.addItem(name, data)

    def calculateUSDPrices(self):
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_price = exchange_data[1]
        exchange_price = float(exchange_price)

        price = self.ui.price_input.text()
        if isfloat(price):
            price_usd = float(price)/exchange_price
            price_usd = round(price_usd,3)
        else:
            price_usd = 0

        self.ui.price_input_usd.setText(str(price_usd))

    def calculateSPPrices(self):
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_price = exchange_data[1]
        exchange_price = float(exchange_price)

        price = self.ui.price_input_usd.text()
        if isfloat(price):
            price_sp = float(price)*exchange_price
            price_sp = round(price_sp,3)
        else:
            price_sp = 0

        self.ui.price_input.setText(str(price_sp))

    def saveProductData(self, window):
        product_name = self.ui.name_input.text()
        product_name_en = self.ui.name_en_input.text()
        working_hours = self.ui.workhours_input.text()
        quantity = self.ui.quantity_input.text()
        pills = self.ui.pills_input.text()
        code = self.ui.code_input.text()
        year_require = self.ui.year_require_input.text()
        ready = self.ui.ready_input.text()
        price = self.ui.price_input.text()
        discount_1 = self.ui.discount_1_input.text()
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_id = exchange_data[0]

        if (product_name_en=='' and product_name==''):
            win32api.MessageBox(0,'خطأ، يرجى المحاولة مرة أخرى','')
        else:
            working_hours = 0 if working_hours=='' else working_hours
            quantity = 0 if quantity=='' else quantity
            pills = 0 if pills=='' else pills
            year_require = 0 if year_require=='' else year_require
            ready = 0 if ready=='' else ready
            price = 0 if price=='' else price
            discount_1 = 0 if discount_1=='' else discount_1


            exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
            exchange_id = exchange_data[0]
            self.database_operations.addNewProduct(product_name, product_name_en, quantity, working_hours, pills,
                                                   year_require, ready, code, price, exchange_id, discount_1)
            window.accept()

    def calculateDiscounts(self):
        price = self.ui.price_input.text()
        discount_1 = self.ui.discount_1_input.text()

        if (isfloat(str(discount_1)) and isfloat(str(price))):
            discount_1_value = float(price) * (100 - float(discount_1)) / 100
            discount_1_value = round(discount_1_value, 3)
        else:
            discount_1_value = 0
        self.ui.discount_1_result_sp.setText(str(discount_1_value))


        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_price = exchange_data[1]
        exchange_price = float(exchange_price)

        discount_1_sp_price = self.ui.discount_1_result_sp.text()


        discount_1_usd_price = float(discount_1_sp_price) / exchange_price
        discount_1_usd_price = round(discount_1_usd_price, 3)
        self.ui.discount_1_result_usd.setText(str(discount_1_usd_price))
