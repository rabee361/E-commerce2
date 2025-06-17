from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QHeaderView, QAbstractItemView, QTableWidgetItem, QDialog, QTreeWidgetItem

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Export_Logic import Ui_Export_Logic
from Ui_Manufacture_Logic import Ui_Manufacture_Logic
from Ui_UpdateManufacture_Logic import Ui_UpdateManufacture_Logic
from Ui_ManufactureProcesses import Ui_ManufactureProcesses
from LanguageManager import LanguageManager

class Ui_ManufactureProcesses_Logic(QDialog):
    def __init__(self, sqlconnector, filemanager, windows_manager=None):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.filemanager = filemanager
        self.ui = Ui_ManufactureProcesses()
        self.windows_manager = windows_manager
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_manufacture_processes = QDialog()
        window_manufacture_processes.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_manufacture_processes)
        self.language_manager.load_translated_ui(self.ui, window_manufacture_processes)
        self.initialize()
        window_manufacture_processes.setWindowIcon(QIcon('icons/hammer.png'))
        window_manufacture_processes.exec()

    def initialize(self):
        self.ui.manu_processes_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.manu_processes_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.manu_processes_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.ui.manu_processes_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.manu_processes_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.manu_processes_table.verticalHeader().hide()
        self.ui.manu_processes_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.add_new_manu_btn.clicked.connect(lambda: self.openNewManufactureWindow())
        self.ui.delete_manu_btn.clicked.connect(lambda: self.updateManufactureOperations())
        self.ui.manu_processes_table.itemDoubleClicked.connect(lambda: self.openManufactureProcess())
        self.ui.export_btn.clicked.connect(lambda: self.openExportWindow())

        self.ui.materials_tree.itemSelectionChanged.connect(self.fetchManufactureProcessOfSelectedMaterials)

        self.ui.manu_processes_table.itemSelectionChanged.connect(lambda: self.updateStateButton())

        self.fetchGroups()
        self.fetchMaterials()
        # self.fetchManufactures()

    def fetchManufactureProcessOfSelectedMaterials(self):
        # Set the custom delegate for the entire table
        self.ui.manu_processes_table.setRowCount(0)
        material = self.ui.materials_tree.currentItem()
        if material:
            if material.text(2) != '':
                material_id = material.text(2)
                manufactures = self.database_operations.fetchManufactureProcessesOfMaterial(material_id)
                for manufacture in manufactures:
                    id = manufacture['id']
                    pullout_date = manufacture['pullout_date']
                    date = manufacture['date_col']
                    expenses_type = manufacture['expenses_type']
                    material_pricing_method = manufacture['material_pricing_method']
                    currency = manufacture['currency']
                    expenses_cost = manufacture['expenses_cost']
                    machines_operation_cost = manufacture['machines_operation_cost']
                    salaries_cost = manufacture['salaries_cost']
                    mid_account = manufacture['mid_account']
                    account = manufacture['account']
                    composition_materials_cost = manufacture['composition_materials_cost']
                    quantity_unit_expenses = manufacture['quantity_unit_expenses']
                    expenses_distribution = manufacture['expenses_distribution']
                    state = manufacture['state_col']
                    factory_id = manufacture['factory_id']
                    ingredients_pullout_method = manufacture['ingredients_pullout_method']
                    ingredients_pullout_account = manufacture['ingredients_pullout_account']
                    
                    # Produced material details
                    quantity1 = manufacture['quantity1']
                    unit1 = manufacture['unit1']
                    quantity2 = manufacture['quantity2']
                    unit2 = manufacture['unit2']
                    quantity3 = manufacture['quantity3']
                    unit3 = manufacture['unit3']
                    working_hours = manufacture['working_hours']
                    batch = manufacture['batch']
                    material_name = manufacture['name']
                    unit1_name = manufacture['unit1_name']
                    unit2_name = manufacture['unit2_name']
                    unit3_name = manufacture['unit3_name']
                    currency_name = manufacture['currency_name']
                    account_name = manufacture['account_name']
                    mid_account_name = manufacture['mid_account_name']

                    if str(composition_materials_cost).lower() in ['', 'none']:
                        composition_materials_cost = 0
                    if str(expenses_cost).lower() in ['', 'none']:
                        expenses_cost = 0
                    if str(machines_operation_cost).lower() in ['', 'none']:
                        machines_operation_cost = 0
                    if str(salaries_cost).lower() in ['', 'none']:
                        salaries_cost = 0
                    total_cost = float(composition_materials_cost) + float(expenses_cost) + float(
                        machines_operation_cost) + float(salaries_cost)
                    numRows = self.ui.manu_processes_table.rowCount()
                    self.ui.manu_processes_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.manu_processes_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.manu_processes_table.setItem(numRows, 1, QTableWidgetItem(str(date)))
                    self.ui.manu_processes_table.setItem(numRows, 2, QTableWidgetItem(str(batch)))
                    self.ui.manu_processes_table.setItem(numRows, 3, MyTableWidgetItem(str(total_cost), float(total_cost)))
                    self.ui.manu_processes_table.setItem(numRows, 4, QTableWidgetItem(str(currency)))
                    self.ui.manu_processes_table.setItem(numRows, 5, QTableWidgetItem(str(currency_name)))
                    self.ui.manu_processes_table.setItem(numRows, 6, QTableWidgetItem(str(state)))

                    if str(state).lower() == 'cancelled':
                        for column in range(self.ui.manu_processes_table.columnCount()):
                            item = self.ui.manu_processes_table.item(numRows, column)
                            item.setBackground(QColor(255, 200, 200))
                    
                    if str(state).lower() == 'active':
                        for column in range(self.ui.manu_processes_table.columnCount()):
                            item = self.ui.manu_processes_table.item(numRows, column)
                            item.setBackground(QColor(255, 255, 255))

    def openNewManufactureWindow(self):
        Ui_Manufacture_Logic(self.sqlconnector).showUi()
        self.fetchManufactureProcessOfSelectedMaterials()

    def openManufactureProcess(self):
        table_row = self.ui.manu_processes_table.item(self.ui.manu_processes_table.currentRow(), 0)  # current row 1 not 0 !
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            manufacture_process_id = table_row.text()
            if manufacture_process_id:
                if self.windows_manager.checkIfWindowIsOpen(f'Manufacture_{manufacture_process_id}Window'):
                    self.windows_manager.raiseWindow(f'Manufacture_{manufacture_process_id}Window')
                else:
                    Ui_UpdateManufacture_Logic(self.sqlconnector, manufacture_process_id=manufacture_process_id,manufacture_process=manufacture_process_id).showUi()

    def updateManufactureOperations(self):
        table_row_id_item = self.ui.manu_processes_table.item(self.ui.manu_processes_table.currentRow(), 0)
        table_row_state_item = self.ui.manu_processes_table.item(self.ui.manu_processes_table.currentRow(), 6)

        if (str(type(table_row_id_item)) == "<class 'NoneType'>") or (
                str(type(table_row_state_item)) == "<class 'NoneType'>"):
            pass
        else:
            manufacture_process_id = table_row_id_item.text()
            manufacture_process_state = table_row_state_item.text()
            new_state = None
            if manufacture_process_id and manufacture_process_state:
                if manufacture_process_state == "active":
                    new_state = "cancelled"
                elif manufacture_process_state == "cancelled":
                    new_state = "active"
                if new_state:
                    self.database_operations.updateManufactureProcessState(manufacture_process_id, new_state)
                    self.fetchManufactureProcessOfSelectedMaterials()

    def openExportWindow(self):
        Ui_Export_Logic(self.sqlconnector, self.filemanager).showUi()

    def fetchGroups(self):
        self.ui.materials_tree.clear()
        groups = self.database_operations.fetchGroups()

        # Add the groups to the tree
        children_queue = []
        for group in groups:
            print(group)
            id = group['id']
            name = group['name']
            code = group['code']
            date = group['date_col']
            parent_id = group['parent_id']
            parent_name = group['parent_name']

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(name), '', '', str(id)])
                self.ui.materials_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.materials_tree.findItems(str(parent_id),Qt.MatchExactly | Qt.MatchRecursive, 3)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(3)

                        child_item = QTreeWidgetItem([str(name), '', '', str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(group)
        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                code = child[2]
                date = child[3]
                parent_id = child[4]
                parent_name = child[5]

                items_already_in_tree = self.ui.materials_tree.findItems(str(parent_id),Qt.MatchExactly | Qt.MatchRecursive, 3)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(3)

                        child_item = QTreeWidgetItem([str(name), '', '', str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)
                            print("DELETED")

        # Add "بدون مجموعة" group
        no_group_item = QTreeWidgetItem([self.language_manager.translate("NO_GROUP"), '', '', "no_group"])
        self.ui.materials_tree.addTopLevelItem(no_group_item)

    def fetchMaterials(self):
        # Get the materials and add each one to its appropriate group in tree
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material[0]
            code = material[1]
            name = material[2]
            group = material[3]

            title = str(code) + "-" + str(name)

            if not group:
                no_group_items = self.ui.materials_tree.findItems("بدون مجموعة", Qt.MatchExactly | Qt.MatchRecursive, 0)
                if no_group_items:
                    no_group_item = no_group_items[0]
                    material_item = QTreeWidgetItem(['', str(title), str(id), ''])
                    no_group_item.addChild(material_item)
            else:
                groups_already_in_tree = self.ui.materials_tree.findItems(str(group), Qt.MatchExactly | Qt.MatchRecursive, 3)
                # print("L=" + str(len(groups_already_in_tree)))
                if (len(groups_already_in_tree) > 0):  # Group already exists in tree, so append its child
                    group = groups_already_in_tree[0]  # only one would exist because we search using ID
                    material = QTreeWidgetItem(['', str(title), str(id), ''])
                    group.addChild(material)

    def updateStateButton(self):
        table_row_state_item = self.ui.manu_processes_table.item(self.ui.manu_processes_table.currentRow(), 6)
        if (str(type(table_row_state_item)) == "<class 'NoneType'>"):
            pass
        else:
            manufacture_process_state = table_row_state_item.text()
            if manufacture_process_state:
                if manufacture_process_state == "active":
                    self.ui.delete_manu_btn.setText(self.language_manager.translate("ACTIVATE_MANUFACTURE_PROCESS"))
                elif manufacture_process_state == "cancelled":
                    self.ui.delete_manu_btn.setText(self.language_manager.translate("ACTIVATE_MANUFACTURE_PROCESS"))

    # Update the color of the row after updating the state
    def updateRowColor(self, row, state):
        if state == "cancelled":
            for column in range(self.ui.manu_processes_table.columnCount()):
                item = self.ui.manu_processes_table.item(row, column)
                item.setBackground(QColor(255, 200, 200))
        else:
            pass
