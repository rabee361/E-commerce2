import win32api
from PyQt5.QtGui import QIcon, QIntValidator, QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QAbstractItemView
from win32con import MB_OKCANCEL, IDCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Composition import Ui_Composition
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
        
class Ui_Composition_Logic(QDialog):
    database_operations = ''
    def __init__(self, sqlconnector, product_id):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations=DatabaseOperations(sqlconnector)
        self.product_id = product_id
        self.ui = Ui_Composition()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)  

    def showUi(self):
        window_composition = QDialog()
        self.ui.setupUi(window_composition)
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_composition)
        window_composition.exec()

    def initialize(self):
        self.ui.materials_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.materials_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.materials_table.verticalHeader().hide()
        self.ui.materials_table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        self.ui.add_btn.clicked.connect(lambda: self.addCompositionMaterial())
        self.ui.delete_btn.clicked.connect(lambda: self.removeCompositionMaterial())
        self.ui.materials_combobox.currentIndexChanged.connect(lambda: self.setUnit())
        self.ui.quantity_required.setValidator(QDoubleValidator())


        self.fetchRawMaterials()
        self.fetchComposition()



    def setUnit(self):
        data = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())
        unit = data[1]
        self.ui.unit.setText(str(unit))
        if unit == '':
            self.ui.unit_combobox.setEnabled(True)
            unit = self.ui.unit_combobox.currentText()
            print(unit)


    def fetchComposition(self):
        compositions=self.database_operations.fetchComposition(self.product_id)
        for composition in compositions:
            id = composition[0]
            name = composition[2]
            quantity = composition[3]
            unit = composition[4]

            # Create a empty row at bottom of table
            numRows = self.ui.materials_table.rowCount()
            self.ui.materials_table.insertRow(numRows)
            # Add text to the row
            self.ui.materials_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.materials_table.setItem(numRows, 1, QTableWidgetItem(name))
            self.ui.materials_table.setItem(numRows, 2, QTableWidgetItem(str(quantity)))
            self.ui.materials_table.setItem(numRows, 3, QTableWidgetItem(unit))

    def addCompositionMaterial(self):
        quantity = self.ui.quantity_required.text()
        unit = self.ui.unit.text()
        if unit == '':
            unit = self.ui.unit_combobox.currentText()

        data = self.ui.materials_combobox.itemData(self.ui.materials_combobox.currentIndex())
        if data is None or quantity=='' or float(quantity)<= 0.0:
            win32api.MessageBox(0,'خطأ في المادة، تأكد من وجود مواد أولية، او من الكمية.','خطأ')
        else:
            material_id = data[0]
            self.database_operations.addCompositionMaterial(quantity,unit,material_id,self.product_id)
            self.clearTable()
            self.fetchComposition()

    def removeCompositionMaterial(self):
        confirm = win32api.MessageBox(0, "حذف؟", " ", MB_OKCANCEL)
        if confirm == IDCANCEL:
            pass
        else:
            table_row = self.ui.materials_table.item(self.ui.materials_table.currentRow(), 0)
            if (str(type(table_row))=="<class 'NoneType'>"):
                pass
            else:
                composition_id = table_row.text()
                self.database_operations.removeCompositionMaterial(composition_id)
                self.clearTable()
                self.fetchComposition()

    def fetchRawMaterials(self):
        materials = self.database_operations.fetchRawMaterials()
        for material in materials:
            id = material[0]
            code = material[1]
            name = material[3]
            invoices = self.database_operations.fetchInvoices(id)
            if(len(invoices) > 0):
                unit = invoices[0][4]
            else:
                unit = ''
            data = [id,unit]
            view_name = str(name)+" ("+str(code)+")"
            self.ui.materials_combobox.addItem(view_name,data)

    def clearTable(self):
        self.ui.materials_table.setRowCount(0)

