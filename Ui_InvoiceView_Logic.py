import math
import datetime
import win32api
import win32con
from PyQt5.QtCore import Qt, QDate, QTranslator
from PyQt5.QtGui import QBrush
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QSizePolicy
from PyQt5 import QtCore, QtGui, QtWidgets
from win32con import MB_YESNO, IDYES, IDNO
from PyQt5.QtGui import QDoubleValidator

from Colors import dark_green, light_red_color
from DatabaseOperations import DatabaseOperations
from Ui_InvoiceView import Ui_InvoiceView
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager


class Ui_InvoiceView_Logic(QDialog):
    def __init__(self, sql_connector, invoice_id=None, invoice_number=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_InvoiceView()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

        self.invoice_id = invoice_id
        self.invoice_number = invoice_number
        self.invoice_remaining_value = 0
        self.old_quantities = {}    # Save quantities before editing
        self.origin_invoice_data = {}

        # Payment currencies exchange rates
        self.payment_currencies_exchange_rates = {}

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        if self.invoice_id:
            window.setObjectName(f'InvoiceView_{self.invoice_number}')
            window.setWindowTitle(f'{self.language_manager.translate( "INVOICE_VIEW")} {self.invoice_number}')
        window.exec()

    def initialize(self, window):
        # self.ui.material_quantity_input.setValidator(QDoubleValidator())
        self.ui.material_discount_input.setValidator(QDoubleValidator())
        self.ui.material_gifts_input.setValidator(QDoubleValidator())
        self.ui.material_discount_percent_input.setValidator(QDoubleValidator())
        self.ui.material_unit_price_input.setValidator(QDoubleValidator())
        self.ui.material_addition_input.setValidator(QDoubleValidator())
        self.ui.material_added_value_input.setValidator(QDoubleValidator())
        self.ui.material_addition_percent_input.setValidator(QDoubleValidator())
        self.ui.material_added_value_input.setValidator(QDoubleValidator())
        self.ui.date_input.setDisplayFormat('dd-MM-yyyy')
        self.ui.production_date_input.setDisplayFormat('dd-MM-yyyy')
        self.ui.expire_date_input.setDisplayFormat('dd-MM-yyyy')
        self.ui.payment_exchange_date_input.setDisplayFormat('dd-MM-yyyy')
        self.ui.date_input.setDate(QDate.currentDate())
        self.ui.payment_exchange_date_input.setDate(QDate.currentDate())

        # self.fetchInvoices()
        self.fetchInvoiceTypes()
        self.fetchClients()
        self.fetchCurrencies()
        self.fetchMaterials()
        self.fetchAccounts()
        self.fetchCostCenters()
        self.fetchWarehouses()
        self.fetchPrices()
        self.fetchUnits()
        self.fetchOutputWays()

        self.setDefaults()
        self.setMaterialDefaults()

        # hide data columns in additions-discount table
        # self.ui.discounts_additions_table.hideColumn(0)
        # self.ui.discounts_additions_table.hideColumn(1)
        # self.ui.discounts_additions_table.hideColumn(3)
        # self.ui.discounts_additions_table.hideColumn(5)
        # self.ui.discounts_additions_table.hideColumn(7)
        # self.ui.discounts_additions_table.hideColumn(10)
        # self.ui.discounts_additions_table.hideColumn(12)

        # hide data columns in materials table
        # self.ui.materials_table.hideColumn(0)
        # self.ui.materials_table.hideColumn(1)
        # self.ui.materials_table.hideColumn(4)
        # self.ui.materials_table.hideColumn(7)
        # self.ui.materials_table.hideColumn(10)
        # self.ui.materials_table.hideColumn(12)
        # self.ui.materials_table.hideColumn(15)
        # self.ui.materials_table.hideColumn(18)
        # self.ui.materials_table.hideColumn(20)
        # self.ui.materials_table.hideColumn(29)
        # self.ui.materials_table.hideColumn(31)
        self.ui.materials_table.hideColumn(42)  # Output way

        # add values to payment method combobox and paid combobox
        self.ui.payment_method_combobox.clear()
        self.ui.payment_method_combobox.addItem(self.language_manager.translate( 'CASH'), 'cash')
        self.ui.payment_method_combobox.addItem(self.language_manager.translate( 'POSTPONED'), 'postponed')
        self.ui.discount_addition_type_combobox.addItem(self.language_manager.translate( 'DISCOUNT'), 'discount')
        self.ui.discount_addition_type_combobox.addItem(self.language_manager.translate( 'ADDITION'), 'addition')
        self.ui.discount_addition_currency_combobox.addItem('%', '%')
        self.ui.gifts_opposite_account_combobox.setEnabled(False)
        self.ui.added_value_account_combobox.setEnabled(False)
        self.ui.stock_account_combobox.setEnabled(False)
        self.ui.materials_account_combobox.setEnabled(False)
        self.ui.monetary_account_combobox.setEnabled(False)
        self.ui.cost_account_combobox.setEnabled(False)
        self.ui.gifts_account_combobox.setEnabled(False)
        self.ui.invoice_warehouse_combobox.setEnabled(False)
        self.ui.invoice_type_combobox.setEnabled(False)
        self.ui.clients_combobox.setEnabled(False)
        self.ui.invoice_cost_center_combobox.setEnabled(False)
        self.ui.client_account_combobox.setEnabled(False)
        self.ui.discount_addition_cost_center_combobox.setEnabled(False)
        self.ui.discount_addition_account_combobox.setEnabled(False)
        # self.ui.material_combobox.setEnabled(False)
        self.ui.material_discount_account_combobox.setEnabled(False)
        self.ui.material_addition_account_combobox.setEnabled(False)
        self.ui.material_warehouse_combobox.setEnabled(False)
        self.ui.client_extra_account_combobox.setEnabled(False)


        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_cost_account_btn.clicked.connect(lambda: self.openSelectCostAccountWindow())
        self.ui.select_gifts_account_btn.clicked.connect(lambda: self.openSelectGiftsAccountWindow())
        self.ui.select_added_value_account_btn.clicked.connect(lambda: self.openSelectAddedValueAccountWindow())
        self.ui.select_monetary_account_btn.clicked.connect(lambda: self.openSelectMonetaryAccountWindow())
        self.ui.select_materials_account_btn.clicked.connect(lambda: self.openSelectMaterialsAccountWindow())
        self.ui.select_stock_account_btn.clicked.connect(lambda: self.openSelectStockAccountWindow())
        self.ui.select_gifts_opposite_account_btn.clicked.connect(lambda: self.openSelectGiftsOppositeAccountWindow())
        self.ui.select_client_account_btn.clicked.connect(lambda: self.openSelectClientAccountWindow())
        self.ui.select_client_btn.clicked.connect(lambda: self.openSelectClientWindow())
        self.ui.select_invoice_type_btn.clicked.connect(lambda: self.openSelectInvoiceTypeWindow())
        self.ui.select_invoice_cost_center_btn.clicked.connect(lambda: self.openSelectInvoiceCostCenterWindow())
        self.ui.select_discount_addition_cost_center_btn.clicked.connect(lambda: self.openSelectDiscountAdditionCostCenterWindow())
        self.ui.select_material_warehouse_btn.clicked.connect(lambda: self.openSelectMaterialWarehouseWindow())
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())
        self.ui.select_material_discount_account_btn.clicked.connect(lambda: self.openSelectMaterialDiscountAccountWindow())
        self.ui.select_material_addition_account_btn.clicked.connect(lambda: self.openSelectMaterialAdditionAccountWindow())
        self.ui.select_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.select_client_extra_account_btn.clicked.connect(lambda: self.openSelectClientExtraAccountWindow())

        # triggers to fetch exchnage values
        self.ui.discount_addition_currency_combobox.currentIndexChanged.connect(
            lambda: self.fetchExchangeValues(self.ui.discount_addition_currency_combobox.currentData(),
                                             self.ui.invoice_currency_combobox.currentData(),
                                             self.ui.discount_addition_exchange_combobox)
        )
        self.ui.material_currency_combobox.currentIndexChanged.connect(
            lambda: self.fetchExchangeValues(self.ui.material_currency_combobox.currentData(),
                                             self.ui.invoice_currency_combobox.currentData(),
                                             self.ui.material_exchange_combobox))
        self.ui.invoice_currency_combobox.currentIndexChanged.connect(
            lambda: self.fetchExchangeValues(self.ui.discount_addition_currency_combobox.currentData(),
                                             self.ui.invoice_currency_combobox.currentData(),
                                             self.ui.discount_addition_exchange_combobox)
        )
        self.ui.invoice_currency_combobox.currentIndexChanged.connect(
            lambda: self.fetchExchangeValues(self.ui.material_currency_combobox.currentData(),
                                             self.ui.invoice_currency_combobox.currentData(),
                                             self.ui.material_exchange_combobox)
        )

        # triggers to fetch invoice's defaults
        self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.setDefaults())
        self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.setMaterialDefaults())
        self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.enableInputOutputInvoiceUiElements())
        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.setClientAccounts())
        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.setDefaults())
        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.setMaterialDefaults())
        # self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.updateDefaultMaterialPrice("invoice"))

        self.ui.material_combobox.currentIndexChanged.connect(lambda: self.setMaterialDefaults())
        self.ui.material_combobox.currentIndexChanged.connect(lambda: self.updateMaterialDefaultPrice())
        self.ui.material_default_price_type_combobox.currentIndexChanged.connect(
            lambda: self.updateMaterialDefaultPrice())

        # gifts discount
        self.ui.material_quantity_input.editingFinished.connect(lambda: self.updateDefaultGifts())
        self.ui.material_unit_price_input.editingFinished.connect(lambda: self.updateDefaultGifts())

        # discounts and additions
        self.ui.material_discount_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition("material_discount"))
        self.ui.material_discount_percent_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition("material_discount_percent"))
        self.ui.material_addition_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition("material_addition"))
        self.ui.material_addition_percent_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition("material_addition_percent"))
        self.ui.material_quantity_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition())
        self.ui.material_unit_price_input.editingFinished.connect(
            lambda: self.updateMaterialDiscountAndAddition())

        self.ui.invoice_discoun_addition_input.editingFinished.connect(lambda: self.updateInvoiceDiscountAndAddition())

        self.ui.discount_addition_currency_combobox.currentIndexChanged.connect(
            lambda: self.updateInvoiceDiscountAndAddition())
        self.ui.invoice_currency_combobox.currentIndexChanged.connect(lambda: self.updateInvoiceDiscountAndAddition())
        self.ui.material_exchange_combobox.currentIndexChanged.connect(lambda: self.updateMaterialEquilivancePrice())
        self.ui.material_unit_price_input.editingFinished.connect(lambda: self.updateMaterialEquilivancePrice())
        # buttons
        self.ui.add_invoice_discount_addition_btn.clicked.connect(lambda: self.addInvoiceDiscountAndAddition())
        self.ui.add_invoice_discount_addition_btn.clicked.connect(lambda: self.calculateInvoiceValues())
        self.ui.remove_invoice_discount_addition_btn.clicked.connect(lambda: self.removeInvoiceDiscountAndAddition())
        self.ui.remove_invoice_discount_addition_btn.clicked.connect(lambda: self.calculateInvoiceValues())

        self.ui.add_material_btn.clicked.connect(lambda: self.addInvoiceItem())
        self.ui.add_material_btn.clicked.connect(lambda: self.calculateInvoiceValues())
        self.ui.remove_material_btn.clicked.connect(lambda: self.removeInvoiceItem())
        self.ui.remove_material_btn.clicked.connect(lambda: self.calculateInvoiceValues())

        self.ui.select_origin_invoice_btn.clicked.connect(lambda: self.openSelectNormalInvoiceWindow())

        self.ui.material_unit_combobox.currentIndexChanged.connect(lambda: self.updateMaterialDefaultPrice())

        self.ui.material_currency_combobox.currentIndexChanged.connect(lambda: self.updateMaterialGiftsValue())
        self.ui.material_gifts_input.editingFinished.connect(lambda: self.updateMaterialGiftsValue())
        self.ui.material_unit_combobox.currentIndexChanged.connect(lambda: self.updateMaterialGiftsValue())

        # buttons
        self.ui.save_btn.clicked.connect(lambda: self.saveInvoice(window))
        # self.ui.material_unit_combobox.currentIndexChanged.connect(lambda: self.)
        # x = QtWidgets.QComboBox()
        # x.addItem("XX","xx")
        # self.ui.materials_table.setCellWidget(0, 2, x)

        if self.invoice_id:
            self.fetchInvoiceData()
            self.displayInvoiceStatus()
            self.ui.select_invoice_type_btn.setEnabled(False)
        else:
            # Set defaults for new invoice
            self.ui.date_input.setDate(QDate.currentDate())
            self.autoInvoiceNumber()

        self.ui.invoice_currency_combobox.currentIndexChanged.connect(
            lambda: self.updateMaterialRowValues(update_all=True)
        )
        # self.ui.materials_table.cellChanged.connect(lambda r, c: self.updateMaterialRowValues(r, c))
        self.ui.pay_from_client_account_btn.clicked.connect(lambda: self.payFromClientExtraAccount(window))

        self.ui.payment_currency_combobox.currentIndexChanged.connect(lambda: self.enablePaymentMethod())
        self.ui.payment_exchange_date_input.editingFinished.connect(lambda: self.enablePaymentMethod())
        self.ui.client_account_status_btn.clicked.connect(lambda: self.displayPaymentCurrenciesExchangeRates())
        self.ui.invoice_type_combobox.currentIndexChanged.connect(lambda: self.setMaterialWarehouseField())
        self.ui.pay_from_client_account_checkbox.stateChanged.connect(lambda: self.enablePaymentFields())

        self.setClientAccounts()
        self.setMaterialWarehouseField()
        self.enablePaymentMethod()

    def fetchInvoices(self):
        invoices = self.database_operations.fetchNormalInvoices()
        for invoice in invoices:
            self.ui.origin_invoice_combobox.addItem(str(invoice['id']), invoice['id'])

    def openSelectNormalInvoiceWindow(self):
        self.fetchInvoices()
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'normal_invoices')
        result = data_picker.showUi()
        if result is not None:
            self.ui.origin_invoice_combobox.setCurrentIndex(self.ui.origin_invoice_combobox.findData(result['id']))
            origin_invoice_id = self.ui.origin_invoice_combobox.currentData()
            invoice_data = self.database_operations.fetchInvoice(origin_invoice_id, items=True)
            if invoice_data:
                invoice = invoice_data['invoice']  # invoice is an object
                items = invoice_data['items']      # items is a list of objects

                self.origin_invoice_data = {}
                for item in items:
                    item_id = item['id']
                    self.origin_invoice_data[item_id] = {
                        'material_id': item['material_id'],
                        'quantity': item['quantity1'],
                        'unit': item['unit1_id']
                    }
        else:
            self.ui.origin_invoice_combobox.clear()
            self.origin_invoice_data.clear()


    def enableInputOutputInvoiceUiElements(self):
        invoice_type_category = self.ui.invoice_type_combobox.currentData()[1]
        if invoice_type_category == 'input':
            self.ui.output_way_combobox.setEnabled(False)
            self.ui.production_date_input.setEnabled(True)
            self.ui.expire_date_input.setEnabled(True)
        if invoice_type_category == 'output':
            self.ui.output_way_combobox.setEnabled(True)
            self.ui.production_date_input.setEnabled(False)
            self.ui.expire_date_input.setEnabled(False)

    def setMaterialWarehouseField(self):
        invoice_type_name = self.ui.invoice_type_combobox.currentText()
        invoice_effect_on_warehouse = self.database_operations.fetchSetting(f'{invoice_type_name}_affects_on_warehouse')
        if invoice_effect_on_warehouse == 'add':
            self.ui.material_warehouse_checkbox.setText(self.language_manager.translate( 'ADD_MATERIAL_TO_WAREHOUSE'))
        if invoice_effect_on_warehouse == 'reduce':
            self.ui.material_warehouse_checkbox.setText(self.language_manager.translate( 'REMOVE_MATERIAL_FROM_WAREHOUSE'))

    def displayPaymentCurrenciesExchangeRates(self):
        # Build message text showing exchange rates for each currency
        message_text = f"{self.language_manager.translate( 'EXCHANGE_RATES_FOR')} {self.ui.payment_currency_combobox.currentText()}\n\n"

        for currency_name, exchange_rate in self.payment_currencies_exchange_rates.items():
            message_text += f"{currency_name}: {exchange_rate}\n"

        # Display message box with exchange rates
        win32api.MessageBox(None, message_text, self.language_manager.translate( 'EXCHANGE_RATES'), win32con.MB_RTLREADING | win32con.MB_RIGHT)

    def fetchInvoiceTypes(self):
        invoices_types = self.database_operations.fetchInvoiceTypes()
        for invoice_type in invoices_types:
            id = invoice_type['id']
            name = invoice_type['name']
            type_col = invoice_type['type_col']
            self.ui.invoice_type_combobox.addItem(name, [id, type_col])

        self.enableInputOutputInvoiceUiElements()

    def enablePaymentFields(self):
        if self.ui.pay_from_client_account_checkbox.isChecked():
            self.ui.paying_amount_input.setEnabled(True)
            self.ui.pay_from_client_account_btn.setEnabled(True)
        else:
            self.ui.paying_amount_input.setEnabled(False)
            self.ui.pay_from_client_account_btn.setEnabled(False)

    def enablePaymentMethod(self):
        client_id = self.ui.clients_combobox.currentData()
        client_extra_account_id = self.ui.client_extra_account_combobox.currentData()
        payment_currency_id = self.ui.payment_currency_combobox.currentData()

        payment_method = self.ui.payment_method_combobox.currentData()
        if payment_method == 'cash':
            self.ui.groupBox_2.setEnabled(False)
            return

        exchange_date = self.ui.payment_exchange_date_input.text()

        # Check if exchange date is valid for all currencies client paid with
        exchange_date_is_valid = True

        # Fetch all currencies client paid with
        client_payments_currencies = self.database_operations.fetchClientPaymentCurrencies(client_id=client_id)
        for currency in client_payments_currencies:
            currency_id = currency['currency_id']
            currency_name = currency['currency_name']
            exchange_rate = None
            if payment_currency_id == currency_id:
                exchange_rate = 1
            else:
                exchange = self.database_operations.fetchExchangeValue(payment_currency_id, currency_id, date=exchange_date)
                if exchange:
                    exchange_rate = exchange[0][1]
            if exchange_rate:
                self.payment_currencies_exchange_rates[currency_name] = exchange_rate
            else:
                self.payment_currencies_exchange_rates[currency_name] = self.language_manager.translate( 'NONE')
                exchange_date_is_valid = False

        if exchange_date_is_valid:
            self.ui.client_account_status_btn.setText('✅')
            client_extra_account_value = self.database_operations.fetchAccountValue(client_extra_account_id, payment_currency_id, date=exchange_date, unify_currency=True)
            # client_extra_account_value = abs(client_extra_account_value)
            self.ui.client_account_value_input.setText(str(round(client_extra_account_value, 2)))
        else:
            self.ui.client_account_status_btn.setText('⚠️')
            self.ui.client_account_status_btn.setToolTip(self.language_manager.translate( 'EXCHANGE_RATES_NOT_FOUND'))

    def payFromClientExtraAccount(self, window):
        client_id = self.ui.clients_combobox.currentData()
        client_name = self.ui.clients_combobox.currentText()
        client_extra_account_id = self.ui.client_extra_account_combobox.currentData()
        client_extra_account_value = self.ui.client_account_value_input.text()

        if client_extra_account_value == '':
            win32api.MessageBox(None, self.language_manager.translate( 'NO_EXTRA_ACCOUNT_VALUE'), self.language_manager.translate( 'ALERT'), win32con.MB_OK | win32con.MB_ICONERROR)
            return
        else:
            client_extra_account_value = float(client_extra_account_value)

        invoice_currency_id = self.ui.invoice_currency_combobox.currentData()
        invoice_remaining_value = self.invoice_remaining_value

        payment_amount = float(self.ui.paying_amount_input.text())
        payment_currency_id = self.ui.payment_currency_combobox.currentData()

        exchange_rate = self.database_operations.fetchExchangeValue(payment_currency_id, invoice_currency_id)
        if exchange_rate:
            payment_amount = payment_amount * exchange_rate[0][1]
            client_extra_account_value = client_extra_account_value * exchange_rate[0][1]

        if payment_amount > invoice_remaining_value:
            win32api.MessageBox(None, self.language_manager.translate( 'PAYMENT_AMOUNT_GREATER_THAN_INVOICE_REMAINING_VALUE'), self.language_manager.translate( 'ALERT'), win32con.MB_OK | win32con.MB_ICONERROR)
            return

        if payment_amount > client_extra_account_value:
            win32api.MessageBox(None, self.language_manager.translate( 'PAYMENT_AMOUNT_GREATER_THAN_EXTRA_ACCOUNT_VALUE'), self.language_manager.translate( 'ALERT'), win32con.MB_OK | win32con.MB_ICONERROR)
            return

        monetary_account_id = self.ui.monetary_account_combobox.currentData()
        if monetary_account_id is None:
            win32api.MessageBox(None, self.language_manager.translate( 'NO_MONETARY_ACCOUNT'), self.language_manager.translate( 'ALERT'), win32con.MB_OK | win32con.MB_ICONERROR)
            return

        current_date = QDate.currentDate().toString(Qt.ISODate)

        # Add journal entry
        journal_entry_id = self.database_operations.addJournalEntry(current_date, invoice_currency_id, origin_type='invoice_payment', origin_id=self.invoice_id, commit=False)

        payment_statement = f"{self.language_manager.translate( 'PAYMENT_FROM_EXTRA_ACCOUNT')} {client_name} {self.language_manager.translate( 'FOR_INVOICE')} {self.invoice_number}"

        # Add journal entry item
        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency_id, 'creditor', payment_statement, client_extra_account_id, monetary_account_id, payment_amount, commit=True)

        if float(payment_amount) == float(self.invoice_remaining_value):
            self.database_operations.setInvoiceAsPaid(self.invoice_id)

        win32api.MessageBox(None, self.language_manager.translate( 'PAYMENT_SUCCESS'), self.language_manager.translate( 'ALERT'), win32con.MB_OK | win32con.MB_ICONINFORMATION)
        window.close()

    def setClientAccounts(self):
        client_id = self.ui.clients_combobox.currentData()
        client_data = self.database_operations.fetchClient(client_id)
        if client_data:
            client_account_id = client_data['client_account_id']
            client_extra_account_id = client_data['extra_account_id']
            self.ui.client_account_combobox.setCurrentIndex(self.ui.client_account_combobox.findData(client_account_id))
            self.ui.client_extra_account_combobox.setCurrentIndex(self.ui.client_extra_account_combobox.findData(client_extra_account_id))

    def displayInvoiceStatus(self):
        info_input = self.ui.invoice_info_input
        info_input.setText("")
        info_input.setStyleSheet("background-color:white;color:black;border: 1px solid #b3b3b3;")
        invoice_data = self.database_operations.fetchInvoicesValues(invoice_id=self.invoice_id)
        if invoice_data:
            invoice_value = invoice_data[0]['invoice_value']
            paid_ammount = invoice_data[0]['paid_ammount']
            paid = invoice_data[0]['paid']
            if paid == 1:   # Cash Payment
                paid_ammount = invoice_value
            info_text = str(paid_ammount) + "/" + str(invoice_value)
            info_input.setText(info_text)
            if float(paid_ammount) == float(invoice_value):
                info_input.setStyleSheet("background-color: darkgreen; color: white;")
                self.ui.invoice_status_input.setText(self.language_manager.translate( 'PAID'))
            elif float(paid_ammount) < float(invoice_value):
                info_input.setStyleSheet("background-color: red; color: white;")
                self.invoice_remaining_value = invoice_value - paid_ammount
                self.ui.invoice_status_input.setText(self.language_manager.translate( 'NEEDS_PAYMENT') + " " + str(self.invoice_remaining_value))
            elif float(paid_ammount) > float(invoice_value):  # TODO: this should never happen
                info_input.setStyleSheet("background-color:yellow;color:black;border: 1px solid #b3b3b3;")

    def openSelectClientExtraAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.client_extra_account_combobox.setCurrentIndex(self.ui.client_extra_account_combobox.findData(result['id']))

    def openSelectMaterialDiscountAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.material_discount_account_combobox.setCurrentIndex(self.ui.material_discount_account_combobox.findData(result['id']))

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            # Iterate through all items in the combobox
            for i in range(self.ui.invoice_warehouse_combobox.count()):
                warehouse_data = self.ui.invoice_warehouse_combobox.itemData(i)  # Get the stored data list

                # Check if the first element (id) matches the result's id
                if warehouse_data and warehouse_data[0] == result['id']:
                    self.ui.invoice_warehouse_combobox.setCurrentIndex(i)  # Set current index to matching item
                    return  # Exit once matching item is found

    def openSelectMaterialAdditionAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.material_addition_account_combobox.setCurrentIndex(self.ui.material_addition_account_combobox.findData(result['id']))

    def openSelectMaterialWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            # Iterate through all items in the combobox
            for i in range(self.ui.material_warehouse_combobox.count()):
                warehouse_data = self.ui.material_warehouse_combobox.itemData(i)  # Get the stored data list

                # Check if the first element (id) matches the result's id
                if warehouse_data and warehouse_data[0] == result['id']:
                    self.ui.material_warehouse_combobox.setCurrentIndex(i)  # Set current index to matching item
                    return  # Exit once matching item is found

    def openSelectMaterialWindow(self):
        invoice_type = self.database_operations.fetchInvoiceType(self.ui.invoice_type_combobox.currentData()[0])
        if invoice_type and invoice_type['returned'] != 1:
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials')
        else:
            # Get material IDs from the origin invoice data
            material_ids = []
            if hasattr(self, 'origin_invoice_data') and self.origin_invoice_data:
                # Extract material IDs from invoice items
                for item_id, item_data in self.origin_invoice_data.items():
                    if 'material_id' in item_data and item_data['material_id'] is not None:
                        material_ids.append(item_data['material_id'])
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'materials', only_include=material_ids)
 
        result = data_picker.showUi()
        if result is not None:
            # Iterate through all items in the combobox
            for i in range(self.ui.material_combobox.count()):
                material_data = self.ui.material_combobox.itemData(i)  # Get 
                if material_data and material_data.get('id') == result['id']:
                    self.ui.material_combobox.setCurrentIndex(i)  
                    return  

    def openSelectInvoiceTypeWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector,'invoice_types')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.invoice_type_combobox.count()):
                if self.ui.invoice_type_combobox.itemData(i)[0] == result['id']:
                    self.ui.invoice_type_combobox.setCurrentIndex(i)
                    break

    def openSelectGiftsAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.gifts_account_combobox.setCurrentIndex(self.ui.gifts_account_combobox.findData(result['id']))

    def openSelectStockAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True  )
        result = data_picker.showUi()
        if result is not None:
            self.ui.stock_account_combobox.setCurrentIndex(self.ui.stock_account_combobox.findData(result['id']))

    def openSelectGiftsOppositeAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.gifts_opposite_account_combobox.setCurrentIndex(self.ui.gifts_opposite_account_combobox.findData(result['id']))

    def openSelectAddedValueAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.added_value_account_combobox.setCurrentIndex(self.ui.added_value_account_combobox.findData(result['id']))

    def openSelectMonetaryAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', default_id=self.ui.monetary_account_combobox.currentData())
        result = data_picker.showUi()
        if result is not None:
            self.ui.monetary_account_combobox.setCurrentIndex(self.ui.monetary_account_combobox.findData(result['id']))

    def openSelectMaterialsAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.materials_account_combobox.setCurrentIndex(self.ui.materials_account_combobox.findData(result['id']))

    def openSelectCostAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.cost_account_combobox.setCurrentIndex(self.ui.cost_account_combobox.findData(result['id']))

    def openSelectInvoiceWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouseslist', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.invoice_warehouse_combobox.count()):
                if self.ui.invoice_warehouse_combobox.itemData(i)[0] == result['id']:
                    self.ui.invoice_warehouse_combobox.setCurrentIndex(i)
                    break

    def openSelectClientWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'clients', client_type='')
        result = data_picker.showUi()
        if result is not None:
            self.ui.clients_combobox.setCurrentIndex(self.ui.clients_combobox.findData(result['id']))

    def openSelectDiscountAdditionCostCenterWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            # Iterate through all items in the combobox
            for i in range(self.ui.discount_addition_cost_center_combobox.count()):
                cost_center_data = self.ui.discount_addition_cost_center_combobox.itemData(i)  # Get the stored data list

                # Check if the first element (id) matches the result's id
                if cost_center_data and cost_center_data[0] == result['id']:
                    self.ui.discount_addition_cost_center_combobox.setCurrentIndex(i)  # Set current index to matching item
                    return  # Exit once matching item is found

    def openSelectInvoiceCostCenterWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.invoice_cost_center_combobox.count()):
                if self.ui.invoice_cost_center_combobox.itemData(i)[0] == result['id']:
                    self.ui.invoice_cost_center_combobox.setCurrentIndex(i)
                    break

    def openSelectClientAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.client_account_combobox.setCurrentIndex(self.ui.client_account_combobox.findData(result['id']))

    def fetchClients(self):
        clients = self.database_operations.fetchClients()
        for client in clients:
            id = client[0]
            name = client[1]
            data = id
            self.ui.clients_combobox.addItem(name, data)

    def fetchCurrencies(self):
        self.ui.invoice_currency_combobox.clear()
        self.ui.material_currency_combobox.clear()
        self.ui.payment_currency_combobox.clear()
        self.ui.discount_addition_currency_combobox.clear()

        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            name = currencie[1]
            data = id
            self.ui.invoice_currency_combobox.addItem(name, data)
            self.ui.material_currency_combobox.addItem(name, data)
            self.ui.payment_currency_combobox.addItem(name, data)
            self.ui.discount_addition_currency_combobox.addItem(name, data)

    def fetchMaterials(self):
        materials = self.database_operations.fetchMaterials()
        self.ui.material_combobox.addItem(self.language_manager.translate( 'NONE'), {})
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
                "groupped": material[65],
                "material_discount_account": material['discount_account'],
                "material_addition_account": material['addition_account']
            }
            display_text = str(material_data['name']) + " (" + str(material_data['code']) + ")"
            self.ui.material_combobox.addItem(display_text, material_data)

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.discount_addition_account_combobox.setCurrentIndex(self.ui.discount_addition_account_combobox.findData(result['id']))

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        None_text = self.language_manager.translate( 'NONE')
        self.ui.client_account_combobox.addItem(None_text, None)
        self.ui.monetary_account_combobox.addItem(None_text, None)
        self.ui.gifts_account_combobox.addItem(None_text, None)
        self.ui.gifts_opposite_account_combobox.addItem(None_text, None)
        self.ui.materials_account_combobox.addItem(None_text, None)
        self.ui.discount_addition_account_combobox.addItem(None_text, None)
        self.ui.added_value_account_combobox.addItem(None_text, None)
        self.ui.cost_account_combobox.addItem(None_text, None)
        self.ui.stock_account_combobox.addItem(None_text, None)
        self.ui.material_discount_account_combobox.addItem(None_text, None)
        self.ui.material_addition_account_combobox.addItem(None_text, None)

        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.client_account_combobox.addItem(display_text, data)
            self.ui.monetary_account_combobox.addItem(display_text, data)
            self.ui.gifts_account_combobox.addItem(display_text, data)
            self.ui.gifts_opposite_account_combobox.addItem(display_text, data)
            self.ui.materials_account_combobox.addItem(display_text, data)
            self.ui.discount_addition_account_combobox.addItem(display_text, data)
            self.ui.added_value_account_combobox.addItem(display_text, data)
            self.ui.cost_account_combobox.addItem(display_text, data)
            self.ui.stock_account_combobox.addItem(display_text, data)
            self.ui.material_discount_account_combobox.addItem(display_text, data)
            self.ui.material_addition_account_combobox.addItem(display_text, data)
            self.ui.client_extra_account_combobox.addItem(display_text, data)

    def fetchCostCenters(self):

        self.ui.invoice_cost_center_combobox.clear()
        self.ui.discount_addition_cost_center_combobox.clear()

        None_text = self.language_manager.translate( 'NONE')
        self.ui.discount_addition_cost_center_combobox.addItem(None_text, [None, None])
        self.ui.invoice_cost_center_combobox.addItem(None_text, [None, None])

        cost_centers = self.database_operations.fetchCostCenters(
            ['normal', 'distributor'])  # arabic should be removed after translation is done
        for cost_center in cost_centers:
            # notes = cost_centers[2]
            # Ascending = cost_centers[4]
            # parent = cost_centers[5]
            # changable_division_factors = cost_centers[6]
            # date = cost_centers[7]
            id = cost_center[0]
            name = cost_center[1]
            cost_center_type = cost_center[3]
            data = [id, cost_center_type]
            self.ui.discount_addition_cost_center_combobox.addItem(name, data)
            self.ui.invoice_cost_center_combobox.addItem(name, data)

    def fetchWarehouses(self):
        self.ui.invoice_warehouse_combobox.clear()
        self.ui.material_warehouse_combobox.clear()
        None_text = self.language_manager.translate( 'NONE')
        self.ui.invoice_warehouse_combobox.addItem(None_text, [None, None])
        self.ui.material_warehouse_combobox.addItem(None_text, [None, None])

        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            id = warehouse[0]
            display_text = warehouse[1]
            account_id = warehouse[5]
            data = [id, account_id]
            self.ui.invoice_warehouse_combobox.addItem(display_text, data)
            self.ui.material_warehouse_combobox.addItem(display_text, data)

    def fetchExchangeValues(self, currency_1, currency_2, target_ui_element):
        target_ui_element.clear()
        if currency_1 is None or currency_2 is None:
            return
        elif currency_1 == currency_2:
            text_to_display = "1"
            data = [None, 1]
            target_ui_element.clear()
            target_ui_element.addItem(text_to_display, data)
            return
        elif currency_1 == '%' or currency_2 == '%':  # when the use want to use percent value on invoice's currency
            return

        exchange_values = self.database_operations.fetchExchangeValue(currency_1, currency_2)
        if exchange_values is None:
            return

        for id, exchange_value, date in exchange_values:
            text_to_display = f"{exchange_value} ({self.language_manager.translate( 'AT_DATE')} {date})"
            data = [id, exchange_value]
            target_ui_element.addItem(text_to_display, data)

    def fetchPrices(self):
        prices = self.database_operations.fetchPrices()
        for price in prices:
            id = price[0]
            display_text = price[1]
            data = [id, None, None, None, None, None, None, None, None,
                    None]  # the data list holds the ID of the price type, and values of the three units prices and currencies (which are fetched in setMaterialDefaults())
            self.ui.material_default_price_type_combobox.addItem(display_text, data)

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.material_unit_combobox.addItem(display_text, data)

    def fetchOutputWays(self):
        output_ways = [
            {"text": self.language_manager.translate( 'FIFO'), "data": "FIFO"},
            {"text": self.language_manager.translate( 'LIFO'), "data": "LIFO"},
            {"text": self.language_manager.translate( 'EXPIRE_DATE_ASC'), "data": "expire_date_asc"},
            {"text": self.language_manager.translate( 'EXPIRE_DATE_DESC'), "data": "expire_date_desc"},
            {"text": self.language_manager.translate( 'PRODUCTION_DATE_ASC'), "data": "production_date_desc"},
            {"text": self.language_manager.translate( 'PRODUCTION_DATE_DESC'), "data": "production_date_asc"}
        ]
        for output_way in output_ways:
            self.ui.output_way_combobox.addItem(output_way["text"], output_way["data"])

    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            self.ui.number_input.setText("1")
        else:
            self.ui.number_input.setText(str(int(last_invoice_number) + 1))

    def fetchInvoiceTypeDefaultSettings(self):
        prefix = self.ui.invoice_type_combobox.currentText()
        default_settings = {}
        for suffix in ['added_value_account', 'gifts_opposite_account', 'monetary_account', 'gifts_account',
                       'cost_account', 'discounts_account', 'materials_account', 'stock_account', 'addition_account', 'items_additions_account', 'items_discounts_account',
                       'invoice_price', 'cost_price', 'gift_price', 'warehouse', 'cost_center', 'currency']:
            setting = f"{prefix}_{suffix}"
            value = self.database_operations.fetchSetting(setting)
            default_settings[suffix] = value

        # print(default_settings)
        return default_settings

    def fetchInvoiceData(self):
        if not self.invoice_id:
            return

        # Fetch invoice data with its items
        invoice_data = self.database_operations.fetchInvoice(self.invoice_id, items=True)
        if not invoice_data:
            return

        invoice = invoice_data['invoice']
        items = invoice_data['items']

        # Set invoice header data
        # Find and set index of matching invoice type
        for i in range(self.ui.invoice_type_combobox.count()):
            if self.ui.invoice_type_combobox.itemData(i)[0] == invoice['type_col']:
                self.ui.invoice_type_combobox.setCurrentIndex(i)
                break

        self.ui.number_input.setText(str(invoice['number']))
        self.ui.date_input.setDate(QDate.fromString(str(invoice['date_col']), 'yyyy-MM-dd'))
        self.ui.clients_combobox.setCurrentIndex(self.ui.clients_combobox.findData(invoice['client']))
        self.ui.client_account_combobox.setCurrentIndex(self.ui.client_account_combobox.findData(invoice['client_account']))
        self.ui.invoice_currency_combobox.setCurrentIndex(self.ui.invoice_currency_combobox.findData(invoice['currency']))
        self.ui.payment_method_combobox.setCurrentText(self.language_manager.translate( 'CASH') if invoice['payment'] == 'cash' else self.language_manager.translate( 'POSTPONED'))
        self.ui.statement_input.setText(invoice['statement_col'])
        for i in range(self.ui.invoice_cost_center_combobox.count()):
            if self.ui.invoice_cost_center_combobox.itemData(i)[0] == invoice['cost_center']:
                self.ui.invoice_cost_center_combobox.setCurrentIndex(i)
                break

        # Fetch and load invoice discounts/additions
        discounts_additions = self.database_operations.fetchInvoiceDiscountsAdditions(self.invoice_id)
        self.ui.discounts_additions_table.setRowCount(0)  # Clear existing rows
        for disc_add in discounts_additions:
            row = self.ui.discounts_additions_table.rowCount()
            self.ui.discounts_additions_table.insertRow(row)

            # Create table items
            id_item = QTableWidgetItem(str(disc_add['id']))
            account_id = QTableWidgetItem(str(disc_add['account']))
            account_name = QTableWidgetItem(disc_add['account_name'])
            type_id = QTableWidgetItem(disc_add['type_col'])
            type_name = QTableWidgetItem(self.language_manager.translate( 'DISCOUNT') if disc_add['type_col'] == 'discount' else self.language_manager.translate( 'ADDITION'))
            currency_id = QTableWidgetItem(str(disc_add['currency']))
            currency_name = QTableWidgetItem(disc_add['currency_name'])
            exchange = QTableWidgetItem(str(disc_add['exchange']))
            exchange_price = QTableWidgetItem(str(disc_add['exchange_price']))
            equilivance = QTableWidgetItem(str(disc_add['equilivance']))
            cost_center = QTableWidgetItem(str(disc_add['cost_center']))
            cost_center_name = QTableWidgetItem(disc_add['cost_center_name'])
            opposite_account = QTableWidgetItem(str(disc_add['opposite_account']))
            opposite_account_name = QTableWidgetItem(disc_add['opposite_account_name'])

            # Set items in table
            self.ui.discounts_additions_table.setItem(row, 0, id_item)        # Hidden column
            self.ui.discounts_additions_table.setItem(row, 1, account_id)     # Hidden column
            self.ui.discounts_additions_table.setItem(row, 2, account_name)
            self.ui.discounts_additions_table.setItem(row, 3, type_id)        # Hidden column
            self.ui.discounts_additions_table.setItem(row, 4, type_name)

            if str(disc_add['percent']) == '1':
                self.ui.discounts_additions_table.setItem(row, 5, QTableWidgetItem('%'))
                self.ui.discounts_additions_table.setItem(row, 6, QTableWidgetItem('%'))
            else:
                self.ui.discounts_additions_table.setItem(row, 5, currency_id)
                self.ui.discounts_additions_table.setItem(row, 6, currency_name)

            self.ui.discounts_additions_table.setItem(row, 7, exchange)
            self.ui.discounts_additions_table.setItem(row, 8, exchange_price)
            self.ui.discounts_additions_table.setItem(row, 9, equilivance)
            self.ui.discounts_additions_table.setItem(row, 10, cost_center)
            self.ui.discounts_additions_table.setItem(row, 11, cost_center_name)
            self.ui.discounts_additions_table.setItem(row, 12, opposite_account)
            self.ui.discounts_additions_table.setItem(row, 13, opposite_account_name)


        # Fetch invoice accounts and warehouses
        # Set warehouse combobox to invoice's warehouse
        for i in range(self.ui.invoice_warehouse_combobox.count()):
            if self.ui.invoice_warehouse_combobox.itemData(i)[0] == invoice['warehouse']:
                self.ui.invoice_warehouse_combobox.setCurrentIndex(i)
                break
        self.ui.cost_account_combobox.setCurrentIndex(self.ui.cost_account_combobox.findData(invoice['cost_account']))
        self.ui.gifts_account_combobox.setCurrentIndex(self.ui.gifts_account_combobox.findData(invoice['gifts_account']))
        self.ui.added_value_account_combobox.setCurrentIndex(self.ui.added_value_account_combobox.findData(invoice['added_value_account']))
        self.ui.monetary_account_combobox.setCurrentIndex(self.ui.monetary_account_combobox.findData(invoice['monetary_account']))
        self.ui.materials_account_combobox.setCurrentIndex(self.ui.materials_account_combobox.findData(invoice['materials_account']))
        self.ui.stock_account_combobox.setCurrentIndex(self.ui.stock_account_combobox.findData(invoice['stock_account']))
        self.ui.gifts_opposite_account_combobox.setCurrentIndex(self.ui.gifts_opposite_account_combobox.findData(invoice['gifts_opposite_account']))

        # Load invoice items directly into materials table
        self.ui.materials_table.setRowCount(0)  # Clear existing rows
        for item in items:
            row = self.ui.materials_table.rowCount()
            self.ui.materials_table.insertRow(row)

            # Set items in table following same pattern as AddNewInvoice
            # Create checkbox for row selection
            checkbox = QtWidgets.QCheckBox()
            checkbox_item = QTableWidgetItem()
            self.ui.materials_table.setItem(row, 0, checkbox_item)
            self.ui.materials_table.setCellWidget(row, 0, checkbox)
            id_item = QTableWidgetItem(str(item['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.ui.materials_table.setItem(row, 0, id_item)
            self.ui.materials_table.setItem(row, 1, QTableWidgetItem(str(item['material_id'])))
            self.ui.materials_table.setItem(row, 2, QTableWidgetItem(str(item['material_name'])))
            self.ui.materials_table.setItem(row, 3, QTableWidgetItem(str(item['quantity1'])))
            self.ui.materials_table.setItem(row, 4, QTableWidgetItem(str(item['unit1_id'])))
            self.ui.materials_table.setItem(row, 5, QTableWidgetItem(str(item['unit1_name'])))
            self.ui.materials_table.setItem(row, 6, QTableWidgetItem(str(item['quantity2'])))
            self.ui.materials_table.setItem(row, 7, QTableWidgetItem(str(item['unit2_id'])))
            self.ui.materials_table.setItem(row, 8, QTableWidgetItem(str(item['unit2_name'])))
            self.ui.materials_table.setItem(row, 9, QTableWidgetItem(str(item['quantity3'])))
            self.ui.materials_table.setItem(row, 10, QTableWidgetItem(str(item['unit3_id'])))
            self.ui.materials_table.setItem(row, 11, QTableWidgetItem(str(item['unit3_name'])))
            self.ui.materials_table.setItem(row, 12, QTableWidgetItem(str(item['price_type_id'])))

            # Create combobox for price type
            price_type_combobox = QtWidgets.QComboBox()
            # Copy items from material_default_price_type_combobox
            for i in range(self.ui.material_default_price_type_combobox.count()):
                price_type_combobox.addItem(
                    self.ui.material_default_price_type_combobox.itemText(i),
                    self.ui.material_default_price_type_combobox.itemData(i)
                )
            # Set current item to match the invoice item's price type
            price_type_combobox.setCurrentText(item['price_type_name'])
            price_type_combobox.currentIndexChanged.connect(
                lambda checked, r=row: self.updateMaterialRowValues(r, 13)
            )
            self.ui.materials_table.setCellWidget(row, 13, price_type_combobox)

            self.ui.materials_table.setItem(row, 14, QTableWidgetItem(str(item['unit_price'])))
            self.ui.materials_table.setItem(row, 15, QTableWidgetItem(str(item['currency_id'])))

            # Create combobox for currency
            currency_combobox = QtWidgets.QComboBox()
            # Copy items from material_currency_combobox
            for i in range(self.ui.material_currency_combobox.count()):
                currency_combobox.addItem(
                    self.ui.material_currency_combobox.itemText(i),
                    self.ui.material_currency_combobox.itemData(i)
                )
            # Set current item to match the invoice item's currency
            currency_combobox.setCurrentIndex(currency_combobox.findData(item['currency_id']))
            # Connect currency combobox change to update function
            currency_combobox.currentIndexChanged.connect(
                lambda checked, r=row: self.updateMaterialRowValues(r, 16)
            )
            self.ui.materials_table.setCellWidget(row, 16, currency_combobox)

            self.ui.materials_table.setItem(row, 17, QTableWidgetItem(str(item['equilivance_price'])))
            self.ui.materials_table.setItem(row, 18, QTableWidgetItem(str(invoice['currency'])))
            self.ui.materials_table.setItem(row, 19, QTableWidgetItem(str(invoice['currency_name'])))
            self.ui.materials_table.setItem(row, 20, QTableWidgetItem(str(item['exchange_id'])))
            self.ui.materials_table.setItem(row, 21, QTableWidgetItem(str(item['exchange_price'])))
            self.ui.materials_table.setItem(row, 22, QTableWidgetItem(str(item['discount'] if item['discount'] is not None else 0.0)))
            self.ui.materials_table.setItem(row, 23, QTableWidgetItem(str(item['discount_percent'] if item['discount_percent'] is not None else 0.0)))
            self.ui.materials_table.setItem(row, 24, QTableWidgetItem(str(item['item_discount_account'])))
            self.ui.materials_table.setItem(row, 25, QTableWidgetItem(str(item['discount_account_name'])))
            self.ui.materials_table.setItem(row, 26, QTableWidgetItem(str(item['addition'])))
            self.ui.materials_table.setItem(row, 27, QTableWidgetItem(str(item['addition_percent'])))
            self.ui.materials_table.setItem(row, 28, QTableWidgetItem(str(item['item_addition_account'])))
            self.ui.materials_table.setItem(row, 29, QTableWidgetItem(str(item['addition_account_name'])))
            self.ui.materials_table.setItem(row, 30, QTableWidgetItem(str(item['added_value'])))
            self.ui.materials_table.setItem(row, 31, QTableWidgetItem(str(item['gifts'])))
            self.ui.materials_table.setItem(row, 32, QTableWidgetItem(str(item['gifts_value'])))
            self.ui.materials_table.setItem(row, 33, QTableWidgetItem(str(item['gifts_discount'])))
            self.ui.materials_table.setItem(row, 34, QTableWidgetItem(str(item['warehouse_id'])))
            self.ui.materials_table.setItem(row, 35, QTableWidgetItem(str(item['warehouse_name'])))
            self.ui.materials_table.setItem(row, 36, QTableWidgetItem(str(item['cost_center_id'])))
            self.ui.materials_table.setItem(row, 37, QTableWidgetItem(str(item['cost_center_name'])))
            self.ui.materials_table.setItem(row, 38, QTableWidgetItem(str(item['notes'])))
            self.ui.materials_table.setItem(row, 39, QTableWidgetItem(str(item['warehouse_account'])))
            self.ui.materials_table.setItem(row, 40, QTableWidgetItem(str(item['production_date'])))
            self.ui.materials_table.setItem(row, 41, QTableWidgetItem(str(item['expire_date'])))

            self.old_quantities[int(item['id'])] = float(item['quantity1'])

        # Update all calculations
        # self.calculateInvoiceValues()

        # Disable fields that shouldn't change after items are added
        # self.ui.invoice_currency_combobox.setEnabled(False)
        # self.ui.invoice_type_combobox.setEnabled(False)

    def updateMaterialRowValues(self, row=None, column=None, update_all=False):
        self.ui.materials_table.blockSignals(True)

        try:
            if update_all: # Update all rows
                if self.ui.materials_table.rowCount() > 0:
                    rows_to_update = range(self.ui.materials_table.rowCount())
                    invoice_currency = self.ui.invoice_currency_combobox.currentData()
                    if invoice_currency:
                        win32api.MessageBox(None, self.language_manager.translate('ALL_FIELDS_WILL_BE_AFFECTED'), self.language_manager.translate('ALERT'))
                    else:
                        win32api.MessageBox(None, self.language_manager.translate('CURRENCY_MUST_BE_SELECTED'), self.language_manager.translate('ERROR'))
                        return
                else:
                    return
            else:
                # Get values from the row
                quantity = float(self.ui.materials_table.item(row, 3).text()) if self.ui.materials_table.item(row, 3) and self.ui.materials_table.item(row, 3).text() != 'None' else 0
                unit_price = float(self.ui.materials_table.item(row, 14).text()) if self.ui.materials_table.item(row, 14) and self.ui.materials_table.item(row, 14).text() != 'None' else 0
                rows_to_update = [row]

            if column == 30: # Added value changed, no need to update other cells
                return

            if column == 3 or column == 14:    # Unit price or quantity changed

                # Only proceed if quantity changed (column 3)
                if column == 3:
                    # Check if unit2 exists by checking unit2_id cell (column 7)
                    unit1_id = self.ui.materials_table.item(row, 4).text()
                    unit2_id = self.ui.materials_table.item(row, 7)
                    if unit2_id and unit2_id.text() != 'None':
                        # Get conversion rate between unit1 and unit2
                        unit2_id = self.ui.materials_table.item(row, 7).text()
                        unit2_conversion = float(self.database_operations.fetchUnitConversionValueBetween(unit1_id, unit2_id)) if unit1_id and unit2_id else 0
                        # Calculate and update unit2 quantity
                        if unit2_conversion:
                            unit2_qty = quantity * unit2_conversion
                            self.ui.materials_table.setItem(row, 6, QTableWidgetItem(str(unit2_qty)))

                    # Check if unit3 exists by checking unit3_id cell (column 10)
                    unit3_id = self.ui.materials_table.item(row, 10)
                    if unit3_id and unit3_id.text() != 'None':
                        # Get conversion rate between unit1 and unit3
                        unit3_id = self.ui.materials_table.item(row, 10).text()
                        unit3_conversion = float(self.database_operations.fetchUnitConversionValueBetween(unit1_id, unit3_id)) if unit1_id and unit3_id else 0
                        # Calculate and update unit3 quantity
                        if unit3_conversion:
                            unit3_qty = quantity * unit3_conversion
                            self.ui.materials_table.setItem(row, 9, QTableWidgetItem(str(unit3_qty)))

                # Get gifts and gifts_for values from material data
                material_id = self.ui.materials_table.item(row, 1).text()
                material_data = self.database_operations.fetchMaterial(material_id)

                if material_data:
                    gifts = float(material_data['gift']) if material_data['gift'] is not None and material_data['gift'] != 0 else 0
                    gifts_for = float(material_data['gift_for']) if material_data['gift_for'] is not None else 0

                    if gifts and gifts_for and quantity >= gifts:
                        if quantity % gifts_for == 0:
                            gifts_value = (quantity / gifts_for) * gifts
                            self.ui.materials_table.setItem(row, 31, QTableWidgetItem(str(gifts_value)))
                        message_text = self.language_manager.translate('GIFTS_AND_GIFTS_FOR_MUST_BE_RESETTED')
                        win32api.MessageBox(None, message_text, self.language_manager.translate('ALERT'))
                        self.ui.materials_table.setItem(row, 31, QTableWidgetItem('0'))
                        self.ui.materials_table.setItem(row, 33, QTableWidgetItem('0'))
                    else:
                        self.ui.materials_table.setItem(row, 31, QTableWidgetItem('0'))
                        self.ui.materials_table.setItem(row, 32, QTableWidgetItem('0'))
                        self.ui.materials_table.setItem(row, 33, QTableWidgetItem('0'))

            if column == 13:    # Price type changed
                # Get price type from combobox
                price_type_combobox = self.ui.materials_table.cellWidget(row, 13)
                price_type_id = price_type_combobox.currentData()[0]

                # Update price type id in cell 12
                self.ui.materials_table.setItem(row, 12, QTableWidgetItem(str(price_type_id)))
                return  # No need to update other cells

            if column == 16:    # Currency changed
                # Get currency from combobox
                currency_combobox = self.ui.materials_table.cellWidget(row, 16)
                currency_id = currency_combobox.currentData()

                # Update currency id in cell 15
                self.ui.materials_table.setItem(row, 15, QTableWidgetItem(str(currency_id)))

            if column == 22:  # Discount value changed
                if unit_price and quantity:
                    total_price = unit_price * quantity
                    discount = float(self.ui.materials_table.item(row, 22).text()) if self.ui.materials_table.item(row, 22).text() not in ['None', ''] else 0
                    if discount:
                            discount_percent = round(discount * 100 / total_price, 3)
                            self.ui.materials_table.setItem(row, 23, QTableWidgetItem(str(discount_percent)))
                    else:
                        self.ui.materials_table.setItem(row, 23, QTableWidgetItem('0'))

            if column == 23:  # Discount percent changed
                if unit_price and quantity:
                    total_price = unit_price * quantity
                    discount_percent = float(self.ui.materials_table.item(row, 23).text()) if self.ui.materials_table.item(row, 23).text() != 'None' else 0
                    if discount_percent:
                            discount = round(discount_percent * total_price / 100, 3)
                            self.ui.materials_table.setItem(row, 22, QTableWidgetItem(str(discount)))
                    else:
                        self.ui.materials_table.setItem(row, 22, QTableWidgetItem('0'))

            if column == 26:  # Addition value changed
                if unit_price and quantity:
                    total_price = unit_price * quantity
                    addition = float(self.ui.materials_table.item(row, 26).text()) if self.ui.materials_table.item(row, 26).text() != 'None' else 0
                    if addition:
                            addition_percent = round(addition * 100 / total_price, 3)
                            self.ui.materials_table.setItem(row, 27, QTableWidgetItem(str(addition_percent)))
                    else:
                        self.ui.materials_table.setItem(row, 27, QTableWidgetItem('0'))

            if column == 27:  # Addition percent changed
                if unit_price and quantity:
                    total_price = unit_price * quantity
                    addition_percent = float(self.ui.materials_table.item(row, 27).text()) if self.ui.materials_table.item(row, 27).text() not in ['None', ''] else 0
                    if addition_percent:
                            addition = round(addition_percent * total_price / 100, 3)
                            self.ui.materials_table.setItem(row, 26, QTableWidgetItem(str(addition)))
                    else:
                        self.ui.materials_table.setItem(row, 26, QTableWidgetItem('0'))

            for row in rows_to_update:
                # Get values from the row
                quantity = float(self.ui.materials_table.item(row, 3).text()) if self.ui.materials_table.item(row, 3) and self.ui.materials_table.item(row, 3).text() != 'None' else 0
                unit_price = float(self.ui.materials_table.item(row, 14).text()) if self.ui.materials_table.item(row, 14) and self.ui.materials_table.item(row, 14).text() != 'None' else 0

                # Get currency data
                currency_combobox = self.ui.materials_table.cellWidget(row, 16)
                material_currency = currency_combobox.currentData() if currency_combobox else None
                invoice_currency = self.ui.invoice_currency_combobox.currentData()

                # Get exchange rate if currencies differ
                exchange_value = 1
                exchange_id = None
                if material_currency and invoice_currency and material_currency != invoice_currency:
                    exchange_values = self.database_operations.fetchExchangeValue(material_currency, invoice_currency)
                    if exchange_values and len(exchange_values) > 0:
                        exchange_id = exchange_values[0][0]
                        exchange_value = float(exchange_values[0][1])

                # Calculate equilivance price
                equilivance_price = unit_price * exchange_value if unit_price else 0

                # Update row values
                self.ui.materials_table.setItem(row, 17, QTableWidgetItem(str(equilivance_price)))
                self.ui.materials_table.setItem(row, 20, QTableWidgetItem(str(exchange_id)))
                self.ui.materials_table.setItem(row, 21, QTableWidgetItem(str(exchange_value)))

                # Calculate discount value
                discount_percent = float(self.ui.materials_table.item(row, 23).text()) if self.ui.materials_table.item(row, 23) and self.ui.materials_table.item(row, 23).text() not in ['None', ''] else 0
                discount = (quantity * equilivance_price * discount_percent / 100) if discount_percent else 0
                self.ui.materials_table.setItem(row, 22, QTableWidgetItem(str(discount)))

                # Calculate addition value
                addition_percent = float(self.ui.materials_table.item(row, 27).text()) if self.ui.materials_table.item(row, 27) and self.ui.materials_table.item(row, 27).text() not in ['None', ''] else 0
                addition = (quantity * equilivance_price * addition_percent / 100) if addition_percent else 0
                self.ui.materials_table.setItem(row, 26, QTableWidgetItem(str(addition)))

            # Recalculate invoice totals
            self.calculateInvoiceValues()

        finally:
            self.ui.materials_table.blockSignals(False)

    def setDefaults(self):
        default_settings = self.fetchInvoiceTypeDefaultSettings()

        # currency
        default_currency = default_settings['currency']
        self.ui.invoice_currency_combobox.setCurrentIndex(self.ui.invoice_currency_combobox.findData(default_currency))

        # cost center
        default_cost_center = default_settings['cost_center']
        self.ui.invoice_cost_center_combobox.setCurrentIndex(
            self.ui.invoice_cost_center_combobox.findData(default_cost_center))

        # warehouse
        default_warehouse = default_settings['warehouse']
        for index in range(self.ui.invoice_warehouse_combobox.count()):
            data = self.ui.invoice_warehouse_combobox.itemData(index)
            if data and data[0] == default_warehouse:
                self.ui.invoice_warehouse_combobox.setCurrentIndex(index)
                break

        # additional accounts (discount/red - addition/green)
        addition_account = default_settings['addition_account']
        text = self.ui.discount_addition_account_combobox.itemText(
            self.ui.discount_addition_account_combobox.findData(addition_account))
        text = f"{text} ({self.language_manager.translate('DEFAULT')})"
        self.ui.discount_addition_account_combobox.setItemText(
            self.ui.discount_addition_account_combobox.findData(addition_account),
            text
        )
        self.ui.discount_addition_account_combobox.setItemData(
            self.ui.discount_addition_account_combobox.findData(addition_account),
            QBrush(light_red_color),
            Qt.TextColorRole
        )

        items_additions_account = default_settings['items_additions_account']
        text = self.ui.material_addition_account_combobox.itemText(
            self.ui.material_addition_account_combobox.findData(items_additions_account))
        text = f"{text} ({self.language_manager.translate('DEFAULT')})"
        self.ui.material_addition_account_combobox.setItemText(
            self.ui.material_addition_account_combobox.findData(items_additions_account), text)
        self.ui.material_addition_account_combobox.setItemData(
            self.ui.material_addition_account_combobox.findData(items_additions_account), QBrush(light_red_color),
            Qt.TextColorRole)
        self.ui.material_addition_account_combobox.setCurrentIndex(
            self.ui.material_addition_account_combobox.findData(items_additions_account))

        discounts_account = default_settings['discounts_account']
        text = self.ui.discount_addition_account_combobox.itemText(
            self.ui.discount_addition_account_combobox.findData(discounts_account))
        text = f"{text} ({self.language_manager.translate('DEFAULT')})"
        self.ui.discount_addition_account_combobox.setItemText(
            self.ui.discount_addition_account_combobox.findData(discounts_account),
            text
        )
        self.ui.discount_addition_account_combobox.setItemData(
            self.ui.discount_addition_account_combobox.findData(discounts_account),
            QBrush(dark_green),
            Qt.TextColorRole
        )

        items_discounts_account = default_settings['items_discounts_account']
        text = self.ui.material_discount_account_combobox.itemText(
            self.ui.material_discount_account_combobox.findData(items_discounts_account));
        text = f"{text} ({self.language_manager.translate('DEFAULT')})"
        self.ui.material_discount_account_combobox.setItemText(
            self.ui.material_discount_account_combobox.findData(items_discounts_account), text)
        self.ui.material_discount_account_combobox.setItemData(
            self.ui.material_discount_account_combobox.findData(items_discounts_account), QBrush(dark_green),
            Qt.TextColorRole)
        self.ui.material_discount_account_combobox.setCurrentIndex(
            self.ui.material_discount_account_combobox.findData(items_discounts_account))
        # default price type should be set here, but it's differed to setMaterialDefaults to set it after fetching default price values of the selected material

        # default accounts
        # materials account
        default_materials_account = default_settings.get('materials_account')
        if default_materials_account:
            index = self.ui.materials_account_combobox.findData(default_materials_account)
            current_text = self.ui.materials_account_combobox.itemText(index)
            self.ui.materials_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.materials_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.materials_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.materials_account_combobox.count()):
                text = self.ui.materials_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.materials_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.materials_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # added value account
        default_added_value_account = default_settings.get('added_value_account')
        if default_added_value_account:
            index = self.ui.added_value_account_combobox.findData(default_added_value_account)
            current_text = self.ui.added_value_account_combobox.itemText(index)
            self.ui.added_value_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.added_value_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.added_value_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.added_value_account_combobox.count()):
                text = self.ui.added_value_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.added_value_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.added_value_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # stock account
        default_stock_account = default_settings.get('stock_account')
        if default_stock_account:
            index = self.ui.stock_account_combobox.findData(default_stock_account)
            current_text = self.ui.stock_account_combobox.itemText(index)
            self.ui.stock_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.stock_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.stock_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.stock_account_combobox.count()):
                text = self.ui.stock_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.stock_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.stock_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # monetary account
        default_monetary_account = default_settings.get('monetary_account')
        if default_monetary_account:
            index = self.ui.monetary_account_combobox.findData(default_monetary_account)
            current_text = self.ui.monetary_account_combobox.itemText(index)
            self.ui.monetary_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.monetary_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.monetary_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.monetary_account_combobox.count()):
                text = self.ui.monetary_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.monetary_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.monetary_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # cost account
        default_cost_account = default_settings.get('cost_account')
        if default_cost_account:
            index = self.ui.cost_account_combobox.findData(default_cost_account)
            current_text = self.ui.cost_account_combobox.itemText(index)
            self.ui.cost_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.cost_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.cost_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.cost_account_combobox.count()):
                text = self.ui.cost_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.cost_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.cost_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # gift account
        default_gifts_account = default_settings.get('gifts_account')
        if default_gifts_account:
            index = self.ui.gifts_account_combobox.findData(default_gifts_account)
            current_text = self.ui.gifts_account_combobox.itemText(index)
            self.ui.gifts_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.gifts_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.gifts_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.gifts_account_combobox.count()):
                text = self.ui.gifts_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.gifts_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.gifts_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

        # gift return account
        default_gifts_opposite_account = default_settings.get('gifts_opposite_account')
        if default_gifts_opposite_account:
            index = self.ui.gifts_opposite_account_combobox.findData(default_gifts_opposite_account)
            current_text = self.ui.gifts_opposite_account_combobox.itemText(index)
            self.ui.gifts_opposite_account_combobox.setItemText(index, f"{current_text} ({self.language_manager.translate('DEFAULT')})")
            self.ui.gifts_opposite_account_combobox.setItemData(index, QBrush(dark_green), Qt.TextColorRole)
            self.ui.gifts_opposite_account_combobox.setCurrentIndex(index)
        else:
            for i in range(self.ui.gifts_opposite_account_combobox.count()):
                text = self.ui.gifts_opposite_account_combobox.itemText(i)
                if f"({self.language_manager.translate('DEFAULT')})" in text:
                    self.ui.gifts_opposite_account_combobox.setItemText(i, text.replace(f"({self.language_manager.translate('DEFAULT')})", ""))
                    self.ui.gifts_opposite_account_combobox.setItemData(i, QBrush(), Qt.TextColorRole)

    def setMaterialDefaults(self):
        material_data = self.ui.material_combobox.currentData()
        default_settings = self.fetchInvoiceTypeDefaultSettings()
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

            # default types of prices
            invoice_price = str(default_settings['invoice_price'])
            client_discount = None
            if str(invoice_price) == 'client_price':
                client_id = self.ui.clients_combobox.currentData()
                if client_id:
                    self.ui.material_discount_input.clear()
                    self.ui.material_discount_percent_input.clear()
                    client_data = self.database_operations.fetchClient(client_id)
                    if client_data:
                        client_used_price = client_data['used_price']
                        client_discount = client_data['discount_account_id']
                        invoice_price = client_used_price
                elif str(invoice_price) == 'client_last_sell':
                    pass

            cost_price = str(default_settings['cost_price'])
            gift_price = str(default_settings['gift_price'])

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
                        if str(invoice_price) == str(data[0]):
                            self.ui.material_default_price_type_combobox.setCurrentIndex(index)

            default_cost_price, default_cost_price_unit = next(
                ((p[default_unit], p[default_unit + 3]) for p in prices if p[0] == cost_price), (None, None))
            default_gift_price, ddefault_gift_price_unit = next(
                ((p[default_unit], p[default_unit + 3]) for p in prices if p[0] == gift_price), (None, None))

            # print(default_invoice_price)
            # print(default_cost_price)
            # print(default_gift_price)

            # set default unit
            self.ui.material_unit_combobox.setCurrentIndex(self.ui.material_unit_combobox.findData(default_unit_value))

            self.ui.material_discount_percent_input.clear()
            self.ui.material_discount_input.clear()
            if client_discount:
                self.ui.material_discount_percent_input.setText(str(client_discount))

            if material_data['material_discount_account']:
                self.ui.material_discount_account_combobox.setCurrentIndex(self.ui.material_discount_account_combobox.findData(material_data['material_discount_account']))
            else:
                items_discounts_account = default_settings['items_discounts_account']
                self.ui.material_discount_account_combobox.setCurrentIndex(self.ui.material_discount_account_combobox.findData(items_discounts_account))

            if material_data['material_addition_account']:
                self.ui.material_addition_account_combobox.setCurrentIndex(self.ui.material_addition_account_combobox.findData(material_data['material_addition_account']))
            else:
                items_additions_account = default_settings['items_additions_account']
                self.ui.material_addition_account_combobox.setCurrentIndex(self.ui.material_addition_account_combobox.findData(items_additions_account))

    def updateDefaultGifts(self):
        self.ui.material_gifts_input.clear()
        self.ui.material_gifts_discount_input.clear()
        material_data = self.ui.material_combobox.currentData()
        if material_data:
            gifts = float(material_data['gift']) if material_data['gift'] is not None and material_data['gift'] != 0 else 0
            gifts_for = float(material_data['gift_for']) if material_data['gift_for'] is not None else 0
            if gifts and gifts_for:
                quantity = float(self.ui.material_quantity_input.text()) if self.ui.material_quantity_input.text() else 0
                unit_price = float(
                    self.ui.material_unit_price_input.text()) if self.ui.material_unit_price_input.text() else 0
                if quantity >= gifts:
                    if quantity % gifts_for == 0:
                        gifts_value = (quantity / gifts_for) * gifts
                        self.ui.material_gifts_input.setText(str(gifts_value))
                    else:
                        gifts_value = int(quantity / gifts_for) * gifts
                        lefts = quantity % gifts_for

                        # print("quantity="+str(quantity))
                        # print("gifts="+str(gifts))
                        # print("gifts_for="+str(gifts_for))
                        # print("lefts="+str(lefts))
                        # print("unit_price="+str(unit_price))

                        gifts_discount = round((lefts * unit_price) / gifts_for, 3)
                        message_text = self.language_manager.translate("GIFTS_DISCOUNT_VALUE") + ' ' + str(gifts_discount)
                        messagebox_result = win32api.MessageBox(None, message_text, self.language_manager.translate("ALERT"), win32con.MB_YESNO)
                        if (messagebox_result == win32con.IDYES):
                            self.ui.material_gifts_discount_input.setText(str(gifts_discount))
                            self.ui.material_gifts_input.setText(str(gifts_value))
                        if (messagebox_result == IDNO):
                            pass

                    self.updateMaterialGiftsValue()

        else:
            win32api.MessageBox(0,self.language_manager.translate("NO_MATERIALS_ADDED"), self.language_manager.translate("ALERT"))

    def updateMaterialDefaultPrice(self):
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
        price_value = 0
        currency = 0
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

    def updateMaterialGiftsValue(self):
        default_settings = self.fetchInvoiceTypeDefaultSettings()
        gift_price = default_settings['gift_price']

        gifts = self.ui.material_gifts_input.text()

        if gifts:
            gifts = float(gifts)
        else:
            gifts = 0

        unit_id = self.ui.material_unit_combobox.currentData()

        data = None
        for i in range(self.ui.material_default_price_type_combobox.count()):
            data = self.ui.material_default_price_type_combobox.itemData(i)
            if str(data[0]) == str(gift_price):
                break

        price_units = [data[1], data[4], data[7]]

        gift_price = 0
        gift_price_currency = ''
        if unit_id in price_units:
            index = price_units.index(unit_id)
            if index == 0:
                gift_price = data[2]
                gift_price_currency = data[3]
            elif index == 1:
                gift_price = data[5]
                gift_price_currency = data[6]
            elif index == 2:
                gift_price = data[8]
                gift_price_currency = data[9]

        currency = self.ui.material_currency_combobox.currentData()
        if currency == gift_price_currency:
            self.ui.material_gifts_value_input.setText(str(gift_price))
        else:
            try:
                exchange_value = self.database_operations.fetchExchangeValue(currency, gift_price_currency)
                gifts_price = float(gift_price) * float(exchange_value[0][1])
                gifts_value = float(gifts) * float(gifts_price)
                gifts_value = round(float(gifts_value), 2)
                self.ui.material_gifts_value_input.setText(str(gifts_value))
            except Exception as e:
                print(e)

    def updateMaterialEquilivancePrice(self):
        exchange_value = 0
        equilivance = 0
        if self.ui.material_exchange_combobox.currentData():
            data = self.ui.material_exchange_combobox.currentData()
            exchange_value = float(data[1]) if data and data[1] else ''

        unit_native_price = self.ui.material_unit_price_input.text()
        unit_native_price = float(unit_native_price) if unit_native_price else ''
        if unit_native_price and exchange_value:
            equilivance = unit_native_price * exchange_value
        self.ui.material_equilivance_price_input.setText(str(equilivance))

    def updateMaterialDiscountAndAddition(self, caller=None):
        unit_price = self.ui.material_unit_price_input.text()
        quantity = self.ui.material_quantity_input.text()

        if unit_price and quantity:
            total_price = float(unit_price) * float(quantity)

            material_discount = float(
                self.ui.material_discount_input.text()) if self.ui.material_discount_input.text() else 0
            material_discount_percent = float(
                self.ui.material_discount_percent_input.text()) if self.ui.material_discount_percent_input.text() else 0
            material_addition = float(
                self.ui.material_addition_input.text()) if self.ui.material_addition_input.text() else 0
            material_addition_percent = float(
                self.ui.material_addition_percent_input.text()) if self.ui.material_addition_percent_input.text() else 0

            if caller == "material_discount":
                if material_discount:
                    discount_percent = round(material_discount * 100 / total_price, 3)
                    self.ui.material_discount_percent_input.setText(str(discount_percent))
                else:
                    self.ui.material_discount_percent_input.setText(str(0))
            elif caller == "material_discount_percent":
                if material_discount_percent:
                    discount = round(material_discount_percent * total_price / 100, 3)
                    self.ui.material_discount_input.setText(str(discount))
                else:
                    self.ui.material_discount_input.setText(str(0))
            elif caller == "material_addition":
                if material_addition:
                    addition_percent = round(material_addition * 100 / total_price, 3)
                    self.ui.material_addition_percent_input.setText(str(addition_percent))
                else:
                    self.ui.material_addition_percent_input.setText(str(0))
            elif caller == "material_addition_percent":
                if material_addition_percent:
                    addition = round(material_addition_percent * total_price / 100, 3)
                    self.ui.material_addition_input.setText(str(addition))
                else:
                    self.ui.material_addition_percent_input.setText(str(0))
            else:
                if material_discount:
                    discount_percent = round(material_discount * 100 / total_price, 3)
                    self.ui.material_discount_percent_input.setText(str(discount_percent))
                elif material_discount_percent:
                    discount = round(material_discount_percent * total_price / 100, 3)
                    self.ui.material_discount_input.setText(str(discount))
                else:
                    self.ui.material_discount_input.setText(str(0))
                    self.ui.material_discount_percent_input.setText(str(0))

                if material_addition:
                    addition_percent = round(material_addition * 100 / total_price, 3)
                    self.ui.material_addition_percent_input.setText(str(addition_percent))
                elif material_addition_percent:
                    addition = round(material_addition_percent * total_price / 100, 3)
                    self.ui.material_addition_input.setText(str(addition))
                else:
                    self.ui.material_addition_input.setText(str(0))
                    self.ui.material_addition_percent_input.setText(str(0))

    def updateInvoiceDiscountAndAddition(self):
        currency = self.ui.discount_addition_currency_combobox.currentData()
        exchange_data = self.ui.discount_addition_exchange_combobox.currentData()
        exchange_value = 0
        if exchange_data:
            exchange_value = exchange_data[1]
        value = self.ui.invoice_discoun_addition_input.text()
        equilivance = ''
        print(exchange_data)
        if currency == '%' and value:
            equilivance = float(value)
        elif value and exchange_value:
            equilivance = float(value) * float(exchange_value)

        self.ui.invoice_discount_addition_equilivance_value_input.setText(str(equilivance))

    def addInvoiceDiscountAndAddition(self):
        value = float(
            self.ui.invoice_discoun_addition_input.text()) if self.ui.invoice_discoun_addition_input.text() else ""
        if (value):
            operation_type = self.ui.discount_addition_type_combobox.currentData()
            operation_type_text = self.ui.discount_addition_type_combobox.currentText()
            exchange_data = self.ui.discount_addition_exchange_combobox.currentData()
            exchange_value = exchange_data[0] if exchange_data and exchange_data[0] else ''
            exchange_text = self.ui.discount_addition_exchange_combobox.currentText()
            account_data = self.ui.discount_addition_account_combobox.currentData()
            account_text = self.ui.discount_addition_account_combobox.currentText()
            currency_data = self.ui.discount_addition_currency_combobox.currentData()
            currency_text = self.ui.discount_addition_currency_combobox.currentText()

            equilivance_value = self.ui.invoice_discount_addition_equilivance_value_input.text()
            cost_center_data = self.ui.discount_addition_cost_center_combobox.currentData()
            cost_center_text = self.ui.discount_addition_cost_center_combobox.currentText()

            if account_data is None:
                win32api.MessageBox(0,self.language_manager.translate("ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
                return

            opposite_account_data = None
            if str(self.ui.payment_method_combobox.currentData()).lower() == 'cash':
                opposite_account_data = self.ui.monetary_account_combobox.currentData()
                opposite_account_text = self.ui.monetary_account_combobox.currentText()

            elif str(self.ui.payment_method_combobox.currentData()).lower() == 'postponed':
                opposite_account_data = self.ui.client_account_combobox.currentData()
                opposite_account_text = self.ui.client_account_combobox.currentText()

            if opposite_account_data and equilivance_value:
                # get current row count
                row_count = self.ui.discounts_additions_table.rowCount()
                # insert a new row
                self.ui.discounts_additions_table.insertRow(row_count)

                # add values to the new row
                self.ui.discounts_additions_table.setItem(row_count, 0, QTableWidgetItem(str('')))
                self.ui.discounts_additions_table.setItem(row_count, 1, QTableWidgetItem(str(account_data)))
                self.ui.discounts_additions_table.setItem(row_count, 2, QTableWidgetItem(str(account_text)))
                self.ui.discounts_additions_table.setItem(row_count, 3, QTableWidgetItem(str(operation_type)))
                self.ui.discounts_additions_table.setItem(row_count, 4, QTableWidgetItem(str(operation_type_text)))
                self.ui.discounts_additions_table.setItem(row_count, 5, QTableWidgetItem(str(currency_data)))
                self.ui.discounts_additions_table.setItem(row_count, 6, QTableWidgetItem(str(currency_text)))
                self.ui.discounts_additions_table.setItem(row_count, 7, QTableWidgetItem(str(exchange_value)))
                self.ui.discounts_additions_table.setItem(row_count, 8, QTableWidgetItem(str(exchange_text)))
                self.ui.discounts_additions_table.setItem(row_count, 9, QTableWidgetItem(str(equilivance_value)))
                self.ui.discounts_additions_table.setItem(row_count, 10, QTableWidgetItem(str(cost_center_data[0])))
                self.ui.discounts_additions_table.setItem(row_count, 11, QTableWidgetItem(str(cost_center_text)))
                self.ui.discounts_additions_table.setItem(row_count, 12, QTableWidgetItem(str(opposite_account_data)))
                self.ui.discounts_additions_table.setItem(row_count, 13, QTableWidgetItem(str(opposite_account_text)))

                # clear inputs and recalculate invoice's values
                self.ui.invoice_discoun_addition_input.clear()
            else:
                win32api.MessageBox(0,self.language_manager.translate("CUSTOMER_ACCOUNT_OR_INVOICE_CURRENCY_ERROR"), self.language_manager.translate("ERROR"))

        # if there are items added to the invoice, user can no longer change invoice's currency.
        if self.ui.discounts_additions_table.columnCount() > 0:
            self.ui.invoice_currency_combobox.setDisabled(True)
            self.ui.invoice_currency_combobox.setToolTip(
                self.language_manager.translate("INVOICE_CURRENCY_CHANGE_ERROR"))
            self.ui.payment_method_combobox.setDisabled(True)
            self.ui.payment_method_combobox.setToolTip(
                self.language_manager.translate("INVOICE_PAYMENT_METHOD_CHANGE_ERROR"))

    def addInvoiceItem(self):
        # Get fields inputs
        material_production_date = self.ui.production_date_input.text() or ''
        material_expire_date = self.ui.expire_date_input.text() or ''
        material_output_way = self.ui.output_way_combobox.currentData() or ''
        material_discount = self.ui.material_discount_input.text() or ''
        material_unit_price = self.ui.material_unit_price_input.text() or ''
        material_equilivance_price = self.ui.material_equilivance_price_input.text() or ''
        material_addition = self.ui.material_addition_input.text() or ''
        material_gifts_discount = self.ui.material_gifts_discount_input.text() or ''
        material_gifts = self.ui.material_gifts_input.text() or ''
        material_gifts_value = self.ui.material_gifts_value_input.text() or ''
        material_discount_percent = self.ui.material_discount_percent_input.text() or ''
        material_addition_percent = self.ui.material_addition_percent_input.text() or ''
        material_notes = self.ui.material_notes_input.text() or ''
        material_added_value = self.ui.material_added_value_input.text() or ''
        quantity = self.ui.material_quantity_input.text() or ''

        material_warehouse_data = self.ui.material_warehouse_combobox.currentData() or ''
        material_warehouse_id = material_warehouse_data[0]

        # Get IDs from comboboxes
        material_default_price_type_id = self.ui.material_default_price_type_combobox.currentData()
        material_cost_center_id = ''
        material_warehouse_id = self.ui.material_warehouse_combobox.currentData()[0]
        material_warehouse_account = self.ui.material_warehouse_combobox.currentData()[1]
        if material_warehouse_id is None:
            material_warehouse_id = self.ui.invoice_warehouse_combobox.currentData()[0]
            material_warehouse_account = self.ui.invoice_warehouse_combobox.currentData()[1]

        material_unit_id = self.ui.material_unit_combobox.currentData()
        material_unit_name = self.ui.material_unit_combobox.currentText()
        material_currency_id = self.ui.material_currency_combobox.currentData()
        invoice_currency_id = self.ui.invoice_currency_combobox.currentData()
        material_exchange_id = self.ui.material_exchange_combobox.currentData()[0] if self.ui.material_exchange_combobox.currentData() else None


        material_discount_account = self.ui.material_discount_account_combobox.currentData()
        material_addition_account = self.ui.material_addition_account_combobox.currentData()
        material_gifts_account = self.ui.gifts_account_combobox.currentData()


        # Get names from comboboxes
        material_default_price_type = self.ui.material_default_price_type_combobox.currentText()
        material_cost_center = ''
        material_warehouse = self.ui.material_warehouse_combobox.currentText()
        if material_warehouse_id is None:
            material_warehouse = self.ui.invoice_warehouse_combobox.currentText()

        material_currency = self.ui.material_currency_combobox.currentText()
        invoice_currency = self.ui.invoice_currency_combobox.currentText()
        material_exchange = self.ui.material_exchange_combobox.currentText()
        material_discount_account_name = self.ui.material_discount_account_combobox.currentText()
        material_addition_account_name = self.ui.material_addition_account_combobox.currentText()

        # Get material data
        material_data = self.ui.material_combobox.currentData()
        if material_data == {}:
            win32api.MessageBox(0, self.language_manager.translate("MATERIAL_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return
        material_id = material_data['id']
        material_name = material_data['name']

        # Units registered with the material
        unit1_id = material_data['unit1']
        unit2_id = material_data['unit2']
        unit3_id = material_data['unit3']
        # fetch units names
        unit1_name = self.database_operations.fetchUnit(unit1_id)[1] if unit1_id and unit1_id != '' else ''
        unit2_name = self.database_operations.fetchUnit(unit2_id)[1] if unit2_id and unit2_id != '' else ''
        unit3_name = self.database_operations.fetchUnit(unit3_id)[1] if unit3_id and unit3_id != '' else ''
        material_units = [unit1_id, unit2_id, unit3_id]

        quantities_and_units = [{"unit_id": unit1_id, "unit_name": unit1_name, "quantity": "", "conversion_rate": 1},
                                {"unit_id": unit2_id, "unit_name": unit2_name, "quantity": "", "conversion_rate": 1},
                                {"unit_id": unit3_id, "unit_name": unit3_name, "quantity": "", "conversion_rate": 1}]

        # Set the quantity of the selected unit in the UI to match the quantity entered in the quantity input in the UI
        for item in quantities_and_units:
            if item['unit_id'] == material_unit_id:
                item['quantity'] = quantity
                break

        for item in quantities_and_units:
            if item['unit_id'] != material_unit_id and item['unit_id'] is not None:
                conversion_rate = self.database_operations.fetchUnitConversionValueBetween(material_unit_id, item['unit_id'])
                if isinstance(conversion_rate, (int, float)):
                    item['quantity'] = float(quantity) * conversion_rate
                else:
                    item['quantity'] = ''
                item['conversion_rate'] = conversion_rate

        if material_production_date and material_expire_date:
            prod_date = datetime.datetime.strptime(material_production_date, '%Y-%m-%d')
            expire_date = datetime.datetime.strptime(material_expire_date, '%Y-%m-%d')
            if prod_date > expire_date:
                win32api.MessageBox(0, self.language_manager.translate("PRODUCTION_DATE_MUST_BE_LESS_THAN_EXPIRE_DATE"), self.language_manager.translate("ALERT"))
                return

        if material_addition not in ['0', '0.0', ''] and material_addition_account is None:
            win32api.MessageBox(0, self.language_manager.translate("ADDITIONS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if material_discount not in ['0', '0.0', ''] and material_discount_account is None:
            win32api.MessageBox(0, self.language_manager.translate("DISCOUNTS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if material_gifts not in ['0', '0.0', ''] and material_gifts_account is None:
            win32api.MessageBox(0, self.language_manager.translate("GIFTS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if material_gifts_discount not in ['0', '0.0', ''] and material_gifts_account is None:
            win32api.MessageBox(0, self.language_manager.translate("GIFTS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if invoice_currency_id is None or invoice_currency_id == "None":
            win32api.MessageBox(0, self.language_manager.translate("INVOICE_CURRENCY_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if material_warehouse_id is None or material_warehouse_id == "None":
            win32api.MessageBox(0, self.language_manager.translate("MATERIAL_WAREHOUSE_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return
        
        if self.origin_invoice_data:
            original_material_quantity = self.origin_invoice_data[material_id]['quantity']
            if float(quantity) > float(original_material_quantity):
                win32api.MessageBox(0, self.language_manager.translate("MATERIAL_QUANTITY_NOT_AVAILABLE_FOR_RETURNED_INVOICE"), self.language_manager.translate("ALERT"))
                return
        else:
            invoice_type_name = self.ui.invoice_type_combobox.currentText()
            invoice_effect_on_warehouse = self.database_operations.fetchSetting(f'{invoice_type_name}_affects_on_warehouse')
            if invoice_effect_on_warehouse == 'reduce':
                # Check if the warehouse has enough stock for the quantity
                material_warehouse_quantity = 0
                material_warehouses = self.database_operations.fetchMaterialWarehouses(material_id)

                for warehouse_id, records in material_warehouses.items():
                    for record in records:
                        if warehouse_id == material_warehouse_id:
                            if material_unit_id == record['unit']:
                                material_warehouse_quantity += record['quantity']
                            else:
                                conversion_rate = self.database_operations.fetchUnitConversionValueBetween(record['unit'], material_unit_id)
                                material_warehouse_quantity += record['quantity'] * conversion_rate

                material_gifts = 0 if material_gifts == '0' or material_gifts == '0.0' or material_gifts == '' or material_gifts == 'None' else float(material_gifts)
                if float(material_warehouse_quantity) < (float(quantity) + float(material_gifts)):
                    win32api.MessageBox(0, f"{self.language_manager.translate('MATERIAL_QUANTITY_NOT_AVAILABLE')}: {material_warehouse_quantity} {material_unit_name}", self.language_manager.translate("ALERT"))
                    return

        # Update material equilivance price based on unit1 conversion rate
        material_equilivance_price = (1 / quantities_and_units[0]['conversion_rate']) * float(material_equilivance_price)

        if all([quantity, material_unit_price, material_equilivance_price]):
            self.ui.materials_table.blockSignals(True)  # disable signals to prevent recalculation

            new_row_number = self.ui.materials_table.rowCount()
            self.ui.materials_table.insertRow(new_row_number)
            checkbox = QtWidgets.QCheckBox()
            checkbox_item = QTableWidgetItem()
            self.ui.materials_table.setItem(new_row_number, 0, checkbox_item)
            self.ui.materials_table.setCellWidget(new_row_number, 0, checkbox)
            self.ui.materials_table.setItem(new_row_number, 1, QTableWidgetItem(str(material_id)))
            self.ui.materials_table.setItem(new_row_number, 2, QTableWidgetItem(str(material_name)))
            self.ui.materials_table.setItem(new_row_number, 3,
                                            QTableWidgetItem(str(quantities_and_units[0]["quantity"])))
            self.ui.materials_table.setItem(new_row_number, 4,
                                            QTableWidgetItem(str(quantities_and_units[0]["unit_id"])))
            self.ui.materials_table.setItem(new_row_number, 5,
                                            QTableWidgetItem(str(quantities_and_units[0]["unit_name"])))
            self.ui.materials_table.setItem(new_row_number, 6,
                                            QTableWidgetItem(str(quantities_and_units[1]["quantity"])))
            self.ui.materials_table.setItem(new_row_number, 7,
                                            QTableWidgetItem(str(quantities_and_units[1]["unit_id"])))
            self.ui.materials_table.setItem(new_row_number, 8,
                                            QTableWidgetItem(str(quantities_and_units[1]["unit_name"])))
            self.ui.materials_table.setItem(new_row_number, 9,
                                            QTableWidgetItem(str(quantities_and_units[2]["quantity"])))
            self.ui.materials_table.setItem(new_row_number, 10,
                                            QTableWidgetItem(str(quantities_and_units[2]["unit_id"])))
            self.ui.materials_table.setItem(new_row_number, 11,
                                            QTableWidgetItem(str(quantities_and_units[2]["unit_name"])))
            self.ui.materials_table.setItem(new_row_number, 12,
                                            QTableWidgetItem(str(material_default_price_type_id[0])))
            self.ui.materials_table.setItem(new_row_number, 13, QTableWidgetItem(str(material_default_price_type)))
            self.ui.materials_table.setItem(new_row_number, 14, QTableWidgetItem(str(material_unit_price)))
            self.ui.materials_table.setItem(new_row_number, 15, QTableWidgetItem(str(material_currency_id)))
            self.ui.materials_table.setItem(new_row_number, 16, QTableWidgetItem(str(material_currency)))
            self.ui.materials_table.setItem(new_row_number, 17, QTableWidgetItem(str(material_equilivance_price)))
            self.ui.materials_table.setItem(new_row_number, 18, QTableWidgetItem(str(invoice_currency_id)))
            self.ui.materials_table.setItem(new_row_number, 19, QTableWidgetItem(str(invoice_currency)))
            self.ui.materials_table.setItem(new_row_number, 20, QTableWidgetItem(str(material_exchange_id)))
            self.ui.materials_table.setItem(new_row_number, 21, QTableWidgetItem(str(material_exchange)))
            self.ui.materials_table.setItem(new_row_number, 22, QTableWidgetItem(str(material_discount)))
            self.ui.materials_table.setItem(new_row_number, 23, QTableWidgetItem(str(material_discount_percent)))
            self.ui.materials_table.setItem(new_row_number, 24, QTableWidgetItem(str(material_discount_account)))
            self.ui.materials_table.setItem(new_row_number, 25, QTableWidgetItem(str(material_discount_account_name)))
            self.ui.materials_table.setItem(new_row_number, 26, QTableWidgetItem(str(material_addition)))
            self.ui.materials_table.setItem(new_row_number, 27, QTableWidgetItem(str(material_addition_percent)))
            self.ui.materials_table.setItem(new_row_number, 28, QTableWidgetItem(str(material_addition_account)))
            self.ui.materials_table.setItem(new_row_number, 29, QTableWidgetItem(str(material_addition_account_name)))
            self.ui.materials_table.setItem(new_row_number, 30, QTableWidgetItem(str(material_added_value)))
            self.ui.materials_table.setItem(new_row_number, 31, QTableWidgetItem(str(material_gifts)))
            self.ui.materials_table.setItem(new_row_number, 32, QTableWidgetItem(str(material_gifts_value)))
            self.ui.materials_table.setItem(new_row_number, 33, QTableWidgetItem(str(material_gifts_discount)))
            self.ui.materials_table.setItem(new_row_number, 34, QTableWidgetItem(str(material_warehouse_id)))
            self.ui.materials_table.setItem(new_row_number, 35, QTableWidgetItem(str(material_warehouse)))
            self.ui.materials_table.setItem(new_row_number, 36, QTableWidgetItem(str(material_cost_center_id)))
            self.ui.materials_table.setItem(new_row_number, 37, QTableWidgetItem(str(material_cost_center)))
            self.ui.materials_table.setItem(new_row_number, 38, QTableWidgetItem(str(material_notes)))
            self.ui.materials_table.setItem(new_row_number, 39, QTableWidgetItem(str(material_warehouse_account)))
            self.ui.materials_table.setItem(new_row_number, 40, QTableWidgetItem(str(material_production_date)))
            self.ui.materials_table.setItem(new_row_number, 41, QTableWidgetItem(str(material_expire_date)))
            self.ui.materials_table.setItem(new_row_number, 42, QTableWidgetItem(str(material_output_way)))

            self.calculateInvoiceValues()

            self.ui.materials_table.blockSignals(False)  # enable signals again

        else:
            win32api.MessageBox(0, self.language_manager.translate("MATERIAL_INSERT_ERROR"), self.language_manager.translate("ALERT"))

    def removeInvoiceDiscountAndAddition(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
        if (messagebox_result == IDYES):
            selected_row = self.ui.discounts_additions_table.currentRow()
            if selected_row is not None and selected_row != -1:
                item_id = self.ui.discounts_additions_table.item(selected_row, 0).text()
                if item_id != '':
                    try:
                        self.database_operations.removeInvoiceDiscountAddition(item_id, commit=False)
                    except:
                        win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
                        return

                self.ui.discounts_additions_table.removeRow(selected_row)
                # if there are items added to the invoice, user can no longer change invoice's currency.
                if self.ui.materials_table.columnCount() > 0:
                    self.ui.invoice_currency_combobox.setEnabled(True)
                    self.ui.invoice_currency_combobox.setToolTip(None)
                    self.ui.payment_method_combobox.setEnabled(True)
                    self.ui.payment_method_combobox.setToolTip(None)

        if (messagebox_result == IDNO):
            pass

    def removeInvoiceItem(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
        if (messagebox_result == IDYES):
            # Iterate through rows in reverse order
            for row in range(self.ui.materials_table.rowCount() - 1, -1, -1):
                checkbox = self.ui.materials_table.cellWidget(row, 0)
                if checkbox.isChecked():
                    item_id = self.ui.materials_table.item(row, 0).text()
                    if item_id != '':
                        try:
                            self.database_operations.removeInvoiceMaterial(item_id, commit=False)
                        except:
                            win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
                            return

                    self.ui.materials_table.removeRow(row)

        if (messagebox_result == IDNO):
            pass

    def calculateInvoiceValues(self):
        total_discounts = 0
        total_additions = 0
        total_gifts_discount = 0
        total_partial_sum = 0

        invoice_base_value = 0  # The value of invoice with materials only discounts and additions
        for row in range(self.ui.materials_table.rowCount()):
            discount_item = self.ui.materials_table.item(row, 22)
            discount = discount_item.text() if discount_item is not None else 0
            if discount and discount != 'None':
                total_discounts += float(discount)
            addition_item = self.ui.materials_table.item(row, 26)
            addition = addition_item.text() if addition_item is not None else 0
            if addition and addition != 'None':
                total_additions += float(addition)
            gifts_discount = self.ui.materials_table.item(row, 33).text() if self.ui.materials_table.item(row,33) else 0
            if gifts_discount and gifts_discount != 'None':
                total_gifts_discount += float(gifts_discount)
            quantity = self.ui.materials_table.item(row, 3).text()  # use quantity 1 for calculations
            equilivance_price = self.ui.materials_table.item(row, 17).text()

            partial_price = round((float(quantity) * float(equilivance_price)), 5)
            total_partial_sum += partial_price

        self.ui.gifts_discount.setText(str(total_gifts_discount))
        self.ui.items_additions.setText(str(total_additions))
        self.ui.items_discounts.setText(str(total_discounts))
        self.ui.partial_sum.setText(str(total_partial_sum))

        # calculate invoice discounts and additions
        total_invoice_discounts = 0
        total_invoice_additions = 0
        total_invoice_percent_discounts = 0
        total_invoice_percent_additions = 0

        # loop discounts and additions table to add/subtract direct values
        for row in range(self.ui.discounts_additions_table.rowCount()):
            type_col = self.ui.discounts_additions_table.item(row, 3).text()
            value = self.ui.discounts_additions_table.item(row, 9).text()  # the value of the equilivance
            currency = self.ui.discounts_additions_table.item(row, 6).text()

            if str(type_col).lower() == 'discount' and str(currency) != '%':  # normal discount
                total_invoice_discounts += float(value)
            elif str(type_col).lower() == 'discount' and str(currency) == '%':  # percent discount
                total_invoice_percent_discounts += float(value)
            elif str(type_col).lower() == 'addition' and str(currency) != '%':  # normal addition
                total_invoice_additions += float(value)
            elif str(type_col).lower() == 'addition' and str(currency) == '%':  # percent addition
                total_invoice_percent_additions += float(value)

        invoice_value = round((float(total_partial_sum) + float(total_additions) - float(total_discounts) - float(
            total_gifts_discount) + float(total_invoice_additions) - float(total_invoice_discounts)), 5)

        invoice_percent_discount_value = (float(invoice_value) * float(total_invoice_percent_discounts) / 100)

        invoice_percent_additions_value = (float(invoice_value) * float(total_invoice_percent_additions) / 100)

        invoice_value = invoice_value + invoice_percent_additions_value - invoice_percent_discount_value

        self.ui.invoice_value_input.setText(str(invoice_value))

        # Do something with the values

    def saveInvoice(self, window):
        # Disable UI
        # self.ui.invoice_tabs.setDisabled(True)

        # invoice info
        number = self.ui.number_input.text()
        date = self.ui.date_input.text()
        statement = self.ui.statement_input.toPlainText()

        invoice_type_data = self.ui.invoice_type_combobox.currentData()
        invoice_type = invoice_type_data[0]
        invoice_type_category = invoice_type_data[1]
        client = self.ui.clients_combobox.currentData() or ''
        client_account = self.ui.client_account_combobox.currentData() or ''
        invoice_currency = self.ui.invoice_currency_combobox.currentData()
        payment_method = self.ui.payment_method_combobox.currentData()
        paid = 1 if payment_method == 'cash' else 0
        invoice_cost_center_data = self.ui.invoice_cost_center_combobox.currentData()
        gifts_account = self.ui.gifts_account_combobox.currentData()
        invoice_warehouse_data = self.ui.invoice_warehouse_combobox.currentData()
        cost_account = self.ui.cost_account_combobox.currentData()
        added_value_account = self.ui.added_value_account_combobox.currentData()
        monetary_account = self.ui.monetary_account_combobox.currentData()
        stock_account = self.ui.stock_account_combobox.currentData()
        gifts_opposite_account = self.ui.gifts_opposite_account_combobox.currentData()
        materials_account = self.ui.materials_account_combobox.currentData()
        inventory_type = self.database_operations.fetchSetting('inventory_type')
        origin_id = self.ui.origin_invoice_combobox.currentData()

        invoice_type_name = self.ui.invoice_type_combobox.currentText()
        invoice_effect_on_warehouse = self.database_operations.fetchSetting(f'{invoice_type_name}_affects_on_warehouse')
        if not invoice_effect_on_warehouse and self.ui.material_warehouse_checkbox.isChecked():
            message = self.language_manager.translate("ADDING_TO_WAREHOUSE_ERROR")
            win32api.MessageBox(0, message, self.language_manager.translate("ALERT"))
            return

        if invoice_currency is None or invoice_currency == "None":
            win32api.MessageBox(0, self.language_manager.translate("INVOICE_CURRENCY_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if monetary_account is None or monetary_account == "None":
            win32api.MessageBox(0, self.language_manager.translate("MONETARY_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if materials_account is None or materials_account == "None":
            win32api.MessageBox(0, self.language_manager.translate("MATERIALS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        if inventory_type == 'perpetual':
            if stock_account is None or cost_account is None:
                win32api.MessageBox(0, self.language_manager.translate("PERPETUAL_INVENTORY_TYPE_ERROR"), self.language_manager.translate("ALERT"))
                return

        # Check and replace values
        if invoice_cost_center_data is None or invoice_cost_center_data == "None" or invoice_cost_center_data[0] is None:
            invoice_cost_center = ""
        else:
            invoice_cost_center = invoice_cost_center_data[0]

        if gifts_account is None or gifts_account == "None":
            gifts_account = ""

        try:
            invoice_warehouse = invoice_warehouse_data[0]
            if invoice_warehouse is None or invoice_warehouse == "None":
                invoice_warehouse = ""
        except:
            invoice_warehouse = ''

        if cost_account is None or cost_account == "None":
            cost_account = ""

        if added_value_account is None or added_value_account == "None":
            added_value_account = ""

        if monetary_account is None or monetary_account == "None":
            monetary_account = ""

        if stock_account is None or stock_account == "None":
            stock_account = ""

        if gifts_opposite_account is None or gifts_opposite_account == "None":
            gifts_opposite_account = ""

        if materials_account is None or materials_account == "None":
            materials_account = ""

        if origin_id is None or origin_id == "None":
            origin_id = ""

        invoice_id = None
        # try:
        if not self.invoice_id: # add new invoice
            invoice_id = self.database_operations.addInvoice(number, date, statement, invoice_type, client, client_account,invoice_currency,payment_method, paid, invoice_cost_center, gifts_account,invoice_warehouse, cost_account,added_value_account, monetary_account, stock_account,gifts_opposite_account, materials_account, origin_id, commit=False)

        else: # update existing invoice
            invoice_id = self.invoice_id
            self.database_operations.updateInvoice(invoice_id, number, date, statement, invoice_type, client, client_account,invoice_currency,payment_method, paid, invoice_cost_center, gifts_account,invoice_warehouse,cost_account,added_value_account, monetary_account, stock_account, gifts_opposite_account, materials_account, commit=False)

        # except Exception as e:
        #     print(e)
        #     win32api.MessageBox(0, "لا يمكن حفظ الفاتورة، قد يكون الرقم مستخدم من قبل فاتورة أخرى", "خطأ")
            # return

        for row in range(self.ui.materials_table.rowCount()):
            invoice_item_id = self.ui.materials_table.item(row, 0).text()
            material_id = self.ui.materials_table.item(row, 1).text()
            material = self.ui.materials_table.item(row, 2).text()
            quantity1 = self.ui.materials_table.item(row, 3).text()
            unit1_id = self.ui.materials_table.item(row, 4).text()
            unit1 = self.ui.materials_table.item(row, 5).text()
            quantity2 = self.ui.materials_table.item(row, 6).text()
            unit2_id = self.ui.materials_table.item(row, 7).text()
            unit2 = self.ui.materials_table.item(row, 8).text()
            quantity3 = self.ui.materials_table.item(row, 9).text()
            unit3_id = self.ui.materials_table.item(row, 10).text()
            unit3 = self.ui.materials_table.item(row, 11).text()
            price_type_id = self.ui.materials_table.item(row, 12).text()
            price_type = self.ui.materials_table.cellWidget(row, 13).currentText() if invoice_item_id != '' else self.ui.materials_table.item(row, 13).text()
            unit_price = self.ui.materials_table.item(row, 14).text()
            currency_id = self.ui.materials_table.item(row, 15).text()
            currency = self.ui.materials_table.cellWidget(row, 16).currentText() if invoice_item_id != '' else self.ui.materials_table.item(row, 16).text()
            equilivance_price = self.ui.materials_table.item(row, 17).text()
            equilivance_currency_id = self.ui.materials_table.item(row, 18).text()
            equilivance_currency = self.ui.materials_table.item(row, 19).text()
            exchange_id = self.ui.materials_table.item(row, 20).text()
            exchange = self.ui.materials_table.item(row, 21).text()
            discount = self.ui.materials_table.item(row, 22).text()
            discount_percent = self.ui.materials_table.item(row, 23).text()
            discount_account = self.ui.materials_table.item(row, 24).text()
            discount_account_name = self.ui.materials_table.item(row, 25).text()
            addition = self.ui.materials_table.item(row, 26).text()
            addition_percent = self.ui.materials_table.item(row, 27).text()
            addition_account = self.ui.materials_table.item(row, 28).text()
            addition_account_name = self.ui.materials_table.item(row, 29).text()
            added_value = self.ui.materials_table.item(row, 30).text()
            gifts = self.ui.materials_table.item(row, 31).text()
            gifts_value = self.ui.materials_table.item(row, 32).text()
            gifts_discount = self.ui.materials_table.item(row, 33).text()
            warehouse_id = self.ui.materials_table.item(row, 34).text()
            warehouse = self.ui.materials_table.item(row, 35).text()
            cost_center_id = self.ui.materials_table.item(row, 36).text()
            cost_center = self.ui.materials_table.item(row, 37).text()
            notes = self.ui.materials_table.item(row, 38).text()
            warehouse_account_id = self.ui.materials_table.item(row, 39).text()
            production_date = self.ui.materials_table.item(row, 40).text()
            expire_date = self.ui.materials_table.item(row, 41).text()

            try:
                output_way = self.ui.materials_table.item(row, 42).text()
            except:
                output_way = ''

            warehouse_id = '' if not warehouse_id or warehouse_id in ['None', None] else warehouse_id
            cost_center_id = '' if not cost_center_id or cost_center_id in ['None', None] else cost_center_id
            exchange_id = '' if not exchange_id or exchange_id in ['None', None] else exchange_id  # '' when material price is same as invoice price
            # Convert quantities to empty strings if None or not set
            quantity1 = '' if not quantity1 or quantity1 == 'None' else quantity1
            quantity2 = '' if not quantity2 or quantity2 == 'None' else quantity2
            quantity3 = '' if not quantity3 or quantity3 == 'None' else quantity3

            # Convert unit IDs to empty strings if None or not set
            unit1_id = '' if not unit1_id or unit1_id == 'None' else unit1_id
            unit2_id = '' if not unit2_id or unit2_id == 'None' else unit2_id
            unit3_id = '' if not unit3_id or unit3_id == 'None' else unit3_id

            # Convert discount and additioسn accounts to empty strings if None or not set
            discount_account = '' if not discount_account or discount_account == 'None' else discount_account
            addition_account = '' if not addition_account or addition_account == 'None' else addition_account

            gifts = 0 if gifts == '0' or gifts == '0.0' or gifts == '' or gifts == 'None' else gifts
            gifts_discount = 0 if gifts_discount == '0' or gifts_discount == '0.0' or gifts_discount == '' or gifts_discount == 'None' else gifts_discount

            if invoice_item_id == '': # add new invoice item
                invoice_item_id = self.database_operations.addInvoiceMaterial(invoice_id, material_id, quantity1, unit1_id, quantity2, unit2_id, quantity3, unit3_id, price_type_id, unit_price, currency_id, equilivance_price, discount, discount_percent, addition, addition_percent, added_value, gifts, gifts_value, gifts_discount, warehouse_id, cost_center_id, notes, exchange_id, discount_account, addition_account, production_date, expire_date, commit=False)

            else: # update existing invoice item
                self.database_operations.updateInvoiceMaterial(invoice_item_id, invoice_id, material_id, quantity1, unit1_id, quantity2, unit2_id, quantity3, unit3_id, price_type_id, unit_price, currency_id, equilivance_price, discount, discount_percent, addition, addition_percent, added_value, gifts, gifts_value, gifts_discount, warehouse_id, cost_center_id, notes, exchange_id, discount_account, addition_account, production_date, expire_date, commit=False)

            if self.ui.material_warehouse_checkbox.isChecked():
                if invoice_effect_on_warehouse == 'add':
                    if self.invoice_id and self.ui.materials_table.item(row, 0).text() != '':
                        old_quantity = self.old_quantities[int(invoice_item_id)] + float(gifts)
                        new_quantity = float(quantity1) - float(old_quantity)
                        new_quantity = new_quantity + float(gifts)
                        if new_quantity > 0:
                            # First create the material move record
                            material_move_id = self.database_operations.moveMaterial(
                                quantity=new_quantity,
                                move_unit=unit1_id,
                                material_id=material_id,
                                to_warehouse=warehouse_id,
                                origin_type='invoice',
                                origin_id=invoice_item_id,
                                commit=False,
                                record_only=True,
                                record_journal_entry=False
                            )

                            # Then create warehouse entry with the material_move_id
                            warehouse_entry_id = self.database_operations.addMaterialToWarehouse(
                                warehouse_id,
                                material_id,
                                new_quantity,
                                unit1_id,
                                production_date=production_date,
                                expire_date=expire_date,
                                material_move_id=material_move_id,
                                commit=False
                            )

                            # Finally update the material move with the warehouse entry
                            self.database_operations.updateMaterialMove(
                                material_move_id,
                                to_warehouse_entry_id=warehouse_entry_id,
                                commit=False
                            )
                        else:
                            quantity_to_reduce = -new_quantity
                            if float(quantity_to_reduce) > 0.0:
                                modified_records = self.database_operations.reduceMaterialInWarehouse(warehouse_id, material_id, quantity_to_reduce, unit1_id, order=output_way, commit=False)
                                for record in modified_records:
                                    self.database_operations.moveMaterial(quantity=record['reduced_quantity'],
                                                                move_unit=record['unit'],
                                                                material_id=material_id,
                                                                from_warehouse=warehouse_id,
                                                                from_warehouse_entry_id=record['id'],
                                                                origin_type='invoice',
                                                                origin_id=invoice_item_id,
                                                                record_only=True,
                                                                commit=False,
                                                                record_journal_entry=False)
                    else:
                        quantity_to_add = float(quantity1) + float(gifts)
                        material_move_id = self.database_operations.moveMaterial(quantity=quantity_to_add, move_unit=unit1_id,
                                                            material_id=material_id,
                                                            to_warehouse=warehouse_id,
                                                            origin_type='invoice',
                                                            origin_id=invoice_item_id,
                                                            commit=False,
                                                            record_only=True,
                                                            record_journal_entry=False)
                        warehouse_entry_id = self.database_operations.addMaterialToWarehouse(warehouse_id, material_id, quantity_to_add, unit1_id,production_date=production_date, expire_date=expire_date, material_move_id=material_move_id, commit=False)
                        if warehouse_entry_id:
                            self.database_operations.updateMaterialMove(
                                material_move_id,
                                to_warehouse_entry_id=warehouse_entry_id,
                                commit=False
                            )

                if invoice_effect_on_warehouse == 'reduce':
                    if self.invoice_id and self.ui.materials_table.item(row, 0).text() != '':
                        old_quantity = self.old_quantities[int(invoice_item_id)] + float(gifts)
                        new_quantity = float(quantity1) - float(old_quantity)
                        new_quantity = new_quantity + float(gifts)
                        if new_quantity > 0:
                            modified_records = self.database_operations.reduceMaterialInWarehouse(warehouse_id, material_id, new_quantity, unit1_id, order=output_way,commit=False)
                            for record in modified_records:
                                self.database_operations.moveMaterial(quantity=record['reduced_quantity'],
                                                            move_unit=record['unit'],
                                                            material_id=material_id,
                                                            from_warehouse=warehouse_id,
                                                            from_warehouse_entry_id=record['id'],
                                                            origin_type='invoice',
                                                            origin_id=invoice_item_id,
                                                            record_only=True,
                                                            commit=False,
                                                            record_journal_entry=False)
                        else:
                            quantity_to_add = -new_quantity
                            if float(quantity_to_add) > 0.0:
                                material_move_id = self.database_operations.moveMaterial(quantity=quantity_to_add, move_unit=unit1_id,
                                                                material_id=material_id,
                                                                to_warehouse=warehouse_id,
                                                                origin_type='invoice',
                                                                origin_id=invoice_item_id,
                                                                commit=False,
                                                                record_only=True,
                                                                record_journal_entry=False)
                                warehouse_entry_id = self.database_operations.addMaterialToWarehouse(warehouse_id, material_id, quantity_to_add, unit1_id, production_date=production_date, expire_date=expire_date, material_move_id=material_move_id, commit=False)
                                if warehouse_entry_id:
                                    self.database_operations.updateMaterialMove(
                                        material_move_id,
                                        to_warehouse_entry_id=warehouse_entry_id,
                                        commit=False
                                    )

                    else:
                        quantity_to_reduce = float(quantity1) + float(gifts)
                        modified_records = self.database_operations.reduceMaterialInWarehouse(warehouse_id, material_id, quantity_to_reduce, unit1_id, order=output_way, commit=False)
                        for record in modified_records:
                            self.database_operations.moveMaterial(quantity=record['reduced_quantity'],
                                                            move_unit=record['unit'],
                                                            material_id=material_id,
                                                            from_warehouse=warehouse_id,
                                                            from_warehouse_entry_id=record['id'],
                                                            origin_type='invoice',
                                                            origin_id=invoice_item_id,
                                                            record_only=True,
                                                            commit=False,
                                                            record_journal_entry=False)

        self.saveJournalEntry(invoice_id, invoice_type_name, invoice_type_category, inventory_type)

        for row in range(self.ui.discounts_additions_table.rowCount()):
            item_id = self.ui.discounts_additions_table.item(row, 0).text()
            account_id = self.ui.discounts_additions_table.item(row, 1).text()
            account = self.ui.discounts_additions_table.item(row, 2).text()
            type_col = self.ui.discounts_additions_table.item(row, 3).text()
            type_text = self.ui.discounts_additions_table.item(row, 4).text()
            currency_id = self.ui.discounts_additions_table.item(row, 5).text()
            currency = self.ui.discounts_additions_table.item(row, 6).text()
            exchange_id = self.ui.discounts_additions_table.item(row, 7).text()
            exchange = self.ui.discounts_additions_table.item(row, 8).text()
            equilivance_price = self.ui.discounts_additions_table.item(row, 9).text()
            cost_center_id = self.ui.discounts_additions_table.item(row, 10).text()
            cost_center = self.ui.discounts_additions_table.item(row, 11).text()
            opposite_account_id = self.ui.discounts_additions_table.item(row, 12).text()
            opposite_account = self.ui.discounts_additions_table.item(row, 13).text()

            percent = 0  # this variable is set to 1 if the discount/addition is in percent.
            # because we can't use the currency column in the invoices_discounts_additions table in db to
            # store the symbol '%' because of foreign key constrain.
            if currency_id == '%':
                currency_id = ''
                percent = 1

            if not cost_center_id or cost_center_id == None or cost_center_id == 'None':
                cost_center_id = ''
            if not exchange_id or exchange_id == None or exchange_id == 'None':
                exchange_id = ''
            # if not opposite_account_id or opposite_account_id == None or opposite_account_id == 'None':
            #     opposite_account_id = ''


            if item_id == '': # add new invoice discount/addition
                self.database_operations.addInvoiceDiscountAddition(invoice_id, account_id, type_col, cost_center_id,
                                                                currency_id, exchange_id, opposite_account_id,
                                                                equilivance_price, percent, commit=False)
            else: # update existing invoice discount/addition
                self.database_operations.updateInvoiceDiscountAddition(item_id, invoice_id, account_id, type_col, cost_center_id,
                                                                currency_id, exchange_id, opposite_account_id,
                                                                equilivance_price, percent, commit=False)

        self.sql_connector.conn.commit()
        window.accept()

    def saveJournalEntry(self, invoice_id, invoice_type_name, invoice_type_category, inventory_type):
        if self.ui.generate_journal_entry.isChecked():
            origin="invoice_"+str(invoice_type_name)
            added_value_account = self.ui.added_value_account_combobox.currentData()
            gifts_opposite_account = self.ui.gifts_opposite_account_combobox.currentData()
            cost_account = self.ui.cost_account_combobox.currentData()
            materials_account = self.ui.materials_account_combobox.currentData()
            stock_account = self.ui.stock_account_combobox.currentData()
            gifts_account = self.ui.gifts_account_combobox.currentData()
            monetary_account = self.ui.monetary_account_combobox.currentData()
            invoice_currency = self.ui.invoice_currency_combobox.currentData()
            invoice_cost_center_data = self.ui.invoice_cost_center_combobox.currentData()
            client_account = self.ui.client_account_combobox.currentData()
            payment_method = str(self.ui.payment_method_combobox.currentData()).lower()

            cost_center_id = None
            distributive_cost_centers_value = None
            if invoice_cost_center_data:
                invoice_cost_center_id = invoice_cost_center_data[0]
                invoice_cost_center_type = invoice_cost_center_data[1]

                distributive_cost_centers_value = []
                if invoice_cost_center_type in ('distributor'):
                    # fetch distributed cost centers
                    journal_entry_distributive_cost_center_centers = self.database_operations.fetchCostCenterAggregationsDistributives(
                        invoice_cost_center_id)
                    if journal_entry_distributive_cost_center_centers:
                        for journal_entry_distributive_cost_center_account in journal_entry_distributive_cost_center_centers:
                            cost_centers_aggregations_distributive_enty_id = journal_entry_distributive_cost_center_account[0]
                            division_factor = journal_entry_distributive_cost_center_account[3]
                            # master_cost_center_id = journal_entry_distributive_cost_center_account[1]
                            # distributed_cost_center_name = journal_entry_distributive_cost_center_account[4]
                            # distributed_cost_center_id = journal_entry_distributive_cost_center_account[2]

                            distributive_cost_centers_value.append([cost_centers_aggregations_distributive_enty_id, division_factor])

                if not distributive_cost_centers_value:
                    distributive_cost_centers_value = None

            else:
                invoice_cost_center_id = None
                distributive_cost_centers_value = None

            partial_sum = self.ui.partial_sum.text()

            date = self.ui.date_input.text()

            journal_entry_id = None

            if self.invoice_id: # check if the journal entry is already generated for this invoice
                journal_entry = self.database_operations.fetchInvoiceJournalEntry(invoice_id)
                if journal_entry:
                    journal_entry_id = journal_entry[-1]['id']  # Fetch last journal entry for the invoice
                    self.database_operations.updateJournalEntry(journal_entry_id, currency=invoice_currency, commit=False)

                    # Delete all journal entry items for the invoice, then re-generate new ones for same journal entry
                    self.database_operations.removeJournalEntriesItems(journal_entry_id, commit=False)

            else: # add new invoice journal entry
                journal_entry_id = self.database_operations.addJournalEntry(date, invoice_currency,
                                                                            origin_type=origin,
                                                                            origin_id=invoice_id, commit=False)

            for row in range(self.ui.materials_table.rowCount()):
                stock_value = 0
                material = None

                # id = self.ui.materials_table.item(row, 0).text()
                # material_id = self.ui.materials_table.item(row, 1).text()
                material = self.ui.materials_table.item(row, 2).text()
                quantity_1 = self.ui.materials_table.item(row, 3).text()
                currency_id = self.ui.materials_table.item(row, 15).text()
                discount = self.ui.materials_table.item(row, 22).text()
                material_discount_account = self.ui.materials_table.item(row, 24).text()
                addition = self.ui.materials_table.item(row, 26).text()
                material_addition_account = self.ui.materials_table.item(row, 28).text()
                added_value = self.ui.materials_table.item(row, 30).text()
                gifts = self.ui.materials_table.item(row, 31).text()
                gifts_value = self.ui.materials_table.item(row, 32).text()
                unit_price_equilivance = self.ui.materials_table.item(row, 17).text()
                gift_discount = self.ui.materials_table.item(row, 33).text()
                warehouse_account_id = self.ui.materials_table.item(row, 39).text()
                # gifts = self.ui.materials_table.item(row, 31).text()
                # unit_1_id = self.ui.materials_table.item(row, 4).text()
                # unit_1 = self.ui.materials_table.item(row, 5).text()
                # quantity_2 = self.ui.materials_table.item(row, 6).text()
                # unit_2_id = self.ui.materials_table.item(row, 7).text()
                # unit_2 = self.ui.materials_table.item(row, 8).text()
                # quantity_3 = self.ui.materials_table.item(row, 9).text()
                # unit_3_id = self.ui.materials_table.item(row, 10).text()
                # unit_3 = self.ui.materials_table.item(row, 11).text()
                # pricing_id = self.ui.materials_table.item(row, 12).text()
                # pricing = self.ui.materials_table.item(row, 13).text()
                # unit_price = self.ui.materials_table.item(row, 14).text()
                # currency = self.ui.materials_table.item(row, 16).text()
                # currency_id = self.ui.materials_table.item(row, 18).text()
                # currency = self.ui.materials_table.item(row, 19).text()
                # exchange_rate_id = self.ui.materials_table.item(row, 20).text()
                # exchange_rate = self.ui.materials_table.item(row, 21).text()
                # discount_percentage = self.ui.materials_table.item(row, 23).text()
                # discount_account_name = self.ui.materials_table.item(row, 25).text()
                # addition_percentage = self.ui.materials_table.item(row, 27).text()
                # addition_account_name = self.ui.materials_table.item(row, 29).text()
                # warehouse = self.ui.materials_table.item(row, 35).text()
                # cost_center_id = self.ui.materials_table.item(row, 36).text()
                # cost_center = self.ui.materials_table.item(row, 37).text()
                # notes = self.ui.materials_table.item(row, 38).text()

                try:
                    if materials_account:
                        value = float(unit_price_equilivance) * float(quantity_1)
                        value = round(value, 2)
                        stock_value += value

                        account = None
                        opposite_account = None
                        if invoice_type_category == 'input':
                            if payment_method == 'cash':
                                account = monetary_account
                                opposite_account = materials_account
                            elif payment_method == 'postponed':
                                account = client_account
                                opposite_account = materials_account
                        elif invoice_type_category == 'output':
                            if payment_method == 'cash':
                                account = materials_account
                                opposite_account = monetary_account
                            elif payment_method == 'postponed':
                                account = materials_account
                                opposite_account = client_account

                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                    str(invoice_type_name) + " " + str(material),
                                                                    account, opposite_account, value,
                                                                    invoice_cost_center_id,
                                                                    distributive_cost_centers_value, commit=False)

                    # الاضافات على البند
                    addition_value = float(addition) if addition is not None and addition != '' else None
                    if addition_value:
                        addition_value = round(addition_value, 2)
                        stock_value += addition_value

                        account = None
                        opposite_account = None
                        if invoice_type_category == 'input':
                                account = client_account
                                opposite_account = material_addition_account
                        elif invoice_type_category == 'output':
                                account = material_addition_account
                                opposite_account = client_account

                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                f"{self.language_manager.translate('ADDITION')} " + str(material),
                                                                account,
                                                                opposite_account, addition_value,
                                                                invoice_cost_center_id,
                                                                distributive_cost_centers_value, commit=False)


                    # الحسومات على البند
                    discount = float(discount) if discount is not None and discount != '' else None
                    if discount:
                        discount = round(discount, 2)
                        stock_value -= discount

                        account = None
                        opposite_account = None
                        if invoice_type_category == 'input':
                                account = material_discount_account
                                opposite_account = client_account
                        elif invoice_type_category == 'output':
                                account = client_account
                                opposite_account = material_discount_account

                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                f"{self.language_manager.translate('DISCOUNT')} " + str(material),
                                                                account, opposite_account, discount,
                                                                invoice_cost_center_id,
                                                                distributive_cost_centers_value, commit=False)


                    # حسم الهدايا
                    gifts_discount = float(gift_discount) if gift_discount is not None and gift_discount != '' else None
                    if gifts_discount:
                        if gifts_account != None:

                            gifts_discount = round(gifts_discount, 2)
                            stock_value -= gifts_discount

                            account = None
                            opposite_account = None
                            if invoice_type_category == 'input':
                                    account = gifts_account
                                    opposite_account = client_account
                            elif invoice_type_category == 'output':
                                    account = client_account
                                    opposite_account = gifts_account

                            self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                    f"{self.language_manager.translate('GIFTS_DISCOUNT')} " + str(material),
                                                                    account, opposite_account, gifts_discount,
                                                                    invoice_cost_center_id,
                                                                    distributive_cost_centers_value, commit=False)
                        else:
                            win32api.MessageBox(0, self.language_manager.translate("GIFTS_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
                            return

                    # الهدايا
                    gifts = float(gifts) if gifts is not None and gifts != '' else None
                    if gifts:

                        gifts_value = self.ui.material_gifts_value_input.text()
                        gifts_value = float(gifts_value) if gifts_value is not None and gifts_value != '' else None
                        if gifts_value:
                            gifts_value = round(gifts_value, 2)
                        else:
                            gifts_value = 0

                        stock_value -= gifts_value

                        account = None
                        opposite_account = None
                        account = gifts_account
                        if gifts_opposite_account:
                            opposite_account = gifts_opposite_account
                        else:
                            if warehouse_account_id:
                                opposite_account = warehouse_account_id
                            else:
                                win32api.MessageBox(0, self.language_manager.translate("GIFTS_OPPOSITE_ACCOUNT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
                                return

                        if invoice_type_category == 'output':
                            temp_account = account
                            account = opposite_account
                            opposite_account = temp_account

                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                    f"{self.language_manager.translate('GIFTS')} " + str(material),
                                                                    account, opposite_account,
                                                                    gifts_value, invoice_cost_center_id,
                                                                    distributive_cost_centers_value, commit=False)

                    # القيمة المضافة
                    added_value = float(added_value) if added_value is not None and added_value != '' else None
                    if added_value:
                        added_value = round(added_value, 2)

                        stock_value += added_value

                        added_value_account = self.ui.added_value_account_combobox.currentData()

                        account = None
                        opposite_account = None
                        if invoice_type_category == 'input':
                            if payment_method == 'cash':
                                account = added_value_account if added_value_account else monetary_account
                                opposite_account = client_account
                            elif payment_method == 'postponed':
                                account = added_value_account if added_value_account else materials_account
                                opposite_account = client_account
                        elif invoice_type_category == 'output':
                            if payment_method == 'cash':
                                account = client_account
                                opposite_account = added_value_account if added_value_account else monetary_account
                            elif payment_method == 'postponed':
                                account = client_account
                                opposite_account = added_value_account if added_value_account else materials_account

                        self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                f"{self.language_manager.translate('ADDED_VALUE')} " + str(material), account,
                                                                opposite_account, added_value,
                                                                invoice_cost_center_id,
                                                                distributive_cost_centers_value, commit=False)

                    if inventory_type == 'perpetual' and stock_account and cost_account and stock_value and material:
                        stock_value = round(stock_value, 2)

                        if invoice_type_category == 'input':
                            self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                             f"{self.language_manager.translate('STOCK')} " + str(material), client_account, stock_account,
                                                             stock_value, invoice_cost_center_id,
                                                             distributive_cost_centers_value, commit=False)

                        elif invoice_type_category == 'output':
                            self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                             f"{self.language_manager.translate('STOCK')} " + str(material), stock_account, cost_account,
                                                             stock_value, invoice_cost_center_id,
                                                             distributive_cost_centers_value, commit=False)

                except Exception as e:
                    print(str(e))

            for row in range(self.ui.discounts_additions_table.rowCount()):
                discount_addition_account_id = self.ui.discounts_additions_table.item(row, 1).text()
                type = self.ui.discounts_additions_table.item(row, 3).text()
                currency_id = self.ui.discounts_additions_table.item(row, 5).text()
                value = self.ui.discounts_additions_table.item(row, 9).text()
                discount_addition_opposite_account_id = self.ui.discounts_additions_table.item(row, 12).text()
                # id = self.ui.discounts_additions_table.item(row, 0).text()
                # account = self.ui.discounts_additions_table.item(row, 2).text()
                # type_text = self.ui.discounts_additions_table.item(row, 4).text()
                # currency = self.ui.discounts_additions_table.item(row, 6).text()
                # exchange_rate_id = self.ui.discounts_additions_table.item(row, 7).text()
                # exchange_rate = self.ui.discounts_additions_table.item(row, 8).text()
                # cost_center_id = self.ui.discounts_additions_table.item(row, 10).text()
                # cost_center = self.ui.discounts_additions_table.item(row, 11).text()
                # opposite_account = self.ui.discounts_additions_table.item(row, 13).text()

                try:
                    value = float(value) if value is not None and value != '' else None
                    if value:
                        number = self.ui.number_input.text()
                        if type == 'discount':
                            stock_value -= value
                            self.database_operations.addJournalEntryItem(journal_entry_id, currency_id, 'creditor',
                                                                         f"{self.language_manager.translate('DISCOUNT')} {self.language_manager.translate('FOR_INVOICE')} " + str(number),
                                                                         discount_addition_opposite_account_id,
                                                                         discount_addition_account_id, value,
                                                                         invoice_cost_center_id,
                                                                         distributive_cost_centers_value,
                                                                         commit=False)

                        elif type == 'addition':
                            stock_value += value
                            self.database_operations.addJournalEntryItem(journal_entry_id, invoice_currency, 'creditor',
                                                                         f"{self.language_manager.translate('ADDITION')} {self.language_manager.translate('FOR_INVOICE')} " + str(number),
                                                                         discount_addition_opposite_account_id,
                                                                         discount_addition_account_id, value,
                                                                         invoice_cost_center_id,
                                                                         distributive_cost_centers_value,
                                                                         commit=False)

                except Exception as e:
                    print(str(e))
