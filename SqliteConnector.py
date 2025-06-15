import os
import sqlite3

print("Sqlite V" + str(sqlite3.sqlite_version))
from datetime import date

import win32api


class SqliteConnector():
    is_connected_to_database = False
    conn = ''

    def __init__(self):
        super().__init__()

    def connectToDatabase(self, database_file):
        if os.path.isfile(database_file) and os.access(database_file, os.R_OK):
            print("Database file exists and is readable")
            if not self.is_connected_to_database:
                self.conn = sqlite3.connect(database_file)
                self.checkDatabaseTables()
                self.is_connected_to_database = True
            else:
                win32api.MessageBox(0, 'Database Already Connected.', 'Database')
        else:
            print("Either the database file is missing or not readable")

    def checkDatabaseTables(self):
        c = self.conn.cursor()
        print("Checking tables...")

        c.execute("PRAGMA foreign_keys = ON;")

        # Note: Theses Statements do not exist in the MySQLConnector file

        # c.execute("CREATE TABLE IF NOT EXISTS lab (id INTEGER PRIMARY KEY, element, quantity, unit, src, date)")
        # c.execute("CREATE TABLE IF NOT EXISTS research (id INTEGER PRIMARY KEY, element, quantity, unit, src, date)")
        # c.execute("CREATE TABLE IF NOT EXISTS prepayments (id INTEGER PRIMARY KEY, client , payment_sp, payment_usd, date)")
        # c.execute("CREATE TABLE IF NOT EXISTS invoices_out_payments (id INTEGER PRIMARY KEY, invoice , payment_sp, payment_usd, date)")
        # c.execute("CREATE TABLE IF NOT EXISTS payments (id INTEGER PRIMARY KEY, invoice, payment_sp, payment_usd, date)")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `financial_statement` (`id` INTEGER PRIMARY KEY, `name` VARCHAR(50) NOT NULL, `final_financial_statement` INTEGER DEFAULT NULL, FOREIGN KEY (`final_financial_statement`) REFERENCES `financial_statement`(`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `financial_statement_block` (`id` INTEGER PRIMARY KEY, `name` VARCHAR(50) NOT NULL, `financial_statement_id` INTEGER, FOREIGN KEY (`financial_statement_id`) REFERENCES `financial_statement`(`id`) ON DELETE CASCADE);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `accounts` ( `id` INTEGER PRIMARY KEY , `name` TEXT NOT NULL, `code` TEXT DEFAULT NULL, `details` TEXT DEFAULT NULL, `parent_account` INTEGER DEFAULT NULL, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, `type_col` TEXT NOT NULL DEFAULT 'normal', `final_account` INTEGER DEFAULT NULL, `financial_statement` INTEGER DEFAULT NULL, `financial_statement_block` INTEGER DEFAULT NULL, `force_cost_center` INTEGER DEFAULT 0, `default_cost_center` INTEGER DEFAULT NULL, FOREIGN KEY (`parent_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`final_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`financial_statement`) REFERENCES `financial_statement` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`financial_statement_block`) REFERENCES `financial_statement_block` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`default_cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `clients` ( `id` INTEGER PRIMARY KEY , `name` TEXT, `governorate` TEXT DEFAULT NULL, `address` TEXT DEFAULT NULL, `email` TEXT DEFAULT NULL, `phone1` TEXT DEFAULT NULL, `phone2` TEXT DEFAULT NULL, `phone3` TEXT DEFAULT NULL, `phone4` TEXT DEFAULT NULL, `client_type` TEXT DEFAULT NULL, `deleted` tinyint(1) DEFAULT 0 );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `currencies` (`id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL UNIQUE, `symbol` TEXT DEFAULT NULL, `parts` TEXT DEFAULT NULL, `parts_relation` REAL DEFAULT NULL);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `warehouseslist` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `code` TEXT DEFAULT NULL, `name` TEXT NOT NULL UNIQUE, `codename` TEXT UNIQUE, `include_in_stock` tinyint(1) DEFAULT 1, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, `parent_warehouse` INTEGER DEFAULT NULL, `account` INTEGER DEFAULT NULL, `address` TEXT DEFAULT NULL, `manager` TEXT DEFAULT NULL, `notes` TEXT DEFAULT NULL, `capacity` REAL DEFAULT NULL, `capacity_unit` INTEGER DEFAULT NULL, FOREIGN KEY (`account`) REFERENCES `accounts` (`id`), FOREIGN KEY (`parent_warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE SET NULL, FOREIGN KEY (`capacity_unit`) REFERENCES `units` (`id`));")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `cost_centers` ( `id` INTEGER PRIMARY KEY , `name` TEXT NOT NULL, `notes` TEXT DEFAULT NULL, `type_col` TEXT NOT NULL, `parent` INTEGER DEFAULT NULL, `changable_division_factors` INTEGER NOT NULL DEFAULT 0, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`parent`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `invoices` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `type_col` INTEGER NOT NULL, `number` INTEGER DEFAULT NULL UNIQUE, `client` INTEGER DEFAULT NULL, `client_account` INTEGER DEFAULT NULL, `payment` varchar(50) DEFAULT NULL, `paid` INTEGER DEFAULT NULL, `currency` INTEGER DEFAULT NULL, `cost_center` INTEGER DEFAULT NULL, `warehouse` INTEGER DEFAULT NULL, `cost_account` INTEGER DEFAULT NULL, `gifts_account` INTEGER DEFAULT NULL, `added_value_account` INTEGER DEFAULT NULL, `monetary_account` INTEGER DEFAULT NULL, `materials_account` INTEGER DEFAULT NULL, `stock_account` INTEGER DEFAULT NULL, `gifts_opposite_account` INTEGER DEFAULT NULL, `statement_col` varchar(500) DEFAULT NULL, `date_col` DATE NOT NULL, `factory_id` INTEGER DEFAULT NULL, FOREIGN KEY (`type_col`) REFERENCES `invoice_types` (`id`), FOREIGN KEY (`client`) REFERENCES `clients` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`client_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`warehouse`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`cost_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`gifts_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`added_value_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`monetary_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`materials_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`stock_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`gifts_opposite_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `exchange_prices` ( `id` INTEGER PRIMARY KEY , `currency1` INTEGER NOT NULL, `currency2` INTEGER NOT NULL, `exchange` REAL NOT NULL DEFAULT 1, `date_col` DATE, `currency1_ordered` INTEGER, `currency2_ordered` INTEGER, UNIQUE(`currency1_ordered`, `currency2_ordered`, `date_col`) );")

        c.execute(
            '''CREATE TRIGGER IF NOT EXISTS set_ordered_values
                AFTER INSERT ON `exchange_prices`
                FOR EACH ROW
                BEGIN
                   UPDATE `exchange_prices`
                    SET `currency1_ordered` = CASE WHEN NEW.`currency1` < NEW.`currency2` THEN NEW.`currency1` ELSE NEW.`currency2` END,
                        `currency2_ordered` = CASE WHEN NEW.`currency1` > NEW.`currency2` THEN NEW.`currency1` ELSE NEW.`currency2` END
                    WHERE `id` = NEW.`id`;
                END;
        ''')

        c.execute(
            "CREATE TABLE IF NOT EXISTS `prices` ( `id` INTEGER PRIMARY KEY , `price` TEXT NOT NULL UNIQUE, `locked` INTEGER NOT NULL DEFAULT 0 );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `groups` ( `id` INTEGER PRIMARY KEY , `name` TEXT NOT NULL, `code` TEXT DEFAULT NULL, `parent_group` INTEGER DEFAULT NULL, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`parent_group`) REFERENCES `groups` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `units` ( `id` INTEGER PRIMARY KEY , `name` TEXT NOT NULL UNIQUE );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `manufacture_halls` ( `id` INTEGER PRIMARY KEY , `warehouse_id` INTEGER NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE (`warehouse_id`), FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `materials` ('id' INTEGER PRIMARY KEY, 'code' TEXT, 'name' TEXT, 'group_col' INTEGER, 'specs' TEXT, 'size_col' TEXT, 'manufacturer' TEXT, 'color' TEXT, 'origin' TEXT, 'quality' TEXT, 'type_col' TEXT, 'model' TEXT, 'unit1' INTEGER, 'unit2' INTEGER, 'unit3' INTEGER, 'default_unit' INTEGER NOT NULL DEFAULT '1', 'current_quantity' REAL, 'max_quantity' REAL, 'min_quantity' REAL, 'request_limit' REAL, 'gift' REAL, 'gift_for' REAL, 'price1_desc' INTEGER, 'price1_1' REAL, 'price1_1_unit' TEXT, 'price1_2' REAL, 'price1_2_unit' TEXT, 'price1_3' REAL, 'price1_3_unit' TEXT, 'price2_desc' INTEGER, 'price2_1' REAL, 'price2_1_unit' TEXT, 'price2_2' REAL, 'price2_2_unit' TEXT, 'price2_3' REAL, 'price2_3_unit' TEXT, 'price3_desc' INTEGER, 'price3_1' REAL, 'price3_1_unit' TEXT, 'price3_2' REAL, 'price3_2_unit' TEXT, 'price3_3' REAL, 'price3_3_unit' TEXT, 'price4_desc' INTEGER, 'price4_1' REAL, 'price4_1_unit' TEXT, 'price4_2' REAL, 'price4_2_unit' TEXT, 'price4_3' REAL, 'price4_3_unit' TEXT, 'price5_desc' INTEGER, 'price5_1' REAL, 'price5_1_unit' TEXT, 'price5_2' REAL, 'price5_2_unit' TEXT, 'price5_3' REAL, 'price5_3_unit' TEXT, 'price6_desc' INTEGER, 'price6_1' REAL, 'price6_1_unit' TEXT, 'price6_2' REAL, 'price6_2_unit' TEXT, 'price6_3' REAL, 'price6_3_unit' TEXT, 'expiray' INTEGER, 'groupped' INTEGER NOT NULL DEFAULT '0', 'yearly_required' REAL, 'work_hours' REAL, 'standard_unit3_quantity' REAL, 'standard_unit2_quantity' REAL, 'standard_unit1_quantity' REAL, 'manufacture_hall' INTEGER, 'discount_account' INTEGER DEFAULT NULL, 'addition_account' INTEGER DEFAULT NULL, FOREIGN KEY ('price1_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('group_col') REFERENCES 'groups' ('id'), FOREIGN KEY ('manufacture_hall') REFERENCES 'manufacture_halls' ('id'), FOREIGN KEY ('price2_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('price3_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('price4_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('price5_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('price6_desc') REFERENCES 'prices' ('id') ON UPDATE CASCADE, FOREIGN KEY ('unit1') REFERENCES 'units' ('id'), FOREIGN KEY ('unit2') REFERENCES 'units' ('id'), FOREIGN KEY ('unit3') REFERENCES 'units' ('id'), FOREIGN KEY ('discount_account') REFERENCES 'accounts' ('id') ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY ('addition_account') REFERENCES 'accounts' ('id') ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `invoice_items` ( `id` INTEGER PRIMARY KEY, `invoice_id` INTEGER NOT NULL, `material_id` INTEGER NOT NULL, `quantity1` REAL DEFAULT NULL, `unit1_id` INTEGER DEFAULT NULL, `quantity2` REAL DEFAULT NULL, `unit2_id` INTEGER DEFAULT NULL, `quantity3` REAL DEFAULT NULL, `unit3_id` INTEGER DEFAULT NULL, `price_type_id` INTEGER DEFAULT NULL, `unit_price` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `equilivance_price` REAL NOT NULL, `exchange_id` INTEGER DEFAULT NULL, `discount` REAL DEFAULT NULL, `discount_percent` REAL DEFAULT NULL, `addition` REAL DEFAULT NULL, `addition_percent` REAL DEFAULT NULL, `added_value` REAL DEFAULT NULL, `gifts` REAL DEFAULT NULL, `gifts_value` REAL DEFAULT NULL, `gifts_discount` REAL DEFAULT NULL, `warehouse_id` INTEGER DEFAULT NULL, `cost_center_id` INTEGER DEFAULT NULL, `notes` TEXT DEFAULT NULL, `deal_id` INTEGER DEFAULT NULL, `item_discount_account` INTEGER DEFAULT NULL, `item_addition_account` INTEGER DEFAULT NULL, `receipt_doc_id` INTEGER DEFAULT NULL, `production_date` DATE DEFAULT NULL, `expire_date` DATE DEFAULT NULL, `factory_id` INTEGER DEFAULT NULL, UNIQUE (`deal_id`), FOREIGN KEY (`cost_center_id`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`exchange_id`) REFERENCES `exchange_prices` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`price_type_id`) REFERENCES `prices` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`item_discount_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`item_addition_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE, FOREIGN KEY (`receipt_doc_id`) REFERENCES `receipt_docs` (`id`) ON UPDATE CASCADE );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `invoices_discounts_additions` ( `id` INTEGER PRIMARY KEY , `invoice_id` INTEGER NOT NULL, `type_col` TEXT NOT NULL, `account` INTEGER NOT NULL, `cost_center` INTEGER DEFAULT NULL, `currency` INTEGER, `exchange` INTEGER DEFAULT NULL, `opposite_account` INTEGER DEFAULT NULL, `equilivance` REAL DEFAULT NULL, `percent` INTEGER DEFAULT 0, FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`exchange`) REFERENCES `exchange_prices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `expenses_types` (id INTEGER PRIMARY KEY , name TEXT NOT NULL, account_id INTEGER DEFAULT NULL, opposite_account_id INTEGER DEFAULT NULL, calculated_in_manufacture INTEGER NOT NULL DEFAULT 0, FOREIGN KEY(account_id) REFERENCES accounts(id), FOREIGN KEY(opposite_account_id) REFERENCES accounts(id));")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `expenses` ( `id` INTEGER PRIMARY KEY, `time_slot` TEXT NOT NULL DEFAULT 'month', `value_col` REAL NOT NULL, `year_col` TEXT NOT NULL, `month_col` TEXT DEFAULT '1', `expense_type` INTEGER NOT NULL, `currency` INTEGER NOT NULL, UNIQUE (`year_col`, `month_col`, `expense_type`), FOREIGN KEY (`expense_type`) REFERENCES `expenses_types` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `expenses_monthly` ( `id` INTEGER PRIMARY KEY , `expenses` REAL NOT NULL, `year_col` TEXT NOT NULL, `month_col` TEXT NOT NULL DEFAULT '1', `type_col` TEXT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `manufacture` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `pullout_date` DATE DEFAULT NULL, `date_col` DATE DEFAULT NULL, `expenses_type` TEXT NOT NULL, `material_pricing_method` TEXT NOT NULL, `currency` INTEGER NOT NULL, `expenses_cost` REAL DEFAULT NULL, `machines_operation_cost` REAL DEFAULT 0, `salaries_cost` REAL DEFAULT NULL, `mid_account` INTEGER NOT NULL, `mid_account_input` INTEGER NOT NULL, `account` INTEGER NOT NULL, `composition_materials_cost` REAL DEFAULT NULL, `quantity_unit_expenses` INTEGER DEFAULT NULL, `expenses_distribution` TEXT DEFAULT NULL, `state_col` TEXT NOT NULL DEFAULT 'active', `factory_id` INTEGER DEFAULT NULL, `ingredients_pullout_method` TEXT DEFAULT NULL, `ingredients_pullout_account` INTEGER DEFAULT NULL, `working_hours` REAL DEFAULT NULL, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`mid_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`quantity_unit_expenses`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`ingredients_pullout_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`mid_account_input`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")
        
        c.execute(
            "CREATE TABLE IF NOT EXISTS `compositions` ( `id` INTEGER PRIMARY KEY AUTOINCREMENT, `material` INTEGER NOT NULL, `name` VARCHAR(250) NOT NULL, `factory_dossier_id` INTEGER DEFAULT NULL, FOREIGN KEY (`material`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `groupped_materials_composition` (`id` INTEGER PRIMARY KEY, `groupped_material_id` INTEGER NOT NULL, `composition_material_id` INTEGER NOT NULL, `composition_id` INTEGER NOT NULL, `quantity` REAL DEFAULT NULL, `unit` INTEGER NOT NULL, FOREIGN KEY (`composition_material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`groupped_material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`composition_id`) REFERENCES `compositions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `manufacture_materials` ( `id` INTEGER PRIMARY KEY, `manufacture_id` INTEGER NOT NULL, `composition_item_id` INTEGER NOT NULL, `standard_quantity` REAL DEFAULT NULL, `required_quantity` REAL DEFAULT NULL, `unit` INTEGER DEFAULT NULL, `unit_cost` INTEGER DEFAULT NULL, `row_type` TEXT NOT NULL, `warehouse_id` INTEGER DEFAULT NULL, `warehouse_account_id` INTEGER DEFAULT NULL, `pulled_quantity` REAL DEFAULT NULL, `shortage` REAL DEFAULT NULL, `currency` INTEGER DEFAULT NULL, `warehouse_quantity` REAL DEFAULT NULL, FOREIGN KEY (`manufacture_id`) REFERENCES `manufacture` (`id`) ON DELETE CASCADE, FOREIGN KEY (`composition_item_id`) REFERENCES `groupped_materials_composition` (`id`), FOREIGN KEY (`unit`) REFERENCES `units` (`id`), FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`), FOREIGN KEY (`warehouse_account_id`) REFERENCES `accounts` (`id`), FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) );")

        c.execute("CREATE TABLE IF NOT EXISTS `manufacture_produced_materials` (`id` INTEGER PRIMARY KEY, `manufacture_id` INTEGER NOT NULL, `material_id` INTEGER NOT NULL, `quantity1` REAL NOT NULL , `damaged_quantity1` REAL NOT NULL, `unit1` INTEGER NOT NULL, `quantity2` REAL DEFAULT NULL, `damaged_quantity2` REAL NOT NULL, `unit2` INTEGER DEFAULT NULL, `quantity3` REAL DEFAULT NULL, `damaged_quantity3` REAL NOT NULL, `unit3` INTEGER DEFAULT NULL, `working_hours` REAL NOT NULL, `batch` INTEGER DEFAULT NULL, `referential_quantity1` REAL NOT NULL, `referential_quantity2` REAL DEFAULT NULL, `referential_quantity3` REAL DEFAULT NULL, `referential_working_hours` REAL DEFAULT NULL, `production_date` DATE DEFAULT NULL, `warehouse` INTEGER DEFAULT NULL, FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), FOREIGN KEY (`unit1`) REFERENCES `units` (`id`), FOREIGN KEY (`unit2`) REFERENCES `units` (`id`), FOREIGN KEY (`unit3`) REFERENCES `units` (`id`), FOREIGN KEY (`warehouse`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT)")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `machines` ( `id` INTEGER PRIMARY KEY , `name` VARCHAR(250) NOT NULL, `years_age` REAL, `estimated_waste_value` REAL, `estimated_waste_currency` INTEGER, `estimated_waste_account` INTEGER, `invoice_item_id` INTEGER, `account` INTEGER, `opposite_account` INTEGER, `notes` VARCHAR(500), FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`estimated_waste_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`estimated_waste_currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")


        c.execute(
            "CREATE TABLE IF NOT EXISTS `maintenance_workers` (`id` INTEGER PRIMARY KEY, `employee_id` INTEGER NOT NULL, `maintenance_id` INTEGER NOT NULL, FOREIGN KEY (`maintenance_id`) REFERENCES `machine_maintenance` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `maintenance_workers` (`id` INTEGER PRIMARY KEY, `employee_id` INTEGER NOT NULL, `maintenance_id` INTEGER NOT NULL, FOREIGN KEY (`maintenance_id`) REFERENCES `machine_maintenance` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `maintenance_materials` (`id` INTEGER PRIMARY KEY, `name` VARCHAR(250) NOT NULL);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `maintenance_operation_materials` (`id` INTEGER PRIMARY KEY, `name` VARCHAR(250) NOT NULL, `maintenance_operation` INTEGER NOT NULL, `quantity` REAL, `unit` INTEGER, `maintenance_material_id` INTEGER, FOREIGN KEY (`maintenance_operation`) REFERENCES `machine_maintenance` (`id`) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`maintenance_material_id`) REFERENCES `maintenance_materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `machine_modes` ( `id` INTEGER PRIMARY KEY , `machine_id` INTEGER NOT NULL, `name` VARCHAR(250) NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute('CREATE TABLE IF NOT EXISTS `manufacture_machines` ("id" INTEGER PRIMARY KEY, "manufacture_id" INTEGER NOT NULL, "machine_id" INTEGER NOT NULL, "mode_id" INTEGER NOT NULL, "duration" REAL NOT NULL, "exclusive" INTEGER NOT NULL, "exclusive_percent" INTEGER NOT NULL, FOREIGN KEY ("machine_id") REFERENCES "machines" ("id"), FOREIGN KEY ("mode_id") REFERENCES "machine_modes" ("id"), FOREIGN KEY ("manufacture_id") REFERENCES "manufacture" ("id") ON DELETE CASCADE);')

        c.execute("CREATE TABLE IF NOT EXISTS `production_lines` (`id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL, `notes` TEXT DEFAULT NULL);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `machine_production_lines` (`id` INTEGER PRIMARY KEY, `machine_id` INTEGER NOT NULL, `production_line_id` INTEGER NOT NULL, `machine_notes` TEXT DEFAULT NULL, FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`production_line_id`) REFERENCES `production_lines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `aggregator` ( `id` INTEGER PRIMARY KEY , `material` INTEGER NOT NULL, `ammount` INTEGER );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `percent_plans` (`id` INTEGER PRIMARY KEY, `material` INTEGER NOT NULL, `priority` INTEGER NOT NULL DEFAULT '999999', `percent` REAL NOT NULL DEFAULT '0');")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `plans` (`id` INTEGER PRIMARY KEY, `material` INTEGER NOT NULL, `priority` INTEGER NOT NULL DEFAULT '999999', `percent` INTEGER NOT NULL DEFAULT '0');")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `variables` ( `id` INTEGER PRIMARY KEY , `variable` TEXT, `value_col` TEXT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `cost_materials` ( `id` INTEGER PRIMARY KEY , `process_id` INTEGER NOT NULL, `material` INTEGER NOT NULL, `price_sp` REAL, `price_usd` REAL, `standard_quantity` REAL, `required_quantity` REAL, `unit` TEXT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `payments` ( `id` INTEGER PRIMARY KEY , `invoice_id` INTEGER, `client_id` INTEGER NOT NULL, `ammount` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `exchange_id` INTEGER, `equilivance` REAL NOT NULL, `date_col` DATE NOT NULL, `notes` TEXT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`exchange_id`) REFERENCES `exchange_prices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`invoice_id`) REFERENCES `invoices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `sales_targets` ( `id` INTEGER PRIMARY KEY , `material` INTEGER NOT NULL, `year_col` INTEGER NOT NULL, `month_col` INTEGER NOT NULL, `location` TEXT, `target` INTEGER NOT NULL );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `settings` ( `id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL UNIQUE, `value_col` TEXT DEFAULT NULL );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `user_settings` (`id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL, `value_col` INTEGER DEFAULT NULL, `user_id` INTEGER NOT NULL, FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `clients_accounts` ( `id` INTEGER PRIMARY KEY , `used_price` INTEGER, `discount` REAL, `payment_method` TEXT, `days_count` INTEGER, `day_col` TEXT, `payment_date` DATE, `client_account_id` INTEGER, `discount_account_id` INTEGER, `tax_account_id` INTEGER, `vat_account_id` INTEGER, `tax_exempt` INTEGER DEFAULT 0, `client_id` INTEGER UNIQUE NOT NULL, `extra_account_id` INTEGER, FOREIGN KEY (`used_price`) REFERENCES `prices` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`client_id`) REFERENCES `clients` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`client_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`discount_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`tax_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`vat_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`extra_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `payment_conditions` ( `id` INTEGER PRIMARY KEY , `client_account_id` INTEGER NOT NULL, `day_number` INTEGER NOT NULL, `discount_percent` REAL, `discount_value` REAL, `discount_account_id` INTEGER, FOREIGN KEY (`discount_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `units_conversion` ( `id` INTEGER PRIMARY KEY , `unit1` INTEGER NOT NULL, `unit2` INTEGER NOT NULL, `value_col` REAL NOT NULL DEFAULT 1, `unit1_ordered` INTEGER, `unit2_ordered` INTEGER, UNIQUE (`unit1_ordered`, `unit2_ordered`), FOREIGN KEY (`unit1`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE CASCADE, FOREIGN KEY (`unit2`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE CASCADE );")

        c.execute('''
            CREATE TRIGGER IF NOT EXISTS `set_ordered_units_insert`
            AFTER INSERT ON `units_conversion`
            FOR EACH ROW
            BEGIN
                UPDATE `units_conversion`
                SET `unit1_ordered` = CASE WHEN NEW.`unit1` < NEW.`unit2` THEN NEW.`unit1` ELSE NEW.`unit2` END,
                    `unit2_ordered` = CASE WHEN NEW.`unit1` > NEW.`unit2` THEN NEW.`unit1` ELSE NEW.`unit2` END
                WHERE `id` = NEW.`id`;
            END;
            ''')

        c.execute(
            "CREATE TABLE IF NOT EXISTS `cost_centers_aggregations_distributives` ( `id` INTEGER NOT NULL PRIMARY KEY , `master_cost_center` INTEGER NOT NULL, `cost_center` INTEGER NOT NULL UNIQUE, `division_factor` REAL DEFAULT NULL, FOREIGN KEY (`cost_center`) REFERENCES `cost_centers` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_courses` ( `id` INTEGER NOT NULL PRIMARY KEY , `title` TEXT NOT NULL, `providor` TEXT NOT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `cost` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, `location` TEXT NOT NULL, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`), FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`));")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employment_requests` ( `id` INTEGER NOT NULL PRIMARY KEY , `national_id` TEXT DEFAULT NULL, `phone` TEXT DEFAULT NULL, `address` TEXT DEFAULT NULL, `name` TEXT NOT NULL, `email` TEXT DEFAULT NULL, `birthdate` DATE DEFAULT NULL, `date_col` TIMESTAMP DEFAULT CURRENT_TIMESTAMP );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employees` (`id` INTEGER PRIMARY KEY, `employment_request_id` INTEGER NOT NULL, `national_id` TEXT DEFAULT NULL, `phone` TEXT DEFAULT NULL, `address` TEXT DEFAULT NULL, `name` TEXT DEFAULT NULL, `email` TEXT DEFAULT NULL, `birthdate` DATE DEFAULT NULL, `start_date` DATE NOT NULL, `resignation_date` DATE DEFAULT NULL, `bank` TEXT DEFAULT NULL, `bank_account_number` TEXT DEFAULT NULL, `bank_notes` TEXT DEFAULT NULL, `photo` BLOB NULL, FOREIGN KEY (`employment_request_id`) REFERENCES `hr_employment_requests` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_course_employees` ( `id` INTEGER NOT NULL PRIMARY KEY , `course_id` INTEGER NOT NULL, `employee_id` INTEGER NOT NULL, `gpa` REAL DEFAULT NULL, FOREIGN KEY (`course_id`) REFERENCES `hr_courses` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_departments` ( `id` INTEGER NOT NULL PRIMARY KEY , `name` TEXT NOT NULL, `day_hours` REAL NOT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `notes` TEXT  DEFAULT NULL, `work_day_friday` tinyint(1) NOT NULL DEFAULT 0, `work_day_tuesday` tinyint(1) NOT NULL DEFAULT 0, `work_day_thursday` tinyint(1) NOT NULL DEFAULT 0, `work_day_wednesday` tinyint(1) NOT NULL DEFAULT 0, `work_day_monday` tinyint(1) NOT NULL DEFAULT 0, `work_day_sunday` tinyint(1) NOT NULL DEFAULT 0, `work_day_saturday` tinyint(1) NOT NULL DEFAULT 0, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_additional_costs` ( `id` INTEGER NOT NULL PRIMARY KEY , `statement_col` TEXT  NOT NULL, `account_id` INTEGER NULL, `department_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER NULL, `value_col` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `date_col` DATE NOT NULL, `state_col` TEXT  NOT NULL DEFAULT 'active', FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_departments_finance` ( `id` INTEGER PRIMARY KEY , `department_id` INTEGER NOT NULL, `statement_col` TEXT NOT NULL, `type_col` VARCHAR(11) NOT NULL, `value_col` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `start_date` DATE NOT NULL, `end_date` DATE DEFAULT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_departments_leaves` ( `id` INTEGER PRIMARY KEY , `department_id` INTEGER NOT NULL, `statement_col` VARCHAR(250), `duration_in_hours` REAL NOT NULL, `duration_in_days` REAL NOT NULL, `start_date` DATE NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employee_received_items` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `warehouse_id` INTEGER, `material_id` INTEGER, `quantity` REAL, `unit_id` INTEGER, `received_date` DATE, `received` INTEGER NOT NULL DEFAULT 0, FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_positions` ( `id` INTEGER PRIMARY KEY , `position_name` VARCHAR(255), `salary` REAL, `currency_id` INTEGER, `notes` VARCHAR(255), FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employees_transfers` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `department_id` INTEGER NOT NULL, `position_id` INTEGER NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employees_certificates` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `university_name` VARCHAR(255) NOT NULL, `university_specialty` VARCHAR(255) NOT NULL, `university_year` VARCHAR(4) NOT NULL, `university_certificate` VARCHAR(255), `university_gpa` FLOAT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employment_request_certificates` ( `id` INTEGER PRIMARY KEY , `employment_request_id` INTEGER NOT NULL, `university_name` VARCHAR(255) NOT NULL, `university_specialty` VARCHAR(255) NOT NULL, `university_year` VARCHAR(4) NOT NULL, `university_certificate` VARCHAR(255), `university_gpa` FLOAT, FOREIGN KEY (`employment_request_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_finance` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `type_col` VARCHAR(50) NOT NULL, `value_col` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `start_date` DATE NOT NULL, `end_date` DATE DEFAULT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `cycle` VARCHAR(50) NOT NULL DEFAULT 'month', `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_leave_types` (`id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL, `days` INTEGER, `days_in_year` INTEGER, `period` TEXT, `date_added` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, `paid` INTEGER NOT NULL DEFAULT 0);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_leaves` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `leave_type_id` INTEGER NOT NULL, `alternative_id` INTEGER NOT NULL, `duration_in_hours` REAL NOT NULL, `duration_in_days` REAL NOT NULL, `start_date` DATE NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, `state_col` TEXT NOT NULL DEFAULT 'active', `duration_type` TEXT DEFAULT NULL, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`alternative_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`leave_type_id`) REFERENCES `hr_leave_types` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_loans` (`id` INTEGER PRIMARY KEY, `employee_id` INTEGER NOT NULL, `value_col` REAL NOT NULL, `currency` INTEGER NOT NULL, `date_col` DATE NOT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `periodically_subtract_from_salary` INTEGER NOT NULL DEFAULT 0, `subtract_currency` INTEGER DEFAULT NULL, `subtract_cycle` VARCHAR(50) DEFAULT NULL, `subtract_value` REAL DEFAULT NULL, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_loans_payment` ( `id` INTEGER PRIMARY KEY , `loan_id` INTEGER NOT NULL, `value_col` INTEGER NOT NULL, `currency` INTEGER NOT NULL, `source` VARCHAR(15) NOT NULL, `date_col` DATE NOT NULL, FOREIGN KEY (`loan_id`) REFERENCES `hr_loans` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_positions_finance` ( `id` INTEGER PRIMARY KEY , `position_id` INTEGER NOT NULL, `statement_col` VARCHAR(250) NOT NULL, `type_col` VARCHAR(50) NOT NULL, `value_col` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `start_date` DATE NOT NULL, `end_date` DATE, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_positions_leaves` ( `id` INTEGER PRIMARY KEY , `position_id` INTEGER NOT NULL, `statement_col` VARCHAR(250), `duration_in_hours` REAL NOT NULL, `duration_in_days` REAL NOT NULL, `start_date` DATE NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`position_id`) REFERENCES `hr_positions` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_extra` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `department_id` INTEGER NOT NULL, `start_date` DATE NOT NULL, `value_col` REAL NOT NULL, `duration_in_hours` REAL NOT NULL, `duration_in_days` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `statement_col` VARCHAR(500), `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `state_col` VARCHAR(11) NOT NULL DEFAULT 'active', FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`department_id`) REFERENCES `hr_departments` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_settings` ( `id` INTEGER PRIMARY KEY , `name` VARCHAR(50) NOT NULL, `value_col` VARCHAR(11), `last_update` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, UNIQUE (`name`) );")

        # Trigger to update the last_update column whenever the row is updated.
        c.execute(
            '''CREATE TRIGGER IF NOT EXISTS update_hr_settings_last_update
                AFTER UPDATE ON `hr_settings`
                FOR EACH ROW
                BEGIN
                    UPDATE `hr_settings`
                    SET `last_update` = CURRENT_TIMESTAMP
                    WHERE `id` = OLD.`id`;
                END;
        ''')

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts` ( `id` INTEGER PRIMARY KEY , `employee_id` INTEGER NOT NULL, `type_col` VARCHAR(50) NOT NULL, `start_date` DATE NOT NULL, `repeatition` INTEGER DEFAULT NULL, `end_date` INTEGER NOT NULL, `value_col` REAL NOT NULL, `account_id` INTEGER DEFAULT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `statement_col` VARCHAR(500) DEFAULT NULL, `currency_id` INTEGER DEFAULT NULL, `state_col` VARCHAR(11) NOT NULL DEFAULT 'active', FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_employees_salaries_additions_discounts_payments` ( `id` INTEGER PRIMARY KEY , `salaries_additions_discounts` INTEGER NOT NULL, `date_col` DATE NOT NULL, FOREIGN KEY (`salaries_additions_discounts`) REFERENCES `hr_employees_salaries_additions_discounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_salary_blocks` (`id` INTEGER PRIMARY KEY, `from_date` DATE NOT NULL, `to_date` DATE NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP )")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_salary_block_entries` ( `id` INTEGER PRIMARY KEY , `salary_block_id` INTEGER NOT NULL, `employee_id` INTEGER NOT NULL, `statement_col` VARCHAR(500), `value_col` REAL NOT NULL, `currency` INTEGER, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`salary_block_id`) REFERENCES `hr_salary_blocks` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_insurance_blocks` ( `id` INTEGER PRIMARY KEY , `from_date` DATE NOT NULL, `to_date` DATE NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `hr_insurance_block_entries` ( `id` INTEGER PRIMARY KEY , `insurance_block_id` INTEGER NOT NULL, `employee_id` INTEGER NOT NULL, `cycles` REAL NOT NULL, `value_col` REAL NOT NULL, `currency` INTEGER, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`employee_id`) REFERENCES `hr_employees` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`insurance_block_id`) REFERENCES `hr_insurance_blocks` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `materials_machines` ( `id` INTEGER PRIMARY KEY , `material_id` INTEGER NOT NULL, `machine_id` INTEGER NOT NULL, `mode_id` INTEGER NOT NULL, `usage_duration` REAL NOT NULL, `exclusive` INTEGER NOT NULL DEFAULT 1, FOREIGN KEY (`machine_id`) REFERENCES `machines` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `resources` ( `id` INTEGER PRIMARY KEY , `name` VARCHAR(200) NOT NULL UNIQUE, `account_id` INTEGER, `notes` VARCHAR(500), FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `resources_costs` ( `id` INTEGER PRIMARY KEY , `resource_id` INTEGER NOT NULL, `value_col` REAL NOT NULL, `currency_id` INTEGER NOT NULL, `unit_id` INTEGER NOT NULL, `notes` VARCHAR(500) NOT NULL, `date_col` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (`currency_id`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `mode_resources` ( `id` INTEGER PRIMARY KEY , `mode_id` INTEGER NOT NULL, `resource_id` INTEGER NOT NULL, `consumption_per_minute` REAL NOT NULL, `unit` INTEGER NOT NULL, UNIQUE (`mode_id`, `resource_id`), FOREIGN KEY (`mode_id`) REFERENCES `machine_modes` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`resource_id`) REFERENCES `resources` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `journal_entries` ( `id` INTEGER PRIMARY KEY, `currency` INTEGER NOT NULL, `date_col` DATE NOT NULL, `entry_date` DATE NOT NULL, `origin_type` VARCHAR(250) DEFAULT NULL, `origin_id` INTEGER DEFAULT NULL, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `journal_entries_items` ( `id` INTEGER PRIMARY KEY, `journal_entry_id` INTEGER NOT NULL, `account_id` INTEGER DEFAULT NULL, `statement_col` TEXT NOT NULL, `currency` INTEGER NOT NULL, `opposite_account_id` INTEGER DEFAULT NULL, `type_col` TEXT NOT NULL, `value_col` REAL NOT NULL, `cost_center_id` INTEGER, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`journal_entry_id`) REFERENCES `journal_entries` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `journal_entries_items_distributive_cost_center_values` ( `id` INTEGER PRIMARY KEY, `journal_entry_item_id` INTEGER NOT NULL, `cost_centers_aggregations_distributives_id` INTEGER NOT NULL, `percentage` REAL NOT NULL DEFAULT 0, UNIQUE (`journal_entry_item_id`, `cost_centers_aggregations_distributives_id`), FOREIGN KEY (`cost_centers_aggregations_distributives_id`) REFERENCES `cost_centers_aggregations_distributives` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`journal_entry_item_id`) REFERENCES `journal_entries_items` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute("CREATE TABLE IF NOT EXISTS `loans` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `currency` INTEGER NOT NULL, `interest` REAL NOT NULL, `cycle` TEXT NOT NULL, `name` TEXT DEFAULT NULL, `amount` REAL NOT NULL, `account_id` INTEGER NOT NULL, `opposite_account_id` INTEGER NOT NULL, `date_col` TIMESTAMP NOT NULL, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`opposite_account_id`) REFERENCES `accounts` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute("CREATE TABLE IF NOT EXISTS `loan_payments` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `loan_id` INTEGER NOT NULL, `amount` REAL NOT NULL, `currency` INTEGER NOT NULL, `date_col` DATE NOT NULL, FOREIGN KEY (`loan_id`) REFERENCES `loans` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `invoice_types` (`id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL UNIQUE, `type_col` TEXT NOT NULL, `returned` TINYINT NOT NULL DEFAULT 0 CHECK (returned IN (0,1)));")

        c.execute("CREATE TABLE IF NOT EXISTS `receipt_docs` (`id` INTEGER PRIMARY KEY, `target_warehouse_id` INTEGER NOT NULL, `rejection_warehouse_id` INTEGER NOT NULL, `date_col` DATE NOT NULL, `material_id` INTEGER NOT NULL, `quantity` REAL NOT NULL, `unit_id` INTEGER NOT NULL, `invoice_item_id` INTEGER DEFAULT NULL, `factory_id` INTEGER DEFAULT NULL, FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), FOREIGN KEY (`unit_id`) REFERENCES `units` (`id`), FOREIGN KEY (`target_warehouse_id`) REFERENCES `warehouseslist` (`id`), FOREIGN KEY (`rejection_warehouse_id`) REFERENCES `warehouseslist` (`id`), FOREIGN KEY (`invoice_item_id`) REFERENCES `invoice_items` (`id`) ON DELETE SET NULL ON UPDATE SET NULL)")

        c.execute("CREATE TABLE IF NOT EXISTS `material_moves` (`id` INTEGER PRIMARY KEY, `source_warehouse_entry_id` INTEGER, `destination_warehouse_entry_id` INTEGER, `source_warehouse` INTEGER, `destination_warehouse` INTEGER, `quantity` REAL NOT NULL, `unit` INTEGER NOT NULL, `origin` TEXT, `origin_id` INTEGER, `date_col` DATE, FOREIGN KEY (`source_warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE SET NULL ON UPDATE CASCADE, FOREIGN KEY (`destination_warehouse`) REFERENCES `warehouseslist` (`id`) ON DELETE SET NULL ON UPDATE CASCADE, FOREIGN KEY (`unit`) REFERENCES `units` (`id`) ON UPDATE CASCADE)")

        c.execute("CREATE TABLE IF NOT EXISTS `period_start_materials` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `material_id` INTEGER NOT NULL, `quantity1` REAL NOT NULL, `unit1_id` INTEGER NOT NULL, `quantity2` REAL DEFAULT NULL, `unit2_id` INTEGER DEFAULT NULL, `quantity3` REAL DEFAULT NULL, `unit3_id` INTEGER DEFAULT NULL, `unit_price` INTEGER NOT NULL, `currency` INTEGER NOT NULL, `warehouse_id` INTEGER NOT NULL, `notes` TEXT DEFAULT NULL, `date_col` DATE NOT NULL, FOREIGN KEY (`currency`) REFERENCES `currencies` (`id`), FOREIGN KEY (`material_id`) REFERENCES `materials` (`id`), FOREIGN KEY (`unit1_id`) REFERENCES `units` (`id`), FOREIGN KEY (`unit2_id`) REFERENCES `units` (`id`), FOREIGN KEY (`unit3_id`) REFERENCES `units` (`id`), FOREIGN KEY (`warehouse_id`) REFERENCES `warehouseslist` (`id`));")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `users` (`id` INTEGER PRIMARY KEY, `username` TEXT NOT NULL UNIQUE, `password` TEXT NOT NULL, `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `criteria` ( `id` INTEGER PRIMARY KEY, `name` TEXT NOT NULL, `key_name` TEXT NOT NULL);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `permissions` ( `id` INTEGER PRIMARY KEY, `criteria_id` INTEGER NOT NULL, `user_id` INTEGER NOT NULL, `type_col` TEXT, FOREIGN KEY (`criteria_id`) REFERENCES `criteria` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT, FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT );")


        c.execute("CREATE TABLE IF NOT EXISTS `user_media` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` VARCHAR(255) NOT NULL, `media` BLOB NOT NULL, CONSTRAINT `chk_image_size` CHECK (LENGTH(media) <= 1048576))")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `user_settings` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL, `value_col` TEXT NOT NULL, `user_id` INTEGER NOT NULL, FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON UPDATE CASCADE ON DELETE RESTRICT);")

        c.execute(
            "CREATE TABLE IF NOT EXISTS `manuals` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `name` TEXT NOT NULL);")

        manuals = [
            'Lebanese_Manual',
            'Saudi_Manual',
            'Simplify_Arabic',
            'Simplify',
        ]

        for manual in manuals:
            c.execute("SELECT count(*) FROM `manuals` WHERE `name` = '" + str(manual) + "';")
            rows = c.fetchall()
            if (rows[0][0] == 0):
                c.execute("INSERT INTO `manuals` (`name`) VALUES (?)", (manual,))


        c.execute("SELECT count(*) FROM `variables` WHERE `variable` = 'api_prefix'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `variables` (`variable`,`value_col`) VALUES ('api_prefix','api')")

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
        #     c.execute("INSERT INTO `accounts` (`name`, `code`, `parent_account`) VALUES ('رأس المال', '3-1', ?)",
        #               (last_id,))
        #     last_id = c.lastrowid
        #     c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES (?, ?)",
        #               ('default_capital_account', last_id))
        # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'التكاليف'")
        # rows = c.fetchall()
        # if (rows[0][0] == 0):
        #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('التكاليف','4')")

        # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'الإيرادات'")
        # rows = c.fetchall()
        # if (rows[0][0] == 0):
        #     c.execute("INSERT INTO accounts (`name`, `code`) VALUES ('الإيرادات','5')")

        # c.execute("SELECT count(*) FROM `accounts` WHERE `name` = 'المصروفات'")
        # rows = c.fetchall()
        # if (rows[0][0] == 0):
        #     c.execute("INSERT INTO `accounts` (`name`, `code`) VALUES ('المصروفات','6')")


        # invoice types
        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='buy_return'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('buy_return', 'output', 1)")

        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='sell_return'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('sell_return', 'input', 1)")

        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='sell'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('sell', 'output', 0)")

        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='buy'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('buy', 'input', 0)")

        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='input'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('input', 'input', 0)")

        c.execute("SELECT count(*) FROM `invoice_types` WHERE `name`='output'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `invoice_types` (`name`, `type_col`, `returned`) VALUES ('output', 'output', 0)")


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
                    'HR_SETTING': 'hr_settings',
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
                    'clients': 'CLIENTS',
                    'currencies': 'CURRENCIES',
                    'groups': 'GROUPS',
                    'variables': 'VARIABLES',
                    'expenses': 'EXPENSES',
                    'invoice_types': 'INVOICE_TYPES',
                    'aggregators': 'AGGREGATORS',
                    'sales': 'SALES',
                    'loans': 'LOANS',
                    'prices': 'PRICES',
                    'units': 'UNITS',
                }


        for option, key_name in criteria_options.items():
            c.execute("SELECT count(*) FROM `criteria` WHERE `name`='" + str(option) + "'")
            rows = c.fetchall()
            if (rows[0][0] == 0):
                c.execute("INSERT INTO `criteria` (`name`, `key_name`) VALUES ('" + str(option) + "', '" + str(key_name) + "')")



        c.execute("SELECT count(*) FROM `settings` WHERE `name`='first_period'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            date_value = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
            c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('first_period', '" + str(date_value) + "')")


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

        c.execute("SELECT count(*) FROM `settings` WHERE `name`='last_period'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            date_value = date(date.today().year, 12, 31).strftime('%Y-%m-%d')
            c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('last_period', '" + str(date_value) + "')")

        c.execute("SELECT count(*) FROM `settings` WHERE `name`='operations_fixation'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            date_value = date(date.today().year, 1, 1).strftime('%Y-%m-%d')
            c.execute(
                "INSERT INTO `settings` (`name`, `value_col`) VALUES ('operations_fixation', '" + str(
                    date_value) + "')")

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


        c.execute("SELECT count(*) FROM `hr_settings` WHERE `name`='setting_month_duration'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `hr_settings` (`name`, `value_col`) VALUES ('setting_month_duration', '30')")


        # check if all default prices are availabe
        default_prices = ["المفرق", "الجملة", "نصف الجملة", "الموزع", "التصدير", "المستهلك", "اخر شراء"];
        for default_price in default_prices:
            c.execute("SELECT count(*) FROM `prices` WHERE `price`='" + str(default_price) + "'")
        rows = c.fetchall()
        if (rows[0][0] == 0):
            c.execute("INSERT INTO `prices` (`price`,`locked`) VALUES ('" + str(default_price) + "','1')")

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

                                     'buy_affects_materials_gain_loss': '0',
                                     'buy_affects_client_price': '1',
                                     'buy_discounts_affects_cost_price': '1',
                                     'buy_discounts_affects_gain': '0',
                                     'buy_affects_last_buy_price': '1',
                                     'buy_additions_affects_cost_price': '1',
                                     'buy_additions_affects_gain': '0',
                                     'buy_affects_cost_price': '1',
                                     'buy_affects_on_warehouse': 'add',

                                     'sell_affects_materials_gain_loss': '0',
                                     'sell_affects_client_price': '0',
                                     'sell_discounts_affects_cost_price': '0',
                                     'sell_discounts_affects_gain': '0',
                                     'sell_affects_last_buy_price': '0',
                                     'sell_additions_affects_cost_price': '0',
                                     'sell_additions_affects_gain': '0',
                                     'sell_affects_cost_price': '0',
                                     'sell_affects_on_warehouse': 'reduce',

                                     'buy_return_affects_materials_gain_loss': '0',
                                     'buy_return_affects_client_price': '0',
                                     'buy_return_discounts_affects_cost_price': '0',
                                     'buy_return_discounts_affects_gain': '0',
                                     'buy_return_affects_last_buy_return_price': '0',
                                     'buy_return_additions_affects_cost_price': '0',
                                     'buy_return_additions_affects_gain': '0',
                                     'buy_return_affects_cost_price': '0',
                                     'buy_return_affects_on_warehouse': 'add',

                                     'sell_return_affects_materials_gain_loss': '0',
                                     'sell_return_affects_client_price': '0',
                                     'sell_return_discounts_affects_cost_price': '0',
                                     'sell_return_discounts_affects_gain': '0',
                                     'sell_return_affects_last_sell_return_price': '0',
                                     'sell_return_additions_affects_cost_price': '0',
                                     'sell_return_additions_affects_gain': '0',
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
                c.execute("INSERT INTO `settings` (`name`, `value_col`) VALUES ('" + str(key) + "',NULLIF('" + str(
                    value) + "',''))")


        factory_database_defaults = {"factory_server": "localhost", "factory_port": "3306", "factory_username": "root",
                                     "factory_password": "root"}
        for key, value in factory_database_defaults.items():
            c.execute("SELECT count(*) FROM `settings` WHERE `name`='" + str(key) + "'")
            rows = c.fetchall()
            if (rows[0][0] == 0):
                c.execute(
                    "INSERT INTO `settings` (`name`, `value_col`) VALUES ('" + str(key) + "',NULLIF('" + str(
                        value) + "',''))")


        self.conn.commit()
        print("Tables check done.")

    def disconnectDatabase(self):
        self.conn.close()
        self.is_connected_to_database = False
