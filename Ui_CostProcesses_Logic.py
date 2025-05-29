
import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAbstractItemView, QDialog, QTableWidgetItem, QHeaderView
from win32con import MB_OKCANCEL, IDCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Cost_Logic import Ui_Cost_Logic
from Ui_CostProcesses import Ui_CostProcesses
from Ui_CostViewEdit_Logic import Ui_CostViewEdit_Logic
from Ui_Export_Logic import Ui_Export_Logic


class Ui_CostProcesses_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.filemanager = filemanager
        self.ui = Ui_CostProcesses()

    def showUi(self):
        window_cost_processes = QDialog()
        self.ui.setupUi(window_cost_processes)
        self.initialize()
        window_cost_processes.exec()

    def initialize(self):
        self.ui.cost_processes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.cost_processes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)

        self.ui.cost_processes_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.cost_processes_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.cost_processes_table.verticalHeader().hide()
        self.ui.cost_processes_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.new_manu_btn.clicked.connect(lambda: self.openNewCostWindow())
        self.ui.delete_manu_btn.clicked.connect(lambda: self.removeCostOperations())
        self.ui.details_manu_btn.clicked.connect(lambda: self.openCostProcess())
        self.ui.export_btn.clicked.connect(lambda: self.openExportWindow())

        self.fetchCosts()


    def fetchCosts(self):
        self.ui.cost_processes_table.setRowCount(0)
        costs = self.database_operations.fetchAllCostProcesses()
        for cost in costs:
            process_id = cost[0]
            cost_date = cost[6]
            name = cost[13]
            name_en = cost[14]
            name_string = name + '/' + name_en

            numRows = self.ui.cost_processes_table.rowCount()
            self.ui.cost_processes_table.insertRow(numRows)
            # Add text to the row
            self.ui.cost_processes_table.setItem(numRows, 0, MyTableWidgetItem(str(process_id), id))
            self.ui.cost_processes_table.setItem(numRows, 1, QTableWidgetItem(str(cost_date)))
            self.ui.cost_processes_table.setItem(numRows, 2, QTableWidgetItem(str(name_string)))


    def openNewCostWindow(self):
        if self.sqlconnector != '' and self.sqlconnector.is_connected_to_database:
            Ui_cost_window = Ui_Cost_Logic(self.sqlconnector).showUi()
            self.ui.cost_processes_table.setRowCount(0)
            self.fetchCosts()
        else:
            pass

    def openCostProcess(self):
        table_row = self.ui.cost_processes_table.item(self.ui.cost_processes_table.currentRow(), 0)  # current row 1 not 0 !
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            Ui_CostViewEdit_Logic(self.sqlconnector, table_row.text()).showUi()
            self.ui.cost_processes_table.setRowCount(0)
            self.fetchCosts()

    def removeCostOperations(self):
        confirm = win32api.MessageBox(0, "حذف؟", " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.cost_processes_table.item(self.ui.cost_processes_table.currentRow(),
                                                       0)  # current row 1 not 0 !
            print(str(type(table_row)))
            if (str(type(table_row)) == "<class 'NoneType'>"):
                pass
            else:
                process_id = table_row.text()
                self.database_operations.removeCostProcess(process_id)
                self.ui.cost_processes_table.setRowCount(0)
                self.fetchCosts()

    def openExportWindow(self):
        Ui_Export_Logic(self.sqlconnector, self.filemanager).showUi()

