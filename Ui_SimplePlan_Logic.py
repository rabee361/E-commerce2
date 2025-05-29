
import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView, QMessageBox
from win32con import MB_OKCANCEL, IDCANCEL

from PyQt5.QtCore import Qt
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_SimplePlan import Ui_SimplePlan
from Ui_SimplePlanResult_Logic import Ui_SimplePlanResult_Logic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QToolButton
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_SimplePlan_Logic(QDialog):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_SimplePlan()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_plan = QDialog()
        window_plan.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_plan)
        window_plan.setWindowIcon(QIcon('icons/graphic_report.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_plan)
        window_plan.exec()

    def initialize(self):
        self.ui.plan_items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.plan_items_table.verticalHeader().hide()
        self.ui.plan_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.plan_items_table.setSelectionMode(QAbstractItemView.SingleSelection)

        self.ui.plan_items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.plan_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.plan_items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.plan_items_table.setSortingEnabled(True)

        self.ui.batches_input.setValidator(QIntValidator())
        self.ui.products.setEnabled(False)

        self.ui.add_btn.clicked.connect(lambda: self.addPlanItem())
        self.ui.products_btn.clicked.connect(lambda: self.openSelectProduct())
        self.ui.plan_items_table.clicked.connect(lambda: self.rowSelected())
        self.ui.clear_btn.clicked.connect(lambda: self.clearPlanItems())
        self.ui.calc_btn.clicked.connect(lambda: self.showResult())

        self.fetchGrouppedMaterials()
        self.fetchSimplePlanItems()

    def openSelectProduct(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.products.count()):
                if self.ui.products.itemData(i)[0] == result['id']:
                    self.ui.products.setCurrentIndex(i)
                    break

    def addPlanItem(self):

        repeatition = self.ui.batches_input.text()
        if not repeatition or not repeatition.isdigit():
            repeatition = 0

        repeatition = int(repeatition)
        if repeatition <= 0:
            repeatition = 1


        data = self.ui.products.itemData(self.ui.products.currentIndex())
        id = data[0]

        last_priority = self.database_operations.fetchLastSimplePlanPriority()

        if last_priority:
            priority = last_priority + 1
        else:
            priority = 1

        print("id=" + str(id))
        i = 1
        while i <= repeatition:
            self.database_operations.addPlanItem(id , priority)
            priority = priority + 1
            i = i + 1
        self.fetchSimplePlanItems()

    def clearPlanItems(self):
        confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            self.database_operations.clearSimplePlanItems()
            self.fetchSimplePlanItems()

    def fetchGrouppedMaterials(self):
        groupped_materials = self.database_operations.fetchGrouppedMaterials()
        for material in groupped_materials:
            id = material['id']
            name = material['name'] 
            working_hours = material['work_hours']
            code = material['code']
            yearly_required = material['yearly_required']
            current_quantity = material['current_quantity']

            data = [id, working_hours, code, yearly_required, current_quantity]
            self.ui.products.addItem(name, data)

    def fetchSimplePlanItems(self):
        self.ui.plan_items_table.setRowCount(0)
        simple_plan_items = self.database_operations.fetchSimplePlanItems()
        for item in simple_plan_items:
            id = item[0]
            product_id = item[1]
            priority = item[2]
            product_name = item[4]
            product_code = item[5]
            numRows = self.ui.plan_items_table.rowCount()
            self.ui.plan_items_table.insertRow(numRows)
            # Add text to the row
            self.ui.plan_items_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.plan_items_table.setItem(numRows, 1, QTableWidgetItem(str(product_code)))
            self.ui.plan_items_table.setItem(numRows, 2, QTableWidgetItem(str(product_name)))
            self.add_priority_buttons(numRows , priority, id)  # Pass the id to the add_priority_buttons method
            self.add_delete_button(numRows , id)


    def add_delete_button(self, row: int, id: int):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        delete_btn = QToolButton()
        delete_btn.setText('❌')
        delete_btn.setFixedSize(20, 20)
        delete_btn.clicked.connect(lambda: self.removePlanItem(id))

        layout.addWidget(delete_btn)
        widget.setLayout(layout)

        self.ui.plan_items_table.setCellWidget(row, self.ui.plan_items_table.columnCount() - 1, widget)



    def add_priority_buttons(self, row: int, priority: int , id: int):
        widget = QWidget()
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        btn_up = QToolButton()
        btn_down = QToolButton()

        btn_up.setArrowType(Qt.UpArrow)
        btn_down.setArrowType(Qt.DownArrow)

        btn_up.setFixedSize(20, 20)
        btn_down.setFixedSize(20, 20)

        btn_up.clicked.connect(lambda: self.move_row(row, -1 ,priority, id))  # Move up
        btn_down.clicked.connect(lambda: self.move_row(row, 1 ,priority, id))  # Move down

        layout.addWidget(btn_up)
        layout.addWidget(btn_down)
        widget.setLayout(layout)

        self.ui.plan_items_table.setCellWidget(row, self.ui.plan_items_table.columnCount() - 2, widget)


    def move_row(self, row: int, direction: int, priority: int, id: int):
        self.database_operations.updateSimplaPlanItemPriority(id, priority+direction)
        target_row = row + direction
        if target_row < 0 or target_row >= self.ui.plan_items_table.rowCount():
            pass
        else:   
            target_row = self.ui.plan_items_table.item(target_row, 0)
            if target_row:
                target_id = target_row.text()
                self.database_operations.updateSimplaPlanItemPriority(target_id, priority)
                self.database_operations.updateSimplaPlanItemPriority(id, priority+direction)
                self.fetchSimplePlanItems()

    def rowSelected(self):
        table_row = self.ui.plan_items_table.item(self.ui.plan_items_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            plan_item_id = table_row.text()
            priority = self.database_operations.fetchSimplePlanPriority(plan_item_id)

    def savePriority(self):
        plan_item_id = self.ui.plan_items_table.item(self.ui.plan_items_table.currentRow(), 0).text()
        priority = 999999 # for now
        self.database_operations.updateSimplaPlanItemPriority(plan_item_id, priority)
        self.fetchSimplePlanItems()

    def removePlanItem(self ,id):
        self.database_operations.removeSimplePlanItem(id)
        self.fetchSimplePlanItems()

    def showResult(self):
        Ui_SimplePlanResult_Logic(self.sqlconnector, self.filemanager).showUi()


