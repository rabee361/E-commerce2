import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_AddMaterialToWarehouse import Ui_AddMaterialToWarehouse
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QTranslator
from LanguageManager import LanguageManager

class Ui_AddMaterialToWarehouse_Logic(QDialog):
    def __init__(self, sql_connector, warehouse_id):
        super().__init__()
        self.warehouse_id = warehouse_id
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_AddMaterialToWarehouse()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        
    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.quantity_input.setValidator(QDoubleValidator())
        self.ui.expire_date_input.setDate(QDate.currentDate())
        self.ui.production_date_input.setDate(QDate.currentDate())
        self.fetchGroups()
        self.fetchCurrencies()
        self.fetchMaterials() #at first launch
        self.displayMaterialUnits() #at first launch
        self.ui.groups_combobox.setEnabled(False)
        self.ui.materials_combobox.setEnabled(False)
        self.ui.groups_combobox.currentIndexChanged.connect(lambda: self.fetchMaterials())
        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.displayMaterialUnits())
        self.ui.save_btn.clicked.connect(lambda: self.saveMaterial(window))
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_group_btn.clicked.connect(lambda: self.openSelectGroupWindow())   
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())   

    def openSelectGroupWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groups')
        result = data_picker.showUi()
        if result is not None:
            self.ui.groups_combobox.setCurrentIndex(self.ui.groups_combobox.findData(result['id']))

    def openSelectAccountWindow(self):
        invoice_type_name = "input_materials_account"
        default_account = self.database_operations.fetchSetting(invoice_type_name)
        if default_account:
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', default_id=int(default_account))
        else:
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.clear()
            self.ui.account_combobox.addItem(result['name'], result['id'])  # (name, id)
            self.ui.account_combobox.setCurrentIndex(0)

    def openSelectMaterialWindow(self):
        group_id = self.ui.groups_combobox.currentData()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials_of_group', group_materials_id=group_id)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.materials_combobox.count()):
                if self.ui.materials_combobox.itemData(i)[0] == result['id']:
                    self.ui.materials_combobox.setCurrentIndex(i)
                    break
                
    def fetchGroups(self):
        groups = self.database_operations.fetchGroups()
        for group in groups:
            id = group['id']
            name = group['name']
            code = group['code']
            display_text = str(code)+"-"+str(name)
            data = id
            self.ui.groups_combobox.addItem(display_text, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            display_text = str(name)
            data = id
            self.ui.currency_combobox.addItem(display_text, data)

    def fetchMaterials(self):
        self.ui.materials_combobox.clear()
        group_id = self.ui.groups_combobox.currentData()
        if group_id:
            materials = self.database_operations.fetchMaterialsOfGroup(group_id)
            for material in materials:
                id=material['id']
                code=material['code']
                name=material['name']
                display_text = str(code)+"-"+str(name)
                units=[]
                unit1 = material['unit1']
                unit1_name = material['unit1_name']
                unit2 = material['unit2']
                unit2_name = material['unit2_name']
                unit3 = material['unit3']
                unit3_name = material['unit3_name']
                units.append((unit1, unit1_name))
                units.append((unit2, unit2_name))
                units.append((unit3, unit3_name))
                data = [id, units]
                self.ui.materials_combobox.addItem(display_text, data)
                
    def displayMaterialUnits(self):
        try:
            units = self.ui.materials_combobox.currentData()[1]
            self.ui.unit_combobox.clear()
            for unit in units:
                # Only add unit if both the ID and name exist and are not None
                if unit and unit[0] and unit[1]:
                    self.ui.unit_combobox.addItem(str(unit[1]), str(unit[0]))
        except:
            # This may happen when changing to a group that doesn't have any materials
            self.ui.unit_combobox.clear()


    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        print(type(last_invoice_number))
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            return 1
        else:
            return int(last_invoice_number) + 1
        

    def addInputInvoice(self):
        input_type_id = self.database_operations.fetchInvoiceTypes(name='input')

        warehouse_data = self.database_operations.fetchWarehouse(id=self.warehouse_id)
        warehouse_id = warehouse_data['id']
        warehouse_name = warehouse_data['name']
        warehouse_account_id = warehouse_data['account']

        production_date = self.ui.production_date_input.date().toString('yyyy-MM-dd')
        expire_date = self.ui.expire_date_input.date().toString('yyyy-MM-dd')
        unit = self.ui.unit_combobox.currentData()
        quantity = self.ui.quantity_input.text()
        unit_price = self.ui.price_input.text() or ''
        currency_id = self.ui.currency_combobox.currentData()

        if input_type_id:
            # Get material data
            material_id = self.ui.materials_combobox.currentData()
            if isinstance(material_id, (list, tuple)):
                material_id = material_id[0]
            
            input_invoice_id = self.database_operations.addInvoice(
                number=self.autoInvoiceNumber(),
                date=QDate.currentDate().toString('yyyy-MM-dd'),
                statement="warehouse_entry",
                type_col=input_type_id[0]['id'],
                payment_method='cash',
                paid=1,
                invoice_currency=currency_id,
                invoice_warehouse=warehouse_id,
                commit=False
            )

            if input_invoice_id:
                invoice_item_id = self.database_operations.addInvoiceMaterial(
                    invoice_id=input_invoice_id,
                    material_id=material_id,
                    unit_price=unit_price,
                    equilivance_price=unit_price,
                    currency_id=currency_id,
                    quantity1=quantity,
                    unit1_id=unit,
                    warehouse_id=warehouse_id,
                    production_date=production_date,
                    expire_date=expire_date,
                    commit=False
                )

                return [input_invoice_id, invoice_item_id]

    def saveMaterial(self, window):
        material_data = self.ui.materials_combobox.currentData()
        production_date = self.ui.production_date_input.date().toString('yyyy-MM-dd')
        expire_date = self.ui.expire_date_input.date().toString('yyyy-MM-dd')
        from_account_warehouse = self.database_operations.fetchAccount(id=self.warehouse_id)
        currency_id = self.ui.currency_combobox.currentData()
        account_id = self.ui.account_combobox.currentData()
        
        if material_data is None:
            win32api.MessageBox(0, "يرجى اختيار مادة أولاً", "خطأ")
        else:
            material_id = material_data[0]
            quantity = self.ui.quantity_input.text()
            unit_price = self.ui.price_input.text() or ''
            if not quantity or not unit_price:
                win32api.MessageBox(0,"الكمية و السعر لا يمكن أن تكون فارغة","خطأ")
            else:
                unit = self.ui.unit_combobox.currentData()
                if str(unit).lower()=='none':
                    unit=''

                result = self.addInputInvoice()
                invoice_item_id = None
                if result:
                    invoice_item_id = result[1]

                if from_account_warehouse:
                    from_account_warehouse = from_account_warehouse['id']
                else:
                    from_account_warehouse = ''

                total_cost = float(quantity) * float(unit_price)

                material_move_id = self.database_operations.moveMaterial(material_id=material_id, quantity=quantity, move_unit=unit, from_warehouse='', from_account_warehouse=account_id, to_account_warehouse=from_account_warehouse, to_warehouse=self.warehouse_id, origin_type='invoice', origin_id=invoice_item_id, cost=total_cost, currency=currency_id, record_only=True, record_journal_entry=True)

                to_warehouse_entry_id = self.database_operations.addMaterialToWarehouse(material_id=material_id, quantity=quantity, unit=unit, warehouse_id=self.warehouse_id, material_move_id=material_move_id, production_date=production_date, expire_date=expire_date)
        
                self.database_operations.updateMaterialMove(material_move_id=material_move_id, to_warehouse_entry_id=to_warehouse_entry_id)

                window.accept()
