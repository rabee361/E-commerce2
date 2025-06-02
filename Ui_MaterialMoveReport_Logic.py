import win32api
import datetime
import xlsxwriter
from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt , QDate
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_MaterialMoveReport import Ui_MaterialMoveReport
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color ,black
from PyQt5.QtGui import QPalette
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32con 
from PyQt5.QtGui import QIcon


class Ui_MaterialMoveReport_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(self.sqlconnector)
        self.ui = Ui_MaterialMoveReport()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


        # Summary of the client's invoices and payments
        self.material_summary = {}

    def showUi(self):
        window_material_report = QDialog()
        window_material_report.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window_material_report.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window_material_report)
        window_material_report.setWindowIcon(QIcon('icons/motion_path.png'))
        self.language_manager.load_translated_ui(self.ui, window_material_report)
        self.initialize()
        window_material_report.exec()

    def initialize(self):
        self.ui.material_moves_table.hideColumn(0)   # Material ID
        self.ui.material_moves_table.hideColumn(6)   # Unit ID
        self.ui.material_moves_table.hideColumn(10)   # Currency ID
        self.ui.material_moves_table.hideColumn(15)  # Origin ID

        self.ui.material_moves_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Fixed)
        self.ui.material_moves_table.horizontalHeader().setSectionResizeMode(9, QHeaderView.Fixed) 

        # self.ui.material_moves_table.setColumnWidth(7, 200)
        # self.ui.material_moves_table.setColumnWidth(3, 200)

        self.ui.materials_combobox.setDisabled(True)  
        self.ui.from_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.to_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.to_date_input.setDate(QDate.currentDate())

        self.ui.material_moves_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.material_moves_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.material_moves_table.verticalHeader().hide()
        self.ui.material_moves_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.material_moves_table.setSortingEnabled(True)
        self.ui.material_moves_table.horizontalHeader().setFixedHeight(40)

        self.fetchMaterials()
        self.fetchCurrencies()
        self.fetchWarehouses()

        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())
        self.ui.select_material_btn.clicked.connect(lambda: self.openSelectMaterialWindow())
        self.ui.select_from_warehouse_btn.clicked.connect(lambda: self.openSelectFromWarehouse())
        self.ui.select_to_warehouse_btn.clicked.connect(lambda: self.openSelectToWarehouse())
        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.clearSummary())
        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.displaySummary())

    def openSelectMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'materials', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            # Find the index where the material ID matches in the combobox
            for i in range(self.ui.materials_combobox.count()):
                if self.ui.materials_combobox.itemData(i)[0] == result['id']:
                    self.ui.materials_combobox.setCurrentIndex(i)
                    break

    def fetchMaterials(self):
        self.ui.materials_combobox.addItem( self.language_manager.translate("ALL_MATERIALS"), [None, None])
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material['id']
            name = material['name']
            code = material['code']
            data = [id, code]
            self.ui.materials_combobox.addItem(name, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.currency_combobox.addItem(name, id)
            self.material_summary[(id, name)] = {
                'total_sell': 0,
                'total_buy': 0
            }
            
    def fetchWarehouses(self):
        pass

    def openSelectFromWarehouse(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.from_warehouse_combobox.setCurrentIndex(self.ui.from_warehouse_combobox.findData(result['id']))

    def openSelectToWarehouse(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.to_warehouse_combobox.setCurrentIndex(self.ui.to_warehouse_combobox.findData(result['id']))

    def clearSummary(self):
        for key in self.material_summary:
            self.material_summary[key] = {
                'total_sell': 0,
                'total_buy': 0
            }
        self.ui.material_moves_table.setRowCount(0)
        self.ui.total_sell_input.setText("0")
        self.ui.total_buy_input.setText("0")
        self.ui.difference_input.setText("0")

    def calculate(self):
        self.ui.material_moves_table.setRowCount(0)

        selected_material = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())
        if selected_material[0] is None:
            selected_material_id = ''
        else:
            selected_material_id = selected_material[0]
        
        material_moves = self.database_operations.fetchMaterialMoves(selected_material_id)
        
        from_date = self.ui.from_date_input.text()
        to_date = self.ui.to_date_input.text()

        for move in material_moves:
            date_col = move['move_date']
            # Check if date_col is already a datetime.date object
            if isinstance(date_col, datetime.date):
                date_col = date_col
            else:
                date_col = datetime.datetime.strptime(date_col, '%Y-%m-%d').date()

            # Convert from_date and to_date to date objects
            from_date_obj = datetime.datetime.strptime(from_date, '%Y-%m-%d').date()
            to_date_obj = datetime.datetime.strptime(to_date, '%Y-%m-%d').date()

            if date_col >= from_date_obj and date_col <= to_date_obj:
                move_id = move['move_id']
                warehouse_id = move['warehouse_id']
                move_type = move['move_type']
                cause = move['move_origin'] or ''
                cause_id = move['move_origin_id'] or ''
                date = move['move_date']
                quantity = move['move_quantity']
                unit = move['move_unit']
                material_id = move['material_id']
                material_code = move['material_code']
                from_warehouse_name = move['from_warehouse_name'] or ''
                material_name = move['material_name']
                unit_name = move['unit_name']
                to_warehouse_name = move['to_warehouse_name'] or ''
                item_currency = move['item_currency']
                item_currency_name = move['item_currency_name']
                item_unit_price = move['item_unit_price']

                # Create an empty row at the bottom of the table
                numRows = self.ui.material_moves_table.rowCount()
                self.ui.material_moves_table.insertRow(numRows)

                # Add text to the row
                self.ui.material_moves_table.setItem(numRows, 0, QTableWidgetItem(str(move_id)))
                self.ui.material_moves_table.setItem(numRows, 1, QTableWidgetItem(str(material_name)))
                self.ui.material_moves_table.setItem(numRows, 2, QTableWidgetItem(str(material_code)))
                self.ui.material_moves_table.setItem(numRows, 3, QTableWidgetItem(str(from_warehouse_name)))
                self.ui.material_moves_table.setItem(numRows, 4, QTableWidgetItem(str(to_warehouse_name)))
                self.ui.material_moves_table.setItem(numRows, 5, QTableWidgetItem(str(quantity)))
                self.ui.material_moves_table.setItem(numRows, 6, QTableWidgetItem(str(unit)))
                self.ui.material_moves_table.setItem(numRows, 7, QTableWidgetItem(str(unit_name)))
                self.ui.material_moves_table.setItem(numRows, 8, QTableWidgetItem(str(move_type)))
                self.ui.material_moves_table.setItem(numRows, 9, QTableWidgetItem(str(date_col)))
                
                self.ui.material_moves_table.setItem(numRows, 10, QTableWidgetItem(str(item_currency)))
                self.ui.material_moves_table.setItem(numRows, 11, QTableWidgetItem(str(item_currency_name)))
                self.ui.material_moves_table.setItem(numRows, 12, QTableWidgetItem(str(item_unit_price)))
                total_price = 0
                if item_unit_price:
                    total_price = float(quantity) * float(item_unit_price)
                    self.ui.material_moves_table.setItem(numRows, 13, 
                    QTableWidgetItem(str(total_price)))
                else:
                    self.ui.material_moves_table.setItem(numRows, 13, 
                    QTableWidgetItem(str(0)))
                
                self.ui.material_moves_table.setItem(numRows, 14, QTableWidgetItem(str(cause)))
                self.ui.material_moves_table.setItem(numRows, 15, QTableWidgetItem(str(cause_id)))
                
                # Colorize the row red when move_type is reduce
                if move_type == 'reduce':
                    colorizeTableRow(self.ui.material_moves_table, numRows, background_color=light_red_color, text_color=black)
                    if item_currency is not None and item_currency_name is not None:
                        self.material_summary[(item_currency, item_currency_name)]['total_sell'] += float(total_price)
                elif move_type == 'add':
                    colorizeTableRow(self.ui.material_moves_table, numRows, background_color=light_green_color, text_color=black)
                    if item_currency is not None and item_currency_name is not None:
                        self.material_summary[(item_currency, item_currency_name)]['total_buy'] += float(total_price)
                elif move_type == 'transfer':
                    colorizeTableRow(self.ui.material_moves_table, numRows, background_color=blue_sky_color, text_color=black)

        self.displaySummary()

    def displaySummary(self):
        # Get selected currency
        selected_currency = self.ui.currency_combobox.currentData()
        selected_currency_name = self.ui.currency_combobox.currentText()
        
        total_sell = self.material_summary[(selected_currency, selected_currency_name)]['total_sell']
        total_buy = self.material_summary[(selected_currency, selected_currency_name)]['total_buy']

        # Display totals in selected currency
        self.ui.total_sell_input.setText(f"{total_sell:.2f}")
        self.ui.total_buy_input.setText(f"{total_buy:.2f}")
        self.ui.difference_input.setText(f"{(total_sell - total_buy):.2f}")
        # self.ui.avg_price.setText(f"{total_sell / total_buy:.2f}")

    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        bold_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'center',
            'valign': 'vcenter'})

        add_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#90EE90'})  # Light green background

        reduce_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#FFB6C1'})  # Light red background

        transfer_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'bg_color': '#2196F3'})  # Light blue background

        center_format = workbook.add_format({
            'align': 'center',
            'border': 1
        })

        worksheet = workbook._add_sheet("Materials Report")
        
        # Fix the column formatting
        worksheet.set_column('A:X', 15, center_format)  

        worksheet.right_to_left()

        worksheet.write("A1", self.language_manager.translate("FROM"), bold_format)
        worksheet.write("A2", self.language_manager.translate("TO"), bold_format)

        worksheet.write("B1", str(self.ui.from_date_input.text()), bold_format)
        worksheet.write("B2", str(self.ui.to_date_input.text()), bold_format)

        # Write headers
        headers = [self.language_manager.translate("MATERIAL"), self.language_manager.translate("CODE"), self.language_manager.translate("SOURCE_WAREHOUSE"), self.language_manager.translate("DESTINATION_WAREHOUSE"), self.language_manager.translate("QUANTITY"), self.language_manager.translate("UNIT"), self.language_manager.translate("MOVE_TYPE"), self.language_manager.translate("CURRENCY"), self.language_manager.translate("UNIT_PRICE"), self.language_manager.translate("TOTAL_PRICE"), self.language_manager.translate("DATE"), self.language_manager.translate("CAUSE")]
        for col, header in enumerate(headers):
            worksheet.write(2, col, header, bold_format)

        # Write data rows with updated formatting
        rowCount = self.ui.material_moves_table.rowCount()
        for row in range(rowCount):
            excel_col = 0  # Track Excel column separately from table column
            for col in range(1, 15):  # Skip invoice ID column (0)
                if col == 6 or col == 10 or col == 15:
                    continue
                    
                cell_item = self.ui.material_moves_table.item(row, col)
                if cell_item:
                    cell_value = cell_item.text()
                    cell_format = center_format
                    
                    if col == 8:
                        if cell_value == 'add':
                            cell_format = add_format
                        elif cell_value == 'reduce':
                            cell_format = reduce_format
                        elif cell_value == 'transfer':
                            cell_format = transfer_format
                    
                    worksheet.write(row + 3, excel_col, str(cell_value), cell_format)
                excel_col += 1  # Increment Excel column counter

        # Write totals
        current_row = rowCount + 5

        # Write total headers
        worksheet.write(current_row, 1, self.language_manager.translate("TOTAL_BUY"), bold_format)
        worksheet.write(current_row, 2, self.language_manager.translate("TOTAL_SELL"), bold_format)
        worksheet.write(current_row, 3, self.language_manager.translate("DIFFERENCE"), bold_format)
        current_row += 1
        for currency, summary in self.material_summary.items():
            if summary['total_sell'] > 0 and summary['total_buy'] > 0:
                worksheet.write(current_row, 0, f"{currency[1]}", bold_format)
                worksheet.write(current_row, 1, str(summary['total_sell']), bold_format)
                worksheet.write(current_row, 2, str(summary['total_buy']), bold_format)
                difference = summary['total_sell'] - summary['total_buy']
                worksheet.write(current_row, 3, str(difference), bold_format)
                current_row += 1

        workbook.close()    
        win32api.MessageBox(0, self.language_manager.translate("REPORT_EXPORTED_SUCCESSFULLY"), self.language_manager.translate("SUCCESS"), 0x00000040)
