import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_RemoveMaterialFromWarehouse import Ui_RemoveMaterialFromWarehouse
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtCore import QDate
from PyQt5.QtCore import QTranslator
from LanguageManager import LanguageManager

class Ui_RemoveMaterialFromWarehouse_Logic(QDialog):
    def __init__(self, sql_connector, warehouse_entry_id, warehouse_id):
        super().__init__()
        self.warehouse_entry_id = warehouse_entry_id
        self.warehouse_id = warehouse_id
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_RemoveMaterialFromWarehouse()
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
        self.ui.price_input.setValidator(QDoubleValidator())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.save_btn.clicked.connect(lambda: self.outputMaterial(window))
        self.fetchCurrencies()
        self.fetchUnits()

    def openSelectAccountWindow(self):
        invoice_type_name = "output_materials_account"
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


    def setInputFields(self):
        self.ui.unit_combobox.setCurrentIndex(0)

    def fetchUnits(self):
        self.ui.unit_combobox.clear()
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.unit_combobox.addItem(display_text, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            self.ui.currency_combobox.setCurrentIndex(0)
            id = currency[0]
            name = currency[1]
            display_text = str(name)
            data = id
            self.ui.currency_combobox.addItem(display_text, data)


    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        print(type(last_invoice_number))
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            return 1
        else:
            return int(last_invoice_number) + 1
        

    def addOutputInvoice(self, material_id):
        output_type_id = self.database_operations.fetchInvoiceTypes(name='output')

        warehouse_data = self.database_operations.fetchWarehouse(id=self.warehouse_id)
        warehouse_id = warehouse_data['id']
        warehouse_name = warehouse_data['name']
        warehouse_account_id = warehouse_data['account']

        unit = self.ui.unit_combobox.currentData()
        quantity = self.ui.quantity_input.text()
        unit_price = self.ui.price_input.text()
        unit_price = unit_price if unit_price else ''
        currency_id = self.ui.currency_combobox.currentData()

        if output_type_id:
            output_invoice_id = self.database_operations.addInvoice(
                number=self.autoInvoiceNumber(),
                date=QDate.currentDate().toString('yyyy-MM-dd'),
                statement="warehouse_entry",
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
                    unit_price=unit_price,
                    equilivance_price=unit_price,
                    currency_id=currency_id,
                    quantity1=quantity,
                    unit1_id=unit,
                    warehouse_id=warehouse_id,
                    commit=False
                )

                # if invoice_item_id:
                #     entry_id = self.database_operations.addJournalEntry(
                #         entry_date=QDate.currentDate().toString('yyyy-MM-dd'),
                #         currency=currency_id,
                #         origin_type="invoice",
                #         origin_id=invoice_item_id,
                #         commit=False
                #     )
                #     if entry_id:
                #         self.database_operations.addJournalEntryItem(
                #             journal_entry_id=entry_id,
                #             currency=currency_id,
                #             type_col='creditor',
                #             account=warehouse_account_id,
                #             opposite_account=warehouse_account_id,
                #             statement="invoice",
                #             value=unit_price,
                #             commit=True
                #         )

                return [output_invoice_id, invoice_item_id]

    def outputMaterial(self, window):
        warehouse_entry = self.database_operations.fetchWarehouseEntry(warehouse_entry_id=self.warehouse_entry_id, warehouse_id=self.warehouse_id)
        if warehouse_entry:
            id = warehouse_entry['id']
            material_id = warehouse_entry['material_id']

            from_account_warehouse = self.database_operations.fetchAccount(id=self.warehouse_id)
            currency_id = self.ui.currency_combobox.currentData()
            account_id = self.ui.account_combobox.currentData()
            quantity = self.ui.quantity_input.text()
            unit_price = self.ui.price_input.text()
            unit_price = unit_price if unit_price else ''
            if not quantity or not unit_price or not account_id:
                win32api.MessageBox(0,self.language_manager.translate("ALL_FIELDS_MUST_BE_FILLED"),self.language_manager.translate("ERROR"))
                return
            
            unit = self.ui.unit_combobox.currentData()
            if str(unit).lower()=='none':
                unit=''

            result = self.addOutputInvoice(material_id)
            invoice_item_id = None
            if result:
                invoice_item_id = result[1]

            if from_account_warehouse:
                from_account_warehouse = from_account_warehouse['id']
            else:
                from_account_warehouse = ''

            total_cost = float(quantity) * float(unit_price)

            material_move_id = self.database_operations.moveMaterial(material_id=material_id, quantity=quantity, move_unit=unit, from_warehouse_entry_id=self.warehouse_entry_id , from_warehouse=self.warehouse_id, from_account_warehouse=from_account_warehouse, quantity_using_source_warehouse_unit=quantity , to_account_warehouse=account_id, to_warehouse='', origin_type='invoice', origin_id=invoice_item_id, cost=total_cost, currency=currency_id, record_only=False, record_journal_entry=True)

            window.accept()
