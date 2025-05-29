from datetime import datetime

import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView, QHeaderView
from win32con import MB_OKCANCEL, MB_YESNO, IDYES
from PyQt5.QtCore import QDate
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Currencies import Ui_Currencies
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5 import QtWidgets


class Ui_Currencies_Logic(QDialog): 
    DatabaseOperations = ''

    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Currencies()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)
        self.float_point_precision = ''

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchFloatPointPrecision()
        # Initialize currencies table
        self.ui.currencies_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.currencies_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.currencies_table.verticalHeader().hide()
        self.ui.currencies_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.currencies_table.setSortingEnabled(True)
        self.ui.currencies_table.setColumnHidden(0, True)
        self.ui.currencies_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

        # initialize exchange table
        self.ui.exchange_table.setColumnHidden(0, True)  # Hide ID column in exchange_table
        self.ui.exchange_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.exchange_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.exchange_table.setSelectionMode(QAbstractItemView.SingleSelection)
        item = QtWidgets.QTableWidgetItem()
        item.setText(self.language_manager.translate("CURRENCY"))
        self.ui.exchange_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(self.language_manager.translate("EXCHANGE_RATE"))
        self.ui.exchange_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        item.setText(self.language_manager.translate("DATE"))
        self.ui.exchange_table.setHorizontalHeaderItem(3, item)
        # self.ui.exchange_table.verticalHeader().hide()
        self.ui.exchange_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.exchange_table.setSortingEnabled(True)

        # format the date fields
        self.ui.exchange_date.setDisplayFormat("dd-MM-yyyy")
        self.ui.exchange_date.setDate(QDate.currentDate())

        # Update field and labels when currency selected from the table.
        self.ui.currencies_table.cellClicked.connect(lambda: self.fetchCurrencyData())

        # Set labels update triggers
        self.ui.name_edit_input.textChanged.connect(lambda: self.updateEditPartsLabels())
        self.ui.parts_edit_input.textChanged.connect(lambda: self.updateEditPartsLabels())
        self.ui.name_input.textChanged.connect(lambda: self.updatePartsLabels())
        self.ui.parts_input.textChanged.connect(lambda: self.updatePartsLabels())

        # Set validators for double-only input fields
        self.ui.parts_relation_input.setValidator(QDoubleValidator())
        self.ui.parts_relation_edit_input.setValidator(QDoubleValidator())

        # Link buttons with their respective functions
        self.ui.save_new_btn.clicked.connect(lambda: self.addCurrency())
        self.ui.save_edits_btn.clicked.connect(lambda: self.editCurrency())
        self.ui.delete_currency_btn.clicked.connect(lambda: self.deleteCurrency())
        self.ui.add_exchange_btn.clicked.connect(lambda: self.addExchabgeValue())
        self.ui.delete_exchange_btn.clicked.connect(lambda: self.deleteExchangeValue())

        # Set comboboxes triggers
        self.ui.exchange_currencies_combobox.currentIndexChanged.connect(lambda: self.fetchExchangeValues())
        self.fetchCurrencies()

    def fetchFloatPointPrecision(self):
        self.float_point_precision = self.database_operations.fetchFloatPointValue()

    def fetchCurrencies(self):
        # clear previous items to prevent duplications
        self.ui.currencies_table.clear()
        self.ui.currencies_table.setRowCount(0)
        self.ui.exchange_currencies_combobox.clear()

        # fetch new items
        currencies = self.database_operations.fetchCurrencies()
        # Add currencies to table
        for currency in currencies:
            id = currency[0]
            name = currency[1]

            # Create a empty row at bottom of table
            numRows = self.ui.currencies_table.rowCount()
            self.ui.currencies_table.insertRow(numRows)

            # Add text to the row
            self.ui.currencies_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
            self.ui.currencies_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

        # Add currencies to exchange combobox
        for currency in currencies:
            id = currency[0]
            display_text = currency[1]
            data = id
            self.ui.exchange_currencies_combobox.addItem(display_text, data)

    def fetchCurrencyData(self):
        # Clear Previous Data
        self.ui.name_edit_input.clear()
        self.ui.pre_relation_edit_label.clear()
        self.ui.post_relation_edit_label.clear()
        self.ui.symbol_edit_input.clear()
        self.ui.parts_edit_input.clear()
        self.ui.parts_relation_edit_input.clear()

        table_row = self.ui.currencies_table.item(self.ui.currencies_table.currentRow(), 0)

        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            currency_id = table_row.text()
            currency_data = self.database_operations.fetchCurrency(currency_id)

            name = currency_data[1]
            symbol = currency_data[2]
            parts = currency_data[3]
            parts_relation = currency_data[4]

            self.ui.name_edit_input.setText(str(name))
            self.ui.pre_relation_edit_label.setText(f"{self.language_manager.translate('EACH')} 1 " + str(name) + "=")
            self.ui.post_relation_edit_label.setText(str(parts))
            self.ui.symbol_edit_input.setText(str(symbol))
            self.ui.parts_edit_input.setText(str(parts))
            self.ui.parts_relation_edit_input.setText(str(parts_relation))

            self.ui.pre_exchange_label.setText(f"{self.language_manager.translate('EACH')} 1 " + str(name) + "=")
            self.fetchExchangeValues()

    def updateEditPartsLabels(self):
        name = self.ui.name_edit_input.text()
        parts = self.ui.parts_edit_input.text()
        self.ui.pre_relation_edit_label.setText(f"{self.language_manager.translate('EACH')} 1 " + str(name) + "=")
        self.ui.post_relation_edit_label.setText(str(parts))

    def updatePartsLabels(self):
        name = self.ui.name_input.text()
        parts = self.ui.parts_input.text()
        self.ui.pre_relation_label.setText(f"{self.language_manager.translate('EACH')} 1 " + str(name) + "=")
        self.ui.post_relation_label.setText(str(parts))

    def addCurrency(self):
        name = self.ui.name_input.text()
        symbol = self.ui.symbol_input.text()
        parts = self.ui.parts_input.text()
        parts_relation = self.ui.parts_relation_input.text()

        if (name and parts and parts_relation):
            try:
                self.database_operations.addCurrency(name, symbol, parts, parts_relation)
                self.fetchCurrencies()
                # Clear Data
                self.ui.name_input.clear()
                self.ui.symbol_input.clear()
                self.ui.parts_input.clear()
                self.ui.parts_relation_input.clear()
                self.ui.pre_relation_label.clear()
                self.ui.post_relation_label.clear()
            except:
                win32api.MessageBox(0, self.language_manager.translate("CURRENCY_ALREADY_EXISTS_ERROR"), self.language_manager.translate("ERROR"))
        else:
            win32api.MessageBox(0, self.language_manager.translate("ALL_FIELDS_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))

    def editCurrency(self):
        id = self.ui.currencies_table.item(self.ui.currencies_table.currentRow(), 0).text()

        if str(type(id)) == "<class 'NoneType'>":
            pass
        else:
            name = self.ui.name_edit_input.text()
            symbol = self.ui.symbol_edit_input.text()
            parts = self.ui.parts_edit_input.text()
            parts_relation = self.ui.parts_relation_edit_input.text()

            if (name and parts and parts_relation):
                try:
                    self.database_operations.editCurrency(id, name, symbol, parts, parts_relation)
                    self.fetchCurrencies()
                    self.fetchCurrencyData()
                except:
                    win32api.MessageBox(0, self.language_manager.translate("CURRENCY_ALREADY_EXISTS_ERROR"), self.language_manager.translate("ERROR"))
            else:
                win32api.MessageBox(0, self.language_manager.translate("ALL_FIELDS_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))

    def deleteCurrency(self):
        id = self.ui.currencies_table.item(self.ui.currencies_table.currentRow(), 0)

        if (str(type(id)) == "<class 'NoneType'>"):
            pass
        else:
            currency_id = id.text()
            self.database_operations.deleteCurrency(currency_id)
            self.fetchCurrencies()
            self.fetchCurrencyData()

    def fetchExchangeValues(self):
        self.ui.exchange_table.setRowCount(0)
        # exchange_value=None
        table_row = self.ui.currencies_table.item(self.ui.currencies_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            currency1_id = table_row.text()
            exchange_values = self.database_operations.fetchExchangeValues(currency1_id)
            for exchange_value in exchange_values:
                id = exchange_value[0]
                exchange = exchange_value[1]
                date = exchange_value[2]
                currency = exchange_value[3]

                numRows = self.ui.exchange_table.rowCount()
                self.ui.exchange_table.insertRow(numRows)

                # Add text to the row
                self.ui.exchange_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                self.ui.exchange_table.setItem(numRows, 1, QTableWidgetItem(str(currency)))
                self.ui.exchange_table.setItem(numRows, 2, MyTableWidgetItem(str(round(float(exchange), int(self.float_point_precision))), float(exchange)))
                self.ui.exchange_table.setItem(numRows, 3, QTableWidgetItem(str(date)))

    def deleteExchangeValue(self):
        table_row = self.ui.exchange_table.item(self.ui.exchange_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            exchange_id = table_row.text()
            confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if confirm == IDYES:
                self.database_operations.removeExchangeValue(exchange_id)
                self.fetchExchangeValues()

    def addExchabgeValue(self):
        currency1_id = self.ui.currencies_table.item(self.ui.currencies_table.currentRow(), 0).text()
        currency2_id = self.ui.exchange_currencies_combobox.currentData()
        exchage_value = self.ui.exchange.text()
        date = datetime.strptime(self.ui.exchange_date.text(), '%Y-%m-%d').strftime('%Y-%m-%d')
        if (exchage_value and currency1_id and currency2_id and date and (int(currency1_id) != int(currency2_id))):
            self.database_operations.addExchageValue(currency1_id, currency2_id, exchage_value, date)
            self.fetchExchangeValues()
