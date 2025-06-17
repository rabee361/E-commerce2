import time
import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QIcon, QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from TypeChecker import isfloat
from Ui_ProductEdit import Ui_ProductEdit
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_ProductEdit_Logic(object):
    def __init__(self, sqlconnector, product_id):
        super().__init__()
        self.product_id = product_id
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_ProductEdit()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_edit = QDialog()
        self.ui.setupUi(window_edit)
        self.language_manager.load_translated_ui(self.ui, window_edit)
        self.initialize(window_edit)
        window_edit.exec()

    def initialize(self, window_edit):
        self.ui.workhours_input.setValidator(QIntValidator())
        self.ui.year_require_input.setValidator(QIntValidator())
        self.ui.ready_input.setValidator(QIntValidator())
        self.ui.price_input.setValidator(QDoubleValidator())
        self.ui.price_input_usd.setValidator(QDoubleValidator())
        self.ui.discount_1_result_sp.setValidator(QDoubleValidator())

        self.ui.price_input.textChanged.connect(lambda: self.calculateDiscounts())
        self.ui.price_input.textChanged.connect(lambda: self.calculateUSDPrices())

        self.ui.price_input_usd.editingFinished.connect(lambda: self.calculateDiscounts())
        self.ui.price_input_usd.editingFinished.connect(lambda: self.calculateSPPrices())

        self.ui.discount_1_input.textChanged.connect(lambda: self.calculateDiscounts())
        self.ui.discount_1_input.textChanged.connect(lambda: self.calculateUSDPrices())

        self.ui.save_btn.clicked.connect(lambda: self.saveProductData(window_edit))

        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.calculateDiscounts())
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.calculateUSDPrices())

        self.fetchExchangePrices()
        self.fetchProductData()
        self.calculateDiscounts()
        self.calculateUSDPrices()

    def fetchProductData(self):
        product_data = self.database_operations.fetchProduct(self.product_id)
        product_name = product_data[0][1]
        product_name_en = product_data[0][2]
        product_quantity = product_data[0][3]
        product_pills = product_data[0][5]
        product_code = product_data[0][6]
        product_working_hours = product_data[0][4]
        product_year_require = product_data[0][7]
        product_ready = product_data[0][8]
        product_price = product_data[0][9]
        discount_1 = product_data[0][11]
        discount_2 = product_data[0][12]
        discount_3 = product_data[0][13]
        discount_4 = product_data[0][14]
        exchange_id = product_data[0][15]

        # set value of qcombobox from database
        if self.ui.exchange_combobox.count() > 0:
            for i in range(0, self.ui.exchange_combobox.count()):
                exchange_data = self.ui.exchange_combobox.itemData(i)
                exchange_id_from_combobox = exchange_data[0]
                if str(exchange_id_from_combobox) == str(exchange_id):
                    self.ui.exchange_combobox.setCurrentIndex(i)

        self.ui.name_input.setText(str(product_name))
        self.ui.name_en_input.setText(str(product_name_en))
        self.ui.workhours_input.setText(str(product_working_hours))
        self.ui.code_input.setText(str(product_code))
        self.ui.year_require_input.setText(str(product_year_require))
        self.ui.ready_input.setText(str(product_ready))
        self.ui.pills_input.setText(str(product_pills))
        self.ui.quantity_input.setText(str(product_quantity))
        self.ui.price_input.setText(str(product_price))
        self.ui.discount_1_input.setText(str(discount_1))

    def fetchExchangePrices(self):
        exchange_prices = self.database_operations.fetchExchangePrices()
        for exchange_price in exchange_prices:
            id = exchange_price[0]
            usd = exchange_price[1]
            date = exchange_price[3]

            data = [id, usd, date]
            print("Aaa = " + str(data[1]))
            name = str(date) + ' / 1 s.p=' + str(usd) + 'usd'
            self.ui.exchange_combobox.addItem(name, data)

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

    def calculateUSDPrices(self):
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_price = exchange_data[1]
        exchange_price = float(exchange_price)

        price = self.ui.price_input.text()
        if isfloat(price):
            price_usd = float(price) / exchange_price
            price_usd = round(price_usd, 3)
        else:
            price_usd = 0

        self.ui.price_input_usd.setText(str(price_usd))

    def calculateSPPrices(self):
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_price = exchange_data[1]
        exchange_price = float(exchange_price)

        price = self.ui.price_input_usd.text()
        if isfloat(price):
            price_sp = float(price) * exchange_price
            price_sp = round(price_sp, 3)
        else:
            price_sp = 0

        self.ui.price_input.setText(str(price_sp))

    def saveProductData(self, window):
        product_name = self.ui.name_input.text()
        product_name_en = self.ui.name_en_input.text()
        working_hours = self.ui.workhours_input.text()
        code = self.ui.code_input.text()
        year_require = self.ui.year_require_input.text()
        ready = self.ui.ready_input.text()
        price = self.ui.price_input.text()
        discount_1 = self.ui.discount_1_input.text()

        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        exchange_id = exchange_data[0]

        all_ok = True

        if product_name == '' and product_name_en == '':
            win32api.MessageBox(0,'خطأ في الاسم','خطأ')
            all_ok = False
        if code == '':
            win32api.MessageBox(0, 'خطأ في الكود', 'خطأ')
            all_ok = False

        if year_require == '' :
            year_require = 0

        if ready == '' :
            ready = 0

        if price == '' :
            price = 0

        if discount_1 == '' :
            discount_1 = 0

        if all_ok:
            self.database_operations.updateProduct(self.product_id, product_name, product_name_en, working_hours, code,
                                                   year_require, ready, price, discount_1, exchange_id)
            window.accept()
        else:
            pass
