import win32api
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Sales_Target import Ui_Sales_Target
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_Sales_Target_Logic(object):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_Sales_Target()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        dialog = QDialog()
        dialog.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(dialog)
        dialog.setWindowIcon(QIcon('icons/project.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, dialog)
        dialog.exec()

    def initialize(self):
        self.ui.targets_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.targets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.targets_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.targets_table.verticalHeader().hide()
        self.ui.targets_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.targets_table.setSortingEnabled(True)

        self.ui.target_input.setValidator(QIntValidator())
        self.ui.save_btn.clicked.connect(lambda: self.addSalesTarget())
        self.ui.delete_btn.clicked.connect(lambda: self.removeSalesTarget())

        self.ui.location_checkbox.clicked.connect(lambda: self.enableLocation())

        self.fetchSalesTargets()
        self.fetchGrouppedMaterials()
        self.setMonths()
        self.setYears()

    def addSalesTarget(self):
        product = self.ui.products_combobox.itemData(self.ui.products_combobox.currentIndex())[0]
        year = self.ui.year_combobox.itemText(self.ui.year_combobox.currentIndex())
        month =self.ui.month_combobox.itemText(self.ui.month_combobox.currentIndex())
        target = self.ui.target_input.text()
        location = ''

        if self.ui.location_checkbox.isChecked():
            location = self.ui.location_input.text()

        try:
            target=int(str(target))
            self.database_operations.addSalesTarget(product, year, month, location, target)
            self.fetchSalesTargets()
            self.ui.target_input.setText('')
            self.ui.location_input.setText('')

        except Exception as e:
            print(e)
            win32api.MessageBox(0, self.language_manager.translate("VALUE_IS_NOT_CORRECT"), self.language_manager.translate("ERROR"))

    def removeSalesTarget(self):
        table_row = self.ui.targets_table.item(self.ui.targets_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            id = table_row.text()
            self.database_operations.removeSalesTarget(id)
            self.fetchSalesTargets()
            self.ui.target_input.setText('')
            self.ui.location_input.setText('')

    def fetchSalesTargets(self):
        self.clearTable()
        targets = self.database_operations.fetchSalesTargets()
        for target in targets:
            id = target['id']
            year = target['year_col']
            month = target['month_col']
            location = target['location']
            target_value = target['target']
            product = target['product']

            numrow = self.ui.targets_table.rowCount()
            self.ui.targets_table.insertRow(numrow)
            self.ui.targets_table.setItem(numrow, 0, MyTableWidgetItem(str(id),int(id)))
            self.ui.targets_table.setItem(numrow, 1, QTableWidgetItem(str(product)))
            self.ui.targets_table.setItem(numrow, 2, MyTableWidgetItem(str(year),int(year)))
            self.ui.targets_table.setItem(numrow, 3, MyTableWidgetItem(str(month),int(month)))
            self.ui.targets_table.setItem(numrow, 4, QTableWidgetItem(str(location)))
            self.ui.targets_table.setItem(numrow, 5, MyTableWidgetItem(str(target_value),int(target_value)))

    def clearTable(self):
        self.ui.targets_table.setRowCount(0)

    def fetchGrouppedMaterials(self):
        materials = self.database_operations.fetchGrouppedMaterials()
        for material in materials:
            id = material['id']
            name = material['name']
            code = material['code']
            work_hours = material['work_hours']
            data = [id]
            self.ui.products_combobox.addItem(name, data)

    def setYears(self):
        for i in range(2000,3000):
            self.ui.year_combobox.addItem(str(i))

    def setMonths(self):
        for i in range(1,(12+1)):
            self.ui.month_combobox.addItem(str(i))

    def enableLocation(self):
        if self.ui.location_checkbox.isChecked():
            self.ui.location_input.setEnabled(True)
        else:
            self.ui.location_input.setEnabled(False)