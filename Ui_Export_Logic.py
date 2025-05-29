from decimal import Decimal

import xlsxwriter
from PyQt5 import QtCore
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from DatabaseOperations import DatabaseOperations
from Ui_Export import Ui_Export


class Ui_Export_Logic(object):
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.filemanager = filemanager
        self.Export = ''
        self.ui = Ui_Export()

    def showUi(self):
        self.Export = QDialog()
        self.ui.setupUi(self.Export)
        self.initialize()
        self.Export.exec()

    def initialize(self):
        self.setYears()
        self.ui.pushButton.clicked.connect(lambda: self.exportToExcel())

    def setYears(self):
        self.ui.comboBox.clear()
        years = self.database_operations.fetchManufacturedYears()
        print(len(years))
        if(len(years)>0):
            for year in years:
                self.ui.comboBox.addItem(str(year[0]))
        else:
            self.Export.accept()


    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        year = self.ui.comboBox.currentText()
        workbook = xlsxwriter.Workbook(file_name)

        merge_format_1 = workbook.add_format({
            'bold': 1,
            'border': 1,
            'valign': 'vcenter',
            'fg_color': 'yellow',
            'align': 'right'})

        merge_format_2 = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'fg_color': '#0000FF',
            'color':'white',
            'align': 'right'})

        merge_format_3 = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'fg_color': '#00FF00',
            'color':'black',
            'align': 'right'})

        merge_format_4 = workbook.add_format({
            'border': 1,
            'valign': 'vcenter',
            'fg_color': '#FF6600',
            'color':'white',
            'align': 'right'})

        right_format = workbook.add_format({
            'align': 'right'
        })

        materials = self.database_operations.fetchManufacturedProducedMaterials()
        used_names = set()  # Keep track of used worksheet names
        
        for material in materials:
            #get product data
            material_id = material['material_id']
            material_name = material['material_name']
            material_quantity = material['quantity1']
            material_hours = material['working_hours']

            manufactures = self.database_operations.fetchManufactureProcessesOfMaterial(str(material_id))

            if (len(manufactures) > 0):
                # Create a unique worksheet name
                base_name = material_name[:28]  # Leave room for numbers
                worksheet_name = base_name
                counter = 1
                
                # If the name is already used, append a number
                while worksheet_name in used_names:
                    worksheet_name = f"{base_name}_{counter}"
                    counter += 1
                
                used_names.add(worksheet_name)
                worksheet = workbook.add_worksheet(worksheet_name)
                worksheet.right_to_left()
                worksheet.set_column("A:I",25)

                worksheet.merge_range("A2:I2","معلومات النموذج",merge_format_2)
                worksheet.write("A3","الكمية", right_format)
                worksheet.write("A4",str(material_quantity), right_format)
                worksheet.write("B3","ساعات العمل", right_format)
                worksheet.write("B4",str(material_hours), right_format)
                worksheet.merge_range("A5:I5", "التركيب", merge_format_3)
                raws = self.database_operations.fetchComposition(material_id)

                worksheet.write("A6","المادة", right_format)
                worksheet.write("B6","الكود", right_format)
                worksheet.write("C6","الكمية", right_format)
                worksheet.write("D6","الواحدة", right_format)
                i=7
                for raw in raws:
                    raw_id = raw['id']
                    raw_name = raw['name']
                    raw_quantity = raw['quantity']
                    raw_unit = raw['unit_name']
                    raw_code = raw['code']

                    cell_location_name="A"+str(i)
                    cell_location_code="B"+str(i)
                    cell_location_quantity_unit="C"+str(i)
                    cell_location_unit="D"+str(i)

                    worksheet.write(cell_location_name,raw_name, right_format)
                    worksheet.write(cell_location_code,raw_code, right_format)
                    worksheet.write(cell_location_quantity_unit,str(raw_quantity), right_format)
                    worksheet.write(cell_location_unit,str(raw_unit), right_format)
                    i = i+1

                worksheet.merge_range("A"+str(i)+":I"+str(i), "عمليات التصنيع", merge_format_4)
                i=i+1

                header_location_operation = "A" + str(i)
                worksheet.write(header_location_operation, "العملية", right_format)
                header_location_date = "B"+str(i)
                worksheet.write(header_location_date,"التاريخ", right_format)
                header_location_batch = "C"+str(i)
                worksheet.write(header_location_batch,"الوجبة", right_format)
                header_location_hours = "D"+str(i)
                worksheet.write(header_location_hours,"الكمية", right_format)
                header_location_quantity = "E"+str(i)
                worksheet.write(header_location_quantity,"ساعات العمل", right_format)
                header_location_expense = "F"+str(i)
                worksheet.write(header_location_expense,"الكلفة الافرادية", right_format)
                header_location_expense_currency = "G"+str(i)
                worksheet.write(header_location_expense_currency,"العملة", right_format)
                header_location_expense_total = "H"+str(i)
                worksheet.write(header_location_expense_total,"الكلفة الاجمالية", right_format)
                header_location_expense_total_currency = "I"+str(i)
                worksheet.write(header_location_expense_total_currency,"العملة", right_format)

                i = i+1

                for manufacture in manufactures:
                    header_location_operation = "A" + str(i)
                    worksheet.write(header_location_operation, manufacture['id'], right_format)
                    header_location_date = "B" + str(i)
                    worksheet.write(header_location_date, str(manufacture['date_col']), right_format)
                    header_location_batch = "C" + str(i)
                    worksheet.write(header_location_batch, manufacture['batch'], right_format)
                    header_location_hours = "E" + str(i)
                    worksheet.write(header_location_hours, manufacture['working_hours'], right_format)
                    header_location_quantity = "D" + str(i)
                    worksheet.write(header_location_quantity, manufacture['quantity1'], right_format)

                    pullout_date = manufacture['pullout_date']
                    box_required = manufacture['quantity1']
                    box_per_batch = material_quantity
                    currency_id = manufacture['currency']

                    #do manufacutre process
                    fraction = Decimal(box_required) / Decimal(box_per_batch)
                    raw_materials_cost = 0
                    for raw in raws:
                        raw_id = raw['id']
                        raw_quantity = raw['quantity']

                        material_avg_price = self.database_operations.fetchAverageMaterialPrice(raw_id, targeted_currency=currency_id, from_date=pullout_date)
                        required_material_avg_price = Decimal(material_avg_price) * Decimal(fraction)
                        raw_materials_cost = Decimal(raw_materials_cost) + Decimal(required_material_avg_price)

                    unit_price = Decimal(raw_materials_cost) / Decimal(box_required)
                    unit_price = round(unit_price, 5)
                    raw_materials_cost = round(raw_materials_cost, 5)

                    header_location_unit_price = "F" + str(i)
                    worksheet.write(header_location_unit_price, str(unit_price), right_format)
                    header_location_unit_price_currency = "G" + str(i)
                    worksheet.write(header_location_unit_price_currency, manufacture['currency_name'], right_format)
                    header_location_total_price = "H" + str(i)
                    worksheet.write(header_location_total_price, str(raw_materials_cost), right_format)
                    header_location_total_price_currency = "I" + str(i)
                    worksheet.write(header_location_total_price_currency, manufacture['currency_name'], right_format)

                    i = i + 1

        workbook.close()
        self.Export.accept()

    def retranslateUi(self, Export):
        _translate = QtCore.QCoreApplication.translate
        Export.setWindowTitle(_translate("Export", "تصدير"))
        Export.setWindowIcon(QIcon("epsic.dll"))
        self.label.setText(_translate("Export", "تصدير عمليات التصنيع لعام:"))
        self.ui.pushButton.setText(_translate("Export", "تصدير"))
