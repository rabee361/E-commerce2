
import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QDialog
from win32con import IDCANCEL, MB_OKCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_NewReturnInvoice import Ui_NewReturnInvoice
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_NewReturnInvoice_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_NewReturnInvoice()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_newreturninvoice = QDialog()
        self.ui.setupUi(window_newreturninvoice)
        self.initialize(window_newreturninvoice)
        self.language_manager.load_translated_ui(self.ui, window_newreturninvoice)
        window_newreturninvoice.exec()

    def initialize(self, window):
        self.ui.date_input.setDisplayFormat('dd-MM-yyyy')
        self.ui.date_input.setDate(QDate.currentDate())

        self.ui.quantity_input.setValidator(QIntValidator())
        self.ui.discount_input.setValidator(QDoubleValidator())
        self.ui.price_sp_input.setValidator(QDoubleValidator())

        self.ui.items_table.verticalHeader().hide()
        self.ui.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        # self.ui.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        # self.ui.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        # self.ui.items_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        # self.ui.items_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)

        self.fetchClients()
        self.fetchProducts()
        self.setProductFields()
        self.changeCurrency()

        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.changeCurrency())
        self.ui.products_combobox.currentIndexChanged.connect(lambda: self.setProductFields())

        self.ui.discount_input.editingFinished.connect(lambda: self.calculateProductFields())
        self.ui.price_sp_input.editingFinished.connect(lambda: self.calculateProductFields())
        self.ui.price_usd_input.editingFinished.connect(lambda: self.calculateProductFields())
        self.ui.exchange_input.editingFinished.connect(lambda: self.calculateProductFields())
        self.ui.result_discount_input.editingFinished.connect(lambda: self.calculateTotalInvoiceValue())
        self.ui.add_btn.clicked.connect(lambda: self.addItem())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteItem())
        self.ui.save_btn.clicked.connect(lambda: self.saveInvoice())
        self.ui.save_btn.clicked.connect(lambda: window.accept())


    def fetchClients(self):
        clients = self.database_operations.fetchClients()
        for client in clients:
            id = client[0]
            name = client[1]
            governorate = client[2]
            data = [id]
            name = str(name) + ' / ' + str(governorate)
            self.ui.clients_combobox.addItem(name, data)


    def fetchProducts(self):
        self.ui.products_combobox.clear()

        products = self.database_operations.fetchProducts()

        for product in products:
            id = product[0]
            name = product[1]
            name_en = product[2]
            unit_price_sp = product[9]
            discount1 = product[11]
            name = name + ' / ' + name_en
            data = [id, name, unit_price_sp, discount1]

            in_table = False

            for row in range(self.ui.items_table.rowCount()):
                product_id_in_table = self.ui.items_table.item(row, 0).text()
                if str(product_id_in_table) == str(id):
                    print("")
                    print("IN TABLE " + str(id) )
                    print("")
                    in_table = True

            if not in_table:
                self.ui.products_combobox.addItem(name, data)


    def setProductFields(self):
        # get product data
        product_data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        if (str(type(product_data)) != "<class 'NoneType'>"):
            product_id = product_data[0]
            product_name = product_data[1]

            units_count = self.ui.quantity_input.text()

            try:
                product_discount = self.ui.discount_input.text()
                product_discount=float(product_discount)
                if product_discount <= 0:
                    product_discount = 0
            except:
                product_discount = 0

            try:
                product_unit_price_sp = self.ui.price_sp_input.text()
                product_unit_price_sp=float(product_unit_price_sp)
                if product_unit_price_sp <= 0:
                    product_unit_price_sp = 0
            except:
                product_unit_price_sp = 0

            try:
                product_unit_price_usd = self.ui.price_usd_input.text()
                product_unit_price_usd=float(product_unit_price_usd)
                if product_unit_price_usd <= 0:
                    product_unit_price_usd = 0
            except:
                product_unit_price_usd = 0


            product_price_after_discount_sp = round(float(float(product_unit_price_sp) * (100 - float(product_discount)) / 100),6)
            product_price_after_discount_usd = round(float(float(product_unit_price_usd) * (100 - float(product_discount)) / 100),6)


            self.ui.price_sp_input.setText(str(product_unit_price_sp))
            self.ui.price_usd_input.setText(str(product_unit_price_usd))
            self.ui.quantity_input.setText(str(units_count))
            self.ui.discount_input.setText(str(product_discount))
            self.ui.price_after_discount_sp_input.setText(str(product_price_after_discount_sp))
            self.ui.price_after_discount_usd_input.setText(str(product_price_after_discount_usd))

    def changeCurrency(self):
        currency = self.ui.currency_combobox.itemText(self.ui.currency_combobox.currentIndex())
        if currency=='دولار':
            self.ui.price_sp_input.setEnabled(False)
            self.ui.price_usd_input.setEnabled(True)
        elif currency=='ل.س':
            self.ui.price_sp_input.setEnabled(True)
            self.ui.price_usd_input.setEnabled(False)
        else:
            pass

    def calculateProductFields(self):
        exchange_rate = self.ui.exchange_input.text()
        try:
            exchange_rate = float(exchange_rate)
            if exchange_rate < 0.0:
                exchange_rate = 0
        except:
            exchange_rate = 0

        currency = self.ui.currency_combobox.itemText(self.ui.currency_combobox.currentIndex())

        product_discount = self.ui.discount_input.text()
        try:
            float(product_discount)
            if float(product_discount) < 0:
                product_discount = 0
        except:
            product_discount = 0

        if currency == 'ل.س':
            product_unit_price_sp = self.ui.price_sp_input.text()
            try:
                if float(product_unit_price_sp)<0:
                    product_unit_price_sp = 0
            except:
                product_unit_price_sp = 0

            units_count = self.ui.quantity_input.text()
            try:
                if int(units_count) < 0:
                    units_count = 0
            except:
                units_count = 0


            product_unit_price_after_discount_sp = round(
                float(float(product_unit_price_sp) * (100 - float(product_discount)) / 100), 6)

            if exchange_rate > 0:
                product_unit_price_usd = round(float(float(product_unit_price_sp) / float(exchange_rate)), 6)
            else:
                product_unit_price_usd = 0

            product_unit_price_after_discount_usd = round(
                float(float(product_unit_price_usd) * (100 - float(product_discount)) / 100), 6)

        elif currency == 'دولار':
            product_unit_price_usd = self.ui.price_usd_input.text()
            try:
                if float(product_unit_price_usd) < 0:
                    product_unit_price_usd = 0
            except:
                product_unit_price_usd = 0

            units_count = self.ui.quantity_input.text()
            try:
                if int(units_count) < 0:
                    units_count = 0
            except:
                units_count = 0

            product_discount = self.ui.discount_input.text()
            try:
                float(product_discount)
                if float(product_discount) < 0:
                    product_discount = 0
            except:
                product_discount = 0

            product_unit_price_after_discount_usd = round(float(float(product_unit_price_usd) * (100 - float(product_discount)) / 100), 6)
            product_unit_price_sp = round(float(float(product_unit_price_usd) * float(exchange_rate)), 6)
            product_unit_price_after_discount_sp = round(float(float(product_unit_price_sp) * (100 - float(product_discount)) / 100), 6)
        else:
            pass

        self.ui.price_sp_input.setText(str(product_unit_price_sp))
        self.ui.price_usd_input.setText(str(product_unit_price_usd))
        self.ui.price_after_discount_sp_input.setText(str(product_unit_price_after_discount_sp))
        self.ui.price_after_discount_usd_input.setText(str(product_unit_price_after_discount_usd))

    def calculateTotalInvoiceValue(self):
        total_sp = 0
        total_usd = 0
        total_sp_after_discount = 0
        total_usd_after_discount = 0
        for i in range(0, self.ui.items_table.rowCount()):
            price_sp = self.ui.items_table.item(i,3).text()
            price_usd = self.ui.items_table.item(i,4).text()
            total_sp = total_sp + float(price_sp)
            total_usd = total_usd + float(price_usd)

        discount = self.ui.result_discount_input.text()
        try:
            if int(discount) < 0:
                discount = 0
                self.ui.result_discount_input.setText("0")
        except:
            discount = 0
            self.ui.result_discount_input.setText("0")

        total_sp_after_discount = round(float(float(total_sp) * (100 - float(discount)) / 100),6)
        total_usd_after_discount = round(float(float(total_usd) * (100 - float(discount)) / 100),6)

        self.ui.result_sp_input.setText(str(total_sp))
        self.ui.result_usd_input.setText(str(total_usd))
        self.ui.result_after_discount_sp_input.setText(str(total_sp_after_discount))
        self.ui.result_after_discount_usd_input.setText(str(total_usd_after_discount))

    def addItem(self):
        # get product
        product_data = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())
        product_id = product_data[0]
        product_name = product_data[1]

        units_count = self.ui.quantity_input.text()
        if str(units_count)=='' or int(units_count) <= 0:
            win32api.MessageBox(0, "عدد القطع غير صحيح", "خطأ")
        else:
            unit_price_sp = self.ui.price_sp_input.text()
            unit_price_usd = self.ui.price_usd_input.text()

            price_sp = float(unit_price_sp)*int(units_count)
            price_usd = float(unit_price_usd)*int(units_count)

            unit_price_after_discount_sp = self.ui.price_after_discount_sp_input.text()
            unit_price_after_discount_usd = self.ui.price_after_discount_usd_input.text()

            price_after_discount_sp = float(unit_price_after_discount_sp) * int(units_count)
            price_after_discount_usd = float(unit_price_after_discount_usd) * int(units_count)

            discount = self.ui.discount_input.text()

            numRows = self.ui.items_table.rowCount()
            self.ui.items_table.insertRow(numRows)

            # Add text to the row
            self.ui.items_table.setItem(numRows, 0, MyTableWidgetItem(str(product_id), int(product_id)))
            self.ui.items_table.setItem(numRows, 0, MyTableWidgetItem(str(product_id), int(product_id)))
            self.ui.items_table.setItem(numRows, 1, QTableWidgetItem(str(product_name)))
            self.ui.items_table.setItem(numRows, 2, QTableWidgetItem(str(units_count)))
            self.ui.items_table.setItem(numRows, 3, QTableWidgetItem(str(price_sp)))
            self.ui.items_table.setItem(numRows, 4, QTableWidgetItem(str(price_usd)))
            self.ui.items_table.setItem(numRows, 5, QTableWidgetItem(str(discount)))
            self.ui.items_table.setItem(numRows, 6, QTableWidgetItem(str(price_after_discount_sp)))
            self.ui.items_table.setItem(numRows, 7, QTableWidgetItem(str(price_after_discount_usd)))

            self.ui.products_combobox.removeItem(self.ui.products_combobox.currentIndex())

        self.calculateTotalInvoiceValue()

    def deleteItem(self):
        confirm = win32api.MessageBox(0, "حذف؟", " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.items_table.currentRow()
            self.ui.items_table.removeRow(table_row)
            self.calculateTotalInvoiceValue()
            self.fetchProducts()

    def saveInvoice(self):
        self.calculateProductFields()

        number = self.ui.number_input.text()
        type = 'returns'
        client_data = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())
        if client_data is not None:
            client = client_data[0]
        else:
            client = ''
        direct_client = ''
        payment = self.ui.payment_combobox.itemText(self.ui.payment_combobox.currentIndex())
        statement = self.ui.statement_input.toPlainText()
        paid = self.ui.paid_combobox.itemText(self.ui.paid_combobox.currentIndex())
        date = self.ui.date_input.text()
        currency = self.ui.currency_combobox.itemText(self.ui.currency_combobox.currentIndex())
        exchange = self.ui.exchange_input.text()
        try:
            exchange = float(exchange)
        except:
            exchange = 0

        total_discount = self.ui.result_discount_input.text()

        if str(total_discount)!="" and float(total_discount) <= 0.0:
            total_discount=0

        if self.ui.items_table.rowCount() > 0 and client != '':
            new_out_invoice_id=self.database_operations.addOutInvoice(number, type, client, direct_client, payment, statement, paid, total_discount, currency, exchange, date)
            for row in range(self.ui.items_table.rowCount()):
                product_id = self.ui.items_table.item(row, 0).text()
                quantity = self.ui.items_table.item(row, 2).text()
                price_sp = self.ui.items_table.item(row, 3).text()
                price_usd = self.ui.items_table.item(row, 4).text()
                discount = self.ui.items_table.item(row, 5).text()
                price_sp_after_discount = self.ui.items_table.item(row, 6).text()
                price_usd_after_discount = self.ui.items_table.item(row, 7).text()

                self.database_operations.addOutInvoiceItem(new_out_invoice_id, product_id, quantity,price_sp, price_usd, discount, price_sp_after_discount, price_usd_after_discount)
                if self.ui.checkBox.isChecked():
                    self.database_operations.increaseProductQuantity(product_id, quantity)
        elif client == '':
            win32api.MessageBox(0,'يجب إضافة زبون أولاً.','خطأ')
        else:
            pass
