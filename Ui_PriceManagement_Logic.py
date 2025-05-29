import win32api
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from PyQt5.QtCore import Qt , QTranslator
from win32con import MB_YESNO, IDYES, IDNO

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_PricesManagement import Ui_PricesManagement
from LanguageManager import LanguageManager

class Ui_PricesManagement_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_PricesManagement()
        self.changed_prices_rows=[]
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.ui.prices_table.hideColumn(0)
        self.ui.save_btn.clicked.connect(lambda: self.savePrices())
        self.ui.add_btn.clicked.connect(lambda: self.addPrice())
        self.ui.delete_btn.clicked.connect(lambda: self.deletePrice())
        self.fetchPrices()
        self.ui.prices_table.itemChanged.connect(lambda: self.changed_prices_rows.append(self.ui.prices_table.currentRow()))

    def fetchPrices(self):
        prices = self.database_operations.fetchPrices()
        for price in prices:
            id = price[0]
            price = price[1]

            # Create a empty row at bottom of table
            numRows = self.ui.prices_table.rowCount()
            self.ui.prices_table.insertRow(numRows)

            # Add text to the row
            self.ui.prices_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
            self.ui.prices_table.setItem(numRows, 1, QTableWidgetItem(str(price)))
        self.changed_prices_rows.clear() #whenever prices fetched, table.itemChanged() will be called, but with no cell selected. So,it adds an empty entry to the array. so we need to clear the array whenever items are fetched

    def addPrice(self):
        name = self.ui.name_input.text()
        if name and name.strip():
            self.database_operations.addPrice(name)
            self.ui.prices_table.setRowCount(0)
            self.fetchPrices()
            self.ui.name_input.clear()

    def savePrices(self):
        print(len(self.changed_prices_rows))
        if len(self.changed_prices_rows)>0:
            for changed_prices_row in self.changed_prices_rows:
                id=self.ui.prices_table.item(changed_prices_row, 0).text()
                new_price_name = self.ui.prices_table.item(changed_prices_row, 1).text()
                self.database_operations.updatePrice(id, new_price_name)
            self.ui.prices_table.setRowCount(0)
            self.fetchPrices()

    def deletePrice(self):
        if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
            table_row = self.ui.prices_table.item(self.ui.prices_table.currentRow(), 0)
            if (str(type(table_row)) == "<class 'NoneType'>"):
                pass
            else:
                messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"),  MB_YESNO)
                if(messagebox_result==IDYES):
                    price_id = table_row.text()
                    self.database_operations.deletePrice(price_id)
                    self.ui.prices_table.setRowCount(0)
                    self.fetchPrices()
                if(messagebox_result==IDNO):
                    pass

