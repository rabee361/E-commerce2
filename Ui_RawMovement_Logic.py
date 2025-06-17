import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QTableWidgetItem, QHeaderView, QAbstractItemView, QDialog
from PyQt5.QtCore import QDate
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem

from Colors import blue_sky_color, light_green_color, light_red_color, light_yellow_color
from Ui_RawMovement import Ui_RawMovement
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_RawMovement_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_RawMovement()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_raw_material_movement = QDialog()
        self.ui.setupUi(window_raw_material_movement)
        self.language_manager.load_translated_ui(self.ui, window_raw_material_movement)
        self.initialize()
        window_raw_material_movement.exec()

    def initialize(self):
        self.ui.from_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.to_date_input.setDisplayFormat("dd-MM-yyyy")
        self.ui.materials_combobox.setEnabled(False)
        self.ui.to_date_input.setDate(QDate.currentDate())
        self.ui.moves_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.ui.moves_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.moves_table.horizontalHeader().setSectionResizeMode(5, QHeaderView.Stretch)

        self.ui.materials_btn.clicked.connect(lambda: self.openSelectRawMaterialWindow())
        self.ui.moves_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.moves_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.moves_table.verticalHeader().hide()
        self.ui.moves_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.moves_table.setSortingEnabled(True)
        
        self.fetchRawMaterials()
        self.ui.calc_btn.clicked.connect(lambda: self.calculate())
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.clearMovesTable())
        self.ui.from_date_input.dateChanged.connect(lambda: self.clearMovesTable())
        self.ui.to_date_input.dateChanged.connect(lambda: self.clearMovesTable())

    def openSelectRawMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'raw_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.materials_combobox.count()):
                if self.ui.materials_combobox.itemData(i)[0] == result['id']:
                    self.ui.materials_combobox.setCurrentIndex(i)
                    break

    def clearMovesTable(self):
        self.ui.moves_table.setRowCount(0)

    def fetchRawMaterials(self):
        materials = self.database_operations.fetchRawMaterials()
        for material in materials:
            id = material[0]
            code = material[1]
            name = material[3]
            name_en = material[4]
            name_string = str(name)+"/"+str(name_en)

            invoices = self.database_operations.fetchInvoices(id)
            if (len(invoices) > 0):
                unit = invoices[0][4]
            else:
                unit = ''
            data = [id, unit, name_string, code]
            view_name = str(name) + " (" + str(code) + ")"
            self.ui.materials_combobox.addItem(view_name, data)

    def calculate(self):
        self.ui.moves_table.setRowCount(0)
        material_id = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())[0]
        from_date = self.ui.from_date_input.text()
        to_date = self.ui.to_date_input.text()
        movements = self.database_operations.getRawMaterialsMovements(material_id, from_date, to_date)
        counter = 0
        for move in movements:
            material_id = move[0]
            material_code = move[1]
            material_name = move[2]
            material_name_en = move[3]
            type = move[4]
            id = move[5]
            quantity = move[6]
            unit = move[7]
            src = move[8]
            product = move[9]
            product_en = move[10]
            resulted_boxes = move[11]
            batch = move[12]
            date = move[13]

            quantity = round(float(quantity),3)

            if type=='invoice':
                src = ''
                to = 'مستودع المواد الأولية'
                bg = light_green_color
                resulted_boxes_string = ''
                product_string = ''

            elif type=='manufacture':
                src= 'مستودع المواد الأولية'
                to = 'الانتاج'
                bg = light_red_color
                resulted_boxes_string = str(resulted_boxes) + " " + str("قطعة")
                product_string = str(product)+"/"+str(product_en)

            elif type=='lab':
                src = 'مستودع المواد الأولية'
                to = 'المخبر'
                bg = blue_sky_color
                resulted_boxes_string = ''
                product_string = ''

            elif type=='research':
                src = 'مستودع المواد الأولية'
                to = 'البحث والتطوير'
                bg = light_yellow_color
                resulted_boxes_string = ''
                product_string = ''

            else:
                src = 'ERROR'

            counter += 1
            rows = self.ui.moves_table.rowCount()
            self.ui.moves_table.insertRow(rows)
            self.ui.moves_table.setItem(rows, 0, MyTableWidgetItem(str(counter), int(counter)))
            self.ui.moves_table.setItem(rows, 1, QTableWidgetItem(str(date)))
            self.ui.moves_table.setItem(rows, 2, QTableWidgetItem(str(src)))
            self.ui.moves_table.setItem(rows, 3, QTableWidgetItem(str(to)))
            self.ui.moves_table.setItem(rows, 4, MyTableWidgetItem(str(quantity)+" "+str(unit), float(quantity)))
            self.ui.moves_table.setItem(rows, 5, QTableWidgetItem(str(product_string)))
            self.ui.moves_table.setItem(rows, 6, QTableWidgetItem(str(resulted_boxes_string)))
            self.ui.moves_table.setItem(rows, 7, QTableWidgetItem(str(batch)))

            self.ui.moves_table.item(rows, 0).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 1).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 2).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 3).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 4).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 5).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 6).setBackground(QtGui.QColor(bg))
            self.ui.moves_table.item(rows, 7).setBackground(QtGui.QColor(bg))

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
            'fg_color': 'yellow',
            'color': 'black'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'green',
            'color': 'white'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'red',
            'color': 'white'})

        blue_format = workbook.add_format({
            'border': 1,
            'align': 'center',
            'valign': 'vcenter',
            'fg_color': 'blue',
            'color': 'white'})

        center_format = workbook.add_format({
            'align': 'center'
        })


        worksheet = workbook._add_sheet("Simple Plan Result")
        worksheet.set_column("A:X", '', center_format)
        worksheet.set_column(1, 1, 35)
        worksheet.right_to_left()
        worksheet.set_column("A:R", 15)
        worksheet.write("A1", "حركة مادة",bold_format)
        worksheet.write("A2", "المادة",bold_format)
        worksheet.write("A3", "الكود",bold_format)
        worksheet.write("A4", "من",bold_format)
        worksheet.write("A5", "إلى",bold_format)

        material_name = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())[2]
        material_code = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())[3]
        from_date = self.ui.from_date_input.text()
        to_date = self.ui.to_date_input.text()

        worksheet.write("B2",material_name,bold_format)
        worksheet.write("B3",material_code ,bold_format)
        worksheet.write("B4",from_date ,bold_format)
        worksheet.write("B5",to_date ,bold_format)

        worksheet.write("A6","#",bold_format)
        worksheet.write("B6","التاريخ" ,bold_format)
        worksheet.write("C6","من" ,bold_format)
        worksheet.write("D6","إلى" ,bold_format)
        worksheet.write("E6","الكمية" ,bold_format)
        worksheet.write("F6","المنتج" ,bold_format)
        worksheet.write("G6","الكمية الناتجة" ,bold_format)
        worksheet.write("H6","الوجبة" ,bold_format)

        rowCount = self.ui.moves_table.rowCount()
        for row in range(0, rowCount):
            worksheet.write("A"+str(row+7), self.ui.moves_table.item(row, 0).text())
            worksheet.write("B"+str(row+7), self.ui.moves_table.item(row, 1).text())
            worksheet.write("C"+str(row+7), self.ui.moves_table.item(row, 2).text())
            worksheet.write("D"+str(row+7), self.ui.moves_table.item(row, 3).text())
            worksheet.write("E"+str(row+7), self.ui.moves_table.item(row, 4).text())
            worksheet.write("F"+str(row+7), self.ui.moves_table.item(row, 5).text())
            worksheet.write("G"+str(row+7), self.ui.moves_table.item(row, 6).text())
            worksheet.write("H"+str(row+7), self.ui.moves_table.item(row, 7).text())


        workbook.close()

