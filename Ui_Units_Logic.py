import win32api
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from win32con import MB_YESNO, IDYES, IDNO
from PyQt5.QtGui import QDoubleValidator
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Units import Ui_Units
from PyQt5.QtCore import Qt , QTranslator
from LanguageManager import LanguageManager

class Ui_Units_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Units()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.convert_value_input.setValidator(QDoubleValidator())
        self.ui.add_unit_btn.clicked.connect(lambda: self.addUnit())
        self.ui.add_conversion_btn.clicked.connect(lambda: self.addConversion())
        self.ui.delete_unit_btn.clicked.connect(lambda: self.removeUnit())
        self.ui.delete_conversion_btn.clicked.connect(lambda: self.removeConversion())
        self.ui.units_table.cellClicked.connect(lambda: self.fetchConversionValues())
        self.ui.units_table.cellClicked.connect(lambda: self.setPreConversionLabel())

        self.ui.units_table.cellChanged.connect(lambda r, c: self.updateUnit(r, c))

        self.fetchUnits()
        self.fetchConversionValues()

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        self.ui.unit2_conversion_combobox.clear()

        for unit in units:
            id = unit[0]
            name = unit[1]

            # Create a empty row at bottom of table
            numRows = self.ui.units_table.rowCount()
            self.ui.units_table.insertRow(numRows)

            # Add text to the row
            self.ui.units_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
            self.ui.units_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

            self.ui.unit2_conversion_combobox.addItem(name, id)

    def setPreConversionLabel(self):
        table_row = self.ui.units_table.item(self.ui.units_table.currentRow(), 1)
        name = table_row.text()
        self.ui.pre_conversion_edit_label.setText(f"{self.language_manager.translate('EACH')} 1 {name} =")

    def addUnit(self):
        name = self.ui.unit_name_input.text()
        if name and name.strip():
            self.database_operations.addUnit(name)
            self.ui.units_table.setRowCount(0)
            self.fetchUnits()
            self.ui.conversion_table.setRowCount(0)
            self.ui.unit_name_input.clear()
            self.fetchConversionValues()

    def updateUnit(self, row=None, column=None, update_all=False):
        pass

    def fetchConversionValues(self):
        float_point_value = self.database_operations.fetchFloatPointValue()
        self.ui.conversion_table.setRowCount(0)
        # conversion_value=None
        table_row = self.ui.units_table.item(self.ui.units_table.currentRow(), 0)
        if (str(type(table_row)) == "<class 'NoneType'>"):
            pass
        else:
            unit_id = table_row.text()
            conversion_values = self.database_operations.fetchUnitConversionValueBetween(unit_id)
            if conversion_values:
                for key, value in conversion_values.items():
                    conversion_id = key[0]
                    unit_id = key[1]
                    unit_name = key[2]
                    conversion_value = value
                    numRows = self.ui.conversion_table.rowCount()
                    self.ui.conversion_table.insertRow(numRows)

                    if float_point_value:
                        if conversion_value.is_integer():
                            formatted_value = f"{int(conversion_value)}"
                        else:
                            # Remove trailing zeros after decimal point while respecting float_point_value
                            formatted_value = f"{conversion_value:.{float_point_value}f}".rstrip('0').rstrip('.')

                    # Add text to the row
                    if conversion_id is not None:
                        self.ui.conversion_table.setItem(numRows, 0, MyTableWidgetItem(str(conversion_id), int(conversion_id)))
                    else:
                        self.ui.conversion_table.setItem(numRows, 0, MyTableWidgetItem(None, None))
                    self.ui.conversion_table.setItem(numRows, 1, QTableWidgetItem(str(unit_name)))
                    self.ui.conversion_table.setItem(numRows, 2, QTableWidgetItem(formatted_value))

    def addConversion(self):
        table_row = self.ui.units_table.item(self.ui.units_table.currentRow(), 0)
        if table_row:
            unit1_id = table_row.text()
            conversion_value = self.ui.convert_value_input.text()
            self.ui.convert_value_input.clear()
            unit2_id = self.ui.unit2_conversion_combobox.currentData()
            if conversion_value and conversion_value.strip() and (int(unit1_id) != int(unit2_id)):
                self.database_operations.addUnitsConversionValue(unit1_id, unit2_id, conversion_value)
                self.ui.conversion_table.setRowCount(0)
                self.fetchConversionValues()

    def removeUnit(self):
        table_row = self.ui.units_table.item(self.ui.units_table.currentRow(), 0)
        if table_row:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                if (str(type(table_row)) == "<class 'NoneType'>"):
                    pass
                else:
                    unit_id = table_row.text()
                    self.database_operations.removeUnit(unit_id)
                    self.ui.units_table.setRowCount(0)
                    self.fetchUnits()
                    self.fetchConversionValues()
            if (messagebox_result == IDNO):
                pass

    def removeConversion(self):
        table_row = self.ui.conversion_table.item(self.ui.conversion_table.currentRow(), 0)
        if table_row:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                if (str(type(table_row)) == "<class 'NoneType'>"):
                    pass
                else:
                    conversion_id = table_row.text()
                    if (conversion_id == ''):   # Conversion has been calculated and does not exist in the database
                        win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
                    else:
                        self.database_operations.removeUnitConversion(conversion_id)
                        self.fetchConversionValues()
            if (messagebox_result == IDNO):
                pass

