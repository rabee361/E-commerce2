import win32api
from datetime import timedelta
from PyQt5.QtCore import Qt
from DatabaseOperations import DatabaseOperations

class SynchronizerHelper:
    def __init__(self, database_operations: DatabaseOperations):
        self.database_operations = database_operations


    def calculate_salaries_cost(self, manufacture_currency, manufacture_date, standard_work_hours, working_hours):
        salaries_cost = 0
        start_date = manufacture_date
        try:
            work_hours = float(standard_work_hours)
            work_duration = timedelta(hours=work_hours)
            end_date = start_date + work_duration
            standard_work_hours_per_day = self.database_operations.fetchHRSetting('setting_day_hours', commit=False)
            standard_work_hours_per_day = standard_work_hours_per_day[0] if standard_work_hours_per_day else 0
            
            payrolls_details = self.database_operations.fetchPayrollDetails(
                from_date=start_date.strftime('%Y-%m-%d'), to_date=end_date.strftime('%Y-%m-%d'),
                statement='paid_value', super=True, commit=False)
            for data in payrolls_details:
                id = data[0]
                salary_block_id = data[1]
                employee_id = data[2]
                statement = data[3]
                value = data[4]
                currency_id = data[5]
                name = data[6]
                currency_name = data[7]
                from_date = data[8]
                to_date = data[9]
                account_id = data[10]

                if currency_id != manufacture_currency:
                    exchange_value = self.database_operations.fetchExchangeValue(currency_id,manufacture_currency,manufacture_date.toString(Qt.ISODate), commit=False)
                    if exchange_value:
                        value = value * float(exchange_value[0][1])
                    else:
                        win32api.MessageBox(0,f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_SALARIES')}: {name}", "تنبيه")
                        return

                if account_id in self.salaries_costs_dict:
                    # If the ID is already in the dictionary, update the price and currency_id in the existing list
                    existing_entry = self.salaries_costs_dict[account_id]
                    existing_entry[0] += value  # Sum the price
                    existing_entry[1] = manufacture_currency  # Update the currency_id
                else:
                    # If the ID is not in the dictionary, create a new entry with a list containing [price, currency_id]
                    self.salaries_costs_dict[account_id] = [value, manufacture_currency]

                try:
                    days_count = (to_date - from_date).days
                    salary_per_day = float(value) / float(days_count)
                    salary_per_hour = salary_per_day / float(standard_work_hours_per_day)
                    fraction = float(working_hours) / float(standard_work_hours_per_day)
                    cost = float(salary_per_hour) * float(fraction)
                    salaries_cost += cost
                except ValueError:
                    return 0

        except ValueError:
            return 0

        return salaries_cost


    def calculate_year_month_expenses_cost(self, distribution_expense, distribution_expense_type, manufacture_currency, manufacture_date, quantity_expenses_target_unit, unit_quantity_produced, working_hours):

        total_expenses = 0 
       
        year = manufacture_date.year
        if distribution_expense == 'month':
            month = manufacture_date.month
        else:
            month = ''

        expenses = None
        expenses_divider = None

        if distribution_expense_type == 'quantity_expenses':
            quantity_data = self.database_operations.fetchQuantityOfManufacturedMaterials(
                unit=quantity_expenses_target_unit, year=year, month=month, commit=False)
            if quantity_data:
                expenses_divider = quantity_data[0]
                if expenses_divider and unit_quantity_produced:
                    expenses_divider += float(unit_quantity_produced)


        if distribution_expense_type == 'hours_expenses':
            hours_data = self.database_operations.fetchWorkHoursOfManufacturedMaterials(year=year, month=month, commit=False)
            if hours_data:
                expenses_divider = hours_data[0]
                # also include the time that is required for this manufacture process
                if expenses_divider and working_hours:
                    expenses_divider += float(working_hours)

        expenses_data = self.database_operations.fetchExpenses(year=year, month=month,calculated_in_manufacture=True,time_slot=distribution_expense, commit=False)

        if len(expenses_data) > 0:
            expenses_data = expenses_data[0]
        if expenses_data:
            expenses = expenses_data[2]
            currency = expenses_data[6]
            year = expenses_data[3]
            month = expenses_data[4]
            if currency != manufacture_currency:
                exchange_value = self.database_operations.fetchExchangeValue(currency, manufacture_currency,manufacture_date.toString(Qt.ISODate), commit=False)
                if exchange_value:
                    expenses = expenses * float(exchange_value[0][1])
                else:
                    latest_exchange_value = self.database_operations.fetchExchangeValue(currency, manufacture_currency, commit=False)
                    if latest_exchange_value:
                        expenses = expenses * float(latest_exchange_value[0][1])
                    else:
                        return 0
                    
        if expenses and expenses_divider:
            try:
                total_expenses = float(expenses) / float(expenses_divider)
            except ValueError:
                return 0
            
        return total_expenses
