import itertools
from typing import List
import win32api
from PyQt5.QtCore import Qt , QDate, QTranslator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from win32con import IDYES, MB_YESNO, IDNO
import Colors
from DatabaseOperations import DatabaseOperations
from Ui_PeriodStart import Ui_PeriodStart
from PyQt5.QtGui import QDoubleValidator
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QIcon
from LanguageManager import LanguageManager

class Ui_PeriodStart_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_PeriodStart()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/time_cycles.png'))
        self.language_manager.load_translated_ui(self.ui, window)   
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchCurrencies()
        self.fetchMaterials()
        self.fetchCostCenters()
        self.fetchWarehouses()
        self.fetchPrices()
        self.fetchUnits()
        self.fetchAccounts()
        self.setMaterialDefaults()
        self.updateMaterialDefaultPrice()
        self.fetchItems()

        self.ui.date_input.setDate(QDate.currentDate())
        self.ui.material_unit_price_input.setValidator(QDoubleValidator())
        self.ui.material_quantity_input.setValidator(QDoubleValidator())

        self.ui.cost_center_combobox.setEnabled(False)
        self.ui.material_warehouse_combobox.setEnabled(False)
        self.ui.material_combobox.setEnabled(False)
        self.ui.capital_account_combobox.setEnabled(False)
        self.ui.period_start_account_combobox.setEnabled(False)

        self.ui.material_combobox.currentIndexChanged.connect(lambda: self.updateMaterialDefaultPrice())
        self.ui.material_default_price_type_combobox.currentIndexChanged.connect(
            lambda: self.updateMaterialDefaultPrice())
        self.ui.material_unit_combobox.currentIndexChanged.connect(lambda: self.updateMaterialDefaultPrice())
        self.ui.material_combobox.currentIndexChanged.connect(lambda: self.setMaterialDefaults())

        self.ui.add_material_btn.clicked.connect(lambda: self.addItem())
        self.ui.add_material_btn.clicked.connect(lambda: self.fetchItems())
        self.ui.remove_material_btn.clicked.connect(lambda: self.removeItem())

        self.ui.select_cost_center_btn.clicked.connect(lambda: self.openSelectCostCenterWindow())
        self.ui.select_material_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.select_capital_account_btn.clicked.connect(lambda: self.openSelectCapitalAccountWindow())
        self.ui.select_period_start_account.clicked.connect(lambda: self.openSelectPeriodStartAccountWindow())
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())

        self.ui.generate_period_opening_entry_checkbox.stateChanged.connect(self.enableAccountsComboboxes)

    def openSelectCostCenterWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.cost_center_combobox.count()):
                if self.ui.cost_center_combobox.itemData(i)[0] == result['id']:
                    self.ui.cost_center_combobox.setCurrentIndex(i)
                    break

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.material_warehouse_combobox.count()):
                if self.ui.material_warehouse_combobox.itemData(i)[0] == result['id']:
                    self.ui.material_warehouse_combobox.setCurrentIndex(i)
                    break

    def openSelectCapitalAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.capital_account_combobox.setCurrentIndex(self.ui.capital_account_combobox.findData(result['id']))

    def openSelectPeriodStartAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.period_start_account_combobox.setCurrentIndex(self.ui.period_start_account_combobox.findData(result['id']))

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials')
        result = data_picker.showUi()
        
        if result is not None:
            # Iterate through all items in the combobox
            for i in range(self.ui.material_combobox.count()):
                material_data = self.ui.material_combobox.itemData(i)  # Get the stored material data (dictionary)
                
                # Check if the 'id' matches the result's 'id'
                if material_data and material_data.get('id') == result['id']:
                    self.ui.material_combobox.setCurrentIndex(i)  # Set the current index to the matching item
                    return  # Exit once the matching item is found

    def enableAccountsComboboxes(self, state):
        if state == 2:
            self.uiElementsActivator([self.ui.period_start_account_combobox, self.ui.capital_account_combobox],True)
        else:
            self.uiElementsActivator([self.ui.period_start_account_combobox, self.ui.capital_account_combobox],False)


    def uiElementsActivator(self, targets: List, state=False): #uiElementsEnabler
        print(targets)
        print(state)
        for ui_element in targets:
            ui_element.setEnabled(state)
   
    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            material_data = {
                "id": material[0],
                "code": material[1],
                "name": material[2],
                "group": material[3],
                "specs": material[4],
                "size": material[5],
                "manufacturer": material[6],
                "color": material[7],
                "origin": material[8],
                "quality": material[9],
                "type": material[10],
                "model": material[11],
                "unit1": material[12],
                "unit2": material[13],
                "unit3": material[14],
                "default_unit": material[15],
                "current_quantity": material[16],
                "max_quantity": material[17],
                "min_quantity": material[18],
                "request_limit": material[19],
                "gift": material[20],
                "gift_for": material[21],
                "price1_desc": material[22],
                "price1_1": material[23],
                "price1_1_unit": material[24],
                "price1_2": material[25],
                "price1_2_unit": material[26],
                "price1_3": material[27],
                "price1_3_unit": material[28],
                "price2_desc": material[29],
                "price2_1": material[30],
                "price2_1_unit": material[31],
                "price2_2": material[32],
                "price2_2_unit": material[33],
                "price2_3": material[34],
                "price2_3_unit": material[35],
                "price3_desc": material[36],
                "price3_1": material[37],
                "price3_1_unit": material[38],
                "price3_2": material[39],
                "price3_2_unit": material[40],
                "price3_3": material[41],
                "price3_3_unit": material[42],
                "price4_desc": material[43],
                "price4_1": material[44],
                "price4_1_unit": material[45],
                "price4_2": material[46],
                "price4_2_unit": material[47],
                "price4_3": material[48],
                "price4_3_unit": material[49],
                "price5_desc": material[50],
                "price5_1": material[51],
                "price5_1_unit": material[52],
                "price5_2": material[53],
                "price5_2_unit": material[54],
                "price5_3": material[55],
                "price5_3_unit": material[56],
                "price6_desc": material[57],
                "price6_1": material[58],
                "price6_1_unit": material[59],
                "price6_2": material[60],
                "price6_2_unit": material[61],
                "price6_3": material[62],
                "price6_3_unit": material[63],
                "expiray": material[64],
                "groupped": material[65]
            }
            code = material_data['code'] if material_data['code'] else ''
            name = material_data['name'] if material_data['name'] else ''
            display_text = name + " (" + code + ")"
            self.ui.material_combobox.addItem(display_text, material_data)

    def fetchWarehouses(self):
        self.ui.material_warehouse_combobox.clear()
        self.ui.material_warehouse_combobox.addItem(self.language_manager.translate("NONE"), [None, None])

        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse[0]
            display_text = warehouse[1]
            account_id = warehouse[5]
            data = [id, account_id]
            self.ui.material_warehouse_combobox.addItem(display_text, data)

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.material_unit_combobox.addItem(display_text, data)

    def fetchAccounts(self):
        # Fetch default capital account
        default_capital_account = self.database_operations.fetchSetting('default_capital_account')
        default_period_start_account = self.database_operations.fetchSetting('default_period_start_account')

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.period_start_account_combobox.addItem(display_text, data)
            self.ui.capital_account_combobox.addItem(display_text, data)

            # Check if the current item is the default capital account
            try:
                if int(id) == int(default_capital_account):
                    # Append "Default Account" to the text
                    display_text += f" ({self.language_manager.translate('CAPITAL_ACCOUNT')})"
                    # Set the text color to green
                    item_index = self.ui.capital_account_combobox.findData(id)
                    if item_index != -1:
                        self.ui.capital_account_combobox.setItemText(item_index, display_text)
                        self.ui.capital_account_combobox.setItemData(item_index, Colors.dark_green,
                                                                     role=Qt.ForegroundRole)
                        self.ui.capital_account_combobox.setCurrentIndex(item_index)
            except Exception as e:
                print(e)

            try:
                if int(id) == int(default_period_start_account):
                    display_text += f" ({self.language_manager.translate('FIRST_PERIOD_ACCOUNT')})"
                    item_index = self.ui.period_start_account_combobox.findData(id)
                    if item_index != -1:
                        self.ui.period_start_account_combobox.setItemText(item_index, display_text)
                        self.ui.period_start_account_combobox.setItemData(item_index, Colors.dark_green,
                                                                     role=Qt.ForegroundRole)
                        self.ui.period_start_account_combobox.setCurrentIndex(item_index)
            except Exception as e:
                print(e)

    def fetchPrices(self):
        prices = self.database_operations.fetchPrices()
        for price in prices:
            id = price[0]
            display_text = price[1]
            data = [id, None, None, None, None, None, None, None, None,
                    None]  # the data list holds the ID of the price type, and values of the three units prices and currencies (which are fetched in setMaterialDefaults())
            self.ui.material_default_price_type_combobox.addItem(display_text, data)

    def fetchCurrencies(self):
        self.ui.material_currency_combobox.clear()

        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            name = currencie[1]
            data = id
            self.ui.material_currency_combobox.addItem(name, data)

    def fetchCostCenters(self):
        self.ui.cost_center_combobox.clear()
        self.ui.cost_center_combobox.addItem(self.language_manager.translate("NONE"), [None, None])

        cost_centers = self.database_operations.fetchCostCenters(
            ['normal', 'distributor'])
        for cost_center in cost_centers:
            id = cost_center['id']
            name = cost_center['name'] 
            type = cost_center['type_col']
            data = [id, type]
            self.ui.cost_center_combobox.addItem(name, data)

    def setMaterialDefaults(self):
        material_data = self.ui.material_combobox.currentData()
        if material_data:
            # default units
            material_units = [material_data['unit1'], material_data['unit2'], material_data['unit3']]
            default_unit = material_data['default_unit']
            default_unit_value = material_units[material_data['default_unit'] - 1]

            # We need to hide the units that are not used in the material definition (Material Card)
            # Iterate through the items in the combobox
            for index in range(self.ui.material_unit_combobox.count()):
                # Get the ID of the item
                item_data = self.ui.material_unit_combobox.itemData(index)
                # Compare the item with the elements in the material_units list
                if item_data in material_units:
                    # If found, show the item
                    self.ui.material_unit_combobox.model().item(index).setEnabled(True)
                else:
                    # If not found, hide the item
                    self.ui.material_unit_combobox.model().item(index).setEnabled(False)

            # cast variables in order to compare them in ifs
            price1_desc = str(material_data['price1_desc']) if material_data['price1_desc'] else None
            price2_desc = str(material_data['price2_desc']) if material_data['price2_desc'] else None
            price3_desc = str(material_data['price3_desc']) if material_data['price3_desc'] else None
            price4_desc = str(material_data['price4_desc']) if material_data['price4_desc'] else None
            price5_desc = str(material_data['price5_desc']) if material_data['price5_desc'] else None
            price6_desc = str(material_data['price6_desc']) if material_data['price6_desc'] else None
            price1_1 = str(material_data['price1_1']) if material_data['price1_1'] else None
            price1_2 = str(material_data['price1_2']) if material_data['price1_2'] else None
            price1_3 = str(material_data['price1_3']) if material_data['price1_3'] else None
            price2_1 = str(material_data['price2_1']) if material_data['price2_1'] else None
            price2_2 = str(material_data['price2_2']) if material_data['price2_2'] else None
            price2_3 = str(material_data['price2_3']) if material_data['price2_3'] else None
            price3_1 = str(material_data['price3_1']) if material_data['price3_1'] else None
            price3_2 = str(material_data['price3_2']) if material_data['price3_2'] else None
            price3_3 = str(material_data['price3_3']) if material_data['price3_3'] else None
            price4_1 = str(material_data['price4_1']) if material_data['price4_1'] else None
            price4_2 = str(material_data['price4_2']) if material_data['price4_2'] else None
            price4_3 = str(material_data['price4_3']) if material_data['price4_3'] else None
            price5_1 = str(material_data['price5_1']) if material_data['price5_1'] else None
            price5_2 = str(material_data['price5_2']) if material_data['price5_2'] else None
            price5_3 = str(material_data['price5_3']) if material_data['price5_3'] else None
            price6_1 = str(material_data['price6_1']) if material_data['price6_1'] else None
            price6_2 = str(material_data['price6_2']) if material_data['price6_2'] else None
            price6_3 = str(material_data['price6_3']) if material_data['price6_3'] else None
            price1_1_unit = str(material_data['price1_1_unit']) if material_data['price1_1_unit'] else None
            price1_2_unit = str(material_data['price1_2_unit']) if material_data['price1_2_unit'] else None
            price1_3_unit = str(material_data['price1_3_unit']) if material_data['price1_3_unit'] else None
            price2_1_unit = str(material_data['price2_1_unit']) if material_data['price2_1_unit'] else None
            price2_2_unit = str(material_data['price2_2_unit']) if material_data['price2_2_unit'] else None
            price2_3_unit = str(material_data['price2_3_unit']) if material_data['price2_3_unit'] else None
            price3_1_unit = str(material_data['price3_1_unit']) if material_data['price3_1_unit'] else None
            price3_2_unit = str(material_data['price3_2_unit']) if material_data['price3_2_unit'] else None
            price3_3_unit = str(material_data['price3_3_unit']) if material_data['price3_3_unit'] else None
            price4_1_unit = str(material_data['price4_1_unit']) if material_data['price4_1_unit'] else None
            price4_2_unit = str(material_data['price4_2_unit']) if material_data['price4_2_unit'] else None
            price4_3_unit = str(material_data['price4_3_unit']) if material_data['price4_3_unit'] else None
            price5_1_unit = str(material_data['price5_1_unit']) if material_data['price5_1_unit'] else None
            price5_2_unit = str(material_data['price5_2_unit']) if material_data['price5_2_unit'] else None
            price5_3_unit = str(material_data['price5_3_unit']) if material_data['price5_3_unit'] else None
            price6_1_unit = str(material_data['price6_1_unit']) if material_data['price6_1_unit'] else None
            price6_2_unit = str(material_data['price6_2_unit']) if material_data['price6_2_unit'] else None
            price6_3_unit = str(material_data['price6_3_unit']) if material_data['price6_3_unit'] else None

            # default prices of the material (pricetype, prices ... values, prices ... units)
            prices = [
                (price1_desc, price1_1, price1_2, price1_3, price1_1_unit, price1_2_unit, price1_3_unit),
                (price2_desc, price2_1, price2_2, price2_3, price2_1_unit, price2_2_unit, price2_3_unit),
                (price3_desc, price3_1, price3_2, price3_3, price3_1_unit, price3_2_unit, price3_3_unit),
                (price4_desc, price4_1, price4_2, price4_3, price4_1_unit, price4_2_unit, price4_3_unit),
                (price5_desc, price5_1, price5_2, price5_3, price5_1_unit, price5_2_unit, price5_3_unit),
                (price6_desc, price6_1, price6_2, price6_3, price6_1_unit, price6_2_unit, price6_3_unit)
            ]

            for index in range(self.ui.material_default_price_type_combobox.count()):
                data = self.ui.material_default_price_type_combobox.itemData(index)
                price_type = data[0]
                data = [price_type, material_data['unit1'], None, None, material_data['unit2'], None, None,
                        material_data['unit3'], None,
                        None]  # we have three units, for each unit we need price & currency
                self.ui.material_default_price_type_combobox.setItemData(index, data)

            for price in prices:
                for index in range(self.ui.material_default_price_type_combobox.count()):
                    data = self.ui.material_default_price_type_combobox.itemData(index)
                    if str(data[0]) == str(price[0]):  # price description
                        data[2] = price[1]
                        data[3] = price[4]
                        data[5] = price[2]
                        data[6] = price[5]
                        data[8] = price[3]
                        data[9] = price[6]
                        self.ui.material_default_price_type_combobox.setItemData(index, data)

            # print(default_invoice_price)
            # print(default_cost_price)
            # print(default_gift_price)

            # set default unit
            self.ui.material_unit_combobox.setCurrentIndex(self.ui.material_unit_combobox.findData(default_unit_value))

    def updateMaterialDefaultPrice(self):
        price_value = None
        currency = None
        self.ui.material_unit_price_input.clear()

        # get unit id
        unit_id = self.ui.material_unit_combobox.currentData()
        # check if unit is currently select price type
        # for i in range(self.ui.material_default_price_type_combobox.count()):
        data = self.ui.material_default_price_type_combobox.currentData()
        # print("data=" + str(data))
        price_units = [data[1], data[4], data[7]]
        # print("uid=" + str(unit_id))
        # print("price_units=" + str(price_units))
        if unit_id in price_units:
            index = price_units.index(unit_id)
            if index == 0:
                price_value = data[2]
                currency = data[3]
            elif index == 1:
                price_value = data[5]
                currency = data[6]
            elif index == 2:
                price_value = data[8]
                currency = data[9]
        if price_value:
            self.ui.material_unit_price_input.setText(str(price_value))
        if currency:
            # print("c="+currency+" "+type(currency))
            self.ui.material_currency_combobox.setCurrentIndex(
                self.ui.material_currency_combobox.findData(currency))

    def addItem(self):
        # Get fields inputs
        material_unit_price = self.ui.material_unit_price_input.text()
        material_notes = self.ui.material_notes_input.text()
        quantity = self.ui.material_quantity_input.text()
        material_default_price_type_id = self.ui.material_default_price_type_combobox.currentData()[0]
        material_warehouse_id = self.ui.material_warehouse_combobox.currentData()[0]
        # material_warehouse_account = self.ui.material_warehouse_combobox.currentData()[1]
        material_unit_id = self.ui.material_unit_combobox.currentData()
        material_currency_id = self.ui.material_currency_combobox.currentData()
        date = self.ui.date_input.date().toString(Qt.ISODate)
        cost_center_combobox = self.ui.cost_center_combobox.currentData()

        if str(material_warehouse_id).lower() == 'none' or (not material_unit_price or str(material_unit_price) == ''):
            message = self.language_manager.translate("VALUES_ENTERED_ERROR")
            win32api.MessageBox(0, message, self.language_manager.translate("ALERT"))
            return

        cost_center_id = None
        distributive_cost_centers_value = None
        if cost_center_combobox:
            cost_center_id = cost_center_combobox[0]
            cost_center_type = cost_center_combobox[1]

            distributive_cost_centers_value=[]
            if cost_center_type and cost_center_type in ('distributor'):
                # fetch distributed cost centers
                journal_entry_distributive_cost_center_centers = self.database_operations.fetchCostCenterAggregationsDistributives(
                    cost_center_id)
                if journal_entry_distributive_cost_center_centers:
                    for journal_entry_distributive_cost_center_account in journal_entry_distributive_cost_center_centers:
                        cost_centers_aggregations_distributive_enty_id = journal_entry_distributive_cost_center_account[
                            0]
                        division_factor = journal_entry_distributive_cost_center_account[3]
                        # master_cost_center_id = journal_entry_distributive_cost_center_account[1]
                        # distributed_cost_center_name = journal_entry_distributive_cost_center_account[4]
                        # distributed_cost_center_id = journal_entry_distributive_cost_center_account[2]

                        distributive_cost_centers_value.append([cost_centers_aggregations_distributive_enty_id, division_factor])

            if not distributive_cost_centers_value:
                distributive_cost_centers_value = None

        # Get material data
        material_data = self.ui.material_combobox.currentData()
        material_id = material_data['id']

        # Units registered with the material
        unit1_id = material_data['unit1']
        unit2_id = material_data['unit2']
        unit3_id = material_data['unit3']
        material_units = [unit1_id, unit2_id, unit3_id]

        quantities_and_units = [{"unit_id": unit1_id if unit1_id is not None else '', "quantity": ""},
                                {"unit_id": unit2_id if unit2_id is not None else '', "quantity": ""},
                                {"unit_id": unit3_id if unit3_id is not None else '', "quantity": ""}]
        # Set the quantity of the selected unit in the UI to match the quantity entered in the quantity input in the UI
        for item in quantities_and_units:
            if item['unit_id'] == material_unit_id:
                item['quantity'] = quantity

        if all([quantity, material_unit_price, material_unit_price]):
            # Calculate value of quantity in all units
            valid_units = [unit for unit in material_units if unit is not None]  # Filter out None units
            units_pairs = list(itertools.combinations(valid_units, 2))  # Get all possible pairs of valid units
            for units_pair in units_pairs:
                unit1, unit2 = units_pair
                if unit1 == material_unit_id:
                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1, unit2)
                elif unit2 == material_unit_id:
                    unit1, unit2 = unit2, unit1
                    conversion_rate = self.database_operations.fetchUnitConversionValueBetween(unit1, unit2)
                else:
                    conversion_rate = None
                if conversion_rate:
                    temp_quantity = float(quantity) * float(conversion_rate) if conversion_rate else ""
                    for item in quantities_and_units:
                        if item["unit_id"] == unit2:
                            item["quantity"] = "{:f}".format(temp_quantity).rstrip("0").rstrip(".")
                            # "{:f}".format(x) : This formats the value of the variable x as a floating point number. The 'f' after the colon specifies that we want to format the number as a floating point.
                            # .rstrip("0") : This method returns a copy of the string with trailing occurrences of the specified characters removed. In this case, it removes all trailing zeros.
                            # .rstrip(".") : This method removes the trailing period. This step is necessary because the previous step may have removed all the trailing zeros, leaving just a period.
                            break

            quantity_1 = quantities_and_units[0]["quantity"]
            unit_id_1 = quantities_and_units[0]["unit_id"]
            quantity_2 = quantities_and_units[1]["quantity"]
            unit_id_2 = quantities_and_units[1]["unit_id"]
            quantity_3 = quantities_and_units[2]["quantity"]
            unit_id_3 = quantities_and_units[2]["unit_id"]

            period_start_material_id = self.database_operations.addPeriodStartMaterial(material_id, quantity_1,
                                                                                       unit_id_1, quantity_2, unit_id_2,
                                                                                       quantity_3, unit_id_3,
                                                                                       material_unit_price,
                                                                                       material_currency_id,
                                                                                       material_warehouse_id,
                                                                                       material_notes, date,
                                                                                       commit=False)
            
            # Add material to warehouse
            warehouse_entry_id = self.database_operations.addMaterialToWarehouse(material_warehouse_id, material_id, quantity, unit1_id, commit=False)

            if self.ui.generate_period_opening_entry_checkbox.isChecked():
                journal_entry_id = self.database_operations.addJournalEntry(date, currency=material_currency_id,
                                                                        origin_type='period_start_material',
                                                                        origin_id=period_start_material_id,
                                                                        commit=False)


                warehouse_account_id = self.ui.material_warehouse_combobox.currentData()[1]
                period_start_account_id = self.ui.period_start_account_combobox.currentData()
                capital_account_id = self.ui.capital_account_combobox.currentData()

                statemenet = "Period opening " + self.ui.material_combobox.currentText()
                value = float(quantity) * float(material_unit_price)

                self.database_operations.addJournalEntryItem(journal_entry_id, material_currency_id, 'creditor',
                                                             statemenet, capital_account_id, period_start_account_id, value,
                                                             cost_center_id,
                                                             distributive_cost_centers_value,
                                                             commit=False)

        else:
            win32api.MessageBox(0, self.language_manager.translate("MATERIAL_INSERT_ERROR"), self.language_manager.translate("ERROR"))

    def removeItem(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
        if (messagebox_result == IDYES):
            selected_row = self.ui.materials_table.currentRow()
            if selected_row >= 0:
                id = self.ui.materials_table.item(selected_row, 0).text()
                self.database_operations.removePeriodStartMaterial(id)
                self.fetchItems()
        if (messagebox_result == IDNO):
            pass

    def fetchItems(self):
        self.ui.materials_table.setRowCount(0)
        period_start_items = self.database_operations.fetchPeriodStartMaterials()
        for period_start_item in period_start_items:
            id = period_start_item[0]
            material_id = period_start_item[1]
            quantity1 = period_start_item[2]
            unit1_id = period_start_item[3]
            quantity2 = period_start_item[4]
            unit2_id = period_start_item[5]
            quantity3 = period_start_item[6]
            unit3_id = period_start_item[7]
            unit_price = period_start_item[8]
            currency = period_start_item[9]
            warehouse_id = period_start_item[10]
            notes = period_start_item[11]
            date = period_start_item[12]
            name = period_start_item[13]
            unit1_name = period_start_item[14]
            unit2_name = period_start_item[15]
            unit3_name = period_start_item[16]
            currency_name = period_start_item[17]
            warehouse_name = period_start_item[18]
            warehouse_account = period_start_item[19]

            row = self.ui.materials_table.rowCount()
            self.ui.materials_table.insertRow(row)

            self.ui.materials_table.setItem(row, 0, QTableWidgetItem(str(id)))
            self.ui.materials_table.setItem(row, 1, QTableWidgetItem(str(material_id)))
            self.ui.materials_table.setItem(row, 2, QTableWidgetItem(name))
            self.ui.materials_table.setItem(row, 3, QTableWidgetItem(str(quantity1)))
            self.ui.materials_table.setItem(row, 4, QTableWidgetItem(str(unit1_id)))
            self.ui.materials_table.setItem(row, 5, QTableWidgetItem(unit1_name))
            self.ui.materials_table.setItem(row, 6, QTableWidgetItem(str(quantity2)))
            self.ui.materials_table.setItem(row, 7, QTableWidgetItem(str(unit2_id)))
            self.ui.materials_table.setItem(row, 8, QTableWidgetItem(unit2_name))
            self.ui.materials_table.setItem(row, 9, QTableWidgetItem(str(quantity3)))
            self.ui.materials_table.setItem(row, 10, QTableWidgetItem(str(unit3_id)))
            self.ui.materials_table.setItem(row, 11, QTableWidgetItem(unit3_name))
            self.ui.materials_table.setItem(row, 12, QTableWidgetItem(str(unit_price)))
            self.ui.materials_table.setItem(row, 13, QTableWidgetItem(str(currency)))
            self.ui.materials_table.setItem(row, 14, QTableWidgetItem(currency_name))
            self.ui.materials_table.setItem(row, 15, QTableWidgetItem(str(warehouse_id)))
            self.ui.materials_table.setItem(row, 16, QTableWidgetItem(warehouse_name))
            self.ui.materials_table.setItem(row, 17, QTableWidgetItem(notes))
            self.ui.materials_table.setItem(row, 18, QTableWidgetItem(str(warehouse_account)))
            self.ui.materials_table.setItem(row, 19, QTableWidgetItem(str(date)))
