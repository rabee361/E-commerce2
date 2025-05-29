import xlsxwriter
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView

from Colors import light_red_color, light_yellow_color, light_green_color
from DatabaseOperations import DatabaseOperations

from PyQt5 import QtCore, QtGui, QtWidgets

from TypeChecker import isfloat
from Ui_AutoAggregator import Ui_AutoAggregator
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_AutoAggregator_Logic(QDialog):
    database_operations = ''
    def __init__(self, sqlconnector, filemanager):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.filemanager = filemanager
        self.database_operations=DatabaseOperations(sqlconnector)
        self.ui = Ui_AutoAggregator()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_aggregator = QDialog()
        window_aggregator.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_aggregator)
        window_aggregator.setWindowIcon(QIcon('icons/task_report.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_aggregator)
        window_aggregator.exec()

    def initialize(self):
        self.ui.auto_aggregator_result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.ui.auto_aggregator_result_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Stretch)
        self.ui.auto_aggregator_result_table.verticalHeader().hide()
        self.ui.auto_aggregator_result_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.auto_aggregator_result_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.auto_aggregator_result_table.setSelectionMode(QAbstractItemView.SingleSelection)


        self.ui.export_btn.clicked.connect(lambda: self.exportToExcel())
        self.ui.regard_raw_warhouse_checkbox.clicked.connect(lambda: self.calculateResult())

        self.calculateResult()


    def calculateResult(self):
        gaga = self
        materials_dict = {} #a dictionary, material_id is the key
        # parse plan items
        groupped_materials = self.database_operations.fetchGrouppedMaterials()
        batchcounter = 1
        for groupped_material in groupped_materials:
            material_id = str(groupped_material['id'])
            batch_quantity = str(groupped_material['current_quantity'])
            still_required = float(groupped_material['yearly_required'])-float(groupped_material['current_quantity']) #year_require-in_warehouse

            if float(batch_quantity) > 0.0:
                print(float(batch_quantity))
                ratio = float(still_required) / float(batch_quantity)
            else:
                ratio = 0

            composition = self.database_operations.fetchComposition(material_id)
            for row in composition:
                material_id = str(row['id'])
                material_name = str(row['name'])
                material_quantity = str(row['quantity'])
                material_unit = str(row['unit'])
                material_code = str(row['code'])
                required_quantity_to_complete_year_require = float(material_quantity)*float(ratio)
                if not material_id in materials_dict:
                    # a list [name, code, ammount, details,details_summarized]
                    material_info = [material_name, material_code, str(required_quantity_to_complete_year_require), "",""]
                    materials_dict[material_id] = material_info
                else:
                    old_required_value = materials_dict[material_id][2] #old required_quantity_to_complete_year_require value
                    new_value = float(old_required_value) + float(required_quantity_to_complete_year_require)
                    materials_dict[material_id][2] = str(new_value)

        if self.ui.regard_raw_warhouse_checkbox.isChecked():
            for key in materials_dict:
                #dict[key][name, code, ammount, details, details_summerized]
                material = self.database_operations.fetchRawMaterial(str(key))
                warehouse_entries = self.database_operations.fetchMaterialWarehouses(str(key))
                material_quantity_in_warehouse = 0
                for warehouse_id, data_list in warehouse_entries.items():
                    for data in data_list:
                        material_quantity_in_warehouse += float(data['quantity'])
                old_required_value = materials_dict[key][2]
                difference = float(material_quantity_in_warehouse)-float(old_required_value)

                if difference > 0:
                    materials_dict[key][2] = 0
                    materials_dict[key][3] = f"{self.language_manager.translate('CURRENT_QUANTITY')}: {str(material_quantity_in_warehouse)} {self.language_manager.translate('REQUIRED_QUANTITY')}: {str(round(difference,3))}"
                    materials_dict[key][4]="+"
                else:
                    if difference == 0:
                        materials_dict[key][2] = 0
                        materials_dict[key][3] = f"{self.language_manager.translate('CURRENT_QUANTITY')}: {str(material_quantity_in_warehouse)} {self.language_manager.translate('REQUIRED_QUANTITY')}: {str(round(difference,3))}"
                        materials_dict[key][4] = "0"
                    else:
                        materials_dict[key][2] =  str(abs(difference))
                        materials_dict[key][3] = f"{self.language_manager.translate('CURRENT_QUANTITY')}: {str(material_quantity_in_warehouse)} {self.language_manager.translate('REQUIRED_QUANTITY')}: {str(round(difference,3))}"
                        materials_dict[key][4] = "-"

        #output the results
        self.ui.auto_aggregator_result_table.setRowCount(0)
        for key in materials_dict:
            # a list [name, code, ammount, details]
            name = str(materials_dict[key][0])
            code = str(materials_dict[key][1])
            quantity = str(round(float(materials_dict[key][2]),3))
            details = str(materials_dict[key][3])
            details_summary = str(materials_dict[key][4])

            numRows = self.ui.auto_aggregator_result_table.rowCount()
            self.ui.auto_aggregator_result_table.insertRow(numRows)

            self.ui.auto_aggregator_result_table.setItem(numRows, 0, QTableWidgetItem(code))
            self.ui.auto_aggregator_result_table.setItem(numRows, 1, QTableWidgetItem(name))
            self.ui.auto_aggregator_result_table.setItem(numRows, 2, QTableWidgetItem(quantity))
            self.ui.auto_aggregator_result_table.setItem(numRows, 3, QTableWidgetItem(details))

            if details_summary == "-":
                self.ui.auto_aggregator_result_table.item(numRows, 3).setBackground(light_red_color)
            else:
                if details_summary == "0":
                    self.ui.auto_aggregator_result_table.item(numRows, 3).setBackground(light_yellow_color)
                else:
                    if details_summary == "+":
                        self.ui.auto_aggregator_result_table.item(numRows, 3).setBackground(light_green_color)

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
            'fg_color': 'yellow',
            'color': 'black'})

        green_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': 'green',
            'color': 'white'})

        red_format = workbook.add_format({
            'border': 1,
            'align': 'right',
            'valign': 'vcenter',
            'fg_color': 'red',
            'color': 'white'})

        center_format = workbook.add_format({
            'align': 'right'
        })

        worksheet = workbook._add_sheet("Simple Plan Result")
        worksheet.set_column(0, 23, 15, center_format)  # A:X columns with width 15
        worksheet.right_to_left()
        worksheet.set_column(3, 3, 60)  # Column D width 60
        
        worksheet.write("A1", self.language_manager.translate("CODE"), bold_format)
        worksheet.write("B1", self.language_manager.translate("RAW_MATERIAL"), bold_format)
        worksheet.write("C1", self.language_manager.translate("REQUIRED_QUANTITY"), bold_format)
        worksheet.write("D1", self.language_manager.translate("DETAILS"), bold_format)

        rowCount = self.ui.auto_aggregator_result_table.rowCount()
        for row in range(0, rowCount):
            worksheet.write("A" + str(row + 2), self.ui.auto_aggregator_result_table.item(row, 0).text())
            worksheet.write("B" + str(row + 2), self.ui.auto_aggregator_result_table.item(row, 1).text())
            worksheet.write("C" + str(row + 2), self.ui.auto_aggregator_result_table.item(row, 2).text())

            if self.ui.auto_aggregator_result_table.item(row, 3):
                condition_cell = self.ui.auto_aggregator_result_table.item(row, 3).background().color()
                if condition_cell == light_green_color:
                    worksheet.write("D"+str(row+2), self.ui.auto_aggregator_result_table.item(row, 3).text(), green_format)
                else:
                    if condition_cell == light_red_color:
                        worksheet.write("D" + str(row+2), self.ui.auto_aggregator_result_table.item(row, 3).text(), red_format)
                    else:
                        if condition_cell == light_yellow_color:
                            worksheet.write("D" + str(row+2), self.ui.auto_aggregator_result_table.item(row, 3).text(), yellow_format)
                        else:
                            worksheet.write("D" + str(row+2), self.ui.auto_aggregator_result_table.item(row, 3).text())

        workbook.close()
