import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView

from Colors import light_green_color, light_yellow_color, light_red_color
from DatabaseOperations import DatabaseOperations
from Ui_SimplePlanResult import Ui_SimplePlanResult
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_SimplePlanResult_Logic(QDialog):
    database_operations = ''

    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_SimplePlanResult()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        simple_plan_result = QDialog()
        self.ui.setupUi(simple_plan_result)
        self.initialize(simple_plan_result)
        self.language_manager.load_translated_ui(self.ui, simple_plan_result)
        simple_plan_result.exec()

    def initialize(self, ui):
        self.ui.simple_plan_result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.simple_plan_result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.simple_plan_result_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.simple_plan_result_table.verticalHeader().hide()
        # self.ui.simple_plan_result_table.setSortingEnabled(True)

        self.ui.simple_plan_result_table.horizontalHeader().setStretchLastSection(False)
        self.ui.simple_plan_result_table.verticalHeader().setStretchLastSection(False)

        self.ui.simple_plan_result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.simple_plan_result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.calculateResult()

    def calculateResult(self):
        # get raw materials
        materials = self.database_operations.fetchRawMaterials()
        materials_dict = {}
        for material in materials:
            id = str(material['id'])
            code = str(material['code'])
            name = str(material['name'])
            quantity = str(material['current_quantity'])

            materials_dict[id] = quantity

        # parse plan items
        simple_plan_items = self.database_operations.fetchSimplePlanItems()
        batchcounter = 1
        for item in simple_plan_items:
            material_id = item['material']
            material = self.database_operations.fetchMaterial(material_id)
            material_name = material['name']
            quantity = material['current_quantity']

            numRows = self.ui.simple_plan_result_table.rowCount()
            self.ui.simple_plan_result_table.insertRow(numRows)
            self.ui.simple_plan_result_table.setItem(numRows, 0, QTableWidgetItem(str(material_name)))
            self.ui.simple_plan_result_table.item(numRows, 0).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 1, QTableWidgetItem(str(batchcounter)))
            self.ui.simple_plan_result_table.item(numRows, 1).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 2, QTableWidgetItem(str(quantity)))
            self.ui.simple_plan_result_table.item(numRows, 2).setBackground(light_yellow_color)
            # rest are empty cells
            self.ui.simple_plan_result_table.setItem(numRows, 3, QTableWidgetItem(str("")))
            self.ui.simple_plan_result_table.item(numRows, 3).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 4, QTableWidgetItem(str("")))
            self.ui.simple_plan_result_table.item(numRows, 4).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 5, QTableWidgetItem(str("")))
            self.ui.simple_plan_result_table.item(numRows, 5).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 6, QTableWidgetItem(str("")))
            self.ui.simple_plan_result_table.item(numRows, 6).setBackground(light_yellow_color)
            self.ui.simple_plan_result_table.setItem(numRows, 7, QTableWidgetItem(str("")))
            self.ui.simple_plan_result_table.item(numRows, 7).setBackground(light_yellow_color)

            composition = self.database_operations.fetchComposition(material_id)
            for row in composition:
                material_id = str(row['composition_material_id'])
                material_name = str(row['name'])
                material_quantity = str(row['quantity'])

                numRows = self.ui.simple_plan_result_table.rowCount()
                self.ui.simple_plan_result_table.insertRow(numRows)

                self.ui.simple_plan_result_table.setItem(numRows, 3, QTableWidgetItem(str(material_name)))
                if float(material_quantity) >= float(materials_dict[material_id]):
                    self.ui.simple_plan_result_table.setItem(numRows, 4, QTableWidgetItem(str(material_quantity)))
                    self.ui.simple_plan_result_table.item(numRows, 4).setBackground(light_red_color)
                    self.ui.simple_plan_result_table.setItem(numRows, 5, QTableWidgetItem(
                        str(round(float(materials_dict[material_id]), 3))))
                    self.ui.simple_plan_result_table.item(numRows, 5).setBackground(light_red_color)
                    materials_dict[material_id] = float(materials_dict[material_id]) - float(material_quantity)
                    self.ui.simple_plan_result_table.setItem(numRows, 6, QTableWidgetItem(
                        str(round(float(materials_dict[material_id]), 3))))
                    self.ui.simple_plan_result_table.item(numRows, 6).setBackground(light_red_color)
                    self.ui.simple_plan_result_table.setItem(numRows, 7, QTableWidgetItem("FAIL"))
                    self.ui.simple_plan_result_table.item(numRows, 7).setBackground(light_red_color)
                else:
                    self.ui.simple_plan_result_table.setItem(numRows, 4, QTableWidgetItem(str(material_quantity)))
                    self.ui.simple_plan_result_table.item(numRows, 4).setBackground(light_green_color)
                    self.ui.simple_plan_result_table.setItem(numRows, 5, QTableWidgetItem(
                        str(round(float(materials_dict[material_id]), 3))))
                    self.ui.simple_plan_result_table.item(numRows, 5).setBackground(light_green_color)
                    materials_dict[material_id] = float(materials_dict[material_id]) - float(material_quantity)
                    self.ui.simple_plan_result_table.setItem(numRows, 6, QTableWidgetItem(
                        str(round(float(materials_dict[material_id]), 3))))
                    self.ui.simple_plan_result_table.item(numRows, 6).setBackground(light_green_color)
                    self.ui.simple_plan_result_table.setItem(numRows, 7, QTableWidgetItem("PASS"))
                    self.ui.simple_plan_result_table.item(numRows, 7).setBackground(light_green_color)

            batchcounter = batchcounter + 1

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

        center_format = workbook.add_format({
            'align': 'center'
        })

        worksheet = workbook._add_sheet("Simple Plan Result")
        worksheet.set_column("A:X", '', center_format)
        worksheet.set_column(1, 1, 35)
        worksheet.right_to_left()
        worksheet.set_column("A:R", 15)
        worksheet.write("A1", "المنتج", bold_format)
        worksheet.write("B1", "الوجبة", bold_format)
        worksheet.write("C1", "القطع في الوجبة", bold_format)
        worksheet.write("D1", "المادة الأولية", bold_format)
        worksheet.write("E1", "الكمية المطلوبة", bold_format)
        worksheet.write("F1", "الكمية المتوفرة", bold_format)
        worksheet.write("G1", "الكمية المتبقية", bold_format)
        worksheet.write("H1", "النتيجة", bold_format)

        rowCount = self.ui.simple_plan_result_table.rowCount()
        for row in range(0, rowCount):
            if str(self.ui.simple_plan_result_table.item(row, 7).text()) == "":
                print("info row" + self.ui.simple_plan_result_table.item(row, 0).text())
                worksheet.write("A" + str(row + 2), self.ui.simple_plan_result_table.item(row, 0).text(), yellow_format)
                worksheet.write("B" + str(row + 2), self.ui.simple_plan_result_table.item(row, 1).text(), yellow_format)
                worksheet.write("C" + str(row + 2), self.ui.simple_plan_result_table.item(row, 2).text(), yellow_format)
                worksheet.write("D" + str(row + 2), "", yellow_format)
                worksheet.write("E" + str(row + 2), "", yellow_format)
                worksheet.write("F" + str(row + 2), "", yellow_format)
                worksheet.write("G" + str(row + 2), "", yellow_format)
                worksheet.write("H" + str(row + 2), "", yellow_format)
            else:
                condition_cell = self.ui.simple_plan_result_table.item(row, 7).text()
                if (str(condition_cell) == "PASS"):
                    worksheet.write("A" + str(row + 2), "")
                    worksheet.write("B" + str(row + 2), "")
                    worksheet.write("C" + str(row + 2), "")
                    worksheet.write("D" + str(row + 2), self.ui.simple_plan_result_table.item(row, 3).text())
                    worksheet.write("E" + str(row + 2), self.ui.simple_plan_result_table.item(row, 4).text(), green_format)
                    worksheet.write("F" + str(row + 2), self.ui.simple_plan_result_table.item(row, 5).text(), green_format)
                    worksheet.write("G" + str(row + 2), self.ui.simple_plan_result_table.item(row, 6).text(), green_format)
                    worksheet.write("H" + str(row + 2), self.ui.simple_plan_result_table.item(row, 7).text(), green_format)
                else:
                    worksheet.write("A" + str(row + 2), "")
                    worksheet.write("B" + str(row + 2), "")
                    worksheet.write("C" + str(row + 2), "")
                    worksheet.write("D" + str(row + 2), self.ui.simple_plan_result_table.item(row, 3).text())
                    worksheet.write("E" + str(row + 2), self.ui.simple_plan_result_table.item(row, 4).text(), red_format)
                    worksheet.write("F" + str(row + 2), self.ui.simple_plan_result_table.item(row, 5).text(), red_format)
                    worksheet.write("G" + str(row + 2), self.ui.simple_plan_result_table.item(row, 6).text(), red_format)
                    worksheet.write("H" + str(row + 2), self.ui.simple_plan_result_table.item(row, 7).text(), red_format)
        workbook.close()
