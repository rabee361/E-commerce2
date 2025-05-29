import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt , QDate
from Ui_ClientReport import Ui_ClientReport
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_InvoiceView_Logic import Ui_InvoiceView_Logic
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_ClientReport_Logic(object):
    def __init__(self, sqlconnector, filemanager , client_type='customer'):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.client_type = client_type
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_ClientReport()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

        # Summary of the client's invoices and payments
        self.client_summary = {}

    def showUi(self):
        window_client_report = QDialog()
        window_client_report.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window_client_report.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window_client_report)
        self.language_manager.load_translated_ui(self.ui, window_client_report)
        if self.client_type == 'customer':
            window_client_report.setWindowIcon(QIcon('icons/clients.png'))
            window_client_report.setWindowTitle(self.language_manager.translate("CLIENT_REPORT"))
        else:
            window_client_report.setWindowIcon(QIcon('icons/suppliers.png'))
            window_client_report.setWindowTitle(self.language_manager.translate("SUPPLIER_REPORT"))
        self.initialize()
        window_client_report.exec()

    def initialize(self):
        self.ui.client_operations_table.hideColumn(0)   # Invoice ID
        self.ui.client_operations_table.hideColumn(5)   # Currency ID

        self.ui.client_operations_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.ui.client_operations_table.setColumnWidth(3, 200)
        self.ui.client_operations_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Fixed) 
        self.ui.client_operations_table.setColumnWidth(7, 200)

        self.ui.clients_combobox.setDisabled(True)  
        self.ui.from_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.to_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.to_date_input.setDate(QDate.currentDate())

        self.ui.client_operations_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.client_operations_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.client_operations_table.verticalHeader().hide()
        self.ui.client_operations_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.client_operations_table.setSortingEnabled(True)
        self.ui.client_operations_table.horizontalHeader().setFixedHeight(40)
        self.ui.client_operations_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)

        if self.client_type == 'supplier':
            self.ui.groupBox.setTitle(self.language_manager.translate("SUPPLIER_REPORT"))
            self.ui.label.setText(self.language_manager.translate("SUPPLIER"))

        self.fetchClients()
        self.fetchCurrencies()

        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())
        self.ui.select_client_btn.clicked.connect(lambda: self.openSelectClientWindow())
        self.ui.client_operations_table.itemDoubleClicked.connect(lambda: self.openInvoiceWindow())
        self.ui.clients_combobox.currentIndexChanged.connect(lambda: self.clearSummary())
        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.displaySummary())

    def openSelectClientWindow(self):
        client_type = self.client_type
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'clients', client_type=client_type)
        result = data_picker.showUi()
        if result is not None:
            # Find the index where the client ID matches in the combobox
            for i in range(self.ui.clients_combobox.count()):
                if self.ui.clients_combobox.itemData(i)[0] == result['id']:
                    self.ui.clients_combobox.setCurrentIndex(i)
                    break

    def openInvoiceWindow(self):
        selected_row = self.ui.client_operations_table.currentRow()
        if selected_row >= 0:
            invoice_item = self.ui.client_operations_table.item(selected_row, 0)
            if invoice_item is None:
                return
            invoice_id = invoice_item.text()
            invoice_view = Ui_InvoiceView_Logic(self.sqlconnector, invoice_id=int(invoice_id))
            invoice_view.showUi()

    def fetchClients(self):
        clients = self.database_operations.fetchClients(client_type=self.client_type)
        for client in clients:
            id = client[0]
            name = client[1]
            governorate = client[2]
            data = [id, name]  # Store both id and name
            display_name = str(name) + ' / ' + str(governorate)
            self.ui.clients_combobox.addItem(display_name, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency[0]
            name = currency[1]
            self.ui.currency_combobox.addItem(name, id)
            self.client_summary[(id, name)] = {
                'total': 0,
                'paid': 0,
                'extra': 0
            }

    def clearSummary(self):
        for key in self.client_summary:
            self.client_summary[key] = {
                'total': 0,
                'paid': 0,
                'extra': 0
            }
        self.ui.client_operations_table.setRowCount(0)
        self.ui.total_input.setText("0")
        self.ui.paid_input.setText("0")
        self.ui.remain_input.setText("0")

    def getInvoicesPaymentsDict(self, client_id):
        invoices_payments = {}

        client_payments = self.database_operations.fetchClientPayments(client_id, include_extra_payments=True)

        for payment in client_payments:
            invoice_id = payment['origin_id']
            if invoice_id:
                if invoice_id not in invoices_payments:
                    invoices_payments[invoice_id] = []
                invoices_payments[invoice_id].append({
                    'origin_type': payment['origin_type'],
                    'date': payment['entry_date'], 
                    'currecny_id': payment['currency'],
                    'currency_name': payment['currency_name'],
                    'value': payment['value_col'],
                    'statement': payment['statement_col']
                })
           
        return invoices_payments

    def calculate(self):
        self.ui.client_operations_table.setRowCount(0)
        client = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())
        if client:
            client_id = client[0]
            client_data = self.database_operations.fetchClient(client_id)
            client_account = client_data['client_account_id']
            if client_account is None:
                win32api.MessageBox(0, self.language_manager.translate("CLIENT_ACCOUNT_NOT_FOUND"), self.language_manager.translate("ERROR"), 0x00000010)
                return
            from_date = self.ui.from_date_input.text()
            to_date = self.ui.to_date_input.text()

            invoices = self.database_operations.fetchInvoicesValues(client_id=client_id)

            invoices_payments = self.getInvoicesPaymentsDict(client_id)
                
            for invoice in invoices:
                date_col = datetime.datetime.strptime(invoice['date_col'], '%Y-%m-%d').date()

                from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
                to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()

                if date_col >= from_date_obj and date_col <= to_date_obj:
                    invoice_id = invoice['id']
                    invoice_type = invoice['invoice_type']
                    payment_type = invoice['payment']
                    invoice_number = invoice['number']
                    invoice_currency = invoice['currency']
                    invoice_currency_name = invoice['invoice_currency_name']
                    invoice_statement = invoice['statement_col']

                    invoice_value = invoice['invoice_value']
                    paid_ammount = invoice['paid_ammount']

                    paid = invoice['paid']
                    if paid == 1:
                        paid_ammount = invoice_value

                    self.client_summary[(invoice_currency, invoice_currency_name)]['total'] += float(invoice_value)
                    self.client_summary[(invoice_currency, invoice_currency_name)]['paid'] += float(paid_ammount)

                    payment_type = self.language_manager.translate("CASH") if payment_type == "cash" else self.language_manager.translate("POSTPONED")

                    rows = self.ui.client_operations_table.rowCount()
                    self.ui.client_operations_table.insertRow(rows)
                    self.ui.client_operations_table.setItem(rows, 0, QTableWidgetItem(str(invoice_id)))
                    self.ui.client_operations_table.setItem(rows, 1, QTableWidgetItem(str(invoice_type)))
                    self.ui.client_operations_table.setItem(rows, 2, QTableWidgetItem(str(invoice_number)))
                    self.ui.client_operations_table.setItem(rows, 3, QTableWidgetItem(str(payment_type)))
                    self.ui.client_operations_table.setItem(rows, 4, QTableWidgetItem(str(date_col)))
                    self.ui.client_operations_table.setItem(rows, 5, QTableWidgetItem(str(invoice_currency)))
                    self.ui.client_operations_table.setItem(rows, 6, QTableWidgetItem(str(invoice_currency_name)))

                    info_text = str(paid_ammount) + "/" + str(invoice_value)
                    info_cell = QTableWidgetItem(info_text)
                    if float(paid_ammount) == float(invoice_value):
                        info_cell.setBackground(QColor("darkgreen"))
                        info_cell.setForeground(QColor("white"))
                    elif float(paid_ammount) < float(invoice_value):
                        info_cell.setBackground(QColor("red")) 
                        info_cell.setForeground(QColor("white"))
                    elif float(paid_ammount) > float(invoice_value):  # TODO: this should never happen
                        info_cell.setBackground(QColor("yellow"))
                        info_cell.setForeground(QColor("black"))
                    self.ui.client_operations_table.setItem(rows, 7, info_cell)

                    self.ui.client_operations_table.setItem(rows, 8, QTableWidgetItem(str(invoice_statement)))

                    if int(invoice_id) in invoices_payments:
                        for payment in invoices_payments[invoice_id]:
                            rows = self.ui.client_operations_table.rowCount()
                            self.ui.client_operations_table.insertRow(rows)

                            color = QColor("yellow")
                            if payment['origin_type'] == 'invoice_payment':
                                payment_type = self.language_manager.translate("PAYMENT")
                            elif payment['origin_type'] == 'extra_payment':
                                payment_type = self.language_manager.translate("EXTRA_PAYMENT")
                                color = QColor("#2196F3")  # A nice light blue color that indicates extra/additional payment
                                self.client_summary[(payment['currecny_id'], payment['currency_name'])]['extra'] += float(payment['value'])
                            
                            # Create merged cell for first 4 columns to show as child
                            self.ui.client_operations_table.setSpan(rows, 0, 1, 3)
                            merged_item = QTableWidgetItem(f'{payment_type} {self.language_manager.translate("FOR_INVOICE")} {invoice_number}')
                            merged_item.setBackground(color)  # Yellow background
                            self.ui.client_operations_table.setItem(rows, 3, merged_item)
                            
                            # Set remaining columns
                            self.ui.client_operations_table.setItem(rows, 4, QTableWidgetItem(str(payment['date'])))
                            self.ui.client_operations_table.setItem(rows, 5, QTableWidgetItem(str(payment['currecny_id'])))
                            self.ui.client_operations_table.setItem(rows, 6, QTableWidgetItem(str(payment['currency_name'])))
                            payment_cell = QTableWidgetItem(str(payment['value']))
                            payment_cell.setBackground(color)
                            self.ui.client_operations_table.setItem(rows, 7, payment_cell)
                            self.ui.client_operations_table.setItem(rows, 8, QTableWidgetItem(str(payment['statement'])))
        
            self.displaySummary()

    def displaySummary(self):
        client = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())
        if client:
            client_id = client[0]
            # Get selected currency
            selected_currency = self.ui.currency_combobox.currentData()
            selected_currency_name = self.ui.currency_combobox.currentText()
            
            total_value = self.client_summary[(selected_currency, selected_currency_name)]['total']
            total_paid = self.client_summary[(selected_currency, selected_currency_name)]['paid']

            client_data = self.database_operations.fetchClient(client_id)
            client_account_id = client_data['client_account_id']
            client_extra_account_id = client_data['extra_account_id']

            extra_paid = self.database_operations.fetchAccountValue(client_extra_account_id, selected_currency)
            
            # Display totals in selected currency
            self.ui.total_input.setText(f"{total_value:.2f}")
            self.ui.paid_input.setText(f"{total_paid:.2f}")
            self.ui.debt_input.setText(f"{(total_value - total_paid):.2f}")
            self.ui.remain_input.setText(f"{extra_paid:.2f}")

    def exportToExcel(self):
        # Get selected client data
        client_data = self.ui.clients_combobox.itemData(self.ui.clients_combobox.currentIndex())
        if not client_data:
            win32api.MessageBox(0, self.language_manager.translate("CLIENT_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))
            return

        try:
            # Create Excel workbook with a default name
            client_name = client_data[1].replace(" ", "_")  # Use the name from client_data
            current_date = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"client_report_{client_name}_{current_date}.xlsx"
            
            workbook = xlsxwriter.Workbook(file_name)
            worksheet = workbook.add_worksheet()
            
            # Set RTL for the worksheet
            worksheet.right_to_left()

            # Define formats
            bold_format = workbook.add_format({'bold': True, 'align': 'center', 'valign': 'vcenter'})
            center_format = workbook.add_format({'align': 'center', 'valign': 'vcenter'})
            payment_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#90EE90'})  # Light green
            extra_payment_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#98FB98'})  # Pale green
            paid_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#98FB98'})  # Pale green
            unpaid_format = workbook.add_format({'align': 'center', 'valign': 'vcenter', 'bg_color': '#FFB6C1'})  # Light red

            # Try to fetch and insert header image
            try:
                header_image = self.database_operations.fetchMedia('header_image')
                if header_image and header_image['file']:
                    import io
                    # Create BytesIO object from image data
                    image_data = io.BytesIO(header_image['file'])
                    
                    # Set header properties
                    worksheet.set_header('&G', {'image_center': image_data})
                    # Set margins to accommodate header
                    worksheet.set_margins(top=1.5)  # Increase top margin for header
            except Exception as e:
                print(f"Error inserting header image: {str(e)}")

            # Write report information
            worksheet.write(0, 0, self.language_manager.translate("NAME"), bold_format)
            worksheet.write(1, 0, self.language_manager.translate("FROM"), bold_format)
            worksheet.write(2, 0, self.language_manager.translate("TO"), bold_format)
            worksheet.write(0, 1, client_data[1], bold_format)  # Use the name from client_data
            worksheet.write(1, 1, str(self.ui.from_date_input.text()), bold_format)
            worksheet.write(2, 1, str(self.ui.to_date_input.text()), bold_format)

            # Write headers
            headers = [self.language_manager.translate("INVOICE_TYPE"), self.language_manager.translate("INVOICE_NUMBER"), self.language_manager.translate("PAYMENT_TYPE"), self.language_manager.translate("DATE"), self.language_manager.translate("CURRENCY"), self.language_manager.translate("PAID_AMOUNT"), self.language_manager.translate("STATEMENT")]
            for col, header in enumerate(headers):
                worksheet.write(4, col, header, bold_format)

            # Write data
            rowCount = self.ui.client_operations_table.rowCount()
            for row in range(rowCount):
                excel_col = 0
                for col in range(1, 9):
                    if col == 5:
                        continue
                        
                    cell_item = self.ui.client_operations_table.item(row, col)
                    if cell_item:
                        cell_value = cell_item.text()
                        cell_format = center_format
                        
                        # Check if this is a payment row by looking at the merged cell in column 3
                        if col == 3 and self.ui.client_operations_table.columnSpan(row, 0) > 1:
                            if "دفعة زائدة" in cell_value:
                                cell_format = extra_payment_format
                            else:
                                cell_format = payment_format
                        
                        # Format the payment info column
                        elif col == 7:
                            if "/" in cell_value:  # This is an invoice row
                                paid, total = map(float, cell_value.split("/"))
                                if paid == total:
                                    cell_format = paid_format
                                elif paid < total:
                                    cell_format = unpaid_format
                            elif self.ui.client_operations_table.columnSpan(row, 0) > 1:  # This is a payment row
                                if self.language_manager.translate("EXTRA_PAYMENT") in self.ui.client_operations_table.item(row, 3).text():
                                    cell_format = extra_payment_format
                                else:
                                    cell_format = payment_format
                                
                        worksheet.write(row + 5, excel_col, str(cell_value), cell_format)
                    excel_col += 1

            # Write totals
            total_row = rowCount + 6
            current_row = total_row

            # Write totals for each currency
            for currency, summary in self.client_summary.items():
                if summary['total'] > 0 or summary['paid'] > 0 or summary['extra'] > 0:
                    worksheet.write(current_row, 1, f"{currency[1]}", bold_format)
                    worksheet.write(current_row, 2, str(summary['total']), bold_format)
                    worksheet.write(current_row, 3, str(summary['paid']), bold_format)
                    debt = summary['total'] - summary['paid']
                    worksheet.write(current_row, 4, str(debt), bold_format)
                    worksheet.write(current_row, 5, str(summary['extra']), bold_format)
                    current_row += 1

            workbook.close()    
            win32api.MessageBox(0, self.language_manager.translate("REPORT_EXPORTED_SUCCESSFULLY"), self.language_manager.translate("SUCCESS"), 0x00000040)
            
        except Exception as e:
            win32api.MessageBox(0, self.language_manager.translate("EXPORTING_REPORT_ERROR"), self.language_manager.translate("ERROR"))