from datetime import datetime
import xlsxwriter
from PyQt5.QtWidgets import QTableWidgetItem, QAbstractItemView, QHeaderView, QDialog
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_OutReadyInvoiceView import Ui_OutReadyInvoiceView
from Ui_Payments_Logic import Ui_Payments_Logic


class Ui_OutReadyInvoiceView_Logic(object):
    def __init__(self, sqlconnector, filemanager, invoice_id):
        super().__init__()
        self.filemanager = filemanager
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.invoice_id = invoice_id
        self.ui = Ui_OutReadyInvoiceView()

    def showUi(self):
        window_viewinvoice = QDialog()
        self.ui.setupUi(window_viewinvoice)
        self.initialize()
        window_viewinvoice.exec()

    def initialize(self):
        self.ui.date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.items_table.verticalHeader().hide()
        self.ui.items_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.items_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.items_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(6, QHeaderView.Stretch)
        self.ui.items_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.Stretch)


        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())
        self.ui.payments_btn.clicked.connect(lambda: self.openPaymentsWindow())
        self.fetchOutReadyInvoice()


    def fetchOutReadyInvoice(self):
        invoice_data = self.database_operations.fetchReadyOutInvoice(self.invoice_id)
        currency = invoice_data[0][0]
        date = invoice_data[0][1]
        invoice_number = invoice_data[0][2]
        paid = invoice_data[0][3]
        payment = invoice_data[0][4]
        statement = invoice_data[0][5]
        final_discout = invoice_data[0][6]
        client = invoice_data[0][14]
        exchange = invoice_data[0][15]


        self.ui.currency_input.setText(str(currency))

        date_object = datetime.strptime(str(date), '%Y-%m-%d')
        self.ui.date_input.setDate(date_object)

        self.ui.number_input.setText(str(invoice_number))

        if paid == 'نعم':
            self.ui.paid_input.setCurrentIndex(0)
        elif paid == 'لا':
            self.ui.paid_input.setCurrentIndex(1)
        else:
            pass

        self.ui.payment_input.setText(str(payment))
        self.ui.statement_input.setText(str(statement))
        self.ui.result_discount_input.setText(str(final_discout))
        self.ui.client_input.setText(str(client))
        exchange_string = "1$="+str(exchange)
        self.ui.exchange_input.setText(exchange_string)

        total_sp = 0
        total_usd = 0
        total_sp_after_discount = 0
        total_usd_after_discount = 0
        counter = 1
        for item in invoice_data:
            product_name = item[13]
            quantity = item[12]
            price_sp = item[8]
            price_usd = item[9]
            discount = item[7]
            price_sp_after_discount = item[10]
            price_usd_after_discount = item[11]

            total_sp = float(total_sp) + float(price_sp)
            total_usd = float(total_usd) + float(price_usd)
            total_sp_after_discount = float(total_sp_after_discount) + float(price_sp_after_discount)
            total_usd_after_discount = float(total_usd_after_discount) + float(price_usd_after_discount)

            numRows = self.ui.items_table.rowCount()
            self.ui.items_table.insertRow(numRows)
            # Add text to the row
            self.ui.items_table.setItem(numRows, 0, MyTableWidgetItem(str(counter), counter))
            self.ui.items_table.setItem(numRows, 1, QTableWidgetItem(str(product_name)))
            self.ui.items_table.setItem(numRows, 2, QTableWidgetItem(str(quantity)))
            self.ui.items_table.setItem(numRows, 3, QTableWidgetItem(str(price_sp)))
            self.ui.items_table.setItem(numRows, 4, QTableWidgetItem(str(price_usd)))
            self.ui.items_table.setItem(numRows, 5, QTableWidgetItem(str(discount)))
            self.ui.items_table.setItem(numRows, 6, QTableWidgetItem(str(price_sp_after_discount)))
            self.ui.items_table.setItem(numRows, 7, QTableWidgetItem(str(price_usd_after_discount)))

            counter = counter + 1

        self.ui.result_sp_input.setText(str(total_sp))
        self.ui.result_usd_input.setText(str(total_usd))
        self.ui.result_after_discount_sp_input.setText(str(total_sp_after_discount))
        self.ui.result_after_discount_usd_input.setText(str(total_usd_after_discount))

    # def savePaidState(self):
    #     paid = self.ui.paid_input.currentText();
    #     self.database_operations.saveOutInvoicePaid(self.invoice_id, paid)

    def setPaid(self):
        invoice_data = self.database_operations.fetchReadyOutInvoice(self.invoice_id)
        paid = invoice_data[0][3]
        self.ui.paid_input.setEnabled(True)
        if paid=='نعم':
            self.ui.paid_input.setCurrentIndex(0)
        elif paid=='لا':
            self.ui.paid_input.setCurrentIndex(1)
        self.ui.paid_input.setEnabled(False)

    def openPaymentsWindow(self):
        Ui_Payments_Logic(self.sqlconnector, self.invoice_id).showUi()
        self.setPaid()


    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        bold_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        yellow_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#000000',
            'color': 'yellow'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'green'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'red'})

        center_format = workbook.add_format({
            'align': 'center'
        })

        worksheet = workbook._add_sheet("Aggregator Result")
        worksheet.set_column("A:X", '', center_format)
        worksheet.set_column(1, 1, 35)
        worksheet.right_to_left()
        worksheet.set_column("A:R", 15)
        worksheet.write("A1", "الزبون", bold_format)
        worksheet.write("B1", self.ui.client_input.text(), bold_format)
        worksheet.write("A2", "الدفع", bold_format)
        worksheet.write("B2", self.ui.payment_input.text(), bold_format)
        worksheet.write("A3", "العملة", bold_format)
        worksheet.write("B3", self.ui.currency_input.text(), bold_format)
        worksheet.write("A4", "التاريخ", bold_format)
        worksheet.write("B4", self.ui.date_input.text(), bold_format)

        worksheet.write("A5", "المنتج")
        worksheet.write("A5", "الكمية")
        worksheet.write("B5", "السعر قبل الحسم")
        worksheet.write("C5", "نسبة الحسم")
        worksheet.write("D5", "السعر بعد الحسم")

        currency = self.ui.currency_input.text()

        excel_row_count = 6
        data_row_count = self.ui.items_table.rowCount()

        if currency == 'ل.س':
            for row in range(0, data_row_count):
                worksheet.write("A" + str(excel_row_count), self.ui.items_table.item(row, 1).text())
                worksheet.write("B" + str(excel_row_count), self.ui.items_table.item(row, 2).text())
                worksheet.write("B" + str(excel_row_count), self.ui.items_table.item(row, 3).text())
                worksheet.write("C" + str(excel_row_count), self.ui.items_table.item(row, 5).text())
                worksheet.write("D" + str(excel_row_count), self.ui.items_table.item(row, 6).text())
                excel_row_count += 1

            worksheet.write("A" + str(excel_row_count), "المجموع")
            worksheet.write("B" + str(excel_row_count), self.ui.result_sp_input.text())

            worksheet.write("A" + str(excel_row_count + 1), "حسم أجمالي")
            worksheet.write("B" + str(excel_row_count + 1), self.ui.result_discount_input.text())

            worksheet.write("A" + str(excel_row_count + 2), "المجموع بعد الحسم")
            worksheet.write("B" + str(excel_row_count + 2), self.ui.result_after_discount_sp_input.text())

        else:
            for row in range(0, data_row_count):
                worksheet.write("A" + str(excel_row_count), self.ui.items_table.item(row, 1).text())
                worksheet.write("B" + str(excel_row_count), self.ui.items_table.item(row, 2).text())
                worksheet.write("B" + str(excel_row_count), self.ui.items_table.item(row, 4).text())
                worksheet.write("C" + str(excel_row_count), self.ui.items_table.item(row, 5).text())
                worksheet.write("D" + str(excel_row_count), self.ui.items_table.item(row, 7).text())
                excel_row_count += 1

            worksheet.write("A" + str(excel_row_count), "المجموع", green_format)
            worksheet.write("B" + str(excel_row_count), self.ui.result_usd_input.text(), green_format)

            worksheet.write("A" + str(excel_row_count + 1), "حسم أجمالي", green_format)
            worksheet.write("B" + str(excel_row_count + 1), self.ui.result_discount_input.text(), green_format)

            worksheet.write("A" + str(excel_row_count + 2), "المجموع بعد الحسم", green_format)
            worksheet.write("B" + str(excel_row_count + 2), self.ui.result_after_discount_usd_input.text(), green_format)

        workbook.close()
