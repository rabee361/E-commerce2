import win32api
from PyQt5.QtGui import QDoubleValidator, QIntValidator
from PyQt5.QtWidgets import QDialog, QAbstractItemView, QTableWidgetItem, QHeaderView
from win32con import MB_YESNO, IDYES, IDNO, MB_OKCANCEL, IDCANCEL
from datetime import datetime
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_ClientAccounts import Ui_ClientAccounts
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

# Clinet Account (This) contains the info related to payments of a client.
# these info includes (Client Account ID) which points to the ID of the (Account) of the
# current client in (accounts) table

class Ui_ClientAccounts_Logic(QDialog):
    def __init__(self, sql_connector, client_id=None, id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

        self.client_id = client_id
        self.id = id

        self.ui = Ui_ClientAccounts()

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window):
        self.ui.payment_conditions_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.payment_conditions_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.payment_conditions_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.payment_conditions_table.verticalHeader().hide()
        self.ui.payment_conditions_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.payment_conditions_table.setColumnHidden(0, True)

        self.ui.payment_date_input.setDisplayFormat("dd-MM-yyyy")

        self.ui.discount_input.setValidator(QIntValidator())
        self.ui.current_balance_input.setValidator(QDoubleValidator())  # TODO
        self.ui.discount_percent_input.setValidator(QDoubleValidator())
        self.ui.day_number_input.setValidator(QIntValidator())
        self.ui.discount_value_input.setValidator(QDoubleValidator())
        self.ui.days_count_input.setValidator(QDoubleValidator())

        weekdays = {"sat": "السبت", "sun": "الأحد", "mon": "الاثنين", "tue": "الثلاثاء", "wed": "الاربعاء",
                    "thu": "الخميس", "fri": "الجمعة"}
        for day in weekdays:
            self.ui.day_combobox.addItem(str(weekdays[day]), str(day))

        self.fetchPricesTypes()
        self.fetchAccounts()
        self.fetchClientAccount()
        self.applyPaymentDatesConditions()

        self.ui.payment_method_combobox.activated.connect(lambda: self.applyPaymentDatesConditions())
        self.ui.add_payment_condition_btn.clicked.connect(lambda: self.addPaymentCondition())
        self.ui.delete_payment_condition_btn.clicked.connect(lambda: self.removePaymentCondition())
        self.ui.save_btn.clicked.connect(lambda: self.saveClientAccount(window))

        self.ui.client_account_combobox.setDisabled(True)
        self.ui.client_extra_account_combobox.setDisabled(True)
        self.ui.discount_account_combobox.setDisabled(True)
        self.ui.vat_account_combobox.setDisabled(True)
        self.ui.tax_account_combobox.setDisabled(True)
        self.ui.condition_discount_account_combobox.setDisabled(True)

        self.ui.select_client_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.client_account_combobox))
        self.ui.select_client_extra_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.client_extra_account_combobox))
        self.ui.select_client_discount_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.discount_account_combobox))
        self.ui.select_vat_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.vat_account_combobox))
        self.ui.select_tax_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.tax_account_combobox))
        self.ui.select_condition_discount_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.condition_discount_account_combobox))


    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result:
            for index in range(combobox.count()):
                item_data = combobox.itemData(index)
                if item_data and item_data[0] == result['id']:
                    combobox.setCurrentIndex(index)
                    break


    def fetchClientAccount(self):
        client_account = self.database_operations.fetchClient(self.client_id)
        if client_account:
            self.client_id = client_account['id']
            name = client_account['name']    
            governorate = client_account['governorate']
            address = client_account['address']

        self.ui.name_input.setText(str(name))
        self.ui.address_input.setText(str(governorate) + "-" + str(address))

        if len(client_account) > 4:
            self.id = client_account['clients_accounts_id']
            used_price = client_account['used_price']
            discount = client_account['discount']
            payment_method = client_account['payment_method']
            days_count = client_account['days_count']
            day = client_account['day_col']
            payment_date = client_account['payment_date']
            client_account_id = client_account['client_account_id']
            client_extra_account_id = client_account['extra_account_id']
            discount_account_id = client_account['discount_account_id']
            tax_account_id = client_account['tax_account_id']
            vat_account_id = client_account['vat_account_id']
            tax_exemption = client_account['tax_exempt']

            if str(discount).lower()=='none':
                discount=''
            if str(days_count).lower()=='none':
                days_count=''
            if str(day).lower()=='none':
                day=''

            self.ui.used_price_combobox.setCurrentIndex(self.ui.used_price_combobox.findData(used_price))
            self.ui.discount_input.setText(str(discount))
            self.ui.payment_method_combobox.setCurrentIndex(self.ui.payment_method_combobox.findText(payment_method))
            self.ui.days_count_input.setText(str(days_count))
            self.ui.day_combobox.setCurrentIndex(self.ui.day_combobox.findData(day))
            payment_date_object = datetime.strptime(str(payment_date if payment_date else '2000-01-01'), '%Y-%m-%d')
            self.ui.payment_date_input.setDate(payment_date_object)


            for index in range(self.ui.client_account_combobox.count()):
                item_data = self.ui.client_account_combobox.itemData(index)
                if item_data and item_data[0] == client_account_id:
                    self.ui.client_account_combobox.setCurrentIndex(index)
                    break

            for index in range(self.ui.client_extra_account_combobox.count()):
                item_data = self.ui.client_extra_account_combobox.itemData(index)
                if item_data and item_data[0] == client_extra_account_id:
                    self.ui.client_extra_account_combobox.setCurrentIndex(index)
                    break

            for index in range(self.ui.discount_account_combobox.count()):
                item_data = self.ui.discount_account_combobox.itemData(index)
                if item_data and item_data[0] == discount_account_id:
                    self.ui.discount_account_combobox.setCurrentIndex(index)
                    break

            for index in range(self.ui.tax_account_combobox.count()):
                item_data = self.ui.tax_account_combobox.itemData(index)
                if item_data and item_data[0] == tax_account_id:
                    self.ui.tax_account_combobox.setCurrentIndex(index)
                    break

            for index in range(self.ui.vat_account_combobox.count()):
                item_data = self.ui.vat_account_combobox.itemData(index)
                if item_data and item_data[0] == vat_account_id:
                    self.ui.vat_account_combobox.setCurrentIndex(index)
                    break

            self.ui.tax_exemption_checkbox.setChecked(True) if tax_exemption==1 else self.ui.tax_exemption_checkbox.setChecked(False)
            self.fetchPaymentConditions()

    def fetchPricesTypes(self):
        prices_types = self.database_operations.fetchPricesTypes()
        self.ui.used_price_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), None)
        for price_type in prices_types:
            id = price_type[0]
            value = price_type[1]
            self.ui.used_price_combobox.addItem(value, id)

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()

        self.ui.client_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])
        self.ui.client_extra_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])
        self.ui.discount_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])
        self.ui.condition_discount_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])
        self.ui.tax_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])
        self.ui.vat_account_combobox.addItem(self.language_manager.translate("NOT_SPECIFIED"), [None, None])

        for account in accounts:
            id = account[0]
            name = account[1]
            final_account = account[8]
            data = [id, final_account]
            self.ui.client_account_combobox.addItem(name, data)
            self.ui.client_extra_account_combobox.addItem(name, data)
            self.ui.discount_account_combobox.addItem(name, data)
            self.ui.condition_discount_account_combobox.addItem(name, data)
            self.ui.tax_account_combobox.addItem(name, data)
            self.ui.vat_account_combobox.addItem(name, data)

    def saveClientAccount(self , window):
        # read values
        id = self.id
        used_price = self.ui.used_price_combobox.currentData()
        discount = self.ui.discount_input.text()
        payment_method = self.ui.payment_method_combobox.currentText()
        days_count = self.ui.days_count_input.text()
        day = self.ui.day_combobox.currentData()
        payment_date = self.ui.payment_date_input.text()
        client_account_id = self.ui.client_account_combobox.currentData()[0]
        client_account_final_account = self.ui.client_account_combobox.currentData()[1]
        client_extra_account_id = self.ui.client_extra_account_combobox.currentData()[0]
        client_extra_account_final_account = self.ui.client_extra_account_combobox.currentData()[1]
        discount_account_id = self.ui.discount_account_combobox.currentData()[0]
        discount_account_final_account = self.ui.discount_account_combobox.currentData()[1]
        tax_account_id = self.ui.tax_account_combobox.currentData()[0]
        tax_account_final_account = self.ui.tax_account_combobox.currentData()[1]
        vat_account_id = self.ui.vat_account_combobox.currentData()[0]
        vat_account_final_account = self.ui.vat_account_combobox.currentData()[1]
        tax_exemption = 1 if self.ui.tax_exemption_checkbox.isChecked() else 0
        client_id = self.client_id

        if str(used_price).lower() == 'none':
            used_price = ''
        if str(discount).lower() == 'none':
            discount = ''
        if str(payment_method).lower() == 'none':
            payment_method = ''
        if str(days_count).lower() == 'none':
            days_count = ''
        if str(day).lower() == 'none':
            day = ''
        if str(payment_date).lower() == 'none':
            payment_date = ''
        if str(client_account_id).lower() == 'none':
            client_account_id = ''
        if str(client_extra_account_id).lower() == 'none':
            client_extra_account_id = ''
        if str(discount_account_id).lower() == 'none':
            discount_account_id = ''
        if str(tax_account_id).lower() == 'none':
            tax_account_id = ''
        if str(vat_account_id).lower() == 'none':
            vat_account_id = ''
        if str(client_id).lower() == 'none':  # should never occur
            client_id = ''
        if str(client_account_final_account).lower() == 'none':
            client_account_final_account=''
        if str(client_extra_account_final_account).lower() == 'none':
            client_extra_account_final_account=''
        if str(discount_account_final_account).lower() == 'none':
            discount_account_final_account=''
        if str(tax_account_final_account).lower() == 'none':
            tax_account_final_account=''
        if str(vat_account_final_account).lower() == 'none':
            vat_account_final_account=''

        # check if a sub-account need to be created
        client_name = self.database_operations.fetchClient(client_id)['name']  # Client_id is never None because it is always fetched once this window is opened.
        if self.ui.client_account_create_subaccount_checkbox.isChecked():
            client_account_parent_id = client_account_id
            client_account_name = self.language_manager.translate("CLIENT_ACCOUNT") + " " + client_name
            client_account_id = self.database_operations.addAccount(client_account_name, '', client_account_parent_id,'normal', client_account_final_account, '', '')  # The financial account

        if self.ui.client_extra_account_create_subaccount_checkbox.isChecked():
            client_extra_account_parent_id = client_extra_account_id
            client_extra_account_name = self.language_manager.translate("EXTRA_ACCOUNT") + " " + client_name
            client_extra_account_id = self.database_operations.addAccount(client_extra_account_name, '', client_extra_account_parent_id,'normal', client_extra_account_final_account, '', '')  # The financial account

        if self.ui.discount_account_create_subaccount_checkbox.isChecked():
            discount_account_parent_id = discount_account_id
            discount_account_name = self.language_manager.translate("DISCOUNT_ACCOUNT") + " " + client_name
            discount_account_id = self.database_operations.addAccount(discount_account_name, '',
                                                                      discount_account_parent_id,'normal', discount_account_final_account, '', '')

        if self.ui.vat_account_create_subaccount_checkbox.isChecked():
            vat_account_parent_id = vat_account_id
            vat_account_name = self.language_manager.translate("VAT_ACCOUNT") + " " + client_name
            vat_account_id = self.database_operations.addAccount(vat_account_name, '', vat_account_parent_id,'normal', vat_account_final_account, '', '')

        if self.ui.tax_account_create_subaccount_checkbox.isChecked():
            tax_account_parent_id = tax_account_id
            tax_account_name = self.language_manager.translate("TAX_ACCOUNT") + " " + client_name
            tax_account_id = self.database_operations.addAccount(tax_account_name, '', tax_account_parent_id,'normal', tax_account_final_account, '', '')

        id = self.database_operations.addClientAccount(used_price, discount, payment_method, days_count, day,payment_date, client_account_id, discount_account_id, tax_account_id,vat_account_id, tax_exemption, client_id, client_extra_account_id)
        window.accept()
        return id

    def addPaymentCondition(self):
        day_number = self.ui.day_number_input.text()
        discount_percent = self.ui.discount_percent_input.text()
        discount_value = self.ui.discount_value_input.text()
        condition_discount_account = self.ui.condition_discount_account_combobox.currentData()[0] # can this be None ?
        if self.id:
            if day_number:
                self.database_operations.addPaymentCondition(self.id, day_number,
                                                             discount_percent, discount_value,
                                                             condition_discount_account)
        else:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("ADD_PAYMENT_CONDITION_MESSAGE"),
                                                    self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                self.id = self.saveClientAccount()
                if (self.id):
                    if day_number:
                        self.database_operations.addPaymentCondition(self.id, day_number,
                                                                     discount_percent, discount_value,
                                                                     condition_discount_account)
                    else:
                        win32api.MessageBox(0, self.language_manager.translate("INVALID_DAYS_NUMBER"), self.language_manager.translate("ERROR"))

            if (messagebox_result == IDNO):
                pass

        self.ui.day_number_input.setText('')
        self.ui.discount_percent_input.setText('')
        self.ui.discount_value_input.setText('')
        self.ui.condition_discount_account_combobox.setCurrentIndex(self.ui.condition_discount_account_combobox.findData(self.language_manager.translate("NOT_SPECIFIED")))
    
        self.fetchPaymentConditions()

    def fetchPaymentConditions(self):
        payment_conditions = self.database_operations.fetchPaymentConditions(self.id)
        self.ui.payment_conditions_table.setRowCount(0)
        for payment_condition in payment_conditions:
            discount_account_name = payment_condition[0]
            payment_condition_id = payment_condition[1]
            client_account_id = payment_condition[2]
            day_number = payment_condition[3]
            discount_percent = payment_condition[4]
            discount_value = payment_condition[5]
            discount_account_id = payment_condition[6]

            numRows = self.ui.payment_conditions_table.rowCount()
            self.ui.payment_conditions_table.insertRow(numRows)
            # Add text to the row
            self.ui.payment_conditions_table.setItem(numRows, 0,
                                                     MyTableWidgetItem(str(payment_condition_id), payment_condition_id))
            self.ui.payment_conditions_table.setItem(numRows, 1, QTableWidgetItem(str(day_number)))
            self.ui.payment_conditions_table.setItem(numRows, 2,
                                                     MyTableWidgetItem(str(discount_percent), discount_percent))
            self.ui.payment_conditions_table.setItem(numRows, 3, MyTableWidgetItem(str(discount_value), discount_value))
            self.ui.payment_conditions_table.setItem(numRows, 4, QTableWidgetItem(str(discount_account_name)))

    def applyPaymentDatesConditions(self):
        payment_method = self.ui.payment_method_combobox.currentText()
        if payment_method == self.language_manager.translate("AFTER_DAYS") or payment_method == self.language_manager.translate("AFTER_MONTH_DAY") or payment_method == self.language_manager.translate("AFTER_MONTH_DAY_NEXT"):
            self.ui.payment_date_input.setDisabled(True)
            self.ui.days_count_input.setEnabled(True)
            self.ui.day_combobox.setDisabled(True)
            self.ui.payment_conditions_conditions_groupbox.setEnabled(True)
        elif payment_method == self.language_manager.translate("AFTER_WEEK_DAY") or payment_method == self.language_manager.translate("AFTER_WEEK_DAY_NEXT"):
            self.ui.payment_date_input.setDisabled(True)
            self.ui.days_count_input.setDisabled(True)
            self.ui.day_combobox.setEnabled(True)
            self.ui.payment_conditions_conditions_groupbox.setEnabled(True)
        elif payment_method == self.language_manager.translate("AFTER_DATE"):
            self.ui.payment_date_input.setEnabled(True)
            self.ui.days_count_input.setDisabled(True)
            self.ui.day_combobox.setDisabled(True)
            self.ui.payment_conditions_conditions_groupbox.setEnabled(True)
        elif payment_method == self.language_manager.translate("AFTER_MONTH_DAY") or payment_method == self.language_manager.translate("AFTER_MONTH_DAY_NEXT"):
            self.ui.payment_date_input.setDisabled(True)
            self.ui.days_count_input.setDisabled(True)
            self.ui.day_combobox.setDisabled(True)
            self.ui.payment_conditions_conditions_groupbox.setEnabled(True)
        else:
            self.ui.payment_date_input.setDisabled(True)
            self.ui.days_count_input.setDisabled(True)
            self.ui.day_combobox.setDisabled(True)
            self.ui.payment_conditions_conditions_groupbox.setDisabled(True)

    def removePaymentCondition(self):
        if self.ui.payment_conditions_table.selectedItems():
            confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("CONFIRM"), MB_OKCANCEL)
            if confirm == IDCANCEL:
                pass
            else:
                table_row = self.ui.payment_conditions_table.item(self.ui.payment_conditions_table.currentRow(), 0)
                if (str(type(table_row)) == "<class 'NoneType'>"):
                    pass
                else:
                    payment_condition_id = table_row.text()
                    self.database_operations.removePaymenCondition(payment_condition_id)
                    self.fetchPaymentConditions()
        else:
            win32api.MessageBox(0, self.language_manager.translate("NO_PAYMENT_CONDITION_SELECTED"), self.language_manager.translate("ERROR"))
            self.fetchPaymentConditions()   
