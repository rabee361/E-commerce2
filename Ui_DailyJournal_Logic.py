from PyQt5.QtWidgets import QDialog, QTreeWidgetItem , QSizePolicy, QCheckBox, QPushButton, QVBoxLayout, QGridLayout, QFrame
import Colors
from DatabaseOperations import DatabaseOperations
from Ui_DailyJournal import Ui_DailyJournal
from PyQt5.QtCore import Qt, QDate
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon


class Ui_DailyJournal_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_DailyJournal()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

        # Save selected invoices
        self.selected_invoices = {}
        self.include_invoices_payments = True

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/business-report.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        window.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window.setWindowState(Qt.WindowMaximized)
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.fetchCurrencies()
        self.ui.calculate_btn.clicked.connect(lambda: self.calculate())
        self.ui.to_date_input.setDate(QDate.currentDate())

        self.fetchInvoiceTypes()
        self.ui.select_invoices_btn.clicked.connect(lambda: self.openSelectInvoicesWindow())

    def fetchInvoiceTypes(self):
        invoice_types = self.database_operations.fetchInvoiceTypes()
        for invoice_type in invoice_types:
            self.selected_invoices[invoice_type['name']] = True

    def openSelectInvoicesWindow(self):
        # Create dialog to select invoice types
        dialog = QDialog(self)
        dialog.setLayoutDirection(Qt.RightToLeft)
        dialog.setWindowTitle(self.language_manager.translate("SELECT_INVOICES"))
        dialog.setFixedWidth(300)
        dialog.setModal(True)
        
        # Get invoice types from database
        invoice_types = self.database_operations.fetchInvoiceTypes()
        
        # Create checkboxes dynamically based on invoice types
        checkboxes = []
        layout = QVBoxLayout()
        
        # Create grid layout for checkboxes
        grid_layout = QGridLayout()
        row = 0
        col = 0
        for i, invoice_type in enumerate(invoice_types):
            invoice_type_name = invoice_type['name']
            checkbox = QCheckBox(invoice_type_name)
            checkbox.setChecked(True)
            if self.selected_invoices:
                if not invoice_type_name in self.selected_invoices.keys():
                    checkbox.setChecked(False)
            grid_layout.addWidget(checkbox, row, col)
            checkboxes.append(checkbox)
            col += 1
            if col == 3:  # After 3 columns, move to next row
                col = 0
                row += 1
        
        # Add grid layout to main layout
        layout.addLayout(grid_layout)

        # Add separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Add checkbox below separator
        include_payments_checkbox = QCheckBox(self.language_manager.translate("INCLUDE_INVOICES_PAYMENTS"))
        include_payments_checkbox.setChecked(True if self.include_invoices_payments else False)
        layout.addWidget(include_payments_checkbox)
            
        # Add OK button
        ok_button = QPushButton(self.language_manager.translate("OK"))
        ok_button.clicked.connect(dialog.accept)
        layout.addWidget(ok_button)
        
        dialog.setLayout(layout)
        
        # Show dialog and get result
        if dialog.exec_() == QDialog.Accepted:
            # Clear previous selections
            self.selected_invoices = {}
            
            # Add checked invoice types to selected_invoices
            for checkbox in checkboxes:
                if checkbox.isChecked():
                    self.selected_invoices[checkbox.text()] = True
                
            if include_payments_checkbox.isChecked():
                self.include_invoices_payments = True
            else:
                self.include_invoices_payments = False

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            self.ui.currency_combobox.addItem(name, id)

    def calculate(self, targeted_currency=None, from_date=None, to_date=None):
        self.ui.results_tree.clear()
        self.ui.debtors_sum_tree.clear()
        self.ui.creditors_sum_tree.clear()

        from_date = self.ui.from_date_input.date().toString(Qt.ISODate)
        to_date = self.ui.to_date_input.date().toString(Qt.ISODate)

        unified_currency = self.ui.unified_currency_radio.isChecked()
        unified_exchange_date = self.ui.unified_exchange_date_radio.isChecked()
        targeted_currency = self.ui.currency_combobox.currentData()
        targeted_currency_name = self.ui.currency_combobox.currentText()
        exchange_date = self.ui.exchange_date_input.date()
        distinct_currency = self.ui.distinct_currency_radio.isChecked()

        data_sources = []

        # Updated checkbox names
        checkbox_names = ["source_period_start_checkbox", "source_period_start_material_checkbox",
                          "source_journal_checkbox"]

        for checkbox_name in checkbox_names:
            checkbox = getattr(self.ui, checkbox_name)
            if checkbox.isChecked():
                # Extract the relevant part of the checkbox name
                extracted_name = checkbox_name.replace("source_", "").replace("_checkbox", "")
                data_sources.append(extracted_name)

        for key, value in self.selected_invoices.items():
            if value:
                data_sources.append('invoice_' + key)

        if self.include_invoices_payments:
            data_sources.append('invoice_payment')
            data_sources.append('extra_payment')

        if self.ui.source_manufacture_checkbox.isChecked():
            data_sources.append('manufacture')
            
        if self.ui.source_loans_checkbox.isChecked():
            data_sources.append('loan')
            data_sources.append('loan_payment') 

        records_dict, debtors_sum_dict, creditors_sum_dict = self.calculateLogic(from_date, to_date, targeted_currency,
                                                                                 unified_currency,
                                                                                 targeted_currency_name,
                                                                                 unified_exchange_date, exchange_date,
                                                                                 distinct_currency, data_sources)



        for journal_entry_id, journal_entry_records in records_dict.items():
            root_item = QTreeWidgetItem([str(journal_entry_id),"","","","","","",""])
            for i in range(root_item.columnCount()):
                root_item.setBackground(i, Colors.dark_yellow_color)
            for journal_entry_record in journal_entry_records:
                account_id, account_name, value, currency, currency_name, journal_entry_date, journal_entry_type, opposite_account_id, opposite_account_name, statement, journal_entry_item_id, origin_type, origin_id = journal_entry_record

                child_item = QTreeWidgetItem(["", str(journal_entry_item_id), str(origin_type), str(account_name),
                                              (str(value) if str(journal_entry_type).lower() == 'creditor' else ""),
                                              (str(value) if str(journal_entry_type).lower() == 'debtor' else ""),
                                              str(currency), str(currency_name), str(statement)])

                for i in range(child_item.columnCount()):
                    child_item.setBackground(i, Colors.light_yellow_color)

                root_item.addChild(child_item)
                self.ui.results_tree.addTopLevelItem(root_item)

        for currency_data, value in debtors_sum_dict.items():
            currency_id = currency_data[0]
            currency_name = currency_data[1]

            root_item = QTreeWidgetItem([str(currency_id),str(currency_name),str(value)])
            self.ui.debtors_sum_tree.addTopLevelItem(root_item)

        for currency_data, value in creditors_sum_dict.items():
            currency_id = currency_data[0]
            currency_name = currency_data[1]

            root_item = QTreeWidgetItem([str(currency_id),str(currency_name),str(value)])
            self.ui.creditors_sum_tree.addTopLevelItem(root_item)


    def calculateLogic(self, from_date, to_date, targeted_currency, unified_currency, targeted_currency_name,
                       unified_exchange_date, exchange_date, distinct_currency, data_sources):

        records_dict = {}

        journal_entry_items = self.database_operations.fetchJournalEntryItems(from_date=from_date, to_date=to_date,
                                                                              sources=data_sources)

        for journal_entry_item in journal_entry_items:
            journal_entry_item_id = journal_entry_item['id']
            journal_entry_id = journal_entry_item['journal_entry_id']
            account_id = journal_entry_item['account_id']
            statement = journal_entry_item['statement_col']
            currency = journal_entry_item['currency']
            opposite_account_id = journal_entry_item['opposite_account_id']
            journal_entry_type = journal_entry_item['type_col']
            value = journal_entry_item['value_col']
            cost_center_id = journal_entry_item['cost_center_id']
            currency_name = journal_entry_item['currency_name']
            account_name = journal_entry_item['account_name']
            opposite_account_name = journal_entry_item['opposite_account_name']
            journal_entry_date = journal_entry_item['entry_date']
            origin_type = journal_entry_item['origin_type']
            origin_id = journal_entry_item['origin_id']

            record = [account_id, account_name, value, currency, currency_name, journal_entry_date, journal_entry_type,
                      opposite_account_id, opposite_account_name, statement, journal_entry_item_id, origin_type, origin_id]

            if journal_entry_id in records_dict:
                records_dict[journal_entry_id].append(record)
            else:
                records_dict[journal_entry_id] = [record]

        if unified_currency:
            if unified_exchange_date:
                exchange_date = exchange_date
            else:
                exchange_date = None


            for journal_entry_id, records in records_dict.items():
                for record in records:
                    currency = record[3]
                    currency_name = record[4]


                    if int(currency) == int(targeted_currency):
                        pass
                    else:
                        if not exchange_date:
                            # change the date to QDate (datetime.date will cause an error)
                            entry_date = QDate(record[5].year, record[5].month, record[5].day)
                            exchange_date = entry_date

                        exchange_value = self.database_operations.fetchExchangeValue(currency,
                                                                                              targeted_currency,
                                                                                              exchange_date.toString(Qt.ISODate))
                        if exchange_value:
                            old_value = record[2]
                            new_value = float(old_value) * float(exchange_value[0][1])
                            new_value = round(new_value, 4)
                            record[2] = new_value
                            record[3] = targeted_currency
                            record[4] = targeted_currency_name

        elif distinct_currency:
            pass

        else:
            return

        # Aggregating debtor and creditor sums
        debtors_sum_dict = {}
        creditors_sum_dict = {}
        for records in records_dict.values():
            for record in records:
                currency_key = tuple([record[3], record[4]])  # [currency_id, currency_name]
                if record[6] == 'debtor':
                    debtors_sum_dict[currency_key] = debtors_sum_dict.get(currency_key, 0) + record[2]
                elif record[6] == 'creditor':
                    creditors_sum_dict[currency_key] = creditors_sum_dict.get(currency_key, 0) + record[2]

        return records_dict, debtors_sum_dict, creditors_sum_dict
