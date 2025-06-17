import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIntValidator, QDoubleValidator, QIcon
from PyQt5.QtWidgets import QAbstractItemView, QTableWidgetItem, QHeaderView, QDialog
from win32con import IDCANCEL, MB_OKCANCEL
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_PlanPercent import Ui_PlanPercent
from Ui_PlanPercentResult_Logic import Ui_PlanPercentResult_Logic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTableWidgetItem, QWidget, QHBoxLayout
from PyQt5.QtWidgets import QToolButton
from Ui_DataPicker_Logic import Ui_DataPicker_Logic

class Ui_PlanPercent_Logic(QDialog):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_PlanPercent()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_plan_percent = QDialog()
        window_plan_percent.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_plan_percent)
        window_plan_percent.setWindowIcon(QIcon('icons/project_stats.png'))
        self.language_manager.load_translated_ui(self.ui, window_plan_percent)
        self.initialize()
        window_plan_percent.exec()

    def initialize(self):
        self.ui.plan_percent_items_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.plan_percent_items_table.verticalHeader().hide()
        self.ui.plan_percent_items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.plan_percent_items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.plan_percent_items_table.setSortingEnabled(True)
        self.ui.plan_percent_items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.batches_input.setValidator(QIntValidator())
        self.ui.products.setEnabled(False)
        self.ui.percent_input.setMinimum(0)
        self.ui.percent_input.setMaximum(100)

        self.ui.add_btn.clicked.connect(lambda: self.addPlanItem())
        self.ui.products_btn.clicked.connect(lambda: self.openSelectProduct())
        # self.ui.priority_btn.clicked.connect(lambda: self.savePriorityAndPercent())
        self.ui.calc_btn.clicked.connect(lambda: self.showResult())
        # self.ui.delete_btn.clicked.connect(lambda: self.removePlanPercentItem())
        self.ui.clear_btn.clicked.connect(lambda: self.clearPlanPercentItems())
        self.ui.plan_percent_items_table.clicked.connect(lambda: self.rowSelected())

        self.fetchProducts()
        self.fetchPlanPercentItems()

    def openSelectProduct(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.products.count()):
                if self.ui.products.itemData(i)[0] == result['id']:
                    self.ui.products.setCurrentIndex(i)
                    break

    def fetchProducts(self):
        materials = self.database_operations.fetchGrouppedMaterials()
        for material in materials:
            id = material['id']
            name = material['name'] 
            work_hours = material['work_hours']
            code = material['code']
            year_required = material['yearly_required']
            current_quantity = material['current_quantity']
            data = [id, work_hours, code, year_required, current_quantity]
            self.ui.products.addItem(name, data)

    def addPlanItem(self):
        last_priority = self.database_operations.fetchLastPercentPlanPriority()
        if last_priority:
            priority = last_priority + 1
        else:
            priority = 1

        percent = self.ui.percent_input.value()
        if not percent:
            win32api.MessageBox(0, self.language_manager.translate("PLAN_PERCENT_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))
            return

        data = self.ui.products.itemData(self.ui.products.currentIndex())
        id = data[0]
        print("id=" + str(id))

        self.database_operations.addPlanPercentItem(id, priority, percent)

        self.ui.percent_input.setValue(00.0)
        self.ui.target_input.setText('')
        self.fetchPlanPercentItems()

    def fetchPlanPercentItems(self):
        self.ui.plan_percent_items_table.setRowCount(0)
        plan_percent_items = self.database_operations.fetchPlanPercentItems()
        total_percent = 0.00
        
        for item in plan_percent_items:
            id = item[0]
            product_id = item[1]
            priority = item[2]
            percent = item[3]
            product_name = item[4]
            product_code = item[5]
            numRows = self.ui.plan_percent_items_table.rowCount()
            self.ui.plan_percent_items_table.insertRow(numRows)

            # Add text to the current row (numRows was already incremented above)
            self.ui.plan_percent_items_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.plan_percent_items_table.setItem(numRows, 1, QTableWidgetItem(str(product_code)))
            self.ui.plan_percent_items_table.setItem(numRows, 2, QTableWidgetItem(str(product_name)))
            self.ui.plan_percent_items_table.setItem(numRows, 3, MyTableWidgetItem(str("%" + str(percent)),percent))
            # self.ui.plan_percent_items_table.setItem(numRows, 5, QTableWidgetItem("test"))  # Extra empty field
            self.add_priority_buttons(numRows , priority, id)  # Pass the id to the add_priority_buttons method
            self.add_delete_button(numRows , id)
            total_percent += percent
            
        # Set validator to limit percent input to max 100
        self.ui.percent_input.setMaximum(100-float(total_percent))
        # self.ui.percent_input.setValidator(validator)



    def add_delete_button(self, row: int, id: int):
            widget = QWidget()
            layout = QHBoxLayout()
            layout.setContentsMargins(0, 0, 0, 0)

            delete_btn = QToolButton()
            delete_btn.setText('❌')
            delete_btn.setFixedSize(20, 20)
            delete_btn.clicked.connect(lambda: self.removePlanPercentItem(id))

            layout.addWidget(delete_btn)
            widget.setLayout(layout)

            self.ui.plan_percent_items_table.setCellWidget(row, self.ui.plan_percent_items_table.columnCount() - 1, widget)




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

            self.ui.plan_percent_items_table.setCellWidget(row, self.ui.plan_percent_items_table.columnCount() - 2, widget)


    def move_row(self, row: int, direction: int, priority: int, id: int):
        self.database_operations.updatePlanPercentItemPriority(id, priority+direction)
        target_row = row + direction
        if target_row < 0 or target_row >= self.ui.plan_percent_items_table.rowCount():
            pass
        else:   
            target_row = self.ui.plan_percent_items_table.item(target_row, 0)
            if target_row:
                target_id = target_row.text()
                self.database_operations.updatePlanPercentItemPriority(target_id, priority)
                self.database_operations.updatePlanPercentItemPriority(id, priority+direction)
                self.fetchPlanPercentItems()

    def rowSelected(self):
        table_row = self.ui.plan_percent_items_table.item(self.ui.plan_percent_items_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            plan_item_id = table_row.text()
            priority = self.database_operations.fetchPlanPercentPriority(plan_item_id)
            percent = self.database_operations.fetchPlanPercentPercent(plan_item_id)
            self.ui.percent_input.setValue(percent)

    def savePriorityAndPercent(self):
        table_row = self.ui.plan_percent_items_table.item(self.ui.plan_percent_items_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            plan_item_id = table_row.text()
            priority = self.ui.priority_input.text()
            if not priority.isdigit():
                priority = 999999
            self.database_operations.updatePlanPercentItemPriority(plan_item_id, priority)

            percent = self.ui.percent_input.text()
            if not float(percent):
                percent = 100
            percent.replace("%", "")
            self.database_operations.updatePlanPercentItemPercent(plan_item_id, percent)

            self.fetchPlanPercentItems()

    def removePlanPercentItem(self ,id):
        self.database_operations.removePlanPercentItem(id)
        self.ui.percent_input.setValue(00.0)
        self.ui.target_input.setText('')
        self.fetchPlanPercentItems()

    def clearPlanPercentItems(self):
        confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            self.database_operations.clearPlanPercentItems()
            # self.ui.priority_input.setText('')
            self.ui.percent_input.setValue(00.0)
            self.ui.target_input.setText('')
            self.fetchPlanPercentItems()

    def showResult(self):
        target = self.ui.target_input.text()
        if not target.isdigit():
            target = 100
        if int(target) <= 0:
            target = 100
        print(str(target))
        Ui_PlanPercentResult_Logic(self.sqlconnector, self.filemanager, target).showUi()

