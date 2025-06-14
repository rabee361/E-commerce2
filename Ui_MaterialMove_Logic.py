import win32api
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QDoubleValidator, QColor
from PyQt5.QtWidgets import QDialog
from LanguageManager import LanguageManager
from Colors import dark_green, light_grey
from DatabaseOperations import DatabaseOperations
from Ui_MaterialMove import Ui_MaterialMove
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtCore import QDate
from win32con import MB_YESNO, IDYES, IDNO, MB_OK , MB_ICONWARNING
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QTranslator


class Ui_MaterialMove_Logic(QDialog):
    def __init__(self, sql_connector, source_warehouse=None, warehouse_entry=None, independent=False):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.independent = independent
        self.ui = Ui_MaterialMove()
        self.source_warehouse = int(source_warehouse)
        self.warehouse_entry = int(warehouse_entry)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.setWindowIcon(QIcon('icons/set-parnet.png'))
        window.exec()

    def initialize(self, window):
        self.float_point_precision = ''
        self.fetchFloatPointValue()
        if self.source_warehouse and self.warehouse_entry:
            self.fetchWarehouses()
            self.fetchMaterials()
            self.fetchUnits()
            self.fetchCurrencies()
            self.setOriginTypes()
            if self.independent:
                self.ui.select_from_account_warehouse_btn.setEnabled(False)
                self.ui.select_to_account_warehouse_btn.setEnabled(False)

            self.fetchAccounts(self.ui.from_account_warehouse_combobox)
            self.fetchAccounts(self.ui.to_account_warehouse_combobox)
            self.ui.from_account_warehouse_combobox.currentIndexChanged.connect(lambda: self.setCreateJournalEntryState())
            self.ui.to_account_warehouse_combobox.currentIndexChanged.connect(lambda: self.setCreateJournalEntryState())
            self.ui.add_journal_entry_checkbox.clicked.connect(lambda: self.setCreateJournalEntryState())
            self.ui.select_from_account_warehouse_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.from_account_warehouse_combobox))
            self.ui.select_to_account_warehouse_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.to_account_warehouse_combobox))



            self.ui.from_warehouse_combobox.currentIndexChanged.connect(
                lambda: self.setDefaultWarehouseAccount(self.ui.from_warehouse_combobox,self.ui.from_account_warehouse_combobox))
            self.ui.to_warehouse_combobox.currentIndexChanged.connect(lambda: self.setDefaultWarehouseAccount(self.ui.to_warehouse_combobox,self.ui.to_account_warehouse_combobox))
            self.setSource()

            self.ui.move_btn.clicked.connect(lambda: self.save(window))
            self.ui.move_quantity_input.setValidator(QDoubleValidator())
            self.ui.journal_entry_item_value.setValidator(QDoubleValidator())

            self.ui.to_warehouse_combobox.setEnabled(False)
            self.ui.from_warehouse_combobox.setEnabled(False)
            self.ui.to_account_warehouse_combobox.setEnabled(False)
            self.ui.from_account_warehouse_combobox.setEnabled(False)
            self.ui.select_to_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow(self.ui.to_warehouse_combobox))


    def fetchFloatPointValue(self):
        self.float_point_precision = self.database_operations.fetchFloatPointValue()    

    def fetchWarehouses(self):
        self.ui.from_warehouse_combobox.clear()
        self.ui.to_warehouse_combobox.clear()
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse['id']
            name = warehouse['name']
            # code = warehouse['code']
            parent_id = warehouse['parent_id']
            parent_name = warehouse['parent_name']
            account = warehouse['account']

            data = [id, account]

            self.ui.from_warehouse_combobox.addItem(name, data)
            self.ui.to_warehouse_combobox.addItem(name, data)

    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material['id']
            name = material['name']
            # unit_price = material['unit_price']
            self.ui.materials_combobox.addItem(name, id)

    def fetchUnits(self):
        self.ui.move_unit_combobox.clear()
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.move_unit_combobox.addItem(display_text, data)
            self.ui.warehouse_unit_combobox.addItem(display_text, data)

    def fetchAccounts(self, target_combobox):
        data = None
        view_name = "لا يوجد"
        target_combobox.addItem(view_name, data)

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account['id']
            name = account['name']
            code = account['code']
            # details = account['details];
            # date = account['date'];
            # parent_id = account['parent_id'];
            # parent_name = account['parent_name'];

            data = id
            view_name = code + " - " + name
            target_combobox.addItem(view_name, data)

    def openSelectWarehouseWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses')
        result = data_picker.showUi()
        if result is not None:
            for i in range(combobox.count()):
                if combobox.itemData(i)[0] == result['id']:
                    combobox.setCurrentIndex(i)
                    break

    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def setOriginTypes(self):
        origin_types = {
            self.language_manager.translate("ORIGIN_TYPE_NONE"):"",
            self.language_manager.translate("ORIGIN_TYPE_INVOICE"):"invoice",
            self.language_manager.translate("ORIGIN_TYPE_MANUFACTURE"):"manufacture"
        }

        for key, value in origin_types.items():
            self.ui.journal_entry_origin_combobox.addItem(key, value)
        self.ui.journal_entry_origin_combobox.setCurrentIndex(0)
        
    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            data = id
            self.ui.journal_entry_item_currency_combobox.addItem(display_text, data)
    
    def setDefaultWarehouseAccount(self, warehouses_combobox, accounts_combobox):
        accounts_combobox.clear()
        self.fetchAccounts(accounts_combobox)
        warehouse_data = warehouses_combobox.currentData()
        if warehouse_data:
            warehouse_id = warehouse_data[0]
            account_id = warehouse_data[1]
            warehouse_account_index = accounts_combobox.findData(account_id)
            if warehouse_account_index:
                item_text = accounts_combobox.itemText(warehouse_account_index)
                new_item_text = item_text + " (" + self.language_manager.translate("DEFAULT_WAREHOUSE_ACCOUNT") + ")"
                accounts_combobox.setItemText(warehouse_account_index, new_item_text)
                # Set the foreground and background colors of the item
                accounts_combobox.setItemData(warehouse_account_index, dark_green, role=Qt.ForegroundRole)
                accounts_combobox.setCurrentIndex(warehouse_account_index)

    def setCreateJournalEntryState(self):
        from_account = self.ui.from_account_warehouse_combobox.currentData()
        to_account = self.ui.to_account_warehouse_combobox.currentData()
        if from_account and to_account:
            self.ui.add_journal_entry_checkbox.setEnabled(True)
        else:
            self.ui.add_journal_entry_checkbox.setDisabled(True)
            self.ui.add_journal_entry_checkbox.setChecked(False)

        if self.ui.add_journal_entry_checkbox.isChecked():
            self.ui.journal_entry_item_value.setEnabled(True)
            self.ui.journal_entry_item_currency_combobox.setEnabled(True)
        else:
            self.ui.journal_entry_item_value.setDisabled(True)
            self.ui.journal_entry_item_currency_combobox.setDisabled(True)

    def setSource(self):
        if self.source_warehouse and self.warehouse_entry:
            from_warehouse_selected = False

            for index in range(self.ui.from_warehouse_combobox.count()):
                item_data = self.ui.from_warehouse_combobox.itemData(index)
                if item_data:
                    warehouse_id = item_data[0]
                    account_id = item_data[1]
                    if warehouse_id == self.source_warehouse:
                        self.ui.from_warehouse_combobox.model().item(index).setEnabled(True)
                        self.ui.from_warehouse_combobox.setCurrentIndex(index)
                        from_warehouse_selected = True
                    else:
                        self.ui.from_warehouse_combobox.setItemData(index, light_grey, role=Qt.ForegroundRole)
                        self.ui.from_warehouse_combobox.model().item(index).setEnabled(False)

            if not from_warehouse_selected:
                self.ui.from_warehouse_combobox.setCurrentIndex(-1)

            for index in range(self.ui.to_warehouse_combobox.count()):
                item_data = self.ui.to_warehouse_combobox.itemData(index)
                if item_data:
                    warehouse_id = item_data[0]
                    account_id = item_data[1]
                    if warehouse_id == self.source_warehouse:
                        self.ui.to_warehouse_combobox.model().item(index).setEnabled(False)
                        self.ui.to_warehouse_combobox.setItemData(index, light_grey, role=Qt.ForegroundRole)
            

            # fetch warehouse entry unit
            warehouse_entry = self.database_operations.fetchWarehouseEntry(warehouse_entry_id=self.warehouse_entry, warehouse_id=self.source_warehouse)
            if warehouse_entry:
                id = warehouse_entry['id']
                material_id = warehouse_entry['material_id']
                quantity = warehouse_entry['quantity']
                unit = warehouse_entry['unit']
                production_batch_id = warehouse_entry['production_batch_id']
                receipt_doc_id = warehouse_entry['receipt_doc_id']
                batch_number = warehouse_entry['batch_number']
                batch_mfg = warehouse_entry['batch_mfg']
                # batch_exp = warehouse_entry['batch_exp']
                material_move_id = warehouse_entry['material_move_id']
                code = warehouse_entry['code']
                material_name = warehouse_entry['name']

                for index in range(self.ui.journal_entry_origin_combobox.count()):
                    item_data = self.ui.journal_entry_origin_combobox.itemData(index)
                    item_data = [item_data, material_move_id, production_batch_id]
                    self.ui.journal_entry_origin_combobox.setItemData(index, item_data)

                self.ui.warehouse_quantity_input.setText(str(quantity))
                self.ui.warehouse_unit_combobox.setCurrentIndex(self.ui.warehouse_unit_combobox.findData(unit))
                self.ui.materials_combobox.setCurrentIndex(self.ui.materials_combobox.findData(material_id))

                for index in range(self.ui.materials_combobox.count()):
                    item_data = self.ui.materials_combobox.itemData(index)
                    if item_data == material_id:
                        item_data = [item_data, production_batch_id, material_move_id, material_name]
                        self.ui.materials_combobox.setItemData(index, item_data)


                    cost = 0
                    currency = ''
                    invoice_data=self.database_operations.fetchInvoiceItem(material_move_id)
                    move_unit = self.ui.move_unit_combobox.currentData()
                    if invoice_data:
                        for index in range(self.ui.journal_entry_origin_combobox.count()):
                            item_data = self.ui.journal_entry_origin_combobox.itemData(index)
                            if item_data:
                                if item_data[0]=='invoice':
                                    self.ui.journal_entry_origin_combobox.setCurrentIndex(index)

                        invoice_item_unit_price = invoice_data['unit_price']
                        invoice_item_unit1_id = invoice_data['unit1_id']
                        invoice_item_currency_id = invoice_data['currency_id']


                        if int(invoice_item_unit1_id) ==int(move_unit):
                            cost = float(invoice_item_unit_price)*(quantity)
                        else:
                            unit_conversion_rate=self.database_operations.fetchUnitConversionValueBetween(move_unit, invoice_item_unit1_id)
                            cost=unit_conversion_rate*invoice_item_unit_price*quantity
                        currency = invoice_item_currency_id

                    production_batch_data = self.database_operations.fetchManufactureProcess(production_batch_id)
                    production_batch_materials = self.database_operations.fetchManufactureProcessProducedMaterials(production_batch_id)
                    if production_batch_materials:
                        for production_batch_material in production_batch_materials:
                            if production_batch_material['material_id'] == material_id:
                                break
                            else:
                                win32api.MessageBox(0, self.language_manager.translate("ALERT_MANUFACTURE_PROCESS_CONFLICT"), self.language_manager.translate("ALERT"))
                                return
                            
                    if production_batch_data:
                        for index in range(self.ui.journal_entry_origin_combobox.count()):
                            item_data = self.ui.journal_entry_origin_combobox.itemData(index)
                            if item_data:
                                if item_data[0]=='manufacture':
                                    self.ui.journal_entry_origin_combobox.setCurrentIndex(index)

                        batch_quantity1 = production_batch_material['quantity1'] if production_batch_material else ''
                        batch_unit1 = production_batch_material['unit1'] if production_batch_material else ''
                        batch_quantity2 = production_batch_material['quantity2'] if production_batch_material else ''
                        batch_unit2 = production_batch_material['unit2'] if production_batch_material else ''
                        batch_quantity3 = production_batch_material['quantity3'] if production_batch_material else ''
                        batch_unit3 = production_batch_material['unit3'] if production_batch_material else ''
                        
                        batch_machines_operation_cost = production_batch_data['machines_operation_cost']
                        batch_salaries_cost = production_batch_data['salaries_cost']
                        batch_composition_materials_cost = production_batch_data['composition_materials_cost']
                        batch_currency = production_batch_data['currency']
                        #calcualte batch cost

                        if batch_machines_operation_cost is None or batch_machines_operation_cost == '' or batch_machines_operation_cost == 'None':
                            batch_machines_operation_cost = 0

                        if batch_salaries_cost is None or batch_salaries_cost == '' or batch_salaries_cost == 'None':
                            batch_salaries_cost = 0

                        if batch_composition_materials_cost is None or batch_composition_materials_cost == '' or batch_composition_materials_cost == 'None':
                            batch_composition_materials_cost = 0

                        currency = batch_currency
                        batch_cost = float(batch_composition_materials_cost)+(float(batch_machines_operation_cost)+float(batch_salaries_cost))


                        if move_unit == batch_unit1:
                            unit_cost = batch_cost/batch_quantity1
                            cost = float(unit_cost)*float(quantity)
                        elif move_unit == batch_unit2:
                            unit_cost = batch_cost/batch_quantity2
                            cost = float(unit_cost)*float(quantity)
                        elif move_unit == batch_unit3:
                            unit_cost = batch_cost/batch_quantity3
                            cost = float(unit_cost)*float(quantity)
                        
                    # This is the most basic way of dividing the cost of production
                    num_produced_items = len(production_batch_materials)
                    if num_produced_items > 0:
                        cost = cost / num_produced_items

                    self.ui.journal_entry_item_value.setText(str(round(cost, int(self.float_point_precision))))
                    self.ui.journal_entry_item_currency_combobox.setCurrentIndex(self.ui.journal_entry_item_currency_combobox.findData(currency))

                # fetch material units:
                material_data = self.database_operations.fetchMaterial(material_id)
                if material_data:
                    id = material_data[0]
                    unit1 = material_data['unit1']
                    unit2 = material_data['unit2']
                    unit3 = material_data['unit3']
                    unit1_to_unit2_rate = material_data['unit1_to_unit2_rate']
                    unit1_to_unit3_rate = material_data['unit1_to_unit3_rate']

                    max_of_unit1 = 0
                    max_of_unit2 = 0
                    max_of_unit3 = 0
                    conversion_rates = {}
                    if int(unit) == unit1:
                        max_of_unit1 = quantity
                        max_of_unit2 = quantity * unit1_to_unit2_rate if unit1_to_unit2_rate else 0
                        max_of_unit3 = quantity * unit1_to_unit3_rate if unit1_to_unit3_rate else 0
                        conversion_rates = {unit1: 1, unit2: 1 / float(unit1_to_unit2_rate) if unit1_to_unit2_rate else 0,
                                            unit3: 1 / float(unit1_to_unit3_rate) if unit1_to_unit3_rate else 0}
                    elif int(unit) == unit2:
                        max_of_unit1 = quantity / unit1_to_unit2_rate if unit1_to_unit2_rate else 0
                        max_of_unit2 = quantity
                        max_of_unit3 = quantity / unit1_to_unit2_rate * unit1_to_unit3_rate if unit1_to_unit2_rate and unit1_to_unit3_rate else 0
                        conversion_rates = {unit1: float(unit1_to_unit2_rate) if unit1_to_unit2_rate else 0,
                                            unit2: 1,
                                            unit3: 1 / (float(unit1_to_unit3_rate) / float(unit1_to_unit2_rate)) if unit1_to_unit2_rate and unit1_to_unit3_rate else 0}
                    elif int(unit) == unit3:
                        max_of_unit1 = quantity / unit1_to_unit3_rate if unit1_to_unit3_rate else 0
                        max_of_unit2 = quantity / unit1_to_unit3_rate * unit1_to_unit2_rate if unit1_to_unit3_rate and unit1_to_unit2_rate else 0
                        max_of_unit3 = quantity
                        conversion_rates = {unit1: float(unit1_to_unit3_rate),
                                            unit2: float(unit1_to_unit3_rate) / float(unit1_to_unit2_rate),
                                            unit3: 1}
                    allowed_units = [[unit1, max_of_unit1, conversion_rates], [unit2, max_of_unit2, conversion_rates],
                                     [unit3, max_of_unit3, conversion_rates]]

                    move_unit_selected = False
                    for index in range(self.ui.move_unit_combobox.count()):
                        item_data = self.ui.move_unit_combobox.itemData(index)

                        # Check if the item exists in the allowed_units list
                        found = False
                        for allowed_unit in allowed_units:
                            if allowed_unit[0] == item_data:
                                # Replace the item data with the unit list
                                self.ui.move_unit_combobox.setItemData(index, allowed_unit)
                                found = True
                                move_unit_selected = True
                                break

                        # If the item does not exist in allowed_units, set its data as [item_data, None]
                        if not found:
                            self.ui.move_unit_combobox.setItemData(index, [item_data, None, None])
                            self.ui.move_unit_combobox.setItemData(index, light_grey, role=Qt.ForegroundRole)
                            self.ui.move_unit_combobox.model().item(index).setEnabled(False)

                    if not move_unit_selected:
                        self.ui.move_unit_combobox.setCurrentIndex(-1)

                    # for index in range(self.ui.move_unit_combobox.count()):
                    #     item_data = self.ui.move_unit_combobox.itemData(index)
                    #     print(item_data)

        for index in range(self.ui.to_warehouse_combobox.count()):
            if self.ui.to_warehouse_combobox.model().item(index).isEnabled():
                self.ui.to_warehouse_combobox.setCurrentIndex(index)
                break
        
        for index in range(self.ui.move_unit_combobox.count()):
            if self.ui.move_unit_combobox.model().item(index).isEnabled():
                self.ui.move_unit_combobox.setCurrentIndex(index)
                break
        

    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            return 1
        else:
            return int(last_invoice_number) + 1

    def addInputInvoice(self, currency_id, equilivance_price, unit_price, add_journal_entry, quantity):
        input_type_id = self.database_operations.fetchInvoiceTypes(name='input')
        if input_type_id:
            # Get warehouse and account data
            warehouse_data = self.ui.from_warehouse_combobox.currentData()
            warehouse_id = warehouse_data[0] if isinstance(warehouse_data, (list, tuple)) else warehouse_data
            
            # Get move unit data
            move_unit_data = self.ui.move_unit_combobox.currentData()
            unit_id = move_unit_data[0] if isinstance(move_unit_data, (list, tuple)) else move_unit_data
            
            # Get material data
            material_id = self.ui.materials_combobox.currentData()
            if isinstance(material_id, (list, tuple)):
                material_id = material_id[0]
            
            input_invoice_id = self.database_operations.addInvoice(
                number=self.autoInvoiceNumber(),
                date=QDate.currentDate().toString('yyyy-MM-dd'),
                statement="material move",
                type_col=input_type_id[0]['id'],
                payment_method='cash',
                paid=1,
                invoice_currency=currency_id,
                invoice_warehouse=warehouse_id,
                cost_account=self.ui.from_account_warehouse_combobox.currentData(),
                commit=False
            )

            if input_invoice_id:
                invoice_item_id = self.database_operations.addInvoiceMaterial(
                    invoice_id=input_invoice_id,
                    material_id=material_id,
                    unit_price=unit_price,
                    equilivance_price=equilivance_price,
                    currency_id=currency_id,
                    warehouse_id=warehouse_id,
                    quantity1=self.ui.move_quantity_input.text(),
                    unit1_id=unit_id,
                    commit=False
                )

            return [input_invoice_id , invoice_item_id]


    def addOutputInvoice(self, currency_id, equilivance_price, unit_price, add_journal_entry, quantity):
        output_type_id = self.database_operations.fetchInvoiceTypes(name='output')
        if output_type_id:
            # Get warehouse and account data
            warehouse_data = self.ui.to_warehouse_combobox.currentData()
            warehouse_id = warehouse_data[0] if isinstance(warehouse_data, (list, tuple)) else warehouse_data
            
            # Get move unit data
            move_unit_data = self.ui.move_unit_combobox.currentData()
            unit_id = move_unit_data[0] if isinstance(move_unit_data, (list, tuple)) else move_unit_data
            
            # Get material data
            material_id = self.ui.materials_combobox.currentData()
            if isinstance(material_id, (list, tuple)):
                material_id = material_id[0]

            output_invoice_id = self.database_operations.addInvoice(
                number=self.autoInvoiceNumber(),
                date=QDate.currentDate().toString('yyyy-MM-dd'),
                statement="material move",
                type_col=output_type_id[0]['id'],
                payment_method='cash',
                paid=1,
                invoice_currency=currency_id,
                invoice_warehouse=warehouse_id,
                commit=False
            )

            if output_invoice_id:
                invoice_item_id = self.database_operations.addInvoiceMaterial(
                    invoice_id=output_invoice_id,
                    material_id=material_id,
                    quantity1=self.ui.move_quantity_input.text(),
                    unit1_id=unit_id,
                    unit_price=unit_price,
                    warehouse_id=warehouse_id,
                    equilivance_price=equilivance_price,
                    currency_id=currency_id,
                    commit=False
                )


    def save(self , window):
        quantity = self.ui.move_quantity_input.text()
        move_unit_data = self.ui.move_unit_combobox.currentData()
        if len(move_unit_data) > 0:
            move_unit, maximum_quantity, conversion_rates = move_unit_data

            # try:
            if 0 < float(quantity) <= float(maximum_quantity):

                from_warehouse = self.ui.from_warehouse_combobox.currentData()
                to_warehouse = self.ui.to_warehouse_combobox.currentData()
                to_account_warehouse = self.ui.to_account_warehouse_combobox.currentData()
                to_account_name_warehouse = self.ui.to_account_warehouse_combobox.currentText()
                from_account_warehouse = self.ui.from_account_warehouse_combobox.currentData()
                from_account_name_warehouse = self.ui.from_account_warehouse_combobox.currentText()
                material_data = self.ui.materials_combobox.currentData()
                warehouse_unit = self.ui.warehouse_unit_combobox.currentData()
                add_movement_entry = self.ui.add_movement_entry_checkbox.isChecked()
                add_journal_entry = self.ui.add_journal_entry_checkbox.isChecked()
                source_warehouse_unit_data = self.ui.warehouse_unit_combobox.currentData()
                origin_type_data = self.ui.journal_entry_origin_combobox.currentData()
                batch_number = ''
                batch_mfg = ''
                batch_exp = ''
                production_date = ''
                expire_date = ''

                # fetch warehouse entry unit
                warehouse_entry = self.database_operations.fetchWarehouseEntry(warehouse_entry_id=self.warehouse_entry, warehouse_id=self.source_warehouse)

                if add_journal_entry and self.ui.journal_entry_item_currency_combobox.isEnabled() and self.ui.journal_entry_item_value.isEnabled():
                    if len(origin_type_data)>0:
                        origin_type = origin_type_data[0]
                        if origin_type=='invoice':
                            origin_id = origin_type_data[1]
                        elif origin_type=='manufacture':
                            origin_id = origin_type_data[2]
                        else:
                            origin_id = ''

                    cost = self.ui.journal_entry_item_value.text()
                    currency = self.ui.journal_entry_item_currency_combobox.currentData()
                else:
                    cost = ''
                    currency = ''
                    origin_type=''
                    origin_id =''

                if warehouse_entry:
                    batch_number = warehouse_entry['batch_number']
                    batch_mfg = warehouse_entry['batch_mfg']
                    # batch_exp = warehouse_entry['batch_exp']
                    production_date = warehouse_entry['production_date']
                    expire_date = warehouse_entry['expire_date']
                    material_move_id = warehouse_entry['material_move_id']
                    invoice_item = ''

                    if material_move_id:
                        move_id = self.database_operations.fetchSingleMaterialMove(material_move_id)
                        invoice_item_id = move_id['origin_id']
                        if invoice_item_id:
                            invoice_item = self.database_operations.fetchInvoiceItem(invoice_item_id)

                unit_price = invoice_item['unit_price'] or ''
                currency_id = invoice_item['currency_id'] or ''
                equilivance_price = invoice_item['equilivance_price'] or ''

                if len(material_data) > 0:
                    material_id, source_production_batch_id, source_invoice_item_id, material_name = material_data
                    conversion_rate_to_source_warehouse_unit = conversion_rates[move_unit]
                    quantity_using_source_warehouse_unit = float(quantity) * conversion_rate_to_source_warehouse_unit

                    source_production_batch_id = source_production_batch_id or ''
                    origin_type = origin_type or ''
                    origin_id = origin_id or ''
                    to_account_warehouse = to_account_warehouse or ''
                    from_account_warehouse = from_account_warehouse or ''
                    to_account_name_warehouse = to_account_name_warehouse or ''
                    from_account_name_warehouse = from_account_name_warehouse or ''
                    cost = cost or ''
                    currency = currency or ''
                    batch_number = batch_number or ''
                    batch_mfg = batch_mfg or ''
                    batch_exp = batch_exp or ''
                    production_date = production_date or ''
                    expire_date = expire_date or ''
                    total_cost = float(quantity) * float(unit_price)
                    input_invoice_id , invoice_item_id = self.addInputInvoice(currency_id, equilivance_price, total_cost, add_journal_entry, quantity)
                    self.addOutputInvoice(currency_id, equilivance_price, total_cost, add_journal_entry, quantity)

                    material_move_id = self.database_operations.moveMaterial(
                        quantity=quantity, 
                        move_unit=move_unit, 
                        material_id=material_id,
                        from_warehouse=from_warehouse[0], 
                        to_warehouse=to_warehouse[0], 
                        material_name=material_name, 
                        from_warehouse_entry_id=self.warehouse_entry, 
                        to_warehouse_entry_id='',
                        quantity_using_source_warehouse_unit=quantity_using_source_warehouse_unit,
                        source_production_batch_id=source_production_batch_id, 
                        source_invoice_item_id=invoice_item_id,
                        source_warehouse_unit=warehouse_unit, 
                        cost=total_cost, 
                        currency=currency_id, 
                        origin_type=origin_type, 
                        origin_id=origin_id,
                        to_account_warehouse=to_account_warehouse, 
                        from_account_warehouse=from_account_warehouse, 
                        to_account_name_warehouse=to_account_name_warehouse,
                        from_account_name_warehouse=from_account_name_warehouse, 
                        record_move=add_movement_entry, 
                        record_journal_entry=add_journal_entry,
                        batch_number=batch_number,
                        batch_mfg=batch_mfg,
                        production_date=production_date,
                        expire_date=expire_date,
                        commit=False
                    )

                    to_warehouse_entry = self.database_operations.fetchWarehouseEntryByMaterialMoveId(material_move_id=material_move_id, warehouse_id=to_warehouse[0])

                    if to_warehouse_entry:
                        to_warehouse_entry_id = to_warehouse_entry['id']

                        self.database_operations.updateMaterialMove(material_move_id=material_move_id, to_warehouse_entry_id=to_warehouse_entry_id, commit=True)

                    window.accept()

            else:
                win32api.MessageBox(0, self.language_manager.translate("ALERT_QUANTITY_GREATER_THAN_WAREHOUSE"), self.language_manager.translate("ALERT"))

            # except Exception as e:
            #     print(e)
            #     win32api.MessageBox(0, "تأكد من القيم المدخلة", "خطأ")

