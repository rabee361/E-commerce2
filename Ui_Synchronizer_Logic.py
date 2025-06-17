import mysql.connector
import win32api, win32con
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QTranslator  
from LanguageManager import LanguageManager
from Ui_Synchronizer import Ui_Synchronizer
from DatabaseOperations import DatabaseOperations
from SynchronizerHelper import SynchronizerHelper


class Ui_Synchronizer_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.synchronizer_helper = SynchronizerHelper(self.database_operations)
        self.ui = Ui_Synchronizer()
        self.factory_database_name = "eps_factory_db"
        self.connection_settings_modified = False
        self.factory_connection = ''
        self.factory_cursor = ''
        self.accountant_cursor = self.sql_connector.conn.cursor()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)    

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.connect_to_factory_btn.clicked.connect(lambda: self.connectToFactoryDatabase())
        self.ui.sync_btn.clicked.connect(lambda: self.sync())
        self.ui.server_input.textEdited.connect(self.markSettingsModified)
        self.ui.username_input.textEdited.connect(self.markSettingsModified)
        self.ui.port_input.textEdited.connect(self.markSettingsModified)
        self.ui.password_input.textEdited.connect(self.markSettingsModified)
        
        # Set up checkbox dependencies
        # self.setupCheckboxDependencies()
        
        self.loadSettings()
        self.connectToFactoryDatabase()

    def setupCheckboxDependencies(self):
        """Set up dependencies between checkboxes"""
        # Define dependencies map: checkbox -> dependencies
        self.dependencies = {
            self.ui.sync_materials_checkBox: [
                self.ui.sync_materials_groups_checkBox
            ],
            self.ui.sync_groupped_materials_checkBox: [
                self.ui.sync_materials_checkBox,
                self.ui.sync_units_checkBox
            ],
            self.ui.sync_machines_checkbox: [
                self.ui.sync_units_checkBox
            ],
            self.ui.sync_purchase_invoices_checkBox: [
                self.ui.sync_warehouseslist_checkBox,
                self.ui.sync_currencies_checkBox,
                self.ui.sync_units_checkBox,
            ],
            self.ui.sync_receipt_docs_checkbox: [
                self.ui.sync_materials_checkBox,
                self.ui.sync_units_checkBox,
                self.ui.sync_warehouseslist_checkBox
            ],
            self.ui.sync_manufacture_checkbox: [
                self.ui.sync_materials_groups_checkBox,
                self.ui.sync_materials_checkBox,
                self.ui.sync_groupped_materials_checkBox,
                self.ui.sync_units_checkBox,
                self.ui.sync_currencies_checkBox,
                self.ui.sync_machines_checkbox,
                self.ui.sync_warehouseslist_checkBox,
                self.ui.sync_purchase_invoices_checkBox
            ],
            self.ui.sync_warehouses_content_checkBox: [
                self.ui.sync_warehouseslist_checkBox,
                self.ui.sync_materials_checkBox,
                self.ui.sync_units_checkBox,
                self.ui.sync_receipt_docs_checkbox,
                self.ui.sync_manufacture_checkbox
            ],
            self.ui.sync_moves_checkbox: [
                # self.ui.sync_warehouses_content_checkBox,
                # self.ui.sync_units_checkBox,
                # self.ui.sync_receipt_docs_checkbox
            ]
        }
        
        # Define reverse dependencies map: dependency -> dependent checkboxes
        self.reverse_dependencies = {}
        for parent, deps in self.dependencies.items():
            for dep in deps:
                if dep not in self.reverse_dependencies:
                    self.reverse_dependencies[dep] = []
                self.reverse_dependencies[dep].append(parent)
        
        # Connect parent checkboxes to ensure dependencies are checked
        for parent, deps in self.dependencies.items():
            parent.stateChanged.connect(self.handleParentCheckboxChange)
        
        # Connect dependency checkboxes to uncheck dependent checkboxes when unchecked
        for dep in self.reverse_dependencies:
            dep.stateChanged.connect(self.handleDependencyCheckboxChange)

    def handleParentCheckboxChange(self, state):
        """Handle changes to parent checkboxes that have dependencies"""
        if state == 2:  # Checked
            parent = self.sender()
            if parent in self.dependencies:
                # Check all dependencies
                for dep in self.dependencies[parent]:
                    dep.setChecked(True)
    
    def handleDependencyCheckboxChange(self, state):
        """Handle changes to dependency checkboxes"""
        if state == 0:  # Unchecked
            dependency = self.sender()
            if dependency in self.reverse_dependencies:
                # Uncheck all dependent parent checkboxes
                for parent in self.reverse_dependencies[dependency]:
                    parent.setChecked(False)
    
    def validateCheckboxDependencies(self):
        """
        Validate that all checkbox dependencies are properly set.
        Returns True if all dependencies are met, False otherwise.
        """
        for parent, deps in self.dependencies.items():
            if parent.isChecked():
                missing_deps = [dep for dep in deps if not dep.isChecked()]
                if missing_deps:
                    # Get the names of the missing dependencies
                    parent_name = parent.text()
                    dep_names = [dep.text() for dep in missing_deps]
                    
                    message = f"{parent_name} {self.language_manager.translate('SYNC_DEPENDENCY_ERROR')}:\n- " + "\n- ".join(dep_names)
                    win32api.MessageBox(None, message, self.language_manager.translate('ERROR'), win32con.MB_OK | win32con.MB_ICONERROR)
                    return False
        
        return True

    def markSettingsModified(self):
        print("Settings modified.")
        self.connection_settings_modified = True

    def loadSettings(self):
        settings = {
            "factory_server": self.database_operations.fetchSetting("factory_server"),
            "factory_username": self.database_operations.fetchSetting("factory_username"),
            "factory_port": self.database_operations.fetchSetting("factory_port"),
            "factory_password": self.database_operations.fetchSetting("factory_password")
        }

        self.ui.server_input.setText(settings["factory_server"])
        self.ui.username_input.setText(settings["factory_username"])
        self.ui.port_input.setText(settings["factory_port"])
        self.ui.password_input.setText(settings["factory_password"])

    def saveSettings(self):
        server = self.ui.server_input.text()
        username = self.ui.username_input.text()
        port = self.ui.port_input.text()
        password = self.ui.password_input.text()  # Assuming there's a password input in the UI

        factory_database_defaults = {"factory_server": server, "factory_port": port, "factory_username": username,
                                     "factory_password": password}

        for key, value in factory_database_defaults.items():
            self.database_operations.saveSetting(key, value)

    def connectToFactoryDatabase(self):
        if self.connection_settings_modified:
            self.saveSettings()
        server = self.ui.server_input.text()
        username = self.ui.username_input.text()
        port = self.ui.port_input.text()
        password = self.ui.password_input.text()  # Assuming there's a password input in the UI

        try:
            factory_connection = mysql.connector.connect(host=server, port=port, user=username, password=password, database=self.factory_database_name)
            if factory_connection.is_connected():
                print("Connection to factory the database successful.")
                self.ui.connection_status_indicator.setStyleSheet("background-color:green; border-radius: 7px;")
                self.ui.connection_status_label.setText(self.language_manager.translate("CONNECTED"))
                self.factory_connection = factory_connection
                self.factory_cursor = self.factory_connection.cursor()
        except mysql.connector.Error as e:
            print(f"Failed to factory connect to the database: {e}")
            self.ui.connection_status_indicator.setStyleSheet("background-color:red; border-radius: 7px;")
            self.ui.connection_status_label.setText(self.language_manager.translate("NOT_CONNECTED"))

    def sync(self):

        # Begin a transaction for the accountant database
        self.accountant_cursor.execute("START TRANSACTION")
        if self.factory_connection and self.factory_connection.is_connected():
            self.factory_cursor.execute("START TRANSACTION")
        
        # try:
        # Validate checkbox dependencies before synchronizing
        # if not self.validateCheckboxDependencies():
        #     raise Exception("Checkbox dependencies not valid.")
        
        ################################################################################################################################################## FUNCTIONS# ####################################################
        #########################################################################################################

        def transfer_data_between_tables(table1_info, table2_info, columns_pairs, conditional_indexes=None, fks=None, result=None, additional_columns=None):
            """
            Transfers data from one table to another based on specified column mappings.
            Inserts new records if they don't exist and updates existing records with latest data.
            
            Parameters:
            -----------
            table1_info : tuple
                A tuple containing the name of the first table and its target database ('factory' or 'accountant') or a query and its target database.
                Example: ('suppliers', 'factory') or ('SELECT * FROM suppliers', 'factory')
            
            table2_info : tuple
                A tuple containing the name of the second table and its target database ('factory' or 'accountant').
                Example: ('clients', 'accountant')
            
            columns_pairs : dict
                A dictionary mapping columns in the first table to columns in the second table.
                Each key-value pair indicates the column in the first table and its corresponding column in the second table.
                Example: {'table1_name': 'table2_name', 'table1_phone1': 'table2_phone1'}
            
            conditional_indexes : list, optional
                A list of indexes of the column pairs in columns_pairs to check for existence before inserting.
                Example: [0, 1]
            
            fks : list, optional
                A list of foreign key transformations. Each transformation is a list containing:
                - fk_index: Index of the foreign key in the columns_pairs parameter.
                - ref_table_origin: Name of the reference table in the origin database.
                - ref_table_dest: Name of the reference table in the destination database.
                - ref_col_origin_dest: List containing the reference column in the origin and destination tables.
                - match_col_origin_dest: List containing the matching column (comparison columns) in the origin and destination tables.
                - copy_missing_fks: Boolean indicating whether to copy missing foreign keys.
                - fk_additional_cols: Optional list of additional columns mapping to copy from source table to destination table
            
            result : list, optional
                If None, the function will return the IDs of the inserted (or already found) rows in the destination table.
                If a list, the function will return the values of the specified columns of table1 for the queries that were executed.
            
            additional_columns : dict, optional
                A dictionary where keys are column names in the destination table and values are the values to be inserted.
                These values are added to every row inserted into the destination table.

            Returns:
            --------
            Tuple
                A tuple containing a list of IDs of the inserted (or already found) rows in the destination table, or a list of values of the specified columns of table1 for the queries that were executed, and a boolean indicating if the row was inserted or not (updated).
            """
            table1_query, table1_cursor = table1_info
            if "SELECT" in table1_query.upper():
                fetch_query = f"SELECT {', '.join(columns_pairs.keys())} FROM ({table1_query}) AS subquery"
            else:
                fetch_query = f"SELECT {', '.join(columns_pairs.keys())} FROM {table1_query}"

            table2_name, table2_cursor = table2_info

            # Fetch data from table1
            rows = executeQuery(table1_cursor, fetch_query)

            # Prepare the SQL query to insert data into table2
            columns_table2 = []
            placeholders = []
            for key, value in columns_pairs.items():
                if isinstance(value, str):
                    columns_table2.append(value)
                    placeholders.append('%s')
                elif isinstance(value, list):
                    columns_table2.extend(value)
                    placeholders.extend(['%s'] * len(value))

            # Add additional columns if provided
            if additional_columns:
                for col_name in additional_columns.keys():
                    columns_table2.append(col_name)
                    placeholders.append('%s')

            columns_table2_str = ', '.join(columns_table2)
            placeholders_str = ', '.join(placeholders)
            insert_query = f"INSERT INTO `{table2_name}` ({columns_table2_str}) VALUES ({placeholders_str})"

            # Check if the row already exists in table2 based on the conditional columns
            if conditional_indexes:
                check_conditions = " AND ".join(
                    [f"{columns_table2[index]} = %s" for index in conditional_indexes])
                check_query = f"SELECT EXISTS(SELECT 1 FROM `{table2_name}` WHERE {check_conditions})"

            # Initialize result list if result is expected to be returned
            result_data = []

            # Adjust fk indices based on repeat_count
            if fks:
                for fk in fks:
                    fk_index = fk[0]
                    for index, key in enumerate(columns_pairs.keys()):
                        if isinstance(columns_pairs[key], list) and fk_index > index:
                            repeat_count = len(columns_pairs[key])
                            fk[0] += repeat_count - 1
                            
            # Insert or update each row fetched from table1
            for row in rows:
                if conditional_indexes:
                    # Transform any foreign key values that are used in conditional checks
                    transformed_check_values = list(row)
                    
                    if fks:
                        for fk in fks:
                            fk_index = fk[0]
                            # Only transform if this FK is used in conditional indexes
                            if fk_index in conditional_indexes:
                                ref_table_origin, ref_table_dest = fk[1], fk[2]
                                ref_col_origin_dest, match_col_origin_dest = fk[3], fk[4]
                                
                                origin_value = row[fk_index]
                                # Fetch matching value from origin
                                fetch_fk_origin_query = f"SELECT {match_col_origin_dest[0]} FROM `{ref_table_origin}` WHERE {ref_col_origin_dest[0]} = %s"
                                match_value_origin = executeQuery(table1_cursor, fetch_fk_origin_query, (origin_value,))
                                
                                if match_value_origin:
                                    match_value_origin = match_value_origin[0][0]
                                    # Fetch corresponding value from destination
                                    fetch_fk_dest_query = f"SELECT {ref_col_origin_dest[1]} FROM `{ref_table_dest}` WHERE {match_col_origin_dest[1]} = %s"
                                    dest_results = executeQuery(table2_cursor, fetch_fk_dest_query, (match_value_origin,))
                                    
                                    if dest_results:
                                        # Use the transformed value for checking existence
                                        transformed_check_values[fk_index] = dest_results[0][0]
                    
                    # Use transformed values for existence check
                    check_values = tuple(transformed_check_values[index] for index in conditional_indexes)
                    exists = executeQuery(table2_cursor, check_query, check_values)[0][0]
                else:
                    exists = False

                # Transform row for insert or update
                transformed_row = []
                repeat_count = 0
                for index, item in enumerate(row):
                    if isinstance(columns_pairs[list(columns_pairs.keys())[index]], list):
                        repeat_count = len(columns_pairs[list(columns_pairs.keys())[index]])
                        transformed_row.extend([item] * repeat_count)
                    else:
                        transformed_row.append(item)

                # Add additional column values to each row
                additional_values = []
                if additional_columns:
                    additional_values = list(additional_columns.values())
                    transformed_row_with_additional = transformed_row + additional_values
                else:
                    transformed_row_with_additional = transformed_row

                # Handle foreign key transformations
                if fks:
                    for fk in fks:
                        fk_index, ref_table_origin, ref_table_dest, ref_col_origin_dest, match_col_origin_dest, copy_missing_fks = fk[:6]
                        if len(fk) > 6:
                            fk_additional_cols = fk[6]
                        else:
                            fk_additional_cols = []

                        origin_value = transformed_row[fk_index]
                        # Fetch matching value from origin
                        fetch_fk_origin_query = f"SELECT {match_col_origin_dest[0]} FROM `{ref_table_origin}` WHERE {ref_col_origin_dest[0]} = %s"
                        match_value_origin = executeQuery(table1_cursor, fetch_fk_origin_query, (origin_value,))
                        if match_value_origin:
                            match_value_origin = match_value_origin[0][0]
                        else:
                            match_value_origin = None
                        # Fetch corresponding value from destination
                        fetch_fk_dest_query = f"SELECT {ref_col_origin_dest[1]} FROM `{ref_table_dest}` WHERE {match_col_origin_dest[1]} = %s"
                        dest_results = executeQuery(table2_cursor, fetch_fk_dest_query, (match_value_origin,))
                        if dest_results:
                            transformed_value = dest_results[0][0]
                        elif copy_missing_fks:
                            # Insert new row in destination table and use the new id
                            fk_additional_columns_str = ''
                            if fk_additional_cols:
                                for col in fk_additional_cols:
                                    if fk_additional_columns_str:
                                        fk_additional_columns_str += ', '
                                    fk_additional_columns_str += col[1]
                            fk_additional_values_str = ', '.join(['%s'] * len(fk_additional_cols)) if fk_additional_cols else ''
                            insert_fk_dest_query = f"INSERT INTO `{ref_table_dest}` ({match_col_origin_dest[1]}{', ' + fk_additional_columns_str if fk_additional_columns_str else ''}) VALUES (%s{', ' + fk_additional_values_str if fk_additional_values_str else ''})"
                            fk_additional_values = [executeQuery(table1_cursor, f"SELECT {col[0]} FROM `{ref_table_origin}` WHERE {ref_col_origin_dest[0]} = %s", (origin_value,))[0][0] for col in fk_additional_cols] if fk_additional_cols else []
                            executeQuery(table2_cursor, insert_fk_dest_query, (match_value_origin, *fk_additional_values))
                            transformed_value = getLastRowId(table2_cursor)
                        else:
                            transformed_value = None
                        transformed_row[fk_index] = transformed_value
                        transformed_row_with_additional[fk_index] = transformed_value

                if exists:
                    # Record exists - UPDATE it
                    fetch_id_query = f"SELECT id FROM `{table2_name}` WHERE {check_conditions}"
                    existing_id = executeQuery(table2_cursor, fetch_id_query, check_values)[0][0]
                    
                    # Build UPDATE query for non-conditional columns
                    update_columns = []
                    update_values = []
                    
                    for i, col in enumerate(columns_table2):
                        # Skip columns used in the conditional check - we don't update key/identifier columns
                        if conditional_indexes and i in conditional_indexes:
                            continue
                        update_columns.append(f"{col} = %s")
                        update_values.append(transformed_row_with_additional[i])
                    
                    if update_columns:  # Only update if there are columns to update
                        update_query = f"UPDATE `{table2_name}` SET {', '.join(update_columns)} WHERE id = %s"
                        executeQuery(table2_cursor, update_query, tuple(update_values + [existing_id]))
                    
                    # Add to result data
                    if result is not None:
                        filtered_row_data = [row[column_index] for column_index, column_name in enumerate(columns_pairs.keys()) if column_name in result]
                        filtered_row_data.insert(0, existing_id)  # Insert the ID at the beginning
                        result_data.append((filtered_row_data, False))
                    else:
                        result_data.append((existing_id, False))
                else:
                    # Record doesn't exist - INSERT it
                    executeQuery(table2_cursor, insert_query, tuple(transformed_row_with_additional))
                    inserted_id = getLastRowId(table2_cursor)
                    if result is not None:
                        # Collect only the specified columns for the result along with the ID
                        filtered_row_data = [row[column_index] for column_index, column_name in enumerate(columns_pairs.keys()) if column_name in result]
                        filtered_row_data.insert(0, inserted_id)  # Insert the ID at the beginning
                        result_data.append((filtered_row_data, True))
                    else:
                        result_data.append((inserted_id, True))

            # Return the result data
            return result_data
        
        def create_tables(names, cols):
            """
            Create tables in a database.

            Args:
            - names: Either a dictionary or a list.
                If a dictionary, keys are table names and values are lists of column definitions.
                If a list, it contains table names, and column definitions are provided separately.
            - cols: A list of column definitions if 'names' is a list.

            Returns:
            None
            """
            try:
                # Check if 'names' is a dictionary
                if isinstance(names, dict):
                    # Iterate through each table name and its columns
                    for table_name, columns in names.items():
                        # Generate column definitions string
                        column_definitions = ', '.join([f"{col[0]} {col[1]}" for col in columns])
                        # Form the SQL query to create the table
                        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({column_definitions})"
                        # Execute the SQL query to create the table
                        executeQuery("accountant", create_table_query)
                # Check if 'names' is a list
                elif isinstance(names, list):
                    # Iterate through each table name
                    for table_name in names:
                        # Generate column definitions string using 'cols' parameter
                        column_definitions = ', '.join([f"{col[0]} {col[1]}" for col in cols])
                        # Form the SQL query to create the table
                        create_table_query = f"CREATE TABLE IF NOT EXISTS `{table_name}` ({column_definitions})"
                        # Execute the SQL query to create the table
                        executeQuery("accountant", create_table_query)
            except Exception as e:
                # Print error message if an exception occurs
                print(f"Error creating tables: {e}")

        def executeQuery(target, query, data=None):
            print("******")
            print(query)
            cursor = self.factory_cursor if target.lower() == 'factory' else self.accountant_cursor if target.lower() == 'accountant' else None
            if cursor:
                print(query, data)
                cursor.execute(query, data if data else None)

                # Only fetch results, don't commit automatically
                if cursor.description:  # Check if the query returns results
                    results = cursor.fetchall()
                    return results
                return None

        def getLastRowId(target):
            cursor = self.factory_cursor if target.lower() == 'factory' else self.accountant_cursor if target.lower() == 'accountant' else None
            try:
                return cursor.lastrowid
            except:
                return None

        #########################################################################################################
        ################################################## CALLS ################################################
        #########################################################################################################

        # Groups
        if self.ui.sync_materials_groups_checkBox.isChecked():
            cols_dict_groups = {
                # "id": "id",
                "name": "name",
                "abbreviation": "code"
            }
            fks = []
            table1_info_groups = ['types', 'factory']
            table2_info_groups = ['groups', 'accountant']
            transfer_data_between_tables(table1_info_groups, table2_info_groups, cols_dict_groups, [0])

        # Material
        if self.ui.sync_materials_checkBox.isChecked():
            # Base column mapping
            cols_dict = {
                "code": "code",
                "name": "name",
                "specs": "specs",
                "type_id": "group_col",
                "unit_id": "unit1"
            }

            # Additional columns and foreign keys if group syncing is enabled
            fks = []
            fks.append([3, 'types', 'groups', ['id', 'id'], ['name', 'name'],
                        self.ui.sync_materials_groups_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
            fks.append([4, 'units', 'units', ['id', 'id'], ['name', 'name'],
                        self.ui.sync_units_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used

            # Define source and target table information
            table1_info = ['codes', 'factory']
            table2_info = ['materials', 'accountant']

            # Transfer data between tables
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks)

        # Units
        if self.ui.sync_units_checkBox.isChecked():
            # Sync only the units tables
            cols_dict_units = {
                #  "id": "id",
                "name": "name"
            }
            fks = []
            table1_info_units = ['units', 'factory']
            table2_info_units = ['units', 'accountant']
            transfer_data_between_tables(table1_info_units, table2_info_units, cols_dict_units, [0])

        # Groupped Materials
        if self.ui.sync_groupped_materials_checkBox.isChecked():
            # Sync the compositions
            cols_dict_compositions = {
                "id": "factory_dossier_id",
                "material_id": "material",
                "name": "name"
            }
            table1_info_compositions = ['SELECT `dossiers`.`id`, `dossiers`.`product_id` AS `material_id`, `codes`.`name` FROM `dossiers` INNER JOIN `codes` ON `dossiers`.`product_id` = `codes`.`id`', 'factory']
            table2_info_compositions = ['compositions', 'accountant']

            fks = []
            fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])

            compositions_ids = transfer_data_between_tables(table1_info_compositions, table2_info_compositions, cols_dict_compositions, [0], fks=fks, result=["id", "factory_dossier_id"])

            for composition in compositions_ids:
                composition_id = composition[0][0]
                factory_dossier_id = composition[0][1]

                cols_dict = {
                    "output_material_id":"groupped_material_id",
                    "input_material_id":"composition_material_id",
                    "quantity": "quantity",
                    "unit_id":"unit"
                }
                factory_groupped_materials_query = f"SELECT `dossiers`.`product_id` AS `output_material_id`, `dossiers.stages.inputs`.`material_id` AS `input_material_id`, `dossiers.stages.inputs`.`quantity`, `dossiers.stages.inputs`.`unit_id` FROM `dossiers` INNER JOIN `dossiers.stages` ON `dossiers`.`id` = `dossiers.stages`.`dossier_id` INNER JOIN `dossiers.stages.inputs` ON `dossiers.stages`.`id` = `dossiers.stages.inputs`.`stage_id` WHERE `dossiers`.`id` = {factory_dossier_id} AND `dossiers.stages.inputs`.`source` IS NOT NULL"
                table1_info = [factory_groupped_materials_query, 'factory']
                table2_info = ['groupped_materials_composition', 'accountant']
                fks = []
                fks.append([0, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])

                additional_columns = {"composition_id": composition_id}
                transfer_data_between_tables(table1_info, table2_info, cols_dict, [0, 1, 2, 3], fks=fks, additional_columns=additional_columns)
        
        # Currencies
        if self.ui.sync_currencies_checkBox.isChecked():
            cols_dict = {
                "name": "name"
            }
            table1_info = ['currencies', 'factory']
            table2_info = ['currencies', 'accountant']
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0])

        # Suppliers
        if self.ui.sync_suppliers_checkBox.isChecked():
            cols_dict = {
                "name": "name",
                "phone1": "phone1",
                "phone2": "phone2",
                "phone3": "phone3",
                "email": "email",
                "address": "address",
            }
            fks = []
            table1_info = ['suppliers', 'factory']
            table2_info = ['clients', 'accountant']
            additional_columns = {"client_type": "supplier"}
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], additional_columns=additional_columns)

        # Clients
        if self.ui.sync_clients_checkBox.isChecked():
            cols_dict = {
                "name": "name",
                "address": "address",
            }
            fks = []
            table1_info = ['clients', 'factory']
            table2_info = ['clients', 'accountant']
            additional_columns = {"client_type": "customer"}
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], additional_columns=additional_columns)


        # Machines and Resources
        if self.ui.sync_machines_checkbox.isChecked():
            # Resources
            cols_dict = {
                "id":"id",
                "name":"name",
                "notes":"notes",
            }
            table1_info = ['resources', 'factory']
            table2_info = ['resources', 'accountant']
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0])
            
            # Machines
            cols_dict = {
                    "id":"id",
                    "name":"name",
                    "years_age": "years_age",
                    "estimated_waste_quantity": "estimated_waste_value",
                    "notes": "notes"
                }
            table1_info = ['machines', 'factory']
            table2_info = ['machines', 'accountant']
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0])
            
            # Modes
            cols_dict = {
                "id":"id",
                "machine_id":"machine_id",
                "name":"name",
            }
            table1_info = ['machine_modes', 'factory']
            table2_info = ['machine_modes', 'accountant']
            fks=[]
            fks.append([1, 'machines', 'machines', ['id', 'id'], ['id', 'id'], self.ui.sync_materials_groups_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0])
            
            # Mode Resources
            cols_dict = {
            "consumption_per_minute":"consumption_per_minute",
            "mode_id":"mode_id",
            "resource_id":"resource_id",
            "unit":"unit"
            }

            table1_info = ['SELECT `mode_resources`.*, `units`.`id` AS `unit` FROM `mode_resources` JOIN `resources` ON `resources`.`id` = `mode_resources`.`resource_id` JOIN `units` ON `units`.`id` = `resources`.`measure_unit`', 'factory']
            table2_info = ['mode_resources', 'accountant']
            fks = []
            fks.append([1, 'machine_modes', 'machine_modes', ['id', 'id'], ['id', 'id'], self.ui.sync_materials_groups_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
            fks.append([2, 'resources', 'resources', ['id', 'id'], ['id', 'id'], self.ui.sync_materials_groups_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
            fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], self.ui.sync_units_checkBox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks)

        # Warehouses
        if self.ui.sync_warehouseslist_checkBox.isChecked():
            cols_dict = {
                "name": "name",
                "code_name": "codename",
                "date": "date_col"
            }
            table1_info = ['warehouseslist', 'factory']
            table2_info = ['warehouseslist', 'accountant']
            created_tables = transfer_data_between_tables(table1_info, table2_info, cols_dict, [1], result=["code_name"])
            column_definitions = [
                ["id", "INT AUTO_INCREMENT PRIMARY KEY"],
                ["material_id", "INT"],
                ["quantity", "FLOAT"],
                ["unit", "INT"],
                ["production_batch_id", "INT"],
                ["receipt_doc_id", "INT"],
                ["batch_number", "INT"],
                ["batch_mfg", "DATE NULL"],
                ["batch_exp", "DATE NULL"],
                ["material_move_id", "INT NULL"],
                ["production_date", "DATE NULL"],
                ["expire_date", "DATE NULL"],
                ["factory_id", "INT"]
            ]
            created_tables_names = [table[0][1] for table in created_tables]  # extract the table names
            create_tables(created_tables_names, column_definitions)

        # Purchase Invoices
        if self.ui.sync_purchase_invoices_checkBox.isChecked():
            cols_dict = {
                "id": "factory_id",
                "supplier_id": "client",
                "payment": "payment",
                "paid": "paid",
                "currency": "currency",
                "warehouse_id": "warehouse",
                "date":"date_col"
            }

            fks = []  # fk_index, ref_table_origin, ref_table_dest, ref_col_origin_dest (usually ID cols), match_col_origin_dest, copy_missing_fks
            # last value, if True, it copies missing fks. else, it checks if they exist, their IDs are used
            fks.append([1, 'suppliers', 'clients', ['id', 'id'], ['name', 'name'], self.ui.sync_suppliers_checkBox.isChecked()])
            fks.append([4, 'currencies', 'currencies', ['id', 'id'], ['name', 'name'], self.ui.sync_currencies_checkBox.isChecked()])
            fks.append([5, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], self.ui.sync_warehouseslist_checkBox.isChecked()])
            table1_info = [
                'SELECT `deals`.`id`, `priceoffers`.`supplier_id`, CASE WHEN LOWER(`deals`.`payment`) = "immediately" THEN "cash" ELSE "postponed" END AS `payment`, CASE WHEN LOWER(`deals`.`paid`) = "yes" THEN 1 ELSE 0 END AS `paid`, `deals`.`currency`, `receipt_docs`.`target_warehouse_id` AS `warehouse_id`, `deals`.`group_number`, `receipt_docs`.`date` FROM `deals` JOIN `priceoffers` ON `priceoffers`.`id` = `deals`.`priceoffer_id` JOIN `suppliers` ON `suppliers`.`id` = `priceoffers`.`supplier_id` JOIN `receipt_docs` ON `receipt_docs`.`deal_id` = `deals`.`id` JOIN `warehouseslist` ON `warehouseslist`.`id` = `receipt_docs`.`target_warehouse_id`', 'factory']
            table2_info = ['invoices', 'accountant']

            try:
                # Get "Buy" invoice type ID from accountant, since all invoices are "Buy" in factory
                buy_invoice_type_id = executeQuery("accountant", "SELECT `id` FROM `invoice_types` WHERE `name` = 'buy'")[0][0]
                buy_materials_account = executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'buy_materials_account'")[0][0]
                buy_monetary_account = executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'buy_monetary_account'")[0][0]
            except:
                raise Exception("Please make sure to set the invoice defaults for buy invoices in the settings")

            additional_columns = {"monetary_account": buy_monetary_account, "materials_account": buy_materials_account , "type_col": buy_invoice_type_id}  

            invoices_ids = transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks, result=["id", "factory_id"], additional_columns=additional_columns)
            for item in invoices_ids:
                invoice_id = item[0][0]
                factory_deal_id = item[0][1]

                # Update invoice number
                last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
                invoice_number = int(last_invoice_number) + 1 if last_invoice_number else 1
                executeQuery("accountant", f"UPDATE `invoices` SET `number` = {invoice_number} WHERE `id` = {invoice_id}")

                cols_dict = {
                    # factory : accountant
                    "id": "factory_id",
                    "material_id": "material_id", #fk
                    "warehouse_id": "warehouse_id", #fk
                    "quantity": "quantity1",
                    "unit": "unit1_id", #fk
                    "unit_price":["unit_price","equilivance_price"],
                    "currency":"currency_id", #fk
                }
                fks = []
                table1_info=[f'SELECT `deals`.`id`, `deals`.`material_id`, `receipt_docs`.`target_warehouse_id` AS `warehouse_id`, `deals`.`quantity`, `deals`.`unit`, `deals`.`unit_price`, `deals`.`currency` FROM `deals` JOIN `priceoffers` ON `priceoffers`.`id` = `deals`.`priceoffer_id` JOIN `suppliers` ON `suppliers`.`id` = `priceoffers`.`supplier_id` JOIN `receipt_docs` ON `receipt_docs`.`deal_id` = `deals`.`id` JOIN `warehouseslist` ON `warehouseslist`.`id` = `receipt_docs`.`target_warehouse_id` WHERE `deals`.`id` = {factory_deal_id}', 'factory']
                table2_info=['invoice_items', 'accountant']
                
                fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True]) #TODO: read value from check materials sync
                fks.append([2, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], True, [["name","name"]]]) #TODO: read value from check materials sync
                fks.append([4, 'units', 'units', ['id', 'id'], ['name', 'name'], True]) #TODO: read value from check unit sync
                fks.append([6, 'currencies', 'currencies', ['id', 'id'], ['name', 'name'], True]) #TODO: read value from check unit sync

                additional_columns = {"invoice_id": invoice_id}

                transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks, additional_columns=additional_columns)

        # Sales Invoices
        if self.ui.sync_sell_invoices_checkBox.isChecked():
            cols_dict = {
                "id": "factory_id",
                "client_id": "client",
                "notes": "statement_col",
                "date":"date_col"
            }

            fks = []  # fk_index, ref_table_origin, ref_table_dest, ref_col_origin_dest (usually ID cols), match_col_origin_dest, copy_missing_fks
            # last value, if True, it copies missing fks. else, it checks if they exist, their IDs are used
            fks.append([1, 'clients', 'clients', ['id', 'id'], ['name', 'name'], self.ui.sync_clients_checkBox.isChecked()])
            table1_info = ['SELECT `invoices`.`id`, `invoices`.`client_id`, `invoices`.`notes`, `invoices`.`date` FROM `invoices` WHERE `invoices`.`state` = "finalized"', 'factory']
            table2_info = ['invoices', 'accountant']

            try:
                # Get "Sell" invoice type ID from accountant, since all invoices are "Sell" in factory
                sale_invoice_type_id = executeQuery("accountant", "SELECT `id` FROM `invoice_types` WHERE `name` = 'sell'")[0][0]
                sell_materials_account = executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'sell_materials_account'")[0][0]
                sell_monetary_account = executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'sell_monetary_account'")[0][0]
                sell_invoice_default_currency = executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'sell_currency'")[0][0]
            except:
                raise Exception("Please make sure to set the invoice defaults for sell invoices in the settings")
            
            additional_columns = {"monetary_account": sell_monetary_account, "materials_account": sell_materials_account, "type_col": sale_invoice_type_id, "currency": sell_invoice_default_currency}  

            invoices_ids = transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks, result=["id", "factory_id"], additional_columns=additional_columns)

            for item in invoices_ids:
                invoice_id = item[0][0]
                factory_invoice_id = item[0][1]

                # Update invoice number
                last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
                invoice_number = int(last_invoice_number) + 1 if last_invoice_number else 1
                executeQuery("accountant", f"UPDATE `invoices` SET `number` = {invoice_number} WHERE `id` = {invoice_id}")

                cols_dict = {
                    # factory : accountant
                    "id": "factory_id",
                    "item_id": "material_id", #fk
                    "warehouse_id": "warehouse_id", #fk
                    "quantity":"quantity1", #fk
                    "unit_id": "unit1_id"
                }
                fks = []
                table1_info=[f"SELECT `invoices.items`.id, `invoices.items`.item_id, `invoices.items`.warehouse_id, `invoices.items`.invoice_id, `invoices.items`.quantity, codes.unit_id FROM `invoices.items` JOIN codes ON `invoices.items`.item_id = codes.id WHERE invoice_id='{factory_invoice_id}'", 'factory']
                table2_info=['invoice_items', 'accountant']
                
                fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True]) #TODO: read value from check materials sync
                fks.append([2, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], True]) #TODO: read value from check materials sync
                fks.append([4, 'units', 'units', ['id', 'id'], ['name', 'name'], True]) #TODO: read value from check unit sync

                additional_columns = {"invoice_id": invoice_id}

                transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks, additional_columns=additional_columns)

        # Receipt Docs
        if self.ui.sync_receipt_docs_checkbox.isChecked():
            cols_dict = {
                "id": "factory_id",
                "date": "date_col",
                "material_id": "material_id",
                "quantity": "quantity",
                "unit_id": "unit_id",
                "target_warehouse_id": "target_warehouse_id",
                "rejection_warehouse_id": "rejection_warehouse_id",
                "deal_id": "invoice_item_id"
            }
            fks = []
            fks.append([2, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
            fks.append([4, 'units', 'units', ['id', 'id'], ['name', 'name'], True])
            fks.append([5, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], True])
            fks.append([6, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], True])
            fks.append([7, 'deals', 'invoice_items', ['id', 'id'], ['id', 'factory_id'], True])
            
            query = "SELECT receipt_docs.id, receipt_docs.deal_id, receipt_docs.date, receipt_docs.material_id, (COALESCE(receipt_docs.first_batch_accepted_quantity, 0) + COALESCE(receipt_docs.second_batch_accepted_quantity, 0) + COALESCE(receipt_docs.third_batch_accepted_quantity, 0) + COALESCE(receipt_docs.fourth_batch_accepted_quantity, 0) + COALESCE(receipt_docs.fifth_batch_accepted_quantity, 0)) AS quantity, deals.unit as unit_id, receipt_docs.target_warehouse_id, receipt_docs.rejection_warehouse_id FROM receipt_docs JOIN deals ON deals.id = receipt_docs.deal_id"
            
            table1_info = [query, 'factory']
            table2_info = ['receipt_docs', 'accountant']
            transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks)
        
        # Manufacture
        if self.ui.sync_manufacture_checkbox.isChecked():

            cols_dict = {
                "id":"factory_id",
                # "batch_number": "batch",
                "date": "date_col"
            }
            table1_info = ["SELECT `production.batches`.* FROM `production.batches` WHERE `production.batches`.`state` = 'locked'", 'factory']
            table2_info = ['manufacture', 'accountant']

            # Get the default currency
            try:
                default_currency = int(executeQuery("accountant", "SELECT `value_col` FROM `settings` WHERE `name` = 'default_currency'")[0][0])
            except:
                default_currency = None

            if default_currency is None:
                raise Exception("Default currency is not set")
            
            # Get synchronization settings defaults
            try:
                mid_account_output = int(self.database_operations.fetchSetting('mid_output_account'))
                mid_account_input = int(self.database_operations.fetchSetting('mid_input_account'))
                input_account = int(self.database_operations.fetchSetting('input_account'))
                output_account = int(self.database_operations.fetchSetting('output_account'))
                material_pricing_method = self.database_operations.fetchSetting('material_pricing_method_sync')
                distribution_expense = self.database_operations.fetchSetting('distribution_expenses_sync')
                distribution_expense_type = self.database_operations.fetchSetting('distribution_expenses_type_sync')
                quantity_expenses_target_unit = int(self.database_operations.fetchSetting('expenses_quantity_unit_sync'))
            except:
                raise Exception("Please make sure to set the synchronizing manufacture defaults in the settings")

            additional_columns = {
                "pullout_date": "date_col",
                "expenses_type": distribution_expense,
                "material_pricing_method": material_pricing_method,
                "currency": default_currency,
                "mid_account": mid_account_output,
                "mid_account_input": mid_account_input,
                "account": input_account,
                "ingredients_pullout_account": output_account,
                "state_col": "active"
                }

            manufacture_ids = transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], result=["id", "factory_id", "date"], additional_columns=additional_columns)

            new_manufacture_ids = [manufacture_id[0] for manufacture_id in manufacture_ids if manufacture_id[1]]

            for manufacture_id in new_manufacture_ids:
                manufacture_id_accountant = manufacture_id[0]
                manufacture_id_factory = manufacture_id[1]
                manufacture_date = manufacture_id[2]

                real_work_hours = 0

                if distribution_expense == "real":

                    # Calculate the total cost of the manufacture process
                    total_cost = 0
                    total_machines_cost = 0

                    # Calculate the resources cost
                    resources_cost = executeQuery("factory", f"SELECT resources.id, resources.name, SUM(pm.duration * mr.consumption_per_minute) AS total_consumption, resources.measure_unit, units.name FROM `production.batches.stages.machines` AS pm JOIN `production.batches.stages` AS ps ON ps.id = pm.stage_id JOIN mode_resources AS mr ON mr.mode_id = pm.mode_id JOIN resources ON resources.id = mr.resource_id JOIN units ON units.id = resources.measure_unit WHERE ps.batch_id = {manufacture_id_factory} GROUP BY resources.id, resources.name, resources.measure_unit;")

                    for resource in resources_cost:
                        resource_id_factory = resource[0]
                        resource_name_factory = resource[1]
                        total_consumption = resource[2]
                        unit_name = resource[4]

                        # Check if the units are synced
                        unit_id = executeQuery("accountant", f"SELECT id FROM units WHERE name = '{unit_name}'")
                        if not unit_id:
                            raise Exception(f"Unit {unit_name} is not synced")
                        unit_id = unit_id[0][0]

                        # Check if the resource is synced
                        resource_id_accountant = executeQuery("accountant", f"SELECT id FROM resources WHERE name = '{resource_name_factory}'")
                        if not resource_id_accountant:
                            raise Exception(f"Resource {resource_name_factory} is not synced")
                        resource_id_accountant = resource_id_accountant[0][0]

                        # Check if there is a resource cost
                        resource_cost = executeQuery("accountant", f"SELECT id, value_col, currency_id FROM resources_costs WHERE resource_id = {resource_id_accountant} AND unit_id = {unit_id}")
                        if not resource_cost:
                            raise Exception(f"No resource cost for {resource_name_factory}")
                        
                        resource_cost_value = resource_cost[0][1]
                        resource_currency_id = resource_cost[0][2]

                        # Calculate the cost of the resource
                        resource_cost = total_consumption * resource_cost_value
                    
                        if resource_currency_id != default_currency:
                            # Convert the cost to the default currency
                            exchange_rate = self.database_operations.fetchExchangeValue(resource_currency_id, default_currency)
                            resource_cost = resource_cost * exchange_rate[0][1]

                        total_machines_cost += resource_cost

                    # Calculate the salaries cost
                    standard_work_minutes = executeQuery("factory", f"SELECT SUM(`dossiers.stages.machines`.duration) FROM `dossiers.stages.machines` JOIN `dossiers.stages` ON `dossiers.stages`.`id` = `dossiers.stages.machines`.`stage_id` JOIN `production.batches` ON `production.batches`.`dossier_id` = `dossiers.stages`.`dossier_id` WHERE `production.batches`.`id` = {manufacture_id_factory}")[0][0]

                    real_work_minutes = executeQuery("factory", f"SELECT SUM(`production.batches.stages.machines`.duration) FROM `production.batches.stages.machines` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.machines`.`stage_id` JOIN `production.batches` ON `production.batches`.`id` = `production.batches.stages`.`batch_id` WHERE `production.batches`.`id` = {manufacture_id_factory}")[0][0]

                    if standard_work_minutes:
                        standard_work_hours = round(float(standard_work_minutes)/60, 2)
                    else:
                        standard_work_hours = 0

                    if real_work_minutes:
                        real_work_hours = round(float(real_work_minutes)/60, 2)
                    else:
                        real_work_hours = 0


                    salaries_cost = self.synchronizer_helper.calculate_salaries_cost(default_currency, manufacture_date, standard_work_hours, real_work_hours)

                    # Update the manufacture cost
                    executeQuery("accountant", f"UPDATE `manufacture` SET `machines_operation_cost` = {total_machines_cost}, `salaries_cost` = {salaries_cost}, `working_hours` = {real_work_hours} WHERE `id` = {manufacture_id_accountant}")

                else: 
                    # Calculate the expenses cost

                    # Get the unit name from the accountant
                    unit_name = executeQuery("accountant", f"SELECT `units`.`name` FROM `units` WHERE `units`.`id` = {quantity_expenses_target_unit}")
                    if not unit_name:
                        raise Exception(f"Unit {quantity_expenses_target_unit} is not synced")
                    unit_name = unit_name[0][0]

                    # Get the unit id in the factory
                    unit_id_factory = executeQuery("factory", f"SELECT `units`.`id` FROM `units` WHERE `units`.`name` = '{unit_name}'")
                    if not unit_id_factory:
                        raise Exception(f"Unit {unit_name} is not synced")
                    unit_id_factory = unit_id_factory[0][0]

                    unit_quantity_produced = executeQuery("factory", f"SELECT SUM(`production.batches.stages.outputs`.quantity) FROM `production.batches.stages.outputs` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.outputs`.`stage_id` JOIN `production.batches` ON `production.batches`.`id` = `production.batches.stages`.`batch_id` WHERE `production.batches`.`id` = {manufacture_id_factory} AND `production.batches.stages.outputs`.`unit_id` = {unit_id_factory}")[0][0]

                    expenses_cost = self.synchronizer_helper.calculate_year_month_expenses_cost(distribution_expense,  distribution_expense_type, default_currency, manufacture_date, quantity_expenses_target_unit, unit_quantity_produced, real_work_hours)

                    # Update the manufacture cost
                    executeQuery("accountant", f"UPDATE `manufacture` SET `expenses_cost` = {expenses_cost} WHERE `id` = {manufacture_id_accountant}")

                # sync composition materials
                cols_dict = {
                    "output_material_id":"groupped_material_id",
                    "input_material_id":"composition_material_id",
                    "quantity": "quantity",
                    "unit_id":"unit"
                }
                factory_input_materials_query = f"SELECT `dossiers`.`product_id` AS `output_material_id`, `dossiers.stages.inputs`.`material_id` AS `input_material_id`, `dossiers.stages.inputs`.`quantity`, `dossiers.stages.inputs`.`unit_id` FROM `dossiers` INNER JOIN `dossiers.stages` ON `dossiers`.`id` = `dossiers.stages`.`dossier_id` INNER JOIN `dossiers.stages.inputs` ON `dossiers.stages`.`id` = `dossiers.stages.inputs`.`stage_id` INNER JOIN `production.batches` ON `dossiers`.`id` = `production.batches`.`dossier_id` WHERE `production.batches`.`id` = {manufacture_id_factory}"
                table1_info = [factory_input_materials_query, 'factory']
                table2_info = ['groupped_materials_composition', 'accountant']
                fks = []
                fks.append([0, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])
                composition_materials = transfer_data_between_tables(table1_info, table2_info, cols_dict, [0, 1, 2, 3], fks=fks, result=['id', 'input_material_id'])

                for composition_material in composition_materials:
                    composition_item_id = composition_material[0][0]
                    input_material_id = composition_material[0][1]

                    # sync input materials
                    cols_dict = {
                    "quantity": "required_quantity",
                    "unit_id":"unit",
                    "source": "warehouse_id"
                    }
                    factory_input_materials_query = f"SELECT `production.batches.stages.inputs`.* FROM `production.batches.stages.inputs` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.inputs`.`stage_id` WHERE `production.batches.stages`.`batch_id`={manufacture_id_factory} AND `production.batches.stages.inputs`.`material_id`={input_material_id}"
                    table1_info = [factory_input_materials_query, 'factory']
                    table2_info = ['manufacture_materials', 'accountant']
                    fks = []
                    fks.append([1, 'units', 'units', ['id', 'id'], ['name', 'name'], True])
                    fks.append([2, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])
                    additional_columns={"manufacture_id":manufacture_id_accountant, "composition_item_id":composition_item_id, "row_type": "parent"}
                    transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, additional_columns=additional_columns)

                # sync produced materials
                cols_dict = {
                "material_id":"material_id",
                "quantity": "quantity1",
                "batch_number": "batch",
                "unit_id":"unit1",
                "working_hours":"working_hours",
                "production_date":"production_date",
                "destination": "warehouse"
                # "refrencial_quantity1":"refrencial_quantity1",
                # "refrencial_working_hours":"refrencial_working_hours"
                }
                factory_output_materials_query = f"SELECT `production.batches.stages.outputs`.*, (SELECT `batch_number` FROM `production.batches` WHERE `production.batches`.`id`={manufacture_id_factory}) AS `batch_number`, (SELECT SUM(`duration`)/60 FROM `production.batches.stages.machines` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.machines`.`stage_id` WHERE `production.batches.stages`.`batch_id`={manufacture_id_factory}) AS `working_hours`, (SELECT `date` FROM `production.batches` WHERE `production.batches`.`id`={manufacture_id_factory}) AS `production_date` FROM `production.batches.stages.outputs` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.outputs`.`stage_id` WHERE `production.batches.stages`.`batch_id`={manufacture_id_factory}"
                table1_info = [factory_output_materials_query, 'factory']
                table2_info = ['manufacture_produced_materials', 'accountant']
                fks = []
                fks.append([0, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
                fks.append([6, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], self.ui.sync_warehouseslist_checkBox.isChecked()])
                additional_columns={"manufacture_id":manufacture_id_accountant}
                transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, additional_columns=additional_columns)
                
                # sync manufacture machines
                cols_dict = {
                "machine_id":"machine_id",
                "mode_id": "mode_id",
                "duration":"duration"
                }
                
                factory_machines_query = f"SELECT `production.batches.stages.machines`.*, `machine_modes`.`machine_id` AS `machine_id` FROM `production.batches.stages.machines` JOIN `production.batches.stages` ON `production.batches.stages`.`id` = `production.batches.stages.machines`.`stage_id` JOIN `machine_modes` ON `machine_modes`.`id` = `production.batches.stages.machines`.`mode_id` WHERE `production.batches.stages`.`batch_id`={manufacture_id_factory}"
                table1_info = [factory_machines_query, 'factory']
                table2_info = ['manufacture_machines', 'accountant']
                fks = []
                fks.append([0, 'machines', 'machines', ['id', 'id'], ['id', 'id'], self.ui.sync_machines_checkbox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
                fks.append([1, 'machine_modes', 'machine_modes', ['id', 'id'], ['id', 'id'], self.ui.sync_machines_checkbox.isChecked()])  # last value, if True, it copies missing fks. else, it checks if they exist, thier IDs are used
                additional_columns={"manufacture_id":manufacture_id_accountant, "exclusive":0, "exclusive_percent":0}
                transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, additional_columns=additional_columns)

        # Warehouses content
        if self.ui.sync_warehouses_content_checkBox.isChecked():
            warehouses_codenames = [row[0] for row in executeQuery("accountant", "SELECT `codename` FROM `warehouseslist`")]
            for warehouse_codename in warehouses_codenames:
                cols_dict = {
                    "id": "factory_id",
                    "material_id": "material_id",
                    "quantity": "quantity",
                    "unit": "unit",
                    "production_batch_id": "production_batch_id",
                    "receipt_doc_id": "receipt_doc_id",
                    "batch_number": "batch_number",
                    "batch_mfg": "batch_mfg",
                    "batch_exp": "batch_exp"
                }
                table1_info = [f"SELECT `{warehouse_codename}`.*, `units`.`id` AS `unit` FROM `{warehouse_codename}` JOIN `codes` ON `codes`.`id` = `{warehouse_codename}`.`material_id` JOIN `units` ON `units`.`id` = `codes`.`unit_id`", 'factory']
                table2_info = [warehouse_codename, 'accountant']

                fks = []
                fks.append([1, 'codes', 'materials', ['id', 'id'], ['code', 'code'], True])
                fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])
                fks.append([4, f"production.batches", 'manufacture', ['id', 'id'], ['id', 'factory_id'], False])  
                fks.append([5, 'receipt_docs', 'receipt_docs', ['id', 'id'], ['id', 'factory_id'], False])  

                transfer_data_between_tables(table1_info, table2_info, cols_dict, [0], fks=fks)
    
        # Materials' Movement
        if self.ui.sync_moves_checkbox.isChecked():
            # # moves resulted from production 
            # cols_dict={
            #     "source_warehouse_entry_id": "source_warehouse_entry_id",
            #     "source_warehouse_id":"source_warehouse",
            #     "destination_warehouse_entry_id": "destination_warehouse_entry_id",
            #     "target_warehouse_id":"destination_warehouse",
            #     "quantity":"quantity",
            #     "unit_id":"unit",
            #     "batch_id":"origin_id",
            #     "date":"date_col"
            # }

            # factory_production_resulted_moves_query = "SELECT pulloutrequests_items.warehouse_item_id AS source_warehouse_entry_id, pulloutrequests.warehouse_id AS source_warehouse_id, NULL AS destination_warehouse_entry_id, NULL AS target_warehouse_id, pulloutrequests_items.quantity, `production.batches.stages.inputs`.unit_id, `production.batches.stages`.batch_id, pulloutrequests.date FROM `pulloutrequests` JOIN `pulloutrequests_items` ON pulloutrequests.id = pulloutrequests_items.pulloutrequest_id JOIN `production.batches.stages.inputs` ON pulloutrequests.id = `production.batches.stages.inputs`.pullout_id JOIN `production.batches.stages` ON `production.batches.stages.inputs`.stage_id = `production.batches.stages`.id JOIN `production.batches` ON `production.batches.stages`.batch_id = `production.batches`.id WHERE pulloutrequests.state = 'done' UNION ALL SELECT NUll AS source_warehouse_entry_id, NULL AS source_warehouse_id, `production.store`.warehouse_item_id AS destination_warehouse_entry_id, `production.store`.target_warehouse_id, `production.store`.quantity, `production.batches.stages.outputs`.unit_id, `production.batches.stages`.batch_id, `production.store`.date FROM `production.store` JOIN `production.batches.stages.outputs` ON `production.store`.stage_output_id = `production.batches.stages.outputs`.id JOIN `production.batches.stages` ON `production.batches.stages.outputs`.stage_id = `production.batches.stages`.id JOIN `production.batches` ON `production.batches.stages`.batch_id = `production.batches`.id WHERE `production.store`.received = 1"

            # table1_info = [factory_production_resulted_moves_query, 'factory']
            # table2_info = ['material_moves', 'accountant']

            # fks=[]
            # fks.append([1, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])  
            # fks.append([3, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])  
            # fks.append([5, f"units", 'units', ['id', 'id'], ['name', 'name'], False])  
            # fks.append([6, f"production.batches", 'manufacture', ['id', 'id'], ['id', 'factory_id'], False])
            # additional_columns = {"origin":'manufacture'}
            # moves = transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, result=['id', 'source_warehouse_entry_id', 'source_warehouse_id', 'destination_warehouse_entry_id', 'target_warehouse_id'], additional_columns=additional_columns)

            # for move in moves:
            #     move_id = move[0][0]
            #     source_warehouse_entry_id = move[0][1]
            #     source_warehouse_id = move[0][2]
            #     destination_warehouse_entry_id = move[0][3]
            #     destination_warehouse_id = move[0][4]

            #     # Update the move source warehouse entry
            #     if source_warehouse_id:
            #         source_warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {source_warehouse_id}")
            #         if not source_warehouse_codename:
            #             raise Exception(f"Source warehouse {source_warehouse_id} is not synced")
            #         source_warehouse_codename = source_warehouse_codename[0][0]

            #         source_warehouse_entry = executeQuery("accountant", f"SELECT `{source_warehouse_codename}`.`id` FROM `{source_warehouse_codename}` WHERE `{source_warehouse_codename}`.`factory_id` = {source_warehouse_entry_id}")
            #         if not source_warehouse_entry:
            #             executeQuery("accountant", f"UPDATE `material_moves` SET `source_warehouse_entry_id` = NULL WHERE `id` = {move_id}")
            #             continue
            #         source_warehouse_entry = source_warehouse_entry[0][0]

            #         executeQuery("accountant", f"UPDATE `material_moves` SET `source_warehouse_entry_id` = {source_warehouse_entry} AND `destination_warehouse_entry_id` = NULL WHERE `id` = {move_id}")

            #     # Update the move destination warehouse entry
            #     if destination_warehouse_id:
            #         # Get the destination warehouse codename in the factory
            #         destination_warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {destination_warehouse_id}")
            #         if not destination_warehouse_codename:
            #             raise Exception(f"Destination warehouse {destination_warehouse_id} is not synced")
            #         destination_warehouse_codename = destination_warehouse_codename[0][0]

            #         destination_warehouse_entry = executeQuery("accountant", f"SELECT `{destination_warehouse_codename}`.`id` FROM `{destination_warehouse_codename}` WHERE `{destination_warehouse_codename}`.`id` = {destination_warehouse_entry_id}")
            #         if not destination_warehouse_entry:
            #             executeQuery("accountant", f"UPDATE `material_moves` SET `destination_warehouse_entry_id` = NULL WHERE `id` = {move_id}")
            #             continue
            #         destination_warehouse_entry = destination_warehouse_entry[0][0]

            #         executeQuery("accountant", f"UPDATE `material_moves` SET `source_warehouse_entry_id` = NULL AND `destination_warehouse_entry_id` = {destination_warehouse_entry} WHERE `id` = {move_id}")

            # # moves resulted from purchase invoices 
            # cols_dict={
            #     "material_id": "source_warehouse_entry_id",
            #     "source_warehouse_id":"source_warehouse",
            #     "target_warehouse_id":"destination_warehouse",
            #     "quantity":"quantity",
            #     "unit_id":"unit",
            #     "deal_id":"origin_id",
            #     "date":"date_col"
            # }

            # factory_production_resulted_moves_query = "SELECT `deals`.`material_id`, NULL AS `source_warehouse_id`, `receipt_docs`.`target_warehouse_id`, `deals`.`quantity`, `deals`.`unit` AS `unit_id`, `deals`.`id` AS `deal_id`, `receipt_docs`.`date` FROM `deals` JOIN `priceoffers` ON `priceoffers`.`id` = `deals`.`priceoffer_id` JOIN `suppliers` ON `suppliers`.`id` = `priceoffers`.`supplier_id` JOIN `receipt_docs` ON `receipt_docs`.`deal_id` = `deals`.`id` JOIN `warehouseslist` ON `warehouseslist`.`id` = `receipt_docs`.`target_warehouse_id` WHERE `receipt_docs`.`received` = 1"
            # table1_info = [factory_production_resulted_moves_query, 'factory']
            # table2_info = ['material_moves', 'accountant']

            # fks=[]
            # fks.append([1, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])  
            # fks.append([2, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])  
            # fks.append([4, 'units', 'units', ['id', 'id'], ['name ', 'name '], True])
            # fks.append([5, 'deals', 'invoices', ['id', 'id'], ['id', 'factory_id'], True])  
            
            # additional_columns = {"origin":'invoice_buy'}
            # moves = transfer_data_between_tables(table1_info, table2_info, cols_dict, [5], fks=fks, result=['id', 'material_id', 'source_warehouse_id', 'target_warehouse_id', 'deal_id'], additional_columns=additional_columns)

            # for move in moves:
            #     move_id = move[0][0]
            #     material_id_factory = move[0][1]
            #     source_warehouse_id = move[0][2]
            #     destination_warehouse_id = move[0][3]
            #     deal_id = move[0][4]

            #     # Get the material id in the accountant
            #     material_code = executeQuery("factory", f"SELECT `codes`.`code` FROM `codes` WHERE `codes`.`id` = {material_id_factory}")
            #     if not material_code:
            #         raise Exception(f"Material {material_id_factory} is not synced")
            #     material_code = material_code[0][0]

            #     material_id_accountant = executeQuery("accountant", f"SELECT `id` FROM `materials` WHERE `code` = '{material_code}'")
            #     if not material_id_accountant:  
            #         raise Exception(f"Material {material_code} is not synced")
            #     material_id_accountant = material_id_accountant[0][0]

            #     # Get the receipt doc id in the factory
            #     receipt_doc_id_factory = executeQuery("factory", f"SELECT `receipt_docs`.`id` FROM `receipt_docs` WHERE `receipt_docs`.`deal_id` = {deal_id}")
            #     if not receipt_doc_id_factory:
            #         raise Exception(f"Receipt doc {deal_id} is not synced")
            #     receipt_doc_id_factory = receipt_doc_id_factory[0][0]

            #     # Get the receipt doc id in the accountant
            #     receipt_doc_id_accountant = executeQuery("accountant", f"SELECT `receipt_docs`.`id` FROM `receipt_docs` WHERE `receipt_docs`.`factory_id` = {receipt_doc_id_factory}")
            #     if not receipt_doc_id_accountant:
            #         raise Exception(f"Receipt doc {deal_id} is not synced")
            #     receipt_doc_id_accountant = receipt_doc_id_accountant[0][0]

            #     # Get the destination warehouse codename in the factory
            #     destination_warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {destination_warehouse_id}")
            #     if not destination_warehouse_codename:
            #         raise Exception(f"Destination warehouse {destination_warehouse_id} is not synced")
            #     destination_warehouse_codename = destination_warehouse_codename[0][0]

            #     destination_warehouse_entry = executeQuery("accountant", f"SELECT `{destination_warehouse_codename}`.`id` FROM `{destination_warehouse_codename}` WHERE `{destination_warehouse_codename}`.`material_id` = {material_id_accountant} AND `{destination_warehouse_codename}`.`receipt_doc_id` = {receipt_doc_id_accountant}")
            #     if not destination_warehouse_entry:
            #         continue
            #     destination_warehouse_entry = destination_warehouse_entry[0][0]

            #     executeQuery("accountant", f"UPDATE `material_moves` SET `destination_warehouse_entry_id` = {destination_warehouse_entry} WHERE `id` = {move_id}")

            # # moves resulted from sales invoices
            # cols_dict={
            #     "warehouse_item_id":"source_warehouse_entry_id",
            #     "warehouse_id":"source_warehouse",
            #     "quantity":"quantity",
            #     "unit_id":"unit",
            #     "invoice_id":"origin_id",
            #     "date":"date_col"
            # }

            # factory_sales_invoices_moves_query = "SELECT `invoices.items`.`warehouse_item_id`, `invoices.items`.`warehouse_id`, `invoices.items`.`quantity`, `units`.`id` AS `unit_id`, `invoices`.`id` AS `invoice_id`, `invoices`.`date` FROM `invoices.items` JOIN `invoices` ON `invoices.items`.`invoice_id` = `invoices`.`id` JOIN `codes` ON `codes`.`id` = `invoices.items`.`item_id` JOIN `units` ON `units`.`id` = `codes`.`unit_id` WHERE `invoices.items`.`state` = 'done'"
            # table1_info = [factory_sales_invoices_moves_query, 'factory']
            # table2_info = ['material_moves', 'accountant']

            # fks=[]
            # fks.append([1, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])
            # fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])
            # fks.append([4, 'invoices', 'invoices', ['id', 'id'], ['id', 'factory_id'], True])

            # additional_columns = {"origin":'invoice_sell'}
            # moves = transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, result=['id', 'warehouse_item_id', 'warehouse_id'], additional_columns=additional_columns)
            
            # for move in moves:
            #     move_id = move[0][0]
            #     warehouse_item_id = move[0][1]
            #     warehouse_id = move[0][2]

            #     # Get the warehouse codename in the factory
            #     warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {warehouse_id}")
            #     if not warehouse_codename:
            #         raise Exception(f"Warehouse {warehouse_id} is not synced")
            #     warehouse_codename = warehouse_codename[0][0]
                
            #     # Get the warehouse entry id in the accountant
            #     warehouse_entry = executeQuery("accountant", f"SELECT `{warehouse_codename}`.`id` FROM `{warehouse_codename}` WHERE `{warehouse_codename}`.`factory_id` = {warehouse_item_id}")
            #     if not warehouse_entry:
            #         continue
            #     warehouse_entry = warehouse_entry[0][0]

            #     # Update the move source warehouse entry
            #     executeQuery("accountant", f"UPDATE `material_moves` SET `source_warehouse_entry_id` = {warehouse_entry} WHERE `id` = {move_id}")

            # moves from materials being transferred between warehouses
            cols_dict={
                "source_warehouse_entry_id":"source_warehouse_entry_id",
                "source_warehouse_id":"source_warehouse",
                "destination_warehouse_entry_id":"destination_warehouse_entry_id",
                "target_warehouse_id":"target_warehouse",
                "quantity":"quantity",
                "unit_id":"unit",
                "date":"date_col"
            }

            factory_materials_transfer_moves_query = "SELECT `moves`.`source_warehouse_entry_id`, `moves`.`source_warehouse_id`, `moves`.`destination_warehouse_entry_id`, `moves`.`target_warehouse_id`, `moves`.`quantity`, `units`.`id` AS `unit_id`, `moves`.`date` FROM `moves` JOIN `codes` ON `codes`.`id` = `moves`.`material_id` JOIN `units` ON `units`.`id` = `codes`.`unit_id` WHERE `moves`.`state` = 'done'"
            table1_info = [factory_materials_transfer_moves_query, 'factory']
            table2_info = ['material_moves', 'accountant']

            fks=[]
            fks.append([1, 'warehouseslist', 'warehouseslist', ['id', 'id'], ['code_name', 'codename'], False])
            fks.append([3, 'units', 'units', ['id', 'id'], ['name', 'name'], True])

            additional_columns = {"origin":'transfer'}
            
            moves = transfer_data_between_tables(table1_info, table2_info, cols_dict, fks=fks, result=['id', 'source_warehouse_entry_id', 'source_warehouse_id', 'destination_warehouse_entry_id', 'target_warehouse_id'], additional_columns=additional_columns)

            for move in moves:
                move_id = move[0][0]
                source_warehouse_entry_id = move[0][1]
                source_warehouse_id = move[0][2]
                destination_warehouse_entry_id = move[0][3]
                target_warehouse_id = move[0][4]

                # Get the warehouse codename in the factory
                source_warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {source_warehouse_id}")
                if not source_warehouse_codename:
                    raise Exception(f"Warehouse {source_warehouse_id} is not synced")
                source_warehouse_codename = source_warehouse_codename[0][0]

                # Get the warehouse entry id in the accountant
                source_warehouse_entry = executeQuery("accountant", f"SELECT `{source_warehouse_codename}`.`id` FROM `{source_warehouse_codename}` WHERE `{source_warehouse_codename}`.`factory_id` = {source_warehouse_entry_id}")
                if not source_warehouse_entry:
                    continue
                source_warehouse_entry = source_warehouse_entry[0][0]
                
                # Get the warehouse codename in the factory
                target_warehouse_codename = executeQuery("factory", f"SELECT `warehouseslist`.`code_name` FROM `warehouseslist` WHERE `warehouseslist`.`id` = {target_warehouse_id}")
                if not target_warehouse_codename:
                    raise Exception(f"Warehouse {target_warehouse_id} is not synced")
                target_warehouse_codename = target_warehouse_codename[0][0]
                
                # Get the warehouse entry id in the accountant
                target_warehouse_entry = executeQuery("accountant", f"SELECT `{target_warehouse_codename}`.`id` FROM `{target_warehouse_codename}` WHERE `{target_warehouse_codename}`.`factory_id` = {destination_warehouse_entry_id}")
                if not target_warehouse_entry:
                    continue
                target_warehouse_entry = target_warehouse_entry[0][0]

                # Update the move destination warehouse entry
                executeQuery("accountant", f"UPDATE `material_moves` SET `source_warehouse_entry_id` = {source_warehouse_entry} AND `destination_warehouse_entry_id` = {target_warehouse_entry} WHERE `id` = {move_id}")
                
        # If everything went well, commit the transactions
        self.accountant_cursor.execute("COMMIT")
        if self.factory_connection and self.factory_connection.is_connected():
            self.factory_cursor.execute("COMMIT")
            
            win32api.MessageBox(None, self.language_manager.translate("SYNC_SUCCESS"), self.language_manager.translate("SUCCESS"), win32con.MB_OK)
        
        # except Exception as e:
        #     # Roll back both transactions if an error occurs
        #     self.accountant_cursor.execute("ROLLBACK")
        #     if self.factory_connection and self.factory_connection.is_connected():
        #         self.factory_cursor.execute("ROLLBACK")

        #     print(e)
        #     win32api.MessageBox(None, str(e), self.language_manager.translate("ERROR"), win32con.MB_OK | win32con.MB_ICONERROR)
