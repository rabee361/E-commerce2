import win32api
from PyQt5.QtCore import Qt , QTranslator
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QTableWidgetItem, QAbstractItemView, QHeaderView , QMainWindow , QApplication, QPushButton
from win32con import IDYES, IDNO, MB_YESNO
import win32con

from Ui_Journal_Logic import Ui_Journal_Logic
from Ui_InventoryReport_Logic import Ui_InventoryReport_Logic
from Ui_QuantitiesReport_Logic import Ui_QuantitiesReport_Logic 
from Ui_ReOrderMaterialReport_Logic import Ui_ReOrderMaterialReport_Logic
from Ui_Value_Report_Logic import Ui_Value_Report_Logic
from Ui_MaterialMoveReport_Logic import Ui_MaterialMoveReport_Logic
from ToolbarManager import ToolbarManager
from Ui_Currencies_Logic import Ui_Currencies_Logic
from FileManager import FileManager
from SqliteConnector import SqliteConnector
from Importer import Importer
from Ui_DatabaseSettings_Logic import Ui_DatabaseSettings_Logic
from Ui_DatabaseBackupRestore_Logic import Ui_DatabaseBackupRestore_Logic

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_AddMaterialToWarehouse_Logic import Ui_AddMaterialToWarehouse_Logic 
from Ui_RemoveMaterialFromWarehouse_Logic import Ui_RemoveMaterialFromWarehouse_Logic 
from Ui_AddWarehouse_Logic import Ui_AddWarehouse_Logic
from Ui_EditMaterialInWarehouse_Logic import Ui_EditMaterialInWarehouse_Logic
from Ui_MaterialMove_Logic import Ui_MaterialMove_Logic
from Ui_Warehouses import Ui_Warehouses
from Ui_Users_Logic import Ui_Users_Logic
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_AuthenticateUser_Logic import Ui_AuthenticateUser_Logic
from PyQt5.QtGui import QColor, QFont, QIcon
from Ui_Select_Language_Logic import Ui_Select_Language_Logic
from LanguageManager import LanguageManager

from PyQt5.QtWidgets import QComboBox

