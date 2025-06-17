

import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate
from PyQt5.QtGui import QDoubleValidator, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QDialog, QTableWidgetItem
from win32con import MB_OKCANCEL, IDCANCEL
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_NewInvoice import Ui_NewInvoice
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator    

class Ui_NewInvoice_Logic(QDialog):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.NewInvoice = QDialog
        self.exchange_value = ''
        self.exchange_date = ''
        self.ui = Ui_NewInvoice()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_newinvoice = QDialog()
        self.ui.setupUi(window_newinvoice)
        self.language_manager.load_translated_ui(self.ui, window_newinvoice)
        self.initialize(window_newinvoice)
        window_newinvoice.exec()    

    def initialize(self, window):
        self.ui.date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.date_input.setDate(QDate.currentDate())

        self.ui.quantity_input.setValidator(QDoubleValidator())
        self.ui.unit_price_input.setValidator(QDoubleValidator())
        self.ui.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.ui.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.items_table.verticalHeader().hide()

        self.ui.suggestions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.suggestions_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.suggestions_table.verticalHeader().hide()
        #self.ui.suggestions_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.suggestions_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.ui.suggestions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.add_btn.clicked.connect(lambda: self.addInvoiceItem())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteInvoiceItem())
        self.ui.save_btn.clicked.connect(lambda: self.saveInvoiceItems())
        self.ui.save_btn.clicked.connect(lambda: window.accept())

        self.autoInvoiceNumber()
        self.fetchExchangeData()
        #self.showSuggestions()
        self.ui.code_input.textChanged.connect(lambda: self.showSuggestions())
        self.ui.date_input.dateChanged.connect(lambda: self.fetchExchangeData())


    def showSuggestions(self):
        text = str(self.ui.code_input.text())
        materials = self.database_operations.fetchMaterialsSuggestions(text)
        self.clearSuggestionsTable()
        for material in materials:
            material_id = material[0]
            material_code = material[1]
            material_name = material[2]
            self.material_name_en = material[3]
            material_name = str(material_name) + " " + str(self.material_name_en)
            # Create a empty row at bottom of table
            numRows = self.ui.suggestions_table.rowCount()
            self.ui.suggestions_table.insertRow(numRows)
            # Add text to the row
            self.ui.suggestions_table.setItem(numRows, 0, MyTableWidgetItem(str(material_id), id))
            self.ui.suggestions_table.setItem(numRows, 1, QTableWidgetItem(material_code))
            self.ui.suggestions_table.setItem(numRows, 2, QTableWidgetItem(material_name))

    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        print(type(last_invoice_number))
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            self.ui.number_input.setText("1")
        else:
            self.ui.number_input.setText(str(int(last_invoice_number) + 1))

    def fetchExchangeData(self):
        date = self.ui.date_input.text()
        try:
            exchange_data = self.database_operations.fetchExchangePrice(date)
            self.exchange_value = exchange_data[0][1]
            self.exchange_date = exchange_data[0][3]
            self.ui.exchange_input.setText(str(exchange_data[0][1]))
            self.recalculateItemsTabel()
        except:
            print("Date error.")

    def recalculateItemsTabel(self):
        for row in range(self.ui.items_table.rowCount()):
            quantity = self.ui.items_table.item(row, 3).text()
            unit_price_sp = self.ui.items_table.item(row, 5).text()
            unit_price_usd = self.ui.items_table.item(row, 6).text()
            total_price_sp = self.ui.items_table.item(row, 7).text()
            total_price_usd = self.ui.items_table.item(row, 8).text()
            currency = self.ui.items_table.item(row, 9).text()

            if currency == 'ل.س':
                unit_price_usd = float(unit_price_sp) / self.exchange_value
                total_price_usd = float(unit_price_usd) * float(quantity)
            else:
                unit_price_sp = float(unit_price_usd) * self.exchange_value
                total_price_sp = float(unit_price_sp) * float(quantity)

            unit_price_usd = round(float(unit_price_usd), 5)
            unit_price_sp = round(float(unit_price_sp), 5)
            total_price_usd = round(float(total_price_usd), 5)
            total_price_sp = round(float(total_price_sp), 5)

            self.ui.items_table.setItem(row, 5, QTableWidgetItem(str(unit_price_sp)))
            self.ui.items_table.setItem(row, 6, QTableWidgetItem(str(unit_price_usd)))
            self.ui.items_table.setItem(row, 7, QTableWidgetItem(str(total_price_sp)))
            self.ui.items_table.setItem(row, 8, QTableWidgetItem(str(total_price_usd)))

    def saveInvoiceItems(self):
        column = 0
        # rowCount() This property holds the number of rows in the table
        date = self.ui.date_input.text()
        invoice_number = self.ui.number_input.text()
        # check if numbre already exists
        if (self.database_operations.checkInvoiceExists(str(self.ui.number_input.text()))):
            win32api.MessageBox(0, "يوجد فاتورة سابقة بنفس الرقم", "خطأ")
        else:
            for row in range(self.ui.items_table.rowCount()):
                material_id = self.ui.items_table.item(row, 0).text()
                material_name = self.ui.items_table.item(row, 1).text()
                material_code = self.ui.items_table.item(row, 2).text()
                quantity = self.ui.items_table.item(row, 3).text()
                unit = self.ui.items_table.item(row, 4).text()
                total_price = self.ui.items_table.item(row, 7).text()
                currency = self.ui.items_table.item(row, 9).text()
                seller = self.ui.seller_input.text()
                statement = self.ui.statement_input.text()

                if currency == 'ل.س':
                    currency = 'SP'
                    unit_price = self.ui.items_table.item(row, 5).text()
                else:
                    currency = "USD"
                    unit_price = self.ui.items_table.item(row, 6).text()
                self.database_operations.addInvoice(invoice_number, material_id, quantity, unit, unit_price, date,
                                                    currency, seller, statement)


    def clearSuggestionsTable(self):
        self.ui.suggestions_table.setRowCount(0)


    def addInvoiceItem(self):
        table_row_id = self.ui.suggestions_table.item(self.ui.suggestions_table.currentRow(), 0)
        if (str(type(table_row_id)) == "<class 'NoneType'>"):
            pass
        else:
            material_id = table_row_id.text()
            table_row_code = self.ui.suggestions_table.item(self.ui.suggestions_table.currentRow(), 1)
            material_code = table_row_code.text()
            table_row_name = self.ui.suggestions_table.item(self.ui.suggestions_table.currentRow(), 2)
            material_name = table_row_name.text()
            quantity = self.ui.quantity_input.text()
            currency = self.ui.currency_input.currentText()
            unit = self.ui.comboBox.currentText()
            unit_price = self.ui.unit_price_input.text()
            if (material_id == '' or material_code == '' or material_name == '' or quantity == '' or unit_price == ''):
                win32api.MessageBox(0, "يرجى التأكد من المعلومات", "خطأ")
            else:
                if (currency == 'ل.س'):
                    unit_price_sp = float(unit_price)
                    unit_price_sp = round(unit_price_sp, 5)
                    print(str(self.exchange_value))
                    unit_price_usd = float(unit_price_sp) / float(self.exchange_value)
                    unit_price_usd = round(unit_price_usd, 5)
                    unit_price_usd_string = str(unit_price_usd)
                    unit_price_sp_string = str(unit_price_sp)
                    total_price_sp = float(quantity) * float(unit_price_sp)
                    total_price_sp = round(total_price_sp, 5)
                    total_price_sp_string = str(total_price_sp)
                    total_price_usd = float(total_price_sp) / float(self.exchange_value)
                    total_price_usd = round(total_price_usd, 5)
                    total_price_usd_string = str(total_price_usd)

                    numRows = self.ui.items_table.rowCount()
                    self.ui.items_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.items_table.setItem(numRows, 0, QTableWidgetItem(material_id))
                    self.ui.items_table.setItem(numRows, 1, QTableWidgetItem(material_name))
                    self.ui.items_table.setItem(numRows, 2, QTableWidgetItem(material_code))
                    self.ui.items_table.setItem(numRows, 3, QTableWidgetItem(str(quantity)))
                    self.ui.items_table.setItem(numRows, 4, QTableWidgetItem(str(unit)))
                    self.ui.items_table.setItem(numRows, 5, QTableWidgetItem(unit_price_sp_string))
                    self.ui.items_table.setItem(numRows, 6, QTableWidgetItem(unit_price_usd_string))
                    self.ui.items_table.setItem(numRows, 7, QTableWidgetItem(total_price_sp_string))
                    self.ui.items_table.setItem(numRows, 8, QTableWidgetItem(total_price_usd_string))
                    self.ui.items_table.setItem(numRows, 9, QTableWidgetItem(str(currency)))
                else:
                    unit_price_usd = float(unit_price)
                    unit_price_usd = round(unit_price_usd, 5)
                    unit_price_sp = float(unit_price_usd) * float(self.exchange_value)
                    unit_price_usd_string = str(unit_price_usd)
                    unit_price_sp_string = str(unit_price_sp)
                    total_price_usd = float(quantity) * float(unit_price_usd)
                    total_price_usd = round(total_price_usd, 5)
                    total_price_usd_string = str(total_price_usd)
                    total_price_sp = float(total_price_usd) * float(self.exchange_value)
                    total_price_sp_string = str(total_price_sp)

                    numRows = self.ui.items_table.rowCount()
                    self.ui.items_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.items_table.setItem(numRows, 0, QTableWidgetItem(material_id))
                    self.ui.items_table.setItem(numRows, 1, QTableWidgetItem(material_name))
                    self.ui.items_table.setItem(numRows, 2, QTableWidgetItem(material_code))
                    self.ui.items_table.setItem(numRows, 3, QTableWidgetItem(str(quantity)))
                    self.ui.items_table.setItem(numRows, 4, QTableWidgetItem(str(unit)))
                    self.ui.items_table.setItem(numRows, 5, QTableWidgetItem(unit_price_sp_string))
                    self.ui.items_table.setItem(numRows, 6, QTableWidgetItem(unit_price_usd_string))
                    self.ui.items_table.setItem(numRows, 7, QTableWidgetItem(total_price_sp_string))
                    self.ui.items_table.setItem(numRows, 8, QTableWidgetItem(total_price_usd_string))
                    self.ui.items_table.setItem(numRows, 9, QTableWidgetItem(str(currency)))

    def deleteInvoiceItem(self):
        confirm = win32api.MessageBox(0, "حذف؟", " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.items_table.currentRow()
            self.ui.items_table.removeRow(table_row)
