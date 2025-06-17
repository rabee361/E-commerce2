from math import ceil

import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView
from Colors import blue_sky_color, light_green_color, light_red_color, light_yellow_color
from DatabaseOperations import DatabaseOperations
from Ui_PlanPercentResult import Ui_PlanPercentResult
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
import win32api

class Ui_PlanPercentResult_Logic(QDialog):
    database_operations = ''
    def __init__(self, sqlconnector, filemanager, target):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations = DatabaseOperations(sqlconnector)
        self.target = target
        self.ui = Ui_PlanPercentResult()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        plan_percent_result = QDialog()
        self.ui.setupUi(plan_percent_result)
        self.language_manager.load_translated_ui(self.ui, plan_percent_result)
        self.initialize()
        plan_percent_result.exec()

    def initialize(self):
        self.ui.plan_percent_result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.plan_percent_result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)

        self.ui.plan_percent_result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.plan_percent_result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.plan_percent_result_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.plan_percent_result_table.verticalHeader().hide()

        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.ui.target_input.setText(str(self.target))
        self.ui.target_btn.clicked.connect(lambda: self.calculateResult())
        self.calculateResult()



    def calculateResult(self):
        #get raw materials
        materials=self.database_operations.fetchRawMaterials()
        materials_dict = {}
        for material in materials:
            id = str(material['id'])
            code = str(material['code'])
            name = str(material['name'])
            quantity = str(material['current_quantity'])

            materials_dict[id]=quantity

        #parse plan items
        plan_percent_items = self.database_operations.fetchPlanPercentItems()
        target = str(self.ui.target_input.text())
        for item in plan_percent_items:
            batch_counter = 0
            valid_batch_counter = 0
            percent = item['percent']
            priority = item['priority']
            plan_target_boxes = float(percent)*float(target)/100
            material_id = item[1]
            material = self.database_operations.fetchMaterial(material_id)
            material_name = material['name']

            material_quantity = 0
            material_warehouses = self.database_operations.fetchMaterialWarehouses(material_id)
            for warehouse_id, records in material_warehouses.items():
                for record in records:
                    material_quantity += record['quantity']

            quantity = material_quantity
            if not quantity:
                win32api.MessageBox(0, "لا يمكن أن يكون الكمية الحالية للمادة صفر", "خطأ")
                return
            plan_batch_count = float(plan_target_boxes)/float(quantity)
            plan_batch_count = ceil(plan_batch_count)
            fail_value = 0
            for i in range (1,plan_batch_count+1):
                batch_counter = batch_counter+1
                numRows = self.ui.plan_percent_result_table.rowCount()
                self.ui.plan_percent_result_table.insertRow(numRows)
                self.ui.plan_percent_result_table.setItem(numRows, 0, QTableWidgetItem(str(material_name)))
                self.ui.plan_percent_result_table.item(numRows, 0).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 1, QTableWidgetItem(str(batch_counter)))
                self.ui.plan_percent_result_table.item(numRows, 1).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 2, QTableWidgetItem(str(quantity)))
                self.ui.plan_percent_result_table.item(numRows, 2).setBackground(QtGui.QColor(light_yellow_color))
                #rest are empty cells
                self.ui.plan_percent_result_table.setItem(numRows, 3, QTableWidgetItem(str("")))
                self.ui.plan_percent_result_table.item(numRows, 3).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 4, QTableWidgetItem(str("")))
                self.ui.plan_percent_result_table.item(numRows, 4).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 5, QTableWidgetItem(str("")))
                self.ui.plan_percent_result_table.item(numRows, 5).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 6, QTableWidgetItem(str("")))
                self.ui.plan_percent_result_table.item(numRows, 6).setBackground(QtGui.QColor(light_yellow_color))
                self.ui.plan_percent_result_table.setItem(numRows, 7, QTableWidgetItem(str("")))
                self.ui.plan_percent_result_table.item(numRows, 7).setBackground(QtGui.QColor(light_yellow_color))


                can_be_done = 1
                composition = self.database_operations.fetchComposition(material_id)
                for row in composition:
                    numRows = self.ui.plan_percent_result_table.rowCount()
                    self.ui.plan_percent_result_table.insertRow(numRows)

                    material_id = str(row['composition_material_id'])
                    material_name = str(row['name'])
                    material_quantity = str(row['quantity'])

                    self.ui.plan_percent_result_table.setItem(numRows, 3, QTableWidgetItem(str(material_name)))
                    if float(material_quantity) >= float(materials_dict[material_id]):
                        self.ui.plan_percent_result_table.setItem(numRows, 4, QTableWidgetItem(str(material_quantity)))
                        self.ui.plan_percent_result_table.item(numRows, 4).setBackground(QtGui.QColor(light_red_color))
                        self.ui.plan_percent_result_table.setItem(numRows, 5, QTableWidgetItem(str(round(float(materials_dict[material_id]),3))))
                        self.ui.plan_percent_result_table.item(numRows, 5).setBackground(QtGui.QColor(light_red_color))
                        materials_dict[material_id] = float(materials_dict[material_id])-float(material_quantity)
                        self.ui.plan_percent_result_table.setItem(numRows, 6, QTableWidgetItem(str(round(float(materials_dict[material_id]),3))))
                        self.ui.plan_percent_result_table.item(numRows, 6).setBackground(QtGui.QColor(light_red_color))
                        self.ui.plan_percent_result_table.setItem(numRows, 7, QTableWidgetItem("FAIL"))
                        self.ui.plan_percent_result_table.item(numRows, 7).setBackground(QtGui.QColor(light_red_color))
                        can_be_done = 0
                        if fail_value==0:
                            fail_value=materials_dict[material_id]
                    else:
                        self.ui.plan_percent_result_table.setItem(numRows, 4, QTableWidgetItem(str(material_quantity)))
                        self.ui.plan_percent_result_table.item(numRows, 4).setBackground(QtGui.QColor(light_green_color))
                        self.ui.plan_percent_result_table.setItem(numRows, 5, QTableWidgetItem(str(round(float(materials_dict[material_id]),3))))
                        self.ui.plan_percent_result_table.item(numRows, 5).setBackground(QtGui.QColor(light_green_color))
                        materials_dict[material_id] = float(materials_dict[material_id])-float(material_quantity)
                        self.ui.plan_percent_result_table.setItem(numRows, 6, QTableWidgetItem(str(round(float(materials_dict[material_id]),3))))
                        self.ui.plan_percent_result_table.item(numRows, 6).setBackground(QtGui.QColor(light_green_color))
                        self.ui.plan_percent_result_table.setItem(numRows, 7, QTableWidgetItem("PASS"))
                        self.ui.plan_percent_result_table.item(numRows, 7).setBackground(QtGui.QColor(light_green_color))


                if can_be_done==1:
                    valid_batch_counter=valid_batch_counter+1

            valid_boxes_count = int(float(valid_batch_counter))*int(float(quantity))

            numRows = self.ui.plan_percent_result_table.rowCount()
            self.ui.plan_percent_result_table.insertRow(numRows)

            self.ui.plan_percent_result_table.setItem(numRows, 0, QTableWidgetItem(str("")))
            self.ui.plan_percent_result_table.setItem(numRows, 1, QTableWidgetItem(str(valid_batch_counter)))
            self.ui.plan_percent_result_table.item(numRows, 1).setBackground(QtGui.QColor(blue_sky_color))
            self.ui.plan_percent_result_table.setItem(numRows, 2, QTableWidgetItem(str(valid_boxes_count)))
            self.ui.plan_percent_result_table.item(numRows, 2).setBackground(QtGui.QColor(blue_sky_color))
            self.ui.plan_percent_result_table.setItem(numRows, 3, QTableWidgetItem(str("")))
            self.ui.plan_percent_result_table.setItem(numRows, 4, QTableWidgetItem(str("")))
            self.ui.plan_percent_result_table.setItem(numRows, 5, QTableWidgetItem(str("")))
            self.ui.plan_percent_result_table.setItem(numRows, 6, QTableWidgetItem(str("")))
            self.ui.plan_percent_result_table.setItem(numRows, 7, QTableWidgetItem(str("")))


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
        worksheet.write("A1", "المنتج",bold_format)
        worksheet.write("B1", "الوجبة",bold_format)
        worksheet.write("C1", "القطع في الوجبة",bold_format)
        worksheet.write("D1", "المادة الأولية",bold_format)
        worksheet.write("E1", "الكمية المطلوبة",bold_format)
        worksheet.write("F1", "الكمية المتوفرة",bold_format)
        worksheet.write("G1", "الكمية المتبقية",bold_format)
        worksheet.write("H1", "النتيجة",bold_format)

        rowCount = self.ui.plan_percent_result_table.rowCount()
        for row in range(0, rowCount):
            if str(self.ui.plan_percent_result_table.item(row, 7).text()) == "":
                if str(self.ui.plan_percent_result_table.item(row, 0).text()) != "":
                    worksheet.write("A"+str(row+2), self.ui.plan_percent_result_table.item(row, 0).text(), yellow_format)
                    worksheet.write("B"+str(row+2), self.ui.plan_percent_result_table.item(row, 0).text(), yellow_format)
                    worksheet.write("C"+str(row+2), self.ui.plan_percent_result_table.item(row, 0).text(), yellow_format)
                    worksheet.write("D"+str(row+2), "", yellow_format)
                    worksheet.write("E"+str(row+2), "", yellow_format)
                    worksheet.write("F"+str(row+2), "", yellow_format)
                    worksheet.write("G"+str(row+2), "", yellow_format)
                    worksheet.write("H"+str(row+2), "", yellow_format)
                else:
                    worksheet.write("A"+str(row+2), "")
                    worksheet.write("B"+str(row+2), self.ui.plan_percent_result_table.item(row, 1).text(), blue_format)
                    worksheet.write("C"+str(row+2), self.ui.plan_percent_result_table.item(row, 2).text(), blue_format)
                    worksheet.write("D"+str(row+2), "")
                    worksheet.write("E"+str(row+2), "")
                    worksheet.write("F"+str(row+2), "")
                    worksheet.write("G"+str(row+2), "")
                    worksheet.write("H"+str(row+2), "")
            else:
                condition_cell = self.ui.plan_percent_result_table.item(row, 7).text()
                if(str(condition_cell) == "PASS"):
                    worksheet.write("A"+str(row+2), "")
                    worksheet.write("B"+str(row+2), "")
                    worksheet.write("C"+str(row+2), "")
                    worksheet.write("D" + str(row+2), self.ui.plan_percent_result_table.item(row, 3).text())
                    worksheet.write("E" + str(row+2), self.ui.plan_percent_result_table.item(row, 4).text(), green_format)
                    worksheet.write("F" + str(row+2), self.ui.plan_percent_result_table.item(row, 5).text(), green_format)
                    worksheet.write("G" + str(row+2), self.ui.plan_percent_result_table.item(row, 6).text(), green_format)
                    worksheet.write("H" + str(row+2), self.ui.plan_percent_result_table.item(row, 7).text(), green_format)
                else:
                    worksheet.write("A" + str(row + 2), "")
                    worksheet.write("B" + str(row + 2), "")
                    worksheet.write("C" + str(row + 2), "")
                    worksheet.write("D" + str(row + 2), self.ui.plan_percent_result_table.item(row, 3).text())
                    worksheet.write("E" + str(row + 2), self.ui.plan_percent_result_table.item(row, 4).text(),
                                    red_format)
                    worksheet.write("F" + str(row + 2), self.ui.plan_percent_result_table.item(row, 5).text(),
                                    red_format)
                    worksheet.write("G" + str(row + 2), self.ui.plan_percent_result_table.item(row, 6).text(),
                                    red_format)
                    worksheet.write("H" + str(row + 2), self.ui.plan_percent_result_table.item(row, 7).text(),
                                    red_format)
        workbook.close()
