import inspect
import traceback
from datetime import datetime, date
import datetime
from ExtendedCursor import extend_cursor_factory
from cryptography.fernet import Fernet
import base64
import functools
from win32api import MessageBox
from win32con import MB_OK, MB_ICONWARNING
from typing import get_type_hints

global current_user
current_user = ''

from MysqlConnector import MysqlConnector

class DatabaseOperations(object):
    sqlconnector = ''

    def __init__(self, sqlconnector):
        class ColumnNamedExtendedCursor(extend_cursor_factory(sqlconnector)):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, index_type='mixed', **kwargs)

        self.sqlconnector = sqlconnector
        params = {
            'cursor_class' if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>" else 'factory': ColumnNamedExtendedCursor
        }
        self.cursor = self.sqlconnector.conn.cursor(**params)
        self.key = '7hJkP2sVbNqXzR4dFgT6wYmC1eU9oL3a' # 32 byte key


    def check_permission(criteria_name, required_type):
        """
        Decorator to check permissions

        Args:
            criteria_name (str): The permission criteria (e.g., 'warehouses', 'accounts')
            required_type (str): The permission type ('R' or 'W')

        Returns:
            function: Decorated function that checks permissions before execution
        """
        def decorator(func):
            @functools.wraps(func)
            def wrapper(self, *args, **kwargs):
                # Get sql_connector and user_id from the instance
                sql_connector = getattr(self, 'sqlconnector', None)
                user_id = current_user
                return_type = get_type_hints(func).get('return')

                if not sql_connector:
                    print("No sql_connector found in class instance")
                if not user_id:
                    print("No user_id found in class instance")

                db = DatabaseOperations(sql_connector)
                has_permission = db.fetchUserPermission(
                    user_id,
                    criteria_name,
                    required_type
                )

                if not has_permission:
                    # MessageBox(0, f"You don't have the required permissions for {criteria_name}", "Access Denied", MB_OK | MB_ICONWARNING)
                    if return_type == list:
                        return []
                    elif return_type == dict:
                        return {}
                    elif return_type == tuple:
                        return ()
                    elif return_type == None:
                        return None

                return func(self, *args, **kwargs)
            return wrapper
        return decorator


    def setCurrentUser(self, user_id):
        global current_user
        current_user = user_id

    @check_permission('materials', 'W')
    def addRawMaterials(self, code_value, name_value, name_en_value, quantity_value, unit, default_price) -> None:
        print("DATABASE> Add new raw material.")
        query = 'INSERT INTO materials (code,name,name_en,quantity, unit, default_price) VALUES("' + str(
            code_value) + '","' + str(
            name_value) + '","' + str(name_en_value) + '","' + str(quantity_value) + '","' + str(unit) + '","' + str(
            default_price) + '")'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'R')
    def fetchApiPrefix(self) -> list:
        print("DATABASE> Fetch Api Prefix .")
        query = "SELECT * FROM variables WHERE variable='api_prefix'"
        ##print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchall()
        return row

    @check_permission('variables', 'W')
    def updateApiPrefix(self, prefix) -> None:
        print("DATABASE> Update Api Prefix .")
        query = 'UPDATE variables SET value_col="' + str(prefix) + '" WHERE variable="api_prefix"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('currencies', 'R')
    def fetchExchangePrice(self, date='') -> list:
        print("DATABASE> Fetch exchange price on " + str(date))
        query = "SELECT * FROM exchange_prices WHERE DATE(`date_col`) <= IFNULL(NULLIF('" + str(
            date) + "',''),'9999-12-30') ORDER BY date_col desc LIMIT 1"
        print(query)
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    @check_permission('currencies', 'R')
    def fetchExchangePriceById(self, exchange_id) -> list:
        print("DATABASE> Fetch exchange price by ID " + str(exchange_id))
        query = 'SELECT * FROM exchange_prices WHERE id="' + str(exchange_id) + '"'
        ##print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('expenses', 'R')
    def fetchExpenses(self, year='', month='', calculated_in_manufacture='', time_slot='', commit=True) -> list:
        print("DATABASE> Fetch expenss in month " + str(month) + " year " + str(year))
        if str(calculated_in_manufacture) != '':
            try:
                calculated_in_manufacture = int(calculated_in_manufacture)
            except:
                calculated_in_manufacture = ''
        query = "SELECT `expenses`.*, `expenses_types`.`calculated_in_manufacture`, `currencies`.`name` as `currency_name`, `expenses_types`.`name` as `expense_name`, `expenses_types`.`account_id`, `expenses_types`.`opposite_account_id` FROM `expenses` JOIN `expenses_types` ON `expenses_types`.`id`=`expenses`.`expense_type` JOIN `currencies` ON `currencies`.`id`=`expenses`.`currency` WHERE `expenses_types`.`calculated_in_manufacture`=COALESCE(NULLIF('" + str(
            calculated_in_manufacture) + "',''),`expenses_types`.`calculated_in_manufacture`) and `expenses`.`year_col`=COALESCE(NULLIF('" + str(
            year) + "',''),`expenses`.`year_col`) and `expenses`.`month_col`=COALESCE(NULLIF('" + str(
            month) + "',''),`expenses`.`month_col`) and `expenses`.`time_slot`=COALESCE(NULLIF('" + str(
            time_slot) + "',''),`expenses`.`time_slot`)"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('currencies', 'W')
    def addExchangePrice(self, exchange_price, date) -> None:
        print("DATABASE> Add exchange price.")
        query = 'INSERT INTO exchange_prices (currency1 ,currency2 ,exchange ,date_col) VALUES (6,5,' + exchange_price + ',"' + date + '")'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('expenses', 'W')
    def addExpenses(self, expenses, currency, month, year, time_slot, expense_type) -> None:
        print("DATABASE> Add expenses of year " + str(year) + ", month " + str(month))
        query = "REPLACE INTO `expenses` (`time_slot`, `value_col`, `year_col`, `month_col`, `expense_type`, `currency`) VALUES ('" + str(
            time_slot) + "', " + str(expenses) + ", '" + str(year) + "', '" + str(month) + "', '" + str(
            expense_type) + "', '" + str(currency) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def addNewProduct(self, name_value, name_en_value, quantity, working_hours, pills, year_require, ready, code, price,
                      exchange_id, discount_1) -> None:
        print("DATABASE> Add new product.")
        query = 'INSERT INTO products (name,name_en,quantity,working_hours,pills,year_require,in_warehouse,code,price,exchange,discount_1) VALUES("' + str(
            name_value) + '","' + str(name_en_value) + '","' + str(quantity) + '","' + str(working_hours) + '","' + str(
            pills) + '","' + str(year_require) + '","' + str(ready) + '","' + str(code) + '","' + str(
            price) + '","' + str(exchange_id) + '","' + str(discount_1) + '")'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('invoice_types', 'W')
    def addInvoiceType(self, name, type_col, returned) -> None:
        print("DATABASE> Add new invoice type.")
        query = "INSERT INTO invoice_types (name, type_col, returned) VALUES ('" + name + "', '" + type_col + "', " + str(returned) + ")"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('invoice_types', 'W')
    def fetchInvoiceTypes(self , name=''):
        print("DATABASE> Fetch invoice types.")
        query = "SELECT * FROM invoice_types"
        if name:
            query += " WHERE name='" + name + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoice_types', 'W')
    def fetchInvoiceType(self, invoice_type_id):
        print("DATABASE> Fetch invoice type.")
        query = "SELECT * FROM invoice_types WHERE id='" + str(invoice_type_id) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('invoice_types', 'W')
    def removeInvoiceType(self, name) -> None:
        print("DATABASE> Remove invoice type.")
        query = "DELETE FROM invoice_types WHERE name='" + name + "'"
        self.cursor.execute(query)

        try:
            # Delete all settings for this custom invoice type
            setting_names = 'custom_invoice_type_' + name
            query = "DELETE FROM settings WHERE name LIKE '%" + str(setting_names) + "%'"
            self.cursor.execute(query)
        except:
            pass

        self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def addInvoice(self, number, date, statement, type_col, client='',client_account='', invoice_currency='', payment_method='', paid='', invoice_cost_center='', gifts_account='', invoice_warehouse='', cost_account='', added_value_account='', monetary_account='', stock_account='', gifts_opposite_account='', materials_account='', origin_id='', commit=True) -> int:
        print("DATABASE> Add new invoice.")

        # Convert None values to empty strings to prevent concatenation errors
        statement = str(statement) if statement is not None else ''
        date = str(date) if date is not None else ''

        query = "INSERT INTO invoices (type_col, number, client, client_account, payment, paid, currency, cost_center, warehouse, cost_account, gifts_account, added_value_account, monetary_account, materials_account, stock_account, gifts_opposite_account, date_col, statement_col) VALUES ('" + str(type_col) + "', " + str(
            number) + ", NULLIF('" + str(client) + "',''), NULLIF('" + str(client_account) + "',''), '" + str(payment_method) + "', " + str(paid) + ", " + str(invoice_currency) + ", NULLIF('" + str(invoice_cost_center) + "',''), NULLIF('" + str(
            invoice_warehouse) + "',''), NULLIF('" + str(cost_account) + "',''), NULLIF('" + str(
            gifts_account) + "',''), NULLIF('" + str(added_value_account) + "',''), NULLIF('" + str(
            monetary_account) + "',''), NULLIF('" + str(materials_account) + "',''), NULLIF('" + str(
            stock_account) + "',''), NULLIF('" + str(gifts_opposite_account) + "',''), '" + date + "', NULLIF('" + statement + "',''))"

        print(query)

        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('invoices', 'W')
    def updateInvoice(self, invoice_id, number, date, statement, type_col, client, client_account, invoice_currency, payment_method, paid, invoice_cost_center, gifts_account, invoice_warehouse, cost_account, added_value_account, monetary_account, stock_account, gifts_opposite_account, materials_account, commit=True) -> None:
        print("DATABASE> Update invoice #" + str(invoice_id))

        query = "UPDATE invoices SET type_col='" + str(type_col) + "', number=" + str(
            number) + ", client=" + str(client) + ", client_account=" + str(client_account) + ", payment='" + payment_method + "', paid=" + str(
            paid) + ", currency=" + str(invoice_currency) + ", cost_center=NULLIF('" + str(invoice_cost_center) + "',''), warehouse=NULLIF('" + str(
            invoice_warehouse) + "',''), cost_account=NULLIF('" + str(cost_account) + "',''), gifts_account=NULLIF('" + str(
            gifts_account) + "',''), added_value_account=NULLIF('" + str(added_value_account) + "',''), monetary_account=NULLIF('" + str(
            monetary_account) + "',''), materials_account=NULLIF('" + str(materials_account) + "',''), stock_account=NULLIF('" + str(
            stock_account) + "',''), gifts_opposite_account=NULLIF('" + str(gifts_opposite_account) + "',''), date_col='" + str(
            date) + "', statement_col=NULLIF('" + str(statement) + "','') WHERE id=" + str(invoice_id)

        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def addInvoiceDiscountAddition(self, invoice_id, account_id, type_col, cost_center_id, currency_id, exchange_id, opposite_account_id, equilivance_price, percent, commit=True) -> None:
        print("DATABASE> Add invoice discount/addition.")
        query = "INSERT INTO `invoices_discounts_additions`(`invoice_id`, `account`, `type_col`, `cost_center`, `currency`, `exchange`, `opposite_account`, `percent`, `equilivance`) VALUES ('" + str(
            invoice_id) + "','" + str(account_id) + "','" + str(type_col) + "',NULLIF('" + str(
            cost_center_id) + "',''),NULLIF(NULLIF('" + str(
            currency_id) + "',''), ''),NULLIF('" + str(
            exchange_id) + "',''),NULLIF('" + str(opposite_account_id) + "','')," + str(
            percent) + ",NULLIF('" + str(equilivance_price) + "',''))"

        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def updateInvoiceDiscountAddition(self, discount_addition_id, invoice_id, account_id, type_col, cost_center_id, currency_id, exchange_id, opposite_account_id, equilivance_price, percent, commit=True) -> None:
        print("DATABASE> Update invoice discount/addition #" + str(discount_addition_id))
        query = "UPDATE `invoices_discounts_additions` SET `invoice_id`='" + str(
            invoice_id) + "', `account`='" + str(account_id) + "', `type_col`='" + str(type_col) + "', `cost_center`=NULLIF('" + str(
            cost_center_id) + "',''), `currency`=NULLIF(NULLIF('" + str(
            currency_id) + "',''), ''), `exchange`=NULLIF('" + str(
            exchange_id) + "',''), `opposite_account`=NULLIF('" + str(opposite_account_id) + "',''), `percent`=" + str(
            percent) + ", `equilivance`=NULLIF('" + str(equilivance_price) + "','') WHERE id=" + str(discount_addition_id)

        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def removeInvoiceDiscountAddition(self, discount_addition_id, commit=True) -> None:
        print("DATABASE> Remove invoice discount/addition #" + str(discount_addition_id))
        query = "DELETE FROM `invoices_discounts_additions` WHERE id=" + str(discount_addition_id)
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()


    @check_permission('invoices', 'R')
    def fetchInvoicesCount(self) -> dict:
        print("DATABASE> Fetch invoices count.")
        query = """SELECT
                CASE
                    WHEN it.name = 'buy_return' THEN 'buy_return'
                    WHEN it.name = 'sell_return' THEN 'sell_return'
                    WHEN it.name = 'sell' THEN 'sell'
                    WHEN it.name = 'buy' THEN 'buy'
                    WHEN it.name = 'input' THEN 'input'
                    WHEN it.name = 'output' THEN 'output'
                    ELSE 'other'
                END AS invoice_type,
                COUNT(i.id) AS invoice_count
            FROM invoice_types it
            LEFT JOIN invoices i ON it.id = i.type_col
            GROUP BY invoice_type;
        """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return {row['invoice_type']: row['invoice_count'] for row in rows}


    def fetchProductProfit(self, product_id, from_date='', to_date='', currency='', origin='invoice'):
        print("DATABASE> Fetch product profit")
        profit = 0
        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        if origin =='invoice':
            buy_price = 0
            buy_price_data = self.fetchLastInvoiceOfMaterial(product_id, invoice_type='buy')
            if buy_price_data:
                material_currency = buy_price_data['invoice_currency']
                material_price = float(buy_price_data['unit_price'])
                if currency == material_currency:
                    buy_price = material_price
                else:
                    exchange_rate = self.fetchExchangeValue(
                        current_date, 
                        material_price,
                        currency
                    )
                    buy_price = round(material_price * exchange_rate[0][1], 3)

            sell_price = 0
            sell_price_data = self.fetchLastInvoiceOfMaterial(product_id, invoice_type='sell')
            if sell_price_data:
                material_currency = buy_price_data['invoice_currency']
                material_price = float(sell_price_data['unit_price'])
                if currency == material_currency:
                    sell_price = material_price
                else:
                    exchange_rate = self.fetchExchangeValue(
                        current_date, 
                        material_price,
                        currency
                    )
                    sell_price = round(material_price * exchange_rate[0][1], 3)
            profit = sell_price - buy_price

        elif origin == 'manufacture':
            manufacture_price = 0
            last_manufacture = self.fetchMaterialLastManufatureProcess(product_id)
            if last_manufacture:
                manufacture_currency = last_manufacture['currency_id']
                expenses_cost = last_manufacture['expenses_cost']
                machines_operations_cost = last_manufacture['machines_operations_cost']
                salaries_cost = last_manufacture['salaries_cost']
                composition_materials_cost = last_manufacture['composition_materials_cost']
                total_cost = expenses_cost + machines_operations_cost + salaries_cost + composition_materials_cost

                if manufacture_currency == currency:
                    manufacture_price = total_cost
                else:
                    exchange_rate = self.fetchExchangeValue(
                        current_date, 
                        total_cost,
                        currency
                    )
                manufacture_price = round(total_cost * exchange_rate[0][1], 3)

            sell_price = 0
            sell_price_data = self.fetchLastInvoiceOfMaterial(product_id, invoice_type='sell')
            if sell_price_data:
                material_currency = buy_price_data['invoice_currency']
                material_price = float(sell_price_data['unit_price'])
                if currency['id'] == material_price:
                    sell_price = material_price
                else:
                    exchange_rate = self.fetchExchangeValue(
                        current_date, 
                        material_price,
                        currency['id']
                    )
                    sell_price = round(material_price * exchange_rate, 3)

            profit = sell_price - manufacture_price

        return profit

    @check_permission('invoices', 'W')
    def addInvoiceMaterial(self, invoice_id, material_id, quantity1='', unit1_id='', quantity2='', unit2_id='', quantity3='', unit3_id='', price_type_id='', unit_price='', currency_id='', equilivance_price='', discount='', discount_percent='', addition='', addition_percent='', added_value='', gifts='', gifts_value='', gifts_discount='', warehouse_id='', cost_center_id='', notes='', exchange_id='', discount_account='', addition_account='', production_date='', expire_date='', commit=True) -> None:
        print("DATABSE> add invoice material")
        query = "INSERT INTO `invoice_items` (invoice_id, material_id, quantity1, unit1_id, quantity2, unit2_id, quantity3, unit3_id, price_type_id, unit_price, currency_id, equilivance_price, discount, discount_percent, addition, addition_percent, added_value, gifts, gifts_value, gifts_discount, warehouse_id, cost_center_id, notes, exchange_id, item_discount_account, item_addition_account, production_date, expire_date) VALUES (" + str(
            invoice_id) + ", " + str(material_id) + ", NULLIF('" + str(quantity1) + "',''), NULLIF('" + str(unit1_id) + "',''), NULLIF('" + str(
            quantity2) + "',''), NULLIF('" + str(unit2_id) + "',''), NULLIF('" + str(quantity3) + "',''), NULLIF('" + str(unit3_id) + "',''), NULLIF('" + str(
            price_type_id) + "',''), NULLIF('" + str(unit_price) + "',''), NULLIF('" + str(currency_id) + "',''), NULLIF('" + str(
            equilivance_price) + "',''), NULLIF('" + str(discount) + "',''), NULLIF('" + str(discount_percent) + "',''), NULLIF('" + str(
            addition) + "',''), NULLIF('" + str(addition_percent) + "',''), NULLIF('" + str(added_value) + "',''), NULLIF('" + str(gifts) + "', ''), NULLIF('" + str(gifts_value) + "', ''), NULLIF('" + str(
            gifts_discount) + "',''), NULLIF('" + str(warehouse_id) + "',''), NULLIF('" + str(
            cost_center_id) + "',''), NULLIF('" + str(notes) + "',''), NULLIF('" + str(
            exchange_id) + "',''), NULLIF('" + str(discount_account) + "',''), NULLIF('" + str(
            addition_account) + "',''), NULLIF('" + str(production_date) + "',''), NULLIF('" + str(expire_date) + "',''))"

        print(query)
        self.cursor.execute(query)
        invoice_item_id = self.cursor.lastrowid
        if commit:
            self.sqlconnector.conn.commit()
        return invoice_item_id

    @check_permission('invoices', 'W')
    def updateInvoiceMaterial(self, invoice_item_id, invoice_id, material_id, quantity1, unit1_id, quantity2, unit2_id, quantity3, unit3_id,price_type_id, unit_price, currency_id, equilivance_price, discount, discount_percent,addition, addition_percent, added_value, gifts, gifts_value, gifts_discount, warehouse_id, cost_center_id, notes,exchange_id, discount_account, addition_account, production_date='', expire_date='', commit=True) -> None:
        print("DATABASE> Update invoice material #" + str(invoice_item_id))
        query = "UPDATE `invoice_items` SET invoice_id=" + str(invoice_id) + ", material_id=" + str(material_id) + ", quantity1=NULLIF('" + str(
            quantity1) + "',''), unit1_id=NULLIF('" + str(unit1_id) + "',''), quantity2=NULLIF('" + str(
            quantity2) + "',''), unit2_id=NULLIF('" + str(unit2_id) + "',''), quantity3=NULLIF('" + str(quantity3) + "',''), unit3_id=NULLIF('" + str(
            unit3_id) + "',''), price_type_id=" + str(price_type_id) + ", unit_price=" + str(unit_price) + ", currency_id=" + str(
            currency_id) + ", equilivance_price=NULLIF('" + str(equilivance_price) + "',''), discount=NULLIF('" + str(discount) + "',''), discount_percent=NULLIF('" + str(
            discount_percent) + "',''), addition=NULLIF('" + str(addition) + "',''), addition_percent=NULLIF('" + str(addition_percent) + "',''), added_value=NULLIF('" + str(added_value) + "',''), gifts=NULLIF('" + str(
            gifts) + "', ''), gifts_value=NULLIF('" + str(gifts_value) + "', ''), gifts_discount=NULLIF('" + str(gifts_discount) + "',''), warehouse_id=NULLIF('" + str(
            warehouse_id) + "',''), cost_center_id=NULLIF('" + str(cost_center_id) + "',''), notes=NULLIF('" + str(
            notes) + "',''), exchange_id=NULLIF('" + str(exchange_id) + "',''), item_discount_account=NULLIF('" + str(
            discount_account) + "',''), item_addition_account=NULLIF('" + str(addition_account) + "',''), production_date=NULLIF('" + str(production_date) + "',''), expire_date=NULLIF('" + str(expire_date) + "','')  WHERE id=" + str(invoice_item_id)

        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def removeInvoiceMaterial(self, invoice_item_id, commit=True) -> None:
        print("DATABASE> Remove invoice material #" + str(invoice_item_id))
        query = "DELETE FROM `invoice_items` WHERE id=" + str(invoice_item_id)
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('materials', 'R')
    def fetchRawMaterials(self) -> list:
        print("DATABASE> fetch raw materials.")
        query = 'SELECT * FROM materials'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()

    @check_permission('materials', 'R')
    def fetchRawMaterial(self, material_id) -> list:
        print("DATABASE> fetch material #" + material_id)
        query = 'SELECT * FROM materials WHERE `id`="' + material_id + '"'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialsSuggestions(self, text) -> list:
        print("DATABASE> fetch materials suggestions.")
        query = 'SELECT * FROM materials WHERE `code` LIKE "%' + text + '%" OR `name` LIKE "%' + text + '%"'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('invoices', 'R')
    def fetchAllInvoices(self, date_filter='', client_filter='', type_filter='') -> list:
        print("DATABASE> Fetch  all invoices grouped.")
        query = (
            "SELECT `invoices`.`id`, "
            "       `invoice_types`.`name` AS `type_col`, "
            "       `invoices`.`date_col`, "
            "       `invoices`.`paid`, "
            "       `invoices`.`number`, "
            "       `invoices`.`currency`, "
            "       `currencies`.`name` AS `invoice_currency_name`, "
            "       `clients`.`name`, "
            "       `clients`.`id` AS `client_id` "
            "       FROM `invoices` "
            "       LEFT JOIN `clients` ON `invoices`.`client` = `clients`.`id` "
            "       LEFT JOIN `currencies` ON `invoices`.`currency` = `currencies`.`id` "
            "       JOIN `invoice_types` ON `invoices`.`type_col` = `invoice_types`.`id` "
            "       WHERE `invoices`.`date_col` = COALESCE(NULLIF('" + str(date_filter) + "', ''), `invoices`.`date_col`) "
            "       AND ((COALESCE(NULLIF('', ''), `invoices`.`client`) IS NOT NULL "
            "        AND `invoices`.`client` = COALESCE(NULLIF('" + str(client_filter) + "', ''), `invoices`.`client`)) "
            "       OR (COALESCE(NULLIF('" + str(client_filter) + "', ''), `invoices`.`client`) IS NULL)) "
            "       AND `invoices`.`type_col` = COALESCE(NULLIF('" + str(type_filter) + "', ''), `invoices`.`type_col`)"
        )
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'R')
    def fetchInvoices(self, material_id) -> list:
        print("DATABASE> Fetch  invoices of material #" + str(material_id))
        query = 'SELECT * FROM invoice_items WHERE `material_id`="' + str(material_id) + '"'
        ##print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'R')
    def fetchInvoice(self, invoice_id, items=False) -> list:
        print("DATABASE> Fetch invoice #" + str(invoice_id))

        # Fetch invoice data
        query = "SELECT `invoices`.*, `clients`.`name` as client_name, `currencies`.`name` as currency_name FROM invoices LEFT JOIN `clients` ON `invoices`.`client` = `clients`.`id` LEFT JOIN `currencies` ON `invoices`.`currency` = `currencies`.`id` WHERE invoices.id = '" + str(invoice_id) + "'"

        self.cursor.execute(query)
        invoice = self.cursor.fetchone()

        if not invoice:
            return None

        if items:
            # Fetch invoice items if requested
            items_query = "SELECT `invoice_items`.*, `materials`.`name` as material_name, u1.`name` as unit1_name, u2.`name` as unit2_name, u3.`name` as unit3_name, `currencies`.`name` as currency_name, `prices`.`price` as price_type_name, `exchange_prices`.`exchange` as exchange_price, da.`name` as discount_account_name, aa.`name` as addition_account_name, `warehouseslist`.`account` as warehouse_account, `warehouseslist`.`name` as warehouse_name, `cost_centers`.`name` as cost_center_name FROM `invoice_items` JOIN `materials` ON `invoice_items`.`material_id` = `materials`.`id` LEFT JOIN `units` u1 ON u1.`id` = `invoice_items`.`unit1_id` LEFT JOIN `units` u2 ON u2.`id` = `invoice_items`.`unit2_id` LEFT JOIN `units` u3 ON u3.`id` = `invoice_items`.`unit3_id` LEFT JOIN `currencies` ON `currencies`.`id` = `invoice_items`.`currency_id` LEFT JOIN `prices` ON `prices`.`id` = `invoice_items`.`price_type_id` LEFT JOIN `exchange_prices` ON `exchange_prices`.`id` = `invoice_items`.`exchange_id` LEFT JOIN `accounts` da ON da.`id` = `invoice_items`.`item_discount_account` LEFT JOIN `accounts` aa ON aa.`id` = `invoice_items`.`item_addition_account` LEFT JOIN `warehouseslist` ON `warehouseslist`.`id` = `invoice_items`.`warehouse_id` LEFT JOIN `cost_centers` ON `cost_centers`.`id` = `invoice_items`.`cost_center_id` WHERE `invoice_items`.`invoice_id` = '" + str(invoice_id) + "'"

            self.cursor.execute(items_query)
            items_rows = self.cursor.fetchall()

            # Return invoice with its items
            return {
                'invoice': invoice,
                'items': items_rows
            }

        # Return just the invoice
        return invoice

    @check_permission('invoices', 'R')
    def fetchInvoiceItems(self, invoice_id) -> list:
        print("DATABASE> Fetch  invoice #" + invoice_id)
        query = "SELECT `invoice_items`.`id`, `invoice_items`.`material_id`, `materials`.`name`, `invoice_items`.`unit_price`, `invoice_items`.`quantity1`, `invoice_items`.`unit1_id`, `units`.`name` as `unit_name` FROM `invoice_items` JOIN `materials` ON `invoice_items`.`material_id`=`materials`.`id` JOIN `units` ON `units`.`id`=`invoice_items`.`unit1_id` WHERE `invoice_items`.`invoice_id`='" + str(
            invoice_id) + "';"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'R')
    def fetchAllInvoiceItems(self, invoice_main_type='', material='', client='', from_date='', to_date='') -> list:
        query = "SELECT invoice_items.*, currencies.name AS currency_name, materials.id, materials.name AS material_name, material_moves.*, invoices.*, invoice_types.*, clients.name AS client_name, clients.phone1 AS client_phone, clients.email AS client_email FROM invoice_items LEFT JOIN materials ON invoice_items.material_id = materials.id LEFT JOIN material_moves ON material_moves.origin_id = invoice_items.id LEFT JOIN invoices ON invoice_items.invoice_id = invoices.id LEFT JOIN invoice_types ON invoices.type_col = invoice_types.id LEFT JOIN clients ON invoices.client = clients.id LEFT JOIN currencies ON invoice_items.currency_id = currencies.id WHERE (material_moves.origin = 'invoice' OR material_moves.origin = 'manufacture') AND invoice_types.type_col = COALESCE(NULLIF('" + str(invoice_main_type) + "', ''), invoice_types.type_col) AND invoice_items.material_id = COALESCE(NULLIF('" + str(material) + "', ''), invoice_items.material_id) AND invoices.client = COALESCE(NULLIF('" + str(client) + "', ''), invoices.client) AND invoices.date_col >= COALESCE(NULLIF('" + str(from_date) + "', ''), invoices.date_col) AND invoices.date_col <= COALESCE(NULLIF('" + str(to_date) + "', ''), invoices.date_col)"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows
    
    @check_permission('invoices', 'R')
    def fetchLastInvoiceOfMaterialWithDiscountsAndAdditions(self, material_id, date='', invoice_type='') -> list:
        print("DATABASE> fetch  last invoice of material #" + str(material_id) + " with discounts and additions.")
        # the query returns the latest invoice with addition and discounts before a specific given date. and if no specific date is given, it returns the latest invoice in the system
        query = "SELECT `invoice_items`.`quantity1`, `invoice_items`.`quantity2`, `invoice_items`.`quantity3`, `invoice_items`.`unit1_id`, `invoice_items`.`unit2_id`, `invoice_items`.`unit3_id`, `invoice_items`.`unit_price`, `invoice_items`.`equilivance_price`, `invoice_items`.`currency_id` AS `payment_currency`, `invoices`.`currency` AS `invoice_currency`, `invoices`.`date_col`, `invoice_items`.`id` AS `invoice_item_id`, `invoices`.`id` AS `invoices_id`, `invoice_items`.`discount` AS `item_discount`, `invoice_items`.`addition` AS `item_addition`, `invoices_discounts_additions`.`type_col` AS `discount_addition_type`, CASE WHEN `invoices_discounts_additions`.`percent` = 1 THEN `invoices_discounts_additions`.`equilivance` * `invoice_items`.`unit_price` / 100 ELSE `invoices_discounts_additions`.`equilivance` END AS `invoice_discount_addition_value` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id` = `invoices`.`id` JOIN `invoice_types` ON `invoices`.`type_col` = `invoice_types`.`id` LEFT JOIN `invoices_discounts_additions` ON `invoices`.`id` = `invoices_discounts_additions`.`invoice_id` WHERE `invoices`.`date_col` <= IFNULL(NULLIF('" + str(date) + "',''),'9999-12-30') AND `invoice_items`.`material_id` = '" + str(material_id) + "' AND `invoice_types`.`name` = COALESCE(NULLIF('" + str(invoice_type) + "',''), `invoice_types`.`name`) ORDER BY `invoices`.`date_col` DESC, `invoices`.`id` DESC LIMIT 1"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        if len(rows) > 0:
            return rows[0]
        else:
            return None

    @check_permission('invoices', 'R')
    def fetchLastInvoiceOfMaterial(self, material_id, date='', invoice_type='') -> list:
        print("DATABASE> fetch  last invoice of material #" + str(material_id))
        # the query returns the latest invoice before a specific given date. and if no specific date is given, it returns the latest invoice in the system
        query = "SELECT `invoice_items`.`quantity1`, `invoice_items`.`quantity2`, `invoice_items`.`quantity3`, `invoice_items`.`unit1_id`, `invoice_items`.`unit2_id`, `invoice_items`.`unit3_id`, `invoice_items`.`unit_price`, `invoice_items`.`equilivance_price`, `invoice_items`.`currency_id` AS `payment_currency`, `invoices`.`currency` AS `invoice_currency`, `invoices`.`date_col`, `invoice_items`.`id` AS `invoice_item_id`, `invoices`.`id` AS `invoices_id` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id` = `invoices`.`id` JOIN `invoice_types` ON `invoices`.`type_col` = `invoice_types`.`id` WHERE `invoices`.`date_col` <= IFNULL(NULLIF('" + str(
            date) + "',''),'9999-12-30') AND `invoice_items`.`material_id` = '" + str(
            material_id) + "' AND `invoice_types`.`name` = COALESCE(NULLIF('" + str(invoice_type) + "',''), `invoice_types`.`name`) ORDER BY date_col DESC,`invoices`.`id` DESC LIMIT 1;"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        if len(rows) > 0:
            return rows[0]
        else:
            return None


    @check_permission('invoices', 'R')
    def fetchInvoiceItem(self, item_id, commit=True) -> list:
        if item_id is None:
            print("DATABASE> Item ID is None")
            return None
        print("DATABASE> Fetch  invoice #" + str(item_id))
        query = "SELECT `invoice_items`.`id`, `invoice_items`.`material_id`, `materials`.`name`, `invoice_items`.`unit_price`, `invoice_items`.`quantity1`, `invoice_items`.`unit1_id`, `units`.`name` as `unit_name`, `invoice_items`.`currency_id`, `invoices`.`date_col` as `invoice_date`, `currencies`.`name` as `currency_name`, `invoice_items`.`equilivance_price` FROM `invoice_items` JOIN `materials` ON `invoice_items`.`material_id`=`materials`.`id` JOIN `units` ON `units`.`id`=`invoice_items`.`unit1_id` JOIN `invoices` ON `invoices`.`id`=`invoice_items`.`invoice_id` JOIN `currencies` ON `currencies`.`id`=`invoice_items`.`currency_id` WHERE `invoice_items`.`id`='" + str(item_id) + "';"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'W')
    def removeInvoiceItems(self, invoice_number) -> None:
        print("DATABASE> Delete invoice #" + invoice_number)
        query = 'DELETE FROM invoices WHERE `number`="' + invoice_number + '"'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('invoices', 'R')
    def fetchInvoicesValues(self, invoice_id='', client_id='') -> list:
        # THE GREAT QUERY
        # THIS QUERY SHOWS THE INVOICE VALUE, AND HOW MUCH IS LEFT TO BE PAID
        # THIS QUERY SHOWS THE INVOICE VALUE, AND THE HOW MUCH IS PAID FOR THIS INVOICE (SUM(PAYMENTS))

        query = "SELECT  `invoices`.`id`, `invoice_types`.`name` AS `invoice_type`, `invoices`.`date_col`, `invoices`.`payment`,  `invoices`.`paid`,  `invoices`.`number`,  `invoices`.`currency`, `invoices`.`statement_col`, `currencies`.`name` AS `invoice_currency_name`,  `clients`.`name`,  COALESCE(  COALESCE(  (  SELECT  SUM(  COALESCE(  `invoice_items`.`equilivance_price` * `invoice_items`.`quantity1`,  0) - COALESCE(`invoice_items`.`discount`, 0) + COALESCE(`invoice_items`.`addition`, 0) - COALESCE(  `invoice_items`.`gifts_discount`,  0))  FROM  `invoice_items`  WHERE  `invoice_items`.`invoice_id` = `invoices`.`id`),  0),  0) +(  SELECT  COALESCE(  SUM(  CASE WHEN `invoices_discounts_additions`.`type_col` = 'discount' AND `invoices_discounts_additions`.`currency` IS NOT NULL THEN -1 * `invoices_discounts_additions`.`equilivance` WHEN `invoices_discounts_additions`.`type_col` = 'discount' AND `invoices_discounts_additions`.`currency` IS NULL THEN -1 * `invoices_discounts_additions`.`equilivance` / 100 * COALESCE(  (  SELECT  SUM(  COALESCE(  `invoice_items`.`equilivance_price`,  0) - COALESCE(`invoice_items`.`discount`, 0) + COALESCE(`invoice_items`.`addition`, 0) - COALESCE(  `invoice_items`.`gifts_discount`,  0))  FROM  `invoice_items`  WHERE  `invoice_items`.`invoice_id` = `invoices`.`id`),  0) WHEN `invoices_discounts_additions`.`type_col` = 'addition' AND `invoices_discounts_additions`.`currency` IS NOT NULL THEN `invoices_discounts_additions`.`equilivance` WHEN `invoices_discounts_additions`.`type_col` = 'addition' AND `invoices_discounts_additions`.`currency` IS NULL THEN `invoices_discounts_additions`.`equilivance` / 100 * COALESCE(  (  SELECT  SUM(  COALESCE(  `invoice_items`.`equilivance_price`,  0) - COALESCE(`invoice_items`.`discount`, 0) + COALESCE(`invoice_items`.`addition`, 0) - COALESCE(  `invoice_items`.`gifts_discount`,  0))  FROM  `invoice_items`  WHERE  `invoice_items`.`invoice_id` = `invoices`.`id`),  0) ELSE 0  END),  0)  FROM  `invoices_discounts_additions`  WHERE  `invoices_discounts_additions`.`invoice_id` = `invoices`.`id`) AS `invoice_value`,  COALESCE((SELECT SUM(`journal_entries_items`.`value_col`) FROM `journal_entries_items` JOIN `journal_entries` ON `journal_entries_items`.`journal_entry_id` = `journal_entries`.`id` JOIN `clients_accounts` ON `clients_accounts`.`client_id` = `invoices`.`client` WHERE ((`journal_entries_items`.`account_id` = `clients_accounts`.`client_account_id` OR `journal_entries_items`.`account_id` = `clients_accounts`.`extra_account_id`) OR (`journal_entries_items`.`opposite_account_id` = `clients_accounts`.`client_account_id` OR `journal_entries_items`.`opposite_account_id` = `clients_accounts`.`extra_account_id`)) AND `journal_entries`.`origin_id` = `invoices`.`id` AND `journal_entries`.`origin_type` = 'invoice_payment'), 0) AS `paid_ammount`  FROM  `invoices`  JOIN `clients` ON `invoices`.`client` = `clients`.`id`  JOIN `currencies` ON `invoices`.`currency` = `currencies`.`id` JOIN `invoice_types` ON  `invoices`.`type_col` = `invoice_types`.`id` WHERE `invoices`.`client` = COALESCE(NULLIF('" + str(client_id) + "',''), `invoices`.`client`) AND `invoices`.`id`=COALESCE(NULLIF('" + str(invoice_id) + "',''),`invoices`.`id`)"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'W')
    def setInvoiceAsPaid(self, invoice_id) -> None:
        print("DATABASE> Set invoice #" + str(invoice_id) + " as paid")
        query = "UPDATE invoices SET paid = 1 WHERE id = '" + str(invoice_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('invoices', 'R')
    def fetchNormalInvoices(self) -> list:
        print("DATABASE> Fetch non-returned invoices")
        query = """
            SELECT invoices.*, invoices.id as name
            FROM invoices
            JOIN invoice_types ON invoices.type_col = invoice_types.id
            WHERE invoice_types.returned = 0
        """
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('invoices', 'R')
    def fetchInvoiceDiscountsAdditions(self, invoice_id) -> list:
        print("DATABASE> Fetch invoice discounts/additions for invoice #" + str(invoice_id))
        query = "SELECT `invoices_discounts_additions`.*, `accounts`.`name` as `account_name`, `currencies`.`name` as `currency_name`, `exchange_prices`.`exchange` as `exchange_price`, `invoices_discounts_additions`.`equilivance` as `equilivance`, `cost_centers`.`id` as `cost_center`, `cost_centers`.`name` as `cost_center_name`, `opposite_accounts`.`id` as `opposite_account`, `opposite_accounts`.`name` as `opposite_account_name` FROM `invoices_discounts_additions` JOIN `accounts` ON `invoices_discounts_additions`.`account` = `accounts`.`id` LEFT JOIN `currencies` ON `invoices_discounts_additions`.`currency` = `currencies`.`id` LEFT JOIN `exchange_prices` ON `invoices_discounts_additions`.`exchange` = `exchange_prices`.`id` LEFT JOIN `cost_centers` ON `invoices_discounts_additions`.`cost_center` = `cost_centers`.`id` LEFT JOIN `accounts` as `opposite_accounts` ON `invoices_discounts_additions`.`opposite_account` = `opposite_accounts`.`id` WHERE `invoices_discounts_additions`.`invoice_id` = '" + str(invoice_id) + "';"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'W')
    def updateMaterial_old(self, material_id, material_name, material_en_name, material_code, material_quantity,
                           material_unit, default_price) -> None:
        print("DATABASE> Update material #" + material_id)
        query = 'UPDATE materials SET `code`="' + material_code + '", `name`="' + material_name + '", `name_en`="' + material_en_name + '", `quantity`="' + material_quantity + '", `unit`="' + str(
            material_unit) + '", `default_price`="' + str(default_price) + '" WHERE `id`="' + material_id + '"'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('materials', 'W')
    def updateOrAddRawMaterials(self, code, name, quantity) -> None:
        print("DATABASE> Update or add if not exist material code " + str(code))
        if self.checkIfRowExist('materials', 'code', code):
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "UPDATE materials SET `quantity` = '" + str(quantity) + "' WHERE `code` = '" + str(
                    code) + "' COLLATE NOCASE"
            else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
                query = "UPDATE materials SET `quantity` = '" + str(quantity) + "' WHERE `code` = '" + str(
                    code) + "'"
            ##print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit
        else:
            self.addRawMaterials(code, "", name, quantity, "", "")

    @check_permission('materials', 'W')
    def updateOrAddProducts(self, code, name, quantity_in_batch, year_require, ready) -> None:
        print("DATABASE> Update or add if not exist product code " + str(code))
        if self.checkIfRowExist('products', 'code', code):
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "UPDATE products SET `name` = '" + str(name) + "', `quantity`='" + str(
                    quantity_in_batch) + "', `year_require`='" + str(year_require) + "', `in_warehouse`='" + str(
                    ready) + "' WHERE `code` = '" + str(code) + "' COLLATE NOCASE"
            else:
                query = "UPDATE products SET `name` = '" + str(name) + "', `quantity`='" + str(
                    quantity_in_batch) + "', `year_require`='" + str(year_require) + "', `in_warehouse`='" + str(
                    ready) + "' WHERE `code` = '" + str(code) + "'"
            ##print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit
        else:
            self.addNewProduct(name, '', quantity_in_batch, 0, 0, year_require, ready, code, 0, 1, 0)

    @check_permission('materials', 'R')
    def checkIfRowExist(self, table_name, where_column, where_value) -> bool:
        print("DATABASE> Check if row exists in table")
        query = "SELECT EXISTS(SELECT 1 FROM `" + str(table_name) + "` WHERE " + str(where_column) + "='" + str(
            where_value) + "' LIMIT 1)"
        print(query)
        result = self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        for row in rows:
            value = row[0]
            if value == 1:
                return True
            else:
                return False

    @check_permission('materials', 'W')
    def removeMaterial(self, material_id) -> None:
        print("DATABASE> Delete material #" + material_id)
        query = "DELETE FROM `materials` WHERE `id`='" + str(material_id) + "'"
        print(query)
        self.cursor.execute(query)

        # query = 'DELETE FROM invoices WHERE `material_id`="' + str(material_id) + '"'
        # print(query)

        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def removeProduct(self, product_id) -> None:
        print("DATABASE> Delete product #" + product_id)
        query = 'DELETE FROM products WHERE `id`="' + product_id + '"'
        ##print(query)
        self.cursor.execute(query)
        query = 'DELETE FROM product_materials WHERE `pid`="' + product_id + '"'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('currencies', 'W')
    def removeExchangePrice(self, exchange_id) -> None:
        print("DATABASE> Delete exchange price #" + exchange_id)
        query = "DELETE FROM exchange_prices WHERE `id`='" + exchange_id + "'"
        ##print(query)
        self.cursor.execute(query)
        query = "UPDATE products set exchange = '1' WHERE exchange = '" + exchange_id + "'"
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('expenses', 'W')
    def removeExpenses(self, expenses_id) -> None:
        print("DATABASE> Delete exchange price #" + expenses_id)
        query = 'DELETE FROM expenses WHERE `id`="' + expenses_id + '"'
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    # def updateInvoice(self, invoice_id, quantity, unit, unit_price, date):
    #     print("DATABASE> Update invoice #" + invoice_id)
    #     query = 'UPDATE invoices SET `quantity`="' + quantity + '", `unit`="' + unit + '", `unit_price`="' + unit_price + '", `date_col`="' + date + '" WHERE `id`="' + invoice_id + '"'
    #     ##print(query)
    #     self.cursor.execute(query)
    #     self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def updateProduct(self, product_id, name, name_en, working_hours, code, year_require, ready, price, discount_1,exchange) -> None:
        print("DATABASE> Update product #" + product_id)
        query = 'UPDATE products SET `name`="' + name + '", `name_en`="' + name_en + '", `working_hours`="' + str(
            working_hours) + '", `code`="' + code + '", `year_require`="' + year_require + '", `in_warehouse`="' + ready + '", `price`="' + str(
            price) + '", `discount_1`="' + str(discount_1) + '", `exchange`="' + str(exchange) + '" WHERE `id`="' + str(
            product_id) + '"'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('invoices', 'W')
    def removeInvoiceItem(self, invoice_item_id, commit=True) -> None:
        print("DATABASE> Delete invoice item #" + str(invoice_item_id))
        query = 'DELETE FROM invoice_items WHERE `id`="' + str(invoice_item_id) + '"'
        ##print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('invoices', 'W')
    def removeInvoice(self, invoice_id, commit=True) -> None:
        print("DATABASE> Delete invoice #" + str(invoice_id))

        invoice_items = self.fetchInvoiceItems(invoice_id)
        for item in invoice_items:
            # Delete all material moves related to the invoice items, and correct its quantity in the warehouse, then delete the invoice items
            self.correctMaterialMovesQuantity(origin='invoice', origin_id=item['id'])
            self.removeMaterialMove(origin='invoice', origin_id=item['id'], commit=False)
            self.removeInvoiceItem(item['id'], commit=False)

        query = 'DELETE FROM invoices WHERE `id`="' + str(invoice_id) + '"'
        #print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def addCompositionMaterial(self, material_quantity, material_unit, material_id, product_id) -> None:
        print("DATABASE> Add composition material to product #" + str(product_id))
        query = 'INSERT INTO product_materials (pid,mid,quantity,unit) VALUES ("' + str(product_id) + '","' + str(
            material_id) + '","' + str(material_quantity) + '","' + str(material_unit) + '")'
        ##print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'R')
    def fetchComposition(self, groupped_material_id, composition_id='') -> list:
        print("DATABASE> Fetch composition")
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT groupped_materials_composition.id, materials.name, groupped_materials_composition.composition_material_id, groupped_materials_composition.quantity, groupped_materials_composition.unit, materials.code, units.name as unit_name, compositions.id as composition_id, compositions.name as composition_name FROM compositions LEFT JOIN groupped_materials_composition ON groupped_materials_composition.composition_id = compositions.id LEFT JOIN units ON groupped_materials_composition.unit = units.id LEFT JOIN materials ON materials.id = groupped_materials_composition.composition_material_id WHERE compositions.material = %s AND compositions.id = %s"
            params = (groupped_material_id, composition_id)
        else:  # SQLite
            query = "SELECT groupped_materials_composition.id, materials.name, groupped_materials_composition.composition_material_id, groupped_materials_composition.quantity, groupped_materials_composition.unit, materials.code, units.name as unit_name, compositions.id as composition_id, compositions.name as composition_name FROM compositions LEFT JOIN groupped_materials_composition ON groupped_materials_composition.composition_id = compositions.id LEFT JOIN units ON groupped_materials_composition.unit = units.id LEFT JOIN materials ON materials.id = groupped_materials_composition.composition_material_id WHERE compositions.material = ? AND compositions.id = ?"
            params = (groupped_material_id, composition_id)
        print(query, params)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialCompositions(self, groupped_material_id='') -> list:
        print("DATABASE> Fetch compositions")
        query = "SELECT * FROM compositions WHERE `material` = '" + str(groupped_material_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialCompositionsData(self, groupped_material_id) -> list:
        print("DATABASE> Fetch composition")
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT groupped_materials_composition.id, materials.name, groupped_materials_composition.composition_material_id, groupped_materials_composition.quantity, groupped_materials_composition.unit, materials.code, units.name as unit_name, compositions.id as composition_id, compositions.name as composition_name FROM compositions LEFT JOIN groupped_materials_composition ON groupped_materials_composition.composition_id = compositions.id LEFT JOIN units ON groupped_materials_composition.unit = units.id LEFT JOIN materials ON materials.id = groupped_materials_composition.composition_material_id WHERE compositions.material = %s"
            params = (groupped_material_id,)
        else:  # SQLite
            query = "SELECT groupped_materials_composition.id, materials.name, groupped_materials_composition.composition_material_id, groupped_materials_composition.quantity, groupped_materials_composition.unit, materials.code, units.name as unit_name, compositions.id as composition_id, compositions.name as composition_name FROM compositions LEFT JOIN groupped_materials_composition ON groupped_materials_composition.composition_id = compositions.id LEFT JOIN units ON groupped_materials_composition.unit = units.id LEFT JOIN materials ON materials.id = groupped_materials_composition.composition_material_id WHERE compositions.material = ?"
            params = (groupped_material_id,)
        print(query, params)
        self.cursor.execute(query, params)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialComposition(self, id):
        print("DATABASE> Fetch composition")
        query = "SELECT * FROM compositions WHERE `id` = '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row
    
    @check_permission('materials', 'R')
    def fetchGrouppedMaterials(self) -> list:
        print("DATABASE> Fetch materials")
        query = "SELECT * FROM materials WHERE `groupped`='1'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('materials', 'R')
    def fetchProducedMaterials(self) -> list:
        print("DATABASE> Fetch produced materials")
        query = "SELECT `materials`.*, units1.name AS unit1_name, units2.name AS unit2_name, units3.name AS unit3_name, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` THEN `value_col` WHEN `unit1` = `materials`.`unit2` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit2`) AS `unit1_to_unit2_rate`, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` THEN `value_col` WHEN `unit1` = `materials`.`unit3` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit3`) AS `unit1_to_unit3_rate` FROM `materials` LEFT JOIN units units1 ON `materials`.`unit1` = `units1`.`id` LEFT JOIN units units2 ON `materials`.`unit2` = `units2`.`id` LEFT JOIN units units3 ON `materials`.`unit3` = `units3`.`id` WHERE `groupped`='1'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('clients', 'R')
    def fetchClients(self, client_type='') -> list:
        rows = []
        print("DATABASE> Fetch all clients")
        query = "SELECT * FROM `clients` WHERE `clients`.`client_type` = COALESCE(NULLIF('" + str(client_type) + "', ''),`clients`.`client_type`) AND `deleted` = '0'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('clients', 'R')
    def fetchClient(self, client_id) -> list:
        print("DATABASE> Fetch  client #" + str(client_id))
        query = "SELECT `clients`.`id`, `clients`.`name`, `clients`.`governorate`, `clients`.`address`, `clients`.`email`, `clients`.`phone1`, `clients`.`phone2`, `clients`.`phone3`, `clients`.`phone4`, `clients`.`client_type`, `clients_accounts`.`id` as `clients_accounts_id`, `clients_accounts`.`used_price`, `clients_accounts`.`discount`, `clients_accounts`.`payment_method`, `clients_accounts`.`days_count`, `clients_accounts`.`day_col`, `clients_accounts`.`payment_date`, `clients_accounts`.`client_account_id`, `clients_accounts`.`discount_account_id`, `clients_accounts`.`tax_account_id`, `clients_accounts`.`vat_account_id`, `clients_accounts`.`tax_exempt`, `clients_accounts`.`extra_account_id` FROM `clients` LEFT JOIN `clients_accounts` ON `clients`.`id` = `clients_accounts`.`client_id` WHERE `clients`.`id` = '" + str(client_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('clients', 'W')
    def addClient(self, name, governorate, address, email, phone1, phone2, phone3, phone4, client_type) -> None:
        print("DATABASE> Add client")
        query = "INSERT INTO clients (name, governorate, address, email, phone1, phone2, phone3, phone4, client_type) VALUES ('" + str(
            name) + "','" + str(governorate) + "','" + str(address) + "','" + str(email) + "','" + str(phone1) + "','" + str(phone2) + "','" + str(phone3) + "','" + str(phone4) + "','" + str(client_type) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('clients', 'W')
    def updateClient(self, client_id, name, governorate, address, email, phone1, phone2, phone3, phone4) -> None:
        print("DATABASE> Fetch Api Prefix .")
        query = "UPDATE clients SET name='" + str(name) + "', governorate='" + str(governorate) + "', address='" + str(
            address) + "', email='" + str(email) + "', phone1='" + str(phone1) + "', phone2='" + str(
            phone2) + "', phone3='" + str(phone3) + "',phone4='" + str(phone4) + "' where id='" + str(client_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('clients', 'W')
    def removeClient(self, client_id) -> None:
        print("DATABASE> Soft delete client #" + str(client_id))

        query = 'UPDATE clients SET deleted = 1 WHERE id = "' + str(client_id) + '"'
        self.cursor.execute(query)

        self.sqlconnector.conn.commit()

    @check_permission('invoices', 'R')
    def checkInvoiceExists(self, invoice_number) -> bool:
        print("DATABASE> Check invoice existence.")
        query = 'SELECT count(*) as count FROM invoices WHERE number LIKE "' + str(invoice_number) + '"'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        for row in rows:
            count = row[0]
        if count > 0:
            return True
        else:
            return False


    @check_permission('materials', 'W')
    def removeCompositionMaterial(self, composition_material_id) -> None:
        print("DATABASE> Delete composition material #" + composition_material_id)
        query = 'DELETE FROM product_materials WHERE `id`="' + composition_material_id + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        print("Deleted invoice #" + composition_material_id)

    @check_permission('materials', 'R')
    def fetchAverageMaterialPrice(self, material_id, targeted_currency=None, from_date='', to_date='', invoice_type='',currency_exchage_date='',targeted_unit=None):

        print("DATABASE> Calculate average price of " + str(material_id) + " until " + str(to_date))

        if not targeted_unit:
            # fetch material's default unit
            material_details = self.fetchMaterial(material_id)
            material_units = {1: material_details[12], 2: material_details[13], 3: material_details[14]}
            default_unit = material_units[material_details[15]]
            targeted_unit = default_unit

        query = "SELECT `invoice_items`.`unit1_id`,`invoice_items`.`unit_price`,  `invoice_items`.`currency_id` AS `payment_currency` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id` = `invoices`.`id` WHERE `invoices`.`date_col` <= COALESCE(NULLIF('" + str(to_date) + "',''),`invoices`.`date_col`) AND `invoice_items`.`material_id` = '" + str(material_id) + "' AND `invoices`.`type_col` = COALESCE(NULLIF('" + str(invoice_type) + "',''),`invoices`.`type_col`) AND `invoices`.`date_col`>=COALESCE(NULLIF('" + str(
            from_date) + "',''),`invoices`.`date_col`)"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        price_of_all_invoices = {}  # dict{currency_id=sum of all invoices in that currency}

        def addPrice(currency, price):
            nonlocal price_of_all_invoices
            if currency in price_of_all_invoices:
                if isinstance(price_of_all_invoices[currency], list):
                    price_of_all_invoices[currency].append(price)
                else:
                    # If the value is not a list, convert it to a list and then append
                    price_of_all_invoices[currency] = [price_of_all_invoices[currency], price]
            else:
                price_of_all_invoices[currency] = [price]

        for row in rows:
            unit1_id = row['unit1_id']
            price = row['unit_price']
            currency = row['payment_currency']

            # Handle unit conversion if needed
            if unit1_id == targeted_unit:
                pass
            else:
                try:
                    conversion_rate = self.fetchUnitConversionValueBetween(unit1_id, targeted_unit)
                    quantity_in_default_unit = 1 * conversion_rate
                    price = float(price) / float(quantity_in_default_unit)
                except:
                    price = 0

            if targeted_currency:
                if currency == targeted_currency:
                    addPrice(targeted_currency, price)  # Store under target currency
                else:
                    if currency_exchage_date and currency_exchage_date:
                        exchange_value = self.fetchExchangeValue(currency, targeted_currency, currency_exchage_date)
                        if not exchange_value:
                            exchange_value = self.fetchExchangeValue(currency, targeted_currency)
                    else:
                        exchange_value = self.fetchExchangeValue(currency, targeted_currency, to_date)

                    if exchange_value:
                        # Convert price to target currency before adding
                        converted_price = price * float(exchange_value[0][1])
                        addPrice(targeted_currency, converted_price)  # Store under target currency
                    else:
                        print("No conversion rate found. (fetchAverageMaterialPrice(...))")
            else:
                addPrice(currency, price)  # No target currency, store under original currency

        average_prices = {}
        for currency in price_of_all_invoices:
            prices = price_of_all_invoices[currency]
            # Calculate the average of prices for each currency
            average_price = sum(prices) / len(prices)
            average_prices[currency] = average_price

        if targeted_currency:
            if targeted_currency in average_prices:
                result = average_prices[targeted_currency]
            else:
                result = 0
        else:
            result = average_prices

        return result

    @check_permission('materials', 'R')
    def fetchMaximumMaterialPrice(self, material_id, targeted_currency, from_date='', to_date='', invoice_type='',currency_exchage_date=''):
        print("DATABASE> Calculate average price of " + str(material_id) + " until " + str(date))

        # fetch material's default unit
        material_details = self.fetchMaterial(material_id)
        material_units = {1: material_details[12], 2: material_details[13], 3: material_details[14]}
        default_unit = material_units[material_details[15]]

        query = "SELECT `invoice_items`.`unit1_id`,`invoice_items`.`unit_price`,  `invoice_items`.`currency_id` AS `payment_currency` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id` = `invoices`.`id` WHERE `invoices`.`date_col` <= COALESCE(NULLIF('" + str(
            to_date) + "',''),`invoices`.`date_col`) AND `invoice_items`.`material_id` = '" + str(
            material_id) + "' AND `invoices`.`type_col` = COALESCE(NULLIF('" + str(
            invoice_type) + "',''),`invoices`.`type_col`) AND `invoices`.`date_col`>=COALESCE(NULLIF('" + str(
            from_date) + "',''),`invoices`.`date_col`)"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        maximum_price = 0
        for row in rows:
            unit1_id = row[0]
            price = row[1]
            currency = row[2]
            if unit1_id == default_unit:
                pass
            else:
                conversion_rate = self.fetchUnitConversionValueBetween(unit1_id, default_unit)
                quantity_in_default_unit = 1 * conversion_rate
                price = float(price) / float(quantity_in_default_unit)

            if currency == targeted_currency:
                if float(price) > float(maximum_price):
                    maximum_price = price
            else:
                if currency_exchage_date:
                    exchange_value = self.fetchExchangeValue(currency, targeted_currency,currency_exchage_date)
                else:
                    exchange_value = self.fetchExchangeValue(currency, targeted_currency, to_date)

                if exchange_value:
                    price = price * float(exchange_value[0][1])
                    if float(price) > float(maximum_price):
                        maximum_price = price
                else:
                    print("No conversion rate found. (fetchMaximumMaterialPrice(...))")
                    pass

        return maximum_price

    @check_permission('manufacture', 'W')
    def saveManufactureProcess(self,produced_materials, manufacture_date,working_hours, ingredients_pullout_date, expenses_cost, currency, input_warehouse, account, mid_account, mid_account_input, batch_number,expenses_type, expenses_distribution, material_pricing_method,composition_materials_cost, machines_operation_cost, salaries_cost, quantity_unit_expenses, ingredients_pullout_method, ingredients_pullout_account,composition_data, machines_data, production_date, commit=True) -> None:

        print("DATABASE> Save manufacure process data")

        query = "INSERT INTO `manufacture` (`pullout_date`, `date_col`, `expenses_type`, `material_pricing_method`, `expenses_cost`, `currency`, `machines_operation_cost`, `salaries_cost`, `mid_account`, `mid_account_input`, `account`, `composition_materials_cost`, `quantity_unit_expenses`, `expenses_distribution`, `ingredients_pullout_method`, `ingredients_pullout_account`, `working_hours`) VALUES ('" + str(
            ingredients_pullout_date) + "', '" + str(manufacture_date) + "', '" + str(expenses_type) + "', '" + str(
            material_pricing_method) + "', '" + str(expenses_cost) + "', '" + str(currency) + "', '" + str(
            machines_operation_cost) + "', '" + str(salaries_cost) + "', '" + str(
            mid_account) + "', '" + str(mid_account_input) + "', '" + str(account) + "', '" + str(composition_materials_cost) + "', '" + str(
            quantity_unit_expenses) + "', '" + str(expenses_distribution) + "', '" + str(
            ingredients_pullout_method) + "', '" + str(ingredients_pullout_account)+  "', '" + str(working_hours) + "')"

        print(query)
        self.cursor.execute(query)
        manufacture_id = self.cursor.lastrowid

        for material in produced_materials:
            material_id = material["material_id"] if material["material_id"] is not None else ''
            warehouse_id = material["warehouse"] if material["warehouse"] is not None else ''

            # Produced quantities
            quantity1 = material["quantities_and_units"]["quantity1"]["amount"] if material["quantities_and_units"]["quantity1"]["amount"] is not None else ''
            damaged_quantity1 = material["quantities_and_units"]["damaged_quantity1"]["amount"] if material["quantities_and_units"]["damaged_quantity1"]["amount"] is not None else ''
            unit1 = material["quantities_and_units"]["quantity1"]["unit"] if material["quantities_and_units"]["quantity1"]["unit"] is not None else ''
            quantity2 = material["quantities_and_units"]["quantity2"]["amount"] if material["quantities_and_units"]["quantity2"]["amount"] is not None else ''
            damaged_quantity2 = material["quantities_and_units"]["damaged_quantity2"]["amount"] if material["quantities_and_units"]["damaged_quantity2"]["amount"] is not None else ''
            unit2 = material["quantities_and_units"]["quantity2"]["unit"] if material["quantities_and_units"]["quantity2"]["unit"] is not None else ''
            quantity3 = material["quantities_and_units"]["quantity3"]["amount"] if material["quantities_and_units"]["quantity3"]["amount"] is not None else ''
            damaged_quantity3 = material["quantities_and_units"]["damaged_quantity3"]["amount"] if material["quantities_and_units"]["damaged_quantity3"]["amount"] is not None else ''
            unit3 = material["quantities_and_units"]["quantity3"]["unit"] if material["quantities_and_units"]["quantity3"]["unit"] is not None else ''

            # Referential quantities
            ref_quantity1 = material["referential_quantities"]["quantity1"]["amount"] if material["referential_quantities"]["quantity1"]["amount"] is not None else ''
            ref_unit1 = material["referential_quantities"]["quantity1"]["unit"] if material["referential_quantities"]["quantity1"]["unit"] is not None else ''
            ref_quantity2 = material["referential_quantities"]["quantity2"]["amount"] if material["referential_quantities"]["quantity2"]["amount"] is not None else ''
            ref_unit2 = material["referential_quantities"]["quantity2"]["unit"] if material["referential_quantities"]["quantity2"]["unit"] is not None else ''
            ref_quantity3 = material["referential_quantities"]["quantity3"]["amount"] if material["referential_quantities"]["quantity3"]["amount"] is not None else ''
            ref_unit3 = material["referential_quantities"]["quantity3"]["unit"] if material["referential_quantities"]["quantity3"]["unit"] is not None else ''

            # Working hours
            working_hours_ref = material["working_hours_ref"] if material["working_hours_ref"] is not None else ''
            working_hours_produced = material["working_hours_produced"] if material["working_hours_produced"] is not None else ''

            # Batch
            batch = material["batch"] if material["batch"] is not None else ''
            query = "INSERT INTO `manufacture_produced_materials` (`manufacture_id`, `material_id`, `quantity1`, `damaged_quantity1`, `unit1`, `quantity2`, `damaged_quantity2`, `unit2`, `quantity3`, `damaged_quantity3`, `unit3`, `working_hours`, `batch`, `referential_quantity1`, `referential_quantity2`, `referential_quantity3`, `referential_working_hours`, `production_date`, `warehouse`) VALUES ('" + str(manufacture_id) + "', '" + str(material_id) + "', NULLIF('" + str(quantity1) + "', ''), NULLIF('" + str(damaged_quantity1) + "', ''), NULLIF('" + str(unit1) + "', ''), NULLIF('" + str(quantity2) + "', ''), NULLIF('" + str(damaged_quantity2) + "', ''), NULLIF('" + str(unit2) + "', ''), NULLIF('" + str(quantity3) + "', ''), NULLIF('" + str(damaged_quantity3) + "', ''), NULLIF('" + str(unit3) + "', ''), NULLIF('" + str(working_hours_produced) + "', ''), NULLIF('" + str(batch) + "', ''), NULLIF('" + str(ref_quantity1) + "', ''), NULLIF('" + str(ref_quantity2) + "', ''), NULLIF('" + str(ref_quantity3) + "', ''), NULLIF('" + str(working_hours_ref) + "', ''), NULLIF('" + str(production_date) + "', ''), NULLIF('" + str(warehouse_id) + "', ''))"
            print(query)
            self.cursor.execute(query)

        for material in composition_data:
            row_type = material[0] if material[0] is not None else ''
            composition_material_id = material[1] if material[1] is not None else ''
            standartd_quantity = material[2] if material[2] is not None else ''
            unit = material[3] if material[3] is not None else ''
            manufactured_quantity = material[4] if material[4] is not None else ''
            unit_cost = material[5] if material[5] is not None else ''
            currency_id = material[6] if material[6] is not None else ''
            warehouse_id = material[7] if material[7] is not None else ''
            warehouse_account_id = material[8] if material[8] is not None else ''
            warehouse_quantity = material[9] if material[9] is not None else ''
            pulled_quantity = material[10] if material[10] is not None else ''
            shortage = material[11] if material[11] is not None else ''


            query = "INSERT INTO `manufacture_materials` (`manufacture_id`, `composition_item_id`, `standard_quantity`, `required_quantity`, `unit`, `unit_cost`, `row_type`, `warehouse_id`, `warehouse_account_id`, `pulled_quantity`, `shortage`, `currency`, `warehouse_quantity`) VALUES ('" + str(manufacture_id) + "', '" + str(composition_material_id) + "', NULLIF('" + str(standartd_quantity) + "',''), NULLIF('" + str(manufactured_quantity) + "', ''), NULLIF('" + str(
                1) + "', ''), NULLIF('" + str(unit_cost) + "', ''), '" + row_type + "', NULLIF('" + str(
                warehouse_id) + "', ''), NULLIF('" + str(warehouse_account_id) + "', ''), NULLIF('" + str(
                pulled_quantity) + "', ''), NULLIF('" + str(shortage) + "', ''), '" + str(
                currency) + "', NULLIF('" + str(warehouse_quantity) + "', ''))"

            print(query)
            self.cursor.execute(query)

        for machine in machines_data:
            machine_id = machine[0]
            mode_id = machine[1]
            duration_in_hours = machine[2]
            exclusive_use = machine[3]
            exclusive_percentage = machine[4]

            query = "INSERT INTO `manufacture_machines`(`manufacture_id`, `machine_id`, `mode_id`, `duration`, `exclusive`, `exclusive_percent`) VALUES ('" + str(
                manufacture_id) + "', '" + str(machine_id) + "', '" + str(mode_id) + "', '" + str(
                duration_in_hours) + "', '" + str(exclusive_use) + "', '" + str(exclusive_percentage) + "')"

            print(query)
            self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()
        return manufacture_id

    @check_permission('manufacture', 'W')
    def saveManufactureProcessMaterial(self, manufacture_id, composition_item_id, standard_quantity, required_quantity, unit, unit_cost, pulled_quantity, shortage, row_type) -> None:
        print("DATABASE> Save manufacure process materials")
        query = "INSERT INTO `manufacture_materials`(`manufacture_id`, `composition_item_id`, `standard_quantity`, `required_quantity`, `unit`, `unit_cost`, `pulled_quantity`, `shortage`, `row_type`) VALUES ('" + str(manufacture_id) + "','" + str(composition_item_id) + "','" + str(standard_quantity) + "','" + str(
            required_quantity) + "','" + str(unit) + "','" + str(unit_cost) + "','" + str(pulled_quantity) + "','" + str(shortage) + "','" + str(row_type) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('manufacture', 'W')
    def removeManufactureProcessMaterial(self, id) -> None:
        print("DATABASE> Delete manufacture process material id #" + str(id))
        query = 'DELETE FROM `manufacture_materials` WHERE `id`="' + str(id) + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    def removeManufactureProcessData(self, id ,commit=False) -> None:
        print("DATABASE> Delete manufacture process data id #" + str(id))
        query = 'DELETE FROM `manufacture_materials` WHERE `manufacture_id`="' + str(id) + '"'
        # print(query)
        self.cursor.execute(query)

        query = 'DELETE FROM `manufacture_produced_materials` WHERE `manufacture_id`="' + str(id) + '"'
        # print(query)
        self.cursor.execute(query)

        query = 'DELETE FROM `manufacture_machines` WHERE `manufacture_id`="' + str(id) + '"'
        # print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('manufacture', 'W')
    def updateManufactureProcessData(self, id, working_hours, pullout_date, quantity1, manufacture_date, standard_hours, expenses_type, material_pricing_method) -> None:
        print("DATABASE> Update manufacure process data")
        query = 'UPDATE `manufacture` SET `pullout_date`="' + str(pullout_date) + '",`date_col`="' + str(
            manufacture_date) + '",`expenses_type`="' + str(expenses_type) + '",`material_pricing_method`="' + str(
            material_pricing_method) + '" WHERE `id`="' + str(id) + '"'
        print(query)
        self.cursor.execute(query)

        # Update manufacture_produced_material table
        query = 'UPDATE `manufacture_produced_materials` SET `working_hours`="' + str(working_hours) + '",`referential_working_hours`="' + str(standard_hours) + '",`material_id`="' + str(id) + '",`quantity1`="' + str(quantity1) + '" WHERE `material_id`="' + str(id) + '"'
        print(query)
        self.cursor.execute(query)

        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('manufacture', 'W')
    def updateManufactureProcessData2(self, manufacture_process_id,produced_materials, manufacture_date,working_hours, ingredients_pullout_date, expenses_cost, currency, input_warehouse, account, mid_account, mid_account_input, batch_number,expenses_type, expenses_distribution, material_pricing_method,composition_materials_cost, machines_operation_cost, salaries_cost, quantity_unit_expenses, ingredients_pullout_method, ingredients_pullout_account,composition_data, machines_data, production_date, commit=True) -> None:

        print("DATABASE> Update manufacture process data")

        query = "UPDATE `manufacture` SET `pullout_date`='" + str(
            ingredients_pullout_date) + "', `date_col`='" + str(manufacture_date) + "', `expenses_type`='" + str(expenses_type) + "', `material_pricing_method`='" + str(
            material_pricing_method) + "', `expenses_cost`='" + str(expenses_cost) + "', `currency`='" + str(currency) + "', `machines_operation_cost`=" + str(
            machines_operation_cost) + ", `salaries_cost`=" + str(salaries_cost) + ", `mid_account`='" + str(
            mid_account) + "', `mid_account_input`='" + str(mid_account_input) + "', `account`='" + str(account) + "', `composition_materials_cost`=" + str(composition_materials_cost) + ", `quantity_unit_expenses`=" + str(
            quantity_unit_expenses) + ", `expenses_distribution`='" + str(expenses_distribution) + "', `ingredients_pullout_method`='" + str(
            ingredients_pullout_method) + "', `ingredients_pullout_account`='" + str(ingredients_pullout_account) + "' WHERE `id`='" + str(manufacture_process_id) + "'"

        print(query)
        self.cursor.execute(query)

        for material in produced_materials:
            material_id = material["material_id"] if material["material_id"] is not None else ''
            warehouse_id = material["warehouse"] if material["warehouse"] is not None else ''

            # Produced quantities
            quantity1 = material["quantities_and_units"]["quantity1"]["amount"] if material["quantities_and_units"]["quantity1"]["amount"] is not None else ''
            unit1 = material["quantities_and_units"]["quantity1"]["unit"] if material["quantities_and_units"]["quantity1"]["unit"] is not None else ''
            quantity2 = material["quantities_and_units"]["quantity2"]["amount"] if material["quantities_and_units"]["quantity2"]["amount"] is not None else ''
            unit2 = material["quantities_and_units"]["quantity2"]["unit"] if material["quantities_and_units"]["quantity2"]["unit"] is not None else ''
            quantity3 = material["quantities_and_units"]["quantity3"]["amount"] if material["quantities_and_units"]["quantity3"]["amount"] is not None else ''
            unit3 = material["quantities_and_units"]["quantity3"]["unit"] if material["quantities_and_units"]["quantity3"]["unit"] is not None else ''

            # Referential quantities
            ref_quantity1 = material["referential_quantities"]["quantity1"]["amount"] if material["referential_quantities"]["quantity1"]["amount"] is not None else ''
            ref_unit1 = material["referential_quantities"]["quantity1"]["unit"] if material["referential_quantities"]["quantity1"]["unit"] is not None else ''
            ref_quantity2 = material["referential_quantities"]["quantity2"]["amount"] if material["referential_quantities"]["quantity2"]["amount"] is not None else ''
            ref_unit2 = material["referential_quantities"]["quantity2"]["unit"] if material["referential_quantities"]["quantity2"]["unit"] is not None else ''
            ref_quantity3 = material["referential_quantities"]["quantity3"]["amount"] if material["referential_quantities"]["quantity3"]["amount"] is not None else ''
            ref_unit3 = material["referential_quantities"]["quantity3"]["unit"] if material["referential_quantities"]["quantity3"]["unit"] is not None else ''

            # Working hours
            working_hours_ref = material["working_hours_ref"] if material["working_hours_ref"] is not None else ''
            working_hours_produced = material["working_hours_produced"] if material["working_hours_produced"] is not None else ''

            # Batch
            batch = material["batch"] if material["batch"] is not None else ''
            query = "INSERT INTO `manufacture_produced_materials` (`manufacture_id`, `material_id`, `quantity1`, `unit1`, `quantity2`, `unit2`, `quantity3`, `unit3`, `working_hours`, `batch`, `referential_quantity1`, `referential_quantity2`, `referential_quantity3`, `referential_working_hours`, `production_date`, `warehouse`) VALUES ('" + str(manufacture_process_id) + "', '" + str(material_id) + "', NULLIF('" + str(quantity1) + "', ''), NULLIF('" + str(unit1) + "', ''), NULLIF('" + str(quantity2) + "', ''), NULLIF('" + str(unit2) + "', ''), NULLIF('" + str(quantity3) + "', ''), NULLIF('" + str(unit3) + "', ''), NULLIF('" + str(working_hours_produced) + "', ''), NULLIF('" + str(batch) + "', ''), NULLIF('" + str(ref_quantity1) + "', ''), NULLIF('" + str(ref_quantity2) + "', ''), NULLIF('" + str(ref_quantity3) + "', ''), NULLIF('" + str(working_hours_ref) + "', ''), NULLIF('" + str(production_date) + "', ''), NULLIF('" + str(warehouse_id) + "', ''))"
            print(query)
            self.cursor.execute(query)

        for material in composition_data:
            row_type = material[0] if material[0] is not None else ''
            composition_material_id = material[1] if material[1] is not None else ''
            standartd_quantity = material[2] if material[2] is not None else ''
            unit = material[3] if material[3] is not None else ''
            manufactured_quantity = material[4] if material[4] is not None else ''
            unit_cost = material[5] if material[5] is not None else ''
            currency_id = material[6] if material[6] is not None else ''
            warehouse_id = material[7] if material[7] is not None else ''
            warehouse_account_id = material[8] if material[8] is not None else ''
            warehouse_quantity = material[9] if material[9] is not None else ''
            pulled_quantity = material[10] if material[10] is not None else ''
            shortage = material[11] if material[11] is not None else ''


            query = "INSERT INTO `manufacture_materials` (`manufacture_id`, `composition_item_id`, `standard_quantity`, `required_quantity`, `unit`, `unit_cost`, `row_type`, `warehouse_id`, `warehouse_account_id`, `pulled_quantity`, `shortage`, `currency`, `warehouse_quantity`) VALUES ('" + str(manufacture_process_id) + "', '" + str(composition_material_id) + "', NULLIF('" + str(standartd_quantity) + "',''), NULLIF('" + str(manufactured_quantity) + "', ''), NULLIF('" + str(
                1) + "', ''), NULLIF('" + str(unit_cost) + "', ''), '" + row_type + "', NULLIF('" + str(
                warehouse_id) + "', ''), NULLIF('" + str(warehouse_account_id) + "', ''), NULLIF('" + str(
                pulled_quantity) + "', ''), NULLIF('" + str(shortage) + "', ''), '" + str(
                currency) + "', NULLIF('" + str(warehouse_quantity) + "', ''))"

            print(query)
            self.cursor.execute(query)

        for machine in machines_data:
            machine_id = machine[0]
            mode_id = machine[1]
            duration_in_hours = machine[2]
            exclusive_use = machine[3]
            exclusive_percentage = machine[4]

            query = "INSERT INTO `manufacture_machines`(`manufacture_id`, `machine_id`, `mode_id`, `duration`, `exclusive`, `exclusive_percent`) VALUES ('" + str(
                manufacture_process_id) + "', '" + str(machine_id) + "', '" + str(mode_id) + "', '" + str(
                duration_in_hours) + "', '" + str(exclusive_use) + "', '" + str(exclusive_percentage) + "')"

            print(query)
            self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()
        return manufacture_process_id

    @check_permission('materials', 'W')
    def increaseProductQuantity(self, product_id, quantity) -> None:
        print("DATABASE> Increase quantity of product #" + str(product_id))
        query = "UPDATE `products` SET `in_warehouse`=`products`.`in_warehouse`+" + str(
            int(float(quantity))) + " WHERE `products`.`id`='" + str(product_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def decreaseProductQuantity(self, product_id, quantity) -> None:
        print("DATABASE> Decrease quantity of product #" + str(product_id))
        query = "UPDATE `products` SET `in_warehouse`=`products`.`in_warehouse`-" + str(
            int(float(quantity))) + " WHERE `products`.`id`='" + str(product_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def increaseMaterialQuantity(self, material_id, quantity) -> None:
        print("DATABASE> Increase quantity of material #" + str(material_id))
        query = "UPDATE `materials` SET `quantity`=`materials`.`quantity`+" + str(
            float(quantity)) + " WHERE `materials`.`id`='" + str(material_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'W')
    def decreaseMaterialQuantity(self, material_id, quantity) -> None:
        print("DATABASE> Decrease quantity of material #" + str(material_id))
        query = "UPDATE `materials` SET `quantity`=`materials`.`quantity`-" + str(
            float(quantity)) + " WHERE `materials`.`id`='" + str(material_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('costs', 'W')
    def saveCostProcessData(self, product_id, quantity, working_hours, pills, cost_date, exchange_price, unit_cost_sp,unit_cost_usd, total_cost_sp, total_cost_usd, expenses_type, material_pricing_method) -> None:
        print("DATABASE> Save manufacure process")
        query = 'INSERT INTO `costs`(`pid`, `unit_cost_sp`, `unit_cost_usd`, `total_cost_sp`, `total_cost_usd`, `date_col`, `exchange_price`, `box_per_batch`, `working_hours_standard`, `pills_standard`, `expenses_type`, `material_pricing_method`) VALUES ("' + str(
            product_id) + '","' + str(unit_cost_sp) + '","' + str(unit_cost_usd) + '","' + str(
            total_cost_sp) + '","' + str(total_cost_usd) + '","' + str(cost_date) + '","' + str(
            exchange_price) + '","' + str(quantity) + '","' + str(working_hours) + '","' + str(pills) + '","' + str(
            expenses_type) + '","' + str(material_pricing_method) + '")'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id


    @check_permission('costs', 'W')
    def saveCostProcessMaterial(self, process_id, material_id, price_sp, price_usd, standard_quantity, unit):
        print("DATABASE> Save cost process materials")
        query = "INSERT INTO `cost_materials`(`process_id`, `material`, `price_sp`, `price_usd`, `standard_quantity`, `unit`) VALUES ('" + str(
            process_id) + "','" + str(material_id) + "','" + str(price_sp) + "','" + str(price_usd) + "','" + str(
            standard_quantity) + "','" + str(unit) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('costs', 'W')
    def removeCostProcessMaterial(self, id) -> None:
        print("DATABASE> Delete cost process material id #" + str(id))
        query = 'DELETE FROM `cost_materials` WHERE `id`="' + str(id) + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('invoices', 'R')
    def fetchLastInvoiceNumber(self):
        print("DATABASE> Fetch last invoice number.")
        query = 'SELECT MAX(invoices.number) FROM invoices'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('manufacture', 'R')
    def fetchManufactureProcessesOfMaterial(self, material_id) -> list:
        print("DATABASE> Fetch all manufacture processes.")
        query = "SELECT manufacture.*, manufacture_produced_materials.material_id, manufacture_produced_materials.quantity1, manufacture_produced_materials.unit1, manufacture_produced_materials.quantity2, manufacture_produced_materials.unit2, manufacture_produced_materials.quantity3, manufacture_produced_materials.unit3, manufacture_produced_materials.working_hours, manufacture_produced_materials.batch, materials.name, units1.name AS unit1_name, units2.name AS unit2_name, units3.name AS unit3_name, currencies.name AS currency_name, accounts1.name AS account_name, accounts2.name AS mid_account_name FROM manufacture JOIN manufacture_produced_materials ON manufacture.id = manufacture_produced_materials.manufacture_id JOIN materials ON materials.id = manufacture_produced_materials.material_id LEFT JOIN units AS units1 ON units1.id = materials.unit1 LEFT JOIN units AS units2 ON units2.id = materials.unit2 LEFT JOIN units AS units3 ON units3.id = materials.unit3 JOIN currencies ON currencies.id = manufacture.currency LEFT JOIN accounts AS accounts1 ON accounts1.id = manufacture.account LEFT JOIN accounts AS accounts2 ON accounts2.id = manufacture.mid_account WHERE manufacture_produced_materials.material_id = " + str(material_id)

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('manufacture', 'R')
    def fetchManufactureProcess(self, manufacture_process_id) -> list:
        if manufacture_process_id is None:
            return None
        print("DATABASE> Fetch manufacture process.")
        query = "SELECT manufacture.*, currencies.name as currency_name FROM `manufacture` LEFT JOIN currencies ON manufacture.currency = currencies.id WHERE manufacture.id = " + str(manufacture_process_id)
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchManufactureProcessMachines(self, process_id) -> list:
        print("DATABASE> Fetch manufacture process machines")
        query = "SELECT manufacture_machines.*, machines.name as machine_name, machine_modes.name as mode_name, machine_modes.id as mode_id, manufacture_machines.duration as duration, manufacture_machines.exclusive as exclusive, manufacture_machines.exclusive_percent as exclusive_percent, machines.account as account_id, a1.name as account_name, machines.opposite_account as opposite_account_id, a2.name as opposite_account_name FROM manufacture_machines LEFT JOIN machines ON manufacture_machines.machine_id = machines.id LEFT JOIN machine_modes ON manufacture_machines.mode_id = machine_modes.id LEFT JOIN accounts a1 ON machines.account = a1.id LEFT JOIN accounts a2 ON machines.opposite_account = a2.id WHERE manufacture_machines.manufacture_id = '" + str(process_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchLastManufatureProcess(self) -> dict:
        print("DATABASE> Fetch last manufacture process")
        query = "SELECT materials.name AS material_name, `manufacture_produced_materials`.`quantity1` ,`manufacture`.* FROM manufacture JOIN manufacture_produced_materials ON manufacture.id = manufacture_produced_materials.manufacture_id JOIN materials ON manufacture_produced_materials.material_id = materials.id ORDER BY manufacture.date_col DESC LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row
    
    @check_permission('manufacture', 'R')
    def fetchMaterialLastManufatureProcess(self, material_id) -> dict:
        print(f"DATABASE> Fetch last manufacture process for material #{material_id}")
        query = "SELECT materials.name AS material_name, manufacture.date_col AS manufacture_date, manufacture_produced_materials.quantity1 AS quantity, warehouseslist.name AS warehouse_name FROM manufacture JOIN manufacture_produced_materials ON manufacture.id = manufacture_produced_materials.manufacture_id JOIN materials ON manufacture_produced_materials.material_id = materials.id JOIN warehouseslist ON manufacture.warehouse = warehouseslist.id WHERE manufacture_produced_materials.material_id = '" + str(material_id) + "' ORDER BY manufacture.date_col DESC LIMIT 1"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row
    
    @check_permission('manufacture', 'R')
    def fetchAllManufactureProcessesCount(self) -> int:
        print("DATABASE> Fetch all manufacture processes.")
        query = 'SELECT COUNT(*) FROM `manufacture`'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('manufacture', 'R')
    def fetchAllManufactureProcessesInfo(self) -> list:
        print("DATABASE> Fetch all manufacture processes")
        query = "SELECT manufacture.*, manufacture_produced_materials.quantity1 as quantity, manufacture_produced_materials.batch, manufacture_produced_materials.working_hours, manufacture_produced_materials.referential_working_hours, manufacture_produced_materials.production_date, materials.id as material_id, materials.name as material_name FROM manufacture LEFT JOIN manufacture_produced_materials ON manufacture.id = manufacture_produced_materials.manufacture_id LEFT JOIN materials ON manufacture_produced_materials.material_id = materials.id"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchManufactureProcessMaterial(self, process_id, composition_item_id) -> list:
        print("DATABASE> Fetch manufacture process material #" + str(process_id) + " material #" + str(composition_item_id))
        query = "SELECT * FROM `manufacture_materials` WHERE `manufacture_id`='" + str(process_id) + "' AND `composition_item_id`='" + str(composition_item_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('manufacture', 'W')
    def updateManufactureProcessState(self, manufacuture_process_id, state) -> None:
        print("DATABASE> Delete manufacture process #" + manufacuture_process_id)
        query = "UPDATE `manufacture` SET `state_col`='" + str(state) + "' WHERE `id`='" + str(
            manufacuture_process_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('manufacture', 'R')
    def fetchManufactureProcessProducedMaterials(self, process_id) -> list:
        print("DATABASE> Fetch produced materials for manufacture process #" + str(process_id))
        query = "SELECT manufacture_produced_materials.*, materials.code, materials.name AS material_name, units1.name AS unit1_name, units2.name AS unit2_name, units3.name AS unit3_name, warehouseslist.name AS warehouse_name FROM manufacture_produced_materials JOIN materials ON manufacture_produced_materials.material_id = materials.id LEFT JOIN units AS units1 ON units1.id = manufacture_produced_materials.unit1 LEFT JOIN units AS units2 ON units2.id = manufacture_produced_materials.unit2 LEFT JOIN units AS units3 ON units3.id = manufacture_produced_materials.unit3 LEFT JOIN warehouseslist ON warehouseslist.id = manufacture_produced_materials.warehouse WHERE manufacture_produced_materials.manufacture_id = '" + str(process_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchManufacturedProducedMaterials(self) -> list:
        print("DATABASE> Fetch manufactured produced materials")
        query = "SELECT materials.id as material_id, materials.name as material_name, manufacture_produced_materials.working_hours, manufacture_produced_materials.quantity1, manufacture_produced_materials.quantity2, manufacture_produced_materials.quantity3, manufacture_produced_materials.unit1, manufacture_produced_materials.unit2, manufacture_produced_materials.unit3 FROM manufacture_produced_materials JOIN materials ON manufacture_produced_materials.material_id = materials.id"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchManufactureProcessMaterials(self, process_id) -> list:
        print("DATABASE> Fetch manufacture process #" + str(process_id))
        query = "SELECT `manufacture_materials`.*, `materials`.`code`, `materials`.`name` AS `material_name`, `units`.`name` AS `unit_name`, `currencies`.`name` AS `currency_name`, `warehouseslist`.`name` AS `warehouse_name` FROM `manufacture_materials` JOIN `groupped_materials_composition` ON `manufacture_materials`.`composition_item_id` = `groupped_materials_composition`.`id` JOIN `materials` ON `materials`.`id` = `groupped_materials_composition`.`composition_material_id` LEFT JOIN `units` ON `manufacture_materials`.`unit` = `units`.`id` JOIN `currencies` ON `currencies`.`id` = `manufacture_materials`.`currency` LEFT JOIN `warehouseslist` ON `warehouseslist`.`id` = `manufacture_materials`.`warehouse_id` WHERE `manufacture_id` ='" + str(
            process_id) + "' ORDER BY CASE WHEN `row_type` = 'parent' THEN 0 ELSE 1 END"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('costs', 'R')
    def fetchCostProcess(self, id) -> list:
        print("DATABASE> Fetch cost processes #" + str(id))
        query = 'SELECT `costs`.*, `products`.`name`, `products`.`name_en`, `cost_materials`.*, `materials`.`name`,`materials`.`name_en`,`materials`.`code` from `costs` JOIN `products` on `costs`.`pid`=`products`.`id` JOIN `cost_materials` ON `costs`.`id` = `cost_materials`.`process_id` JOIN `materials` ON `cost_materials`.`material`=`materials`.`id` WHERE `costs`.`id`="' + str(
            id) + '"'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('costs', 'R')
    def fetchAllCostProcessesCount(self) -> int:
        print("DATABASE> Fetch all cost processes.")
        query = 'SELECT COUNT(*) FROM `costs`'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('costs', 'R')
    def fetchCostProcessMaterial(self, process_id, material_id) -> list:
        print("DATABASE> Fetch cost process #" + str(process_id) + " material #" + str(material_id))
        query = 'SELECT * FROM `cost_materials` WHERE `process_id`="' + str(process_id) + '" and `material`="' + str(
            material_id) + '"'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('costs', 'W')
    def updateCostProcessData(self, id, product_id, quantity, working_hours, pills, cost_date, exchange_price,unit_cost_sp,unit_cost_usd, total_cost_sp, total_cost_usd, expenses_type, material_pricing_method) -> None:

        print("DATABASE> Update cost process data")
        query = "UPDATE `costs` SET `pid`='" + str(product_id) + "',`unit_cost_sp`='" + str(
            unit_cost_sp) + "',`unit_cost_usd`='" + str(unit_cost_usd) + "',`total_cost_sp`='" + str(
            total_cost_sp) + "',`total_cost_usd`='" + str(total_cost_usd) + "',`date_col`='" + str(
            cost_date) + "',`exchange_price`='" + str(exchange_price) + "',`box_per_batch`='" + str(
            quantity) + "',`working_hours_standard`='" + str(working_hours) + "',`pills_standard`='" + str(
            pills) + "',`expenses_type`='" + str(expenses_type) + "',`material_pricing_method`='" + str(
            material_pricing_method) + "' WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('manufacture', 'R')
    def fetchProductManufactureAverageUntilDate(self, id, date) -> list:
        print("DATABASE> Fetch " + str(id) + " manufacture vaerage price until #" + str(date))
        query = 'SELECT AVG(`unit_cost_sp`) as `unit_cost_sp_avg`, AVG(`unit_cost_usd`) as `unit_cost_usd_avg` FROM `manufacture` WHERE `manufacture`.`pid` ="' + str(
            id) + '" AND `manufacture`.`date_col`<=DATE("' + str(date) + '")'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('costs', 'W')
    def removeCostProcess(self, cost_process_id) -> None:
        print("DATABASE> Delete cost process #" + cost_process_id)
        query = 'DELETE FROM costs WHERE id ="' + cost_process_id + '"'
        # print(query)
        self.cursor.execute(query)
        query = 'DELETE FROM cost_materials WHERE process_id ="' + cost_process_id + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        print("Deleted cost process #" + cost_process_id)

    @check_permission('manufacture', 'R')
    def fetchQuantityOfManufacturedMaterials(self, unit, year, month='', commit=True) -> list:  # fetchQuantityInYear
        print("DATABASE> Fetch pills count in year " + str(year))
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT SUM(CASE WHEN manufacture_produced_materials.unit1 = " + str(unit) + " THEN manufacture_produced_materials.quantity1 WHEN manufacture_produced_materials.unit2 = " + str(
                unit) + " THEN manufacture_produced_materials.quantity2 WHEN manufacture_produced_materials.unit3 = " + str(
                unit) + " THEN manufacture_produced_materials.quantity3 ELSE 0 END) AS sum_result FROM `manufacture_produced_materials` " + \
                "INNER JOIN `manufacture` ON manufacture.id = manufacture_produced_materials.manufacture_id " + \
                "WHERE YEAR(manufacture.date_col)='" + str(year) + "' AND MONTH(manufacture.date_col)=COALESCE(NULLIF('" + str(month) + "',''),MONTH(manufacture.date_col))"

        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = "SELECT SUM(CASE WHEN manufacture_produced_materials.unit1 = " + str(unit) + " THEN manufacture_produced_materials.quantity1 WHEN manufacture_produced_materials.unit2 = " + str(unit) + " THEN manufacture_produced_materials.quantity2 WHEN manufacture_produced_materials.unit3 = " + str(unit) + " THEN manufacture_produced_materials.quantity3 ELSE 0 END) AS sum_result FROM `manufacture_produced_materials` INNER JOIN `manufacture` ON manufacture.id = manufacture_produced_materials.manufacture_id WHERE strftime('%Y', manufacture.date_col) = '" + str(year) + "' AND strftime('%m', manufacture.date_col)=COALESCE(NULLIF('" + str(month) + "',''),strftime('%m', manufacture.date_col))"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchWorkHoursOfManufacturedMaterials(self, year, month='', commit=True) -> list:
        print("Fetch hours count in year " + str(year))
        
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            # MySQL version using YEAR() and MONTH()
            year_condition = f"YEAR(`date_col`) = '{year}'"
            month_condition = f"MONTH(`date_col`) = COALESCE(NULLIF('{month}',''), MONTH(`date_col`))"
        else:
            # SQLite version using strftime
            year_condition = f"strftime('%Y', date_col) = '{year}'"
            month_condition = f"strftime('%m', date_col) = COALESCE(NULLIF('{month}',''), strftime('%m', date_col))"

        query = f"""
            SELECT SUM(`working_hours`) AS sum_result 
            FROM `manufacture`
            WHERE {year_condition} AND {month_condition}
        """

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'R')
    def fetchHoursInMonth(self, year, month) -> list:
        print("Fetch hours count in year " + year + " month " + month)

        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = 'SELECT SUM(working_hours) FROM manufacture WHERE DATE_FORMAT(date_col,"%Y")="' + str(
                year) + '" AND DATE_FORMAT(date_col,"%c")="' + str(month) + '"'
        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = 'SELECT SUM(working_hours) FROM manufacture WHERE strftime("%Y",date_col)="' + str(
                year) + '" AND strftime("%m",date_col)+0="' + str(month) + '"'

        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        try:
            result = rows[0][0]
            if str(result) == "None":
                result = 0
        except:
            result = 0
        return result

    @check_permission('manufacture', 'R')
    def fetchManufacturedYears(self) -> list:
        print("DATABASE> Fetch manufactured years")

        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            # MySQL version using YEAR()
            query = "SELECT DISTINCT YEAR(date_col) FROM manufacture"
        else:
            # SQLite version using strftime
            query = 'SELECT DISTINCT strftime("%Y",date) FROM manufacture'

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('manufacture', 'W')
    def addPlanItem(self, id ,priority) -> None:
        print("DATABASE> Add plan item")
        query = "INSERT INTO plans (material,priority) VALUES ('" + str(id) + "','" + str(priority) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        print("New plan item added")


    @check_permission('manufacture', 'R')
    def fetchLastSimplePlanPriority(self) -> int:
        print("DATABASE> Fetch last simple plan priority")
        query = "SELECT MAX(priority) FROM plans"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('plans', 'R')
    def fetchSimplePlanItems(self) -> list:
        print("DATABASE> Fetch simple plan items")
        query = "SELECT plans.*, materials.name, materials.code FROM plans join materials on plans.material=materials.id ORDER BY plans.priority"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('plans', 'R')
    def fetchSimplePlanPriority(self, plan_item_id) -> int:
        print("DATABASE> Fetch simple plan priority")
        query = "SELECT priority FROM plans WHERE id='" + str(plan_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('plans', 'W')
    def updateSimplaPlanItemPriority(self, plan_item_id, priority) -> None:
        print("DATABASE> Update simple plan item #" + str(plan_item_id))
        query = 'UPDATE plans SET `priority`="' + str(priority) + '" WHERE `id`="' + str(plan_item_id) + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('plans', 'W')
    def removeSimplePlanItem(self, plan_item_id) -> None:
        print("DATABASE> Delete simple plan item#" + str(plan_item_id))
        query = "DELETE FROM plans WHERE id='" + str(plan_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('plans', 'W')
    def clearSimplePlanItems(self) -> None:
        print("DATABASE> Delete all simple plan items")
        query = "DELETE FROM plans"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('plans', 'W')
    def addPlanPercentItem(self, id, priority, percent) -> None:
        print("DATABASE> Add plan percent item")
        query = "INSERT INTO percent_plans (material,priority,percent) VALUES ('" + str(id) + "','" + str(
            priority) + "','" + str(percent) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('plans', 'R')
    def fetchLastPercentPlanPriority(self) -> int:
        print("DATABASE> Fetch last percent plan priority")
        query = "SELECT MAX(priority) FROM percent_plans"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('plans', 'R')
    def fetchPlanPercentItems(self) -> list:
        print("DATABASE> Fetch plan percent items")
        query = "SELECT percent_plans.*, materials.name, materials.code FROM percent_plans join materials on percent_plans.material=materials.id ORDER BY percent_plans.priority"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('plans', 'R')
    def fetchPlanPercentPriority(self, plan_item_id) -> int:
        print("DATABASE> Fetch plan percent priority")
        query = "SELECT priority FROM percent_plans WHERE id='" + str(plan_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]


    @check_permission('plans', 'R')
    def fetchPlanPercentPercent(self, plan_item_id) -> int:
        print("DATABASE> Fetch plan percent percent")
        query = "SELECT percent FROM percent_plans WHERE id='" + str(plan_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]

    @check_permission('plans', 'W')
    def updatePlanPercentItemPriority(self, plan_item_id, priority) -> None:
        print("DATABASE> Update plan percent item #" + str(plan_item_id))
        query = 'UPDATE percent_plans SET `priority`="' + str(priority) + '" WHERE `id`="' + str(plan_item_id) + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('plans', 'W')
    def updatePlanPercentItemPercent(self, plan_item_id, percent) -> None:
        print("DATABASE> Update plan percent item #" + str(plan_item_id))
        query = 'UPDATE percent_plans SET `percent`="' + str(percent) + '" WHERE `id`="' + str(plan_item_id) + '"'
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('plans', 'W')
    def removePlanPercentItem(self, plan_item_id) -> None:
        print("DATABASE> Delete plan percent item #" + str(plan_item_id))
        query = "DELETE FROM percent_plans WHERE id='" + str(plan_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('plans', 'W')
    def clearPlanPercentItems(self) -> None:
        print("DATABASE> Delete all plan percent items")
        query = "DELETE FROM percent_plans"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('aggregators', 'R')
    def fetchAggregatorItems(self) -> list:
        print("DATABASE> Fetch aggregatore items")
        query = "SELECT aggregator.*, materials.name, materials.code , materials.id AS material_id FROM aggregator JOIN materials on aggregator.material=materials.id"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('aggregators', 'R')
    def fetchMaterialAggregator(self, material_id) -> list:
        print("DATABASE> Fetch material aggregator")
        query = "SELECT aggregator.*, materials.name, materials.current_quantity AS quantity, materials.code , materials.id AS material_id FROM aggregator JOIN materials ON aggregator.material=materials.id WHERE aggregator.material='" + str(material_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('aggregators', 'W')
    def addAggregatorItem(self, id, target) -> None:
        print("DATABASE> Add aggregator item")
        query = "INSERT INTO aggregator (material, ammount) VALUES ('" + str(id) + "','" + str(target) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        print("New aggregator item added.")

    @check_permission('aggregators', 'W')
    def removeAggregatorItem(self, aggregator_item_id) -> None:
        print("DATABASE> Delete aggregator item #" + str(aggregator_item_id))
        query = "DELETE FROM aggregator WHERE id='" + str(aggregator_item_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('aggregators', 'W')
    def clearAggregatorItems(self) -> None:
        print("DATABASE> Delete all aggregator items")
        query = "DELETE FROM aggregator"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ################################################################
    ######################### LAB ##################################
    ################################################################

    def addLabPullOut(self, element_id, src, quantity, unit, date):
        print("DATABASE> Add lab pull out item")
        query = "INSERT INTO `lab`( `element`, `quantity`, `unit`, `src`, `date_col`) VALUES ('" + str(
            element_id) + "','" + str(quantity) + "','" + str(unit) + "','" + str(src) + "','" + str(date) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchLabPullOuts(self):
        print("DATABASE> Fetch lab pullouts")
        query = "SELECT * FROM (SELECT `lab`.*, `materials`.`name`, `materials`.`name_en`, `materials`.`code` FROM `lab` JOIN `materials` ON `lab`.`element`=`materials`.`id` WHERE `lab`.`src`='raws') as `raws` UNION SELECT `lab`.*, `products`.`name`, `products`.`name_en`, `products`.`code` FROM `lab` JOIN `products` ON `lab`.`element`=`products`.`id` WHERE `lab`.`src`='products' ORDER By `date_col` DESC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeLabPullOut(self, id):
        print("DATABASE> Remove lab pullout #" + str(id))
        query = "DELETE FROM `lab` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ################################################################
    ######################### RESEARCH ##################################
    ################################################################
    def addResearchPullOut(self, element_id, src, quantity, unit, date):
        print("DATABASE> Add research pull out item")
        query = "INSERT INTO `research`( `element`, `quantity`, `unit`, `src`, `date_col`) VALUES ('" + str(
            element_id) + "','" + str(quantity) + "','" + str(unit) + "','" + str(src) + "','" + str(date) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchResearchPullOuts(self):
        print("DATABASE> Fetch research pullouts")
        query = "SELECT * FROM (SELECT `research`.*, `materials`.`name`, `materials`.`name_en`, `materials`.`code` FROM `research` JOIN `materials` ON `research`.`element`=`materials`.`id` WHERE `research`.`src`='raws') as `raws` UNION SELECT `research`.*, `products`.`name`, `products`.`name_en`, `products`.`code` FROM `research` JOIN `products` ON `research`.`element`=`products`.`id` WHERE `research`.`src`='products' ORDER By `date_col` DESC"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeResearchPullOut(self, id):
        print("DATABASE> Remove research pullout #" + str(id))
        query = "DELETE FROM `research` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    #######################################################
    ################# OUT INVOICES OPERATIONS ###########
    #######################################################

    def addOutInvoice(self, number, type, client, direct_client, payment, statement, paid, total_discount, currency,
                      exchange, date):
        print("DATABASE> Add out invoice")
        query = "INSERT INTO `invoices_out`(`number`, `type_col`, `client`, `direct_client`, `payment`, `statement_col`, `paid`, `total_discount`, `currency`, `exchange`, `date_col`) VALUES ('" + str(
            number) + "','" + str(type) + "','" + str(client) + "','" + str(direct_client) + "','" + str(
            payment) + "','" + str(statement) + "','" + str(paid) + "','" + str(total_discount) + "','" + str(
            currency) + "','" + str(exchange) + "','" + str(date) + "')"
        print(query)
        self.cursor.execute(query)
        last_id = self.cursor.lastrowid
        self.sqlconnector.conn.commit()
        return last_id

    def addOutInvoiceItem(self, new_out_invoice_id, product_id, quantity, price_sp, price_usd, discount,price_sp_after_discount, price_usd_after_discount):
        print("DATABASE> Add out invoice item")
        query = "INSERT INTO `invoices_out_items`(`invoice`, `product`, `quantity`, `price_sp`, `price_usd`, `discount`, `price_sp_after_discount`, `price_usd_after_discount`) VALUES ('" + str(
            new_out_invoice_id) + "','" + str(product_id) + "','" + str(quantity) + "','" + str(price_sp) + "','" + str(
            price_usd) + "','" + str(discount) + "','" + str(price_sp_after_discount) + "','" + str(
            price_usd_after_discount) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def saveOutInvoicePaid(self, invoice_id, paid):
        print("DATABASE> Update ready out invoice paid")
        query = "UPDATE `invoices_out` SET `paid`='" + str(paid) + "' WHERE `id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'R')
    def getRawMaterialsMovements(self, material_id, from_date, to_date) -> list:
        print("DATABASE> Fetch raw materials movements")
        query = "SELECT `materials`.`id` as `material_id`,`materials`.`code` as `material_code`,`materials`.`name` as `material_name`,'invoice' as `type_col`, `invoices`.`id` as `id`,'' as `src`,'' as `product`,'' as `product_en`,'' as `resulted_boxes`,'' as `batch`,`invoices`.`date_col` as `date_col`FROM`materials` JOIN `invoices` ON `materials`.`id`=`invoices`.`material_id`WHERE `materials`.`id`='" + str(
            material_id) + "' AND DATE(`invoices`.`date_col`)>=DATE('" + str(
            from_date) + "') and DATE(`invoices`.`date_col`)<=DATE('" + str(
            to_date) + "') UNION SELECT `materials`.`id` as `material_id`,`materials`.`code` as `material_code`,`materials`.`name` as `material_name`,'manufacture' as `type_col`,`manufacture`.`id` as `id`,`manufacture_materials`.`required_quantity` as `quantity`,`manufacture_materials`.`unit` as `unit`,'' as `src`,`products`.`name` as `product`,`products`.`name_en` as `product`,`manufacture`.`quantity` as `resulted_boxes`,`manufacture`.`batch` as `batch`,`manufacture`.`date_col` as `date_col` FROM`materials` JOIN `manufacture_materials` ON `materials`.`id`=`manufacture_materials`.`material` JOIN `manufacture` ON `manufacture_materials`.`process_id`=`manufacture`.`id` JOIN `products` ON `manufacture`.`pid` = `products`.`id`WHERE `materials`.`id`='" + str(
            material_id) + "' AND DATE(`manufacture`.`date_col`)>=DATE('" + str(
            from_date) + "') and DATE(`manufacture`.`date_col`)<=DATE('" + str(
            to_date) + "') ORDER BY `date_col` DESC"
        ############### Uncomment and copy ##################
        # (SELECT
        #
        #  `materials`.`id` as `material_id`,
        #  `materials`.`code` as `material_code`,
        #  `materials`.`name` as `material_name`,
        #  `materials`.`name_en` as `material_name_en`,
        #
        #  "invoice" as `type_col`,
        #  `invoices`.`id` as `id`,
        #  `invoices`.`quantity` as `quantity`,
        #  `invoices`.`unit` as `unit`,
        #  "" as `src`,
        #  "" as `product`,
        #  "" as `product_en`,
        #  "" as `resulted_boxes`,
        #  "" as `batch`,
        #  `invoices`.`date_col` as `date_col`
        #
        #  FROM
        #  `materials` JOIN `invoices` ON `materials`.`id`=`invoices`.`material_id`
        #  WHERE `materials`.`id`='matid' AND
        #  DATE(`invoices`.`date_col`) >= DATE("2021-01-01") and DATE(`invoices`.
        # `date_col`) <= DATE("2022-1-1")
        # )
        #
        #
        # UNION
        #
        # (SELECT
        #  `materials`.`id` as `material_id`,
        #  `materials`.`code` as `material_code`,
        #  `materials`.`name` as `material_name`,
        #  `materials`.`name_en` as `material_name_en`,
        #
        #  "manufacture" as `type_col`,
        #  `manufacture`.`id` as `id`,
        #  `manufacture_materials`.`required_quantity` as `quantity`,
        #  `manufacture_materials`.`unit` as `unit`,
        #  "" as `src`,
        #  `products`.`name` as `product`,
        #  `products`.`name_en` as `product`,
        #  `manufacture`.`quantity` as `resulted_boxes`,
        #  `manufacture`.`batch` as `batch`,
        #  `manufacture`.`date_col` as `date_col`
        #
        #  FROM
        #  `materials` JOIN `manufacture_materials` ON `materials`.`id`=`manufacture_materials`.`material` JOIN `manufacture` ON `manufacture_materials`.`process_id`=`manufacture`.`id` JOIN `products` ON `manufacture`.`pid` = `products`.`id`
        #  WHERE `materials`.`id`='matid' AND
        #  DATE(`manufacture`.`date_col`) >= DATE("2021-01-01") and DATE(`manufacture`.
        # `date_col`) <= DATE("2022-1-1")
        # )
        #
        #
        #
        #
        # UNION
        #
        # (SELECT
        #  `materials`.`id` as `material_id`,
        #  `materials`.`code` as `material_code`,
        #  `materials`.`name` as `material_name`,
        #  `materials`.`name_en` as `material_name_en`,
        #
        #  "lab" as `type_col`,
        #  `lab`.`id` as `id`,
        #  `lab`.`quantity` as `quantity`,
        #  `lab`.`unit` as `unit`,
        #  `lab`.`src` as `src`,
        #  "" as `product`,
        #  "" as `product`,
        #  "" as `resulted_boxes`,
        #  "" as `batch`,
        #  `lab`.`date_col` as `date_col`
        #
        #  FROM
        #  `materials` JOIN `lab` ON `materials`.`id`=`lab`.`element`
        #  WHERE `materials`.`id`='matid' AND
        #  DATE(`lab`.`date_col`) >= DATE("2021-01-01") and DATE(`lab`.
        # `date_col`) <= DATE("2022-1-1")
        # )
        #
        # UNION
        #
        # (SELECT
        #  `materials`.`id` as `material_id`,
        #  `materials`.`code` as `material_code`,
        #  `materials`.`name` as `material_name`,
        #  `materials`.`name_en` as `material_name_en`,
        #
        #  "research" as `type_col`,
        #  `research`.`id` as `id`,
        #  `research`.`quantity` as `quantity`,
        #  `research`.`unit` as `unit`,
        #  `research`.`src` as `src`,
        #  "" as `product`,
        #  "" as `product`,
        #  "" as `resulted_boxes`,
        #  "" as `batch`,
        #  `research`.`date_col` as `date_col`
        #
        #  FROM
        #  `materials` JOIN `research` ON `materials`.`id`=`research`.`element`
        #  WHERE `materials`.`id`='matid' AND
        #  DATE(`research`.`date_col`) >= DATE("2021-01-01") and DATE(`research`.
        # `date_col`) <= DATE("2022-1-1")
        # )
        #
        # ORDER BY `date_col` DESC
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('sales', 'R')
    def fetchSalesInvoices(self, material_id, from_date, to_date, invoice_sell_id) -> list:
        print("DATABASE> Fetch products sales")
        query = """SELECT `invoices`.`id`, `invoices`.`number`, `invoices`.`type_col`, `invoices`.`paid`, `invoices`.`date_col`, `invoice_items`.`quantity1`, `invoice_items`.`unit1_id`, `invoice_items`.`discount`, `invoice_items`.`addition`, `invoice_items`.`discount_percent`, `invoice_items`.`addition_percent`, `invoice_items`.`unit_price` as `price`, `invoice_items`.`equilivance_price` as `currency`, `clients`.`name` as `client_name`, `currencies`.`name` as `currency_name`, `units`.`name` as `unit1` FROM `invoices` JOIN `invoice_items` ON `invoices`.`id` = `invoice_items`.`invoice_id` LEFT OUTER JOIN `clients` ON `invoices`.`client` = `clients`.`id` LEFT OUTER JOIN `currencies` ON `invoice_items`.`currency_id` = `currencies`.`id` LEFT OUTER JOIN `units` ON `invoice_items`.`unit1_id` = `units`.`id` WHERE `invoice_items`.`material_id` = '{}' AND DATE(`invoices`.`date_col`) >= '{}' AND DATE(`invoices`.`date_col`) <= '{}' AND `invoices`.`type_col` = '{}'""".format(material_id, from_date, to_date, invoice_sell_id)

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    ############# Ready out invoices operations ############
    def fetchAllReadyOutInvoices(self):
        print("DATABASE> Fetch  all ready out invoices grouped.")
        query = 'SELECT `invoices_out`.`id`,`invoices_out`.`number`,`invoices_out`.`payment`,`invoices_out`.`date_col`,`clients`.`name`,SUM(`invoices_out_items`.`price_sp_after_discount`) as `total_sp`,SUM(`invoices_out_items`.`price_usd_after_discount`) as `total_usd` FROM `invoices_out` JOIN `clients` ON `invoices_out`.`client`=`clients`.`id` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice`  WHERE `invoices_out`.`type_col` = "ready" GROUP BY `invoices_out`.`id`'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchReadyOutInvoice(self, invoice_id):
        print("DATABASE> Fetch ready out invoice #" + invoice_id)
        query = "SELECT `invoices_out`.`currency`, `invoices_out`.`date_col`, `invoices_out`.`number`, `invoices_out`.`paid`, `invoices_out`.`payment`, `invoices_out`.`statement_col`, `invoices_out`.`total_discount`, `invoices_out_items`.`discount`, `invoices_out_items`.`price_sp`, `invoices_out_items`.`price_usd`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`,`invoices_out_items`.`quantity`, `products`.`name` as `product_name`, `clients`.`name` as `client_name`, `invoices_out`.`exchange`, `products`.`id` as `product_id` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice` JOIN `products` ON `invoices_out_items`.`product`=`products`.`id` JOIN `clients` ON `invoices_out`.`client`=`clients`.`id` WHERE `invoices_out`.`id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeReadyOutInvoice(self, invoice_id):
        print("DATABASE> Delete ready out invoice #" + str(invoice_id))
        query = "DELETE FROM `invoices_out` WHERE id='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `invoices_out_items` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `payments` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############# Direct out invoices operations ############
    def fetchAllDirectOutInvoices(self):
        print("DATABASE> Fetch  all direct out invoices grouped.")
        query = 'SELECT `invoices_out`.`id`,`invoices_out`.`number`,`invoices_out`.`payment`,`invoices_out`.`date_col`,`invoices_out`.`direct_client`,SUM(`invoices_out_items`.`price_sp_after_discount`) as `total_sp`,SUM(`invoices_out_items`.`price_usd_after_discount`) as `total_usd` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice`  WHERE `invoices_out`.`type_col` = "direct" GROUP BY `invoices_out`.`id`'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchDirectOutInvoice(self, invoice_id):
        print("DATABASE> Fetch  direct out invoice #" + invoice_id)
        query = "SELECT `invoices_out`.`currency`, `invoices_out`.`date_col`, `invoices_out`.`number`, `invoices_out`.`paid`, `invoices_out`.`payment`, `invoices_out`.`statement_col`, `invoices_out`.`total_discount`, `invoices_out_items`.`discount`, `invoices_out_items`.`price_sp`, `invoices_out_items`.`price_usd`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`,`invoices_out_items`.`quantity`, `products`.`name` as `product_name`, `invoices_out`.`direct_client` as `client_name`, `invoices_out`.`exchange`, `products`.`id` as `product_id` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice` JOIN `products` ON `invoices_out_items`.`product`=`products`.`id` WHERE `invoices_out`.`id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeDirectOutInvoice(self, invoice_id):
        print("DATABASE> Delete direct out invoice #" + str(invoice_id))
        query = "DELETE FROM `invoices_out` WHERE id='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `invoices_out_items` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `payments` WHERE invoice='" + str(invoice_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############# Samples out invoices operations ############
    def fetchAllSamplesOutInvoices(self):
        print("DATABASE> Fetch  all sample out invoices grouped.")
        query = 'SELECT `invoices_out`.`id`,`invoices_out`.`number`,`invoices_out`.`payment`,`invoices_out`.`date_col`,`clients`.`name`,SUM(`invoices_out_items`.`price_sp_after_discount`) as `total_sp`,SUM(`invoices_out_items`.`price_usd_after_discount`) as `total_usd` FROM `invoices_out` JOIN `clients` ON `invoices_out`.`client`=`clients`.`id` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice`  WHERE `invoices_out`.`type_col` = "samples" GROUP BY `invoices_out`.`id`'
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchSamplesOutInvoice(self, invoice_id):
        print("DATABASE> Fetch  sample out invoice #" + invoice_id)
        query = "SELECT `invoices_out`.`currency`, `invoices_out`.`date_col`, `invoices_out`.`number`, `invoices_out`.`paid`, `invoices_out`.`payment`, `invoices_out`.`statement_col`, `invoices_out`.`total_discount`, `invoices_out_items`.`discount`, `invoices_out_items`.`price_sp`, `invoices_out_items`.`price_usd`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`,`invoices_out_items`.`quantity`, `products`.`name` as `product_name`, `invoices_out`.`direct_client` as `client_name`, `invoices_out`.`exchange`, `products`.`id` as `product_id` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice` JOIN `products` ON `invoices_out_items`.`product`=`products`.`id` WHERE `invoices_out`.`id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeSamplesOutInvoice(self, invoice_id):
        print("DATABASE> Delete sample out invoice #" + str(invoice_id))
        query = "DELETE FROM `invoices_out` WHERE id='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `invoices_out_items` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `payments` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############# Gift out invoices operations ############
    def fetchAllGiftsOutInvoices(self):
        print("DATABASE> Fetch  all gifts out invoices grouped.")
        query = 'SELECT `invoices_out`.`id`,`invoices_out`.`number`,`invoices_out`.`payment`,`invoices_out`.`date_col`,`clients`.`name`,SUM(`invoices_out_items`.`price_sp_after_discount`) as `total_sp`,SUM(`invoices_out_items`.`price_usd_after_discount`) as `total_usd` FROM `invoices_out` JOIN `clients` ON `invoices_out`.`client` = `clients`.`id` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice`  WHERE `invoices_out`.`type_col` = "gifts" GROUP BY `invoices_out`.`id`'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchGiftsOutInvoice(self, invoice_id):
        print("DATABASE> Fetch  gifts out invoice #" + invoice_id)
        query = "SELECT `invoices_out`.`currency`, `invoices_out`.`date_col`, `invoices_out`.`number`, `invoices_out`.`paid`, `invoices_out`.`payment`, `invoices_out`.`statement_col`, `invoices_out`.`total_discount`, `invoices_out_items`.`discount`, `invoices_out_items`.`price_sp`, `invoices_out_items`.`price_usd`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`,`invoices_out_items`.`quantity`, `products`.`name` as `product_name`, `invoices_out`.`direct_client` as `client_name`, `invoices_out`.`exchange`, `products`.`id` as `product_id` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice` JOIN `products` ON `invoices_out_items`.`product`=`products`.`id` WHERE `invoices_out`.`id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removeGiftsOutInvoice(self, invoice_id):
        print("DATABASE> Delete gifts out invoice #" + str(invoice_id))
        query = "DELETE FROM `invoices_out` WHERE id='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `invoices_out_items` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `payments` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############# Return out invoices operations ############
    def fetchAllReturnOutInvoices(self):
        print("DATABASE> Fetch  all return out invoices grouped.")
        query = 'SELECT `invoices_out`.`id`,`invoices_out`.`number`,`invoices_out`.`payment`,`invoices_out`.`date_col`,`clients`.`name`,SUM(`invoices_out_items`.`price_sp_after_discount`) as `total_sp`,SUM(`invoices_out_items`.`price_usd_after_discount`) as `total_usd` FROM `invoices_out` JOIN `clients` ON `invoices_out`.`client`=`clients`.`id` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice`  WHERE `invoices_out`.`type_col` = "returns" GROUP BY `invoices_out`.`id`'
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchReturnsOutInvoice(self, invoice_id):
        print("DATABASE> Fetch return out invoice #" + invoice_id)
        query = "SELECT `invoices_out`.`currency`, `invoices_out`.`date_col`, `invoices_out`.`number`, `invoices_out`.`paid`, `invoices_out`.`payment`, `invoices_out`.`statement_col`, `invoices_out`.`total_discount`, `invoices_out_items`.`discount`, `invoices_out_items`.`price_sp`, `invoices_out_items`.`price_usd`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`,`invoices_out_items`.`quantity`, `products`.`name` as `product_name`, `invoices_out`.`direct_client` as `client_name`, `invoices_out`.`exchange`, `products`.`id` as `product_id` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id`=`invoices_out_items`.`invoice` JOIN `products` ON `invoices_out_items`.`product`=`products`.`id` WHERE `invoices_out`.`id`='" + invoice_id + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows
    def removeReturnsOutInvoice(self, invoice_id):
        print("DATABASE> Delete return out invoice #" + str(invoice_id))
        query = "DELETE FROM `invoices_out` WHERE id='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `invoices_out_items` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        query = "DELETE FROM `payments` WHERE invoice='" + str(invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############ General out invoices operations ############
    def fetchOutInvoice(self, invoice_id):
        print("DATABASE> Fetch out invoice #" + str(invoice_id))
        query = "SELECT `invoices_out`.`id` as `invoice_id`, `invoices_out`.`number`, `invoices_out`.`direct_client`, `invoices_out`.`statement_col`, `invoices_out`.`currency`, `invoices_out`.`exchange`, `invoices_out`.`date_col`, `invoices_out_items`.`id` as `item_id`, `invoices_out_items`.`price_sp_after_discount`, `invoices_out_items`.`price_usd_after_discount`, `clients`.`name` as `client` FROM `invoices_out` JOIN `invoices_out_items` ON `invoices_out`.`id` = `invoices_out_items`.`invoice` LEFT OUTER JOIN `clients` ON `invoices_out`.`client` = `clients`.`id` WHERE `invoices_out`.`id`='" + str(
            invoice_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def addInvoiceOutPayment(self, invoice, sp, usd, date):
        print("DATABASE> Add out invoice payment")
        query = "INSERT INTO `payments`(`invoice`, `payment_sp`, `payment_usd`, `date_col`) VALUES ('" + str(
            invoice) + "','" + str(sp) + "','" + str(usd) + "','" + str(date) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        print("Out invoice payment added")

    def removeInvoiceOutPayment(self, payment_id):
        print("DATABASE> Remove out invoice payment")
        query = "DELETE FROM `payments` WHERE `id`='" + str(payment_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchOutInvoicePayments(self, invoice_id):
        print("DATABASE> Fetch  out invoice #" + str(invoice_id))
        query = "SELECT * FROM `payments` WHERE `invoice`='" + str(invoice_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    ########################################################################
    ######################### Prepayments ##################################
    ########################################################################

    def addPayment(self, client_id, invoice_id, exchange_id, payment_currency_id, invoice_currency_id, notes,
                   payment, equilivance, date, add_journal_entry=False, journal_entry_account=None, journal_entry_opposite_account=None, journal_statement=''):
        print("DATABASE> Add prepayment")
        query = "INSERT INTO `payments`(`invoice_id`, `client_id`, `ammount`, `currency_id`, `exchange_id`, `equilivance`, `date_col`, `notes`) VALUES (NULLIF('" + str(
            invoice_id) + "', ''), '" + str(client_id) + "', '" + str(payment) + "', '" + str(
            payment_currency_id) + "', NULLIF('" + str(exchange_id) + "', ''), '" + str(equilivance) + "', '" + str(
            date) + "', NULLIF('" + str(notes) + "', ''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def removePayment(self, id):
        print("DATABASE> Remove prepayment")
        query = "DELETE FROM `payments` WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchClientPayments(self, client_id, include_extra_payments=False):
        print("DATABASE> Fetch payments from client: " + str(client_id))

        client_account_id = None
        client_extra_account_id = None
        try:
            client_data = self.fetchClient(client_id)
            client_account_id = client_data['client_account_id']
            client_extra_account_id = client_data['extra_account_id']
        except:
            pass

        client_creditor_payments = self.fetchJournalEntryItems(account=client_account_id, origin_type='invoice_payment')
        client_debtor_payments = self.fetchJournalEntryItems(opposite_account=client_account_id, origin_type='invoice_payment')
        client_extra_creditor_payments = self.fetchJournalEntryItems(account=client_extra_account_id, origin_type='invoice_payment')
        client_extra_debtor_payments = self.fetchJournalEntryItems(opposite_account=client_extra_account_id, origin_type='invoice_payment')

        client_payments = client_creditor_payments + client_debtor_payments + client_extra_creditor_payments + client_extra_debtor_payments

        if include_extra_payments:
            client_payments.extend(self.fetchJournalEntryItems(account=client_extra_account_id, origin_type='extra_payment'))
            client_payments.extend(self.fetchJournalEntryItems(opposite_account=client_extra_account_id, origin_type='extra_payment'))

        return client_payments

    @check_permission('accounts', 'R')
    def fetchAccountValue(self, account_id, currency_id, date='', unify_currency=False) -> float:
        print("DATABASE> Fetch account value")

        # Account value is the
        # SUM
        # (debtor entries values where account is the provided account
        # and creditor entries values where the opposite account is the provided account)
        # MINUS
        # SUM
        # (debtor entries values where the opposite account is the provided account
        # and creditor entries values where the account is the provided account)

        account_value = 0

        debtor_account_entries = self.fetchJournalEntryItems(account=account_id, type='debtor')
        debtor_account_entries_value = 0
        for entry in debtor_account_entries:
            if entry['currency'] == currency_id:
                debtor_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        debtor_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        creditor_opposite_account_entries = self.fetchJournalEntryItems(opposite_account=account_id, type='creditor')
        creditor_opposite_account_entries_value = 0
        for entry in creditor_opposite_account_entries:
            if entry['currency'] == currency_id:
                creditor_opposite_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        creditor_opposite_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        debtor_opposite_account_entries = self.fetchJournalEntryItems(opposite_account=account_id, type='debtor')
        debtor_opposite_account_entries_value = 0
        for entry in debtor_opposite_account_entries:
            if entry['currency'] == currency_id:
                debtor_opposite_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        debtor_opposite_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        creditor_account_entries = self.fetchJournalEntryItems(account=account_id, type='creditor')
        creditor_account_entries_value = 0
        for entry in creditor_account_entries:
            if entry['currency'] == currency_id:
                creditor_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        creditor_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        account_value = (debtor_account_entries_value + creditor_opposite_account_entries_value) - (creditor_account_entries_value + debtor_opposite_account_entries_value)

        # If account has children accounts, we need to fetch their values and add them to the account value
        children_accounts = self.fetchChildAccounts(parent_id=account_id)
        for child_account in children_accounts:
            child_account_value = self.fetchAccountValue(child_account['id'], currency_id, date, unify_currency)
            account_value += child_account_value

        return account_value

    @check_permission('accounts', 'R')
    def fetchAccountSingleValue(self, account_id, currency_id, date='', unify_currency=False) -> float:
        print("DATABASE> Fetch account single value")

        # Account value is the
        # SUM
        # (debtor entries values where account is the provided account
        # and creditor entries values where the opposite account is the provided account)
        # MINUS
        # SUM
        # (debtor entries values where the opposite account is the provided account
        # and creditor entries values where the account is the provided account)

        account_value = 0

        debtor_account_entries = self.fetchJournalEntryItems(account=account_id, type='debtor')
        debtor_account_entries_value = 0
        for entry in debtor_account_entries:
            if entry['currency'] == currency_id:
                debtor_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        debtor_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        creditor_opposite_account_entries = self.fetchJournalEntryItems(opposite_account=account_id, type='creditor')
        creditor_opposite_account_entries_value = 0
        for entry in creditor_opposite_account_entries:
            if entry['currency'] == currency_id:
                creditor_opposite_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        creditor_opposite_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        debtor_opposite_account_entries = self.fetchJournalEntryItems(opposite_account=account_id, type='debtor')
        debtor_opposite_account_entries_value = 0
        for entry in debtor_opposite_account_entries:
            if entry['currency'] == currency_id:
                debtor_opposite_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        debtor_opposite_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        creditor_account_entries = self.fetchJournalEntryItems(account=account_id, type='creditor')
        creditor_account_entries_value = 0
        for entry in creditor_account_entries:
            if entry['currency'] == currency_id:
                creditor_account_entries_value += entry['value_col']
            else:
                if unify_currency:
                    exchange_rate = self.fetchExchangeValue(entry['currency'], currency_id, date)
                    if exchange_rate:
                        creditor_account_entries_value += entry['value_col'] * exchange_rate[0][1]

        account_value = (debtor_account_entries_value + creditor_opposite_account_entries_value) - (creditor_account_entries_value + debtor_opposite_account_entries_value)

        # This method only calculates the value for the specified account, not including its children
        return account_value

    @check_permission('clients', 'R')
    def fetchClientAccountValue(self, client_id, currency_id, date='', unify_currency=False):
        print("DATABASE> Fetch client account value")

        client_account_id = None
        account_value = 0
        try:
            client_data = self.fetchClient(client_id)
            client_account_id = client_data['client_account_id']
        except:
            pass

        if client_account_id:
            account_value = self.fetchAccountValue(client_account_id, currency_id, date, unify_currency)
        return account_value


    @check_permission('clients', 'R')
    def fetchClientPaymentCurrencies(self, client_id) -> list:
        print("DATABASE> Fetch client payment currencies")
        query = "SELECT DISTINCT `invoices`.`currency` as `currency_id`, `currencies`.`name` as `currency_name` FROM `invoices` JOIN `currencies` ON `invoices`.`currency`=`currencies`.`id` WHERE `invoices`.`client`='" + str(client_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('clients', 'R')
    def fetchClientReport(self, client_id, from_date, to_date) -> list:
        print("DATABASE> Fetch client report")

        query = """
            SELECT
                invoices.id as invoice_id,
                invoices.date_col as date_col,
                invoices.type_col as invoice_type,
                invoices.currency,
                invoices.payment,
                invoices.paid,
                CASE
                    WHEN invoices.paid = 'yes' THEN 0
                    ELSE SUM(invoice_items.quantity1 * invoice_items.equilivance_price)
                END as debt,
                clients.name as client_name,
                currencies.name as currency_name,
                SUM(invoice_items.quantity1 * invoice_items.equilivance_price) as invoice_value
            FROM invoices
            LEFT JOIN clients ON invoices.client = clients.id
            LEFT JOIN invoice_items ON invoices.id = invoice_items.invoice_id
            LEFT JOIN currencies ON invoices.currency = currencies.id
            WHERE invoices.client = %s
            AND DATE(invoices.date_col) >= DATE(%s)
            AND DATE(invoices.date_col) <= DATE(%s)
            GROUP BY invoices.id
            ORDER BY invoices.date_col DESC"""

        self.cursor.execute(query, (str(client_id), str(from_date), str(to_date)))
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('sales', 'R')
    def fetchSalesTargets(self) -> list:
        print("DATABASE> Fetch sales targets")
        query = "SELECT `sales_targets`.*, `materials`.`name` as `product` FROM `sales_targets` JOIN `materials` ON `sales_targets`.`material`=`materials`.`id`"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('sales', 'W')
    def addSalesTarget(self, product, year, month, location, target) -> int:
        print("DATABASE> Add sales target")
        query = "INSERT INTO `sales_targets`(`material`, `year_col`, `month_col`, `location`, `target`) VALUES ('" + str(
            product) + "','" + str(year) + "','" + str(month) + "','" + str(location) + "','" + str(target) + "')"
        # print(query)
        self.cursor.execute(query)
        last_id = self.cursor.lastrowid
        self.sqlconnector.conn.commit()
        return last_id

    @check_permission('sales', 'W')
    def removeSalesTarget(self, id) -> None:
        print("DATABASE> Delete sales target item#" + str(id))
        query = "DELETE FROM sales_targets WHERE id='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('sales', 'R')
    def fetchSoldVsTargets(self, product, year) -> list:
        print("DATABASE> Fetch sales vs. targets")
        invoice_sell_id = self.fetchInvoiceTypes(name='sell')[0]['id']
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT MONTH(`invoices`.`date_col`) as `month_col`, SUM(`invoice_items`.`quantity1`) as `sold`, `sales_targets`.`target` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `sales_targets` ON MONTH(`invoices`.`date_col`)=`sales_targets`.`month_col` WHERE `sales_targets`.`material`='" + str(
                product) + "' AND YEAR(`invoices`.`date_col`)='" + str(
                year) + "' AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY MONTH(`invoices`.`date_col`)"
        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = "SELECT strftime('%m', `invoices`.`date_col`)+0 as `month_col`, SUM(`invoice_items`.`quantity1`) as `sold`, `sales_targets`.`target` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `sales_targets` ON strftime('%m',`invoices`.`date_col`)+0=(`sales_targets`.`month_col`)+0 WHERE `sales_targets`.`material`='" + str(
                product) + "' AND strftime('%Y',`invoices`.`date_col`)+0='" + str(
                year) + "'+0 AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY strftime('%m',`invoices`.`date_col`)+0"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('sales', 'R')
    def fetchClientsProductSalesPerMonth(self, product, year) -> list:
        print("DATABASE> Fetch clients sales vs. targets")
        invoice_sell_id = self.fetchInvoiceTypes(name='sell')[0]['id']
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT MONTH(`invoices`.`date_col`) as `month_col`, SUM(`invoice_items`.`quantity1`) as `sold`, `clients`.`name`, `clients`.`governorate` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `clients` ON `invoices`.`client`=`clients`.`id` WHERE `invoice_items`.`material_id`='" + str(product) + "' AND YEAR(`invoices`.`date_col`)='" + str(year) + "' AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY MONTH(`invoices`.`date_col`), `clients`.`name`"
        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = "SELECT strftime('%m',`invoices`.`date_col`)+0 as `month_col`, SUM(`invoice_items`.`quantity1`) as `sold`, `clients`.`name`, `clients`.`governorate` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `clients` ON `invoices`.`client`=`clients`.`id` WHERE `invoice_items`.`material_id`='" + str(
                product) + "' AND strftime('%Y',`invoices`.`date_col`)+0='" + str(
                year) + "'+0 AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY strftime('%m',`invoices`.`date_col`), `clients`.`name`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('sales', 'R')
    def fetchGovernoratesProductSalesPerMonth(self, product, year) -> list:
        print("DATABASE> Fetch governorates sales vs. targets")
        invoice_sell_id = self.fetchInvoiceTypes(name='sell')[0]['id']

        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT MONTH(`invoices`.`date_col`) as `month_col`, `clients`.`governorate` as location, SUM(`invoice_items`.`quantity1`) as sold, `sales_targets`.`target` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `clients` ON `invoices`.`client`=`clients`.`id` JOIN `sales_targets` ON MONTH(`invoices`.`date_col`)=`sales_targets`.`month_col` AND `clients`.`governorate`=`sales_targets`.`location` WHERE `sales_targets`.`material`='" + str(product) + "' AND YEAR(`invoices`.`date_col`)='" + str(year) + "' AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY MONTH(`invoices`.`date_col`), `clients`.`governorate`"
        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = "SELECT strftime('%m',`invoices`.`date_col`)+0 as month_col, `clients`.`governorate` as location, SUM(`invoice_items`.`quantity1`) as sold, `sales_targets`.`target` FROM `invoice_items` JOIN `invoices` ON `invoice_items`.`invoice_id`=`invoices`.`id` JOIN `clients` ON `invoices`.`client`=`clients`.`id` JOIN `sales_targets` ON strftime('%m',`invoices`.`date_col`)+0=`sales_targets`.`month_col`+0 AND `clients`.`governorate`=`sales_targets`.`location` WHERE `sales_targets`.`material`='" + str(product) + "' AND strftime('%Y',`invoices`.`date_col`)+0='" + str(year) + "'+0 AND `invoices`.`type_col`='" + str(invoice_sell_id) + "' GROUP BY strftime('%m',`invoices`.`date_col`), `clients`.`governorate`"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    ############ accounts ############

    @check_permission('accounts', 'R')
    def fetchAccounts(self, type="all", final_account='', financial_statement_block='') -> list:
        print("DATABASE> Fetch accounts")
        # Check if using MySQL connection
        if isinstance(self.sqlconnector, MysqlConnector):
            query = "SELECT `accounts`.`id`, `accounts`.`name`, `accounts`.`code`, `accounts`.`details`, `accounts`.`date_col`,`parent`.`id` as `parent_id`, `parent`.`name` as `parent_name`, `accounts`.`type_col`, `accounts`.`final_account`, `accounts`.`financial_statement`, `accounts`.`financial_statement_block`, `accounts`.`force_cost_center`, `accounts`.`default_cost_center` FROM `accounts` LEFT JOIN `accounts` AS `parent` ON `accounts`.`parent_account`=`parent`.`id` WHERE `accounts`.`type_col`= COALESCE(NULLIF('" + str(
                type) + "','all'),`accounts`.`type_col`) AND IFNULL(`accounts`.`final_account`, '0') = IFNULL(NULLIF('" + str(
                final_account) + "',''), IFNULL(`accounts`.`final_account`, '0')) AND IFNULL(`accounts`.`financial_statement_block`, '0') =  IFNULL(NULLIF('" + str(
                financial_statement_block) + "', ''), IFNULL(`accounts`.`financial_statement_block`, '0')) ORDER BY `accounts`.`id`, `parent_id` ASC"
            print(query)
            self.cursor.execute(query)

        else: # if str(type(self.sqlconnector)) == "<class 'SqliteConnector.SqliteConnector'>":
            query = (
                "SELECT accounts.id, accounts.name, accounts.code, accounts.details, accounts.date_col, "
                "       parent.id as parent_id, parent.name as parent_name, accounts.type_col, accounts.final_account, "
                "       accounts.financial_statement, accounts.financial_statement_block, accounts.force_cost_center, accounts.default_cost_center "
                "FROM accounts LEFT JOIN accounts AS parent ON accounts.parent_account = parent.id "
                "WHERE accounts.type_col = COALESCE(NULLIF(?,'all'), accounts.type_col) "
                "  AND IFNULL(accounts.final_account, '0') = IFNULL(NULLIF(?,''), IFNULL(accounts.final_account, '0')) "
                "  AND IFNULL(accounts.financial_statement_block, '0') = IFNULL(NULLIF(?,''), IFNULL(accounts.financial_statement_block, '0')) "
                    "ORDER BY accounts.id, parent_id ASC"
            )
            self.cursor.execute(query, (type, final_account, financial_statement_block))

        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('accounts', 'R')
    def fetchAccount(self, id) -> dict:
        print("DATABASE> Fetch account #" + str(id))
        query = "SELECT * FROM `accounts` WHERE `id` = '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0]  # Because it always returns one row.

    @check_permission('accounts', 'R')
    def fetchChildAccounts(self, parent_id, type='') -> list:
        print("DATABASE> Fetch childern accounts of #" + str(parent_id))
        query = "SELECT * FROM `accounts` WHERE `parent_account` = '" + str(
            parent_id) + "' AND IFNULL(`accounts`.`type_col`,'0') =  IFNULL(NULLIF('" + str(
            type) + "',''),IFNULL(`accounts`.`type_col`,0)) ORDER BY `date_col` ASC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchParentAccount(self, account_id):
        print("DATABASE> Fetch parent account of #" + str(account_id))
        query = "SELECT `parents`.* FROM `accounts` as children join `accounts` as parents ON `children`.`parent_account`=`parents`.`id` WHERE `children`.`id`='" + str(
            account_id) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        if row:
            return row
        return None

    @check_permission('accounts', 'R')
    def fetchAccountDescendants(self, account_id, depth=-1) -> list:
        descendants = []
        if depth != 0:
            child_accounts = self.fetchChildAccounts(account_id)
            for child_account in child_accounts:
                descendants.append(child_account)
                if depth >= 1 or depth <= -1:
                    child_descendants = self.fetchAccountDescendants(child_account[0], depth - 1)
                    descendants.extend(child_descendants)
        return descendants


    @check_permission('accounts', 'R')
    def fetchSiblingAccounts(self, account_id) -> list:
        print("DATABASE> Fetch sibling accounts of #" + str(account_id))
        # Get parent ID
        query = "SELECT `parent_account` FROM `accounts` WHERE `id`='" + str(account_id) + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        parent_id = rows[0][0]
        # Get children of that parent which have id != account_id
        query = "SELECT * FROM `accounts` WHERE `parent_account`='" + str(parent_id) + "' and `id` != '" + str(
            account_id) + "' ORDER BY `date_col` ASC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    @check_permission('accounts', 'R')
    def fetchAccountAncestors(self, account_id, depth=-1) -> list:
        # Check if depth is 0 or if the parent_id is None
        ancestors = []
        if depth != 0:
            row = self.fetchParentAccount(account_id)
            parent_id = None
            if row:
                ancestors.append(row)
                parent_id = row[4]
            if parent_id and depth - 1 > 0:
                parent_ancestors = self.fetchAccountAncestors(row[0], depth - 1)
                ancestors.extend(parent_ancestors)

        return ancestors

    @check_permission('accounts', 'W')
    def recalculateAccountsCodes(self, account_id=None) -> None:
        if not account_id:
            # we can't use [ORDER BY `asc`] alone, because rows might all be inserted at the same time when creating dababase (see MysqlConnector.py & SqliteConnector.py)
            query = "SELECT * FROM (SELECT `id`, CAST(`code` AS UNSIGNED) as `code`, `parent_account`, `date_col` FROM `accounts`) as `accounts` ORDER BY `date_col`, `code` ASC"
        else:
            query = "SELECT `id`, `code`, `parent_account` FROM `accounts` WHERE `id`='" + str(
                account_id) + "'  ORDER BY `date_col` ASC"

        self.cursor.execute(query)
        accounts = self.cursor.fetchall()
        next_main_code = 1
        for account in accounts:
            account_id = account[0]
            account_parent = account[2]

            if not account_parent or account_parent == '':  # This is a main account
                query = "UPDATE `accounts` SET `code`='" + str(next_main_code) + "' WHERE `id`='" + str(
                    account_id) + "'"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()
                next_main_code += 1

            else:  # this is a sub-account
                # get the code of the parent
                query = "SELECT `code` FROM `accounts` WHERE `id`='" + str(account_parent) + "'"
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                parent_code = rows[0][0]
                self.sqlconnector.conn.commit()

                children = self.fetchChildAccounts(account_parent)
                next_child_code = 0
                for child in children:
                    child_id = child[0]
                    next_code = str(parent_code) + "-" + str(next_child_code + 1)
                    query = "UPDATE `accounts` SET `code`='" + str(next_code) + "' WHERE `id`='" + str(child_id) + "'"
                    self.cursor.execute(query)
                    self.sqlconnector.conn.commit()
                    next_child_code += 1

            # re-code childern
            children = self.fetchChildAccounts(account_id)
            for child in children:
                child_id = child[0]
                self.recalculateAccountsCodes(child_id)


    @check_permission('accounts', 'W')
    def addAccount(self, name, details, parent_account, account_type, final_account, financial_statement,financial_statement_block, force_cost_center=0, default_cost_center='', code='', auto=False) -> int:

        # check if parent account still exists
        if not parent_account:
            parent_account = ''
            parent_exists = True
        else:
            parent_exists = self.checkIfRowExist('accounts', 'id', parent_account)

        if parent_exists:
            query = "INSERT INTO `accounts`(`name`, `details`, `code`, `parent_account`, `type_col`, `final_account`, `financial_statement`, `financial_statement_block`, `force_cost_center`, `default_cost_center`) VALUES ('" + str(
                name) + "', NULLIF('" + str(details) + "', ''), NULLIF('" + str(code) + "', ''), NULLIF('" + str(parent_account) + "', ''), '" + str(
                account_type) + "', NULLIF('" + str(final_account) + "', ''), NULLIF('" + str(financial_statement) + "', ''), NULLIF('" + str(
                financial_statement_block) + "', ''), NULLIF('" + str(force_cost_center) + "', ''), NULLIF('" + str(default_cost_center) + "', ''))"

            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            new_account_id = self.cursor.lastrowid
            if not auto:
                self.recalculateAccountsCodes()
            return new_account_id

    @check_permission('accounts', 'W')
    def updateAccount(self, id, name, code, details, parent_account, final_account_id, financial_statement,
                      financial_statement_block, force_cost_center, default_cost_center) -> None:
        # get descendats to check later for infinity loops and prevent them.
        descendants = [descendant[0] for descendant in list(self.fetchAccountDescendants(id))]

        # get old parent
        old_parent_id = self.fetchAccount(id)[3]

        if not parent_account:
            parent_account = ''

        if (parent_account == '') or (parent_account and self.checkIfRowExist('accounts', 'id', parent_account)):
            query = "UPDATE `accounts` SET `name`='" + str(name) + "', `details`=NULLIF('" + str(
                details) + "', ''), `code`=NULLIF('" + str(
                code) + "', ''), `parent_account`=NULLIF('" + str(
                parent_account) + "', ''), `final_account`=NULLIF('" + str(
                final_account_id) + "', ''), `financial_statement`=NULLIF('" + str(
                financial_statement) + "', ''), `financial_statement_block`=NULLIF ('" + str(
                financial_statement_block) + "', ''), `force_cost_center`=NULLIF('" + str(
                force_cost_center) + "', ''), `default_cost_center`=NULLIF('" + str(
                default_cost_center) + "', '') WHERE `id`='" + id + "'"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            if parent_account in descendants:
                query = "UPDATE `accounts` SET `parent_account`='" + str(old_parent_id) + "' WHERE `id`='" + str(
                    parent_account) + "'"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()

            self.recalculateAccountsCodes()

        else:
            print("Error - Parent account doesn't exist.")


    @check_permission('accounts', 'W')
    def removeAccount(self, id) -> bool:
        print("Delete Account " + str(id))
        query = "DELETE FROM `accounts` WHERE `id`='" + str(id) + "'"
        print(query)
        deleted = False
        try:
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            deleted = True
        except Exception as e:
            print('Error Deleting Account!, ', e)
        return deleted

    def fetchLoans(self):
        query = "SELECT loans.*, currencies.name as currency_name, currencies.id as currency_id, accounts1.name as account_name, accounts2.name as opposite_account_name FROM loans LEFT JOIN currencies ON loans.currency = currencies.id LEFT JOIN accounts accounts1 ON loans.account_id = accounts1.id LEFT JOIN accounts accounts2 ON loans.opposite_account_id = accounts2.id"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('loans', 'W')
    def fetchLoan(self, id):
        query = "SELECT * FROM `loans` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0]

    @check_permission('loans', 'W')
    def addLoan(self, name, amount, date_col, account_id, opposite_account_id, cycle, currency, interest):
        query = "INSERT INTO `loans` (`name`, `amount`, `date_col`, `account_id`, `opposite_account_id`, `cycle`, `currency`, `interest`) VALUES ('" + str(name) + "', '" + str(amount) + "', '" + str(date_col) + "', '" + str(account_id) + "', '" + str(opposite_account_id) + "', '" + str(cycle) + "', '" + str(currency) + "', '" + str(interest) + "')"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        return self.cursor.lastrowid


    def updateLoan(self, id, name, amount, date_col, account_id, opposite_account_id, cycle, currency, interest):
        query = "UPDATE `loans` SET `name`='" + str(name) + "', `amount`='" + str(amount) + "', `date_col`='" + str(date_col) + "', `account_id`='" + str(account_id) + "', `opposite_account_id`='" + str(opposite_account_id) + "', `cycle`='" + str(cycle) + "', `currency`='" + str(currency) + "', `interest`='" + str(interest) + "' WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('loans', 'W')
    def removeLoan(self, id):
        query = "DELETE FROM `loans` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('loans', 'W')
    def fetchLoanPayments(self, loan_id=''):
        if loan_id:
            query = "SELECT loan_payments.*, loans.name as loan_name FROM `loan_payments` LEFT JOIN loans ON loan_payments.loan_id = loans.id WHERE loan_payments.loan_id='" + str(loan_id) + "'"
        else:
            query = "SELECT loan_payments.*, loans.name as loan_name FROM `loan_payments` LEFT JOIN loans ON loan_payments.loan_id = loans.id"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows
    
    @check_permission('loans', 'W')
    def fetchLoanPayment(self, id):
        query = "SELECT * FROM `loan_payments` WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows[0]

    @check_permission('loans', 'W')
    def addLoanPayment(self, loan_id, date, amount, currency):
        query = "INSERT INTO `loan_payments` (`loan_id`, `date_col`, `amount`, `currency`) VALUES ('" + str(loan_id) + "', '" + str(date) + "', '" + str(amount) + "', '" + str(currency) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        return self.cursor.lastrowid

    @check_permission('loans', 'W')
    def removeLoanPayment(self, id):
        query = "DELETE FROM `loan_payments` WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('loans', 'W')
    def updateLoanPayment(self, id, amount, currency, date):
        query = "UPDATE `loan_payments` SET `amount`='" + str(amount) + "', `currency`='" + str(currency) + "', `date_col`='" + str(date) + "' WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ############ Settings #############

    # @check_permission('settings', 'R')
    def fetchSetting(self, setting_name) -> str:
        print("DATABASE> Fetch setting " + str(setting_name))
        query = "SELECT `value_col` FROM `settings` WHERE `name`='" + str(setting_name) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if (len(rows) > 0):
            return rows[0][0]
        else:
            return None


    @check_permission('settings', 'R')
    def fetchSettings(self, settings_names) -> list:
        print("DATABASE> Fetch settings like " + str(settings_names))
        query = "SELECT `name`, `value_col` FROM `settings` WHERE `name` LIKE '%" + str(settings_names) + "%'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('settings', 'R')
    def fetchUserSetting(self, user_id, setting_name) -> str:
        print("DATABASE> Fetch user setting " + str(user_id))
        query = "SELECT `name` FROM `user_settings` WHERE `user_id`='" + str(user_id) + "' AND `name`='" + str(setting_name) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if (len(rows) > 0):
            return rows[0]['name']
        else:
            return None


    # @check_permission('settings', 'R')
    def fetchUserSettings(self, user_id) -> list:
        print("DATABASE> Fetch user_settings")
        query = "SELECT `name` FROM `user_settings` WHERE `user_id`='" + str(user_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('settings', 'W')
    def saveUserSetting(self, user_id, name) -> None:
        query = "INSERT INTO `user_settings` (`user_id`, `name`) VALUES ('" + str(user_id) + "', '" + str(name) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('settings', 'W')
    def removeUserSetting(self, user_id, name) -> None:
        query = "DELETE FROM `user_settings` WHERE `user_id`='" + str(user_id) + "' AND `name`='" + str(name) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('settings', 'W')
    def fetchFloatPointValue(self) -> str:
        query = "SELECT `value_col` FROM `settings` WHERE `name`='float_point_value'"
        self.cursor.execute(query)
        print(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0][0]


    @check_permission('settings', 'W')
    def updateFloatPointValue(self, value) -> None:
        query = "UPDATE `settings` SET `value_col`='" + str(value) + "' WHERE `name`='float_point_value'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('currencies', 'R')
    def fetchCurrencies(self) -> list:
        print("DATABASE> Fetch all currencies")
        query = "SELECT * FROM `currencies`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('currencies', 'R')
    def fetchCurrencyByName(self, name) -> dict:
        query = "SELECT * FROM `currencies` WHERE `name` = '" + str(name) + "'"
        self.cursor.execute(query)
        print(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0]

    @check_permission('currencies', 'R')
    def fetchMaterialCurrencies(self, material_id) -> list:
        print("DATABASE> Fetch all material currencies")
        query = "SELECT DISTINCT `invoice_items`.`currency_id`, `currencies`.`name` FROM `invoice_items` JOIN `currencies` ON `invoice_items`.`currency_id` = `currencies`.`id` WHERE `invoice_items`.`material_id` = '" + str(material_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('settings', 'W')
    def saveSetting(self, setting_name, value) -> None:
        print("DATABASE> Save setting " + str(setting_name))
        if not value:
            value = ''
        query = "REPLACE INTO `settings` (`name`,`value_col`) VALUES ('" + str(setting_name) + "', NULLIF('" + str(
            value) + "',''))"  # To use REPLACE INTO, one or more of the targeted columns has to be unique
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('settings', 'W')
    def removeSetting(self, setting_name) -> None:
        print("DATABASE> Remove setting " + str(setting_name))
        query = f"DELETE FROM `settings` WHERE `name` = '{setting_name}'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ######## Currencies ########
    @check_permission('currencies', 'R')
    def fetchCurrency(self, id) -> dict:
        query = "SELECT * FROM `currencies` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0]

    @check_permission('currencies', 'W')
    def addCurrency(self, name, symbol, parts, parts_realation) -> None:
        print("DATABASE> Add currency")
        query = "INSERT INTO `currencies` (`name`, `symbol`, `parts`, `parts_relation`) VALUES ('" + name + "','" + symbol + "','" + parts + "','" + parts_realation + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('currencies', 'W')
    def editCurrency(self, id, name, symbol, parts, parts_relation) -> None:
        print("DATABASE> Edit currency")
        query = "UPDATE `currencies` SET `name`='" + name + "', `symbol`='" + symbol + "', `parts`='" + parts + "', `parts_relation`='" + parts_relation + "' WHERE `id`='" + str(
            id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('currencies', 'W')
    def deleteCurrency(self, id) -> bool:
        print("DATABASE> Delete currency")
        query = f"DELETE FROM `currencies` WHERE `id` = '{id}'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        if self.cursor.rowcount > 0:
            return True  # Currency was successfully deleted
        else:
            return False  # No records were deleted

    @check_permission('currencies', 'R')
    def fetchExchangeValue(self, currency1_id, currency2_id, date=None, commit=True) -> list:
        """
        Fetch exchange rate between two currencies.

        Args:
            currency1_id: ID of first currency
            currency2_id: ID of second currency
            date: Optional date to filter by

        Returns:
            If date provided:
                - Float exchange rate value if found
                - Last available exchange rate if not found for specified date
                - None if no exchange rates exist
            If no date:
                - List of tuples (id, exchange_rate, date) for all exchanges
                - Empty list if none found
        """
        print(f"DATABASE> Fetch exchange value between {currency1_id} and {currency2_id}" +
              (f" ON {date}" if date else ""))

        if str(currency1_id) == str(currency2_id):
            return [(1, 1, date)]

        exchange_values = []

        # Try both currency order combinations
        for currency1, currency2 in ((currency1_id, currency2_id), (currency2_id, currency1_id)):
            query = f"SELECT * FROM `exchange_prices` WHERE `currency1` = {str(currency1)} and `currency2` = {str(currency2)}"
            if date:
                # First try to get exact date match
                date_query = query + f" and `date_col` = '{date}'"
                print(date_query)
                self.cursor.execute(date_query)
                rows = self.cursor.fetchall()

            else:
                print(query)
                self.cursor.execute(query)
                rows = self.cursor.fetchall()

            # Process results based on currency order
            for row in rows:
                exchange_rate = row[3] if currency1 == currency1_id else 1 / float(row[3])
                exchange_values.append((row[0], exchange_rate, row[4]))

        if commit:
            self.sqlconnector.conn.commit()

        return exchange_values

    @check_permission('currencies', 'R')
    def fetchExchangeValues(self, currency_id) -> list:
        print("DATABASE> Fetch exchange value_col for " + str(currency_id));
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "SELECT `exchange_data`.`id`, `exchange_data`.`exchange`, `exchange_data`.`date_col`, `currencies`.`name` FROM (select id, case when currency1=" + str(
                currency_id) + " then `currency2` when `currency2`=" + str(
                currency_id) + " then `currency1` end as `currency`,  case when `currency1` = " + str(
                currency_id) + " then `exchange` when `currency2` =" + str(
                currency_id) + " then 1/`exchange` end as `exchange`, `date_col` from `exchange_prices`)  AS exchange_data JOIN `currencies` ON exchange_data.currency=`currencies`.`id`"

        else:  # if type(self.sql_connector)=="<class 'SqliteConnector.SqliteConnector'>"
            query = "SELECT `exchange_data`.`id`, `exchange_data`.`exchange`, `exchange_data`.`date_col`, `currencies`.`name` FROM (select id, case when currency1=" + str(
                currency_id) + " then `currency2` when `currency2`=" + str(
                currency_id) + " then `currency1` end as `currency`, case when `currency1` = " + str(
                currency_id) + " then `exchange` when `currency2` =" + str(
                currency_id) + " then 1/`exchange` end as `exchange`, `date_col` from `exchange_prices`) AS exchange_data JOIN `currencies` ON exchange_data.currency=`currencies`.`id`"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows  # id, exchange, name

    @check_permission('currencies', 'W')
    def removeExchangeValue(self, exchange_id) -> None:
        print("DATABASE> Remove exchange value_col for " + str(exchange_id));
        query = "DELETE FROM `exchange_prices` WHERE `id`=" + str(exchange_id)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('currencies', 'W')
    def addExchageValue(self, currency1_id, currency2_id, exchage_value, date) -> None:
        print("DATABASE> Fetch exchange value_col between " + str(currency1_id) + " and " + str(currency2_id))
        try:
            exchage_value = float(exchage_value)
            #
            # # check if a previous exchange value_col between currency1 and currency2 already exists
            # old_exchage_value = self.fetchExchangeValue(currency1_id, currency2_id, date)
            # if (not old_exchage_value or old_exchage_value not in (exchage_value, 1 / exchage_value)):
            #     # if there's no old exchange value_col, add the new one
            #     # also, if the old exchnage value_col is different from the new one, replace the old one by the new one.
            #     # please note that we used 1/exchange_value, because the exchange rate may be set from currency2 to currency1.
            query = "REPLACE INTO `exchange_prices` (`currency1`,`currency2`,`exchange`,`date_col`) VALUES ('" + str(
                currency1_id) + "', '" + str(currency2_id) + "', " + str(exchage_value) + ", '" + str(date) + "')"
            print(query)
            self.cursor.execute(query)
            # Make sure to delete the opposite-side exchange value_col if it exists
            # query = "DELETE FROM `exchange_prices` WHERE `currency1`=" + str(
            #     currency2_id) + " AND `currency2`=" + str(
            #     currency1_id)
            # self.cursor.execute(query)
            self.sqlconnector.conn.commit()

        except:
            traceback.print_exc()

    ######### GROUPS ###########
    @check_permission('groups', 'R')
    def fetchGroups(self) -> list:
        print("DATABASE> Fetch groups")
        query = "SELECT `groups`.`id`, `groups`.`name`, `groups`.`code`, `groups`.`date_col`,`parent`.`id` as `parent_id`, `parent`.`name` as `parent_name` FROM `groups` LEFT JOIN `groups` AS `parent` ON `groups`.`parent_group`=`parent`.`id` ORDER BY `groups`.`id`, `parent_id` ASC"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchGroupsCount(self):
        print("DATABASE> Fetch groups count")
        query = "SELECT COUNT(*) FROM `groups`"
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return {'groups_count': rows[0]}

    def fetchGroup(self, id):
        print("DATABASE> Fetch account #" + str(id))
        query = "SELECT * FROM `groups` WHERE `id` = '" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0]  # Because it always returns one row.

    def fetchChildGroups(self, parent_id):
        print("DATABASE> Fetch childern accounts of #" + str(parent_id))
        query = "SELECT * FROM `groups` WHERE `parent_group` = '" + str(parent_id) + "' ORDER BY `date_col` ASC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchDescendantGroups(self, parent_id):
        # Yield functions accumulates results and finally returns a (generator) object, which can be converted into a list.
        print("DATABASE> Fetch descendant accounts of #" + str(parent_id))
        query = "SELECT * FROM `groups` WHERE `parent_group` = '" + str(parent_id) + "' ORDER BY `date_col` ASC"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            yield row  # Return (Row) and continue execution.
            child_id = row[0]
            yield from self.fetchChildAccounts(child_id)  # This is similar to
            # for child in self.fetchChildAccounts(child_id):
            #      yield(child)
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('groups', 'R')
    def fetchSiblingGroups(self, group_id) -> list:
        print("DATABASE> Fetch sibling accounts of #" + str(group_id))
        # Get parent ID
        query = "SELECT `parent_group` FROM `groups` WHERE `id`='" + str(group_id) + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        parent_id = rows[0][0]
        # Get children of that parent which have id != account_id
        query = "SELECT * FROM `groups` WHERE `parent_group`='" + str(group_id) + "' and `id` != '" + str(
            group_id) + "' ORDER BY `date_col` ASC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('groups', 'W')
    def recalculateGroupsCodes(self, group_id=None) -> None:
        if not group_id:
            # we can't use [ORDER BY `asc`] alone, because rows might all be inserted at the same time when creating dababase (see MysqlConnector.py & SqliteConnector.py)
            query = "SELECT * FROM (SELECT `id`, CAST(`code` AS UNSIGNED) as `code`, `parent_group`, `date_col` FROM `groups`) as `groups` ORDER BY `date_col`, `code` ASC"
        else:
            query = "SELECT `id`, `code`, `parent_group` FROM `groups` WHERE `id`='" + str(
                group_id) + "'  ORDER BY `date_col` ASC"
        print(query)
        self.cursor.execute(query)
        groups = self.cursor.fetchall()
        next_main_code = 1
        for group in groups:
            group_id = group[0]
            group_parent = group[2]

            if not group_parent or group_parent == '':  # This is a main group
                query = "UPDATE `groups` SET `code`='" + str(next_main_code) + "' WHERE `id`='" + str(
                    group_id) + "'"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()
                next_main_code += 1

            else:  # this is a sub-group
                # get the code of the parent
                query = "SELECT `code` FROM `groups` WHERE `id`='" + str(group_parent) + "'"
                # print(query)
                self.cursor.execute(query)
                rows = self.cursor.fetchall()
                parent_code = rows[0][0]
                self.sqlconnector.conn.commit()

                children = self.fetchChildGroups(group_parent)
                next_child_code = 0
                for child in children:
                    child_id = child[0]
                    next_code = str(parent_code) + "-" + str(next_child_code + 1)
                    query = "UPDATE `groups` SET `code`='" + str(next_code) + "' WHERE `id`='" + str(child_id) + "'"
                    self.cursor.execute(query)
                    self.sqlconnector.conn.commit()
                    next_child_code += 1

            # re-code childern
            children = self.fetchChildGroups(group_id)
            for child in children:
                child_id = child[0]
                self.recalculateGroupsCodes(child_id)

    @check_permission('groups', 'W')
    def addGroup(self, name, parent_group) -> None:
        # check if parent group still exists
        if not parent_group:
            parent_group = 'NULL'
            parent_exists = True
        else:
            parent_exists = self.checkIfRowExist('groups', 'id', parent_group)

        if parent_exists:
            query = "INSERT INTO `groups`(`name`, `code`, `parent_group`) VALUES ('" + str(
                name) + "', NULL ," + str(parent_group) + ")"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            new_group_id = self.cursor.lastrowid
            self.recalculateGroupsCodes()


    @check_permission('groups', 'W')
    def updateGroup(self, id, name, parent_group) -> None:
        # get descendats to check later for infinity loops and prevent them.
        descendants = [descendant[0] for descendant in list(self.fetchDescendantGroups(id))]

        # get old parent
        old_parent_id = self.fetchGroup(id)[3]

        if not parent_group:
            parent_group = 'NULL'

        if parent_group == 'NULL' or (parent_group and self.checkIfRowExist('groups', 'id', parent_group)):
            query = "UPDATE `groups` SET `name`='" + str(name) + "', `code`=NULL, `parent_group`=" + str(
                parent_group) + " WHERE `id`='" + id + "'"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            if parent_group in descendants:
                query = "UPDATE `groups` SET `parent_group`='" + str(old_parent_id) + "' WHERE `id`='" + str(
                    parent_group) + "'"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()

            self.recalculateGroupsCodes()

        else:
            print("Error - Parent group doesn't exist.")

    @check_permission('groups', 'W')
    def removeGroup(self, id) -> None:
        print("DATABASE> Delete group #" + str(id))
        # First, delete any child groups recursively
        children = self.fetchChildGroups(id)
        for child in children:
            child_id = child[0]
            self.removeGroup(child_id)

        # Then, delete the group itself
        query = "DELETE FROM `groups` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    ########## Materials ##################
    @check_permission('materials', 'R')
    def fetchMaterials(self) -> list:
        print("DATABASE> fetch materials.")
        # query = 'SELECT `id`, `code`, `name`, `group_col`, `unit1`, `unit2`, `unit3` FROM `materials`' #deprecated
        # query = 'SELECT * FROM `materials`' #deprecated
        query = "SELECT `materials`.*, u1.name AS unit1_name, u2.name AS unit2_name, u3.name AS unit3_name, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` THEN `value_col` WHEN `unit1` = `materials`.`unit2` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit2`) AS `unit1_to_unit2_rate`, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` THEN `value_col` WHEN `unit1` = `materials`.`unit3` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit3`) AS `unit1_to_unit3_rate` FROM `materials` LEFT JOIN units u1 ON `materials`.`unit1` = `u1`.`id` LEFT JOIN units u2 ON `materials`.`unit2` = `u2`.`id` LEFT JOIN units u3 ON `materials`.`unit3` = `u3`.`id`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterial(self, id) -> dict:
        print("DATABASE> fetch material #" + str(id))
        query = "SELECT `materials`.*, u1.name AS unit1_name, u2.name AS unit2_name, u3.name AS unit3_name, (SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` THEN `value_col` WHEN `unit1` = `materials`.`unit2` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit2`) AS `unit1_to_unit2_rate`, (SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` THEN `value_col` WHEN `unit1` = `materials`.`unit3` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit3`) AS `unit1_to_unit3_rate` FROM `materials` LEFT JOIN units u1 ON `materials`.`unit1` = `u1`.`id` LEFT JOIN units u2 ON `materials`.`unit2` = `u2`.`id` LEFT JOIN units u3 ON `materials`.`unit3` = `u3`.`id` WHERE `materials`.`id`='" + str(
            id) + "'"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialsCount(self) -> list:
        print("DATABASE> Fetch materials count")
        query = "SELECT COUNT(*) as materials_count FROM `materials` GROUP BY `group_col`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchMaterialsOfGroup(self, group_id) -> list:
        print("DATABASE> fetch materials of group #" + str(group_id))
        query = "SELECT `materials`.*, u1.name AS unit1_name, u2.name AS unit2_name, u3.name AS unit3_name, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` THEN `value_col` WHEN `unit1` = `materials`.`unit2` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit2` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit2`) AS `unit1_to_unit2_rate`, ( SELECT CASE WHEN `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` THEN `value_col` WHEN `unit1` = `materials`.`unit3` AND `unit2` = `materials`.`unit1` THEN 1 / `value_col` END AS `value_col` FROM `units_conversion` WHERE `unit1` = `materials`.`unit1` AND `unit2` = `materials`.`unit3` OR `unit2` = `materials`.`unit1` AND `unit1` = `materials`.`unit3`) AS `unit1_to_unit3_rate` FROM `materials` LEFT JOIN units u1 ON `materials`.`unit1` = `u1`.`id` LEFT JOIN units u2 ON `materials`.`unit2` = `u2`.`id` LEFT JOIN units u3 ON `materials`.`unit3` = `u3`.`id`  WHERE `group_col` = '" + str(
            group_id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def fetchGrouppedMaterialsOfGroup(self, group_id) -> list:
        query = "SELECT `materials`.* FROM `materials` WHERE `group_col`='" + str(group_id) + "' AND `groupped`='1'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'W')
    def addMaterial(self, code, name, specs, size, manufacturer, color, origin, quality, model, unit1, unit2, unit3,
                    default_unit,
                    current_quantity, max_quantity, min_quantity, request_limit, gift,
                    gift_for, price1_desc, price1_1, price1_2, price1_3, price2_desc, price2_1, price2_2, price2_3,
                    price3_desc, price3_1, price3_2, price3_3, price4_desc, price4_1, price4_2, price4_3, price5_desc,
                    price5_1, price5_2, price5_3, price6_desc, price6_1, price6_2, price6_3, expiray, group,
                    price1_1_unit, price2_1_unit, price3_1_unit, price4_1_unit, price5_1_unit, price6_1_unit,
                    price1_2_unit, price2_2_unit, price3_2_unit, price4_2_unit, price5_2_unit, price6_2_unit,
                    price1_3_unit, price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit, price6_3_unit,
                    material_type, groupped, standard_unit1_quantity, standard_unit2_quantity,
                    standard_unit3_quantity, standard_work_hours,
                    yearly_required, manufacture_hall, material_addition_account, material_discount_account) -> None:

        print("DATABASE> Add new material")

        # if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
        query = "INSERT INTO `materials`(`code`, `name`, `group_col`, `specs`, `size_col`, `manufacturer`, `color`, `origin`, `quality`, `model`, `unit1`, `unit2`, `unit3`, `default_unit`, `current_quantity`, `max_quantity`, `min_quantity`, `request_limit`, `gift`, `gift_for`, `price1_desc`, `price1_1`, `price1_1_unit`, `price1_2`, `price1_2_unit`, `price1_3`, `price1_3_unit`, `price2_desc`, `price2_1`, `price2_1_unit`, `price2_2`, `price2_2_unit`, `price2_3`, `price2_3_unit`, `price3_desc`, `price3_1`, `price3_1_unit`, `price3_2`, `price3_2_unit`, `price3_3`, `price3_3_unit`, `price4_desc`, `price4_1`, `price4_1_unit`, `price4_2`, `price4_2_unit`, `price4_3`, `price4_3_unit`, `price5_desc`, `price5_1`, `price5_1_unit`, `price5_2`, `price5_2_unit`, `price5_3`, `price5_3_unit`, `price6_desc`, `price6_1`, `price6_1_unit`, `price6_2`, `price6_2_unit`, `price6_3`, `price6_3_unit`, `expiray`, `type_col`, `groupped`, `standard_unit1_quantity`, `standard_unit2_quantity`, `standard_unit3_quantity`, `work_hours`, `yearly_required`, `manufacture_hall`, `discount_account`, `addition_account`) VALUES ('" + str(
            code) + "', '" + str(name) + "', '" + str(group) + "', NULLIF('" + str(specs) + "',''), NULLIF('" + str(
            size) + "',''), NULLIF('" + str(manufacturer) + "',''), NULLIF('" + str(color) + "',''), NULLIF('" + str(
            origin) + "',''), NULLIF('" + str(quality) + "',''), NULLIF('" + str(model) + "',''), NULLIF('" + str(
            unit1) + "','') , NULLIF('" + str(unit2) + "','') , NULLIF('" + str(unit3) + "',''), " + str(
            default_unit) + ", NULLIF('" + str(
            current_quantity) + "',''), NULLIF('" + str(max_quantity) + "',''), NULLIF('" + str(
            min_quantity) + "',''), NULLIF('" + str(request_limit) + "','') , NULLIF('" + str(
            gift) + "',''), NULLIF('" + str(gift_for) + "',''), '" + str(price1_desc) + "', NULLIF('" + str(
            price1_1) + "',''), '" + str(price1_1_unit) + "', NULLIF('" + str(price1_2) + "',''), '" + str(
            price1_2_unit) + "', NULLIF('" + str(price1_3) + "',''), '" + str(price1_3_unit) + "', '" + str(
            price2_desc) + "', NULLIF('" + str(price2_1) + "',''), '" + str(price2_1_unit) + "', NULLIF('" + str(
            price2_2) + "',''), '" + str(price2_2_unit) + "', NULLIF('" + str(price2_3) + "',''), '" + str(
            price2_3_unit) + "', '" + str(price3_desc) + "', NULLIF('" + str(price3_1) + "',''), '" + str(
            price3_1_unit) + "', NULLIF('" + str(price3_2) + "',''), '" + str(price3_2_unit) + "', NULLIF('" + str(
            price3_3) + "',''), '" + str(price3_3_unit) + "', '" + str(price4_desc) + "', NULLIF('" + str(
            price4_1) + "',''), '" + str(price4_1_unit) + "', NULLIF('" + str(price4_2) + "',''), '" + str(
            price4_2_unit) + "', NULLIF('" + str(price4_3) + "',''), '" + str(price4_3_unit) + "', '" + str(
            price5_desc) + "', NULLIF('" + str(price5_1) + "',''), '" + str(price5_1_unit) + "', NULLIF('" + str(
            price5_2) + "',''), '" + str(price5_2_unit) + "', NULLIF('" + str(price5_3) + "',''), '" + str(
            price5_3_unit) + "', '" + str(price6_desc) + "', NULLIF('" + str(price6_1) + "',''), '" + str(
            price6_1_unit) + "', NULLIF('" + str(price6_2) + "',''), '" + str(price6_2_unit) + "', NULLIF('" + str(
            price6_3) + "',''), '" + str(price6_3_unit) + "', NULLIF('" + str(expiray) + "',''),'" + str(
            material_type) + "','" + str(groupped) + "', NULLIF('" + str(
            standard_unit1_quantity) + "',''), NULLIF('" + str(
            standard_unit2_quantity) + "',''), NULLIF('" + str(standard_unit3_quantity) + "',''), NULLIF('" + str(
            standard_work_hours) + "',''), NULLIF('" + str(yearly_required) + "',''), NULLIF('" + str(
            manufacture_hall) + "',''), NULLIF('" + str(material_discount_account) + "',''), NULLIF('" + str(
            material_addition_account) + "',''))"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def addComposition(self, composition_name, material_id):
        query = "INSERT INTO `compositions` (`name`, `material`) VALUES ('" + str(composition_name) + "', '" + str(material_id) + "')"
        self.cursor.execute(query)
        composition_id = self.cursor.lastrowid
        self.sqlconnector.conn.commit()
        return composition_id

    @check_permission('materials', 'W')
    def updateGrouppedMaterialComposition(self,composition_id, groupped_material_id, composition_materials: list) -> None:

        # check if material is really groupped: No need because this condition has to be already satisfied in order to access the composition window

        # delete previous composition
        query = "DELETE FROM `groupped_materials_composition` WHERE `groupped_material_id`='" + str(groupped_material_id) + "' AND `composition_id`='" + str(composition_id) + "'"
        self.cursor.execute(query)
        # for each material in the composition_materials array, insert a new record into groupped_materials_composition table
        for material in composition_materials:
            composition_material_id = material[0]
            quantity = material[1]
            unit = material[2]
            query = "INSERT INTO `groupped_materials_composition` (`groupped_material_id`, `composition_material_id`, `quantity`, `unit`, `composition_id`) VALUES ('" + str(groupped_material_id) + "','" + str(composition_material_id) + "','" + str(quantity) + "','" + str(unit) + "','" + str(composition_id) + "')"
            print(query)
            self.cursor.execute(query)

        self.sqlconnector.conn.commit()


    @check_permission('materials', 'R')
    def fetchGrouppedMaterialComposition(self, groupped_material_id) -> list:
        query = "SELECT `groupped_materials_composition`.*, `units`.`name` as `unit_name`, `units`.`id` as `unit_id` FROM `groupped_materials_composition` LEFT JOIN `units` ON `groupped_materials_composition`.`unit`=`units`.`id` WHERE `groupped_material_id`='" + str(
            groupped_material_id) + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    ############## Warehouses ###################
    @check_permission('warehouses', 'R')
    def fetchWarehouseCodename(self, warehouse_id) -> str:
        query = "SELECT `codename` FROM `warehouseslist` WHERE `id`='" + str(warehouse_id) + "'"
        # print(query)
        self.cursor.execute(query)
        try:  # in case result is unfetchable
            rows = self.cursor.fetchall()
            self.sqlconnector.conn.commit()
            codename = rows[0][0]
        except Exception as e:
            print(e)
            codename = None

        if codename and str(str(codename).replace(" ", "")):
            return codename
        else:
            return None

    @check_permission('warehouses', 'R')
    def fetchWarehouses(self, account='', warehouse_filter='all', final_account='') -> list:
        print("DATABASE> Fetch warehouses")
        if warehouse_filter == 'include_in_stock':
            query = "SELECT `warehouseslist`.`id`, `warehouseslist`.`name`, `warehouseslist`.`include_in_stock`, `warehouseslist`.`code`, `parent`.`id` as `parent_id`, `parent`.`name` as `parent_name`, `warehouseslist`.`account`, `warehouseslist`.`codename`, `warehouseslist`.`capacity` FROM `warehouseslist` LEFT JOIN `warehouseslist` AS `parent` ON `warehouseslist`.`parent_warehouse`=`parent`.`id` LEFT JOIN `accounts` ON `warehouseslist`.`account`=`accounts`.`id` WHERE IFNULL(`warehouseslist`.`account`,'0')=IFNULL(NULLIF('" + str(account) + "',''),IFNULL(`warehouseslist`.`account`,'0')) AND `warehouseslist`.`include_in_stock`='1' AND IFNULL(`accounts`.`final_account`,'0')=IFNULL(NULLIF('" + str(final_account) + "',''),IFNULL(`accounts`.`final_account`,'0')) ORDER BY `warehouseslist`.`id`, `parent_id` ASC;"
            
        elif warehouse_filter == 'not_in_stock':
            query = "SELECT `warehouseslist`.`id`, `warehouseslist`.`name`, `warehouseslist`.`include_in_stock`, `warehouseslist`.`code`, `parent`.`id` as `parent_id`, `parent`.`name` as `parent_name`, `warehouseslist`.`account`, `warehouseslist`.`codename`, `warehouseslist`.`capacity` FROM `warehouseslist` LEFT JOIN `warehouseslist` AS `parent` ON `warehouseslist`.`parent_warehouse`=`parent`.`id` LEFT JOIN `accounts` ON `warehouseslist`.`account`=`accounts`.`id` WHERE IFNULL(`warehouseslist`.`account`,'0')=IFNULL(NULLIF('" + str(account) + "',''),IFNULL(`warehouseslist`.`account`,'0')) AND `warehouseslist`.`include_in_stock`='0' AND IFNULL(`accounts`.`final_account`,'0')=IFNULL(NULLIF('" + str(final_account) + "',''),IFNULL(`accounts`.`final_account`,'0')) ORDER BY `warehouseslist`.`id`, `parent_id` ASC;"
        else:
            query = "SELECT `warehouseslist`.`id`, `warehouseslist`.`name`, `warehouseslist`.`include_in_stock`, `warehouseslist`.`code`, `parent`.`id` as `parent_id`, `parent`.`name` as `parent_name`, `warehouseslist`.`account`, `warehouseslist`.`codename`, `warehouseslist`.`capacity` FROM `warehouseslist` LEFT JOIN `warehouseslist` AS `parent` ON `warehouseslist`.`parent_warehouse`=`parent`.`id` LEFT JOIN `accounts` ON `warehouseslist`.`account`=`accounts`.`id` WHERE IFNULL(`warehouseslist`.`account`,'0')=IFNULL(NULLIF('" + str(account) + "',''),IFNULL(`warehouseslist`.`account`,'0')) AND IFNULL(`accounts`.`final_account`,'0')=IFNULL(NULLIF('" + str(final_account) + "',''),IFNULL(`accounts`.`final_account`,'0')) ORDER BY `warehouseslist`.`id`, `parent_id` ASC;"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    # @check_permission('warehouses', 'R')
    def fetchWarehousesCount(self) -> dict:
        print("DATABASE> Fetch warehouses count")
        query = "SELECT COUNT(*) FROM `warehouseslist`"
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return {'warehouses_count': rows[0]}

    def fetchWarehouse(self, id):
        print("DATABASE> fetch material #" + str(id))
        query = "SELECT `warehouseslist`.*, `accounts`.`name` as `account_name` FROM `warehouseslist` LEFT JOIN `accounts` ON `warehouseslist`.`account`=`accounts`.`id` WHERE `warehouseslist`.`id`='" + str(
            id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        # self.sqlconnector.conn.commit()
        return rows

    @check_permission('warehouses', 'W')
    def addWarehouse(self, name, code, parent, account, address, manager, capacity, capacity_unit, notes) -> None:
        # Adding a new warehouse involves two steps:
        # 1- Creating a table for the new warehouse
        # 2- Add the new warehouse info to (warehouseslist) table.

        # codename is the name of the warehouse table in database.
        codename = "warehouse." + str(name).lower()

        # create the table:
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":  # mysql database
            query = "CREATE TABLE IF NOT EXISTS `" + codename + "` (`id` INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT, `material_id` INTEGER NOT NULL, `quantity` DOUBLE NOT NULL DEFAULT 0, `unit` INTEGER, `production_batch_id` INTEGER DEFAULT NULL, `receipt_doc_id` INTEGER DEFAULT NULL, `batch_number` INTEGER DEFAULT NULL, `batch_mfg` DATE DEFAULT NULL, `batch_exp` DATE DEFAULT NULL, `material_move_id` INTEGER DEFAULT NULL, `production_date` DATE DEFAULT NULL, `expire_date` DATE DEFAULT NULL, FOREIGN KEY (`material_id`) REFERENCES materials(`id`) ON DELETE RESTRICT, FOREIGN KEY (`material_move_id`) REFERENCES material_moves(`id`) ON DELETE CASCADE) ENGINE=InnoDB"
        else:  # sqlite database
            query = "CREATE TABLE IF NOT EXISTS `" + codename + "` (`id` INTEGER PRIMARY KEY AUTOINCREMENT, `material_id` INTEGER NOT NULL, `quantity` DOUBLE NOT NULL DEFAULT 0, `unit` INTEGER, `production_batch_id` INTEGER DEFAULT NULL, `receipt_doc_id` INTEGER DEFAULT NULL, `batch_number` INTEGER DEFAULT NULL, `batch_mfg` DATE DEFAULT NULL, `batch_exp` DATE DEFAULT NULL, `material_move_id` INTEGER DEFAULT NULL, `production_date` DATE DEFAULT NULL, `expire_date` DATE DEFAULT NULL, FOREIGN KEY (`material_id`) REFERENCES materials(`id`) ON DELETE RESTRICT, FOREIGN KEY (`material_move_id`) REFERENCES material_moves(`id`) ON DELETE CASCADE)"

        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

        # make sure the table is renamed:
        table_created = False
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":  # mysql database
            query = "SHOW TABLES LIKE '" + codename + "'"
            self.cursor.execute(query)
            try:
                rows = self.cursor.fetchall()
                self.sqlconnector.conn.commit()
                if len(rows) > 0:
                    table_created = True
            except:
                pass

        else:  # sqlite database
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + codename + "'"
            self.cursor.execute(query)
            try:
                rows = self.cursor.fetchall()
                self.sqlconnector.conn.commit()
                if len(rows) > 0:
                    table_created = True
            except:
                pass

        # If the table is successfully created, insert a record into warehouseslist table
        if table_created:
            if str(parent).lower() == 'none':
                parent = ''
            if str(account).lower() == 'none':
                account = ''
            if str(address).lower() == 'none':
                address = ''
            if str(manager).lower() == 'none':
                manager = ''
            if str(capacity).lower() == 'none':
                capacity = ''
            if str(notes).lower() == 'none':
                notes = ''

            query = "INSERT INTO `warehouseslist` (`code`, `name`, `codename`, `parent_warehouse`, `account`, `address`, `manager`, `notes`, `capacity`, `capacity_unit`) VALUES ('" + str(
                code) + "', '" + str(name) + "', '" + str(codename) + "', NULLIF('" + str(
                parent) + "',''), NULLIF('" + str(
                account) + "',''), NULLIF('" + str(address) + "',''), NULLIF('" + str(
                manager) + "',''), NULLIF('" + str(
                notes) + "', ''), NULLIF('" + str(capacity) + "',''), NULLIF('" + str(capacity_unit) + "',''))"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    @check_permission('warehouses', 'W')
    def updateWarehouse(self, id, name, code, include_in_stock, address, manager, capacity, capacity_unit, notes, parent, account) -> None:
        print("DATABASE> Update warehouse #" + str(code))

        new_codename = "warehouse." + str(name).lower()

        include_in_stock = 1 if include_in_stock else 0

        # fetch old codename
        query = "SELECT `codename` FROM `warehouseslist` WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        old_codename = rows[0][0]

        if old_codename != new_codename:
            # Rename the warehouse table in the database
            query = "ALTER TABLE `" + str(old_codename) + "` RENAME TO `" + str(new_codename) + "`"
            print(query)
            self.cursor.execute(query)
        self.sqlconnector.conn.commit()

        # make sure the table is renamed:
        table_created = False
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":  # mysql database
            query = "SHOW TABLES LIKE '" + new_codename + "'"
            self.cursor.execute(query)
            try:
                rows = self.cursor.fetchall()
                self.sqlconnector.conn.commit()
                if len(rows) > 0:
                    table_created = True
            except Exception as e:
                print("Warehouse table not found." + str(e))

        else:  # sqlite database
            query = "SELECT name FROM sqlite_master WHERE type='table' AND name='" + new_codename + "'"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            try:
                rows = self.cursor.fetchall()
                self.sqlconnector.conn.commit()
                if len(rows) > 0:
                    table_created = True
            except Exception as e:
                print("Warehouse table not found." + str(e))

        # If the table is successfully renamed, update its record into warehouseslist table
        if table_created:
            query = "UPDATE `warehouseslist` SET `code`=NULLIF('" + str(code) + "',''), `name`=NULLIF('" + str(
                name) + "',''), `codename`=NULLIF('" + str(
                new_codename) + "',''), `parent_warehouse`=NULLIF('" + str(parent) + "',''), `account`=NULLIF('" + str(
                account) + "',''), `address`=NULLIF('" + str(address) + "',''), `manager`=NULLIF('" + str(
                manager) + "',''), `capacity`=NULLIF('" + str(capacity) + "',''), `capacity_unit`=NULLIF('" + str(
                capacity_unit) + "',''), `include_in_stock`=NULLIF('" + str(include_in_stock) + "',''), `notes`=NULLIF('" + str(notes) + "','') WHERE `id`='" + str(id) + "'"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    @check_permission('warehouses', 'W')
    def addMaterialToWarehouse(self, warehouse_id, material_id, quantity, unit, production_batch_id='', production_date='', expire_date='', material_move_id='', commit=True) -> int:
        # fetch warehouse codename
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "INSERT INTO `" + str(codename) + "` (`material_id`, `quantity`, `unit`, `production_batch_id`, `material_move_id`, `production_date`, `expire_date`) VALUES ('" + str( material_id) + "', '" + str(quantity) + "','" + str(unit) + "', NULLIF ('" + str(production_batch_id) + "',''), NULLIF('" + str(material_move_id) + "',''), NULLIF ('" + str(production_date) + "',''), NULLIF ('" + str(expire_date) + "',''))"

            print(query)
            self.cursor.execute(query)
            inserted_id = self.cursor.lastrowid
            if commit:
                self.sqlconnector.conn.commit()
            return inserted_id

    @check_permission('warehouses', 'W')
    def removeMaterialFromWarehouse(self, warehouse_entry_id, warehouse_id) -> None:
        print("DELETE FROM Warehouse #" + str(warehouse_id) + " Entry #" + str(warehouse_entry_id))
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "DELETE FROM `" + str(codename) + "` WHERE `id`='" + str(warehouse_entry_id) + "'"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    # This function reduces the quantity of a material in a warehouse. It handles unit conversion if necessary.
    # It iterates through the records of the material in the warehouse and reduces the quantity accordingly.
    @check_permission('warehouses', 'W')
    def reduceMaterialInWarehouse(self, warehouse_id, material_id, quantity, unit_id, entry_id_to_reduce_from=None, order='desc', commit=True) -> list:
        modified_records = []
        warehouse_codename = self.fetchWarehouseCodename(warehouse_id)

        if warehouse_codename:
            if order == 'FIFO':
                order = '`id` ASC'
            elif order == 'LIFO':
                order = '`id` DESC'
            elif order == 'expire_date_desc':
                order = '`expire_date` DESC'
            elif order == 'expire_date_asc':
                order = '`expire_date` ASC'
            elif order == 'production_date_desc':
                order = '`production_date` DESC'
            elif order == 'production_date_asc':
                order = '`production_date` ASC'
            else:
                order = '`id` ASC'

            if entry_id_to_reduce_from is not None:
                query = f"SELECT * FROM `{warehouse_codename}` WHERE `id`='{entry_id_to_reduce_from}'"
            else:
                query = f"SELECT * FROM `{warehouse_codename}` WHERE `material_id`='{material_id}' ORDER BY {order}"
            
            self.cursor.execute(query)
            records = self.cursor.fetchall()

            quantity_to_reduce = quantity
            for record in records:
                if quantity_to_reduce <= 0:
                    break
                record_id = record['id']
                record_quantity = record['quantity']
                record_unit_id = record['unit']

                if str(record_unit_id) != unit_id:
                    # Convert record quantity to required unit using fetchUnitConversionValueBetween
                    conversion_rate = self.fetchUnitConversionValueBetween(record_unit_id, unit_id)
                    converted_quantity = record_quantity * conversion_rate

                    # Convert quantity_to_reduce to record's unit
                    reduce_quantity = quantity_to_reduce / conversion_rate

                    reduced_quantity = 0
                    if record_quantity <= reduce_quantity:
                        # Record has less quantity than needed, zero it out
                        new_quantity = 0
                        quantity_to_reduce -= converted_quantity
                        reduced_quantity = record_quantity
                    else:
                        # Record has enough quantity, reduce by full amount needed
                        new_quantity = record_quantity - reduce_quantity
                        reduced_quantity = reduce_quantity
                        quantity_to_reduce = 0

                    new_quantity = round(new_quantity, 2)
                    reduced_quantity = round(reduced_quantity, 2)

                    query = f"UPDATE `{warehouse_codename}` SET `quantity`='{new_quantity}' WHERE `id`='{record_id}'"
                    self.cursor.execute(query)
                    if commit:
                        self.sqlconnector.conn.commit()
                    if reduced_quantity > 0:
                        modified_records.append({
                            'id': record_id,
                            'reduced_quantity': reduced_quantity,
                            'unit': record_unit_id
                        })

                else:
                    try:
                        record_quantity = float(record_quantity)
                        quantity_to_reduce = float(quantity_to_reduce)
                    except ValueError:
                        print("Error: Unable to cast record_quantity or quantity to float.")
                        return modified_records

                    reduced_quantity = 0
                    if record_quantity <= quantity_to_reduce:
                        # Record has less quantity than needed, zero it out
                        new_quantity = 0
                        quantity_to_reduce -= record_quantity
                        reduced_quantity = record_quantity
                    else:
                        # Record has enough quantity, reduce by full amount needed
                        new_quantity = record_quantity - quantity_to_reduce
                        reduced_quantity = quantity_to_reduce
                        quantity_to_reduce = 0

                    new_quantity = round(new_quantity, 2)
                    reduced_quantity = round(reduced_quantity, 2)

                    query = f"UPDATE `{warehouse_codename}` SET `quantity`='{new_quantity}' WHERE `id`='{record_id}'"
                    self.cursor.execute(query)
                    if commit:
                        self.sqlconnector.conn.commit()
                    if reduced_quantity > 0:
                        modified_records.append({
                            'id': record_id,
                            'reduced_quantity': reduced_quantity,
                            'unit': record_unit_id
                        })

        return modified_records


    # This function updates the quantity and unit of a material entry in a warehouse based on the warehouse entry ID and warehouse ID.
    # It is used to modify the existing record of a material in the warehouse.
    @check_permission('warehouses', 'W')
    def updateMaterialInWarehouse (self, warehouse_entry_id, warehouse_id, quantity, unit) -> None:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "UPDATE `" + str(codename) + "` SET `quantity`='" + str(quantity) + "', `unit`=NULLIF('" + str(
                unit) + "','') WHERE `id`='" + str(warehouse_entry_id) + "'"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()


    @check_permission('warehouses', 'W')
    def updateWarehouseEntryQuantity(self, warehouse_id, warehouse_entry_id, quantity, updating_type) -> None:
        warehouse_codename = self.fetchWarehouseCodename(warehouse_id)
        if warehouse_codename:
            warehouse_entry = self.fetchWarehouseEntry(warehouse_entry_id, warehouse_id)
            warehouse_entry_quantity = warehouse_entry['quantity']
            if updating_type == 'add':
                new_quantity = warehouse_entry_quantity + quantity
                query = "UPDATE `" + str(warehouse_codename) + "` SET `quantity`='" + str(new_quantity) + "' WHERE `id`='" + str(warehouse_entry_id) + "'"
            elif updating_type == 'reduce':
                new_quantity = warehouse_entry_quantity - quantity
                query = "UPDATE `" + str(warehouse_codename) + "` SET `quantity`='" + str(new_quantity) + "' WHERE `id`='" + str(warehouse_entry_id) + "'"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    @check_permission('warehouses', 'R')
    def fetchWarehouseMaterials(self, warehouse_id) -> list:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "SELECT `" + str(codename) + "`.*, `materials`.`code`, `materials`.`name` as `material_name`, `units`.`name` as `unit_name`, `" + str(codename) + "`.`production_date`, `" + str(codename) + "`.`expire_date` FROM `" + str(codename) + "` JOIN `materials` ON `" + str(codename) + "`.`material_id`=`materials`.`id` JOIN `units` ON `units`.`id` = `" + str(codename) + "`.`unit` ORDER BY `id` ASC"
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.sqlconnector.conn.commit()
            return rows

    @check_permission('warehouses', 'R')
    def fetchMaterialWarehouses(self, material_id, material_source='all', sort='asc') -> dict:  # return the warehouses that contains a specific material, along with the quantity in each warehouse
        # material_source specifies whether the material came to the warehouse from an invoice or from a manufacture process

        result = {}  # warehouse_id:quantity
        warehouses = self.fetchWarehouses(warehouse_filter='include_in_stock')  # get a list of warehouses
        for warehouse in warehouses:
            warehouse_id = warehouse['id']
            warehouse_name = warehouse['name']
            warehouse_code = warehouse['code']
            warehouse_parent_id = warehouse['parent_id']
            warehouse_parent_name = warehouse['parent_name']
            warehouse_account_id = warehouse['account']
            warehouse_include_in_stock = warehouse['include_in_stock']
            warehouse_codename = warehouse['codename']

            # Build the query dynamically based on the source value
            if material_source == 'all':
                query = "SELECT `" + str(
                    warehouse_codename) + "`.*, `invoices`.`id` AS `invoice_id`, `invoices`.`date_col` AS `invoice_date`, `manufacture`.`date_col` AS `manufacture_date`, `invoice_items`.`id` as `invoice_item_id` FROM `" + str(
                    warehouse_codename) + "` LEFT JOIN `material_moves` ON `material_moves`.`id`=`" + str(
                    warehouse_codename) + "`.`material_move_id` LEFT JOIN `invoice_items` ON (`material_moves`.`origin`='invoice' AND `invoice_items`.`id`=`material_moves`.`origin_id`) LEFT JOIN `invoices` ON `invoices`.`id`=`invoice_items`.`invoice_id` LEFT JOIN `manufacture` ON `" + str(
                    warehouse_codename) + "`.`production_batch_id`=`manufacture`.`id` WHERE `" + str(
                    warehouse_codename) + "`.`material_id`='" + str(
                    material_id) + "' ORDER BY `invoice_date`,`manufacture_date` " + str(sort)

            elif material_source == 'invoice':
                query = "SELECT `" + str(
                    warehouse_codename) + "`.*, `invoices`.`id` AS `invoice_id`, `invoices`.`date_col` AS `invoice_date`, `invoice_items`.`id` as `invoice_item_id`, NULL AS `manufacture_date` FROM `" + str(
                    warehouse_codename) + "` JOIN `material_moves` ON `material_moves`.`id`=`" + str(
                    warehouse_codename) + "`.`material_move_id` JOIN `invoice_items` ON `invoice_items`.`id`=`material_moves`.`origin_id` JOIN `invoices` ON `invoices`.`id`=`invoice_items`.`invoice_id` WHERE `" + str(
                    warehouse_codename) + "`.`material_id`='" + str(
                    material_id) + "' AND `material_moves`.`origin`='invoice' ORDER BY `invoice_date` " + str(sort)

            elif material_source == 'manufacture':
                query = "SELECT `" + str(
                    warehouse_codename) + "`.*, NULL AS `invoice_id`, NULL AS  `invoice_date`, `manufacture`.`date_col` AS `manufacture_date` FROM `" + str(
                    warehouse_codename) + "` JOIN `manufacture` ON `" + str(
                    warehouse_codename) + "`.`production_batch_id`=`manufacture`.`id` WHERE `" + str(
                    warehouse_codename) + "`.`material_id`='" + str(
                    material_id) + "' ORDER BY `manufacture_date` " + str(sort)

            else:
                print("Invalid source value.")
                return

            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                max_numeric_index = max([key for key in row.keys() if isinstance(key, int)], default=-1)
                row[max_numeric_index + 1] = warehouse_name
                row['warehouse_name'] = warehouse_name
                row[max_numeric_index + 2] = warehouse_account_id
                row['warehouse_account_id'] = warehouse_account_id
                if warehouse_id not in result:
                    result[warehouse_id] = []
                result[warehouse_id].append(row)
        return result

    @check_permission('warehouses', 'R')
    def fetchInvoiceItemWarehouse(self, material_move_id) -> tuple:  # return the warehouses that contains an invoice item, along with the quantity that is left of it and info of the warehouse

        result = ()  # warehouse_id:quantity
        warehouses = self.fetchWarehouses()  # get a list of warehouses
        found = False
        for warehouse in warehouses:
            warehouse_id = warehouse[0]
            warehouse_name = warehouse[1]
            warehouse_code = warehouse[2]
            warehouse_parent_id = warehouse[3]
            warehouse_parent_name = warehouse[4]
            warehouse_account_id = warehouse[5]
            warehouse_codename = warehouse[6]

            query = "SELECT `id`, `quantity`, `unit` FROM `" + str(
                warehouse_codename) + "` WHERE `material_move_id` = '" + str(material_move_id) + "'"
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            for row in rows:
                result = (row['quantity'], row['unit'], warehouse_id, warehouse_name, warehouse_account_id, row['id'])
                found = True
                break
            if found:
                break

        return result

    @check_permission('warehouses', 'R')
    def fetchWarehouseEntry(self, warehouse_entry_id, warehouse_id) -> dict:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "SELECT `" + str(codename) + "`.*, `materials`.`code`, `materials`.`name` FROM `" + str(
                codename) + "` JOIN `materials` ON `" + str(
                codename) + "`.`material_id`=`materials`.`id` WHERE `" + str(codename) + "`.`id`='" + str(
                warehouse_entry_id) + "'"
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows[0]

    @check_permission('warehouses', 'R')
    def fetchWarehouseEntryByMaterialMoveId(self, material_move_id, warehouse_id) -> dict:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "SELECT `" + str(codename) + "`.*, `materials`.`code`, `materials`.`name` FROM `" + str(
                codename) + "` JOIN `materials` ON `" + str(
                codename) + "`.`material_id`=`materials`.`id` WHERE `" + str(codename) + "`.`material_move_id`='" + str(material_move_id) + "'"
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            if rows:
                return rows[0]
            else:
                return None


    @check_permission('warehouses', 'R')
    def fetchWarehouseMaterial(self, warehouse_id, material_id) -> list:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "SELECT `" + str(codename) + "`.*, `materials`.`code`, `materials`.`name` FROM `" + str(
                codename) + "` JOIN `materials` ON `" + str(
                codename) + "`.`material_id`=`materials`.`id` WHERE `" + str(codename) + "`.`material_id`='" + str(
                material_id) + "'"
            print(query)
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows


    @check_permission('warehouses', 'W')
    def removeWarehouse(self, warehouse_id) -> None:
        codename = self.fetchWarehouseCodename(warehouse_id)

        query = "DELETE FROM `warehouseslist` WHERE `id`='" + str(warehouse_id) + "'"
        print(query)
        self.cursor.execute(query)

        if codename:
            query = "DROP TABLE `" + str(codename) + "`"
            self.cursor.execute(query)

        self.sqlconnector.conn.commit()

    @check_permission('warehouses', 'W')
    def removeWarehouseEntry(self, warehouse_id, warehouse_entry_id, commit=True) -> None:
        codename = self.fetchWarehouseCodename(warehouse_id)
        if codename:
            query = "DELETE FROM `" + str(codename) + "` WHERE `id`='" + str(warehouse_entry_id) + "'"
            self.cursor.execute(query)
            if commit:
                self.sqlconnector.conn.commit()

    @check_permission('prices', 'R')
    def fetchPricesTypes(self) -> list:
        print("Fetch prices types.")
        query = "SELECT * FROM `prices`"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('clients', 'W')
    def addClientAccount(self, used_price, discount, payment_method, days_count, day,payment_date, client_account_id, discount_account_id, tax_account_id,vat_account_id, tax_exemption, client_id, extra_account_id) -> int:
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "INSERT INTO `clients_accounts`(`used_price`, `discount`, `payment_method`, `days_count`, `day_col`, `payment_date`, `client_account_id`, `discount_account_id`, `tax_account_id`, `vat_account_id`, `tax_exempt`, `client_id`, `extra_account_id`) VALUES (NULLIF('" + str(used_price) + "', ''), NULLIF('" + str(discount) + "', ''), NULLIF('" + str(payment_method) + "', ''), NULLIF('" + str(days_count) + "', ''), NULLIF('" + str(day) + "', ''), NULLIF('" + str(payment_date) + "', ''), NULLIF('" + str(client_account_id) + "', ''), NULLIF('" + str(discount_account_id) + "', ''), NULLIF('" + str(tax_account_id) + "', ''), NULLIF('" + str(vat_account_id) + "', ''), NULLIF('" + str(tax_exemption) + "', ''), " + (str(client_id) if client_id else 'NULL') + ", " + (str(extra_account_id) if extra_account_id else 'NULL') + ") ON DUPLICATE KEY UPDATE `used_price`=NULLIF('" + str(used_price) + "', ''), `discount`=NULLIF('" + str(discount) + "', ''), `payment_method`=NULLIF('" + str(payment_method) + "', ''), `days_count`=NULLIF('" + str(days_count) + "', ''), `day_col`=NULLIF('" + str(day) + "', ''), `payment_date`=NULLIF('" + str(payment_date) + "', ''), `client_account_id`=NULLIF('" + str(client_account_id) + "', ''), `discount_account_id`=NULLIF('" + str(discount_account_id) + "', ''), `tax_account_id`=NULLIF('" + str(tax_account_id) + "', ''), `vat_account_id`=NULLIF('" + str(vat_account_id) + "', ''), `tax_exempt`=NULLIF('" + str(tax_exemption) + "', ''), `extra_account_id`=NULLIF('" + str(extra_account_id) + "', '');"
        else:
            query = "INSERT OR REPLACE INTO `clients_accounts`(`used_price`, `discount`, `payment_method`, `days_count`, `day_col`, `payment_date`, `client_account_id`, `discount_account_id`, `tax_account_id`, `vat_account_id`, `tax_exempt`, `client_id`, `extra_account_id`) VALUES (NULLIF('" + str(used_price) + "', ''), NULLIF('" + str(discount) + "', ''), NULLIF('" + str(payment_method) + "', ''), NULLIF('" + str(days_count) + "', ''), NULLIF('" + str(day) + "', ''), NULLIF('" + str(payment_date) + "', ''), NULLIF('" + str(client_account_id) + "', ''), NULLIF('" + str(discount_account_id) + "', ''), NULLIF('" + str(tax_account_id) + "', ''), NULLIF('" + str(vat_account_id) + "', ''), NULLIF('" + str(tax_exemption) + "', ''), " + (str(client_id) if client_id else 'NULL') + ", " + (str(extra_account_id) if extra_account_id else 'NULL') + ");"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        result = None
        if last_id:
            result = last_id
        return result


    def addPaymentCondition(self, client_account_id, day_number, discount_percent, discount_value,condition_discount_account):

        query = "INSERT INTO `payment_conditions`(`client_account_id`, `day_number`, `discount_percent`, `discount_value`, `discount_account_id`) VALUES ('" + str(client_account_id) + "','" + str(day_number) + "',NULLIF('" + str(discount_percent) + "',''),NULLIF('" + str(discount_value) + "',''),NULLIF('" + str(condition_discount_account) + "',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchPaymentConditions(self, client_account_id):
        query = "SELECT IFNULL(`accounts`.`name`,''),`payment_conditions`.`id`, `payment_conditions`.`client_account_id`, `payment_conditions`.`day_number`, IFNULL(`payment_conditions`.`discount_percent`,''), IFNULL(`payment_conditions`.`discount_value`,''), `payment_conditions`.`discount_account_id` FROM `payment_conditions` LEFT JOIN `accounts` ON `payment_conditions`.`discount_account_id`=`accounts`.`id` WHERE `client_account_id`='" + str(client_account_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def removePaymenCondition(self, payment_condition_id):
        query = "DELETE FROM `payment_conditions` WHERE `id`='" + str(payment_condition_id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('prices', 'R')
    def fetchPrices(self) -> list:
        query = "SELECT * FROM `prices`"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    @check_permission('prices', 'W')
    def fetchPrice(self, price_id) -> dict:
        query = "SELECT * FROM `prices` WHERE `id`='" + str(price_id) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row

    @check_permission('prices', 'W')
    def addPrice(self, name) -> None:
        if not self.checkIfRowExist('prices', 'price', name):
            query = "INSERT INTO `prices` (`price`) VALUES ('" + str(name) + "')";
            # print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    @check_permission('prices', 'W')
    def deletePrice(self, id) -> None:
        query = "DELETE FROM `prices` WHERE `id`='" + str(id) + "' and `locked`='0'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('prices', 'W')
    def updatePrice(self, id, name) -> None:
        query = "UPDATE `prices` SET `price`='" + str(name) + "' WHERE `id`='" + str(id) + "' and `locked`='0'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('units', 'W')
    def addUnit(self, text) -> None:
        query = "INSERT INTO `units`(`name`) VALUES ('" + str(text) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('units', 'R')
    def fetchUnits(self) -> list:
        query = "SELECT * FROM `units`"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('units', 'R')
    def fetchUnitByName(self, name) -> dict:
        if name:
            query = "SELECT * FROM `units` WHERE `name` = '" + str(name) + "'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows[0]
        else:
            pass

    @check_permission('units', 'R')
    def fetchUnit(self, id) -> dict:
        if id:
            query = "SELECT * FROM `units` WHERE `id`='" + str(id) + "'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            return rows[0]
        else:
            return None

    @check_permission('units', 'R')
    def fetchUnitConversionValues(self, unit_id) -> dict:
        return self.fetchUnitConversionValueBetween(unit_id, None)

    @check_permission('units', 'R')
    def fetchUnitConversionValueBetween(self, unit1_id, unit2_id=None) -> float:
        print("DATABASE> Fetch exchange value between " + str(unit1_id) + " and " + str(unit2_id))
        unit1_id = int(unit1_id)
        unit2_id = int(unit2_id) if unit2_id is not None else None

        def buildAdjacenyList(connection_pairs):
            connections_dict = {}
            for connection in connection_pairs:
                if connection[0] not in connections_dict:
                    connections_dict[connection[0]] = []
                connections_dict[connection[0]].append(connection[1])

                if connection[1] not in connections_dict:
                    connections_dict[connection[1]] = []
                connections_dict[connection[1]].append(connection[0])
            return connections_dict

        def bfs(graph, start: int, end: int = None):
            if start not in graph:  # Check if graph contains start value
                return {}  # Return empty dictionary if start value not found in graph
            queue = [start]
            visited = {start: None}  # Keep track of visited nodes and their parents
            while queue:
                current_unit = queue.pop(0)
                if end is not None and current_unit == end:
                    return visited
                for neighbor in graph[current_unit]:
                    if neighbor not in visited:
                        queue.append(neighbor)
                        visited[neighbor] = current_unit
            return visited  # Return the visited dictionary

        # get all units conversions
        query = "SELECT * FROM `units_conversion`"
        self.cursor.execute(query)
        all_conversion_data = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        all_conversion_pairs = []
        for row in all_conversion_data:
            all_conversion_pairs.append([int(row[1]), int(row[2])])
        graph = buildAdjacenyList(all_conversion_pairs)
        if unit2_id is not None:
            # Fetch exchange value between the given units
            path = bfs(graph, unit1_id, unit2_id)
            if unit2_id not in path:
                return None  # No conversion path found
            multiplication_sequence = []
            current_unit = unit2_id
            while current_unit is not None:
                parent_unit = path[current_unit]
                for row in all_conversion_data:
                    if row[1] == parent_unit and row[2] == current_unit:
                        multiplication_sequence.append(row[3])
                        break
                    elif row[1] == current_unit and row[2] == parent_unit:
                        multiplication_sequence.append(1 / row[3])
                        break
                current_unit = parent_unit
            conversion_rate = 1
            for num in multiplication_sequence:
                conversion_rate *= num
            return conversion_rate
        else:
            # Return all conversion values of the given unit
            visited = bfs(graph, unit1_id)
            conversion_values = {}
            for unit, parent_unit in visited.items():
                if parent_unit is not None:
                    conversion_factor = 1  # Initialize conversion factor
                    current_unit = unit
                    while current_unit is not None:
                        parent_unit = visited[current_unit]
                        for row in all_conversion_data:
                            if row[1] == parent_unit and row[2] == current_unit:
                                conversion_factor *= row[3]  # Multiply conversion factors
                                break
                            elif row[1] == current_unit and row[2] == parent_unit:
                                conversion_factor *= 1 / row[3]  # Invert and multiply conversion factors
                                break
                        current_unit = parent_unit
                    conversion_values[unit] = conversion_factor

            updated_conversion_values = {}
            for unit_id, conversion_factor in list(conversion_values.items()):
                unit_data = self.fetchUnit(unit_id)  # Get unit name using the provided function
                if unit_data:
                    unit_name = unit_data[1]
                    conversion_exists = False
                    for row in all_conversion_data:
                        if (row[1] == unit1_id) and (row[2] == unit_id):  # Conversion value is already exists
                            conversion_id = row[0]
                            updated_conversion_values[(conversion_id, unit_id, unit_name)] = conversion_factor
                            conversion_exists = True
                            break
                    if not conversion_exists:  # Conversion value has been calculated
                        updated_conversion_values[(None, unit_id, unit_name)] = conversion_factor

            conversion_values.update(updated_conversion_values)

            return updated_conversion_values

    @check_permission('units', 'W')
    def addUnitsConversionValue(self, unit1_id, unit2_id, conversion_value) -> None:
        query = "REPLACE INTO `units_conversion` (`unit1`, `unit2`, `value_col`) VALUES ('" + str(
            unit1_id) + "','" + str(
            unit2_id) + "','" + str(conversion_value) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('units', 'W')
    def removeUnit(self, id) -> None:
        query = "DELETE FROM `units` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('units', 'W')
    def removeUnitConversion(self, id) -> None:
        query = "DELETE FROM `units_conversion` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('cost_centers', 'R')
    def fetchCostCenters(self, cost_center_type=0) -> list:
        print("Fetch Cost Centers")

        if type(cost_center_type) is list:
            types_range = ",".join(f"'{item}'" for item in cost_center_type)
        elif type(cost_center_type) is str:
            types_range = "'" + cost_center_type + "'"
        else:
            types_range = False

        query = "SELECT * FROM `cost_centers`"

        if types_range:
            query += " WHERE `type_col` IN (" + str(types_range) + ")"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    @check_permission('cost_centers', 'R')
    def fetchCostCentersCount(self) -> dict:
        print("DATABASE> Fetch cost centers count")
        query = """
                SELECT
                    COUNT(*) AS cost_center_count
                FROM `cost_centers`
                GROUP BY type_col;
                """
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('cost_centers', 'W')
    def deleteCostCenter(self,id) -> bool:
        print("DATABASE> Delete cost_center")
        query = f"DELETE FROM `cost_centers` WHERE `id` = '{id}'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        if self.cursor.rowcount > 0:
            return True  # Cost Center was successfully deleted
        else:
            return False  # No records were deleted

    @check_permission('cost_centers', 'W')
    def addCostCenter(self, name, notes, type, parent) -> None:
        if not parent:
            parent = ""
        query = "INSERT INTO `cost_centers` (name, notes, type_col, parent) VALUES ('" + str(
            name) + "', NULLIF('" + str(
            notes) + "','') ,'" + str(
            type) + "', NULLIF('" + str(parent) + "',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('cost_centers', 'R')
    def fetchCostCenter(self, id) -> dict:
        print("DATABASE> fetch cost center #" + str(id))
        query = "SELECT * FROM `cost_centers` WHERE `id`='" + str(id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows[0]

    @check_permission('cost_centers', 'R')
    def fetchDescendantCostCenters(self, parent_id) -> list:
        # Yield functions accumulates results and finally returns a (generator) object, which can be converted into a list.
        print("DATABASE> Fetch descendant cost centers of #" + str(parent_id))
        query = "SELECT * FROM `cost_centers` WHERE `parent` = '" + str(parent_id) + "' ORDER BY `date_col` ASC"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        for row in rows:
            yield row  # Return (Row) and continue execution.
            child_id = row[0]
            yield from self.fetchChildAccounts(child_id)  # This is similar to
            # for child in self.fetchChildAccounts(child_id):
            #      yield(child)
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('cost_centers', 'W')
    def updateCostCenter(self, id, name, notes, type, parent) -> None:
        print("DATABASE> Update cost center #" + str(id))
        # get descendats to check later for infinity loops and prevent them.
        descendants = [descendant[0] for descendant in list(self.fetchDescendantCostCenters(id))]

        # get old parent
        old_parent_id = self.fetchCostCenter(id)[4]

        if not parent:
            parent = ''

        if (parent == '') or (parent and self.checkIfRowExist('cost_centers', 'id', parent)):
            query = "UPDATE `cost_centers` SET `name`='" + str(name) + "', `notes`=NULLIF('" + str(
                notes) + "',''), `type_col`='" + str(type) + "', `parent`=NULLIF('" + str(
                parent) + "','') WHERE `id`='" + str(id) + "'"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            if parent in descendants:
                query = "UPDATE `cost_centers` SET `parent`='" + str(old_parent_id) + "' WHERE `id`='" + str(
                    parent) + "'"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()

            self.recalculateAccountsCodes()

        else:
            print("Error - Parent account doesn't exist.")


    @check_permission('cost_centers', 'W')
    def addAggregationDistributiveCostCenter(self, cost_center_id, cost_center, division_factor) -> None:
        print("DATABASE> Add Aggregation/Distributive Cost Center To Cost Center #" + str(cost_center_id))
        query = "REPLACE INTO `cost_centers_aggregations_distributives` (`master_cost_center`, `cost_center`, `division_factor`) VALUES ('" + str(
            cost_center_id) + "','" + str(cost_center) + "',NULLIF('" + str(division_factor) + "',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('cost_centers', 'R')
    def fetchCostCenterAggregationsDistributives(self, id, check_for_modified_values=False, journal_entry_item_id=None) -> list:
        print("DATABASE> Fetch Aggregation/Distributive Cost Centers of Cost Center #" + str(id))
        # check_for_modified_values checks if there are any modified values for the distributive cost center in `journal_entries_items_distributive_cost_center_values` table. To do so, there must be a Journal Entry Item ID provided. Because the modified values should be linked with a journal entry item.
        # use the modified values.
        if not check_for_modified_values:
            query = "SELECT `cost_centers_aggregations_distributives`.*, `cost_centers`.`name` FROM `cost_centers_aggregations_distributives` JOIN `cost_centers` ON `cost_centers_aggregations_distributives`.`cost_center`=`cost_centers`.`id` WHERE `cost_centers_aggregations_distributives`.`master_cost_center`='" + str(
                id) + "'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            self.sqlconnector.conn.commit()
            return rows
        else:
            # the master cost center must be of type (distributed)
            query = "SELECT `type_col` FROM `cost_centers` WHERE `id`='" + str(id) + "'"
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            if rows and journal_entry_item_id:
                type = rows[0][0]
                if str(type).lower() == 'distributor':  # remove after translation
                    query = "SELECT `cost_centers_aggregations_distributives`.`id`, `cost_centers_aggregations_distributives`.`master_cost_center`,`cost_centers_aggregations_distributives`.`cost_center`,`journal_entries_items_distributive_cost_center_values`.`percentage`, `cost_centers`.`name` FROM `journal_entries_items_distributive_cost_center_values` JOIN `cost_centers_aggregations_distributives` ON `cost_centers_aggregations_distributives`.`id` = `journal_entries_items_distributive_cost_center_values`.`cost_centers_aggregations_distributives_id` JOIN `cost_centers` ON `cost_centers`.`id` = `cost_centers_aggregations_distributives`.`master_cost_center`  WHERE `cost_centers_aggregations_distributives`.`master_cost_center`='" + str(
                        id) + "' AND `journal_entries_items_distributive_cost_center_values`.`journal_entry_item_id`='" + str(
                        journal_entry_item_id) + "'"
                    print(query)
                    self.cursor.execute(query)
                    rows = self.cursor.fetchall()
                    if rows:
                        return rows
                    else:
                        query = "SELECT `cost_centers_aggregations_distributives`.*, `cost_centers`.`name` FROM `cost_centers_aggregations_distributives` JOIN `cost_centers` ON `cost_centers_aggregations_distributives`.`cost_center`=`cost_centers`.`id` WHERE `cost_centers_aggregations_distributives`.`master_cost_center`='" + str(
                            id) + "'"

                        self.cursor.execute(query)
                        rows = self.cursor.fetchall()
                        self.sqlconnector.conn.commit()
                        return rows

    @check_permission('cost_centers', 'W')
    def updateCostCenterChangableDivisionFactorState(self, id, state) -> None:
        print("DATABASE> Update Changable Division Factors State on Cost Center #" + str(id))
        query = "UPDATE `cost_centers` SET `changable_division_factors` = '" + str(int(state)) + "' WHERE `id`='" + str(
            id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def updateMaterial(self, material_id, code, name, specs, size, manufacturer, color, origin, quality, model, unit1,
                       unit2, unit3, default_unit, current_quantity, max_quantity, min_quantity, request_limit, gift,
                       gift_for, price1_desc, price1_1, price1_2, price1_3, price2_desc, price2_1, price2_2, price2_3,
                       price3_desc, price3_1, price3_2, price3_3, price4_desc, price4_1, price4_2, price4_3,
                       price5_desc, price5_1, price5_2, price5_3, price6_desc, price6_1, price6_2, price6_3, expiray,
                       group, price1_1_unit, price2_1_unit, price3_1_unit, price4_1_unit, price5_1_unit, price6_1_unit,
                       price1_2_unit, price2_2_unit, price3_2_unit, price4_2_unit, price5_2_unit, price6_2_unit,
                       price1_3_unit, price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit, price6_3_unit,
                       material_type, groupped, standard_unit1_quantity_input, standard_unit2_quantity_input,
                       standard_unit3_quantity_input, standard_work_hours_input, yearly_required_input,
                       manufacture_hall, material_discount_account, material_addition_account):

        print("DATABASE> Update material #" + str(material_id))
        # if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
        query = "UPDATE `materials` SET `code`='" + str(code) + "', `name`='" + str(
            name) + "', `group_col`=NULLIF('" + str(
            group) + "',''), `specs`=NULLIF('" + str(specs) + "',''), `size_col`=NULLIF('" + str(
            size) + "',''), `manufacturer`=NULLIF('" + str(manufacturer) + "',''), `color`=NULLIF('" + str(
            color) + "',''), `origin`=NULLIF('" + str(origin) + "',''), `quality`=NULLIF('" + str(
            quality) + "',''), `model`=NULLIF('" + str(model) + "',''), `unit1`=NULLIF('" + str(
            unit1) + "',''), `unit2`=NULLIF('" + str(unit2) + "',''), `unit3`=NULLIF('" + str(
            unit3) + "',''), `default_unit`='" + str(default_unit) + "', `current_quantity`=NULLIF('" + str(
            current_quantity) + "',''), `max_quantity`=NULLIF('" + str(
            max_quantity) + "',''), `min_quantity`=NULLIF('" + str(
            min_quantity) + "',''), `request_limit`=NULLIF('" + str(request_limit) + "',''), `gift`=NULLIF('" + str(
            gift) + "',''), `gift_for`=NULLIF('" + str(gift_for) + "',''), `price1_desc`=NULLIF('" + str(
            price1_desc) + "',''), `price1_1`=NULLIF('" + str(price1_1) + "',''), `price1_2`=NULLIF('" + str(
            price1_2) + "',''), `price1_3`=NULLIF('" + str(price1_3) + "',''), `price2_desc`=NULLIF('" + str(
            price2_desc) + "',''), `price2_1`=NULLIF('" + str(price2_1) + "',''), `price2_2`=NULLIF('" + str(
            price2_2) + "',''), `price2_3`=NULLIF('" + str(price2_3) + "',''), `price3_desc`=NULLIF('" + str(
            price3_desc) + "',''), `price3_1`=NULLIF('" + str(price3_1) + "',''), `price3_2`=NULLIF('" + str(
            price3_2) + "',''), `price3_3`=NULLIF('" + str(price3_3) + "',''), `price4_desc`=NULLIF('" + str(
            price4_desc) + "',''), `price4_1`=NULLIF('" + str(price4_1) + "',''), `price4_2`=NULLIF('" + str(
            price4_2) + "',''), `price4_3`=NULLIF('" + str(price4_3) + "',''), `price5_desc`=NULLIF('" + str(
            price5_desc) + "',''), `price5_1`=NULLIF('" + str(price5_1) + "',''), `price5_2`=NULLIF('" + str(
            price5_2) + "',''), `price5_3`=NULLIF('" + str(price5_3) + "',''), `price6_desc`=NULLIF('" + str(
            price6_desc) + "',''), `price6_1`=NULLIF('" + str(price6_1) + "',''), `price6_2`=NULLIF('" + str(
            price6_2) + "',''), `price6_3`=NULLIF('" + str(price6_3) + "',''), `expiray`=NULLIF('" + str(
            expiray) + "',''), `price1_1_unit`='" + str(price1_1_unit) + "', `price2_1_unit`='" + str(
            price2_1_unit) + "', `price3_1_unit`='" + str(price3_1_unit) + "', `price4_1_unit`='" + str(
            price4_1_unit) + "', `price5_1_unit`='" + str(price5_1_unit) + "', `price6_1_unit`='" + str(
            price6_1_unit) + "', `price1_2_unit`='" + str(price1_2_unit) + "', `price2_2_unit`='" + str(
            price2_2_unit) + "', `price3_2_unit`='" + str(price3_2_unit) + "', `price4_2_unit`='" + str(
            price4_2_unit) + "', `price5_2_unit`='" + str(price5_2_unit) + "', `price6_2_unit`='" + str(
            price6_2_unit) + "', `price1_3_unit`='" + str(price1_3_unit) + "', `price2_3_unit`='" + str(
            price2_3_unit) + "', `price3_3_unit`='" + str(price3_3_unit) + "', `price4_3_unit`='" + str(
            price4_3_unit) + "', `price5_3_unit`='" + str(price5_3_unit) + "', `price6_3_unit`='" + str(
            price6_3_unit) + "', `manufacture_hall`=NULLIF('" + str(manufacture_hall) + "',''), `type_col`='" + str(
            material_type) + "', `groupped`='" + str(groupped) + "', `standard_unit1_quantity`=NULLIF('" + str(
            standard_unit1_quantity_input) + "',''), `standard_unit2_quantity`=NULLIF('" + str(
            standard_unit2_quantity_input) + "',''), `standard_unit3_quantity`=NULLIF('" + str(
            standard_unit3_quantity_input) + "',''), `yearly_required`=NULLIF('" + str(
            yearly_required_input) + "',''), `work_hours`=NULLIF('" + str(
            standard_work_hours_input) + "',''), `discount_account`=NULLIF('" + str(
            material_discount_account) + "',''), `addition_account`=NULLIF('" + str(
            material_addition_account) + "','') WHERE `id`='" + str(material_id) + "'"

        print(query)

        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees_requests', 'R')
    def fetchEmploymentRequests(self) -> list:
        query = "SELECT * FROM `hr_employment_requests` ORDER BY `date_col` DESC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    # @check_permission('hr_employment_requests', 'R')
    def fetchEmploymentRequestsCount(self) -> dict:
        print("DATABASE> Fetch Employment Request Count")
        pending_query = "SELECT COUNT(*) AS pending_count FROM `hr_employment_requests` WHERE `id` NOT IN (SELECT `employment_request_id` FROM `hr_employees`)"
        self.cursor.execute(pending_query)
        pending_rows = self.cursor.fetchone()

        accepted_query = "SELECT COUNT(*) AS accepted_count FROM `hr_employment_requests` WHERE `id` IN (SELECT `employment_request_id` FROM `hr_employees`)"
        self.cursor.execute(accepted_query)
        accepted_rows = self.cursor.fetchone()

        return {
            'pending_employment_requests_count': pending_rows[0],
            'accepted_employment_requests_count': accepted_rows[0]
        }


    @check_permission('hr_employees_requests', 'W')
    def addNewEmploymentRequest(self, name) -> None:
        query = "INSERT INTO `hr_employment_requests` (`name`) VALUES ('" + name + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees_requests', 'R')
    def fetchEmploymentRequest(self, selected_id = None, name = None) -> dict:
        query = "SELECT * FROM `hr_employment_requests` WHERE " + ("`id` = '" + str(selected_id) + "'" if selected_id else "`name` = '" + str(name) + "'")
        print(query)
        self.cursor.execute(query)
        employment_request = self.cursor.fetchone()
        return employment_request


    @check_permission('hr_employees_requests', 'W')
    def addEmploymentRequestCertificate(self, employment_request_id, university_name, university_certificate,university_year, university_specialty, university_gpa) -> None:
        query = "INSERT INTO hr_employment_request_certificates (" + "employment_request_id, university_name, university_certificate, university_year, university_specialty, university_gpa) " + "VALUES (" + "'" + employment_request_id + "', " + "'" + university_name + "', " + "'" + university_certificate + "', " + "'" + university_year + "', " + "'" + university_specialty + "', " + "'" + university_gpa + "'" + ")"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('hr_employees_requests', 'W')
    def removeEmploymentRequestCertificate(self, id) -> None:
        query = "DELETE FROM `hr_employment_request_certificates` WHERE `id` = '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees_requests', 'R')
    def fetchEmploymentRequestsCertificates(self, employment_request_id) -> list:
        # Assuming you have a database connection established
        # and a cursor object available

        # Perform necessary validation and error handling, if needed

        # Construct the SQL query to fetch employment request certificates
        query = "SELECT * FROM hr_employment_request_certificates WHERE employment_request_id = {}".format(
            employment_request_id)

        try:
            # Execute the query
            self.cursor.execute(query)
            # Fetch all rows from the result set
            result = self.cursor.fetchall()
            # Commit the transaction
            self.sqlconnector.conn.commit()
            # Return the fetched rows
            return result
        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            print(e)

    @check_permission('hr_employees_requests', 'W')
    def updateEmploymentRequest(self, id, national_id, phone, address, name, email, birthdate) -> None:
        query = "UPDATE `hr_employment_requests` SET `national_id` = '" + national_id + "', `phone` = '" + phone + "', `address` = '" + address + "', `name` = '" + name + "', `email` = '" + email + "', `birthdate` = '" + birthdate + "' WHERE `id` = '" + str(
            id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees_requests', 'W')
    def employ(self, selected_employment_request_id, department_id, position_id, start_date, salary_account='', salary_opposite_account='') -> None:
        # Fetch the employment request data from hr_employment_requests table
        query = "SELECT * FROM `hr_employment_requests` WHERE id='" + str(selected_employment_request_id) + "'"
        self.cursor.execute(query)
        employment_request = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        if employment_request:
            # Extract the data from employment_request tuple
            national_id = employment_request[1]
            phone = employment_request[2]
            address = employment_request[3]
            name = employment_request[4]
            email = employment_request[5]
            birthdate = employment_request[6]

            # Insert the employment request data into hr_employees table
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "INSERT INTO hr_employees (`employment_request_id`, `national_id`, `phone`, `address`, `name`, `email`, `birthdate`, `start_date`) VALUES ('" + str(
                    selected_employment_request_id) + "', NULLIF('" + str(national_id) + "','None'), NULLIF('" + str(phone) + "','None'), NULLIF('" + str(address) + "','None'), NULLIF('" + str(name) + "','None'), NULLIF('" + str(email) + "','None'), NULLIF('" + str(birthdate) + "','None'), NULLIF('" + str(
                    start_date) + "','None')) ON DUPLICATE KEY UPDATE `national_id`=NULLIF('" + str(national_id) + "','None'), `phone`=NULLIF('" + str(phone) + "','None'), `address`=NULLIF('" + str(address) + "','None'), `name`=NULLIF('" + str(name) + "','None'), `email`=NULLIF('" + str(email) + "','None'), `birthdate`=NULLIF('" + str(birthdate) + "','None'), `start_date`=NULLIF('" + str(start_date) + "','None'), `resignation_date`=NULL"
            else:
                # For SQLite, use INSERT OR REPLACE instead
                query = "INSERT OR REPLACE INTO hr_employees (`employment_request_id`, `national_id`, `phone`, `address`, `name`, `email`, `birthdate`, `start_date`, `resignation_date`) VALUES ('" + str(
                    selected_employment_request_id) + "', NULLIF('" + str(national_id) + "','None'), NULLIF('" + str(phone) + "','None'), NULLIF('" + str(address) + "','None'), NULLIF('" + str(name) + "','None'), NULLIF('" + str(email) + "','None'), NULLIF('" + str(birthdate) + "','None'), NULLIF('" + str(
                    start_date) + "','None'), NULL)"

            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            new_employee_id = self.cursor.lastrowid

            # Fetch the employment request certificates data from hr_employment_request_certificates table
            query = "SELECT * FROM `hr_employment_request_certificates` WHERE employment_request_id=" + str(
                selected_employment_request_id)
            print(query)
            self.cursor.execute(query)
            certificates = self.cursor.fetchall()
            self.sqlconnector.conn.commit()
            for certificate in certificates:
                # Extract the certificate data
                university_name = str(certificate[2])
                university_specialty = str(certificate[3])
                university_year = str(certificate[4])
                university_certificate = str(certificate[5])
                university_gpa = str(certificate[6])

                # Insert the certificate data into hr_employees_certificates table
                query = "INSERT INTO `hr_employees_certificates` (employee_id, university_name, university_specialty, university_year, university_certificate, university_gpa) VALUES ('" + str(
                    new_employee_id) + "', '" + university_name + "', '" + university_specialty + "', '" + university_year + "', '" + university_certificate + "', '" + university_gpa + "')"
                self.cursor.execute(query)
                self.sqlconnector.conn.commit()

            # add position and department logs
            current_date = datetime.datetime.now().date()
            query = "INSERT INTO `hr_employees_transfers`(`employee_id`, `department_id`, `position_id`, `date_col`) VALUES ('" + str(
                new_employee_id) + "','" + str(department_id) + "','" + str(position_id) + "','" + str(start_date) + "')"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            position = self.fetchPosition(position_id)
            position_salary = position['salary']
            position_salary_currency = position['currency_id']

            # add salary to finance
            # if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = "INSERT INTO `hr_finance` (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `account_id`, `opposite_account_id`) VALUES (" + str(new_employee_id) + ", 'salary', " + str(position_salary) + ", " + str(position_salary_currency) + ", '" + str(current_date) + "', " + (str(salary_account) if salary_account else "NULL") + ", " + (str(salary_opposite_account) if salary_opposite_account else "NULL") + ")"
            # else:
            #     query = "INSERT INTO `hr_finance` (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `account_id`, `opposite_account_id`) VALUES (" + str(new_employee_id) + ", 'salary', " + str(position_salary) + ", " + str(position_salary_currency) + ", '" + str(current_date) + "', " + (str(salary_account) if salary_account else "NULL") + ", " + (str(salary_opposite_account) if salary_opposite_account else "NULL") + ")"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            print("Employment request with ID", selected_employment_request_id, "has been employed.")
        else:
            print("Employment request with ID", selected_employment_request_id, "not found.")

    def resign(self, employee_id, date):
        query = "UPDATE `hr_employees` SET `resignation_date` = '" + date + "' WHERE `id` = '" + str(employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'R')
    def fetchDepartments(self) -> list:
        query = "SELECT * FROM `hr_departments`;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_positions', 'R')
    def fetchPositions(self) -> list:
        query = "SELECT * FROM `hr_positions`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployees(self, state=None, department_id=None, exclude_id=None) -> list:
        if state and state.lower() == 'current':
            query = "SELECT `p`.`id` AS `position_id`, `p`.`position_name`, `hr_employees`.`id`, `hr_employees`.`name`, `hr_employees`.`start_date`, `hr_employees`.`resignation_date`, `d`.`id` AS `department_id`, `d`.`name` AS `department_name` FROM `hr_employees` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`department_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_departments`.`name` FROM `hr_employees_transfers` JOIN `hr_departments` ON `hr_employees_transfers`.`department_id` = `hr_departments`.`id` WHERE ( `hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col` ) IN( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `d` ON `d`.`employee_id` = `hr_employees`.`id` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`position_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_positions`.`position_name` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_employees_transfers`.`position_id` = `hr_positions`.`id` WHERE (`hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col`) IN ( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `p` ON `p`.`employee_id` = `hr_employees`.`id` WHERE `hr_employees`.`resignation_date` IS NULL"
        elif state and state.lower() == 'resigned':
            query = "SELECT `p`.`id` AS `position_id`, `p`.`position_name`, `hr_employees`.`id`, `hr_employees`.`name`, `hr_employees`.`start_date`, `hr_employees`.`resignation_date`, `d`.`id` AS `department_id`, `d`.`name` AS `department_name` FROM `hr_employees` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`department_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_departments`.`name` FROM `hr_employees_transfers` JOIN `hr_departments` ON `hr_employees_transfers`.`department_id` = `hr_departments`.`id` WHERE ( `hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col` ) IN( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `d` ON `d`.`employee_id` = `hr_employees`.`id` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`position_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_positions`.`position_name` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_employees_transfers`.`position_id` = `hr_positions`.`id` WHERE (`hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col`) IN ( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `p` ON `p`.`employee_id` = `hr_employees`.`id` WHERE `hr_employees`.`resignation_date` IS NOT NULL"
        else:  # fetch both resgined and current employees
            query = "SELECT `p`.`id` AS `position_id`, `p`.`position_name`, `hr_employees`.`id`, `hr_employees`.`name`, `hr_employees`.`start_date`, `hr_employees`.`resignation_date`, `d`.`id` AS `department_id`, `d`.`name` AS `department_name` FROM `hr_employees` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`department_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_departments`.`name` FROM `hr_employees_transfers` JOIN `hr_departments` ON `hr_employees_transfers`.`department_id` = `hr_departments`.`id` WHERE ( `hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col` ) IN( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `d` ON `d`.`employee_id` = `hr_employees`.`id` JOIN( SELECT MAX(`hr_employees_transfers`.`date_col`) AS `max_date`, `hr_employees_transfers`.`position_id` AS `id`, `hr_employees_transfers`.`employee_id`, `hr_positions`.`position_name` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_employees_transfers`.`position_id` = `hr_positions`.`id` WHERE (`hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`date_col`) IN ( SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id` ) GROUP BY `hr_employees_transfers`.`employee_id` ) AS `p` ON `p`.`employee_id` = `hr_employees`.`id`;"

        if exclude_id:
            query += " AND `hr_employees`.`id` != '" + str(exclude_id) + "'"

        if department_id:
            query += " AND `d`.`id` = '" + str(department_id) + "'"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchAllEmployees(self) -> list:
        query = "SELECT * FROM `hr_employees`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'W')
    def updateEmployeePhoto(self, employee_id, photo_data) -> None:
        print("DATABASE> Update employee photo")
        query = "UPDATE `hr_employees` SET `photo` = %s WHERE `id` = %s"
        self.cursor.execute(query, (photo_data, employee_id))
        self.sqlconnector.conn.commit()


    @check_permission('hr_employees', 'R')
    def fetchEmployeesCount(self, position='', department_id='', from_date='', to_date='') -> dict:
        print("DATABASE> Fetch employees count")
        query = "SELECT SUM(CASE WHEN `e`.`resignation_date` IS NULL THEN 1 ELSE 0 END) as `current_count`, SUM(CASE WHEN `e`.`resignation_date` IS NOT NULL THEN 1 ELSE 0 END) as `resigned_count`, COUNT(*) as `total_count` FROM `hr_employees` `e` LEFT JOIN (SELECT `employee_id`, `position_id`, `department_id` FROM `hr_employees_transfers` WHERE (`employee_id`, `date_col`) IN (SELECT `employee_id`, MAX(`date_col`) FROM `hr_employees_transfers` GROUP BY `employee_id`)) `t` ON `e`.`id` = `t`.`employee_id` WHERE `t`.`position_id` = COALESCE(NULLIF('" + str(position) + "',''), `t`.`position_id`) AND `t`.`department_id` = COALESCE(NULLIF('" + str(department_id) + "',''), `t`.`department_id`)"
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return {
            'current_count': rows[0] if rows[0] is not None else 0,
            'resigned_count': rows[1] if rows[1] is not None else 0,
            'total_count': rows[2] if rows[2] is not None else 0,
        }

    @check_permission('hr_employees', 'R')
    def fetchEmployee(self, id='', employment_request_id='') -> dict:
        query = "SELECT `hr_employees`.*, `t`.`position_id`, `t`.`position_name`, `t`.`department_id`, `t`.`department_name` FROM `hr_employees` JOIN (SELECT `hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`department_id`, `hr_employees_transfers`.`position_id`, `hr_positions`.`position_name`, `hr_departments`.`name` as `department_name`, `hr_employees_transfers`.`date_col` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_positions`.`id` = `hr_employees_transfers`.`position_id` JOIN `hr_departments` ON `hr_departments`.`id` = `hr_employees_transfers`.`department_id`) AS `t` ON `t`.`employee_id` = `hr_employees`.`id` WHERE `t`.`date_col` = (SELECT MAX(`date_col`) FROM `hr_employees_transfers` WHERE `employee_id` = COALESCE(NULLIF('" + str(id) + "',''), `hr_employees`.`id`)) AND `hr_employees`.`id` = COALESCE(NULLIF('" + str(id) + "',''), `hr_employees`.`id`) AND `hr_employees`.`employment_request_id` = COALESCE(NULLIF('" + str(employment_request_id) + "',''), `hr_employees`.`employment_request_id`)"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployeeTransfers(self, id, from_date='', to_date='') -> list:
        query = "SELECT `hr_employees_transfers`.`id`, `hr_employees_transfers`.`date_col`, `hr_positions`.`id` AS `position_id`, `hr_positions`.`position_name`, `hr_departments`.`id` AS `department_id`, `hr_departments`.`name` AS `department_name` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_employees_transfers`.`position_id` = `hr_positions`.`id` JOIN `hr_departments` ON `hr_departments`.`id` = `hr_employees_transfers`.`department_id` WHERE `hr_employees_transfers`.`employee_id`='" + str(id) + "'"

        if from_date and to_date:
            query += " AND `hr_employees_transfers`.`date_col` BETWEEN '" + str(from_date) + "' AND '" + str(to_date) + "'"

        query += " ORDER BY `hr_employees_transfers`.`date_col` DESC"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployeeCertificates(self, id) -> list:
        query = "SELECT * FROM `hr_employees_certificates` WHERE `employee_id`= '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployeeCourses(self, id) -> list:
        query = "SELECT `hr_course_employees`.`id`, `hr_courses`.`title`, `hr_courses`.`providor`, `hr_courses`.`date_col`, `hr_course_employees`.`gpa` FROM `hr_course_employees` JOIN `hr_courses` ON `hr_courses`.`id`=`hr_course_employees`.`course_id` WHERE `hr_course_employees`.`employee_id`='" + str(
            id) + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'W')
    def addEmployeeReceivedItem(self, employee_id, warehouse_id, quantity, material_id, unit_id, received_date) -> int:
        query = "INSERT INTO `hr_employee_received_items` (`employee_id`, `warehouse_id`, `quantity`, `material_id`, `unit_id`, `received_date`) VALUES ('" + str(employee_id) + "', '" + str(warehouse_id) + "', '" + str(quantity) + "', '" + str(material_id) + "', '" + str(unit_id) + "', NULLIF('" + str(received_date) + "',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('hr_employees', 'R')
    def fetchEmployeeReceivedItems(self, id) -> list:
        query = "SELECT `hr_employee_received_items`.*, `hr_employees`.`name` AS `employee_name`, `warehouseslist`.`name` AS `warehouse_name`, `materials`.`name` AS `material_name`, `hr_employee_received_items`.`quantity`, `units`.`name` AS `unit_name`, `hr_employee_received_items`.`received_date`, `hr_employee_received_items`.`received` FROM `hr_employee_received_items` JOIN `hr_employees` ON `hr_employee_received_items`.`employee_id` = `hr_employees`.`id` JOIN `warehouseslist` ON `hr_employee_received_items`.`warehouse_id` = `warehouseslist`.`id` JOIN `materials` ON `hr_employee_received_items`.`material_id` = `materials`.`id` JOIN `units` ON `hr_employee_received_items`.`unit_id` = `units`.`id` WHERE `hr_employees`.`id`='" + str(
            id) + "';"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployeesReceivedItemsCount(self) -> dict:
        query = "SELECT COUNT(*) AS items_count FROM `hr_employee_received_items`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return {'items_count': rows[0]}

    @check_permission('hr_employees', 'W')
    def removeEmployeeReceivedItem(self, id) -> None:
        query = "DELETE FROM `hr_employee_received_items` WHERE `id` = '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees', 'R')
    def fetchEmployeeFinanceInfo(self, id) -> dict:
        query = "SELECT `hr_employees`.`bank`, `hr_employees`.`bank_account_number`, `hr_employees`.`bank_notes`, `salary_info`.`salary`, `salary_info`.`cycle` as `salary_cycle`, `salary_info`.`currency` as `salary_currency`, `insurance_info`.`insurance`, `salary_info`.`account_id` AS `salary_account_id`, `salary_info`.`opposite_account_id` AS `salary_opposite_account_id`, `insurance_info`.`account_id` AS `insurance_account_id`, `insurance_info`.`opposite_account_id` AS `insurance_opposite_account_id`, `insurance_info`.`currency` as `insurance_currency`, `insurance_info`.`cycle` as `insurance_cycle`, `hr_departments`.`day_hours` FROM `hr_employees` JOIN (SELECT `hr_employees_transfers`.`employee_id`, `hr_employees_transfers`.`department_id`, `hr_employees_transfers`.`position_id`, `hr_positions`.`position_name`, `hr_departments`.`name` as `department_name`, `hr_employees_transfers`.`date_col` FROM `hr_employees_transfers` JOIN `hr_positions` ON `hr_positions`.`id` = `hr_employees_transfers`.`position_id` JOIN `hr_departments` ON `hr_departments`.`id` = `hr_employees_transfers`.`department_id`) AS `t` ON `t`.`employee_id` = `hr_employees`.`id` LEFT JOIN( SELECT `employee_id`, `value_col` AS `salary`, `cycle`, `currency_id` AS `currency` , `account_id`, `opposite_account_id` FROM `hr_finance` WHERE `type_col` = 'salary' AND `date_col` =( SELECT MAX(`date_col`) FROM `hr_finance` WHERE `employee_id` = '" + str(id) + "' AND `type_col`='salary') AND `employee_id` = '" + str(id) + "' ) AS `salary_info` ON `hr_employees`.`id` = `salary_info`.`employee_id` LEFT JOIN( SELECT `employee_id`, `value_col` AS `insurance`, `cycle`, `currency_id` AS `currency`, `account_id`, `opposite_account_id` FROM `hr_finance` WHERE `type_col` = 'insurance' AND `date_col` =( SELECT MAX(`date_col`) FROM `hr_finance` WHERE `employee_id` = '" + str(id) + "' AND `type_col`='insurance') AND `employee_id` = '" + str(id) + "' ) AS `insurance_info` ON `hr_employees`.`id` = `insurance_info`.`employee_id` JOIN `hr_finance` ON `hr_employees`.`id` = `hr_finance`.`employee_id` JOIN `currencies` ON `hr_finance`.`currency_id` = `currencies`.`id` JOIN `hr_departments` ON `hr_departments`.`id` = `t`.`department_id` WHERE `hr_employees`.`id` = '" + str(id) + "' AND `t`.`date_col` = (SELECT MAX(`date_col`) FROM `hr_employees_transfers` WHERE `employee_id` = '" + str(id) + "') GROUP BY `hr_employees`.`id`;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'R')
    def fetchEmployeesFinanceInfo(self, from_date='', to_date='') -> list:
        query = '''SELECT
                    `hr_employees`.`id` as `employee_id`,
                    `hr_employees`.`name`,
                    `t`.`position_id`,
                    `t`.`position_name`,
                    `t`.`department_id`,
                    `t`.`department_name`,
                    `hr_employees`.`name`,
                    `hr_employees`.`bank`,
                    `hr_employees`.`bank_account_number`,
                    `hr_employees`.`bank_notes`,
                    `salary_info`.`salary`,
                    `salary_info`.`cycle` AS `salary_cycle`,
                    `salary_info`.`currency` AS `salary_currency`,
                    `insurance_info`.`insurance`,
                    `salary_info`.`account_id` AS `salary_account_id`,
                    `salary_info`.`opposite_account_id` AS `salary_opposite_account_id`,
                    `insurance_info`.`account_id` AS `insurance_account_id`,
                    `insurance_info`.`opposite_account_id` AS `insurance_opposite_account_id`,
                    `insurance_info`.`currency` AS `insurance_currency`,
                    `insurance_info`.`cycle` AS `insurance_cycle`,
                    `c1`.`name` AS `salary_currency_name`,
                    `c2`.`name` AS `insurance_currency_name`,
                    `a1`.`name` AS `salary_account_name`,
                    `a2`.`name` AS `salary_opposite_account_name`
                FROM
                    `hr_employees`
                LEFT JOIN(
                    SELECT
                        `employee_id`,
                        `value_col` AS `salary`,
                        `cycle`,
                        `currency_id` AS `currency`,
                        `account_id`,
                        `opposite_account_id`
                    FROM
                        `hr_finance`
                    JOIN `hr_employees` ON `hr_employees`.`id` = `hr_finance`.`employee_id`
                    WHERE
                        `type_col` = 'salary' AND `date_col` =(
                        SELECT
                            MAX(`date_col`)
                        FROM
                            `hr_finance`
                        WHERE
                            `employee_id` = `hr_employees`.`id` AND `type_col` = 'salary'
                    )
                ) AS `salary_info`
                ON
                    `hr_employees`.`id` = `salary_info`.`employee_id`
                LEFT JOIN(
                    SELECT
                        `employee_id`,
                        `value_col` AS `insurance`,
                        `cycle`,
                        `currency_id` AS `currency`,
                        `account_id`,
                        `opposite_account_id`
                    FROM
                        `hr_finance`
                    JOIN `hr_employees` ON `hr_employees`.`id` = `hr_finance`.`employee_id`
                    WHERE
                        `type_col` = 'insurance' AND `date_col` =(
                        SELECT
                            MAX(`date_col`)
                        FROM
                            `hr_finance`
                        WHERE
                            `employee_id` = `hr_employees`.`id` AND `type_col` = 'insurance'
                    )
                ) AS `insurance_info`
                ON
                    `hr_employees`.`id` = `insurance_info`.`employee_id`
                JOIN `hr_finance` ON `hr_employees`.`id` = `hr_finance`.`employee_id`
                JOIN `currencies` as `c1` ON `hr_finance`.`currency_id` = `c1`.`id`
                JOIN `currencies` as `c2` ON `hr_finance`.`currency_id` = `c2`.`id`
                LEFT JOIN `accounts` as `a1` ON `salary_info`.`account_id` = `a1`.`id`
                LEFT JOIN `accounts` as `a2` ON `salary_info`.`opposite_account_id` = `a2`.`id`
                JOIN(
                    SELECT `hr_employees_transfers`.`employee_id`,
                        `hr_employees_transfers`.`department_id`,
                        `hr_employees_transfers`.`position_id`,
                        `hr_positions`.`position_name`,
                        `hr_departments`.`name` AS `department_name`
                    FROM
                        `hr_employees_transfers` JOIN `hr_employees` ON `hr_employees_transfers`.`employee_id`=`hr_employees`.`id`
                    JOIN `hr_positions` ON `hr_positions`.`id` = `hr_employees_transfers`.`position_id`
                    JOIN `hr_departments` ON `hr_departments`.`id` = `hr_employees_transfers`.`department_id`
                    WHERE
                        date_col =(
                        SELECT
                            MAX(date_col)
                        FROM
                            `hr_employees_transfers`
                        WHERE
                            `employee_id` = `hr_employees`.`id`
                    ) AND `employee_id` = `hr_employees`.`id`
                ) AS `t`
                ON
                    `t`.`employee_id` = `hr_employees`.`id`'''

        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query += " WHERE  (`hr_employees`.`resignation_date` IS NULL AND `hr_employees`.`start_date` <= COALESCE(NULLIF(%s, ''), DATE('9999-12-31')))  GROUP BY   `hr_employees`.`id`;"
        else:
            # SQLite syntax
            query += " WHERE  (`hr_employees`.`resignation_date` IS NULL AND `hr_employees`.`start_date` <= COALESCE(NULLIF(?, ''), date('9999-12-31')))  GROUP BY   `hr_employees`.`id`;"

        print(query)
        self.cursor.execute(query, (to_date,))
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_employees', 'W')
    def saveEmployee(self, id, employee_name, employee_email, employee_address, employee_phone, employee_national_id,employee_position, employee_department, employee_birthdate, employee_start_date) -> None:
        query = "UPDATE hr_employees SET national_id='" + employee_national_id + "', phone='" + employee_phone + "', address='" + employee_address + "', name='" + employee_name + "', email='" + employee_email + "', birthdate='" + employee_birthdate + "', start_date='" + employee_start_date + "' WHERE id='" + id + "'"
        print(query)
        self.cursor.execute(query)

        query = "SELECT `department_id`, `position_id` FROM `hr_employees_transfers` WHERE `date_col`=(SELECT MAX(`date_col`) FROM `hr_employees_transfers` WHERE `employee_id`='" + id + "')"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        last_transfer = [rows[0], rows[1]]
        new_transfer = [employee_department, employee_position]
        if not last_transfer == new_transfer:
            query = "INSERT INTO `hr_employees_transfers`(`employee_id`, `department_id`, `position_id`) VALUES ('" + str(
                id) + "','" + str(employee_department) + "','" + str(employee_position) + "')"
            print(query)
            self.cursor.execute(query)

        self.sqlconnector.conn.commit()


    @check_permission('hr_employees', 'W')
    def addEmployeeCertificate(self, employee_id, university_name, university_certificate, university_year,university_specialty, university_gpa) -> None:
        query = "INSERT INTO `hr_employees_certificates` (`employee_id`, `university_name`, `university_certificate`, `university_year`, `university_specialty`, `university_gpa`) " + "VALUES (" + "'" + employee_id + "', " + "'" + university_name + "', " + "'" + university_certificate + "', " + "'" + university_year + "', " + "'" + university_specialty + "', " + "'" + university_gpa + "'" + ")"
        print(query)
        try:
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
        except Exception as e:
            # Handle any exceptions that may occur during the database operation
            print("Error adding new employment request certificate:", e)

    @check_permission('hr_employees', 'W')
    def removeEmployeeCertificate(self, certificate_id) -> None:
        query = "DELETE FROM `hr_employees_certificates` WHERE `id`='" + str(certificate_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_employees', 'W')
    def saveEmployeeFinanceInfo(self, id, employee_bank_input, employee_bank_account_number, employee_bank_notes,
                                employee_salary, employee_insurance, employee_salary_currency, employee_salary_cycle,
                                employee_salary_account, employee_salary_opposite_account, employee_insurance_account,
                                employee_insurance_opposite_account, employee_salary_start_date,
                                employee_insurance_cycle,
                                employee_insurance_start_date) -> None:
        try:
            # Update employee bank info
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "UPDATE `hr_employees` SET `bank`=%s, `bank_account_number`=%s, `bank_notes`=%s WHERE `id`=%s"
            else:
                query = "UPDATE `hr_employees` SET `bank`=?, `bank_account_number`=?, `bank_notes`=? WHERE `id`=?"
            params = (employee_bank_input, employee_bank_account_number, employee_bank_notes, id)
            self.cursor.execute(query, params)

            # Delete old salary and insurance finance
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "DELETE FROM `hr_finance` WHERE `employee_id`=%s AND (`type_col`='salary' OR `type_col`='insurance')"
            else:
                query = "DELETE FROM `hr_finance` WHERE `employee_id`=? AND (`type_col`='salary' OR `type_col`='insurance')"
            self.cursor.execute(query, (id,))

            # Insert new salary finance record
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = """INSERT INTO `hr_finance`
                    (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`,
                    `account_id`, `opposite_account_id`, `cycle`, `date_col`)
                    VALUES(%s, 'salary', %s, %s, %s, NULL,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CURRENT_TIMESTAMP)"""
            else:
                query = """INSERT INTO `hr_finance`
                    (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`,
                    `account_id`, `opposite_account_id`, `cycle`, `date_col`)
                    VALUES(?, 'salary', ?, ?, ?, NULL,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CURRENT_TIMESTAMP)"""
            params = (id, employee_salary, employee_salary_currency, employee_salary_start_date,
                     employee_salary_account, employee_salary_account,
                     employee_salary_opposite_account, employee_salary_opposite_account,
                     employee_salary_cycle, employee_salary_cycle)
            self.cursor.execute(query, params)

            # Insert new insurance finance record
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = """INSERT INTO `hr_finance`
                    (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`,
                    `account_id`, `opposite_account_id`, `cycle`, `date_col`)
                    VALUES(%s, 'insurance', %s, %s, %s, NULL,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CASE WHEN %s = '' THEN NULL ELSE %s END,
                    CURRENT_TIMESTAMP)"""
            else:
                query = """INSERT INTO `hr_finance`
                    (`employee_id`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`,
                    `account_id`, `opposite_account_id`, `cycle`, `date_col`)
                    VALUES(?, 'insurance', ?, ?, ?, NULL,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CASE WHEN ? = '' THEN NULL ELSE ? END,
                    CURRENT_TIMESTAMP)"""
            params = (id, employee_insurance, employee_salary_currency, employee_insurance_start_date,
                     employee_insurance_account, employee_insurance_account,
                     employee_insurance_opposite_account, employee_insurance_opposite_account,
                     employee_insurance_cycle, employee_insurance_cycle)
            self.cursor.execute(query, params)

            self.sqlconnector.conn.commit()

        except Exception as e:
            print(f"Error saving employee finance info: {str(e)}")
            self.sqlconnector.conn.rollback()
            raise

    @check_permission('hr_departments', 'W')
    def addNewDepartment(self, name, day_hours, account=None, opposite_account=None, notes='') -> None:
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = """INSERT INTO `hr_departments`
                    (`name`, `day_hours`, `account_id`, `opposite_account_id`, `notes`)
                    VALUES (%s, %s, %s, %s, %s)"""
        else:
            query = """INSERT INTO `hr_departments`
                    (`name`, `day_hours`, `account_id`, `opposite_account_id`, `notes`)
                    VALUES (?, ?, ?, ?, ?)"""
        params = (name, day_hours, account if account else None, opposite_account if opposite_account else None, notes)

        print(query, params)
        self.cursor.execute(query, params)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'R')

    def fetchDepartment(self, id) -> dict:
        query = "SELECT * FROM `hr_departments` WHERE `id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_departments', 'R')
    def fetchDepartmentsCount(self) -> dict:
        print("DATABASE> Fetch departments count")
        query = "SELECT COUNT(*) AS departments_count FROM `hr_departments`"
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        return {'departments_count': rows[0]}

    @check_permission('hr_departments', 'W')
    def saveDepartment(self, selected_department_id, department_name, department_day_hours, department_account,
                       department_opposite_account, department_notes, departments_work_day_friday,
                       departments_work_day_tuesday, departments_work_day_thursday, departments_work_day_wednesday,
                       departments_work_day_monday, departments_work_day_sunday, departments_work_day_saturday) -> None:
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            query = """UPDATE `hr_departments` SET
                    `name`=%s,
                    `day_hours`=%s,
                    `account_id`=%s,
                    `opposite_account_id`=%s,
                    `notes`=%s,
                    `work_day_saturday`=%s,
                    `work_day_sunday`=%s,
                    `work_day_monday`=%s,
                    `work_day_tuesday`=%s,
                    `work_day_wednesday`=%s,
                    `work_day_thursday`=%s,
                    `work_day_friday`=%s
                    WHERE `id`=%s"""
        else:
            query = """UPDATE `hr_departments` SET
                    `name`=?,
                    `day_hours`=?,
                    `account_id`=?,
                    `opposite_account_id`=?,
                    `notes`=?,
                    `work_day_saturday`=?,
                    `work_day_sunday`=?,
                    `work_day_monday`=?,
                    `work_day_tuesday`=?,
                    `work_day_wednesday`=?,
                    `work_day_thursday`=?,
                    `work_day_friday`=?
                    WHERE `id`=?"""

        # Handle empty strings for foreign keys to prevent FOREIGN KEY constraint failures
        account_id = None if not department_account or department_account == '' else department_account
        opposite_account_id = None if not department_opposite_account or department_opposite_account == '' else department_opposite_account

        params = (
            department_name,
            department_day_hours,
            account_id,
            opposite_account_id,
            department_notes,
            departments_work_day_saturday,
            departments_work_day_sunday,
            departments_work_day_monday,
            departments_work_day_tuesday,
            departments_work_day_wednesday,
            departments_work_day_thursday,
            departments_work_day_friday,
            selected_department_id
        )

        print(query, params)
        self.cursor.execute(query, params)
        self.sqlconnector.conn.commit()


    @check_permission('hr_departments', 'W')
    def saveDepartmentFinance(self, selected_department_id, departments_additions_discounts_currency,
                              departments_additions_discounts_statement, departments_additions_discounts_value,
                              departments_additions_discounts_start_date,
                              departments_additions_discounts_end_date, departments_additions_discounts_type,
                              departments_additions_discounts_account,
                              departments_additions_discounts_opposite_account)-> None:
        query = "INSERT INTO `hr_departments_finance` (`department_id`, `statement_col`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`, `account_id`, `opposite_account_id`) VALUES ('" + str(
            selected_department_id) + "', '" + str(departments_additions_discounts_statement) + "', '" + str(
            departments_additions_discounts_type) + "', '" + str(departments_additions_discounts_value) + "', '" + str(
            departments_additions_discounts_currency) + "', '" + str(
            departments_additions_discounts_start_date) + "', '" + str(
            departments_additions_discounts_end_date) + "', '" + str(
            departments_additions_discounts_account) + "', '" + str(
            departments_additions_discounts_opposite_account) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'W')
    def saveDepartmentLeave(self, selected_department_id, department_leave_statement, department_leave_duration_hours,
                            department_leave_duration_days,
                            department_leave_start_date) -> None:
        query = "INSERT INTO `hr_departments_leaves`(`department_id`, `statement_col`, `duration_in_hours`, `duration_in_days`, `start_date`) VALUES (" + str(
            selected_department_id) + ", '" + department_leave_statement + "', " + str(
            department_leave_duration_hours) + ", " + str(
            department_leave_duration_days) + ", '" + department_leave_start_date + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'W')
    def removeDepartmentLeave(self, department_leave_id) -> None:
        query = "DELETE FROM `hr_departments_leaves` WHERE `id`='" + str(department_leave_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'R')
    def fetchDepartmentDiscountsAdditions(self, department_id, start_date='', end_date='') -> list:
        query = "SELECT `hr_departments_finance`.*, `currencies`.`name` AS `currency_name`, `accounts`.`name` AS `account`, `opposite_accounts`.`name` AS `opposite_account` FROM `hr_departments_finance` JOIN `currencies` ON `currencies`.`id`=`hr_departments_finance`.`currency_id` LEFT JOIN (SELECT `id`, `name` FROM `accounts`) as `accounts` ON `accounts`.`id` = `hr_departments_finance`.`account_id` LEFT JOIN (SELECT `id`, `name` FROM `accounts`) as `opposite_accounts` ON `opposite_accounts`.`id` = `hr_departments_finance`.`opposite_account_id` WHERE `hr_departments_finance`.`department_id` = " + str(
            department_id) + " AND (`start_date` >= COALESCE(NULLIF('" + str(
            start_date) + "',''), DATE('1000-01-01')) OR `end_date` <= COALESCE(NULLIF('" + str(
            end_date) + "',''), DATE('9999-12-31')));"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_departments', 'W')
    def removeDepartmentAdditionAndDiscount(self, department_additions_discounts_id) -> None:
        query = "DELETE FROM `hr_departments_finance` WHERE `id`='" + str(department_additions_discounts_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_departments', 'R')
    def fetchDepartmentLeaves(self, id , start_date='') -> list:
        query = "SELECT * FROM `hr_departments_leaves` WHERE `hr_departments_leaves`.`department_id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_positions', 'R')
    def fetchPosition(self, id) -> dict:
        query = "SELECT `hr_positions`.*, `currencies`.`name` as `currency_name` FROM `hr_positions` JOIN `currencies` on `hr_positions`.`currency_id`=`currencies`.`id` WHERE `hr_positions`.`id`='" + str(
            id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_positions', 'W')
    def savePositionLeave(self, id, position_leave_statement, position_leave_duration_hours, position_leave_duration_days, position_leave_start_date) -> None:
        query = "INSERT INTO `hr_positions_leaves`(`position_id`, `statement_col`, `duration_in_hours`, `duration_in_days`, `start_date`) VALUES (" + str(
            id) + ", '" + position_leave_statement + "', " + str(
            position_leave_duration_hours) + ", " + str(
            position_leave_duration_days) + ", '" + position_leave_start_date + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def removePositionLeave(self, position_leave_id) -> None:
        query = "DELETE FROM `hr_positions_leaves` WHERE `id`='" + str(position_leave_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'R')
    def fetchPositionDiscountsAdditions(self, position_id, start_date='', end_date='') -> list:
        print("DATABASE> Fetch position discounts and additions")

        query = "SELECT `hr_positions_finance`.*, `currencies`.`name` as `currency_name`, `accounts`.`name` as `account`, `opposite_accounts`.`name` as `opposite_account` FROM `hr_positions_finance` JOIN `currencies` ON `currencies`.`id`=`hr_positions_finance`.`currency_id` LEFT JOIN (SELECT `id`, `name` FROM `accounts`) as `accounts` ON `accounts`.`id` = `hr_positions_finance`.`account_id` LEFT JOIN (SELECT `id`, `name` FROM `accounts`) as `opposite_accounts` ON `opposite_accounts`.`id` = `hr_positions_finance`.`opposite_account_id`  WHERE `hr_positions_finance`.`position_id`='" + str(
            position_id) + "' AND (`start_date` >= COALESCE(NULLIF('" + str(
            start_date) + "',''), DATE('1000-01-01')) OR `end_date` <= COALESCE(NULLIF('" + str(
            end_date) + "',''), DATE('9999-12-31')));"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_positions', 'W')
    def savePositionFinance(self, selected_position_id, positions_additions_discounts_currency,
                            positions_additions_discounts_statement, positions_additions_discounts_value,
                            positions_additions_discounts_start_date,
                            positions_additions_discounts_end_date, positions_additions_discounts_type,
                            positions_additions_discounts_account,
                            positions_additions_discounts_opposite_account) -> None:
        query = "INSERT INTO `hr_positions_finance` (`position_id`, `statement_col`, `type_col`, `value_col`, `currency_id`, `start_date`, `end_date`, `account_id`, `opposite_account_id`) VALUES ('" + str(
            selected_position_id) + "', '" + str(positions_additions_discounts_statement) + "', '" + str(
            positions_additions_discounts_type) + "', '" + str(positions_additions_discounts_value) + "', '" + str(
            positions_additions_discounts_currency) + "', '" + str(
            positions_additions_discounts_start_date) + "', '" + str(
            positions_additions_discounts_end_date) + "', '" + str(
            positions_additions_discounts_account) + "', '" + str(positions_additions_discounts_opposite_account) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def removePositionFinance(self, position_finance_id) -> None:
        query = "DELETE FROM `hr_positions_finance` WHERE `id`='" + str(position_finance_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'R')
    def fetchPositionLeaves(self, id) -> list:
        query = "SELECT * FROM `hr_positions_leaves` WHERE `hr_positions_leaves`.`position_id`='" + str(id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_positions', 'W')
    def addNewPosition(self, position_name, position_salary, position_salary_currency, position_notes) -> None:
        query = "INSERT INTO `hr_positions` (`position_name`, `salary`, `currency_id`, `notes`) VALUES ('" + str(position_name) + "', '" + str(position_salary) + "', '" + str(position_salary_currency) + "', '" + str(position_notes) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def savePosition(self, selected_position_id, position_name, position_salary,position_salary_currency, position_notes) -> None:
        query = "UPDATE `hr_positions` SET `position_name`='" + str(position_name) + "', `salary`='" + str(
            position_salary) + "', `currency_id`='" + str(position_salary_currency) + "', `notes`='" + str(
            position_notes) + "' WHERE `id`='" + str(selected_position_id) + "'"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def removePosition(self, position_id) -> None:
        query = "DELETE FROM `hr_positions` WHERE `id`='" + str(position_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_leaves', 'R')
    def fetchEmployeeLeaves(self, employee_id, start_date='', state='', paid='') -> list:
        query = "SELECT `hr_leaves`.*, `employee`.`name` as `employee_name`, `alternative_employee`.`name` as `alternative_employee_name`, `hr_leave_types`.`name` as type_name FROM `hr_leaves` JOIN `hr_employees` as `employee` ON `employee`.`id`=`hr_leaves`.`employee_id` JOIN `hr_employees` as `alternative_employee` ON `hr_leaves`.`alternative_id`=`alternative_employee`.`id` JOIN `hr_leave_types` ON `hr_leaves`.`leave_type_id` = `hr_leave_types`.`id` WHERE `hr_leaves`.`employee_id` = " + str(
            employee_id) + " AND `hr_leaves`.`start_date` >= COALESCE(NULLIF('" + str(
            start_date) + "',''), DATE('1000-01-01')) AND (`hr_leaves`.`state_col` = COALESCE(NULLIF('" + str(
            state) + "',''), `hr_leaves`.`state_col`)) AND (`hr_leave_types`.`paid` = COALESCE(NULLIF('" + str(
            paid) + "',''), `hr_leave_types`.`paid`))"

        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchall()
        return row


    @check_permission('hr_leaves', 'W')
    def saveLeave(self, selected_employee_id, leave_type_id, alternative_id, duration_in_hours, duration_in_days,
                  start_date) -> None:
        query = "INSERT INTO `hr_leaves`(`employee_id`, `leave_type_id`, `alternative_id`, `duration_in_hours`, `duration_in_days`, `start_date`) VALUES ('" + str(
            selected_employee_id) + "','" + str(leave_type_id) + "','" + str(alternative_id) + "','" + str(
            duration_in_hours) + "','" + str(duration_in_days) + "','" + str(start_date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_leaves', 'W')
    def removeLeave(self, leave_id) -> None:
        query = "DELETE FROM `hr_leaves` WHERE `id`='" + str(leave_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'R')
    def fetchCourses(self) -> list:
        query = "SELECT `hr_courses`.*, `account`.`name` as `account_name`, `opposite_account`.`name` as `opposite_account` FROM `hr_courses` LEFT JOIN `accounts` as `account` ON `hr_courses`.`account_id` = `account`.`id` LEFT JOIN `accounts` as `opposite_account` ON `hr_courses`.`opposite_account_id` = `opposite_account`.`id` ORDER BY `date_col` DESC;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_courses', 'R')
    def fetchSelectedCourse(self, id) -> dict:
        query = "SELECT `hr_courses`.*, `account`.`name` as `account_name`, `opposite_account`.`name` as `opposite_account` FROM `hr_courses` LEFT JOIN `accounts` as `account` ON `hr_courses`.`account_id` = `account`.`id` LEFT JOIN `accounts` as `opposite_account` ON `hr_courses`.`opposite_account_id` = `opposite_account`.`id` WHERE `hr_courses`.`id`='" + str(
            id) + "';"
        # print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('hr_courses', 'W')
    def addNewCourse(self, title, cost, providor, location, account_id, opposite_account_id, currency_id, date) -> int:
        query = "INSERT INTO `hr_courses`(`title`, `cost`, `providor`, `location`, `account_id`, `opposite_account_id`, `currency_id`, `date_col`) VALUES (NULLIF('" + str(title) + "',''),NULLIF('" + str(cost) + "',''), NULLIF('" + str(providor) + "',''), NULLIF('" + str(location) + "',''), NULLIF('" + str(account_id) + "',''), NULLIF('" + str(opposite_account_id) + "',''), NULLIF('" + str(currency_id) + "',''), NULLIF('" + str(date) + "',''))"
        print(query)
        self.cursor.execute(query)
        course_id = self.cursor.lastrowid
        self.sqlconnector.conn.commit()
        return course_id

    @check_permission('hr_courses', 'W')
    def saveCourse(self, selected_course_id, title, cost, providor, location, account_id, opposite_account_id,
                   currency_id, date) -> None:
        query = "UPDATE `hr_courses` SET `title`='" + str(title) + "', `providor`='" + str(
            providor) + "', `account_id`= NULLIF('" + str(account_id) + "',''), `opposite_account_id`= NULLIF('" + str(
            opposite_account_id) + "',''), `cost`='" + str(cost) + "', `currency_id`='" + str(
            currency_id) + "', `date_col`='" + str(date) + "', `location`='" + str(location) + "' WHERE `id`='" + str(
            selected_course_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'W')
    def removeCourse(self, course_id) -> None:
        query = "DELETE FROM `hr_courses` WHERE `id`='" + str(course_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'W')
    def addCourseEmployee(self, course_id, employee_id, gpa) -> None:
        query = "INSERT INTO `hr_course_employees`(`course_id`, `employee_id`, `gpa`) VALUES ('" + str(
            course_id) + "','" + str(employee_id) + "','" + str(gpa) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'W')
    def removeCourseEmployee(self, course_employee_id) -> None:
        query = "DELETE FROM `hr_course_employees` WHERE `id`='" + str(course_employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'R')
    def fetchCourseEmployees(self, course_id) -> list:
        query = "select `hr_course_employees`.*, `hr_employees`.`name` as `employee_name` FROM `hr_course_employees` JOIN `hr_employees` ON `hr_course_employees`.`employee_id`=`hr_employees`.`id` WHERE `hr_course_employees`.`course_id`='" + str(
            course_id) + "' "
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_courses', 'W')
    def updateCourseEmployeeGpa(self, course_employee_id, new_gpa) -> None:
        query = "UPDATE hr_course_employees SET gpa='" + str(new_gpa) + "' WHERE id='" + str(course_employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_loans', 'W')
    def addHRLoan(self, selected_employee_id, loan_value, loan_currency, loan_date, loan_account, loan_opposite_account, loan_subtract, loan_subtract_value, loan_subtract_currency, loan_subtract_cycle) -> None:

        if loan_subtract_currency:
            query = "INSERT INTO `hr_loans`(`employee_id`, `value_col`, `currency`, `date_col`, `account_id`, `opposite_account_id`, `periodically_subtract_from_salary`, `subtract_currency`, `subtract_value`, `subtract_cycle`) VALUES ('" + str(
            selected_employee_id) + "','" + str(loan_value) + "',NULLIF('" + str(loan_currency) + "',''),'" + str(
            loan_date) + "','" + str(loan_account) + "','" + str(loan_opposite_account) + "','" + str(
            loan_subtract) + "',NULLIF('" + str(loan_subtract_currency) + "',''),NULLIF('" + str(loan_subtract_value) + "',''),NULLIF('" + str(loan_subtract_cycle) + "',''))"

        else:
            query = "INSERT INTO `hr_loans`(`employee_id`, `value_col`, `currency`, `date_col`, `account_id`, `opposite_account_id`, `periodically_subtract_from_salary`, `subtract_currency`, `subtract_value`) VALUES ('" + str(
            selected_employee_id) + "','" + str(loan_value) + "',NULLIF('" + str(loan_currency) + "',''),'" + str(
            loan_date) + "','" + str(loan_account) + "','" + str(loan_opposite_account) + "','" + str(loan_subtract) + "',NULLIF('',''), NULLIF('',''))"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        return self.cursor.lastrowid

    @check_permission('hr_loans', 'W')
    def removeHRLoan(self, loan_id) -> None:
        query = "DELETE FROM `hr_loans` WHERE `id`='" + str(loan_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_loans', 'R')
    def fetchHRLoans(self, position_id='', department_id='', start_date='', end_date=''):
        query = "SELECT hr_loans.*, SUM(hr_loans.value_col) AS total_loans_value , hr_loans.value_col AS remaining_amount, hr_employees.name, hr_departments.name AS department_name, hr_positions.position_name AS position_name FROM hr_loans JOIN hr_employees ON hr_loans.employee_id = hr_employees.id LEFT JOIN (SELECT t1.employee_id, t1.department_id, t1.position_id FROM hr_employees_transfers t1 JOIN (SELECT employee_id, MAX(date_col) as max_date FROM hr_employees_transfers GROUP BY employee_id) t2 ON t1.employee_id = t2.employee_id AND t1.date_col = t2.max_date) AS latest_transfers ON hr_employees.id = latest_transfers.employee_id LEFT JOIN hr_departments ON latest_transfers.department_id = hr_departments.id LEFT JOIN hr_positions ON latest_transfers.position_id = hr_positions.id WHERE hr_loans.date_col >= COALESCE(NULLIF('" + str(start_date) + "', ''), DATE('1000-01-01')) AND hr_loans.date_col <= COALESCE(NULLIF('" + str(end_date) + "', ''), DATE('9999-12-31'))"

        # Add position filter if provided
        if position_id:
            query += " AND latest_transfers.position_id = '" + str(position_id) + "'"
            
        # Add department filter if provided
        if department_id:
            query += " AND latest_transfers.department_id = '" + str(department_id) + "'"
            
        query += " ORDER BY hr_employees.name, hr_loans.date_col DESC;"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('hr_loans', 'R')
    def fetchLoansOfEmployee(self, employee_id, from_date='') -> list:
        query = "SELECT hr_loans.*, currencies.name AS currency_name, accounts.name AS account_name, opposite_accounts.name AS opposite_account_name, COALESCE(payments.total_payments, 0) AS total_payments, hr_loans.value_col - COALESCE(payments.total_payments, 0) AS remaining_amount, subtract_currencies.name AS subtract_currency_name FROM hr_loans JOIN currencies ON hr_loans.currency = currencies.id JOIN accounts ON hr_loans.account_id = accounts.id JOIN accounts AS opposite_accounts ON hr_loans.opposite_account_id = opposite_accounts.id LEFT JOIN currencies AS subtract_currencies ON hr_loans.subtract_currency = subtract_currencies.id LEFT JOIN (SELECT hr_loans_payment.loan_id, SUM(hr_loans_payment.value_col) AS total_payments FROM hr_loans_payment GROUP BY hr_loans_payment.loan_id) AS payments ON hr_loans.id = payments.loan_id WHERE hr_loans.employee_id = '" + str(
            employee_id) + "' AND hr_loans.date_col >= COALESCE(NULLIF('" + str(from_date) + "', ''), DATE('1000-01-01'));"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_loans', 'R')
    def fetchHRLoanPayments(self, loan_id) -> list:
        query = "SELECT hr_loans_payment.*, currencies.name AS currency_name FROM hr_loans_payment JOIN hr_loans ON hr_loans_payment.loan_id = hr_loans.id JOIN currencies ON hr_loans.currency = currencies.id WHERE hr_loans.id = '" + str(
            loan_id) + "';"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_loans', 'W')
    def addHRLoanPayment(self, loan_id, value, currency, source, date) -> None:
        query = "INSERT INTO `hr_loans_payment`(`loan_id`, `value_col`, `currency`, `source`, `date_col`) VALUES ('" + str(
            loan_id) + "','" + str(value) + "','" + str(currency) + "','" + str(source) + "','" + str(date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        return self.cursor.lastrowid

    @check_permission('hr_additional_costs', 'R')
    def fetchAdditionalCosts(self) -> list:
        query = "SELECT hr_additional_costs.*, currencies.name AS currency_name, COALESCE(accounts.name, '') AS account_name, COALESCE(opposite_accounts.name, '') AS opposite_account_name, hr_departments.name AS department_name FROM hr_additional_costs LEFT JOIN accounts ON hr_additional_costs.account_id = accounts.id LEFT JOIN accounts AS opposite_accounts ON hr_additional_costs.opposite_account_id = opposite_accounts.id JOIN currencies ON hr_additional_costs.currency_id = currencies.id JOIN hr_departments ON hr_additional_costs.department_id = hr_departments.id ORDER BY hr_additional_costs.date_col DESC;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_additional_costs', 'W')
    def addAdditionalCost(self, account, opposite_account, date, currency, department, statement, value) -> None:
        query = "INSERT INTO `hr_additional_costs` (`statement_col`, `account_id`, `department_id`, `opposite_account_id`, `value_col`, `currency_id`, `date_col`) VALUES ('" + str(statement) + "', NULLIF('" + str(account) + "', 'None'), '" + str(department) + "', NULLIF('" + str(opposite_account) + "', 'None'), '" + str(
            value) + "','" + str(currency) + "','" + str(date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_additional_costs', 'W')
    def removeAdditionalCost(self, additional_cost_id) -> None:
        query = "DELETE FROM `hr_additional_costs` WHERE `id`='" + str(additional_cost_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_settings', 'W')
    def saveHRSetting(self,
                      setting_work_day_sunday,
                      setting_work_day_monday,
                      setting_work_day_tuesday,
                      setting_work_day_wednesday,
                      setting_work_day_thursday,
                      setting_work_day_friday,
                      setting_work_day_saturday,
                      setting_cycle_unused_leaves,
                      setting_day_hours,
                      setting_insurance_opposite_account,
                      setting_departments_default_account,
                      setting_additional_costs_account,
                      setting_departments_additions_opposite_account,
                      setting_additions_opposite_account,
                      setting_salaries_opposite_account,
                      setting_departments_additions_account,
                      setting_salaries_account,
                      setting_additions_account,
                      setting_discounts_opposite_account,
                      setting_departments_default_opposite_account,
                      setting_departments_discounts_account,
                      setting_discounts_account,
                      setting_additional_costs_opposite_account,
                      setting_courses_costs_account,
                      setting_courses_costs_opposite_account,
                      setting_loans_account,
                      setting_departments_discounts_opposite_account,
                      setting_loans_opposite_account,
                      setting_insurance_account,
                      setting_extra_account,
                      setting_extra_opposite_account,
                      setting_week_start_day, setting_extra_normal,
                      setting_extra_high,
                      setting_month_duration,
                      setting_resource_recipients_account,
                      setting_priority_additions_salary,
                      setting_priority_discount_salary
                      ) -> None:
        # create a dictionary of the parameter name-value pairs
        params_dict = {k: v for k, v in inspect.getargvalues(inspect.currentframe()).locals.items() if k != 'self'}
        for var_name, var_value in params_dict.items():
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                query = "INSERT INTO hr_settings (name, value_col) VALUES ('" + str(var_name) + "', NULLIF('" + str(
                    var_value) + "', '')) ON DUPLICATE KEY UPDATE value_col = NULLIF('" + str(var_value) + "', '')"
            else:
                # SQLite doesn't support ON DUPLICATE KEY UPDATE
                query = "INSERT OR REPLACE INTO hr_settings (name, value_col) VALUES ('" + str(var_name) + "', NULLIF('" + str(
                    var_value) + "', ''))"
            print(query)
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

    @check_permission('hr_settings', 'R')
    def fetchHRSettings(self) -> list:
        query = "SELECT `name`, IFNULL(`value_col`, '') FROM `hr_settings`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_settings', 'R')
    def fetchHRSetting(self, setting_name, commit=True) -> dict:
        query = "SELECT `value_col` FROM `hr_settings` WHERE `name`='" + setting_name + "'"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_extra', 'R')
    def fetchEmployeeExtra(self, employee_id='', department_id='', from_date='', state='') -> list:
        query = "SELECT `hr_extra`.*, `accounts`.`name` AS `account_name`, `opposite_accounts`.`name` AS `opposite_account_name`, `currencies`.`name` AS `currency_name` FROM `hr_extra` LEFT JOIN `accounts` ON `hr_extra`.`account_id` = `accounts`.`id` LEFT JOIN `accounts` AS `opposite_accounts` ON `hr_extra`.`opposite_account_id` = `opposite_accounts`.`id` JOIN `currencies` ON `hr_extra`.`currency_id` = `currencies`.`id` WHERE (`hr_extra`.`employee_id` = '" + str(
            employee_id) + "' OR `hr_extra`.`department_id` = '" + str(
            department_id) + "') AND `hr_extra`.`start_date` >= COALESCE(NULLIF('" + str(
            from_date) + "',''), DATE('1000-01-01')) AND `hr_extra`.`state_col`=COALESCE(NULLIF('" + str(
            state) + "',''),`hr_extra`.`state_col`);"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_extra', 'W')
    def addExtras(self, employee_id, department_id, extra_date, extra_duration_hours, extra_duration_days, extra_value,
                  extra_currency,
                  extra_account, extra_opposite_account, extra_statement_input) -> None:
        query = "INSERT INTO `hr_extra`(`employee_id`, `department_id`, `start_date`, `value_col`, `duration_in_hours`, `duration_in_days`, `currency_id`, `statement_col`, `account_id`, `opposite_account_id`) VALUES ('" + str(
            employee_id) + "','" + str(department_id) + "','" + str(extra_date) + "','" + str(
            extra_value) + "','" + str(extra_duration_hours) + "','" + str(extra_duration_days) + "','" + str(
            extra_currency) + "','" + str(extra_statement_input) + "', NULLIF('" + str(extra_account) + "',''), NULLIF('" + str(
            extra_opposite_account) + "',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_extra', 'W')
    def removeExtra(self, extra_id) -> None:
        query = "DELETE FROM `hr_extra` WHERE `id`='" + str(extra_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_salaries', 'W')
    def addSalaryAdditionAndDiscount(self, selected_employee_id, type_col, start_date, repeatition, value_col, account_id, opposite_account_id, statement, currency_id) -> None:
        query = "INSERT INTO `hr_employees_salaries_additions_discounts`(`employee_id`, `type_col`, `start_date`, `repeatition`, `value_col`, `account_id`, `opposite_account_id`, `statement_col`, `currency_id`) VALUES ('" + str(
            selected_employee_id) + "', '" + str(type_col) + "', '" + str(start_date) + "', '" + str(
            repeatition) + "', '" + str(value_col) + "', '" + str(account_id) + "', '" + str(
            opposite_account_id) + "', '" + str(statement) + "', '" + str(currency_id) + "')"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_salaries', 'W')
    def removeSalaryAdditionAndDiscount(self, salaries_additions_discounts_id) -> None:
        query = "DELETE FROM `hr_employees_salaries_additions_discounts` WHERE `id`='" + str(salaries_additions_discounts_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_salaries', 'R')
    def fetchSalaryAdditionsAndDiscounts(self, employee_id, state='') -> list:
        query = "SELECT `hr_employees_salaries_additions_discounts`.*, `currencies`.`name` AS `currency_name`, `accounts`.`name` AS `account_name`, `opposite_accounts`.`name` AS `opposite_account_name`, COUNT(`hr_employees_salaries_additions_discounts_payments`.`id`) AS `num_payments` FROM `hr_employees_salaries_additions_discounts` INNER JOIN `currencies` ON `hr_employees_salaries_additions_discounts`.`currency_id` = `currencies`.`id` INNER JOIN `accounts` ON `hr_employees_salaries_additions_discounts`.`account_id` = `accounts`.`id` INNER JOIN `accounts` AS `opposite_accounts` ON `hr_employees_salaries_additions_discounts`.`opposite_account_id` = `opposite_accounts`.`id` LEFT JOIN `hr_employees_salaries_additions_discounts_payments` ON `hr_employees_salaries_additions_discounts`.`id` = `hr_employees_salaries_additions_discounts_payments`.`salaries_additions_discounts` WHERE `hr_employees_salaries_additions_discounts`.`state_col` = COALESCE(NULLIF('" + str(
            state) + "',''),`hr_employees_salaries_additions_discounts`.`state_col`) AND `hr_employees_salaries_additions_discounts`.`employee_id` = '" + str(employee_id) + "' GROUP BY `hr_employees_salaries_additions_discounts`.`id`"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_salaries', 'R')
    def fetchSalaryAdditionsAndDiscountPayments(self, salaries_additions_discounts_id) -> list:
        query = "SELECT * FROM `hr_employees_salaries_additions_discounts_payments` WHERE `salaries_additions_discounts` = '" + str(salaries_additions_discounts_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_salaries', 'W')
    def addSalaryAdditionAndDiscountPayment(self, salaries_additions_discounts_id, date) -> None:
        query = "INSERT INTO `hr_employees_salaries_additions_discounts_payments`(`salaries_additions_discounts`, `date_col`) VALUES ('" + str(
            salaries_additions_discounts_id) + "', '" + str(date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_leaves', 'R')
    def fetchLeaveTypes(self) -> list:
        query = "SELECT * FROM `hr_leave_types`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_leaves', 'W')
    def removeLeaveType(self, leave_type_id) -> None:
        query = "DELETE FROM `hr_leave_types` WHERE `id`='" + str(leave_type_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('hr_positions', 'W')
    def addNewPosition(self, position_name, position_salary, position_salary_currency, position_notes) -> None:
        query = "INSERT INTO `hr_positions` (`position_name`, `salary`, `currency_id`, `notes`) VALUES ('" + str(position_name) + "', '" + str(position_salary) + "', '" + str(position_salary_currency) + "', '" + str(position_notes) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def savePosition(self, selected_position_id, position_name, position_salary,
                     position_salary_currency,
                     position_notes) -> None:
        query = "UPDATE `hr_positions` SET `position_name`='" + str(position_name) + "', `salary`='" + str(
            position_salary) + "', `currency_id`='" + str(position_salary_currency) + "', `notes`='" + str(
            position_notes) + "' WHERE `id`='" + str(selected_position_id) + "'"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_positions', 'W')
    def removePosition(self, position_id) -> None:
        query = "DELETE FROM `hr_positions` WHERE `id`='" + str(position_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('hr_leaves', 'W')
    def saveLeave(self, selected_employee_id, leave_type_id, alternative_id, duration_in_hours, duration_in_days,
                  start_date) -> None:
        query = "INSERT INTO `hr_leaves`(`employee_id`, `leave_type_id`, `alternative_id`, `duration_in_hours`, `duration_in_days`, `start_date`) VALUES ('" + str(
            selected_employee_id) + "','" + str(leave_type_id) + "','" + str(alternative_id) + "','" + str(
            duration_in_hours) + "','" + str(duration_in_days) + "','" + str(start_date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_leaves', 'W')
    def removeLeave(self, leave_id) -> None:
        query = "DELETE FROM `hr_leaves` WHERE `id`='" + str(leave_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'R')
    def fetchCourses(self) -> list:
        query = "SELECT `hr_courses`.*, `account`.`name` as `account_name`, `opposite_account`.`name` as `opposite_account` FROM `hr_courses` LEFT JOIN `accounts` as `account` ON `hr_courses`.`account_id` = `account`.`id` LEFT JOIN `accounts` as `opposite_account` ON `hr_courses`.`opposite_account_id` = `opposite_account`.`id` ORDER BY `date_col` DESC;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_courses', 'R')
    def fetchSelectedCourse(self, id) -> dict:
        query = "SELECT `hr_courses`.*, `account`.`name` as `account_name`, `opposite_account`.`name` as `opposite_account` FROM `hr_courses` LEFT JOIN `accounts` as `account` ON `hr_courses`.`account_id` = `account`.`id` LEFT JOIN `accounts` as `opposite_account` ON `hr_courses`.`opposite_account_id` = `opposite_account`.`id` WHERE `hr_courses`.`id`='" + str(
            id) + "';"
        # print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('hr_courses', 'W')
    def addNewCourse(self, title, cost, providor, location, account_id, opposite_account_id, currency_id, date) -> int:
        query = "INSERT INTO `hr_courses`(`title`, `cost`, `providor`, `location`, `account_id`, `opposite_account_id`, `currency_id`, `date_col`) VALUES (NULLIF('" + str(title) + "',''),NULLIF('" + str(cost) + "',''), NULLIF('" + str(providor) + "',''), NULLIF('" + str(location) + "',''), NULLIF('" + str(account_id) + "',''), NULLIF('" + str(opposite_account_id) + "',''), NULLIF('" + str(currency_id) + "',''), NULLIF('" + str(date) + "',''))"
        print(query)
        self.cursor.execute(query)
        course_id = self.cursor.lastrowid
        self.sqlconnector.conn.commit()
        return course_id

    @check_permission('hr_courses', 'W')
    def saveCourse(self, selected_course_id, title, cost, providor, location, account_id, opposite_account_id,
                   currency_id, date) -> None:
        query = "UPDATE `hr_courses` SET `title`='" + str(title) + "', `providor`='" + str(
            providor) + "', `account_id`= NULLIF('" + str(account_id) + "',''), `opposite_account_id`= NULLIF('" + str(
            opposite_account_id) + "',''), `cost`='" + str(cost) + "', `currency_id`='" + str(
            currency_id) + "', `date_col`='" + str(date) + "', `location`='" + str(location) + "' WHERE `id`='" + str(
            selected_course_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'W')
    def addCourseEmployee(self, course_id, employee_id, gpa):
        query = "INSERT INTO `hr_course_employees`(`course_id`, `employee_id`, `gpa`) VALUES ('" + str(
            course_id) + "','" + str(employee_id) + "','" + str(gpa) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_courses', 'W')
    def removeCourseEmployee(self, course_employee_id) -> None:
        query = "DELETE FROM `hr_course_employees` WHERE `id`='" + str(course_employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_loans', 'R')
    def fetchLoansOfEmployee(self, employee_id, from_date='') -> list:
        query = "SELECT hr_loans.*, currencies.name AS currency_name, accounts.name AS account_name, opposite_accounts.name AS opposite_account_name, COALESCE(payments.total_payments, 0) AS total_payments, hr_loans.value_col - COALESCE(payments.total_payments, 0) AS remaining_amount, subtract_currencies.name AS subtract_currency_name FROM hr_loans JOIN currencies ON hr_loans.currency = currencies.id JOIN accounts ON hr_loans.account_id = accounts.id JOIN accounts AS opposite_accounts ON hr_loans.opposite_account_id = opposite_accounts.id LEFT JOIN currencies AS subtract_currencies ON hr_loans.subtract_currency = subtract_currencies.id LEFT JOIN (SELECT hr_loans_payment.loan_id, SUM(hr_loans_payment.value_col) AS total_payments FROM hr_loans_payment GROUP BY hr_loans_payment.loan_id) AS payments ON hr_loans.id = payments.loan_id WHERE hr_loans.employee_id = '" + str(
            employee_id) + "' AND hr_loans.date_col >= COALESCE(NULLIF('" + str(from_date) + "', ''), DATE('1000-01-01'));"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    @check_permission('hr_leaves', 'W')
    def addLeaveType(self, name, days, period, paid) -> None:
        query = "INSERT INTO `hr_leave_types` (`name`, `days`, `period`, `paid`) VALUES ('" + str(name) + "', '" + str(
            days) + "', '" + str(period) + "', '" + str(paid) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    def fetchEmployeeLeavesBalance(self, employee_id):
        # get total paid leaved allowed
        query = "SELECT SUM(`days`) FROM `hr_leave_types` WHERE `paid` is FALSE"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if rows:
            total_unpaid_leaves_month = rows[0]
            if total_unpaid_leaves_month:
                total_unpaid_leaves_year = total_unpaid_leaves_month * 12
            else:
                total_unpaid_leaves_year = 0
        self.sqlconnector.conn.commit()

        # get total paid leaved allowed
        query = "SELECT SUM(`days`) FROM `hr_leave_types` WHERE `paid` is TRUE"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if rows:
            total_paid_leaves_month = rows[0]
            if total_paid_leaves_month:
                total_paid_leaves_year = total_paid_leaves_month * 12
            else:
                total_paid_leaves_year = 0
        self.sqlconnector.conn.commit()

        # get total unpaid leaves take by employee since year start
        # get the current date
        current_year = datetime.date.today().year

        # Check database engine type and use appropriate YEAR function
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            # MySQL and other databases use YEAR function
            query = "SELECT SUM(`duration_in_days`) FROM `hr_leaves` JOIN `hr_leave_types` ON `hr_leaves`.`leave_type_id`=`hr_leave_types`.`id` WHERE YEAR(`start_date`)='" + str(
                current_year) + "' AND `hr_leave_types`.`paid`='0' AND `hr_leaves`.`employee_id`='" + str(employee_id) + "'"
        else:
            # SQLite doesn't have YEAR function, use strftime instead
            query = "SELECT SUM(`duration_in_days`) FROM `hr_leaves` JOIN `hr_leave_types` ON `hr_leaves`.`leave_type_id`=`hr_leave_types`.`id` WHERE strftime('%Y', `start_date`)='" + str(
                current_year) + "' AND `hr_leave_types`.`paid`='0' AND `hr_leaves`.`employee_id`='" + str(employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if rows:
            total_unpaid_taken_this_year = rows[0]
        if not total_unpaid_taken_this_year:
            total_unpaid_taken_this_year = 0

        # Check database engine type and use appropriate YEAR function
        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            # MySQL and other databases use YEAR function
            query = "SELECT SUM(`duration_in_days`) FROM `hr_leaves` JOIN `hr_leave_types` ON `hr_leaves`.`leave_type_id`=`hr_leave_types`.`id` WHERE YEAR(`start_date`)='" + str(
                current_year) + "' AND `hr_leave_types`.`paid`='1' AND `hr_leaves`.`employee_id`='" + str(employee_id) + "'"
        else:
            # SQLite doesn't have YEAR function, use strftime instead
            query = "SELECT SUM(`duration_in_days`) FROM `hr_leaves` JOIN `hr_leave_types` ON `hr_leaves`.`leave_type_id`=`hr_leave_types`.`id` WHERE strftime('%Y', `start_date`)='" + str(
                current_year) + "' AND `hr_leave_types`.`paid`='1' AND `hr_leaves`.`employee_id`='" + str(employee_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        if rows:
            total_paid_taken_this_year = rows[0]
        if not total_paid_taken_this_year:
            total_paid_taken_this_year = 0

        if int(total_unpaid_leaves_year) > -1 and int(total_unpaid_taken_this_year) > -1:
            unpaid_balance = int(total_unpaid_leaves_year) - int(total_unpaid_taken_this_year)

        if int(total_paid_leaves_year) > -1 and int(total_paid_taken_this_year) > -1:
            paid_balance = int(total_paid_leaves_year) - int(total_paid_taken_this_year)

        result = {"paid_balance": paid_balance, "unpaid_balance": unpaid_balance}
        return result

    @check_permission('hr_salaries', 'W')
    def addSalariesBlock(self, salaries_from_date, salaries_to_date) -> int:
        # Get the current date
        current_date = datetime.datetime.now()
        # Get the date part of the current date
        date_only = current_date.date()
        # Convert the date_only to ISO format
        iso_date = date_only.isoformat()

        query = "INSERT INTO `hr_salary_blocks`(`from_date`, `to_date`, `date_col`) VALUES ('" + str(
            salaries_from_date) + "','" + str(salaries_to_date) + "','" + str(iso_date) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('hr_salaries', 'W')
    def addSalariesBlockEntry(self, salaries_block_id, employee_id, statement, value, currency) -> None:
        query = "INSERT INTO `hr_salary_block_entries` (`salary_block_id`, `employee_id`, `statement_col`, `value_col`, `currency`) VALUES ('" + str(
            salaries_block_id) + "', '" + str(employee_id) + "', '" + statement + "', '" + str(
            value) + "', NULLIF('" + currency + "', ''))"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_salaries', 'R')
    def fetchPayrolls(self) -> list:
        query = "SELECT * FROM `hr_salary_blocks` ORDER BY `to_date` DESC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_salaries', 'R')
    def fetchPayrollsDetails(self, from_date='', to_date='', department='', position=''):
        query = "SELECT hr_salary_block_entries.*, hr_salary_blocks.from_date, hr_salary_blocks.to_date, hr_salary_blocks.date_col FROM hr_salary_block_entries JOIN hr_salary_blocks ON hr_salary_block_entries.salary_block_id = hr_salary_blocks.id JOIN hr_employees ON hr_salary_block_entries.employee_id = hr_employees.id LEFT JOIN (SELECT employee_id, department_id, position_id, MAX(date_col) as max_date FROM hr_employees_transfers GROUP BY employee_id) AS transfers ON hr_employees.id = transfers.employee_id WHERE (transfers.position_id = COALESCE(NULLIF('" + str(position) + "', ''), transfers.position_id));"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchDepartmentPayrolls(self, department_id, from_date='', to_date=''):
        query = "SELECT hr_salary_block_entries.*, hr_salary_blocks.from_date, hr_salary_blocks.to_date, hr_salary_blocks.date_col FROM hr_salary_block_entries JOIN hr_salary_blocks ON hr_salary_block_entries.salary_block_id = hr_salary_blocks.id JOIN hr_employees ON hr_salary_block_entries.employee_id = hr_employees.id LEFT JOIN (SELECT employee_id, department_id, position_id, MAX(date_col) as max_date FROM hr_employees_transfers GROUP BY employee_id) AS transfers ON hr_employees.id = transfers.employee_id WHERE (transfers.department_id = COALESCE(NULLIF('" + str(department_id) + "', ''), transfers.department_id));"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_salaries', 'R')
    def fetchPayrollDetails(self, payroll_id='', from_date='', to_date='', statement='', super=False, commit=True) -> list:
        # super: defines whether to select the records with sarly_block range that falls WITHIN from_date-to_date or out of it.
        # if it is false, select the records that falls within the passed range.
        # if it is true, select the records which forms a superset that includes the records of the range from_date-to_date
        # you can use super=True to get the salary block that contains specific salaries costs in a specific range of time
        if super:
            query = "SELECT sbe.id, sbe.salary_block_id, sbe.employee_id, sbe.statement_col, sbe.value_col, sbe.currency, e.name, c.name AS currency_name, sb.from_date, sb.to_date FROM hr_salary_block_entries AS sbe LEFT JOIN hr_employees AS e ON sbe.employee_id = e.id LEFT JOIN currencies AS c ON sbe.currency = c.id LEFT JOIN hr_salary_blocks AS sb ON sbe.salary_block_id = sb.id WHERE sbe.salary_block_id=COALESCE(NULLIF('" + str(
                payroll_id) + "',''),salary_block_id) AND `sb`.`from_date` <= COALESCE(NULLIF('" + str(
                from_date) + "', ''),DATE('1000-01-01')) AND `sb`.`to_date` >= COALESCE(NULLIF('" + str(
                to_date) + "', ''),DATE('9999-12-31')) AND `sbe`.`statement_col`=COALESCE(NULLIF('" + str(
                statement) + "',''),`sbe`.`statement_col`)"
        else:
            query = "SELECT sbe.id, sbe.salary_block_id, sbe.employee_id, sbe.statement_col, sbe.value_col, sbe.currency, e.name, c.name AS currency_name, sb.from_date, sb.to_date FROM hr_salary_block_entries AS sbe LEFT JOIN hr_employees AS e ON sbe.employee_id = e.id LEFT JOIN currencies AS c ON sbe.currency = c.id LEFT JOIN hr_salary_blocks AS sb ON sbe.salary_block_id = sb.id WHERE sbe.salary_block_id=COALESCE(NULLIF('" + str(
                payroll_id) + "',''),salary_block_id) AND `sb`.`from_date` >= COALESCE(NULLIF('" + str(
                from_date) + "', ''),DATE('1000-01-01')) AND `sb`.`to_date` <= COALESCE(NULLIF('" + str(
                to_date) + "', ''),DATE('9999-12-31')) AND `sbe`.`statement_col`=COALESCE(NULLIF('" + str(
                statement) + "',''),`sbe`.`statement_col`)"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        if commit:
            self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_insurance', 'R')
    def fetchInsurancePayrolls(self) -> list:
        query = "SELECT * FROM `hr_insurance_blocks` ORDER BY `to_date` DESC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_insurance', 'W')
    def addInsuranceBlock(self, insurance_from_date, insurance_to_date) -> int:
        # Get the current date
        current_date = datetime.datetime.now()
        # Get the date part of the current date
        date_only = current_date.date()
        # Convert the date_only to ISO format
        iso_date = date_only.isoformat()

        query = "INSERT INTO `hr_insurance_blocks`(`from_date`, `to_date`, `date_col`) VALUES ('" + insurance_from_date + "','" + insurance_to_date + "','" + iso_date + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()
        last_id = self.cursor.lastrowid
        return last_id

    @check_permission('hr_insurance', 'W')
    def addInsuranceBlockEntry(self, insurance_block_id, employee_id, cycles, value, currency) -> None:
        query = "INSERT INTO `hr_insurance_block_entries` (`insurance_block_id`, `employee_id`, cycles, `value_col`, `currency`) VALUES ('" + str(
            insurance_block_id) + "', '" + str(employee_id) + "', '" + str(cycles) + "', '" + str(
            value) + "', NULLIF('" + currency + "', ''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('hr_insurance', 'R')
    def fetchInsurancePayrollDetails(self, insurance_payroll_id) -> list:
        query = "SELECT hr_insurance_block_entries.id, hr_insurance_block_entries.insurance_block_id, hr_insurance_block_entries.employee_id, hr_insurance_block_entries.cycles, hr_insurance_block_entries.value_col, hr_insurance_block_entries.currency, hr_employees.name, currencies.name AS currency_name, hr_insurance_blocks.from_date, hr_insurance_blocks.to_date FROM hr_insurance_block_entries LEFT JOIN hr_employees ON hr_insurance_block_entries.employee_id = hr_employees.id LEFT JOIN currencies ON hr_insurance_block_entries.currency = currencies.id LEFT JOIN hr_insurance_blocks ON hr_insurance_block_entries.insurance_block_id = hr_insurance_blocks.id WHERE hr_insurance_block_entries.insurance_block_id = ('" + str(insurance_payroll_id) + "');"

        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('hr_insurance', 'R')
    def fetchInsurancePayrollsDetails(self, from_date='', to_date='') -> list:
        query = "SELECT hr_insurance_block_entries.id, hr_insurance_block_entries.insurance_block_id, hr_insurance_block_entries.employee_id, hr_insurance_block_entries.cycles, hr_insurance_block_entries.value_col, hr_insurance_block_entries.currency, hr_employees.name, currencies.name AS currency_name, hr_insurance_blocks.from_date, hr_insurance_blocks.to_date FROM hr_insurance_block_entries LEFT JOIN hr_employees ON hr_insurance_block_entries.employee_id = hr_employees.id LEFT JOIN currencies ON hr_insurance_block_entries.currency = currencies.id LEFT JOIN hr_insurance_blocks ON hr_insurance_block_entries.insurance_block_id = hr_insurance_blocks.id WHERE hr_insurance_blocks.from_date >= '" + str(from_date) + "'" + " AND hr_insurance_blocks.to_date <= '" + str(to_date) + "'"

        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchAvgfInsurance(self, from_date='', to_date=''):
        query = "SELECT AVG(`hr_insurance_block_entries`.`value_col`) as avg_insurance, SUM(`hr_insurance_block_entries`.`value_col`) as sum_insurance FROM `hr_insurance_block_entries` JOIN `hr_insurance_blocks` ON `hr_insurance_block_entries`.`insurance_block_id` = `hr_insurance_blocks`.`id` WHERE `hr_insurance_blocks`.`from_date` >= COALESCE(NULLIF('" + str(from_date) + "', ''), `hr_insurance_blocks`.`from_date`) AND `hr_insurance_blocks`.`to_date` <= COALESCE(NULLIF('" + str(to_date) + "', ''), `hr_insurance_blocks`.`to_date`)"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def fetchPositionAvgfInsurance(self, from_date='', to_date=''):
        query = "SELECT `hr_positions`.`id` AS position_id, `hr_positions`.`position_name`, AVG(`hr_insurance_block_entries`.`value_col`) as avg_insurance, SUM(`hr_insurance_block_entries`.`value_col`) as sum_insurance FROM `hr_insurance_block_entries` JOIN `hr_insurance_blocks` ON `hr_insurance_block_entries`.`insurance_block_id` = `hr_insurance_blocks`.`id` JOIN `hr_employees` ON `hr_insurance_block_entries`.`employee_id` = `hr_employees`.`id` JOIN (SELECT `employee_id`, `position_id`, MAX(`date_col`) as max_date FROM `hr_employees_transfers` GROUP BY `employee_id`) AS latest_transfers ON `hr_employees`.`id` = latest_transfers.`employee_id` JOIN `hr_positions` ON latest_transfers.`position_id` = `hr_positions`.`id` WHERE `hr_insurance_blocks`.`from_date` >= COALESCE(NULLIF('" + str(from_date) + "', ''), `hr_insurance_blocks`.`from_date`) AND `hr_insurance_blocks`.`to_date` <= COALESCE(NULLIF('" + str(to_date) + "', ''), `hr_insurance_blocks`.`to_date`) GROUP BY `hr_positions`.`id`, `hr_positions`.`position_name`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def fetchDepartmentAvgfInsurance(self, from_date='', to_date=''):
        query = "SELECT `hr_departments`.`id` AS department_id, `hr_departments`.`name`, AVG(`hr_insurance_block_entries`.`value_col`) as avg_insurance, SUM(`hr_insurance_block_entries`.`value_col`) as sum_insurance FROM `hr_insurance_block_entries` JOIN `hr_insurance_blocks` ON `hr_insurance_block_entries`.`insurance_block_id` = `hr_insurance_blocks`.`id` JOIN `hr_employees` ON `hr_insurance_block_entries`.`employee_id` = `hr_employees`.`id` JOIN (SELECT `employee_id`, `department_id`, MAX(`date_col`) as max_date FROM `hr_employees_transfers` GROUP BY `employee_id`) AS latest_transfers ON `hr_employees`.`id` = latest_transfers.`employee_id` JOIN `hr_departments` ON latest_transfers.`department_id` = `hr_departments`.`id` WHERE `hr_insurance_blocks`.`from_date` >= COALESCE(NULLIF('" + str(from_date) + "', ''), `hr_insurance_blocks`.`from_date`) AND `hr_insurance_blocks`.`to_date` <= COALESCE(NULLIF('" + str(to_date) + "', ''), `hr_insurance_blocks`.`to_date`) GROUP BY `hr_departments`.`id`, `hr_departments`.`name`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def addMachine(self, machine_name):
        query = "INSERT INTO machines (name) VALUES ('" + str(machine_name) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def fetchMachine(self, machine_id) -> list:
        query = "SELECT `machines`.*, `invoice_items`.`unit_price`, `invoice_items`.`currency_id` FROM `machines` LEFT JOIN `invoice_items` ON `machines`.`invoice_item_id`=`invoice_items`.`id` WHERE `machines`.`id`='" + str(
            machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        return rows

    @check_permission('machines', 'R')
    def fetchMachines(self) -> list:
        query = "SELECT * FROM `machines` ORDER BY `name`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def updateMachine(self, machine_id, machine_account, machine_opposite_account, name, estimated_waste_value, machine_standard_age, machine_notes,
                      machine_invoice_item_id,
                      estimated_waste_currency, estimated_waste_account):
        query = "UPDATE `machines` SET `name` = '" + str(name) + "', `years_age` = NULLIF('" + str(
            machine_standard_age) + "', ''), `estimated_waste_value` = NULLIF('" + str(
            estimated_waste_value) + "', ''), `estimated_waste_currency` = NULLIF('" + str(
            estimated_waste_currency) + "', ''), `estimated_waste_account` = NULLIF('" + str(
            estimated_waste_account) + "', ''), `invoice_item_id` = NULLIF('" + str(
            machine_invoice_item_id) + "', ''), `notes` = NULLIF('" + str(
            machine_notes) + "', ''), `account` = NULLIF('" + str(
            machine_account) + "', ''), `opposite_account` = NULLIF('" + str(
            machine_opposite_account) + "', '') WHERE `id` = '" + str(machine_id) + "'"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def fetchTotalMachineWork(self, machine_id) -> int:
        query = "SELECT SUM(duration) as total_duration FROM `manufacture_machines` WHERE `machine_id` = '" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row['total_duration'] if row['total_duration'] else 0

    @check_permission('machines', 'R')
    def fetchManufactureMachine(self, machine_id) -> list:
        query = "SELECT * FROM `manufacture_machines` WHERE `machine_id` = '" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def removeMachine(self, machine_id) -> None:
        query = "DELETE FROM `machines` WHERE `id`='" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'W')
    def addMachineMode(self, machine_id, mode) -> None:
        query = "INSERT INTO machine_modes(machine_id, name) VALUES ('" + str(machine_id) + "','" + str(mode) + "')"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def removeMachineMode(self, machine_mode_id) -> None:
        query = "DELETE FROM `machine_modes` WHERE `id`='" + str(machine_mode_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchMachineModeResources(self, machine_id) -> list:
        query = "SELECT `mode_resources`.*, `resources`.`name` as `resource_name`, `resources`.`id` as `resource_id`, `machine_modes`.`name` as `mode_name`, `units`.`name` as `consumption_unit`, `resources_costs`.`value_col` as `resource_cost`, `currencies`.`name` as `currency_name` FROM `mode_resources` JOIN `resources` ON `mode_resources`.`resource_id` = `resources`.`id` JOIN `machine_modes` ON `mode_resources`.`mode_id` = `machine_modes`.`id` JOIN `units` ON `mode_resources`.`unit` = `units`.`id` LEFT JOIN `resources_costs` ON `mode_resources`.`resource_id` = `resources_costs`.`resource_id` LEFT JOIN `currencies` ON `resources_costs`.`currency_id` = `currencies`.`id` WHERE `machine_modes`.`machine_id` = '" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('machines', 'R')
    def fetchMachineModes(self, machine_id) -> list:
        query = "SELECT * FROM `machine_modes` WHERE `machine_id`='" + str(machine_id) + "' ORDER BY `date_col` DESC"
        # print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('machines', 'W')
    def deleteMachineMode(self, mode_id) -> None:
        query = "DELETE FROM `machine_modes` WHERE `id`='" + str(mode_id) + "'"
        # print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchResources(self) -> list:
        query = "SELECT `resources`.*, `resource_cost`.`value_col` as `cost`, `resource_cost`.`unit_id`, `resource_cost`.`unit_name` FROM `resources` LEFT JOIN( SELECT rc.*, `units`.`name` as `unit_name` FROM resources_costs rc INNER JOIN( SELECT resource_id, MAX(DATE_col) AS max_date FROM resources_costs GROUP BY resource_id ) subquery ON rc.resource_id = subquery.resource_id AND rc.date_col = subquery.max_date JOIN `units` ON `rc`.`unit_id`=`units`.`id` ) AS `resource_cost` ON `resources`.`id` = `resource_cost`.`resource_id`;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def addResource(self, resouce_name) -> None:
        query = "INSERT INTO resources (name) VALUES ('" + str(resouce_name) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def updateResource(self, selected_resource_id, resource_name, resource_account, resource_notes) -> None:
        query = "UPDATE `resources` SET `name`='" + str(resource_name) + "',`account_id`=NULLIF('" + str(
            resource_account) + "',''),`notes`=NULLIF('" + str(resource_notes) + "','') WHERE `id`='" + str(selected_resource_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def removeResource(self, resource_id) -> None:
        query = "DELETE FROM `resources` WHERE `id`='" + str(resource_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def addResourceCost(self, selected_resource_id, resource_cost_per_minute, resource_cost_currency,
                        resource_cost_unit, resource_notes) -> None:
        query = "INSERT INTO `resources_costs`(`resource_id`, `value_col`, `currency_id`, `unit_id`, `notes`) VALUES ('" + str(
            selected_resource_id) + "', '" + str(resource_cost_per_minute) + "', '" + str(
            resource_cost_currency) + "', '" + str(resource_cost_unit) + "', '" + str(resource_notes) + "')"

        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def removeResourceCost(self, resource_cost_id) -> None:
        print('DATABASE> REMOVE RESOURCE COST')
        query = "DELETE FROM `resources_costs` WHERE `id`='" + str(resource_cost_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchResource(self, selected_resource_id) -> list:
        query = "SELECT * FROM `resources` WHERE `id`='" + str(selected_resource_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        return rows

    @check_permission('machines', 'W')
    def addModeResource(self, mode_id, resource_id, consumption_per_minute, unit) -> None:
        query = "INSERT INTO `mode_resources` (`mode_id`, `resource_id`, `consumption_per_minute`, `unit`) VALUES (" + str(
            mode_id) + ", '" + str(resource_id) + "', '" + str(consumption_per_minute) + "', '" + str(unit) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def removeModeResource(self, mode_id) -> None:
        query = "DELETE FROM `mode_resources` WHERE `id`='" + str(mode_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def fetchModeResources(self, mode_id) -> list:
        query = "SELECT `mode_resources`.*, `resources`.`name` as `resource_name`, `units`.`name` as `unit_name` FROM `mode_resources` JOIN `resources` ON `mode_resources`.`resource_id`=`resources`.`id` JOIN `units` ON `mode_resources`.`unit`=`units`.`id` WHERE `mode_resources`.`mode_id`='" + str(
            mode_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('machines', 'R')
    def fetchResouceCosts(self, resource_id) -> list:
        query = "SELECT `resources_costs`.*, `currencies`.`name` AS `currency_name`, `units`.`name` AS `unit_name` FROM `resources_costs` JOIN `currencies` ON `resources_costs`.`currency_id` = `currencies`.`id` JOIN `units` ON `resources_costs`.`unit_id`=`units`.`id` WHERE `resources_costs`.`resource_id` = '" + str(
            resource_id) + "' ORDER BY `resources_costs`.`date_col` DESC;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows



    @check_permission('machines', 'W')
    def addProductionLine(self, name , notes='') -> None:
        query = f"INSERT INTO `production_lines`(`name`, `notes`) VALUES ('{str(name)}', NULLIF('{str(notes)}',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'W')
    def updateProductionLine(self, production_line_id, name, notes) -> None:
        query = f"UPDATE `production_lines` SET `name`='{str(name)}', `notes`=NULLIF('{str(notes)}','') WHERE `id`='{str(production_line_id)}'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchProductionLines(self) -> list:
        print("DATABASE> FETCH PRODUCTION LINES")
        query = "SELECT `id`, `name`, `notes` FROM `production_lines` ORDER BY `id` ASC"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'R')
    def fetchProductionLine(self, production_line_id) -> list:
        print("DATABASE> FETCH PRODUCTION LINES")
        query = "SELECT * FROM `production_lines` WHERE `id`= " + str(production_line_id) + ";"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row
    


    @check_permission('machines', 'W')
    def removeProductionLine(self, production_line_id) -> None:
        print("DATABASE> REMOVE PRODUCTION LINE")
        query = "DELETE FROM `production_lines` WHERE `id`='" + str(production_line_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchProductionLineMachines(self, production_line_id=None, machine_id=None) -> list:
        print("DATABASE> FETCH PRODUCTION LINE MACHINES")
        query = "SELECT `machine_production_lines`.*, `machines`.`name` as `machine_name` FROM `machine_production_lines` JOIN `machines` ON `machine_production_lines`.`machine_id`=`machines`.`id` WHERE `machine_production_lines`.`production_line_id`='" + str(production_line_id) + "'"
        if machine_id is not None:  # Add condition for machine_id
            query += " AND `machine_production_lines`.`machine_id`='" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows


    @check_permission('machines', 'W')
    def addProductionLineMachine(self, production_line_id, machine_id, machine_notes='') -> None:
        query = f"INSERT INTO `machine_production_lines`(`production_line_id`, `machine_id`, `machine_notes`) VALUES ('{str(production_line_id)}', '{str(machine_id)}', NULLIF('{str(machine_notes)}',''))"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()



    @check_permission('machines', 'W')
    def removeProductionLineMachine(self, production_line_machine_id) -> None:
        query = "DELETE FROM `machine_production_lines` WHERE `id`='" + str(production_line_machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'W')
    def addMaterialMachine(self, material_id, machine_id, machine_mode, use_duration, exclusive) -> None:
        query = "INSERT INTO `materials_machines`(`material_id`, `machine_id`, `mode_id`, `usage_duration`, `exclusive`) VALUES (" + str(
            material_id) + ",'" + str(machine_id) + "','" + str(machine_mode) + "','" + str(use_duration) + "','" + str(
            exclusive) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'W')
    def deleteMaterialMachine(self, machine_usage_id) -> None:
        query = "DELETE FROM `materials_machines` WHERE `id`='" + str(machine_usage_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def fetchMaterialMachines(self, material_id) -> list:
        query = "SELECT `materials_machines`.*, `machines`.`name` as `machine_name`, `machine_modes`.`name` as `mode_name`, `machines`.`account` as `account_id`, `machines`.`opposite_account` as `opposite_account_id`, a1.name as account_name, a2.name as opposite_account_name FROM `materials_machines` JOIN `machines` ON `materials_machines`.`machine_id`=`machines`.`id` JOIN `machine_modes` ON `materials_machines`.`mode_id`=`machine_modes`.`id` LEFT JOIN accounts a1 ON machines.account = a1.id LEFT JOIN accounts a2 ON machines.opposite_account = a2.id WHERE `materials_machines`.`material_id`='" + str(
            material_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit
        return rows

    @check_permission('machines', 'R')
    def fetchMachineMaintenanceOperations(self, machine_id) -> list:
        query = "SELECT machine_maintenance.*, machines.name as machine_name FROM `machine_maintenance` JOIN machines ON machine_maintenance.machine_id = machines.id WHERE machine_maintenance.machine_id = '" + str(machine_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def addMaintenanceOperation(self, name, machine_id, account, opposite_account, start_period, end_period, cost, statment_col=None) -> None:
        query = "INSERT INTO `machine_maintenance`(`name`, `machine_id`, `account`, `opposite_account`, `start_date`, `end_date`, `cost`, `statment_col`) VALUES ('" + str(name) + "', '" + str(machine_id) + "', '" + str(account) + "', '" + str(opposite_account) + "', '" + str(start_period) + "', '" + str(end_period) + "', '" + str(cost) + "', '" + str(statment_col) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    @check_permission('machines', 'R')
    def fetchMaintenanceOperation(self, maintenance_id) -> list:
        query = "SELECT * FROM `machine_maintenance` WHERE `id` = '" + str(maintenance_id) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row

    @check_permission('machines', 'R')
    def fetchMaintenanceWorkers(self, maintenance_id=None) -> list: #edit
        query = "SELECT maintenance_workers.*, hr_employees.name as name FROM `maintenance_workers` JOIN `hr_employees` ON maintenance_workers.employee_id = hr_employees.id WHERE `maintenance_id` = '" + str(maintenance_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'W')
    def addMaintenanceWorker(self, maintenance_id, employee_id):
        query = "INSERT INTO `maintenance_workers`(`maintenance_id`, `employee_id`) VALUES ('" + str(maintenance_id) + "', '" + str(employee_id) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def removeMaintenanceWorker(self, worker_id):
        query = "DELETE FROM `maintenance_workers` WHERE `id` = '" + str(worker_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def removeMachineMaintenance(self, maintenance_id):
        query = "DELETE FROM `machine_maintenance` WHERE `id` = '" + str(maintenance_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def addMachineMaintenance(self, machine_id, maintenance_start_date, maintenance_end_date, maintenance_type, maintenance_cost, statment_col):
        query = "INSERT INTO `machine_maintenance`(`machine_id`, `maintenance_start_date`, `maintenance_end_date`, `maintenance_type`, `maintenance_cost`, `statment_col`) VALUES ('" + str(machine_id) + "', '" + str(maintenance_start_date) + "', '" + str(maintenance_end_date) + "', '" + str(maintenance_type) + "', '" + str(maintenance_cost) + "', '" + str(statment_col) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def updateMachineMaintenance(self, maintenance_id, start_date, end_date, maintenance_type, cost, statment_col, name, account, opposite_account):
        query = "UPDATE `machine_maintenance` SET `start_date` = '" + str(start_date) + "', `end_date` = '" + str(end_date) + "', `maintenance_type` = '" + str(maintenance_type) + "', `cost` = '" + str(cost) + "', `statment_col` = '" + str(statment_col) + "', `name` = '" + str(name) + "', `account` = '" + str(account) + "', `opposite_account` = '" + str(opposite_account) + "' WHERE `id` = '" + str(maintenance_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def fetchMaintenanceOperationMaterials(self, maintenance_id):
        query = "SELECT maintenance_operation_materials.*, units.name as `unit_name` FROM `maintenance_operation_materials` JOIN `units` ON maintenance_operation_materials.unit = units.id WHERE `maintenance_operation` = '" + str(maintenance_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'R')
    def addMaintenanceOperationMaterial(self, maintenance_id, material_id, quantity, unit):
        query = "INSERT INTO `maintenance_operation_materials`(`maintenance_operation`, `maintenance_material_id`, `quantity`, `unit`) VALUES ('" + str(maintenance_id) + "', '" + str(material_id) + "', '" + str(quantity) + "', '" + str(unit) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def removeMaintenanceMaterial(self, material_id):
        query = "DELETE FROM `maintenance_operation_materials` WHERE `id`='" + str(material_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchMaintenanceMaterials(self):
        query = "SELECT * FROM `maintenance_materials`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    @check_permission('machines', 'R')
    def fetchModeCosts(self, mode_id):
        query = "SELECT mode_resources.consumption_per_minute, mode_resources.unit, resources_costs.value_col, resources_costs.currency_id, resources.account_id as `resource_account_id`, resources.name as `resource_name`, resources.id as `resource_id` FROM mode_resources JOIN( SELECT resource_id, MAX(date_col) AS max_date FROM resources_costs GROUP BY resource_id ) AS latest_costs ON mode_resources.resource_id = latest_costs.resource_id JOIN resources_costs ON mode_resources.resource_id = resources_costs.resource_id AND resources_costs.date_col = latest_costs.max_date JOIN resources ON resources.id=mode_resources.resource_id WHERE mode_resources.mode_id ='" + str(
            mode_id) + "';"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('machines', 'R')
    def addExpenseType(self, name, account_id, opposite_account_id, calculate_in_manufacture):
        account_id = account_id if account_id is not None else 'NULL'
        opposite_account_id = opposite_account_id if opposite_account_id is not None else 'NULL'

        query = "INSERT INTO `expenses_types`(`name`, `account_id`, `opposite_account_id`, `calculated_in_manufacture`) VALUES ('{}', {}, {}, '{}')".format(
            name, account_id, opposite_account_id, calculate_in_manufacture)
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('machines', 'R')
    def removeExpenseType(self, expense_type_id):
        query = "DELETE FROM `expenses_types` WHERE `id`='" + str(expense_type_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchExpensesTypes(self):
        query = "SELECT `expenses_types`.*, `a`.`name` as `account_name`, `oa`.`name` as `opposite_account_name` FROM `expenses_types` LEFT JOIN `accounts` as `a` ON `expenses_types`.`account_id`=`a`.`id` LEFT JOIN `accounts` as `oa` ON `expenses_types`.`opposite_account_id`=`oa`.`id`"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchExpenseType(self, expense_type_id=None):
        query = "SELECT * FROM `expenses_types` WHERE `id` = '" + str(expense_type_id) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        return row

    @check_permission('journal_entries', 'R')
    def fetchJournalEntries(self, date_filter='', account='', type_filter='', origin_type='', origin_id=''):
        query = "SELECT DISTINCT `journal_entries`.*, `currencies`.`name` as `currency_name` FROM `journal_entries` JOIN `currencies` ON `journal_entries`.`currency` = `currencies`.`id` LEFT JOIN `journal_entries_items` ON `journal_entries_items`.`journal_entry_id` = `journal_entries`.`id` WHERE `journal_entries`.`entry_date` = COALESCE( NULLIF('" + str(date_filter) + "', ''), `journal_entries`.`entry_date` ) AND IFNULL(`journal_entries`.`origin_type`,0) = IFNULL( NULLIF('" + str(origin_type) + "', ''), IFNULL(`journal_entries`.`origin_type`,0) ) AND IFNULL(`journal_entries`.`origin_id`,'') = IFNULL( NULLIF('" + str(origin_id) + "', ''), IFNULL(`journal_entries`.`origin_id`,'')) AND (( `journal_entries_items`.`account_id` = COALESCE( NULLIF('" + str(account) + "', ''), `journal_entries_items`.`account_id` ) OR `journal_entries_items`.`opposite_account_id` = COALESCE( NULLIF('" + str(account) + "', ''), `journal_entries_items`.`opposite_account_id` ) ) OR `journal_entries_items`.`journal_entry_id` IS NULL) AND (`journal_entries_items`.`type_col` = COALESCE( NULLIF('" + str(type_filter) + "', ''), `journal_entries_items`.`type_col` ) OR `journal_entries_items`.`type_col` IS NULL) AND (('"+str(type_filter)+"' = 'creditor' AND ((`journal_entries_items`.`account_id` = '"+str(account)+"' AND `journal_entries_items`.`type_col` = 'creditor') OR (`journal_entries_items`.`opposite_account_id` = '"+str(account)+"' AND `journal_entries_items`.`type_col` = 'debtor'))) OR '"+str(type_filter)+"' != 'creditor') ORDER BY `journal_entries`.`date_col` desc;"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('journal_entries', 'R')
    def removeJournalEntry(self, journal_entry_id):
        query = "DELETE FROM `journal_entries` WHERE `id`='" + str(journal_entry_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('journal_entries', 'R')
    def fetchJournalEntryItems(self, journal_entry='', from_date='', to_date='', account='', opposite_account='', type='', origin_type='', cost_center_id='', sources=''):

        # Convert the list of sources into a string for SQL query
        sources_str = "','".join(sources)

        query = "SELECT `journal_entries_items`.*, `currencies`.`name` as `currency_name`, `a`.`name` as `account_name`, `oa`.`name` as `opposite_account_name`, `journal_entries`.`entry_date`,  `journal_entries`.`origin_type`, `journal_entries`.`origin_id` FROM `journal_entries_items` JOIN `currencies` ON `journal_entries_items`.`currency`=`currencies`.`id` JOIN `accounts` as `a` ON `a`.`id` = `journal_entries_items`.`account_id` LEFT JOIN `accounts` AS `oa` ON `oa`.`id`=`journal_entries_items`.`opposite_account_id` JOIN `journal_entries` ON `journal_entries`.`id`=`journal_entries_items`.`journal_entry_id` WHERE `journal_entries_items`.`journal_entry_id`=COALESCE(NULLIF('" + str(
            journal_entry) + "',''),`journal_entries_items`.`journal_entry_id`) AND IFNULL(`journal_entries`.`origin_type`,'') = IFNULL(NULLIF('" + str(
            origin_type) + "',''),IFNULL(`journal_entries`.`origin_type`,'')) AND IFNULL(`journal_entries_items`.`cost_center_id`,'') = IFNULL(NULLIF('" + str(
            cost_center_id) + "',''),IFNULL(`journal_entries_items`.`cost_center_id`,'')) AND `journal_entries_items`.`account_id`=COALESCE(NULLIF('" + str(
            account) + "',''),`journal_entries_items`.`account_id`) AND IFNULL(`journal_entries_items`.`opposite_account_id`, '') = IFNULL(NULLIF('" + str(
            opposite_account) + "',''), IFNULL(`journal_entries_items`.`opposite_account_id`,'')) AND `journal_entries_items`.`type_col`=COALESCE(NULLIF('" + str(
            type) + "',''),`journal_entries_items`.`type_col`) AND ((`journal_entries`.`date_col`>=COALESCE(NULLIF('" + str(
            from_date) + "',''),'0001-01-01')) AND (`journal_entries`.`date_col`<=COALESCE(NULLIF('" + str(
            to_date) + "',''),'9999-12-31')))"

        # Add the condition for sources only if it's not empty
        if sources:
            query += " AND `journal_entries`.`origin_type` IN ('" + sources_str + "')"

        query += ";"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('journal_entries', 'R')
    def fetchSelectedJournalEntry(self, entry_id):
        query = "SELECT * FROM `journal_entries` WHERE `id` = '" + str(entry_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        return rows
    
    @check_permission('journal_entries', 'R')
    def fetchInvoiceJournalEntry(self, invoice_id):
        query = "SELECT * FROM `journal_entries` WHERE `origin_id` = '" + str(invoice_id) + "'"
        print(query)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
        except Exception as e:
            rows = None
        return rows
    
    @check_permission('journal_entries', 'R')
    def updateJournalEntry(self, entry_id, entry_date='', currency='', commit=True):
        query = "UPDATE `journal_entries` SET `currency`=COALESCE(NULLIF('" + str(currency) + "',''), `currency`), `entry_date`=COALESCE(NULLIF('" + str(
            entry_date) + "',''), `entry_date`) WHERE `id`='" + str(entry_id) + "';"
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()


    @check_permission('journal_entries', 'R')
    def deleteJournalEntry(self, entry_id='', origin_id=''):
        query = "DELETE FROM `journal_entries` WHERE `id` = COALESCE(NULLIF('" + str(entry_id) + "', ''), `id`) AND `origin_id` = COALESCE(NULLIF('" + str(origin_id) + "', ''), `origin_id`)"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('journal_entries', 'R')
    def addJournalEntry(self, entry_date, currency, origin_type='', origin_id='', commit=True) -> int:
        current_date = date.today().isoformat()
        query = "INSERT INTO `journal_entries`(`currency`, `date_col`, `entry_date`, `origin_type`, `origin_id`) VALUES ('" + str(
            currency) + "', '" + str(current_date) + "', '" + str(entry_date) + "', NULLIF('" + str(
            origin_type) + "',''), NULLIF('" + str(origin_id) + "',''));"
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()
        return self.cursor.lastrowid

    @check_permission('journal_entries', 'R')
    def fetchSelectedJournalEntryItem(self, entry_item_id):
        query = "SELECT `journal_entries_items`.*, `currencies`.`name` AS `currency_name`, `a`.`name` AS `account_name`, `oa`.`name` AS `opposite_account_name` FROM `journal_entries_items` JOIN `currencies` ON `journal_entries_items`.`currency`=`currencies`.`id` JOIN `accounts` AS `a` ON `journal_entries_items`.`account_id`=`a`.`id` LEFT JOIN `accounts` as `oa` ON `oa`.`id`=`journal_entries_items`.`opposite_account_id` WHERE `journal_entries_items`.`id` = '" + str(entry_item_id) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchone()
        return rows

    @check_permission('journal_entries', 'R')
    def fetchJournalEntryItem(self, journal_entry_id='', statement='', type=''):
        query = "SELECT * FROM `journal_entries_items` WHERE `journal_entry_id`=COALESCE(NULLIF('" + str(journal_entry_id) + "', ''), `journal_entry_id`) AND `statement_col`=COALESCE(NULLIF('" + str(statement) + "', ''), `statement_col`) AND `type_col`=COALESCE(NULLIF('" + str(type) + "', ''), `type_col`)"
        print(query)
        try:
            self.cursor.execute(query)
            rows = self.cursor.fetchall()
            if rows:
                rows = rows[-1] # Fetch last journal entry item for the statement
        except Exception as e:
            rows = None
        return rows

    @check_permission('journal_entries', 'R')
    def updateJournalEntryItem(self, journal_entry_item_id, currency, type, statement, account, opposite_account, value,
                               cost_center_id, distributive_cost_center_distributed_values, commit=True):
        if cost_center_id is None:
            cost_center_id = ''

        # Fetch the entry currency if the provided currency is None
        if currency is None:
            entry_query = "SELECT `currency` FROM `journal_entries` WHERE `id` = (SELECT `journal_entry_id` FROM `journal_entries_items` WHERE `id` = %s)"
            self.cursor.execute(entry_query, (journal_entry_item_id,))
            entry_currency_row = self.cursor.fetchone()
            currency = entry_currency_row['currency'] if entry_currency_row else None


        query = "UPDATE `journal_entries_items` SET `account_id`='" + str(account) + "', `statement_col`='" + str(
            statement) + "', `currency`='" + str(currency) + "', `opposite_account_id`='" + str(
            opposite_account) + "', `type_col`='" + str(type) + "', `value_col`='" + str(
            value) + "', `cost_center_id` = NULLIF('" + str(cost_center_id) + "','') WHERE `id`='" + str(
            journal_entry_item_id) + "'"

        print(query)
        self.cursor.execute(query)

        if distributive_cost_center_distributed_values:
            for distributed_value in distributive_cost_center_distributed_values:
                query = """
                   INSERT INTO journal_entries_items_distributive_cost_center_values (cost_centers_aggregations_distributives_id, journal_entry_item_id, percentage) VALUES (%s, %s, %s) ON DUPLICATE KEY UPDATE percentage = %s;
                   """
                values = (distributed_value[0], journal_entry_item_id, distributed_value[1], distributed_value[1])

                # Print the formatted query for viewing
                formatted_query = f"""
                {query}
                Parameters: {values}
                """
                print(formatted_query)

                self.cursor.execute(query, values)

        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('journal_entries', 'R')
    def addJournalEntryItem(self, journal_entry_id, currency, type_col, statement, account, opposite_account, value,cost_center_id=None, distributive_cost_center_distributed_values=None, commit=True):
        # Get saved_journal_entries setting
        saved_journal_entries = self.fetchSetting('saved_journal_entries')

        if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
            if saved_journal_entries == 'double':
                # Save as single double-entry item
                query = """
                INSERT INTO `journal_entries_items` (`journal_entry_id`, `account_id`, `statement_col`, `currency`, `opposite_account_id`, `type_col`, `value_col`, `cost_center_id`)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                values = (journal_entry_id, account, statement, currency, opposite_account, type_col, value, cost_center_id)
                print(query)
                self.cursor.execute(query, values)

            else:
                # Save as two individual items
                query = """
                INSERT INTO `journal_entries_items` (`journal_entry_id`, `account_id`, `statement_col`, `currency`, `type_col`, `value_col`, `cost_center_id`)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # First item with provided type
                values1 = (journal_entry_id, account, statement, currency, type_col, value, cost_center_id)
                print(query)
                self.cursor.execute(query, values1)

                # Check if opposite account is provided
                if opposite_account:
                    # Second item with opposite type
                    opposite_type = 'debtor' if type_col == 'creditor' else 'creditor'
                    values2 = (journal_entry_id, opposite_account, statement, currency, opposite_type, value, cost_center_id)
                    print(query)
                    self.cursor.execute(query, values2)

        else:

            if saved_journal_entries == 'double':
                # Save as single double-entry item
                query = """
                INSERT INTO `journal_entries_items` (`journal_entry_id`, `account_id`, `statement_col`, `currency`, `opposite_account_id`, `type_col`, `value_col`, `cost_center_id`)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """
                values = (journal_entry_id, account, statement, currency, opposite_account, type_col, value, cost_center_id)
                print(query)
                self.cursor.execute(query, values)

            else:
                # Save as two individual items
                query = """
                INSERT INTO `journal_entries_items` (`journal_entry_id`, `account_id`, `statement_col`, `currency`, `type_col`, `value_col`, `cost_center_id`)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                # First item with provided type
                values1 = (journal_entry_id, account, statement, currency, type_col, value, cost_center_id)
                print(query)
                self.cursor.execute(query, values1)

                # Check if opposite account is provided
                if opposite_account:
                    # Second item with opposite type
                    opposite_type = 'debtor' if type_col == 'creditor' else 'creditor'
                    values2 = (journal_entry_id, opposite_account, statement, currency, opposite_type, value, cost_center_id)
                    print(query)
                    self.cursor.execute(query, values2)


        journal_entry_item_id = self.cursor.lastrowid  # Get the ID of the newly inserted item

        if distributive_cost_center_distributed_values:
            for distributed_value in distributive_cost_center_distributed_values:
                print(distributed_value)
                query = """
                   INSERT INTO `journal_entries_items_distributive_cost_center_values` (`journal_entry_item_id`, `cost_centers_aggregations_distributives_id`, `percentage`)
                   VALUES (%s, %s, %s)
                   """
                values = (str(journal_entry_item_id), str(distributed_value[0]), str(distributed_value[1]))
                self.cursor.execute(query, values)

        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('journal_entries', 'R')
    def deleteJournalEntryItem(self, item_id):
        query = "DELETE FROM `journal_entries_items` WHERE `id`='" + str(item_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('journal_entries', 'R')
    def removeJournalEntriesItems(self, journal_entry_id, commit=True):
        query = "DELETE FROM `journal_entries_items` WHERE `journal_entry_id`='" + str(journal_entry_id) + "'"
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('manufacture', 'R')
    def addManufactureHall(self, warehouse_id):
        query = "INSERT INTO `manufacture_halls` (`warehouse_id`) VALUES ('" + str(warehouse_id) + "')"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('manufacture', 'R')
    def removeManufactureHall(self, hall_id):
        query = "DELETE FROM `manufacture_halls` WHERE `id`='" + str(hall_id) + "'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('manufacture', 'R')
    def fetchManufactureHalls(self):
        query = "SELECT `manufacture_halls`.*, `warehouseslist`.`name`,  `warehouseslist`.`id` as `account_id`, `accounts`.`name` as `account_name` FROM `manufacture_halls` JOIN `warehouseslist` ON `manufacture_halls`.`warehouse_id`=`warehouseslist`.`id` JOIN `accounts` ON `accounts`.`id`=`warehouseslist`.`account`;"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('materials', 'R')
    def addPeriodStartMaterial(self, material_id, quantity_1, unit_id_1, quantity_2, unit_id_2, quantity_3, unit_id_3,
                               material_unit_price, material_currency_id,
                               material_warehouse_id, material_notes, date, commit=False):

        query = "INSERT INTO `period_start_materials`(`material_id`, `quantity1`, `unit1_id`, `quantity2`, `unit2_id`, `quantity3`, `unit3_id`, `unit_price`, `currency`, `warehouse_id`, `notes`, `date_col`) VALUES ('" + str(
            material_id) + "','" + str(quantity_1) + "','" + str(unit_id_1) + "',NULLIF('" + str(quantity_2) + "',''), NULLIF('" + str(
            unit_id_2) + "',''),NULLIF('" + str(quantity_3) + "',''),NULLIF('" + str(unit_id_3) + "',''),'" + str(
            material_unit_price) + "','" + str(
            material_currency_id) + "','" + str(material_warehouse_id) + "',NULLIF('" + str(
            material_notes) + "',''),'" + str(
            date) + "')"

        print(query)
        # Execute the query using the values from the parameters
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

        return self.cursor.lastrowid

    @check_permission('materials', 'R')
    def removePeriodStartMaterial(self, id):
        # remove period start material
        query = "DELETE FROM `period_start_materials` WHERE `id`= '" + str(id) + "'"
        print(query)
        self.cursor.execute(query)

        # remove related journal entries
        query = "DELETE FROM `journal_entries` WHERE `origin_id`='" + str(id) + "' AND `origin_type`='period_start'"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('materials', 'R')
    def fetchPeriodStartMaterials(self):
        query = "SELECT `period_start_materials`.*, `materials`.`name`, `u1`.`name` as `unit1_name`, `u2`.`name` as `unit2_name`, `u3`.`name` as `unit3_name`, `currencies`.`name` AS `currency_name`, `warehouseslist`.`name` AS `warehouse_name`, `warehouseslist`.`account` AS `warehouse_account` FROM `period_start_materials` JOIN `materials` ON `period_start_materials`.`material_id`=`materials`.`id` JOIN `units` AS `u1` ON `u1`.`id`=`period_start_materials`.`unit1_id` LEFT JOIN `units` AS `u2` ON `u2`.`id`=`period_start_materials`.`unit2_id` LEFT JOIN `units` AS `u3` ON `u3`.`id`=`period_start_materials`.`unit3_id` JOIN `currencies`ON `currencies`.`id`=`period_start_materials`.`currency` JOIN `warehouseslist` ON `warehouseslist`.`id`=`period_start_materials`.`warehouse_id`;"

        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    ################ Financial Statements Operations ################

    @check_permission('financial_statements', 'R')
    def fetchFinancialStatements(self, final_financial_statement=''):
        print("DATABASE> Fetch all Financial Statements")
        query = "SELECT * FROM `financial_statement` WHERE IFNULL(`final_financial_statement`,'0') = IFNULL(NULLIF('" + str(
            final_financial_statement) + "',''), IFNULL(`final_financial_statement`, '0'));"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('financial_statements', 'R')
    def fetchFinancialStatement(self, financial_statement_id):
        print("DATABASE> Fetch Financial Statement")
        query = f"SELECT * FROM `financial_statement` WHERE `id` = {financial_statement_id};"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('financial_statements', 'R')
    def fetchFinancialStatementBlocks(self, financial_statement_id):
        print("DATABASE> Fetch Financial Statement Blocks")
        query = f"SELECT * FROM `financial_statement_block` WHERE `financial_statement_id` = {financial_statement_id};"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('financial_statements', 'R')
    def addFinancialStatement(self, financial_statement_name, final_financial_statement_id=''):
        print("DATABASE> Adding Financial Statement")
        query = "INSERT INTO `financial_statement` (`name`, `final_financial_statement`) VALUES ('" + str(financial_statement_name) + "', NULLIF('" + str(final_financial_statement_id) + "',''));"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('financial_statements', 'R')
    def addFinancialStatementBlock(self, financial_statement_id, financial_statement_block_name):
        print("DATABASE> Adding Financial Statement Block")
        query = f"INSERT INTO `financial_statement_block` (`name`, `financial_statement_id`) VALUES ('{financial_statement_block_name}', {financial_statement_id});"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('financial_statements', 'R')
    def updateFinancialStatement(self, financial_statement_id, financial_statement_name, final_financial_statement_id):
        print("DATABASE> Updating Financial Statement")
        query = "UPDATE `financial_statement` SET `name` = '" + str(financial_statement_name) + "', `final_financial_statement` = NULLIF('" + str(final_financial_statement_id) + "','') WHERE `id` = '" + str(financial_statement_id) + "';"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('financial_statements', 'R')
    def updateFinancialStatementBlock(self, financial_statement_block_id, financial_statement_block_name):
        print("DATABASE> Updating Financial Statement Block")
        query = f"UPDATE `financial_statement_block` SET `name` = '{financial_statement_block_name}'  WHERE `id` = {financial_statement_block_id};"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('financial_statements', 'R')
    def removeFinancialStatement(self, financial_statement_id):
        print("DATABASE> Deleting Financial Statement")
        query = f"DELETE FROM `financial_statement` WHERE `id` = {financial_statement_id};"
        print(query)
        deleted = False
        try:
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()
            deleted = True
        except Exception as e:
            print('Error Deleting Financial Statement!, ', e)
        return deleted

    @check_permission('financial_statements', 'R')
    def removeFinancialStatementBlock(self, financial_statement_block_id):
        print("DATABASE> Deleting Financial Statement Block")
        query = f"DELETE FROM `financial_statement_block` WHERE `id` = {financial_statement_block_id};"
        print(query)
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('financial_statements', 'R')
    def filterFinancialStatements(self, financial_statement_name):
        print("DATABASE> Filtering Financial Statements")
        query = f"SELECT * FROM `financial_statement` WHERE `name` LIKE '%{financial_statement_name}%';"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows


    ############## Receipt Docs Operations #########################
    @check_permission('receipt_docs', 'R')
    def fetchReceiptDocs(self):
        print("DATABASE> Fetch all receipt documents")
        query = "SELECT receipt_docs.*, units.name as unit_name, materials.name as material_name, target_warehouse.name as target_warehouse_name, rejection_warehouse.name as rejection_warehouse_name FROM receipt_docs JOIN units ON receipt_docs.unit_id = units.id JOIN materials ON receipt_docs.material_id = materials.id JOIN warehouseslist AS target_warehouse ON receipt_docs.target_warehouse_id = target_warehouse.id JOIN warehouseslist AS rejection_warehouse ON receipt_docs.rejection_warehouse_id = rejection_warehouse.id"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    @check_permission('receipt_docs', 'R')
    def fetchReceiptDoc(self, id):
        print("DATABASE> Fetch receipt document with id: " + str(id))
        query = ("SELECT receipt_docs.*, units.name as unit_name, materials.name as material_name, target_warehouse.name as target_warehouse_name, rejection_warehouse.name as rejection_warehouse_name, invoices.id as invoice_id, invoices.number as invoice_number FROM receipt_docs JOIN units ON receipt_docs.unit_id = units.id JOIN materials ON receipt_docs.material_id = materials.id JOIN warehouseslist AS target_warehouse ON receipt_docs.target_warehouse_id = target_warehouse.id JOIN warehouseslist AS rejection_warehouse ON receipt_docs.rejection_warehouse_id = rejection_warehouse.id LEFT JOIN invoice_items ON receipt_docs.invoice_item_id = invoice_items.id LEFT JOIN invoices ON invoice_items.invoice_id = invoices.id WHERE receipt_docs.id = " + str(id))
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('receipt_docs', 'R')
    def addReceiptDoc(self, material_id, target_warehouse_id, rejection_warehouse_id, unit_id, quantity, invoice_number, date):
        print("DATABASE> Add new receipt document.")
        query = ("INSERT INTO `receipt_docs` "
                 "(`material_id`, `target_warehouse_id`, `rejection_warehouse_id`, `unit_id`, `quantity`, `invoice_item_id`, `date`) "
                 "VALUES (" + str(material_id) + ", " + str(target_warehouse_id) + ", " + str(rejection_warehouse_id) + ", " + str(unit_id) + ", " + str(quantity) + ", '" + str(invoice_number) + "', '" + str(date) + "')")
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('receipt_docs', 'R')
    def removeReceiptDoc(self, receipt_doc_id):
        print("DATABASE> Deleting receipt document with id: " + str(receipt_doc_id))
        query = f"DELETE FROM `receipt_docs` WHERE `id` = {receipt_doc_id};"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    @check_permission('receipt_docs', 'R')
    def updateReceiptDoc(self, receipt_doc_id, material_id, target_warehouse_id, rejection_warehouse_id, unit_id, quantity, invoice_number, date):
        print("DATABASE> Updating receipt document with id: " + str(receipt_doc_id))
        query = f"UPDATE `receipt_docs` SET `material_id` = {material_id}, `target_warehouse_id` = {target_warehouse_id}, `rejection_warehouse_id` = {rejection_warehouse_id}, `unit_id` = {unit_id}, `quantity` = {quantity}, `invoice_item_id` = NULLIF('{invoice_number}',''), `date` = '{date}' WHERE `id` = {receipt_doc_id};"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()


    #################### Material Moves #############################

    @check_permission('material_moves', 'W')
    def moveMaterial(self, quantity, move_unit, material_id='',
                    from_warehouse='', to_warehouse='', material_name='', from_warehouse_entry_id='', to_warehouse_entry_id='',
                    quantity_using_source_warehouse_unit='', source_production_batch_id='', source_invoice_item_id='',
                    source_warehouse_unit='', cost='', currency='', origin_type='', origin_id='',
                    to_account_warehouse='', from_account_warehouse='', to_account_name_warehouse='',
                    batch_number='', batch_mfg='', batch_exp='', production_date='', expire_date='',
                    from_account_name_warehouse='', record_move=True, record_journal_entry=True, record_only=False,
                    commit=True):
        # The 'record_only' parameter, when set to True, ensures that the material move is only recorded in the database `material_moves`` table
        # without actually moving the material between warehouses. This is useful when movement between warehouses was done by some other logic
        # and we just want to record that movement.
        from_warehouse_name = ''
        to_warehouse_name = ''
        material_move_id = None

        if record_move or record_only:
            try:
                date = datetime.date.today().isoformat()

                source_warehouse = str(from_warehouse) if from_warehouse else ''
                destination_warehouse = str(to_warehouse) if to_warehouse else ''
                quantity_str = str(quantity)
                unit_str = str(move_unit)
                date_str = str(date)

                query = "INSERT INTO `material_moves` (`source_warehouse_entry_id`, `destination_warehouse_entry_id`, `source_warehouse`, `destination_warehouse`, `quantity`, `unit`, `date_col`, `origin`, `origin_id`) VALUES (NULLIF('" + str(from_warehouse_entry_id) + "', ''), NULLIF('" + str(to_warehouse_entry_id) + "', ''), NULLIF('" + str(source_warehouse) + "', ''), NULLIF('" + str(destination_warehouse) + "', ''), '" + str(quantity_str) + "', '" + str(unit_str) + "', '" + str(date_str) + "', NULLIF('" + str(origin_type) + "', ''), NULLIF('" + str(origin_id) + "', ''))"
                print(query)
                self.cursor.execute(query)
                material_move_id = self.cursor.lastrowid
            except Exception as e:
                print("An error occured:", str(e))

        if not record_only:
            if not material_id:
                print ("Material ID is mandatory when record_only is False")
                return
            try:
                from_warehouse_codename = None
                from_warehouse_name= None
                to_warehouse_codename = None
                to_warehouse_name = None
                from_warehouse_data = self.fetchWarehouse(from_warehouse) if from_warehouse else {}
                to_warehouse_data = self.fetchWarehouse(to_warehouse) if to_warehouse else {}

                if len(from_warehouse_data) > 0:
                    from_warehouse_name = from_warehouse_data['name']
                    from_warehouse_codename = from_warehouse_data['codename']

                if len(to_warehouse_data) > 0:
                    to_warehouse_name = to_warehouse_data['name']
                    to_warehouse_codename = to_warehouse_data['codename']

                source_warehouse_entry_id = None
                destination_warehouse_entry_id = None

                if from_warehouse_codename and quantity_using_source_warehouse_unit and from_warehouse_entry_id:
                    query = "UPDATE `" + from_warehouse_codename + "` SET `quantity`=`quantity`-" + str(quantity_using_source_warehouse_unit) + " WHERE `" + from_warehouse_codename + "`.`id`='" + str(from_warehouse_entry_id) + "'"
                    print(query)
                    self.cursor.execute(query)
                    source_warehouse_entry_id = from_warehouse_entry_id

                if to_warehouse_codename and quantity and move_unit:
                    query = "INSERT INTO `" + to_warehouse_codename + "` (material_id, quantity, unit, production_batch_id, receipt_doc_id, batch_number, batch_mfg, batch_exp, material_move_id, production_date, expire_date) VALUES ('" + str(material_id) + "', '" + str(quantity) + "', '" + str(move_unit) + "', NULLIF('" + str(source_production_batch_id) + "', ''), NULLIF('" + str(source_invoice_item_id) + "', ''), NULLIF('" + str(batch_number) + "', ''), NULLIF('" + str(batch_mfg) + "', ''), NULLIF('" + str(batch_exp) + "', ''), NULLIF('" + str(material_move_id) + "', ''), NULLIF('" + str(production_date) + "', ''), NULLIF('" + str(expire_date) + "', ''))"
                    print(query)
                    self.cursor.execute(query)
                    destination_warehouse_entry_id = self.cursor.lastrowid

            except Exception as e:
                print("An error occurred:", str(e))
                print("The material was not moved.")

        if record_journal_entry:
            date = datetime.date.today().isoformat()
            journal_entry_id = self.addJournalEntry(date, currency, origin_type=origin_type, origin_id=origin_id, commit=False)

            statement = "Move material " + str(material_name) + " from " + str(from_warehouse_name) + " to " + str(
                to_warehouse_name)

            self.addJournalEntryItem(journal_entry_id, currency, 'creditor', statement, to_account_warehouse,from_account_warehouse, cost, commit=True)
        if commit:
            self.sqlconnector.conn.commit()
        return material_move_id

    @check_permission('material_moves', 'W')
    def updateMaterialMove(self, material_move_id, to_warehouse_entry_id, commit=True):
        query = "UPDATE `material_moves` SET `destination_warehouse_entry_id` = '" + str(to_warehouse_entry_id) + "' WHERE `id` = '" + str(material_move_id) + "'"
        print(query)
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    @check_permission('material_moves', 'W')
    def fetchMaterialMove(self, material_move_id='', origin_type='', origin_id=''):
        if material_move_id:
            query = "SELECT * FROM `material_moves` WHERE `id`='" + str(material_move_id) + "'"
        elif origin_type and origin_id:
            query = "SELECT * FROM `material_moves` WHERE `origin`='" + str(origin_type) + "' AND `origin_id`='" + str(origin_id) + "'"
        else:
            return None

        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('material_moves', 'W')
    def fetchSingleMaterialMove(self, move_id):
        query = "SELECT * FROM `material_moves` WHERE `id`='" + str(move_id) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    @check_permission('material_moves', 'W')
    def fetchMaterialMoves(self, material_id='', from_date='', to_date='', from_warehouse='', to_warehouse='', ordered=False):
        print("DATABASE> Fetch material moves for material id: " + str(material_id))
        query = "SELECT * FROM `warehouseslist`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        moves_list = []
        for row in rows:
            id = row['id']
            name = row['name']
            codename = row['codename']

            table_name = codename
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                check_query = "SHOW TABLES LIKE '" + table_name + "'"
                self.cursor.execute(check_query)
            else:
                check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
                self.cursor.execute(check_query, (table_name,))
            table_exists = self.cursor.fetchone()

            if table_exists:
                query = "SELECT * FROM `" + table_name + "` WHERE `material_id` = COALESCE(NULLIF('" + str(material_id) + "', ''), `material_id`)"
                self.cursor.execute(query)
                materials = self.cursor.fetchall()
                if materials:
                    for material in materials:
                        warehouse_entry_id = material['id']
                        warehouse_material_id = material['material_id']
                        # quantity = material['quantity']
                        # unit = material['unit']
                        # production_batch_id = material['production_batch_id']
                        # receipt_doc_id = material['receipt_doc_id']
                        # batch_number = material['batch_number']
                        # batch_mfg = material['batch_mfg']
                        # batch_exp = material['batch_exp']

                        # Check for moves related to this warehouse entry
                        moves = "SELECT * FROM material_moves WHERE ((source_warehouse_entry_id = " + str(warehouse_entry_id) + " AND source_warehouse = " + str(id) + ") OR (destination_warehouse_entry_id = " + str(warehouse_entry_id) + " AND destination_warehouse = " + str(id) + ")) AND date_col BETWEEN COALESCE(NULLIF('" + str(from_date) + "',''),'1000-01-01') AND COALESCE(NULLIF('" + str(to_date) + "',''),'9999-12-31')" + ((" AND source_warehouse = " + str(from_warehouse)) if from_warehouse else "") + ((" AND destination_warehouse = " + str(to_warehouse)) if to_warehouse else "")
                        if ordered:
                            moves + "ORDER BY `date_col` DESC LIMIT 1"
                        print(moves)
                        self.cursor.execute(moves)
                        moves = self.cursor.fetchall()

                        if moves:
                            for move in moves:
                                move_id = move['id']
                                move_quantity = move['quantity']
                                move_unit = move['unit']
                                move_origin = move['origin']
                                move_origin_id = move['origin_id']
                                move_date = move['date_col']
                                if (move['source_warehouse_entry_id'] == warehouse_entry_id and move['source_warehouse'] == id) and not move['destination_warehouse_entry_id'] and not move['destination_warehouse']:
                                    move_type = 'reduce'
                                    from_warehouse_name = name
                                    to_warehouse_name = None
                                elif (move['destination_warehouse_entry_id'] == warehouse_entry_id and move['destination_warehouse']) and not move['source_warehouse_entry_id'] and not move['source_warehouse'] == id:
                                    move_type = 'add'
                                    from_warehouse_name = None
                                    to_warehouse_name = name
                                else:
                                    move_type = 'transfer'
                                    from_warehouse_name = self.fetchWarehouse(move['source_warehouse'])['name']
                                    to_warehouse_name = self.fetchWarehouse(move['destination_warehouse'])['name']

                                material = self.fetchMaterial(warehouse_material_id)
                                material_name = material['name'] if material else None
                                material_code = material['code'] if material else None
                                unit_name = self.fetchUnit(move_unit)
                                unit_name = unit_name['name'] if unit_name else None

                                invoice_item = self.fetchInvoiceItem(move_origin_id)
                                if invoice_item:
                                    item_currency = invoice_item['currency_id']
                                    item_currency_name = invoice_item['currency_name']
                                    item_unit_price = invoice_item['unit_price']
                                else:
                                    item_currency = None
                                    item_currency_name = None
                                    item_unit_price = None

                                moves_list.append({
                                    'move_id': move_id,
                                    'warehouse_id': id,
                                    'move_type': move_type,
                                    'move_origin': move_origin,
                                    'move_origin_id': move_origin_id,
                                    'move_date': move_date,
                                    'move_quantity': move_quantity,
                                    'move_unit': move_unit,
                                    'material_id': warehouse_material_id,
                                    'from_warehouse_name': from_warehouse_name,
                                    'material_name': material_name,
                                    'material_code': material_code,
                                    'unit_name': unit_name,
                                    'to_warehouse_name': to_warehouse_name,
                                    'item_currency': item_currency,
                                    'item_currency_name': item_currency_name,
                                    'item_unit_price': item_unit_price
                                })
        return moves_list

    @check_permission('material_moves', 'W')
    def fetchLastMaterialMovement(self):
        query = "SELECT * FROM `warehouseslist`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        moves_list = []
        for row in rows:
            id = row['id']
            name = row['name']
            codename = row['codename']

            table_name = codename
            if str(type(self.sqlconnector)) == "<class 'MysqlConnector.MysqlConnector'>":
                check_query = "SHOW TABLES LIKE '" + table_name + "'"
                self.cursor.execute(check_query)
            else:
                check_query = "SELECT name FROM sqlite_master WHERE type='table' AND name=?"
                self.cursor.execute(check_query, (table_name,))
            table_exists = self.cursor.fetchone()

            if table_exists:
                query = "SELECT * FROM `" + table_name + "` WHERE `material_id` = COALESCE(NULLIF('" + str(material_id) + "', ''), `material_id`)"
                self.cursor.execute(query)
                materials = self.cursor.fetchall()
                if materials:
                    for material in materials:
                        warehouse_entry_id = material['id']
                        warehouse_material_id = material['material_id']
                        # quantity = material['quantity']
                        # unit = material['unit']
                        # production_batch_id = material['production_batch_id']
                        # receipt_doc_id = material['receipt_doc_id']
                        # batch_number = material['batch_number']
                        # batch_mfg = material['batch_mfg']
                        # batch_exp = material['batch_exp']

                        # Check for moves related to this warehouse entry
                        moves = "SELECT * FROM material_moves WHERE ((source_warehouse_entry_id = " + str(warehouse_entry_id) + " AND source_warehouse = " + str(id) + ") OR (destination_warehouse_entry_id = " + str(warehouse_entry_id) + " AND destination_warehouse = " + str(id) + ")) AND date_col BETWEEN COALESCE(NULLIF('" + str(from_date) + "',''),'1000-01-01') AND COALESCE(NULLIF('" + str(to_date) + "',''),'9999-12-31')" + ((" AND source_warehouse = " + str(from_warehouse)) if from_warehouse else "") + ((" AND destination_warehouse = " + str(to_warehouse)) if to_warehouse else "")
                        if ordered:
                            moves + "ORDER BY `date_col` DESC LIMIT 1"
                        print(moves)
                        self.cursor.execute(moves)
                        moves = self.cursor.fetchall()

                        if moves:
                            for move in moves:
                                move_id = move['id']
                                move_quantity = move['quantity']
                                move_unit = move['unit']
                                move_origin = move['origin']
                                move_origin_id = move['origin_id']
                                move_date = move['date_col']
                                if (move['source_warehouse_entry_id'] == warehouse_entry_id and move['source_warehouse'] == id) and not move['destination_warehouse_entry_id'] and not move['destination_warehouse']:
                                    move_type = 'reduce'
                                    from_warehouse_name = name
                                    to_warehouse_name = None
                                elif (move['destination_warehouse_entry_id'] == warehouse_entry_id and move['destination_warehouse']) and not move['source_warehouse_entry_id'] and not move['source_warehouse'] == id:
                                    move_type = 'add'
                                    from_warehouse_name = None
                                    to_warehouse_name = name
                                else:
                                    move_type = 'transfer'
                                    from_warehouse_name = self.fetchWarehouse(move['source_warehouse'])['name']
                                    to_warehouse_name = self.fetchWarehouse(move['destination_warehouse'])['name']

                                material = self.fetchMaterial(warehouse_material_id)
                                material_name = material['name'] if material else None
                                material_code = material['code'] if material else None
                                unit_name = self.fetchUnit(move_unit)
                                unit_name = unit_name['name'] if unit_name else None

                                invoice_item = self.fetchInvoiceItem(move_origin_id)
                                if invoice_item:
                                    item_currency = invoice_item['currency_id']
                                    item_currency_name = invoice_item['currency_name']
                                    item_unit_price = invoice_item['unit_price']
                                else:
                                    item_currency = None
                                    item_currency_name = None
                                    item_unit_price = None

                                moves_list.append({
                                    'move_id': move_id,
                                    'warehouse_id': id,
                                    'move_type': move_type,
                                    'move_origin': move_origin,
                                    'move_origin_id': move_origin_id,
                                    'move_date': move_date,
                                    'move_quantity': move_quantity,
                                    'move_unit': move_unit,
                                    'material_id': warehouse_material_id,
                                    'from_warehouse_name': from_warehouse_name,
                                    'material_name': material_name,
                                    'material_code': material_code,
                                    'unit_name': unit_name,
                                    'to_warehouse_name': to_warehouse_name,
                                    'item_currency': item_currency,
                                    'item_currency_name': item_currency_name,
                                    'item_unit_price': item_unit_price
                                })
        return moves_list


    @check_permission('material_moves', 'W')
    def removeMaterialMove(self, move_id='', origin='', origin_id='', commit=True):
        query = "DELETE FROM `material_moves` WHERE `id`=COALESCE(NULLIF('" + str(move_id) + "', ''), `id`) AND `origin`=COALESCE(NULLIF('" + str(origin) + "', ''), `origin`) AND `origin_id`=COALESCE(NULLIF('" + str(origin_id) + "', ''), `origin_id`)"
        self.cursor.execute(query)
        if commit:
            self.sqlconnector.conn.commit()

    def correctMaterialMovesQuantity(self, origin, origin_id):
        print("DATABASE> Correct material moves quantity for origin:", origin, "origin_id:", origin_id)

        # Get the material move related to the origin and origin_id
        query = """
            SELECT mm.*, i.type_col as invoice_type, mm.source_warehouse_entry_id, mm.destination_warehouse_entry_id,
                   mm.quantity, mm.unit
            FROM material_moves mm
            LEFT JOIN invoice_items ii ON mm.origin_id = ii.id
            LEFT JOIN invoices i ON ii.invoice_id = i.id
            WHERE mm.origin = %s AND mm.origin_id = %s
        """
        self.cursor.execute(query, (origin, origin_id))
        move = self.cursor.fetchone()

        if move:
            try:
                invoice_type = self.fetchInvoiceType(move['invoice_type'])
                invoice_type_category = invoice_type['type_col']
                if invoice_type_category == 'input':
                    # For input invoices, reduce the quantity from warehouse entry
                    self.updateWarehouseEntryQuantity(move['destination_warehouse'], move['destination_warehouse_entry_id'], move['quantity'], updating_type='reduce')

                elif invoice_type_category == 'output':
                    # For output invoices, add the quantity back to warehouse entry
                    self.updateWarehouseEntryQuantity(move['source_warehouse'], move['source_warehouse_entry_id'], move['quantity'], updating_type='add')

                self.sqlconnector.conn.commit()

            except Exception as e:
                print("Error correcting material moves quantity:", str(e))
                self.sqlconnector.conn.rollback()

    @check_permission('material_moves', 'W')
    def fetchWarehouseMoves(self, warehouse_id, to_date):
        warehouse_code = self.fetchWarehouseCodename(warehouse_id)
        if warehouse_code is None:
            return []

        query = "SELECT `material_moves`.*, `material_moves`.quantity as move_quantity, COALESCE(`source_warehouse`.material_id, `destination_warehouse`.material_id) as material_id, COALESCE(`source_warehouse`.quantity, `destination_warehouse`.quantity) as quantity, COALESCE(`source_warehouse`.unit, `destination_warehouse`.unit) as unit, `materials`.`name` AS `material_name`, `units`.`name` AS `unit_name` FROM `material_moves` LEFT JOIN `" + str(warehouse_code) + "` AS `source_warehouse` ON `material_moves`.`source_warehouse_entry_id` = `source_warehouse`.`id` LEFT JOIN `" + str(warehouse_code) + "` AS `destination_warehouse` ON `material_moves`.`destination_warehouse_entry_id` = `destination_warehouse`.`id` LEFT JOIN `materials` ON COALESCE(`source_warehouse`.material_id, `destination_warehouse`.material_id) = `materials`.`id` LEFT JOIN `units` ON COALESCE(`source_warehouse`.unit, `destination_warehouse`.unit) = `units`.`id` WHERE (`material_moves`.`source_warehouse` = '" + str(warehouse_id) + "' OR `material_moves`.`destination_warehouse` = '" + str(warehouse_id) + "') AND `material_moves`.`date_col` <= '" + str(to_date) + "'"
        print(query)
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    ########################## Users ##########################
    def fetchUsers(self):
        query = "SELECT * FROM users"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchUser(self, id):
        query = "SELECT * FROM `users` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    def fetchUserByUsername(self, username):
        query = "SELECT * FROM `users` WHERE `username`='" + str(username) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    def ResetUserPassword(self, id, password):
        # Encrypt the password
        key = base64.urlsafe_b64encode(self.key.encode('utf-8'))
        cipher = Fernet(key)
        encrypted_password = cipher.encrypt(password.encode()).decode()
        query = "UPDATE `users` SET `password`='" + str(encrypted_password) + "' WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def addUser(self, username, password=None):
        # Encrypt the password using the existing key
        key = base64.urlsafe_b64encode(self.key.encode('utf-8'))
        cipher = Fernet(key)  # Use the key initialized in __init__
        encrypted_password = cipher.encrypt(password.encode()).decode()
        query = "INSERT INTO `users` (`username`, `password`) VALUES ('" + str(username) + "', '" + str(encrypted_password) + "')"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def removeUser(self, id):
        query = "DELETE FROM `users` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchUserPermissions(self, user_id):
        rows = []
        query = "SELECT permissions.*, criteria.name as criteria , criteria.key_name as criteria_key, users.username FROM permissions LEFT JOIN criteria ON permissions.criteria_id = criteria.id LEFT JOIN users ON permissions.user_id = users.id WHERE permissions.user_id = '" + str(user_id) + "'"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchUserPermission(self, user_id, criteria, type_col):
        query = "SELECT * FROM permissions JOIN criteria ON permissions.criteria_id = criteria.id WHERE permissions.user_id = '" + str(user_id) + "' AND criteria.name = '" + str(criteria) + "' AND permissions.type_col = '" + str(type_col) + "'"
        print(query)
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row[0] if row else None

    def addUserPermission(self, criteria_id, user_id, type_col):
        query = "INSERT INTO `permissions` (`criteria_id`, `user_id`, `type_col`) VALUES ('" + str(criteria_id) + "', '" + str(user_id) + "', '" + str(type_col) + "')"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def removeUserPermission(self, id)  :
        query = "DELETE FROM `permissions` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        self.sqlconnector.conn.commit()

    def fetchCriterias(self):
        rows = []
        query = "SELECT * FROM `criteria`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchCriteria(self, id):
        query = "SELECT * FROM `criteria` WHERE `id`='" + str(id) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    def fetchOwner(self):
        query = "SELECT * FROM `users` WHERE `username`='admin'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    def createOwner(self, password=''):
        # Check if admin user already exists
        query = "SELECT id FROM users WHERE username='admin'"
        self.cursor.execute(query)
        admin = self.cursor.fetchone()

        key = base64.urlsafe_b64encode(self.key.encode('utf-8'))
        cipher = Fernet(key)

        # Encrypt the password '12345'
        encrypted_password = cipher.encrypt(password.encode()).decode()

        if not admin:
            # Create admin user if doesn't exist
            query = "INSERT INTO `users` (`username`, `password`) VALUES ('admin', '" + str(encrypted_password) + "')"
            self.cursor.execute(query)
            self.sqlconnector.conn.commit()

            # Get amdin's user ID
            query = "SELECT id FROM users WHERE username='admin'"
            self.cursor.execute(query)
            admin_id = self.cursor.fetchone()[0]

            # Get all criteria
            query = "SELECT id FROM criteria"
            self.cursor.execute(query)
            criteria_rows = self.cursor.fetchall()

            # Add all permissions for admin
            for criteria in criteria_rows:
                criteria_id = criteria['id']
                # Add read permission
                query = "INSERT INTO permissions (criteria_id, user_id, type_col) VALUES (" + str(criteria_id) + ", " + str(admin_id) + ", 'R')"
                self.cursor.execute(query)
                # Add write permission
                query = "INSERT INTO permissions (criteria_id, user_id, type_col) VALUES (" + str(criteria_id) + ", " + str(admin_id) + ", 'W')"
                self.cursor.execute(query)

            self.sqlconnector.conn.commit()

            # Get full user record to return
            query = "SELECT * FROM users WHERE id = " + str(admin_id)
            self.cursor.execute(query)
            return self.cursor.fetchone()

        return admin

    def fetchAllMedia(self):
        rows = []
        query = "SELECT * FROM `media`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        self.sqlconnector.conn.commit()
        return rows

    def fetchMedia(self, name):
        row = []
        query = "SELECT * FROM `media` WHERE `name`='" + str(name) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row

    def addMedia(self, name, file):
        # Use parameterized query to safely handle binary data
        query = "INSERT INTO `media` (`name`, `file`) VALUES (%s, %s)"
        self.cursor.execute(query, (name, file))
        self.sqlconnector.conn.commit()

    def deleteMedia(self, name):
        query = "DELETE FROM `media` WHERE `name`=%s"
        self.cursor.execute(query, (name,))
        self.sqlconnector.conn.commit()

    def fetchManuals(self):
        query = "SELECT * FROM `manuals`"
        self.cursor.execute(query)
        rows = self.cursor.fetchall()
        return rows

    def fetchManual(self, name):
        query = "SELECT * FROM `manuals` WHERE `name`= '" + str(name) + "'"
        self.cursor.execute(query)
        row = self.cursor.fetchone()
        self.sqlconnector.conn.commit()
        return row
