
import xlsxwriter
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView

from DatabaseOperations import DatabaseOperations
from Ui_AggregatorResult import Ui_AggregatorResult
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_AggregatorResult_Logic(QDialog):
    database_operations = ''
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations=DatabaseOperations(sqlconnector)
        self.ui = Ui_AggregatorResult()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        aggregator_result = QDialog()
        self.ui.setupUi(aggregator_result)
        self.language_manager.load_translated_ui(self.ui, aggregator_result)
        self.initialize()
        aggregator_result.exec()

    def initialize(self):
        self.ui.aggregator_result_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.ui.aggregator_result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.aggregator_result_table.verticalHeader().hide()
        self.ui.aggregator_result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.aggregator_result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.aggregator_result_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())

        self.calculateResult()

    def calculateResult(self):

        materials_dict = {}

        #parse plan items
        aggregator_items = self.database_operations.fetchAggregatorItems()
        batchcounter = 1
        for item in aggregator_items:
            material_id = item['material_id']
            target_quantity = item['ammount']
            material = self.database_operations.fetchMaterialAggregator(material_id)
            material_name = material[0]['name']
            batch_quantity = material[0]['quantity']
            if batch_quantity != 0:
                ratio = float(target_quantity)/float(batch_quantity)
                composition = self.database_operations.fetchComposition(material_id)
                for row in composition:
                    material_id = str(row['composition_material_id'])
                    material_name = str(row['name'])
                    material_quantity = str(row['quantity'])
                    material_quantity_ratio = float(material_quantity)*float(ratio)

                    if not material_name in materials_dict:
                        materials_dict[material_name]=material_quantity_ratio

                    else:
                        old_value = materials_dict[material_name]
                        new_value = float(old_value) + float(material_quantity_ratio)
                        materials_dict[material_name] = str(new_value)

        for key in materials_dict:
            numRows = self.ui.aggregator_result_table.rowCount()
            self.ui.aggregator_result_table.insertRow(numRows)
            self.ui.aggregator_result_table.setItem(numRows, 0, QTableWidgetItem(str(key)))
            self.ui.aggregator_result_table.setItem(numRows, 1, QTableWidgetItem(str(round(float(materials_dict[key]),3))))

    def exportToExcel(self):
        file_name = self.filemanager.createEmptyFile('xlsx')
        workbook = xlsxwriter.Workbook(file_name)

        bold_format = workbook.add_format({
            'bold': True,
            'border': 1,
            'align': 'right',
            'valign': 'vcenter'})

        yellow_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#000000',
            'color': 'yellow'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'green'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': '#FFFFFF',
            'color': 'red'})

        center_format = workbook.add_format({
            'align': 'right'
        })

        worksheet = workbook._add_sheet("Aggregator Result")
        worksheet.set_column(0, 23, 15, center_format)
        worksheet.set_column(1, 1, 35)
        worksheet.right_to_left()
        
        worksheet.write("A1", "المادة الأولية", bold_format)
        worksheet.write("B1", "الكمية", bold_format)

        rowCount = self.ui.aggregator_result_table.rowCount()
        for row in range(0, rowCount):
            worksheet.write("A" + str(row+2), self.ui.aggregator_result_table.item(row,0).text())
            worksheet.write("B" + str(row+2), self.ui.aggregator_result_table.item(row,1).text())

        workbook.close()