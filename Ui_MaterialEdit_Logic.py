import win32api
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon, QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_MaterialEdit import Ui_MaterialEdit
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_MaterialEdit_Logic(QDialog):
    def __init__(self, sqlconnector, material_id):
        super().__init__()
        self.material_id = material_id
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_MaterialEdit()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):   
        window_raw_edit = QDialog()
        self.ui.setupUi(window_raw_edit)
        self.initialize(window_raw_edit)
        self.language_manager.load_translated_ui(self.ui, window_raw_edit)
        window_raw_edit.exec()

    def initialize(self, window):
        float_point_value = self.database_operations.fetchFloatPointValue()
        validator = QDoubleValidator()
        if float_point_value:
            validator = QDoubleValidator(float_point_value)
            
        self.ui.quantity_lineEdit.setValidator(validator)
        self.ui.default_price_lineEdit.setValidator(validator)

        self.ui.save_btn.clicked.connect(lambda: self.saveMaterialData(window))


        self.fetchMaterialData()
        print("Material edit UI loaded.")

    def fetchMaterialData(self):
        material_data = self.database_operations.fetchRawMaterial(self.material_id)
        material_id = material_data[0][0]
        material_code = material_data[0][1]
        material_name = material_data[0][2]
        material_name_en = material_data[0][3]
        material_quantity = material_data[0][4]
        material_date = material_data[0][5]
        material_unit = material_data[0][6]
        material_default_price = material_data[0][7]

        self.ui.id_lineEdit.setText(str(material_id))
        self.ui.name_lineEdit.setText(material_name)
        self.ui.name_en_lineEdit.setText(material_name_en)
        self.ui.code_lineEdit.setText(material_code)
        self.ui.quantity_lineEdit.setText(str(material_quantity))
        self.ui.date_lineEdit.setText(str(material_date))
        self.ui.unit_combobox.setCurrentText(str(material_unit))
        self.ui.default_price_lineEdit.setText(str(material_default_price))

    def saveMaterialData(self, window):
        material_name = self.ui.name_lineEdit.text()
        material_name_en = self.ui.name_en_lineEdit.text()

        material_code = self.ui.code_lineEdit.text()
        material_quantity = self.ui.quantity_lineEdit.text()
        material_unit = self.ui.unit_combobox.itemText(self.ui.unit_combobox.currentIndex())
        material_default_price = self.ui.default_price_lineEdit.text()

        all_ok = True
        if material_name=='' and material_name_en=='':
            win32api.MessageBox(0,'يرجى التأكد من اسم المادة','خطأ')
            all_ok = False
        if material_code == '':
            win32api.MessageBox(0, 'يرجى التأكد من رمز المادة', 'خطأ')
            all_ok = False

        if all_ok:
            self.database_operations.updateMaterial(self.material_id, material_name, material_name_en, material_code,
                                                material_quantity, material_unit, material_default_price)
            window.accept()


