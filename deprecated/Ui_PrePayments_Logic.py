import datetime

import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from win32con import MB_OKCANCEL, IDCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_PrePayments import Ui_PrePayments

class Ui_PrePayments_Logic(object):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.exchage_value = 0
        self.ui = Ui_PrePayments()

    def showUi(self):
        window_pre_payments = QDialog()
        self.ui.setupUi(window_pre_payments)
        self.initialize()
        window_pre_payments.exec()

    def initialize(self):
        self.ui.payments_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.payments_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.ui.payments_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.payments_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.payments_table.verticalHeader().hide()
        self.ui.payments_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.payments_table.setSortingEnabled(True)
        
        self.fetchClients()
        self.fetchExchangePrices()
        self.setExchangeValue()
        self.fetchPayments()

        self.ui.payment_sp_input.textChanged.connect(lambda: self.calculate())
        self.ui.payment_usd_input.textChanged.connect(lambda: self.calculate())
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.setExchangeValue())
        self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.calculate())
        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.calculate())

        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.clearTable())
        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.fetchPayments())

        self.ui.add_btn.clicked.connect(lambda: self.save())
        self.ui.add_btn.clicked.connect(lambda: self.clearTable())
        self.ui.add_btn.clicked.connect(lambda: self.fetchPayments())
        self.ui.delete_btn.clicked.connect(lambda: self.deletePayment())
        self.ui.delete_btn.clicked.connect(lambda: self.clearTable())
        self.ui.delete_btn.clicked.connect(lambda: self.fetchPayments())


    def fetchClients(self):
        clients = self.database_operations.fetchClients()
        for client in clients:
            id = client[0]
            name = client[1]
            governorate = client[2]
            data = [id]
            name = str(name) + ' / ' + str(governorate)
            self.ui.clients_combobox.addItem(name, data)

    def fetchExchangePrices(self):
        exchange_prices = self.database_operations.fetchExchangePrice()
        for exchange_price in exchange_prices:
            value = exchange_price[1]
            date = exchange_price[3]
            display_string = "1$ = " + str(value) + " SP (" + str(date) + ")"
            data = [value, date]
            self.ui.exchange_combobox.addItem(display_string, data)

    def setExchangeValue(self):
        exchange_data = self.ui.exchange_combobox.itemData(self.ui.exchange_combobox.currentIndex())
        self.exchage_value = exchange_data[0]

    def calculate(self):
        currency = self.ui.currency_combobox.itemText(self.ui.currency_combobox.currentIndex())

        if currency == 'ل.س':

            self.ui.payment_sp_input.setEnabled(True)
            self.ui.payment_usd_input.setEnabled(False)

            sp = self.ui.payment_sp_input.text()

            if sp == '':
                sp = 0

            try:
                usd = float(sp) / float(self.exchage_value)
            except:
                usd = 0

            usd = round(usd, 5)
            self.ui.payment_usd_input.setText(str(usd))

        if currency == 'دولار':

            self.ui.payment_sp_input.setEnabled(False)
            self.ui.payment_usd_input.setEnabled(True)

            usd = self.ui.payment_usd_input.text()

            if usd == '':
                usd = 0

            try:
                sp = float(usd) * float(self.exchage_value)
            except:
                sp = 0

            sp = round(sp,5)
            self.ui.payment_sp_input.setText(str(sp))

    def save(self):
        client_id = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())[0]
        payment_sp = self.ui.payment_sp_input.text()
        payment_usd = self.ui.payment_usd_input.text()

        if payment_sp=='' or payment_usd=='':
            win32api.MessageBox(0, "القيم غير صحيحة", "خطأ")

        else:
            try:
                payment_sp = float(payment_sp)
            except:
                payment_sp=0

            try:
                payment_usd = float(payment_usd)
            except:
                payment_usd=0


            date = self.ui.date_input.text()

            self.database_operations.addPrePayment(client_id, payment_sp, payment_usd, date)

    def deletePayment(self):
        confirm = win32api.MessageBox(0, "حذف؟", "تأكيد", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.payments_table.item(self.ui.payments_table.currentRow(), 0)
            print(str(type(table_row)))
            if (str(type(table_row)) == "<class 'NoneType'>"):
                pass
            else:
                id = table_row.text()
                self.database_operations.removePrePayment(id)
                self.clearTable()
                self.fetchPayments()

    def clearTable(self):
        self.ui.payments_table.setRowCount(0)

    def fetchPayments(self):
        client_id = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())[0]
        payments = self.database_operations.fetchPrepayments(client_id)
        for payment in payments:
            id = payment[0]
            sp = payment[2]
            usd = payment[3]
            date = payment[4]

            numRows = self.ui.payments_table.rowCount()
            self.ui.payments_table.insertRow(numRows)

            self.ui.payments_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
            self.ui.payments_table.setItem(numRows, 1, MyTableWidgetItem(str(sp), float(sp)))
            self.ui.payments_table.setItem(numRows, 2, MyTableWidgetItem(str(usd), float(usd)))
            self.ui.payments_table.setItem(numRows, 3, QTableWidgetItem(str(date)))

    def retranslateUi(self, PrePayments):
        _translate = QtCore.QCoreApplication.translate
        PrePayments.setWindowTitle(_translate("PrePayments", "دفعات الزبائن"))
        item = self.ui.payments_table.horizontalHeaderItem(0)
        item.setText(_translate("PrePayments", "#"))
        item = self.ui.payments_table.horizontalHeaderItem(1)
        item.setText(_translate("PrePayments", "التاريخ"))
        item = self.ui.payments_table.horizontalHeaderItem(2)
        item.setText(_translate("PrePayments", "الدفعة (ل.س)"))
        item = self.ui.payments_table.horizontalHeaderItem(3)
        item.setText(_translate("PrePayments", "الدفعة (دولار)"))
        self.label.setText(_translate("PrePayments", "الزبون:"))
        self.label_4.setText(_translate("PrePayments", "العملة:"))
        self.label_7.setText(_translate("PrePayments", "سعر الصرف:"))
        self.label_2.setText(_translate("PrePayments", "الدفعة:"))
        self.ui.currency_combobox.setItemText(0, _translate("PrePayments", "ل.س"))
        self.ui.currency_combobox.setItemText(1, _translate("PrePayments", "دولار"))
        self.label_3.setText(_translate("PrePayments", "التاريخ:"))
        self.label_5.setText(_translate("PrePayments", "ل.س"))
        self.label_6.setText(_translate("PrePayments", "دولار"))
        self.ui.add_btn.setText(_translate("PrePayments", "إضافة"))
        self.ui.delete_btn.setText(_translate("PrePayments", "حذف"))
