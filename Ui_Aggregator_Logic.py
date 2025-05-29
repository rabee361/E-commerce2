import win32api
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QHeaderView, QTableWidgetItem, QDialog
from win32con import MB_OKCANCEL, IDCANCEL
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Aggregator import Ui_Aggregator
from Ui_AggregatorResult_Logic import Ui_AggregatorResult_Logic


class Ui_Aggregator_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_Aggregator()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_aggregator = QDialog()
        window_aggregator.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_aggregator)
        window_aggregator.setWindowIcon(QIcon('icons/resources.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_aggregator)
        window_aggregator.exec()

    def initialize(self):
        self.ui.aggregator_items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.aggregator_items_table.verticalHeader().hide()
        self.ui.aggregator_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.aggregator_items_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.ui.aggregator_items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.aggregator_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.aggregator_items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.aggregator_items_table.setSortingEnabled(True)

        self.ui.target_input.setValidator(QIntValidator())

        self.ui.add_btn.clicked.connect(lambda: self.addAggregatorItem())

        self.ui.delete_btn.clicked.connect(lambda: self.removeAggregatorItem())
        self.ui.clear_btn.clicked.connect(lambda: self.clearAggregatorItems())
        self.ui.calc_btn.clicked.connect(lambda: self.showResult())

        self.fetchGrouppedMaterials()
        self.fetchAggregatorItems()

    def fetchGrouppedMaterials(self):
        groupped_materials = self.database_operations.fetchGrouppedMaterials()
        for groupped_material in groupped_materials:
            id = groupped_material['id'] 
            name = groupped_material['name']
            work_hours = groupped_material['work_hours']
            code = groupped_material['code']
            yearly_required = groupped_material['yearly_required']
            data = [id, work_hours, code, yearly_required]

            self.ui.products.addItem(name, data)

    def addAggregatorItem(self):
        target = self.ui.target_input.text()
        if not target.isdigit():
            target = 100
        else:
            if int(target)<=0:
                target = 100

        data = self.ui.products.itemData(self.ui.products.currentIndex())
        id = data[0]
        print("id=" + str(id))

        self.database_operations.addAggregatorItem(id, target)

        self.ui.target_input.setText('')
        self.fetchAggregatorItems()


    def fetchAggregatorItems(self):
        self.ui.aggregator_items_table.setRowCount(0)
        aggregator_items = self.database_operations.fetchAggregatorItems()
        for item in aggregator_items:
            id = item['id']
            product_id = item['material_id']
            target = item['ammount']
            product_name = item['material']
            product_code = item['code']
            numRows = self.ui.aggregator_items_table.rowCount()
            self.ui.aggregator_items_table.insertRow(numRows)
            # Add text to the row
            self.ui.aggregator_items_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.aggregator_items_table.setItem(numRows, 1, QTableWidgetItem(str(product_code)))
            self.ui.aggregator_items_table.setItem(numRows, 2, QTableWidgetItem(str(product_name)))
            self.ui.aggregator_items_table.setItem(numRows, 3, MyTableWidgetItem(str(target), target))

    def removeAggregatorItem(self):
        table_row = self.ui.aggregator_items_table.item(self.ui.aggregator_items_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            aggregator_item_id = table_row.text()
            self.database_operations.removeAggregatorItem(aggregator_item_id)
            self.ui.target_input.setText('')
            self.fetchAggregatorItems()

    def clearAggregatorItems(self):
        confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            self.database_operations.clearAggregatorItems()
            self.fetchAggregatorItems()

    def showResult(self):
        Ui_AggregatorResult_Logic(self.sqlconnector, self.filemanager).showUi()

