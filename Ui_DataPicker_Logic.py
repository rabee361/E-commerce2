import win32api
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QHeaderView, QTableWidgetItem, QGridLayout, QCheckBox
from win32con import MB_TASKMODAL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_DataPicker import Ui_DataPicker

class Ui_DataPicker_Logic(QDialog):
    '''
    # DataPicker

    A flexible UI component for selecting records from database tables with search functionality. Supports both single-table and parent-child (linked) table selections.

    ## Quick Start

    ### Parameters
    - sql_connector: Your database connection
    - table_name: Name of primary table
    - columns: Columns to display (optional)
    - linked_table: Related table name (optional)
    - linked_columns: Related table columns (optional)
    - include_none_option: Add "None" option (optional)
    - exclusions: IDs to exclude (optional)
    - only_include: IDs to include (optional)

    ### Return Value
    Returns either:
    - A list containing the selected record (when using single table)
    - A dictionary with:
      - primary: Selected main record
      - linked: Selected related record (when using linked tables)

    ## Features
    - Real-time search filtering
    - Sortable columns
    - Single/Linked table support
    - Data validation
    - Arabic interface

    ## Requirements
    - DatabaseOperations class with appropriate fetch methods
    - Ui_DataPicker.ui file with basic widgets
    '''
    def __init__(self, sql_connector, table_name=None, columns=None, linked_table=None, linked_columns=None, search_column=None, include_none_option=False, exclusions=None , only_include=None, group_materials_id=None, warehouse_id=None, client_id=None , client_type=None, criterias={}, default_id=None, checkable=False):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_DataPicker()
        self.selected_item = None
        self.selected_items = {}
        self.fetching_items_mapper = {}
        self.fetching_item_mapper = {}
        self.table_name = table_name if table_name else 'accounts'
        self.search_column = search_column
        self.search_column_index = 1
        self.include_none_option = include_none_option
        self.exclusions = exclusions if exclusions else []
        self.only_include = only_include if only_include else []
        self.default_id = default_id
        self.checkable = checkable 
        self.checkable_column_index = None

        # Column configurations - just simple lists of column names
        self.columns = columns if columns else ['id', 'name']
        if self.checkable and 'checkable' not in self.columns:
            self.columns.append('checkable')
        
        self.linked_columns = linked_columns if linked_columns else ['id', 'name']
        if self.checkable and 'checkable' not in self.linked_columns:
            self.linked_columns.append('checkable')

        # Linked table attributes
        self.linked_table = linked_table
        self.linked_items_dict = {}
        self.primary_selected_id = None
        self.items_dict = {}

        # Custom attributes
        self.warehouse_id = warehouse_id
        self.group_materials_id = group_materials_id
        self.client_id = client_id
        self.criterias = criterias
        self.client_type = client_type

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        window.exec()
        return self.selected_item

    def initialize(self, window):
        # Setup primary table
        self.setupTable(self.ui.result_table, self.columns)

        # Connect item clicked signal to handle checkbox clicks
        if self.checkable:
            self.ui.result_table.cellClicked.connect(self.handleCellClicked)

        self.ui.result_table.itemDoubleClicked.connect(lambda: self.setSelectedItem(window))

        if self.search_column:
            # Get index of search column (defaulting to 1 if not found)
            for i in range(self.ui.result_table.columnCount()):
                if self.ui.result_table.horizontalHeaderItem(i).text() == self.search_column:
                    self.search_column_index = i
                    break

        if self.linked_table:
            # Setup linked table
            self.setupTable(self.ui.linked_table, self.linked_columns)
            self.ui.result_table.itemSelectionChanged.connect(self.updateLinkedTable)
            # Connect primary table selection to update linked table
            self.ui.result_table.itemSelectionChanged.connect(self.updateLinkedTable)
            # Set result table width to half of dialog width
            self.ui.result_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
            self.ui.result_table.setMaximumWidth(window.width() // 3)
        else:
            # Hide linked table
            self.ui.linked_table.hide()

        # Link buttons with its respective function
        self.ui.save_btn.clicked.connect(lambda: self.setSelectedItem(window))
        self.ui.cancel_btn.clicked.connect(lambda: self.cancelProcess(window))

        # Link search bar with search function that triggers every time the text changes
        self.ui.search_input.textChanged.connect(lambda: self.searchItems())

        # Match table name parameter to its respective fetching function in DatabaseOperations file
        self.fetching_items_mapper = {
            'accounts': self.database_operations.fetchAccounts,
            'cost_centers': self.database_operations.fetchCostCenters,
            'clients': lambda: self.database_operations.fetchClients(self.client_type),
            'warehouses': self.database_operations.fetchWarehouses,
            'invoices': self.database_operations.fetchAllInvoices,
            'prices': self.database_operations.fetchPrices,
            'units': self.database_operations.fetchUnits,
            'currencies': self.database_operations.fetchCurrencies,
            'materials': self.database_operations.fetchMaterials,
            'groups': self.database_operations.fetchGroups,
            'invoice_types': self.database_operations.fetchInvoiceTypes,
            'financial_statements': self.database_operations.fetchFinancialStatements,
            'machines': self.database_operations.fetchMachines,
            'expenses_types': self.database_operations.fetchExpensesTypes,
            'groupped_materials': self.database_operations.fetchGrouppedMaterials,
            'raw_materials': self.database_operations.fetchRawMaterials,
            'current_employees': lambda: self.database_operations.fetchEmployees('current'),
            'warehouse_materials': lambda: self.database_operations.fetchWarehouseMaterials(self.warehouse_id),
            'materials_of_group': lambda: self.database_operations.fetchMaterialsOfGroup(self.group_materials_id),
            'groupped_materials_of_group': lambda: self.database_operations.fetchGrouppedMaterialsOfGroup(self.group_materials_id),
            'users': self.database_operations.fetchUsers,
            'compositions': lambda: self.database_operations.fetchMaterialCompositions(self.group_materials_id),
            'criteria': self.database_operations.fetchCriterias,
            'client_invoices': lambda: self.database_operations.fetchInvoicesValues(client_id=self.client_id),
            'normal_invoices': lambda: self.database_operations.fetchNormalInvoices(),
            'departments': lambda: self.database_operations.fetchDepartments(),
            'positions': lambda: self.database_operations.fetchPositions(),
        }

        # We will use this to check if the selected item still exists in database
        self.fetching_item_mapper = {
            'accounts': self.database_operations.fetchAccount,
            'cost_centers': self.database_operations.fetchCostCenter,
            'clients': self.database_operations.fetchClient,
            'warehouses': self.database_operations.fetchWarehouse,
            'invoices': self.database_operations.fetchInvoice,
            'invoice_items': self.database_operations.fetchInvoiceItem,
            'prices': self.database_operations.fetchPrice,
            'units': self.database_operations.fetchUnit,
            'currencies': self.database_operations.fetchCurrency,
            'materials': self.database_operations.fetchMaterial,
            'groups': self.database_operations.fetchGroup,
            'invoice_types': self.database_operations.fetchInvoiceType,
            'materials_of_group': self.database_operations.fetchMaterial,
            'financial_statements': self.database_operations.fetchFinancialStatement,
            'machines': self.database_operations.fetchMachine,
            'expenses_types': self.database_operations.fetchExpenseType,
            'groupped_materials': self.database_operations.fetchMaterial,
            'groupped_materials_of_group': self.database_operations.fetchMaterial,
            'raw_materials': self.database_operations.fetchRawMaterial,
            'current_employees': self.database_operations.fetchEmployee,
            'warehouse_materials': self.database_operations.fetchWarehouseEntry,
            'users': self.database_operations.fetchUser,
            'compositions': self.database_operations.fetchMaterialComposition,
            'criteria': self.database_operations.fetchCriteria,
            'client_invoices': self.database_operations.fetchInvoice,
            'normal_invoices': self.database_operations.fetchInvoice,
            'departments': self.database_operations.fetchDepartment,
            'positions': self.database_operations.fetchPosition,
        }

        self.fetching_linked_items_mapper = {
            ('invoices', 'invoice_items'): lambda invoice_id: self.database_operations.fetchInvoiceItems(invoice_id),
            # Add other linked table fetching methods as needed
        }

        self.fetchResults()

    def setupTable(self, table, columns):
        """Setup table with given columns"""
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setSelectionMode(QAbstractItemView.SingleSelection)
        table.verticalHeader().hide()
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSortingEnabled(True)

        # Set column count and headers
        table.setColumnCount(len(columns))
        table.setHorizontalHeaderLabels(columns)

        # Hide ID column (assuming first column is always ID)
        table.setColumnHidden(0, True)
        
        # If checkable is enabled, set up the checkable column
        if self.checkable and 'checkable' in columns:
            # Find the checkable column index
            self.checkable_column_index = columns.index('checkable')
            # Don't hide the checkable column
            table.setColumnHidden(self.checkable_column_index, False)

        # Stretch the name column (assuming second column is name)
        if len(columns) > 1:
            table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)

    def fetchResults(self):
        # Clear previous items
        self.ui.result_table.setRowCount(0)
        self.items_dict.clear()

        # Fetch data
        results = self.fetching_items_mapper[self.table_name]()

        if self.include_none_option:
            self.ui.result_table.insertRow(0)
            self.ui.result_table.setItem(0, 0, MyTableWidgetItem(str(-1), int(-1)))  # Because -1 does not exist in database as an ID
            self.ui.result_table.setItem(0, 1, QTableWidgetItem('لا يوجد'))

            # Save None Item
            self.items_dict[-1] = {'id': None, 'name': 'لا يوجد'}

        # Add data to the table
        for result in results:
            id = result['id']  # Assuming 'id' is always present

            include_this_item = True
            if id in self.exclusions:
                include_this_item = False


            if self.only_include:
                if id in self.only_include:
                    include_this_item = True
                else:
                    include_this_item = False


            if self.criterias:
                for criteria, value in self.criterias.items():
                    if result[criteria] != value:
                        include_this_item = False
                        break

            if include_this_item:
                # Create empty row
                numRows = self.ui.result_table.rowCount()
                self.ui.result_table.insertRow(numRows)

                # Add data for each column
                for col_idx, column in enumerate(self.columns):
                    # Handle checkable column specially since it doesn't exist in database
                    if self.checkable and column == 'checkable':
                        # Create a checkbox item
                        checkbox = QCheckBox()
                        checkbox.setChecked(False)
                        self.ui.result_table.setCellWidget(numRows, col_idx, checkbox)
                        self.checkable_column_index = col_idx
                    else:
                        # For other columns, get value from result
                        if column in result:
                            value = result[column]
                            
                            # Add "(default)" text to name column for default record
                            if self.default_id is not None and id == self.default_id and column == 'name':
                                value = f"{value} (default)"
                                
                            item = (MyTableWidgetItem(str(value), int(value))
                                   if column == 'id'
                                   else QTableWidgetItem(str(value)))

                            # Highlight default record
                            if self.default_id is not None and id == self.default_id:
                                item.setBackground(Qt.green)

                            self.ui.result_table.setItem(numRows, col_idx, item)

                # Save item
                self.items_dict[id] = result

    def searchItems(self):
        if self.linked_table:
            self.ui.result_table.clearSelection()
            self.ui.linked_table.setRowCount(0)

        search_text = self.ui.search_input.text()
        for row in range(self.ui.result_table.rowCount()):
            item = self.ui.result_table.item(row, self.search_column_index)
            if search_text.lower() in item.text().lower():
                self.ui.result_table.setRowHidden(row, False)
            else:
                self.ui.result_table.setRowHidden(row, True)

    def updateLinkedTable(self):
        if not self.linked_table:
            return

        current_row = self.ui.result_table.currentRow()
        if current_row >= 0:
            id_item = self.ui.result_table.item(current_row, 0)
            if id_item:
                primary_id = id_item.text()
                self.primary_selected_id = primary_id

                # Clear previous items
                self.ui.linked_table.setRowCount(0)
                self.linked_items_dict.clear()

                # Fetch and display linked items
                linked_results = self.fetching_linked_items_mapper[(self.table_name, self.linked_table)](primary_id)
                for result in linked_results:
                    id = result['id']  # Assuming 'id' is always present

                    # Create empty row
                    numRows = self.ui.linked_table.rowCount()
                    self.ui.linked_table.insertRow(numRows)

                    # Add data for each column
                    for col_idx, column in enumerate(self.linked_columns):
                        value = result[column]
                        item = (MyTableWidgetItem(str(value), int(value))
                               if column == 'id'
                               else QTableWidgetItem(str(value)))
                        self.ui.linked_table.setItem(numRows, col_idx, item)

                    # Save item
                    self.linked_items_dict[id] = result

    def setSelectedItem(self, window):
        if self.checkable and self.selected_items:
            # Return the dictionary of selected items when checkable is enabled
            # and at least one item is selected
            self.selected_item = self.selected_items
            window.accept()
        elif self.linked_table:
            # Existing linked table selection logic
            primary_row = self.ui.result_table.currentRow()
            linked_row = self.ui.linked_table.currentRow()

            if primary_row >= 0 and linked_row >= 0:
                primary_item = self.ui.result_table.item(primary_row, 0)
                linked_item = self.ui.linked_table.item(linked_row, 0)

                # Check if the selected item still exist in database
                primary_exists = self.fetching_item_mapper[self.table_name](primary_item.text())
                linked_exists = self.fetching_item_mapper[self.linked_table](linked_item.text())

                if not primary_exists or not linked_exists:
                    win32api.MessageBox(0, 'حصل تغيير ما في قاعدة البيانات،<|im_start|>رجى إعادة الاختيار.', "خطأ", MB_TASKMODAL)
                    self.fetchResults()
                    return
                else:
                    self.selected_item = {
                        'primary': self.items_dict[int(primary_item.text())],
                        'linked': self.linked_items_dict[int(linked_item.text())]
                    }
                    window.accept()
        else:
            # Existing single-table selection logic
            table_row = self.ui.result_table.item(self.ui.result_table.currentRow(), 0)

            if str(type(table_row)) == "<class 'NoneType'>":
                pass
            else:
                selected_item_id = table_row.text()
                if selected_item_id == str(-1):  # None option has been chosen
                    self.selected_item = self.items_dict[-1]
                    window.accept()
                else:
                    # Check if the selected item still exists in database
                    if self.table_name == 'warehouse_materials':
                        item = self.fetching_item_mapper[self.table_name](selected_item_id, self.warehouse_id)
                    else:
                        item = self.fetching_item_mapper[self.table_name](selected_item_id)
                    if item:    # Item exists
                        self.selected_item = self.items_dict[int(selected_item_id)]
                        window.accept()
                    else:
                        win32api.MessageBox(0, 'حصل تغيير ما في قاعدة البيانات،<|im_end|>رجى إعادة الاختيار.', "خطأ", MB_TASKMODAL)
                        self.fetchResults()

    def handleCellClicked(self, row, column):
        """Handle cell click to toggle checkbox state"""
        if self.checkable and column == self.checkable_column_index:
            # Get the checkbox widget
            checkbox = self.ui.result_table.cellWidget(row, column)
            if checkbox:
                # Toggle the checkbox state
                checkbox.setChecked(not checkbox.isChecked())
                
                # Get the item ID and name
                id_item = self.ui.result_table.item(row, 0)
                name_item = self.ui.result_table.item(row, 1)
                
                if id_item and name_item:
                    item_id = int(id_item.text())
                    item_name = name_item.text()
                    
                    # Add or remove from selected items based on checkbox state
                    if checkbox.isChecked():
                        self.selected_items[item_id] = {'id': item_id, 'name': item_name}
                    else:
                        if item_id in self.selected_items:
                            del self.selected_items[item_id]
    
    def cancelProcess(self, window):
        window.accept()