class Ui_Warehouses_Logic(QDialog):
    def __init__(self, sql_connector='', warehouse_id=None, independent=False):
        super().__init__()
        self.sql_connector = sql_connector
        if self.sql_connector:
            self.database_operations = DatabaseOperations(sql_connector)
        self.window = QMainWindow()
        self.ui = Ui_Warehouses()
        self.filemanager = ''
        self.warehouse_id = warehouse_id
        self.current_user = ''
        self.toolbar_manager = ''
        self.windows_manager = ''
        self.independent = independent
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        self.ui.setupUi(self.window)
        self.window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.window.setWindowIcon(QIcon('icons/warehouse.png'))
        self.filemanager = FileManager()
        self.initialize()
        self.window.show()
        self.showToolBar()

        # Disable if independent before connecting to DB
        if self.independent:
            self.DisableAccountInputs()
            # self.ui.centralWidget.setEnabled(False)
        else:   
            self.toolbar_manager.hideToolBar()

    def initialize(self):
        self.language_manager.load_translated_ui(self.ui, self.window)

        self.float_point_precision = ''

        if self.sql_connector: # only fetch data if connected to DB
            self.fetchData()

        self.ui.warehouses_tree.hideColumn(2)
        self.ui.option_new.triggered.connect(lambda: self.createFile(self.window))
        self.ui.option_open.triggered.connect(lambda: self.openFile(self.window))
        self.ui.option_connect_to_database.triggered.connect(lambda: self.openDatabaseSettings())
        self.ui.account_combobox.setEnabled(False)
        self.ui.parent_combobox.setEnabled(False)
        self.ui.inventory_report_btn.clicked.connect(lambda: self.openInventoryReportWindow())
        self.ui.reorder_reports_btn.clicked.connect(lambda: self.openReORderReportWindow())
        self.ui.quantities_report_btn.clicked.connect(lambda: self.openQuantitesReportWindow())
        self.ui.material_movement_reports_btn.clicked.connect(lambda: self.openMaterialMoveReportWindow())
        self.ui.value_reports_btn.clicked.connect(lambda: self.openValueReportWindow())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())
        self.ui.add_warehouse_btn.clicked.connect(lambda: self.openAddWarehouseWindow())
        self.ui.delete_warehouse_btn.clicked.connect(lambda: self.removeWarehouse())
        self.ui.save_btn.clicked.connect(lambda: self.saveWarehouse())
        self.ui.add_material_btn.clicked.connect(lambda: self.openAddWarehouseMaterialWindow())
        self.ui.remove_material_btn.clicked.connect(lambda: self.openRemoveWarehouseMaterialWindow())
        self.ui.edit_material_quantity_btn.clicked.connect(lambda: self.openEditMaterialInWarehouseWindow())
        self.ui.move_material_btn.clicked.connect(lambda: self.openMaterialMoveWindow())
        self.ui.backup_option.triggered.connect(lambda: self.openDatabaseBackup())
        self.ui.option_users.triggered.connect(lambda: self.openUsersWindow())
        self.ui.option_select_language.triggered.connect(lambda: self.openSelectLanguageWindow())

        if self.warehouse_id:
            self.ui.add_warehouse_btn.hide()
            self.ui.groupBox_5.hide()
            self.fetchWarehouses(self.warehouse_id)
            # Select the item containing the selected warehouse
            items = self.ui.warehouses_tree.findItems(str(self.warehouse_id), Qt.MatchExactly | Qt.MatchRecursive, 2)
            if items:
                self.ui.warehouses_tree.setCurrentItem(items[0])
            self.fetchWarehouseMaterials()




    def closeAllWindows(self, event=None):
        if self.windows_manager.checkForOpenWindows(self.window) is False:
            if event:
                event.accept()
            else:
                return True
        else:
            pass

    def showToolBar(self):
        # Initialize toolbar manager with the main window
        self.toolbar_manager = ToolbarManager(self.windows_manager, self.current_user, self.ui)

        # Map action names to their handler methods
        action_handlers = {
            "new_file": lambda: self.createFile(self.window),
            "connect_database": lambda: self.openDatabaseSettings(),
            "open_file": lambda: self.openFile(self.window),
            "calculator": lambda: self.openCalculatorWindow(),
            "users": lambda: self.openUsersWindow(),
            "refresh": lambda: self.fetchData(),
            "backup": lambda: self.openDatabaseBackup(),
            "language": lambda: self.openSelectLanguageWindow(),
            "currencies": lambda: self.openCurrenciesWindow(),
            "journal_entry": lambda: self.openJournalWindow(),
        }   
        
        # Connect each action to its handler
        for action in self.toolbar_manager.actions:
            if action.objectName() in action_handlers:
                action.triggered.connect(action_handlers[action.objectName()])
        
        # Add toolbar to the main window
        self.window.addToolBar(self.toolbar_manager.toolbar)
        self.toolbar_manager.showToolBar(action_handlers)


    def openCurrenciesWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Currencies_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_DATABASE'), self.language_manager.translate( 'ERROR'))


    def openJournalWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            if self.windows_manager.checkIfWindowIsOpen('JournalWindow'):
                self.windows_manager.raiseWindow('JournalWindow')
            else:
                Ui_Journal_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate('ALERT_OPEN_FILE'), self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_SYSTEMMODAL)

    def openSelectLanguageWindow(self):
        Ui_Select_Language_Logic().showUi()
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.toolbar_manager.retranslateToolbar()


    def fetchFloatPointPrecision(self):
        self.float_point_precision = self.database_operations.fetchFloatPointValue()

    def fetchData(self):
        self.fetchFloatPointPrecision()
        self.ui.warehouses_tree.clicked.connect(lambda: self.fetchSelectedWarehouse())
        self.ui.warehouses_tree.clicked.connect(lambda: self.fetchWarehouseMaterials())
        self.fetchWarehouses()
        self.fetchUnits()
        self.fetchAccounts()

    def createFile(self, MainWindow):
        file = self.filemanager.createEmptyFile('db')
        print(file)
        if file != "":
            if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
                self.sql_connector.disconnectDatabase()
            self.sql_connector = SqliteConnector()
            self.sql_connector.connectToDatabase(file)
            self.database_operations = DatabaseOperations(self.sql_connector)
            self.current_user = Ui_AuthenticateUser_Logic(self.sql_connector).getCurrentUser()
            # self.database_operations.createOwner()
            # self.importer = Importer(self.sql_connector, self.filemanager)
            self.window.centralWidget().setEnabled(True)
            self.fetchData()
        else:
            print("No File.")

    def openFile(self, MainWindow):
        file = self.filemanager.openFile("db")
        if file != "":
            if (self.sql_connector != '' and self.sql_connector.is_connected_to_database):
                self.sql_connector.disconnectDatabase()
            self.sql_connector = SqliteConnector()
            self.sql_connector.connectToDatabase(file)
            self.database_operations = DatabaseOperations(self.sql_connector)
            self.current_user = Ui_AuthenticateUser_Logic(self.sql_connector).getCurrentUser()
            # self.database_operations.createOwner()
            self.importer = Importer(self.sql_connector, self.filemanager)
            self.window.centralWidget().setEnabled(True)
            self.fetchData()
        else:
            print("No File.")

    def openDatabaseSettings(self):
        db_setting_window = Ui_DatabaseSettings_Logic(self.filemanager)
        db_setting_window.showUi()
        mysql_connector = db_setting_window.getMysqlConnector()
        database_name = db_setting_window.getDatabsaeName()
        if mysql_connector.is_connected_to_database:
            if self.sql_connector != '':
                if self.sql_connector.is_connected_to_database:
                    self.sql_connector.disconnectDatabase()
            self.sql_connector = mysql_connector
            self.database_name = database_name
            self.database_operations = DatabaseOperations(self.sql_connector)
            self.current_user = Ui_AuthenticateUser_Logic(self.sql_connector).getCurrentUser()

            if not self.current_user:
                user = Ui_AuthenticateUser_Logic(self.sql_connector).showUi()
                if user:
                    self.current_user = user
                self.window.centralWidget().setEnabled(True) # edit this
            self.fetchData()

    def openDatabaseBackup(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database and str(
                type(self.sql_connector)) == "<class 'MysqlConnector.MysqlConnector'>":
            Ui_DatabaseBackupRestore_Logic(self.sql_connector, self.database_name, self.filemanager).showUi()
            self.openDatabaseSettings()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_DATABASE'), self.language_manager.translate( 'ERROR'))
 
    def openUsersWindow(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            Ui_Users_Logic(self.sql_connector).showUi()
        else:
            win32api.MessageBox(0, self.language_manager.translate( 'ALERT_OPEN_FILE'), self.language_manager.translate( 'ERROR'))


    def checkPermission(self,criteria, type_col):
        permission = self.database_operations.fetchUserPermission(criteria=criteria, user_id=self.current_user, type_col=type_col)
        return permission

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit['id']
            name = unit['name']
            self.ui.capacity_unit_combobox.addItem(name, id)

    def fetchWarehouses(self, selected_warehouse_id=None):
        self.ui.warehouses_tree.clear()
        warehouses = self.database_operations.fetchWarehouses()

        self.ui.parent_combobox.clear()
        self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)

        # Build warehouses tree
        children_queue = []
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            code = warehouse['code']
            parent_id = warehouse['parent_id']
            parent_name = warehouse['parent_name']
            include_in_stock = warehouse['include_in_stock']

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(code), str(name), str(id)])
                self.ui.warehouses_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.warehouses_tree.findItems(str(parent_id),
                                                                          Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(warehouse)

            # Add parent to parent combobox
            display_text = str(code) + "-" + str(name)
            data = id
            self.ui.parent_combobox.addItem(display_text, data)

        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                code = child[2]
                parent_id = child[3]
                # parent_name = child[4]

                items_already_in_tree = self.ui.warehouses_tree.findItems(str(parent_id),
                                                                          Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)

        if selected_warehouse_id:
            # Hide all top-level items except the one containing the selected warehouse
            for i in range(self.ui.warehouses_tree.topLevelItemCount()):
                top_item = self.ui.warehouses_tree.topLevelItem(i)
                if str(top_item.text(2)) != str(selected_warehouse_id):
                    top_item.setHidden(True)
                else:
                    top_item.setHidden(False)
                    top_item.setExpanded(True)

    def openInventoryReportWindow(self):
        Ui_InventoryReport_Logic.showUi()

    def openReORderReportWindow(self):
        Ui_ReOrderMaterialReport_Logic.showUi()

    def openValueReportWindow(self):
        Ui_Value_Report_Logic.showUi()

    def openQuantitesReportWindow(self):
        Ui_QuantitiesReport_Logic.showUi()

    def openMaterialMoveReportWindow(self):
        Ui_MaterialMoveReport_Logic.showUi()

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(result['id']))
        
    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        self.ui.account_combobox.addItem(self.language_manager.translate("NONE"), None)
        for account in accounts:
            id = account[0]
            name = account[1]
            code = account[2]
            display_text = code + "-" + name
            data = id
            self.ui.account_combobox.addItem(display_text, data)

    def openSelectParentWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def fetchSelectedWarehouse(self):
        warehouse_id = self.ui.warehouses_tree.currentItem().text(2)
        if warehouse_id:
            material = self.database_operations.fetchWarehouse(warehouse_id)
            id = material['id']
            code = material['code']
            name = material['name']
            include_in_stock = material['include_in_stock']
            date = material['date_col']
            parent_warehouse = material['parent_warehouse']
            address = material['address']
            account = material['account']
            account_name = material['account_name']
            manager = material['manager']
            notes = material['notes']
            capacity = material['capacity']
            capacity_unit = material['capacity_unit']

            if str(code).lower() == 'none':
                code = ''

            if str(account).lower() == 'none':
                account = ''
            if str(address).lower() == 'none':
                address = ''
            if str(manager).lower() == 'none':
                manager = ''
            if str(notes).lower() == 'none':
                notes = ''
            if str(capacity).lower() == 'none':
                capacity = ''

            self.ui.code_input.setText(str(code))
            self.ui.name_input.setText(str(name))
            self.ui.date_input.setText(str(date))
            self.ui.address_input.setText(str(address))
            self.ui.manager_input.setText(str(manager))
            self.ui.capacity_input.setText(str(capacity))
            self.ui.notes_input.setText(str(notes))
            self.ui.include_in_stock_checkbox.setChecked(include_in_stock)
            self.ui.capacity_unit_combobox.setCurrentIndex(self.ui.capacity_unit_combobox.findData(capacity_unit))
            
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(parent_warehouse))
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(account))


    def fetchWarehouseMaterials(self):
        warehouse = self.ui.warehouses_tree.currentItem()
        self.ui.materials_table.setRowCount(0)
        if warehouse:
            warehouse_id = warehouse.text(2)
            warehouse = self.database_operations.fetchWarehouse(warehouse_id)
            warehouse_capacity_unit = warehouse['capacity_unit']

            materials = self.database_operations.fetchWarehouseMaterials(warehouse_id)
            
            # Group materials by material_id
            grouped_materials = {}
            for material in materials:
                key = (material['material_id'], material['unit'])  # Group by material_id and unit
                if key not in grouped_materials:
                    grouped_materials[key] = {
                        'material_id': material['material_id'],
                        'code': material['code'],
                        'material_name': material['material_name'],
                        'unit': material['unit'],
                        'unit_name': material['unit_name'],
                        'total_quantity': 0,
                        'entries': []
                    }
                grouped_materials[key]['total_quantity'] += float(material['quantity'] or 0)
                grouped_materials[key]['entries'].append(material)

            # Add grouped rows to table
            for key, group in grouped_materials.items():
                numRows = self.ui.materials_table.rowCount()
                self.ui.materials_table.insertRow(numRows)

                # Create expand/collapse button
                expand_button = QPushButton("+")
                expand_button.setFixedWidth(20)
                expand_button.setStyleSheet("QPushButton { background-color: #e0e0e0; border: none; }")
                self.ui.materials_table.setCellWidget(numRows, 0, expand_button)

                # Add group summary row
                self.ui.materials_table.setItem(numRows, 1, QTableWidgetItem(str(group['code'])))
                self.ui.materials_table.setItem(numRows, 2, QTableWidgetItem(str(group['material_name'])))
                self.ui.materials_table.setItem(numRows, 3, MyTableWidgetItem(str(round(float(group['total_quantity']), int(self.float_point_precision))), float(group['total_quantity'])))
                self.ui.materials_table.setItem(numRows, 4, QTableWidgetItem(str(group['unit'])))
                self.ui.materials_table.setItem(numRows, 5, QTableWidgetItem(str(group['unit_name'])))
                self.ui.materials_table.setItem(numRows, 6, QTableWidgetItem(str(group['material_id'])))

                # Style the group row
                for col in range(self.ui.materials_table.columnCount()):
                    item = self.ui.materials_table.item(numRows, col)
                    if item:
                        item.setBackground(QColor(180, 200, 255))
                        font = item.font()
                        font.setBold(True)
                        item.setFont(font)

                # Store the detail rows data with the button
                expand_button.entries = group['entries']
                expand_button.parent_row = numRows
                expand_button.is_expanded = False
                expand_button.clicked.connect(lambda checked, btn=expand_button: self.toggleMaterialDetails(btn))

                # Check if units match or have a conversion path
                should_highlight = False
                if int(group['unit']) != warehouse_capacity_unit:
                    conversion_value = self.database_operations.fetchUnitConversionValueBetween(
                        int(group['unit']), warehouse_capacity_unit)
                    if conversion_value is None:
                        should_highlight = True

                if should_highlight:
                    for col in range(self.ui.materials_table.columnCount()):
                        item = self.ui.materials_table.item(numRows, col)
                        if item:
                            item.setBackground(QColor(255, 255, 0))

    def toggleMaterialDetails(self, button):
        if button.is_expanded:
            # Calculate the correct position of detail rows for this group
            offset = 0
            for row in range(0, button.parent_row):
                cell_widget = self.ui.materials_table.cellWidget(row + offset, 0)
                if isinstance(cell_widget, QPushButton) and cell_widget.is_expanded:
                    offset += len(cell_widget.entries)
                
            # Remove detail rows for this specific group
            start_row = button.parent_row + offset + 1
            for i in range(len(button.entries)):
                self.ui.materials_table.removeRow(start_row)
            
            button.setText("+")
            button.is_expanded = False
        else:
            # Calculate the correct insertion position by counting expanded rows before this button
            offset = 0
            for row in range(0, button.parent_row):
                cell_widget = self.ui.materials_table.cellWidget(row + offset, 0)
                if isinstance(cell_widget, QPushButton) and cell_widget.is_expanded:
                    offset += len(cell_widget.entries)
            
            # Insert detail rows at the correct position
            insert_position = button.parent_row + offset + 1
            for i, entry in enumerate(button.entries):
                self.ui.materials_table.insertRow(insert_position + i)
                
                # Add detail row data
                self.ui.materials_table.setItem(insert_position + i, 0, QTableWidgetItem(str(entry['id'])))
                self.ui.materials_table.setItem(insert_position + i, 1, QTableWidgetItem(str(entry['code'] or '')))
                self.ui.materials_table.setItem(insert_position + i, 2, QTableWidgetItem(str(entry['material_name'])))
                self.ui.materials_table.setItem(insert_position + i, 3, MyTableWidgetItem(str(round(float(entry['quantity']), int(self.float_point_precision))), float(entry['quantity'])))
                self.ui.materials_table.setItem(insert_position + i, 4, QTableWidgetItem(str(entry['unit'])))
                self.ui.materials_table.setItem(insert_position + i, 5, QTableWidgetItem(str(entry['unit_name'])))
                self.ui.materials_table.setItem(insert_position + i, 6, QTableWidgetItem(str(entry['material_id'])))
                self.ui.materials_table.setItem(insert_position + i, 7, QTableWidgetItem(str(entry['production_date'] or '')))
                self.ui.materials_table.setItem(insert_position + i, 8, QTableWidgetItem(str(entry['expire_date'] or '')))

                # Style detail rows
                for col in range(self.ui.materials_table.columnCount()):
                    item = self.ui.materials_table.item(insert_position + i, col)
                    if item:
                        item.setBackground(QColor(250, 250, 250))
                        item.setFont(QFont("Arial", 10))  # Slightly smaller font for details

            button.setText("-")
            button.is_expanded = True

    def openAddWarehouseWindow(self):
        Ui_AddWarehouse_Logic(self.sql_connector, independent=self.independent).showUi()
        self.ui.warehouses_tree.clear()
        self.fetchWarehouses()


    def openAddWarehouseMaterialWindow(self):
        try:
            warehouse_id = self.ui.warehouses_tree.currentItem().text(2)
        except:
            warehouse_id = False

        if warehouse_id:
            window = Ui_AddMaterialToWarehouse_Logic(self.sql_connector, warehouse_id)
            window.showUi()
            self.fetchWarehouseMaterials()

    def openRemoveWarehouseMaterialWindow(self):
        try:
            warehouse_entry_id = self.ui.materials_table.item(self.ui.materials_table.currentRow(), 0).text()
            warehouse_id = self.ui.warehouses_tree.currentItem().text(2)
        except:
            warehouse_entry_id = False
            warehouse_id = False

        if warehouse_entry_id and warehouse_id:
            window = Ui_RemoveMaterialFromWarehouse_Logic(self.sql_connector, warehouse_entry_id, warehouse_id)
            window.showUi()
            self.fetchWarehouseMaterials()

    def openEditMaterialInWarehouseWindow(self):
        try:
            warehouse_entry_id = self.ui.materials_table.item(self.ui.materials_table.currentRow(), 0).text()
            warehouse_id = self.ui.warehouses_tree.currentItem().text(2)
        except:
            warehouse_entry_id=False
            warehouse_id=False

        if warehouse_entry_id and warehouse_id:
            window = Ui_EditMaterialInWarehouse_Logic(self.sql_connector, warehouse_id, warehouse_entry_id)
            window.showUi()
            self.fetchWarehouseMaterials()

    def saveWarehouse(self):
        selected_warehouse = self.ui.warehouses_tree.currentItem()
        if (str(type(selected_warehouse)) == "<class 'NoneType'>"):
                pass
        else:
            warehouse_id = selected_warehouse.text(2)
            code = self.ui.code_input.text()
            name = self.ui.name_input.text()
            include_in_stock = True if self.ui.include_in_stock_checkbox.isChecked() else False
            address = self.ui.address_input.text()
            manager = self.ui.manager_input.text()
            capacity = self.ui.capacity_input.text()
            capacity_unit = self.ui.capacity_unit_combobox.currentData()
            notes = self.ui.notes_input.text()

            parent = self.ui.parent_combobox.currentData()
            account = self.ui.account_combobox.currentData()

            if not name or str(name.replace(" ", "")).lower() == '':
                win32api.MessageBox(0, self.language_manager.translate("NAME_CANNOT_BR_NONE"), self.language_manager.translate("ERROR"))
            elif str(parent) == str(warehouse_id):
                win32api.MessageBox(0, self.language_manager.translate("ALERT_CANNOT_SELECT_MAIN_WAREHOUSE"), self.language_manager.translate("ERROR"))
            else:
                if str(code).lower() == 'none':
                    code = ''
                if str(address).lower() == 'none':
                    address = ''
                if str(manager).lower() == 'none':
                    manager = ''
                if str(capacity).lower() == 'none':
                    capacity = ''
                if str(notes).lower() == 'none':
                    notes = ''
                if str(parent).lower() == 'none':
                    parent = ''
                if str(account).lower() == 'none':
                    account = ''
    
                warehouses = self.database_operations.fetchWarehouses()
                # Check if name already exists in warehouses
                for warehouse in warehouses:
                    if (warehouse['name'].lower() == name.lower() or warehouse['codename'].lower() == code.lower()) and str(warehouse['id']) != str(warehouse_id):
                        win32api.MessageBox(0, self.language_manager.translate("ALERT_WAREHOUSE_ALREADY_EXISTS"), self.language_manager.translate("ERROR")) 
                        return

                self.database_operations.updateWarehouse(warehouse_id, name, code, include_in_stock, address, manager, capacity, capacity_unit, notes,parent, account)
                self.fetchWarehouses()
                self.fetchWarehouseMaterials()

    def removeWarehouse(self):
        warehouse_id = self.ui.warehouses_tree.currentItem() # get the warehouse
        if warehouse_id:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("ALERT_REMOVE_WAREHOUSE"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                try:
                    self.database_operations.removeWarehouse(warehouse_id.text(2)) # get the warehouse id and pass it
                    if self.warehouse_id:
                        self.fetchWarehouses(self.warehouse_id)
                    else:
                        self.fetchWarehouses()
                    self.ui.materials_table.setRowCount(0)
                except Exception as e:
                    print(e)
                    win32api.MessageBox(0, self.language_manager.translate("ALERT_CANNOT_REMOVE_MAIN_WAREHOUSE"), self.language_manager.translate("ERROR"))
            if (messagebox_result == IDNO):
                pass

    def openMaterialMoveWindow(self):
        try:
            warehouse_id = self.ui.warehouses_tree.currentItem().text(2)
            warehouse_entry_id = self.ui.materials_table.item(self.ui.materials_table.currentRow(), 0).text()
            print(str(warehouse_entry_id))

        except:
            warehouse_id = None
            warehouse_entry_id = None

        if warehouse_id and warehouse_entry_id:
            window = Ui_MaterialMove_Logic(self.sql_connector, source_warehouse=warehouse_id, warehouse_entry=warehouse_entry_id, independent=self.independent)
            window.showUi()
            self.fetchWarehouseMaterials()


    def DisableAccountInputs(self):
        # Find and disable all comboboxes and buttons containing "account" in their name
        for widget in self.ui.__dict__.values():
            if isinstance(widget, (QComboBox, QPushButton)) and "account" in widget.objectName().lower():
                if isinstance(widget, QComboBox):
                    widget.clear()  # Clear the combobox items before disabling
                widget.setEnabled(False)




if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    hr_logic = Ui_Warehouses_Logic(independent=True)
    hr_logic.showUi()
    app.exec_()
