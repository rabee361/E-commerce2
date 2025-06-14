import os
import traceback
import mysql.connector
from datetime import date
from mysql.connector.locales.eng import client_error

class MysqlConnector:
    is_connected_to_database = False  # True if connected to database
    is_connected_to_server = False  # True if connected to server. used only in class.

    conn = ''
    filemanager = ''

    host = ''
    port = ''
    username = ''
    password = ''

    def __init__(self, filemanager):
        super().__init__()
        self.filemanager = filemanager

    def connectToServer(self):
        self.disconnectDatabase()
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        database_settings_file = os.path.join(epsilon_dir, 'dbs.dat')

        if os.path.isfile(database_settings_file):
            try:
                print("Connecting to server...")
                json_data = self.filemanager.readJsonFile(database_settings_file)
                self.server_address = str(json_data['connection_info'][0]['server'])
                self.port = str(json_data['connection_info'][0]['port'])
                self.username = str(json_data['connection_info'][0]['username'])
                self.password = str(json_data['connection_info'][0]['password'])

                self.conn = mysql.connector.connect(host=self.server_address, port=int(self.port), user=self.username,passwd=self.password, use_unicode=True, charset="utf8",auth_plugin='mysql_native_password')
                self.is_connected_to_server = True

                print("Connected to server.")

            except Exception as e:
                print("Unable to connect to remote server database. - " + str(e))
                traceback.print_exc()
        else:
            print("Unable to read connection settings file.")

    def getDatabasesList(self):
        databases = []
        if self.is_connected_to_server:
            try:
                curser = self.conn.cursor()
                curser.execute("SHOW DATABASES")
                for item in curser:
                    if ('eps_acc_' in str(item)):
                        databases.append(str(item))
            except Exception as e:
                print("Unable to get databases list. - " + str(e))
                traceback.print_exc()
        else:
            print("Unable to get databases list. Not Connected to server.")

        return databases

    def connectToDatabase(self, database_name):
        if self.is_connected_to_server:
            try:
                print("Connecting to database...")
                self.conn = mysql.connector.connect(host=self.server_address, port=self.port, user=self.username,
                                                    passwd=self.password, database=database_name, use_unicode=True,
                                                    charset="utf8")
                print("Connected to database.")
                self.is_connected_to_database = True
                self.checkDatabaseTables()

            except Exception as e:
                print("Unable to connect to database - " + str(e))
                traceback.print_exc()
        else:
            print("Unable to connecto to database. Not connected to server. ")

    
    def createDatabase(self, db_name):
        if self.is_connected_to_server:
            try:
                c = self.conn.cursor()
                new_db_name = "eps_acc_" + db_name  # eps (epsilon) prefix, acc (accountant) prefix.
                c.execute("CREATE DATABASE `" + str(new_db_name) + "` CHARACTER SET utf8 COLLATE utf8_general_ci;")
                self.conn = mysql.connector.connect(host=self.host, user=self.username, passwd=self.password, database=new_db_name, use_unicode=True, charset="utf8")
                self.is_connected_to_database = True
                self.checkDatabaseTables()
            except Exception as e:
                print(e)
        else:
            print("Unable to create database. Not connected to server.")

    def checkDatabaseTables(self):
        if self.is_connected_to_database:
            try:
                c = self.conn.cursor(buffered=True)
                print("Checking tables...")
                

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `currencies` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL, `symbol` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL, `parts` varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL, `parts_relation` double DEFAULT NULL, PRIMARY KEY (`id`), UNIQUE KEY `name` (`name`)) ENGINE=InnoDB AUTO_INCREMENT=5 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `units` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `name` VARCHAR(50) NOT NULL UNIQUE) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `financial_statement` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `final_financial_statement` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `final_financial_statement` (`final_financial_statement`), CONSTRAINT `financial_statement_ibfk_1` FOREIGN KEY (`final_financial_statement`) REFERENCES `financial_statement` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `cost_centers` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `notes` varchar(500) DEFAULT NULL, `type_col` varchar(50) NOT NULL, `parent` int(11) DEFAULT NULL, `changable_division_factors` tinyint(1) NOT NULL DEFAULT '0', `date_col` datetime NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `parent` (`parent`), CONSTRAINT `cost_centers_ibfk_1` FOREIGN KEY (`parent`) REFERENCES `cost_centers` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `financial_statement_block` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `financial_statement_id` int(11) NOT NULL , PRIMARY KEY (`id`), CONSTRAINT `financial_statement_block_ibfk_1` FOREIGN KEY (`financial_statement_id`) REFERENCES `financial_statement` (`id`) ON DELETE CASCADE) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `accounts` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `code` varchar(50) DEFAULT NULL, `details` varchar(50) DEFAULT NULL, `parent_account` int(11) DEFAULT NULL, `date_col` timestamp NULL DEFAULT CURRENT_TIMESTAMP, `type_col` varchar(25) NOT NULL DEFAULT 'normal', `final_account` int(11) DEFAULT NULL, `financial_statement` int(11) DEFAULT NULL, `financial_statement_block` int(11) DEFAULT NULL, `force_cost_center` boolean NOT NULL DEFAULT FALSE, `default_cost_center` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `parent_account` (`parent_account`), KEY `final_account` (`final_account`), KEY `financial_statement` (`financial_statement`), KEY `financial_statement_block` (`financial_statement_block`), KEY `default_cost_center` (`default_cost_center`), CONSTRAINT `accounts_ibfk_1` FOREIGN KEY (`parent_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `accounts_ibfk_2` FOREIGN KEY (`final_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `accounts_ibfk_3` FOREIGN KEY (`financial_statement`) REFERENCES `financial_statement` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `accounts_ibfk_4` FOREIGN KEY (`financial_statement_block`) REFERENCES `financial_statement_block` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `accounts_ibfk_5` FOREIGN KEY (`default_cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `warehouseslist` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `code` VARCHAR(50) DEFAULT NULL, `include_in_stock` tinyint(1) DEFAULT '1',  `name` VARCHAR(50) NOT NULL, `codename` VARCHAR(50), `date_col` DATETIME DEFAULT CURRENT_TIMESTAMP, `parent_warehouse` int(11) DEFAULT NULL, `account` int(11) DEFAULT NULL, `address` VARCHAR(100) DEFAULT NULL, `manager` VARCHAR(50) DEFAULT NULL, `notes` VARCHAR(200) DEFAULT NULL, `capacity` DOUBLE DEFAULT NULL, `capacity_unit` int(11) DEFAULT NULL, FOREIGN KEY (`account`) REFERENCES `accounts` (`id`), FOREIGN KEY (`parent_warehouse`) REFERENCES `warehouseslist` (`id`), FOREIGN KEY (`capacity_unit`) REFERENCES `units` (`id`), UNIQUE KEY `unique_name` (`name`), UNIQUE KEY `unique_codename` (`codename`)) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `manufacture_halls` (`id` int(11) NOT NULL AUTO_INCREMENT, `warehouse_id` int(11) NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), UNIQUE KEY `warehouse_id` (`warehouse_id`), CONSTRAINT `manufacture_halls_ibfk_1` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `groups` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `name` VARCHAR(50) NOT NULL, `code` VARCHAR(50) DEFAULT NULL, `parent_group` int(11) DEFAULT NULL, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`parent_group`) REFERENCES `groups` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `prices` (`id` int(11) NOT NULL AUTO_INCREMENT, `price` varchar(50) NOT NULL, `locked` tinyint(1) NOT NULL DEFAULT '0', PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                # Fix the materials table creation SQL - move ENGINE clause outside the constraints
                c.execute("""
                    CREATE TABLE IF NOT EXISTS `materials` (
                        `id` int(11) NOT NULL AUTO_INCREMENT,
                        `code` varchar(50) DEFAULT NULL,
                        `name` varchar(50) DEFAULT NULL,
                        `group_col` int(11) DEFAULT NULL,
                        `specs` varchar(500) DEFAULT NULL,
                        `size_col` varchar(50) DEFAULT NULL,
                        `manufacturer` varchar(50) DEFAULT NULL,
                        `color` varchar(50) DEFAULT NULL,
                        `origin` varchar(50) DEFAULT NULL,
                        `quality` varchar(50) DEFAULT NULL,
                        `type_col` varchar(50) DEFAULT NULL,
                        `model` varchar(50) DEFAULT NULL,
                        `unit1` int(11) DEFAULT NULL,
                        `unit2` int(11) DEFAULT NULL,
                        `unit3` int(11) DEFAULT NULL,
                        `default_unit` int(11) NOT NULL DEFAULT '1',
                        `current_quantity` double DEFAULT NULL,
                        `max_quantity` double DEFAULT NULL,
                        `min_quantity` double DEFAULT NULL,
                        `request_limit` double DEFAULT NULL,
                        `gift` double DEFAULT NULL,
                        `gift_for` double DEFAULT NULL,
                        `price1_desc` int(11) DEFAULT NULL,
                        `price1_1` double DEFAULT NULL,
                        `price1_1_unit` varchar(50) DEFAULT NULL,
                        `price1_2` double DEFAULT NULL,
                        `price1_2_unit` varchar(50) DEFAULT NULL,
                        `price1_3` double DEFAULT NULL,
                        `price1_3_unit` varchar(50) DEFAULT NULL,
                        `price2_desc` int(11) DEFAULT NULL,
                        `price2_1` double DEFAULT NULL,
                        `price2_1_unit` varchar(50) DEFAULT NULL,
                        `price2_2` double DEFAULT NULL,
                        `price2_2_unit` varchar(50) DEFAULT NULL,
                        `price2_3` double DEFAULT NULL,
                        `price2_3_unit` varchar(50) DEFAULT NULL,
                        `price3_desc` int(11) DEFAULT NULL,
                        `price3_1` double DEFAULT NULL,
                        `price3_1_unit` varchar(50) DEFAULT NULL,
                        `price3_2` double DEFAULT NULL,
                        `price3_2_unit` varchar(50) DEFAULT NULL,
                        `price3_3` double DEFAULT NULL,
                        `price3_3_unit` varchar(50) DEFAULT NULL,
                        `price4_desc` int(11) DEFAULT NULL,
                        `price4_1` double DEFAULT NULL,
                        `price4_1_unit` varchar(50) DEFAULT NULL,
                        `price4_2` double DEFAULT NULL,
                        `price4_2_unit` varchar(50) DEFAULT NULL,
                        `price4_3` double DEFAULT NULL,
                        `price4_3_unit` varchar(50) DEFAULT NULL,
                        `price5_desc` int(11) DEFAULT NULL,
                        `price5_1` double DEFAULT NULL,
                        `price5_1_unit` varchar(50) DEFAULT NULL,
                        `price5_2` double DEFAULT NULL,
                        `price5_2_unit` varchar(50) DEFAULT NULL,
                        `price5_3` double DEFAULT NULL,
                        `price5_3_unit` varchar(50) DEFAULT NULL,
                        `price6_desc` int(11) DEFAULT NULL,
                        `price6_1` double DEFAULT NULL,
                        `price6_1_unit` varchar(50) DEFAULT NULL,
                        `price6_2` double DEFAULT NULL,
                        `price6_2_unit` varchar(50) DEFAULT NULL,
                        `price6_3` double DEFAULT NULL,
                        `price6_3_unit` varchar(50) DEFAULT NULL,
                        `expiray` int(11) DEFAULT NULL,
                        `groupped` tinyint(1) NOT NULL DEFAULT '0',
                        `yearly_required` double DEFAULT NULL,
                        `work_hours` double DEFAULT NULL,
                        `standard_unit3_quantity` double DEFAULT NULL,
                        `standard_unit2_quantity` double DEFAULT NULL,
                        `standard_unit1_quantity` double DEFAULT NULL,
                        `manufacture_hall` int(11) DEFAULT NULL,
                        `discount_account` int(11) DEFAULT NULL,
                        `addition_account` int(11) DEFAULT NULL,
                        PRIMARY KEY (`id`),
                        KEY `price1_desc` (`price1_desc`),
                        KEY `price2_desc` (`price2_desc`),
                        KEY `price3_desc` (`price3_desc`),
                        KEY `price4_desc` (`price4_desc`),
                        KEY `price5_desc` (`price5_desc`),
                        KEY `price6_desc` (`price6_desc`),
                        KEY `unit1` (`unit1`),
                        KEY `unit2` (`unit2`),
                        KEY `unit3` (`unit3`),
                        KEY `group_col` (`group_col`),
                        KEY `manufacture_hall` (`manufacture_hall`),
                        KEY `discount_account` (`discount_account`),
                        KEY `addition_account` (`addition_account`),
                        CONSTRAINT `materials_ibfk_1` FOREIGN KEY (`price1_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_2` FOREIGN KEY (`price2_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_3` FOREIGN KEY (`price3_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_4` FOREIGN KEY (`price4_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_5` FOREIGN KEY (`price5_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_6` FOREIGN KEY (`price6_desc`) REFERENCES `prices` (`id`) ON UPDATE CASCADE,
                        CONSTRAINT `materials_ibfk_7` FOREIGN KEY (`unit1`) REFERENCES `units` (`id`),
                        CONSTRAINT `materials_ibfk_8` FOREIGN KEY (`unit2`) REFERENCES `units` (`id`),
                        CONSTRAINT `materials_ibfk_9` FOREIGN KEY (`unit3`) REFERENCES `units` (`id`),
                        CONSTRAINT `materials_ibfk_10` FOREIGN KEY (`group_col`) REFERENCES `groups` (`id`),
                        CONSTRAINT `materials_ibfk_11` FOREIGN KEY (`manufacture_hall`) REFERENCES `manufacture_halls` (`id`),
                        CONSTRAINT `materials_ibfk_12` FOREIGN KEY (`discount_account`) REFERENCES `accounts` (`id`),
                        CONSTRAINT `materials_ibfk_13` FOREIGN KEY (`addition_account`) REFERENCES `accounts` (`id`)
                    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
                """)
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `users` (`id` int(11) NOT NULL AUTO_INCREMENT, `username` varchar(200) NOT NULL UNIQUE, `password` varchar(300) NOT NULL, `created_at` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `clients` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) DEFAULT NULL, `governorate` varchar(50) DEFAULT NULL, `address` varchar(50) DEFAULT NULL, `email` varchar(50) DEFAULT NULL, `phone1` varchar(50) DEFAULT NULL, `phone2` varchar(50) DEFAULT NULL, `phone3` varchar(50) DEFAULT NULL, `phone4` varchar(50) DEFAULT NULL, `client_type` varchar(50) DEFAULT NULL, `deleted` tinyint(1) DEFAULT 0, PRIMARY KEY (`id`)) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `invoice_types` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL UNIQUE, `type_col` varchar(50) NOT NULL, `returned` tinyint(1) NOT NULL DEFAULT '0', PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `invoices` (`id` int(11) NOT NULL AUTO_INCREMENT, `type_col` int(11) NOT NULL, `number` int(11) DEFAULT NULL UNIQUE, `client` int(11) DEFAULT NULL, `client_account` int(11) DEFAULT NULL, `payment` varchar(50) DEFAULT NULL, `paid` tinyint(1) DEFAULT NULL, `currency` int(11) DEFAULT NULL, `cost_center` int(11) DEFAULT NULL, `warehouse` int(11) DEFAULT NULL, `cost_account` int(11) DEFAULT NULL, `gifts_account` int(11) DEFAULT NULL, `added_value_account` int(11) DEFAULT NULL, `monetary_account` int(11) DEFAULT NULL, `materials_account` int(11) DEFAULT NULL, `stock_account` int(11) DEFAULT NULL, `gifts_opposite_account` int(11) DEFAULT NULL, `statement_col` varchar(500) DEFAULT NULL, `date_col` DATE NOT NULL, `origin_id` int(11) DEFAULT NULL, PRIMARY KEY (`id`), `factory_id` int DEFAULT NULL, FOREIGN KEY (`type_col`) REFERENCES `invoice_types` (`id`), FOREIGN KEY (`origin_id`) REFERENCES `invoices` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `exchange_prices` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `currency1` int(11) NOT NULL, `currency2` int(11) NOT NULL, `exchange` DOUBLE NOT NULL DEFAULT 1, `date_col` DATE,  `currency1_ordered` int(11) as (LEAST(currency1, currency2)) STORED,  `currency2_ordered` int(11) as (GREATEST(currency2, currency1)) STORED,  unique key `unqBi_test` (`currency1_ordered`, `currency2_ordered`, `date_col`)) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `invoice_items` ( `id` int(11) NOT NULL AUTO_INCREMENT, `invoice_id` int(11) NOT NULL, `material_id` int(11) NOT NULL, `quantity1` double DEFAULT NULL, `unit1_id` int(11) DEFAULT NULL, `quantity2` double DEFAULT NULL, `unit2_id` int(11) DEFAULT NULL, `quantity3` float DEFAULT NULL, `unit3_id` int(11) DEFAULT NULL, `price_type_id` int(11) DEFAULT NULL, `unit_price` double NOT NULL, `currency_id` int(11) NOT NULL, `equilivance_price` double NOT NULL, `exchange_id` int(11) DEFAULT NULL, `discount` double DEFAULT NULL, `discount_percent` double DEFAULT NULL, `addition` double DEFAULT NULL, `addition_percent` double DEFAULT NULL, `added_value` double DEFAULT NULL, `gifts` double DEFAULT NULL, `gifts_value` double DEFAULT NULL, `gifts_discount` double DEFAULT NULL, `warehouse_id` int(11) DEFAULT NULL, `cost_center_id` int(11) DEFAULT NULL, `notes` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL, `deal_id` int(11) DEFAULT NULL, `item_discount_account` int(11) DEFAULT NULL, `item_addition_account` int(11) DEFAULT NULL, `receipt_doc_id` int(11) DEFAULT NULL, `production_date` DATE DEFAULT NULL, `expire_date` DATE DEFAULT NULL, `factory_id` int DEFAULT NULL, PRIMARY KEY (`id`), UNIQUE KEY `deal_id` (`deal_id`), KEY `cost_center_id` (`cost_center_id`), KEY `currency_id` (`currency_id`), KEY `exchange_id` (`exchange_id`), KEY `material_id` (`material_id`), KEY `price_type_id` (`price_type_id`), KEY `invoice_id` (`invoice_id`), KEY `item_discount_account` (`item_discount_account`), KEY `item_addition_account` (`item_addition_account`), KEY `receipt_doc_id` (`receipt_doc_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `invoices_discounts_additions` (`id` int(11) NOT NULL AUTO_INCREMENT, `invoice_id` int(11) NOT NULL, `type_col` varchar(50) NOT NULL, `account` int(11) NOT NULL, `cost_center` int(11) DEFAULT NULL, `currency` int(11) DEFAULT NULL, `exchange` int(11) DEFAULT NULL, `opposite_account` int(11) DEFAULT NULL, `equilivance` double DEFAULT NULL, `percent` tinyint DEFAULT 0, PRIMARY KEY (`id`), KEY `cost_center` (`cost_center`), KEY `currency` (`currency`), KEY `exchange` (`exchange`), KEY `opposite_account` (`opposite_account`), KEY `invoices_discounts_additions_ibfk_6` (`account`), KEY `invoices_discounts_additions_ibfk_7` (`invoice_id`), CONSTRAINT `invoices_discounts_additions_ibfk_1` FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `invoices_discounts_additions_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `invoices_discounts_additions_ibfk_4` FOREIGN KEY (`exchange`) REFERENCES `exchange_prices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `invoices_discounts_additions_ibfk_5` FOREIGN KEY (`opposite_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `invoices_discounts_additions_ibfk_6` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `invoices_discounts_additions_ibfk_7` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `expenses_types` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(25) COLLATE utf8mb4_unicode_ci NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `calculated_in_manufacture` int(11) NOT NULL DEFAULT '0', PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `opposite_account_id` (`opposite_account_id`), CONSTRAINT `expenses_types_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`), CONSTRAINT `expenses_types_ibfk_2` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `expenses` (`id` int(11) NOT NULL AUTO_INCREMENT, `time_slot` varchar(25) NOT NULL DEFAULT 'month', `value_col` DOUBLE NOT NULL, `year_col` varchar(50) NOT NULL, `month_col` varchar(50) DEFAULT '1', `expense_type` int(11) NOT NULL, `currency` int(11) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `unqBi_test` (`year_col`, `month_col`, `expense_type`) USING BTREE, KEY `expense_type` (`expense_type`), KEY `currency` (`currency`), CONSTRAINT `expenses_ibfk_1` FOREIGN KEY (`expense_type`) REFERENCES `expenses_types` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `expenses_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `expenses_monthly` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `expenses` DOUBLE NOT NULL, `year_col` VARCHAR(50) NOT NULL, `month_col` VARCHAR(50) NOT NULL DEFAULT '1', `type_col` VARCHAR(50)) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `manufacture` ( `id` int NOT NULL AUTO_INCREMENT, `pullout_date` DATE DEFAULT NULL, `date_col` DATE DEFAULT NULL, `expenses_type` varchar(50) NOT NULL, `material_pricing_method` varchar(50) NOT NULL, `currency` int NOT NULL, `expenses_cost` DECIMAL(10,2) DEFAULT NULL, `machines_operation_cost` DECIMAL(10,2) DEFAULT 0, `salaries_cost` DECIMAL(10,2) DEFAULT NULL, `mid_account` int NOT NULL, `mid_account_input` int NOT NULL, `account` int NOT NULL, `composition_materials_cost` DECIMAL(10,2) DEFAULT NULL, `quantity_unit_expenses` int DEFAULT NULL, `expenses_distribution` varchar(50) DEFAULT NULL, `state_col` varchar(20) NOT NULL DEFAULT 'active', `factory_id` int DEFAULT NULL, `ingredients_pullout_method` varchar(50) DEFAULT NULL, `ingredients_pullout_account` int DEFAULT NULL, `working_hours` DECIMAL(10,2) DEFAULT NULL, PRIMARY KEY (`id`), KEY `mid_account` (`mid_account`), KEY `mid_account_input` (`mid_account_input`), KEY `account` (`account`), KEY `quantity_unit_expenses` (`quantity_unit_expenses`), KEY `manufacture_ibfk_1` (`currency`), CONSTRAINT `manufacture_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `manufacture_ibfk_3` FOREIGN KEY (`mid_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `manufacture_ibfk_4` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `manufacture_ibfk_5` FOREIGN KEY (`quantity_unit_expenses`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `manufacture_ibfk_6` FOREIGN KEY (`ingredients_pullout_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `manufacture_ibfk_7` FOREIGN KEY (`mid_account_input`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `compositions` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `material` int(11) NOT NULL, `name` varchar(250) NOT NULL, `factory_dossier_id` int(11) DEFAULT NULL, FOREIGN KEY (`material`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `groupped_materials_composition` (`id` int(11) NOT NULL AUTO_INCREMENT, `groupped_material_id` int(11) NOT NULL, `composition_material_id` int(11) NOT NULL, `composition_id` int(11) NOT NULL, `quantity` double DEFAULT NULL, `unit` int(50) NOT NULL, PRIMARY KEY (`id`), KEY `composition_material_id` (`composition_material_id`), KEY `groupped_material_id` (`groupped_material_id`), KEY `unit` (`unit`), KEY `composition_id` (`composition_id`), CONSTRAINT `groupped_materials_composition_ibfk_2` FOREIGN KEY (`groupped_material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `groupped_materials_composition_ibfk_3` FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `groupped_materials_composition_ibfk_4` FOREIGN KEY (`composition_id`) REFERENCES `compositions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `manufacture_materials` ( `id` int(11) NOT NULL AUTO_INCREMENT, `manufacture_id` int(11) NOT NULL, `composition_item_id` int(11) NOT NULL, `standard_quantity` double DEFAULT NULL, `required_quantity` double DEFAULT NULL, `unit` int(50) DEFAULT NULL, `unit_cost` int(11) DEFAULT NULL, `row_type` varchar(10) NOT NULL, `warehouse_id` int(11) DEFAULT NULL, `warehouse_account_id` int(11) DEFAULT NULL, `pulled_quantity` double DEFAULT NULL, `shortage` double DEFAULT NULL, `currency` int(11) DEFAULT NULL, `warehouse_quantity` double DEFAULT NULL, PRIMARY KEY (`id`), KEY `manufacture_id` (`manufacture_id`), KEY `unit` (`unit`), KEY `manufacture_materials_ibfk_2` (`composition_item_id`), KEY `warehouse_id` (`warehouse_id`), KEY `warehouse_account_id` (`warehouse_account_id`), KEY `currency` (`currency`), CONSTRAINT `manufacture_materials_ibfk_1` FOREIGN KEY (`manufacture_id`) REFERENCES `manufacture` (`id`) ON DELETE CASCADE, CONSTRAINT `manufacture_materials_ibfk_2` FOREIGN KEY (`composition_item_id`) REFERENCES `groupped_materials_composition` (`id`), CONSTRAINT `manufacture_materials_ibfk_3` FOREIGN KEY (`unit`) REFERENCES `units` (`id`), CONSTRAINT `manufacture_materials_ibfk_4` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`), CONSTRAINT `manufacture_materials_ibfk_6` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute( 
                    "CREATE TABLE IF NOT EXISTS `manufacture_produced_materials` ( `id` int(11) NOT NULL AUTO_INCREMENT, `manufacture_id` int(11) NOT NULL, `material_id` int(11) NOT NULL, `quantity1` double NOT NULL,`damaged_quantity1` double DEFAULT NULL, `unit1` int(11) NOT NULL, `quantity2` double DEFAULT NULL, `damaged_quantity2` double DEFAULT NULL, `unit2` int(11) DEFAULT NULL, `quantity3` double DEFAULT NULL, `damaged_quantity3` double DEFAULT NULL, `unit3` int(11) DEFAULT NULL, `working_hours` double NOT NULL, `batch` int(11) DEFAULT NULL, `referential_quantity1` double NOT NULL, `referential_quantity2` double DEFAULT NULL, `referential_quantity3` double DEFAULT NULL, `referential_working_hours` double DEFAULT NULL, `production_date` DATE NOT NULL, `warehouse` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `material_id` (`material_id`), KEY `unit1` (`unit1`), KEY `unit2` (`unit2`), KEY `unit3` (`unit3`), KEY `warehouse` (`warehouse`), CONSTRAINT `manufacture_produced_materials_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), CONSTRAINT `manufacture_produced_materials_ibfk_2` FOREIGN KEY (`unit1`) REFERENCES `units` (`id`), CONSTRAINT `manufacture_produced_materials_ibfk_3` FOREIGN KEY (`unit2`) REFERENCES `units` (`id`), CONSTRAINT `manufacture_produced_materials_ibfk_4` FOREIGN KEY (`unit3`) REFERENCES `units` (`id`), CONSTRAINT `manufacture_produced_materials_ibfk_5` FOREIGN KEY (`warehouse`) REFERENCES `warehouseslist` (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `machines` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(250) NOT NULL, `years_age` double DEFAULT NULL, `estimated_waste_value` double DEFAULT NULL, `estimated_waste_currency` int(11) DEFAULT NULL, `estimated_waste_account` int(11) DEFAULT NULL, `invoice_item_id` int(11) DEFAULT NULL, `notes` varchar(500) DEFAULT NULL, `account` int(11) DEFAULT NULL, `opposite_account` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `invoice_item_id` (`invoice_item_id`), KEY `estimated_waste_account` (`estimated_waste_account`), KEY `estimated_waste_currency` (`estimated_waste_currency`), KEY `account` (`account`), KEY `opposite_account` (`opposite_account`), CONSTRAINT `machines_ibfk_1` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `machines_ibfk_2` FOREIGN KEY (`estimated_waste_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `machines_ibfk_3` FOREIGN KEY (`estimated_waste_currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `machines_ibfk_4` FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `machines_ibfk_5` FOREIGN KEY (`opposite_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `machine_modes` (`id` int(11) NOT NULL AUTO_INCREMENT, `machine_id` int(11) NOT NULL, `name` varchar(250) NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `machine_modes_ibfk_1` (`machine_id`), CONSTRAINT `machine_modes_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `manufacture_machines` ( `id` int(11) NOT NULL AUTO_INCREMENT, `manufacture_id` int(11) NOT NULL, `machine_id` int(11) NOT NULL, `mode_id` int(11) NOT NULL, `duration` double NOT NULL, `exclusive` tinyint(11) NOT NULL, `exclusive_percent` int(11) NOT NULL, PRIMARY KEY (`id`), KEY `machine_id` (`machine_id`), KEY `mode_id` (`mode_id`), KEY `manufacture_id` (`manufacture_id`), CONSTRAINT `manufacture_machines_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`), CONSTRAINT `manufacture_machines_ibfk_2` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`), CONSTRAINT `manufacture_machines_ibfk_3` FOREIGN KEY (`manufacture_id`) REFERENCES `manufacture` (`id`) ON DELETE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `production_lines` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(250) NOT NULL, `notes` varchar(500) DEFAULT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `machine_production_lines` (`id` int(11) NOT NULL AUTO_INCREMENT, `machine_id` int(11) NOT NULL, `production_line_id` int(11) NOT NULL, `machine_notes` varchar(500) DEFAULT NULL, PRIMARY KEY (`id`), KEY `machine_id` (`machine_id`), KEY `production_line_id` (`production_line_id`), CONSTRAINT `machine_production_lines_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `machine_production_lines_ibfk_2` FOREIGN KEY (`production_line_id`) REFERENCES `production_lines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `machine_maintenance` (`id` int(11) NOT NULL AUTO_INCREMENT, `machine_id` int(11) NOT NULL, `name` VARCHAR(250) NOT NULL, `start_date` DATETIME DEFAULT NULL, `end_date` DATETIME DEFAULT NULL, `maintenance_type` VARCHAR(50) DEFAULT NULL, `cost` DOUBLE DEFAULT NULL, `statment_col` VARCHAR(500) DEFAULT NULL, `account` INTEGER DEFAULT NULL, `opposite_account` INTEGER DEFAULT NULL, PRIMARY KEY (`id`), KEY `machine_id` (`machine_id`), KEY `account` (`account`), KEY `opposite_account` (`opposite_account`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `maintenance_materials` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` VARCHAR(250) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `maintenance_operation_materials` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(250) NOT NULL, `maintenance_operation` int(11) NOT NULL, `quantity` double, `unit` int(11), `maintenance_material_id` int(11), PRIMARY KEY (`id`), KEY `maintenance_operation` (`maintenance_operation`), KEY `unit` (`unit`), KEY `maintenance_material_id` (`maintenance_material_id`), CONSTRAINT `maintenance_operation_materials_ibfk_1` FOREIGN KEY (`maintenance_operation`) REFERENCES `machine_maintenance` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `maintenance_operation_materials_ibfk_2` FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `maintenance_operation_materials_ibfk_3` FOREIGN KEY (`maintenance_material_id`) REFERENCES `maintenance_materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `aggregator` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `material` int(11) NOT NULL, `ammount` int(11)) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `percent_plans` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `material` int(11) NOT NULL, `priority` int(11) NOT NULL DEFAULT '999999', `percent` DOUBLE NOT NULL DEFAULT '0') CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `plans` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `material` int(11) NOT NULL, `priority` int(11) NOT NULL DEFAULT '999999', `percent` int(11) NOT NULL DEFAULT '0') CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `variables` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `variable` VARCHAR(50), `value_col` VARCHAR(50)) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `cost_materials` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `process_id` int(11) NOT NULL, `material` int(11) NOT NULL, `price_sp` FLOAT, `price_usd` FLOAT, `standard_quantity` FLOAT, `required_quantity` FLOAT, `unit` VARCHAR(50)) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `payments` (`id` int(11) NOT NULL AUTO_INCREMENT, `invoice_id` int(11) DEFAULT NULL, `client_id` int(11) NOT NULL, `ammount` double NOT NULL, `currency_id` int(11) NOT NULL, `exchange_id` int(11) DEFAULT NULL, `equilivance` double NOT NULL, `date_col` DATE NOT NULL, `notes` varchar(500)  DEFAULT NULL, PRIMARY KEY (`id`), KEY `currency_id` (`currency_id`), KEY `exchange_id` (`exchange_id`), KEY `invoice_id` (`invoice_id`), KEY `client_id` (`client_id`), CONSTRAINT `payments_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `payments_ibfk_2` FOREIGN KEY (`exchange_id`) REFERENCES `exchange_prices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `payments_ibfk_3` FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `payments_ibfk_4` FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `sales_targets` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `material` int(11) NOT NULL , `year_col` int(11) NOT NULL, `month_col` int(11) NOT NULL, `location` VARCHAR(50), `target` int(11) NOT NULL) CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `settings` (id int(11) NOT NULL AUTO_INCREMENT,  name varchar(50) COLLATE utf8mb4_unicode_ci NOT NULL,  value_col varchar(50) COLLATE utf8mb4_unicode_ci DEFAULT NULL, PRIMARY KEY (id),  UNIQUE KEY name (name)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `user_settings` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `value_col` varchar(50) DEFAULT NULL, `user_id` int(11) NOT NULL, PRIMARY KEY (`id`), KEY `user_id` (`user_id`), CONSTRAINT `user_settings_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `clients_accounts` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `used_price` int(11) DEFAULT NULL, `discount` DOUBLE DEFAULT NULL, `payment_method` VARCHAR(50), `days_count` int(11) DEFAULT NULL, `day_col` VARCHAR(50) DEFAULT NULL, `payment_date` DATE DEFAULT NULL, `client_account_id` int(11) DEFAULT NULL, `discount_account_id` int(11) DEFAULT NULL, `tax_account_id` int(11) DEFAULT NULL, `vat_account_id` int(11) DEFAULT NULL, `tax_exempt` BOOLEAN DEFAULT 0, `client_id` int(11) UNIQUE NOT NULL, `extra_account_id` int(11) DEFAULT NULL, FOREIGN KEY (`used_price`) REFERENCES `prices`(`id`), FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`client_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`discount_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`tax_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`vat_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`extra_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `payment_conditions` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `client_account_id` int(11) NOT NULL, `day_number` int(11) NOT NULL, `discount_percent` int(11) NULL DEFAULT NULL, `discount_value` int(11) NULL DEFAULT NULL, `discount_account_id` int(11) NULL DEFAULT NULL, FOREIGN KEY (`discount_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `units_conversion` (`id` int(11) PRIMARY KEY AUTO_INCREMENT, `unit1` int(11) NOT NULL, `unit2` int(11) NOT NULL, `value_col` DOUBLE NOT NULL DEFAULT 1, `unit1_ordered` int(11) AS (LEAST(`unit1`, `unit2`)), `unit2_ordered` int(11) AS (GREATEST(`unit2`, `unit1`)), UNIQUE KEY `unqBi_test` (`unit1_ordered`, `unit2_ordered`), FOREIGN KEY (`unit1`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (`unit2`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE CASCADE) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `cost_centers_aggregations_distributives` (`id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, `master_cost_center` int(11) NOT NULL, `cost_center` int(11) NOT NULL UNIQUE, `division_factor` DOUBLE NULL DEFAULT NULL, FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE = InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_courses` (`id` int(11) NOT NULL AUTO_INCREMENT, `title` varchar(250) NOT NULL, `providor` varchar(250) NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `cost` double NOT NULL, `currency_id` int(11) NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, `location` varchar(250) NOT NULL, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), CONSTRAINT `hr_courses_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_courses_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_courses_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employment_requests` (`id` int(11) NOT NULL AUTO_INCREMENT, `national_id` varchar(255) DEFAULT NULL, `phone` varchar(255) DEFAULT NULL, `address` varchar(255)  DEFAULT NULL, `name` varchar(255)  NOT NULL, `email` varchar(255) DEFAULT NULL, `birthdate` DATE DEFAULT NULL, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`ID`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employees` (`id` int(11) NOT NULL AUTO_INCREMENT, `employment_request_id` int(11) NOT NULL, `national_id` varchar(255) DEFAULT NULL, `phone` varchar(255) DEFAULT NULL, `address` varchar(255) DEFAULT NULL, `name` varchar(255) DEFAULT NULL, `email` varchar(255) DEFAULT NULL, `birthdate` DATE DEFAULT NULL, `start_date` DATE NOT NULL, `resignation_date` DATE DEFAULT NULL, `bank` varchar(250) DEFAULT NULL, `bank_account_number` varchar(250) DEFAULT NULL, `bank_notes` varchar(250) DEFAULT NULL, `photo` MEDIUMBLOB NULL, PRIMARY KEY (`id`), UNIQUE KEY `employment_request_id` (`employment_request_id`), CONSTRAINT `hr_employees_ibfk_1` FOREIGN KEY (`employment_request_id`) REFERENCES `hr_employment_requests` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_course_employees` (`id` int(11) NOT NULL AUTO_INCREMENT, `course_id` int(11) NOT NULL, `employee_id` int(11) NOT NULL, `gpa` DOUBLE DEFAULT NULL, PRIMARY KEY (`id`), KEY `course_id` (`course_id`), KEY `employee_id` (`employee_id`), CONSTRAINT `hr_course_employees_ibfk_1` FOREIGN KEY (`course_id`) REFERENCES `hr_courses` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_course_employees_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_departments` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(250) NOT NULL, `day_hours` double NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `notes` varchar(250) DEFAULT NULL, `work_day_friday` tinyint(1) NOT NULL DEFAULT 0, `work_day_tuesday` tinyint(1) NOT NULL DEFAULT 0, `work_day_thursday` tinyint(1) NOT NULL DEFAULT 0, `work_day_wednesday` tinyint(1) NOT NULL DEFAULT 0, `work_day_monday` tinyint(1) NOT NULL DEFAULT 0, `work_day_sunday` tinyint(1) NOT NULL DEFAULT 0, `work_day_saturday` tinyint(1) NOT NULL DEFAULT 0, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `opposite_account_id` (`opposite_account_id`), CONSTRAINT `hr_departments_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_departments_ibfk_2` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_additional_costs` (`id` int(11) NOT NULL AUTO_INCREMENT, `statement_col` varchar(500) NOT NULL, `account_id` int(11) DEFAULT NULL, `department_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `value_col` double NOT NULL, `currency_id` int(11) NOT NULL, `date_col` DATE NOT NULL, `state_col` varchar(10) NOT NULL DEFAULT 'active', PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), KEY `department_id` (`department_id`), CONSTRAINT `hr_additional_costs_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_additional_costs_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_additional_costs_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_additional_costs_ibfk_4` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_departments_finance` (`id` int(11) NOT NULL AUTO_INCREMENT, `department_id` int(11) NOT NULL, `statement_col` varchar(500) NOT NULL, `type_col` varchar(11) NOT NULL, `value_col` double NOT NULL, `currency_id` int(11) NOT NULL, `start_date` DATE NOT NULL, `end_date` DATE DEFAULT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), KEY `employee_id` (`department_id`), CONSTRAINT `hr_departments_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_departments_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_departments_finance_ibfk_3` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_departments_finance_ibfk_4` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_departments_leaves` (`id` int(11) NOT NULL AUTO_INCREMENT, `department_id` int(11) NOT NULL, `statement_col` varchar(250) DEFAULT NULL, `duration_in_hours` double NOT NULL, `duration_in_days` double NOT NULL, `start_date` DATE NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `hr_positions_leaves_ibfk_1` (`department_id`), CONSTRAINT `hr_departments_leaves_ibfk_1` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employee_received_items` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `warehouse_id` int(11) DEFAULT NULL, `material_id` int(11) DEFAULT NULL, `quantity` double DEFAULT NULL, `unit_id` int(11) DEFAULT NULL, `received_date` date DEFAULT NULL, `received` tinyint(1) NOT NULL DEFAULT 0, PRIMARY KEY (`id`), KEY `material_id` (`material_id`), KEY `unit_id` (`unit_id`), KEY `warehouse_id` (`warehouse_id`), KEY `hr_employee_received_items_ibfk_4` (`employee_id`), CONSTRAINT `hr_employee_received_items_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employee_received_items_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employee_received_items_ibfk_3` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employee_received_items_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_positions` (`id` int(11) NOT NULL AUTO_INCREMENT, `position_name` varchar(255) DEFAULT NULL, `salary` double DEFAULT NULL, `currency_id` int(11) DEFAULT NULL, `notes` varchar(255) DEFAULT NULL, PRIMARY KEY (`id`), KEY `currency_id` (`currency_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employees_transfers` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `department_id` int(11) NOT NULL, `position_id` int(11) NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `employee_id` (`employee_id`), KEY `department_id` (`department_id`), KEY `position_id` (`position_id`), CONSTRAINT `hr_employees_transfers_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employees_transfers_ibfk_2` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employees_transfers_ibfk_3` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employees_certificates` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `university_name` varchar(255) NOT NULL, `university_specialty` varchar(255) NOT NULL, `university_year` varchar(4) NOT NULL, `university_certificate` varchar(255) DEFAULT NULL, `university_gpa` float DEFAULT NULL, PRIMARY KEY (`id`), KEY `employment_request_id` (`employee_id`), CONSTRAINT `hr_employee_certificates_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employment_request_certificates` (`id` int(11) NOT NULL AUTO_INCREMENT, `employment_request_id` int(11) NOT NULL, `university_name` varchar(255) NOT NULL, `university_specialty` varchar(255) NOT NULL, `university_year` varchar(4) NOT NULL, `university_certificate` varchar(255) DEFAULT NULL, `university_gpa` float DEFAULT NULL, PRIMARY KEY (`id`), KEY `employment_request_id` (`employment_request_id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_finance` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `type_col` varchar(50) NOT NULL, `value_col` double NOT NULL, `currency_id` int(11) NOT NULL, `start_date` date NOT NULL, `end_date` date DEFAULT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `cycle` varchar(50) NOT NULL DEFAULT 'month', `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), KEY `employee_id` (`employee_id`), CONSTRAINT `hr_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_finance_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_finance_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_leave_types` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` VARCHAR(255) NOT NULL, `days` int(11) NULL, `days_in_year` int(11) NULL, `period` varchar(50) NULL, `date_added` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, `paid` BOOLEAN NOT NULL DEFAULT FALSE, PRIMARY KEY (`id`)) ENGINE=InnoDB CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_leaves` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `leave_type_id` int(50) NOT NULL, `alternative_id` int(11) NOT NULL, `duration_in_hours` double NOT NULL, `duration_in_days` double NOT NULL, `start_date` date NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, `state_col` varchar(11) NOT NULL DEFAULT 'active', PRIMARY KEY (`id`), KEY `employee_id` (`employee_id`), KEY `alternative_id` (`alternative_id`), KEY `type_col` (`leave_type_id`), CONSTRAINT `hr_leaves_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_leaves_ibfk_2` FOREIGN KEY (`alternative_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_leaves_ibfk_3` FOREIGN KEY (`leave_type_id`) REFERENCES `hr_leave_types` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_loans` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `value_col` double NOT NULL, `currency` int(11) NOT NULL, `date_col` date NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `periodically_subtract_from_salary` tinyint(1) NOT NULL DEFAULT '0', `subtract_currency` int(11) DEFAULT NULL, `subtract_cycle` varchar(50) DEFAULT NULL, `subtract_value` double DEFAULT NULL, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency` (`currency`), KEY `opposite_account_id` (`opposite_account_id`), KEY `employee_id` (`employee_id`), CONSTRAINT `hr_loans_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_loans_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_loans_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_loans_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_loans_payment` (`id` int(11) NOT NULL AUTO_INCREMENT, `loan_id` int(11) NOT NULL, `value_col` int(11) NOT NULL, `currency` int(11) NOT NULL, `source` varchar(15) NOT NULL, `date_col` date NOT NULL, PRIMARY KEY (`id`), KEY `loan_id` (`loan_id`), KEY `currency` (`currency`), CONSTRAINT `hr_loans_payment_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `hr_loans` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_loans_payment_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_positions_finance` (`id` int(11) NOT NULL AUTO_INCREMENT, `position_id` int(11) NOT NULL, `statement_col` varchar(250) NOT NULL, `type_col` varchar(50) NOT NULL, `value_col` double NOT NULL, `currency_id` int(11) NOT NULL, `start_date` date NOT NULL, `end_date` date DEFAULT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), KEY `employee_id` (`position_id`), CONSTRAINT `hr_positions_finance_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_positions_finance_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_positions_finance_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_positions_finance_ibfk_4` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_positions_leaves` (`id` int(11) NOT NULL AUTO_INCREMENT, `position_id` int(11) NOT NULL, `statement_col` varchar(250) DEFAULT NULL, `duration_in_hours` double NOT NULL, `duration_in_days` double NOT NULL, `start_date` date NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `hr_positions_leaves_ibfk_1` (`position_id`), CONSTRAINT `hr_positions_leaves_ibfk_1` FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_extra` (`id` int(11) NOT NULL PRIMARY KEY AUTO_INCREMENT, `employee_id` int(11) DEFAULT NULL, `department_id` int(11) DEFAULT NULL, `start_date` date NOT NULL, `value_col` double NOT NULL, `duration_in_hours` double NOT NULL, `duration_in_days` double NOT NULL, `currency_id` int(11) NOT NULL, `statement_col` varchar(500) DEFAULT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `state_col` varchar(11) NOT NULL DEFAULT 'active', KEY `currency_id` (`currency_id`), KEY `employee_id` (`employee_id`), KEY `department_id` (`department_id`), KEY `account_id` (`account_id`), KEY `opposite_account_id` (`opposite_account_id`), CONSTRAINT `hr_extra_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_extra_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_extra_ibfk_3` FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_extra_ibfk_4` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_extra_ibfk_5` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_settings` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(50) NOT NULL, `value_col` varchar(11) DEFAULT NULL, `last_update` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, PRIMARY KEY (`id`), UNIQUE KEY `name` (`name`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `type_col` varchar(50) NOT NULL, `start_date` date NOT NULL, `repeatition` int(11) DEFAULT NULL, `end_date` INT(11) NOT NULL, `value_col` double NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `statement_col` varchar(500) DEFAULT NULL, `currency_id` int(11) DEFAULT NULL, `state_col` varchar(11) NOT NULL DEFAULT 'active', PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency_id` (`currency_id`), KEY `opposite_account_id` (`opposite_account_id`), KEY `employee_id` (`employee_id`), CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_2` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_employees_salaries_additions_discounts_ibfk_4` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts_payments` (`id` int(11) NOT NULL AUTO_INCREMENT, `salaries_additions_discounts` int(11) NOT NULL, `date_col` date NOT NULL, PRIMARY KEY (`id`), KEY `salaries_additions_discounts` (`salaries_additions_discounts`), CONSTRAINT `hr_employees_salaries_additions_discounts_payments_ibfk_1` FOREIGN KEY (`salaries_additions_discounts`) REFERENCES `hr_employees_salaries_additions_discounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_salary_blocks` (`id` int(11) NOT NULL AUTO_INCREMENT, `from_date` date NOT NULL, `to_date` date NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")


                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_salary_block_entries` (`id` int(11) NOT NULL AUTO_INCREMENT, `salary_block_id` int(11) NOT NULL, `employee_id` int(11) NOT NULL, `statement_col` varchar(500) NOT NULL, `value_col` double NOT NULL, `currency` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `salary_block_id` (`salary_block_id`), KEY `employee_id` (`employee_id`), KEY `currency` (`currency`), CONSTRAINT `hr_salary_block_entries_ibfk_1` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_salary_block_entries_ibfk_2` FOREIGN KEY (`salary_block_id`) REFERENCES `hr_salary_blocks` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_salary_block_entries_ibfk_3` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_salary_block_entries_ibfk_4` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_insurance_blocks` (`id` int(11) NOT NULL AUTO_INCREMENT, `from_date` date NOT NULL, `to_date` date NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `hr_insurance_block_entries` (`id` int(11) NOT NULL AUTO_INCREMENT, `insurance_block_id` int(11) NOT NULL, `employee_id` int(11) NOT NULL, `cycles` double NOT NULL, `value_col` double NOT NULL, `currency` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `salary_block_id` (`insurance_block_id`), KEY `employee_id` (`employee_id`), KEY `currency` (`currency`), CONSTRAINT `hr_insurance_block_entries_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_insurance_block_entries_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `hr_insurance_block_entries_ibfk_3` FOREIGN KEY (`insurance_block_id`) REFERENCES `hr_insurance_blocks` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `materials_machines` (`id` int(11) NOT NULL AUTO_INCREMENT, `material_id` int(11) NOT NULL, `machine_id` int(11) NOT NULL, `mode_id` int(11) NOT NULL, `usage_duration` double NOT NULL, `exclusive` tinyint(1) NOT NULL DEFAULT '1', PRIMARY KEY (`id`), KEY `machine_id` (`machine_id`), KEY `material_id` (`material_id`), KEY `mode_id` (`mode_id`), CONSTRAINT `materials_machines_ibfk_1` FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `materials_machines_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `materials_machines_ibfk_3` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `resources` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(200) NOT NULL UNIQUE, `account_id` int(11) DEFAULT NULL, `notes` varchar(500) DEFAULT NULL, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), CONSTRAINT `resources_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `resources_costs` (`id` int(11) NOT NULL AUTO_INCREMENT, `resource_id` int(11) NOT NULL, `value_col` double NOT NULL, `currency_id` int(11) NOT NULL, `unit_id` int(11) NOT NULL, `notes` varchar(500) NOT NULL, `date_col` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP, PRIMARY KEY (`id`), KEY `currency_id` (`currency_id`), KEY `unit_id` (`unit_id`), KEY `resources_costs_ibfk_2` (`resource_id`), CONSTRAINT `resources_costs_ibfk_1` FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `resources_costs_ibfk_2` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `resources_costs_ibfk_3` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `mode_resources` (`id` int(11) NOT NULL AUTO_INCREMENT, `mode_id` int(11) NOT NULL, `resource_id` int(11) NOT NULL, `consumption_per_minute` double NOT NULL, `unit` int(11) NOT NULL, PRIMARY KEY (`id`), UNIQUE KEY `mode_id` (`mode_id`,`resource_id`), KEY `unit` (`unit`), KEY `resource_id` (`resource_id`), CONSTRAINT `mode_resources_ibfk_1` FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `mode_resources_ibfk_2` FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `mode_resources_ibfk_3` FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `journal_entries` (`id` int(11) NOT NULL AUTO_INCREMENT, `currency` int(11) NOT NULL, `date_col` date NOT NULL, `entry_date` date NOT NULL, `origin_type` varchar(250) DEFAULT NULL, `origin_id` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `currency` (`currency`), CONSTRAINT `journal_entries_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `journal_entries_items` (`id` int(11) NOT NULL AUTO_INCREMENT, `journal_entry_id` int(11) NOT NULL, `account_id` int(11) NOT NULL, `statement_col` varchar(2500) NOT NULL, `currency` int(11) NOT NULL, `opposite_account_id` int(11) DEFAULT NULL, `type_col` varchar(50) NOT NULL, `value_col` double NOT NULL, `cost_center_id` int(10) DEFAULT NULL, PRIMARY KEY (`id`), KEY `account_id` (`account_id`), KEY `currency` (`currency`), KEY `opposite_account_id` (`opposite_account_id`), KEY `journal_entries_items_ibfk_3` (`journal_entry_id`), KEY `cost_center` (`cost_center_id`), CONSTRAINT `journal_entries_items_ibfk_1` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE RESTRICT, CONSTRAINT `journal_entries_items_ibfk_2` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON DELETE RESTRICT, CONSTRAINT `journal_entries_items_ibfk_3` FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, CONSTRAINT `journal_entries_items_ibfk_4` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `journal_entries_items_distributive_cost_center_values` (`id` int(11) NOT NULL AUTO_INCREMENT, `journal_entry_item_id` int(11) NOT NULL, `cost_centers_aggregations_distributives_id` int(11) NOT NULL, `percentage` float NOT NULL DEFAULT '0', PRIMARY KEY (`id`), UNIQUE KEY `journal_entry_item_id` (`journal_entry_item_id`,`cost_centers_aggregations_distributives_id`), KEY `cost_centers_aggregations_distributives_id` (`cost_centers_aggregations_distributives_id`), CONSTRAINT `journal_entries_items_distributive_cost_center_values_ibfk_1` FOREIGN KEY (`cost_centers_aggregations_distributives_id`) REFERENCES `cost_centers_aggregations_distributives` (`id`) ON DELETE RESTRICT, CONSTRAINT `journal_entries_items_distributive_cost_center_values_ibfk_2` FOREIGN KEY (`journal_entry_item_id`) REFERENCES `journal_entries_items` (`id`) ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `loans` (`id` int(11) NOT NULL AUTO_INCREMENT, `currency` int(11) NOT NULL, `interest` double NOT NULL, `cycle` varchar(50) NOT NULL, `name` varchar(100) DEFAULT NULL, `amount` double NOT NULL, `account_id` int(11) DEFAULT NULL, `opposite_account_id` int(11) DEFAULT NULL, `date_col` timestamp NOT NULL, PRIMARY KEY (`id`), KEY `currency` (`currency`), KEY `account_id` (`account_id`), KEY `opposite_account_id` (`opposite_account_id`), CONSTRAINT `loans_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `loans_ibfk_2` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `loans_ibfk_3` FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
                )

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `loan_payments` (`id` int(11) NOT NULL AUTO_INCREMENT, `loan_id` int(11) NOT NULL, `amount` double NOT NULL, `currency` int(11) NOT NULL, `date_col` date NOT NULL, PRIMARY KEY (`id`), KEY `loan_id` (`loan_id`), CONSTRAINT `loans_payments_ibfk_1` FOREIGN KEY (`loan_id`) REFERENCES `loans` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;"
                )

                c.execute("CREATE TABLE IF NOT EXISTS `receipt_docs` (`id` int(11) NOT NULL AUTO_INCREMENT, `target_warehouse_id` int(11) NOT NULL, `rejection_warehouse_id` int(11) NOT NULL, `date_col` date NOT NULL, `material_id` int(11) NOT NULL, `quantity` double NOT NULL, `unit_id` int(11) NOT NULL, `invoice_item_id` int(11) DEFAULT NULL, `factory_id` int(11) DEFAULT NULL, PRIMARY KEY (`id`), KEY `material_id` (`material_id`), KEY `unit_id` (`unit_id`), KEY `target_warehouse_id` (`target_warehouse_id`), KEY `rejection_warehouse_id` (`rejection_warehouse_id`), KEY `receipt_docs_ibfk_5` (`invoice_item_id`), CONSTRAINT `receipt_docs_ibfk_1` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), CONSTRAINT `receipt_docs_ibfk_2` FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`), CONSTRAINT `receipt_docs_ibfk_3` FOREIGN KEY (`target_warehouse_id`) REFERENCES `warehouseslist` (`id`), CONSTRAINT `receipt_docs_ibfk_4` FOREIGN KEY (`rejection_warehouse_id`) REFERENCES `warehouseslist` (`id`), CONSTRAINT `receipt_docs_ibfk_5` FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE SET NULL ON UPDATE SET NULL) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute("CREATE TABLE IF NOT EXISTS `material_moves` ( `id` int(11) NOT NULL AUTO_INCREMENT, `source_warehouse_entry_id` int(11), `destination_warehouse_entry_id` int(11), `source_warehouse` int(11), `destination_warehouse` int(11), `quantity` REAL NOT NULL, `unit` int(11) NOT NULL, `origin` TEXT, `origin_id` int(11), `date_col` DATE, PRIMARY KEY (`id`), FOREIGN KEY (`source_warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE SET NULL ON UPDATE CASCADE, FOREIGN KEY (`destination_warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE SET NULL ON UPDATE CASCADE, FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci")

                c.execute("CREATE TABLE IF NOT EXISTS `period_start_materials` (`id` int(11) NOT NULL AUTO_INCREMENT, `material_id` int(11) NOT NULL, `quantity1` double NOT NULL, `unit1_id` int(11) NOT NULL, `quantity2` double DEFAULT NULL, `unit2_id` int(11) DEFAULT NULL, `quantity3` double DEFAULT NULL, `unit3_id` int(11) DEFAULT NULL, `unit_price` int(11) NOT NULL, `currency` int(11) NOT NULL, `warehouse_id` int(11) NOT NULL, `notes` varchar(500) COLLATE utf8mb4_unicode_ci DEFAULT NULL, `date_col` date NOT NULL, PRIMARY KEY (`id`), KEY `currency` (`currency`), KEY `material_id` (`material_id`), KEY `unit1_id` (`unit1_id`), KEY `unit2_id` (`unit2_id`), KEY `unit3_id` (`unit3_id`), KEY `warehouse_id` (`warehouse_id`), CONSTRAINT `period_start_materials_ibfk_1` FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`), CONSTRAINT `period_start_materials_ibfk_2` FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), CONSTRAINT `period_start_materials_ibfk_3` FOREIGN KEY (`unit1_id`) REFERENCES `units` (`id`), CONSTRAINT `period_start_materials_ibfk_4` FOREIGN KEY (`unit2_id`) REFERENCES `units` (`id`), CONSTRAINT `period_start_materials_ibfk_5` FOREIGN KEY (`unit3_id`) REFERENCES `units` (`id`), CONSTRAINT `period_start_materials_ibfk_6` FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `criteria` ( `id` int(11) NOT NULL AUTO_INCREMENT, `name` VARCHAR(200) NOT NULL, `key_name` VARCHAR(200) NOT NULL, PRIMARY KEY (`id`) ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `permissions` ( `id` int(11) NOT NULL AUTO_INCREMENT, `criteria_id` int(11) NOT NULL, `user_id` int(11) NOT NULL, `type_col` VARCHAR(2), PRIMARY KEY (`id`), FOREIGN KEY (`criteria_id`) REFERENCES `criteria` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")

                c.execute(
                    "CREATE TABLE IF NOT EXISTS `maintenance_workers` (`id` int(11) NOT NULL AUTO_INCREMENT, `employee_id` int(11) NOT NULL, `maintenance_id` int(11) NOT NULL, PRIMARY KEY (`id`), KEY `maintenance_id` (`maintenance_id`), KEY `employee_id` (`employee_id`), CONSTRAINT `maintenance_workers_ibfk_1` FOREIGN KEY (`maintenance_id`) REFERENCES `machine_maintenance` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, CONSTRAINT `maintenance_workers_ibfk_2` FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                
                c.execute("CREATE TABLE IF NOT EXISTS `media` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(255) NOT NULL, `file` mediumblob NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")
                    
                c.execute(
                    "CREATE TABLE IF NOT EXISTS `manuals` (`id` int(11) NOT NULL AUTO_INCREMENT, `name` varchar(255) NOT NULL, PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;")


                manuals = [
                    'syria_manual',
                    'turkish_manual',
                    'egyptian_manual',
                    'iraq_manual',
                ]

                for manual in manuals:
                    c.execute("INSERT INTO `manuals` (`name`) VALUES (%s)", (manual,))


                # Check if indexes exist before creating them
                c.execute("SHOW INDEX FROM material_moves WHERE Key_name = 'idx_source_warehouse'")
                if not c.fetchone():
                    c.execute("CREATE INDEX idx_source_warehouse ON material_moves(source_warehouse)")
                
                c.execute("SHOW INDEX FROM material_moves WHERE Key_name = 'idx_destination_warehouse'")
                if not c.fetchone():
                    c.execute("CREATE INDEX idx_destination_warehouse ON material_moves(destination_warehouse)")
                
                c.execute("SHOW INDEX FROM material_moves WHERE Key_name = 'idx_unit'")
                if not c.fetchone():
                    c.execute("CREATE INDEX idx_unit ON material_moves(unit)")
                
                c.execute("SELECT count(*) FROM `variables` WHERE `variable` = 'api_prefix'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `variables` (`variable`, `value_col`) VALUES ('api_prefix','api')")

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'الأصول'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('الأصول','1')")

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'الخصوم'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('الخصوم','2')")

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'حقوق الملكية'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('حقوق الملكية','3')")
                #     last_id = c.lastrowid
                #     c.execute(
                #         "INSERT INTO `accounts` (`name`, `code`, `parent_account`) VALUES ('رأس المال', '3-1', %s)",
                #         (last_id,))
                #     last_id = c.lastrowid
                #     c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES (%s, %s)",
                #               ('default_capital_account', last_id))

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'التكاليف'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('التكاليف','4')")

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'الإيرادات'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('الإيرادات','5')")

                # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'المصروفات'")
                # rows = c.fetchall()
                # if (rows[0][0] == 0):
                #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('المصروفات','6')")

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='first_period'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    date_value = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
                    c.execute(
                        "INSERT INTO `settings` (`name`, `value_col`) VALUES ('first_period', '" + str(
                            date_value) + "')")

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='last_period'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    date_value = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
                    c.execute(
                        "INSERT INTO `settings` (`name`, `value_col`) VALUES ('last_period', '" + str(
                            date_value) + "')")

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='operations_fixation'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    date_value = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
                    c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('operations_fixation', '" + str(
                        date_value) + "')")

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='float_point_value'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`, `value_col`) VALUES ('float_point_value', '2')")
                    

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='mid_output_account'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`) VALUES ('mid_output_account')")
                    
                c.execute("SELECT count(*) FROM `settings` WHERE `name`='mid_input_account'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`) VALUES ('mid_input_account')")
                    
                c.execute("SELECT count(*) FROM `settings` WHERE `name`='output_account'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`) VALUES ('output_account')")
                    
                c.execute("SELECT count(*) FROM `settings` WHERE `name`='input_account'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`) VALUES ('input_account')")
                    
                c.execute("SELECT count(*) FROM `settings` WHERE `name`='selected_manual'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `settings` (`name`,`value_col`) VALUES ('selected_manual','syria_manual')")

                # invoice types
                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='buy_return'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('buy_return', 'output',1)")

                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='sell_return'") 
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('sell_return', 'input',1)")

                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='sell'") 
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('sell', 'output',0)")

                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='buy'") 
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('buy', 'input',0)")

                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='input'") 
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('input', 'input',0)")

                c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='output'") 
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `invoice_types` (`name`, `type_col`,`returned`) VALUES ('output', 'output',0)")




                c.execute("SELECT count(*) FROM `currencies` WHERE `name`='دولار أمريكي'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute(
                        "INSERT INTO `currencies` (`name`, `symbol`, `parts`, `parts_relation`) VALUES ('دولار أمريكي', '$', 'سنت', '100')")

                c.execute("SELECT count(*) FROM `settings` WHERE `name`='default_currency'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("SELECT `id` FROM `currencies` WHERE `name`='دولار أمريكي'")
                rows = c.fetchall()
                if (len(rows) > 0):
                    usd_id = rows[0][0]
                    c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('default_currency', '" + str(
                        usd_id) + "')")
                    
                c.execute("SELECT count(*) FROM `settings` WHERE `name`='saved_journal_entries'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('saved_journal_entries', 'individual')")
                    
                # Insert default HR settings for work days
                hr_settings = [
                    'setting_work_day_saturday',
                    'setting_work_day_sunday', 
                    'setting_work_day_monday',
                    'setting_work_day_tuesday',
                    'setting_work_day_wednesday',
                    'setting_work_day_thursday',
                    'setting_work_day_friday',
                    'setting_salaries_account'
                ]

                for setting in hr_settings:
                    c.execute(f"SELECT count(*) FROM `hr_settings` WHERE `name`='{setting}'")
                    rows = c.fetchall()
                    if (rows[0][0] == 0):
                        c.execute(f"INSERT INTO `hr_settings` (`name`, `value_col`) VALUES ('{setting}', '1')")
                                
                c.execute("SELECT COUNT(*) FROM `hr_settings` WHERE `name` = 'setting_month_duration'")
                rows = c.fetchall()
                if (rows[0][0] == 0):
                    c.execute("INSERT INTO `hr_settings` (`name`, `value_col`) VALUES ('setting_month_duration', '30')")

                criteria_options = {
                    'invoices': 'INVOICES',
                    'warehouses': 'WAREHOUSES', 
                    'materials': 'MATERIALS',
                    'machines': 'MACHINES',
                    'production_lines': 'PRODUCTION_LINES',
                    'HR_employees_requests': 'HR_EMPLOYEES_REQUESTS',
                    'HR_employees': 'HR_EMPLOYEES',
                    'HR_leaves': 'HR_LEAVES',
                    'HR_insurance_blocks': 'HR_INSURANCE_BLOCKS',
                    'HR_salaries': 'HR_SALARIES',
                    'HR_salaries_previous_payments': 'HR_SALARIES_PREVIOUS_PAYMENTS',
                    'HR_salaries_additions_and_discounts': 'HR_SALARIES_ADDITIONS_AND_DISCOUNTS',
                    'HR_departments': 'HR_DEPARTMENTS',
                    'HR_department_leaves': 'HR_DEPARTMENT_LEAVES',
                    'HR_department_leaves_types': 'HR_DEPARTMENT_LEAVES_TYPES',
                    'HR_department_additions_and_discounts': 'HR_DEPARTMENT_ADDITIONS_AND_DISCOUNTS',
                    'HR_extra_hours': 'HR_EXTRA_HOURS',
                    'plans': 'PLANS',
                    'accounts': 'ACCOUNTS',
                    'material_moves': 'MATERIAL_MOVES',
                    'cost_centers': 'COST_CENTERS',
                    'users': 'USERS',
                    'permissions': 'PERMISSIONS',
                    'syncronization': 'SYNCRONIZATION',
                    'settings': 'SETTINGS',
                    'backup': 'BACKUP',
                    'reports': 'REPORTS',
                    'manufacture': 'MANUFACTURE',
                    'production_lines': 'PRODUCTION_LINES',
                    'machines': 'MACHINES',
                    'users': 'USERS',
                    'customers': 'CUSTOMERS',
                    'suppliers': 'SUPPLIERS',
                    'currencies': 'CURRENCIES',
                }

                for option, key_name in criteria_options.items():
                    c.execute("SELECT count(*) FROM `criteria` WHERE `name`='" + str(option) + "'")
                    rows = c.fetchall()
                    if (rows[0][0] == 0):
                        c.execute("INSERT INTO `criteria` (`name`, `key_name`) VALUES ('" + str(option) + "', '" + str(key_name) + "')")

                # check if all default prices are availabe
                default_prices = ["المفرق", "الجملة", "نصف الجملة", "الموزع", "التصدير", "المستهلك", "اخر شراء"];
                for default_price in default_prices:
                    c.execute("SELECT count(*) FROM `prices` WHERE `price`='" + str(default_price) + "'")
                    rows = c.fetchall()
                    if (rows[0][0] == 0):
                        c.execute("INSERT INTO `prices` (`price`, `locked`) VALUES ('" + str(default_price) + "','1')")

                invoices_default_settings = {'buy_added_value_account': None,
                                             'buy_gift_opposite_account': None,
                                             'buy_monetary_account': None,
                                             'buy_gifts_account': None,
                                             'buy_cost_account': None,
                                             'buy_discounts_account': None,
                                             'buy_materials_account': None,
                                             'buy_stock_account': None,
                                             'buy_addition_account': None,
                                             'buy_invoice_price': None,
                                             'buy_cost_price': None,
                                             'buy_gift_price': None,
                                             'buy_warehouse': None,
                                             'buy_cost_center': None,
                                             'buy_currency': None,

                                             'sell_added_value_account': None,
                                             'sell_gift_opposite_account': None,
                                             'sell_monetary_account': None,
                                             'sell_gifts_account': None,
                                             'sell_cost_account': None,
                                             'sell_discounts_account': None,
                                             'sell_materials_account': None,
                                             'sell_stock_account': None,
                                             'sell_addition_account': None,
                                             'sell_invoice_price': None,
                                             'sell_cost_price': None,
                                             'sell_gift_price': None,
                                             'sell_warehouse': None,
                                             'sell_cost_center': None,
                                             'sell_currency': None,

                                             'buy_return_added_value_account': None,
                                             'buy_return_gift_opposite_account': None,
                                             'buy_return_monetary_account': None,
                                             'buy_return_gifts_account': None,
                                             'buy_return_cost_account': None,
                                             'buy_return_discounts_account': None,
                                             'buy_return_materials_account': None,
                                             'buy_return_stock_account': None,
                                             'buy_return_addition_account': None,
                                             'buy_return_invoice_price': None,
                                             'buy_return_cost_price': None,
                                             'buy_return_gift_price': None,
                                             'buy_return_warehouse': None,
                                             'buy_return_cost_center': None,
                                             'buy_return_currency': None,

                                             'sell_return_added_value_account': None,
                                             'sell_return_gift_opposite_account': None,
                                             'sell_return_monetary_account': None,
                                             'sell_return_gifts_account': None,
                                             'sell_return_cost_account': None,
                                             'sell_return_discounts_account': None,
                                             'sell_return_materials_account': None,
                                             'sell_return_stock_account': None,
                                             'sell_return_addition_account': None,
                                             'sell_return_invoice_price': None,
                                             'sell_return_cost_price': None,
                                             'sell_return_gift_price': None,
                                             'sell_return_warehouse': None,
                                             'sell_return_cost_center': None,
                                             'sell_return_currency': None,

                                             'input_added_value_account': None,
                                             'input_gift_opposite_account': None,
                                             'input_monetary_account': None,
                                             'input_gifts_account': None,
                                             'input_cost_account': None,
                                             'input_discounts_account': None,
                                             'input_materials_account': None,
                                             'input_stock_account': None,
                                             'input_addition_account': None,
                                             'input_invoice_price': None,
                                             'input_cost_price': None,
                                             'input_gift_price': None,
                                             'input_warehouse': None,
                                             'input_cost_center': None,
                                             'input_currency': None,

                                             'output_added_value_account': None,
                                             'output_gift_opposite_account': None,
                                             'output_monetary_account': None,
                                             'output_gifts_account': None,
                                             'output_cost_account': None,
                                             'output_discounts_account': None,
                                             'output_materials_account': None,
                                             'output_stock_account': None,
                                             'output_addition_account': None,
                                             'output_invoice_price': None,
                                             'output_cost_price': None,
                                             'output_gift_price': None,
                                             'output_warehouse': None,
                                             'output_cost_center': None,
                                             'output_currency': None,

                                             'buy_affects_materials_gain_loss': '1',
                                             'buy_affects_client_price': '1',
                                             'buy_discounts_affects_cost_price': '1',
                                             'buy_discounts_affects_gain': '1',
                                             'buy_affects_last_buy_price': '1',
                                             'buy_additions_affects_cost_price': '1',
                                             'buy_additions_affects_gain': '1',
                                             'buy_affects_cost_price': '1',
                                             'buy_affects_on_warehouse': 'add',

                                             'sell_affects_materials_gain_loss': '1',
                                             'sell_affects_client_price': '1',
                                             'sell_discounts_affects_cost_price': '0',
                                             'sell_discounts_affects_gain': '1',
                                             'sell_affects_last_buy_price': '0',
                                             'sell_additions_affects_cost_price': '0',
                                             'sell_additions_affects_gain': '1',
                                             'sell_affects_cost_price': '0',
                                             'sell_affects_on_warehouse': 'reduce',

                                             'buy_return_affects_materials_gain_loss': '0',
                                             'buy_return_affects_client_price': '0',
                                             'buy_return_discounts_affects_cost_price': '1',
                                             'buy_return_discounts_affects_gain': '0',
                                             'buy_return_affects_last_buy_return_price': '0',
                                             'buy_return_additions_affects_cost_price': '1',
                                             'buy_return_additions_affects_gain': '0',
                                             'buy_return_affects_cost_price': '1',
                                             'buy_return_affects_on_warehouse': 'add',

                                             'sell_return_affects_materials_gain_loss': '0',
                                             'sell_return_affects_client_price': '0',
                                             'sell_return_discounts_affects_cost_price': '0',
                                             'sell_return_discounts_affects_gain': '1',
                                             'sell_return_affects_last_sell_return_price': '0',
                                             'sell_return_additions_affects_cost_price': '0',
                                             'sell_return_additions_affects_gain': '1',
                                             'sell_return_affects_cost_price': '0',
                                             'sell_return_affects_on_warehouse': 'reduce',

                                             'input_affects_materials_gain_loss': '0',
                                             'input_affects_client_price': '0',
                                             'input_discounts_affects_cost_price': '0',
                                             'input_discounts_affects_gain': '0',
                                             'input_affects_last_input_price': '0',
                                             'input_additions_affects_cost_price': '0',
                                             'input_additions_affects_gain': '0',
                                             'input_affects_cost_price': '0',
                                             'input_affects_on_warehouse': 'add',

                                             'output_affects_materials_gain_loss': '0',
                                             'output_affects_client_price': '0',
                                             'output_discounts_affects_cost_price': '0',
                                             'output_discounts_affects_gain': '0',
                                             'output_affects_last_output_price': '0',
                                             'output_additions_affects_cost_price': '0',
                                             'output_additions_affects_gain': '0',
                                             'output_affects_cost_price': '0',
                                             'output_affects_on_warehouse': 'reduce'}   
                
                for key, value in invoices_default_settings.items():
                    if not value:
                        value = ""
                    c.execute("SELECT count(*) FROM `settings` WHERE `name`='" + str(key) + "'")
                    rows = c.fetchall()
                    if rows[0][0] == 0:
                        c.execute(
                            "INSERT INTO `settings` (`name`, `value_col`) VALUES ('" + str(key) + "',NULLIF('" + str(
                                value) + "',''))")

                factory_database_defaults = {"factory_server": "localhost", "factory_port": "3306",
                                             "factory_username": "root", "factory_password": "root"}
                for key, value in factory_database_defaults.items():
                    c.execute("SELECT count(*) FROM `settings` WHERE `name`='" + str(key) + "'")
                    rows = c.fetchall()
                    if (rows[0][0] == 0):
                        c.execute(
                            "INSERT INTO `settings` (`name`, `value_col`) VALUES ('" + str(key) + "',NULLIF('" + str(
                                value) + "',''))")

                self.conn.commit()
                print("Tables check done.")
            except Exception as e:
                print("Unable to check tables. - " + str(e))
                traceback.print_exc()
        else:
            print("Unable to check tables. Not connected to database")

    def disconnectDatabase(self):
        if self.is_connected_to_server:
            try:
                self.conn.close()
                self.is_connected_to_database = False
                self.is_connected_to_server = False
            except Exception as e:
                print("Error while trying to disconnect. - " + str(e))
                traceback.print_exc()
        else:
            print("Already disconnected.")

    def deleteDatabase(self, db_name):
        if self.is_connected_to_server:
            try:
                c = self.conn.cursor()
                c.execute("DROP DATABASE `" + str(db_name) + "`")
                self.is_connected_to_database = False
            except Exception as e:
                print("Unable to delete database. -" + str(e))
                traceback.print_exc()
        else:
            print("Unable to delete database. Not connected to server.")
