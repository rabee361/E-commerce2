import math
from datetime import datetime, timedelta
import win32api
import win32con
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import QDate, Qt, QEvent, QObject, QTime, QTranslator
from PyQt5.QtGui import QIntValidator, QIcon, QDoubleValidator, QBrush, QColor
from PyQt5.QtWidgets import QDialog, QTableWidgetItem, QHeaderView, QAbstractItemView, QSizePolicy, QTreeWidgetItem, QWidget, QCheckBox, QComboBox, QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QDateEdit, QTimeEdit, QDateTimeEdit

from Colors import light_red_color, light_green_color
from MyCustomTableCellDelegate import MyCustomTableCellDelegate

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_Currencies_Logic import Ui_Currencies_Logic
from Ui_Manufacture import Ui_Manufacture
from win32con import IDYES, IDNO, MB_YESNO, MB_OK
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_GrouppedMaterialComposition_Logic import Ui_GrouppedMaterialComposition_Logic
from LanguageManager import LanguageManager


class Ui_Manufacture_Logic(QDialog):
    database_operations = ''
    materials_costs_dict = {}  # this dictionary holds material_id:
    machines_operation_costs_dict = {}  # this dictionaty holds account_id:[operation_cost] for each machine that participated in manufacturing
    salaries_costs_dict = {}  # this dictionary holds account_id:[value, currency] for each salay_block_id that participated in manufacturing
    expenses_dict = {}  # this dictionary holds resource_id:[...] for each salay_block_id that participated in manufacturing

    def __init__(self, sql_connector, manufacture_process_id=''):
        super().__init__()
        self.sql_connector = sql_connector
        self.manufacture_process_id = manufacture_process_id
        self.database_operations = DatabaseOperations(sql_connector)
        self.exchange_price = 0
        self.material_pricing_method = 'avg_pullout'
        self.manufacture_result = []
        self.ui = Ui_Manufacture()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_manufacture = QDialog()
        window_manufacture.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        window_manufacture.setWindowState(Qt.WindowMaximized)
        window_manufacture.setWindowFlags(Qt.Window | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.WindowMinimizeButtonHint)  
        self.ui.setupUi(window_manufacture)
        self.language_manager.load_translated_ui(self.ui, window_manufacture)
        self.initialize(window_manufacture)
        window_manufacture.exec()

    def initialize(self, window):
        self.float_point_precision = ''
        self.fetchFloatPointPrecision()
        self.ui.working_hours_input.setValidator(QDoubleValidator())
        self.ui.produced_quantity1_input.setValidator(QDoubleValidator())
        self.ui.produced_quantity2_input.setValidator(QDoubleValidator())
        self.ui.produced_quantity3_input.setValidator(QDoubleValidator())
        self.ui.explicit_raw_materials_price_input.setValidator(QDoubleValidator())

        self.ui.manufacture_date_input.setDate(QDate.currentDate())
        self.ui.ingredients_pullout_date_input.setDate(QDate.currentDate())
        self.ui.material_production_date_input.setDate(QDate.currentDate())

        self.ui.select_cost_center_btn.clicked.connect(lambda: self.openSelectCostCenterWindow())

        self.hideColumns()

        self.ui.add_composition_material_btn.clicked.connect(lambda: self.openAddCompositionMaterialWindow())
        self.ui.select_composition_btn.clicked.connect(lambda: self.openSelectCompositionWindow())

        self.ui.produced_material_combobox.currentIndexChanged.connect(lambda: self.fetchSelectedMaterial())
        self.ui.produced_material_combobox.currentIndexChanged.connect(lambda: self.suggestNewBatchNumber())
        self.ui.mid_account_combobox.setEnabled(False)
        self.ui.mid_account_input_combobox.setEnabled(False)
        self.ui.ingredients_pullout_account_combobox.setEnabled(False)
        self.ui.output_warehouse_combobox.setEnabled(False)
        self.ui.cost_center_combobox.setEnabled(False)
        self.ui.account_combobox.setEnabled(False)
        self.ui.produced_material_combobox.setEnabled(False)
        self.ui.input_warehouse_combobox.setEnabled(False)
        # self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.getComposition())
        # self.ui.exchange_combobox.currentIndexChanged.connect(lambda: self.manufacture())

        self.ui.select_produced_material_btn.clicked.connect(lambda: self.openSelectProducedMaterialWindow())
        self.ui.material_invoices_average_till_pollout_radio.clicked.connect(lambda: self.fetchComposition())
        self.ui.material_invoices_average_radio.clicked.connect(lambda: self.fetchComposition())
        self.ui.material_last_purchase_radio.clicked.connect(lambda: self.fetchComposition())
        self.ui.material_exact_invoice_radio.clicked.connect(lambda: self.fetchComposition())

        self.ui.remove_material.clicked.connect(lambda: self.removeProducedMaterial())

        self.ui.select_pullout_account_btn.clicked.connect(lambda: self.openSelectPulloutAccountWindow())
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_mid_account_btn.clicked.connect(lambda: self.openSelectMidAccountWindow())
        self.ui.select_mid_input_account_btn.clicked.connect(lambda: self.openSelectMidAccountInputWindow())
        self.ui.select_output_warehouse_btn.clicked.connect(lambda: self.openSelectWarehouseWindow())
        self.ui.select_input_warehouse_btn.clicked.connect(lambda: self.openSelectInputWarehouseWindow())

        self.ui.ingredients_pullout_method_combobox.currentIndexChanged.connect(lambda: self.fetchComposition())

        self.ui.explicit_raw_materials_price_input.textEdited.connect(lambda: self.fetchComposition())
        self.ui.explicit_raw_materials_unit_combobox.currentIndexChanged.connect(lambda: self.fetchComposition())
        
        self.ui.manufacture_btn.clicked.connect(lambda: self.manufacture())
        self.ui.save_btn.clicked.connect(lambda: self.saveResults(window))

        self.ui.produced_quantity1_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.produced_quantity2_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.produced_quantity3_input.textEdited.connect(lambda: self.updateQuantities())

        
        # Connect functions to add_produced_material_btn
        self.ui.add_produced_material_btn.clicked.connect(lambda: self.addProducedMaterial())
        self.ui.add_produced_material_btn.clicked.connect(lambda: self.fetchComposition())
        self.ui.add_produced_material_btn.clicked.connect(lambda: self.fetchMaterialMachines())
        self.ui.add_produced_material_btn.clicked.connect(lambda: self.setAllowedUnits())

        self.ui.material_last_purchase_radio.clicked.connect(lambda: self.setIngredientsPricingParameters())
        self.ui.material_invoices_average_radio.clicked.connect(lambda: self.setIngredientsPricingParameters())
        self.ui.material_invoices_average_till_pollout_radio.clicked.connect(lambda: self.setIngredientsPricingParameters())
        self.ui.material_exact_invoice_radio.clicked.connect(lambda: self.setIngredientsPricingParameters())
        self.ui.ingredients_pullout_account_combobox.currentIndexChanged.connect(lambda: self.setIngredientsPricingParameters())
        
        self.ui.input_warehouse_combobox.currentIndexChanged.connect(lambda: self.updateMaterialWarehouse())

        self.ui.currencies_and_exchange_btn.clicked.connect(lambda: self.openCurrenciesWindow())
        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.fetchComposition())
        self.ui.currency_combobox.currentIndexChanged.connect(lambda: self.updateLinkedElement(self.ui.currency_combobox, self.ui.explicit_raw_materials_currency_combobox))
        
        
        self.ui.maximum_machine_time_radio.clicked.connect(lambda: self.fetchMaterialMachines())
        self.ui.sum_machine_times_radio.clicked.connect(lambda: self.fetchMaterialMachines())
        self.setExpensesTypes()
        self.fetchMaterials()
        self.fetchUnits()
        self.fetchSelectedMaterial()
        self.fetchCurrencies()
        self.fetchMaterialCompositions()
        self.updateQuantities()
        self.fetchAccounts()
        self.fetchWarehouses()
        self.setIngredientsPulloutMethods()
        self.fetchCostCenters()
        

        self.ui.material_invoices_average_radio.setChecked(True)
        self.setIngredientsPricingParameters()

        # if self.mode == "r":  # read-only mode, used to view previous manufacture processes
        #     # in read-only mode,UI elements are not responsive to user interactions.
        #     groupboxes_to_be_responiveless = [self.ui.quantities_groupbox, self.ui.dates_invoices_groupbox,self.ui.buttons_groupbox]
        #     for element in groupboxes_to_be_responiveless:
        #         for widget in element.findChildren(QWidget):
        #             widget.installEventFilter(self)
        #     self.viewSavedProcess()

    def fetchFloatPointPrecision(self):
        self.float_point_precision = self.database_operations.fetchFloatPointValue()


    def hideColumns(self):
        self.ui.produced_materials_tree.setColumnHidden(3, True)
        self.ui.produced_materials_tree.setColumnHidden(6, True)
        self.ui.produced_materials_tree.setColumnHidden(9, True)


    def openAddCompositionMaterialWindow(self):
        material = self.ui.produced_material_combobox.currentData()
        if material:
            Ui_GrouppedMaterialComposition_Logic(self.sql_connector, material[0]).showUi()

    def fetchMaterialCompositions(self):
        self.ui.composition_combobox.clear()
        groupped_material_id = self.ui.produced_material_combobox.currentData()[0]
        if groupped_material_id:
            compositions = self.database_operations.fetchMaterialCompositions(groupped_material_id)
            for composition in compositions:
                data = id = composition['id']
                display_text = composition['name']
                self.ui.composition_combobox.addItem(display_text, data)

    def openSelectCompositionWindow(self):
        group_material_id = self.ui.produced_material_combobox.currentData()[0]
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='compositions', group_materials_id=group_material_id)
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.composition_combobox.count()):
                if self.ui.composition_combobox.itemData(i) == result['id']:
                    self.ui.composition_combobox.setCurrentIndex(i)
                    break

    def removeProducedMaterial(self):
        current_item = self.ui.produced_materials_tree.currentItem()
        if current_item:
            self.ui.produced_materials_tree.takeTopLevelItem(self.ui.produced_materials_tree.indexOfTopLevelItem(current_item))
            self.fetchSelectedMaterial()
        self.fetchComposition()

    def fetchCostCenters(self):
        cost_centers = self.database_operations.fetchCostCenters()
        if not cost_centers:
            self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_COST_CENTERS"))
        else:
            self.ui.cost_center_combobox.clear()
            for cost_center in cost_centers:
                id = cost_center['id']
                display_text = cost_center['name']
                data = id
                self.ui.cost_center_combobox.addItem(display_text, data)


    def openSelectProducedMaterialWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector ,table_name='groupped_materials')
        result = data_picker.showUi()
        if result is not None:
            for i in range(self.ui.produced_material_combobox.count()):
                if self.ui.produced_material_combobox.itemData(i)[0] == result['id']:
                    self.ui.produced_material_combobox.setCurrentIndex(i)
                    break

    def openSelectCostCenterWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, table_name='cost_centers')
        result = data_picker.showUi()
        if result is not None:
            self.ui.cost_center_combobox.setCurrentIndex(self.ui.cost_center_combobox.findData(result['id']))

    def setExpensesTypes(self):
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("MONTHLY_COSTS"), "month")
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("YEARLY_COSTS"), "year")
        self.ui.expenses_type_combobox.addItem(self.language_manager.translate("REAL_COSTS"), "real")
    
    def updateLinkedElement(self, source_element, target_element):
        if isinstance(source_element, QCheckBox):
            target_element.setChecked(source_element.isChecked())
        elif isinstance(source_element, QComboBox):
            target_data = source_element.currentData()
            index = target_element.findData(target_data)
            if index != -1:
                target_element.setCurrentIndex(index)
        elif isinstance(source_element, QLineEdit):
            target_element.setText(source_element.text())
        elif isinstance(source_element, QTextEdit):
            target_element.setPlainText(source_element.toPlainText())
        elif isinstance(source_element, QSpinBox):
            target_element.setValue(source_element.value())
        elif isinstance(source_element, QDoubleSpinBox):
            target_element.setValue(source_element.value())
        elif isinstance(source_element, QDateEdit):
            target_element.setDate(source_element.date())
        elif isinstance(source_element, QTimeEdit):
            target_element.setTime(source_element.time())
        elif isinstance(source_element, QDateTimeEdit):
            target_element.setDateTime(source_element.dateTime())
            

    def addProducedMaterial(self):
        try:
            # Get selected material info
            material_data = self.ui.produced_material_combobox.currentData()
            if not material_data:
                self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_PRODUCED_MATERIAL_SELECTED"))
                return
            
            amount = self.ui.produced_quantity1_input.text()
            if not amount:
                self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_PRODUCED_QUANTITY_SELECTED"))
                return
            

            material_id = material_data[0]
            material_default_unit = material_data[10]
            material_name = self.ui.produced_material_combobox.currentText()

            # Check if the material already exists in the tree
            root = self.ui.produced_materials_tree.invisibleRootItem()
            existing_item = None
            for i in range(root.childCount()):
                if root.child(i).text(0) == str(material_id):
                    existing_item = root.child(i)
                    break

            if existing_item:
                # Update existing item
                top_item = existing_item
            else:
                # Create new top-level item for the material
                top_item = QtWidgets.QTreeWidgetItem(self.ui.produced_materials_tree)
                top_item.setText(0, str(material_id))
                top_item.setText(1, material_name)

            # Set light blue background for material id and name
            for i in range(14):
                top_item.setBackground(i, QtGui.QColor("#E6F3FF"))

            # Update or create standard quantities row (yellow background)
            standard_item = top_item.child(0) if top_item.childCount() > 0 else QtWidgets.QTreeWidgetItem(top_item)
            standard_item.setText(0, "Standard")
            standard_item.setText(2, self.ui.standard_quantity1_input.text() if self.ui.standard_quantity1_input.text() else "")
            standard_item.setText(3, str(self.ui.standard_unit1_combobox.currentData()) if self.ui.standard_unit1_combobox.currentData() else "")
            standard_item.setText(4, self.ui.standard_unit1_combobox.currentText() if self.ui.standard_unit1_combobox.currentText() else "")
            standard_item.setText(5, self.ui.standard_quantity2_input.text() if self.ui.standard_quantity2_input.text() else "")
            standard_item.setText(6, str(self.ui.standard_unit2_combobox.currentData()) if self.ui.standard_unit2_combobox.currentData() else "")
            standard_item.setText(7, self.ui.standard_unit2_combobox.currentText() if self.ui.standard_unit2_combobox.currentText() else "")
            standard_item.setText(8, self.ui.standard_quantity3_input.text() if self.ui.standard_quantity3_input.text() else "")
            standard_item.setText(9, str(self.ui.standard_unit3_combobox.currentData()) if self.ui.standard_unit3_combobox.currentData() else "")
            standard_item.setText(10, self.ui.standard_unit3_combobox.currentText() if self.ui.standard_unit3_combobox.currentText() else "")
            standard_item.setText(11, self.ui.standard_work_hours_input.text() if self.ui.standard_work_hours_input.text() else "0")
            standard_item.setText(12, self.ui.standard_new_batches_count.text() if self.ui.standard_new_batches_count.text() else "")
            standard_item.setText(14, str(material_default_unit) if material_default_unit is not None else "")
            
            for i in range(standard_item.columnCount()):
                standard_item.setBackground(i, QtGui.QColor("#FFFFD0"))

            # Update or create produced quantities row (orange background)
            produced_item = top_item.child(1) if top_item.childCount() > 1 else QtWidgets.QTreeWidgetItem(top_item)
            produced_item.setText(0, "Produced")
            produced_item.setText(2, self.ui.produced_quantity1_input.text() if self.ui.produced_quantity1_input.text() else "")
            produced_item.setText(3, str(self.ui.produced_unit1_combobox.currentData()) if self.ui.produced_unit1_combobox.currentData() else "")
            produced_item.setText(4, self.ui.produced_unit1_combobox.currentText() if self.ui.produced_unit1_combobox.currentText() else "")
            produced_item.setText(5, self.ui.produced_quantity2_input.text() if self.ui.produced_quantity2_input.text() else "")
            produced_item.setText(6, str(self.ui.produced_unit2_combobox.currentData()) if self.ui.produced_unit2_combobox.currentData() else "")
            produced_item.setText(7, self.ui.produced_unit2_combobox.currentText() if self.ui.produced_unit2_combobox.currentText() else "")
            produced_item.setText(8, self.ui.produced_quantity3_input.text() if self.ui.produced_quantity3_input.text() else "")
            produced_item.setText(9, str(self.ui.produced_unit3_combobox.currentData()) if self.ui.produced_unit3_combobox.currentData() else "")
            produced_item.setText(10, self.ui.produced_unit3_combobox.currentText() if self.ui.produced_unit3_combobox.currentText() else "")
            produced_item.setText(11, self.ui.working_hours_input.text() if self.ui.working_hours_input.text() else "0")
            produced_item.setText(13, self.ui.batch_number_input.text() if self.ui.batch_number_input.text() else "")
            produced_item.setText(14, str(material_default_unit) if material_default_unit is not None else "")
            for i in range(produced_item.columnCount()):
                produced_item.setBackground(i, QtGui.QColor("#FFD8C0"))

            # Expand the top-level item to show its children
            self.ui.produced_materials_tree.expandItem(top_item)
            self.fetchComposition()
        except Exception as e:
            error_message = f"⚠️ حدث خطأ أثناء إضافة المادة المنتجة: {str(e)}"
            self.ui.status_bar_label.setText(error_message)

        
    
    def fetchMaterials(self):
        self.ui.produced_material_combobox.clear()
        try:
            products = self.database_operations.fetchProducedMaterials()
            if not products:
                self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_PRODUCED_MATERIALS"))
                return
            for product in products:
                id = product.get('id')
                code = product.get('code')
                name = product.get('name')
                group = product.get('group_col')
                unit1 = product.get('unit1')
                unit2 = product.get('unit2')
                unit3 = product.get('unit3')
                default_unit = product.get('default_unit')
                work_hours = product.get('work_hours')
                standard_unit3_quantity = product.get('standard_unit3_quantity')
                standard_unit2_quantity = product.get('standard_unit2_quantity')
                standard_unit1_quantity = product.get('standard_unit1_quantity')
                unit1_to_unit2_rate = product.get('unit1_to_unit2_rate')
                unit1_to_unit3_rate = product.get('unit1_to_unit3_rate')

                material_units = [unit1, unit2, unit3]
                default_unit = material_units[default_unit-1]

                data = [id, unit1, unit2, unit3, standard_unit1_quantity, standard_unit2_quantity,standard_unit3_quantity, unit1_to_unit2_rate, unit1_to_unit3_rate, work_hours, default_unit]

                self.ui.produced_material_combobox.addItem(name, data)
                
        except Exception as e:
            error_message = f"⚠️ {self.language_manager.translate('ALERT_ERROR_FETCHING_MATERIALS')}: {str(e)}"
            self.ui.status_bar_label.setText(error_message)



    def fetchSelectedMaterial(self):
        try:
            self.ui.standard_quantity1_input.clear()
            self.ui.standard_unit1_combobox.setCurrentIndex(0)
            self.ui.produced_unit1_combobox.setCurrentIndex(0)
            self.ui.produced_quantity1_input.clear()
            
            self.ui.standard_quantity2_input.clear()
            self.ui.standard_unit2_combobox.setCurrentIndex(0)
            self.ui.produced_unit2_combobox.setCurrentIndex(0)
            self.ui.produced_quantity2_input.clear()
            
            self.ui.standard_quantity3_input.clear()
            self.ui.standard_unit3_combobox.setCurrentIndex(0)
            self.ui.produced_unit3_combobox.setCurrentIndex(0)
            self.ui.produced_quantity3_input.clear()

            material_data = self.ui.produced_material_combobox.currentData()
            if material_data:
                id = material_data[0]
                unit1 = material_data[1]
                unit2 = material_data[2]
                unit3 = material_data[3]
                standard_unit1_quantity = material_data[4]
                standard_unit2_quantity = material_data[5]
                standard_unit3_quantity = material_data[6]
                uni1_to_unit2_rate = material_data[7]
                uni1_to_unit3_rate = material_data[8]
                working_hours = material_data[9]
                default_unit = material_data[10]

                if standard_unit1_quantity:
                    self.ui.standard_quantity1_input.setText(str(float(standard_unit1_quantity)))
                    self.ui.standard_unit1_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit1))
                    self.ui.produced_unit1_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit1))
                if standard_unit2_quantity:
                    self.ui.standard_quantity2_input.setText(str(float(standard_unit2_quantity)))
                    self.ui.standard_unit2_combobox.setCurrentIndex(self.ui.standard_unit2_combobox.findData(unit2))
                    self.ui.produced_unit2_combobox.setCurrentIndex(self.ui.standard_unit2_combobox.findData(unit2))
                if standard_unit3_quantity:
                    self.ui.standard_quantity3_input.setText(str(float(standard_unit3_quantity)))
                    self.ui.standard_unit3_combobox.setCurrentIndex(self.ui.standard_unit3_combobox.findData(unit3))
                    self.ui.produced_unit3_combobox.setCurrentIndex(self.ui.standard_unit3_combobox.findData(unit3))

                if not working_hours:
                    working_hours = ''
                self.ui.standard_work_hours_input.setText(str(working_hours))
            else:
                self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_DATA_FOR_SELECTED_MATERIAL"))
        except Exception as e:
            error_message = f"⚠️ {self.language_manager.translate('ALERT_ERROR_FETCHING_MATERIALS')}: {str(e)}"
            self.ui.status_bar_label.setText(error_message)

    def setAllowedUnits(self):
        root = self.ui.produced_materials_tree.invisibleRootItem()
        unit1, unit2, unit3 = None, None, None

        for i in range(root.childCount()):
            top_item = root.child(i)
            if top_item.childCount() > 0:
                child_item = top_item.child(0)
                unit1 = child_item.text(3)
                unit2 = child_item.text(6)
                unit3 = child_item.text(9)

            enabled_options = 0
            for i in range(self.ui.radio_quantity_unit_expenses_combobox.count()):
                unit_id = self.ui.radio_quantity_unit_expenses_combobox.itemData(i)
                item = self.ui.radio_quantity_unit_expenses_combobox.model().item(i)
                if str(unit_id) not in [str(unit1), str(unit2), str(unit3)]:
                    item.setEnabled(False)
                elif item.isEnabled():
                    enabled_options += 1

            if enabled_options > 0:
                for i in range(self.ui.radio_quantity_unit_expenses_combobox.count()):
                    if self.ui.radio_quantity_unit_expenses_combobox.model().item(i).isEnabled():
                        self.ui.radio_quantity_unit_expenses_combobox.setCurrentIndex(i)
                        break
            else:
                self.ui.no_expenses_radio.setChecked(True)
                self.ui.radio_quantity_unit_expenses_combobox.setCurrentIndex(-1)

            enabled_options = 0
            for i in range(self.ui.explicit_raw_materials_unit_combobox.count()):
                unit_id = self.ui.explicit_raw_materials_unit_combobox.itemData(i)
                item = self.ui.explicit_raw_materials_unit_combobox.model().item(i)
                if str(unit_id) not in [str(unit1), str(unit2), str(unit3)]:
                    item.setEnabled(False)
                elif item.isEnabled():
                    enabled_options += 1

            if enabled_options > 0:
                for i in range(self.ui.explicit_raw_materials_unit_combobox.count()):
                    if self.ui.explicit_raw_materials_unit_combobox.model().item(i).isEnabled():
                        self.ui.explicit_raw_materials_unit_combobox.setCurrentIndex(i)
                        break

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        if not currencies:
            self.ui.status_bar_label.setText(self.language_manager.translate('ALERT_NO_CURRENCIES_DEFINED'))
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            data = id
            self.ui.currency_combobox.addItem(display_text, data)
            self.ui.explicit_raw_materials_currency_combobox.addItem(display_text, data)
            
    def fetchUnits(self):
        self.ui.standard_unit1_combobox.clear()
        self.ui.produced_unit1_combobox.clear()
        self.ui.standard_unit2_combobox.clear()
        self.ui.produced_unit2_combobox.clear()
        self.ui.standard_unit3_combobox.clear()
        self.ui.produced_unit3_combobox.clear()
        self.ui.radio_quantity_unit_expenses_combobox.clear()
        self.ui.explicit_raw_materials_unit_combobox.clear()
        self.ui.standard_unit1_combobox.addItem('', None)
        self.ui.produced_unit1_combobox.addItem('', None)
        self.ui.standard_unit2_combobox.addItem('', None)
        self.ui.produced_unit2_combobox.addItem('', None)
        self.ui.standard_unit3_combobox.addItem('', None)
        self.ui.produced_unit3_combobox.addItem('', None)
        units = self.database_operations.fetchUnits()
        if not units:
            self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_UNITS_DEFINED"))
        else:
            for unit in units:
                id = unit['id']
                display_text = unit['name']
                data = id
                self.ui.standard_unit1_combobox.addItem(display_text, data)
                self.ui.produced_unit1_combobox.addItem(display_text, data)
                self.ui.standard_unit2_combobox.addItem(display_text, data)
                self.ui.produced_unit2_combobox.addItem(display_text, data)
                self.ui.standard_unit3_combobox.addItem(display_text, data)
                self.ui.produced_unit3_combobox.addItem(display_text, data)
                self.ui.radio_quantity_unit_expenses_combobox.addItem(display_text, data)
                self.ui.explicit_raw_materials_unit_combobox.addItem(display_text, data)
                
    def fetchComposition(self):
        self.ui.composition_tree.clear()

        # Get all produced material IDs from the produced_materials_tree
        produced_material_ids = []
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            produced_material_id = item.text(0)
            produced_material_ids.append(produced_material_id)

        if not produced_material_ids:
            self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_PRODUCED_MATERIALS"))
            return
        else:
            self.ui.status_bar_label.setText("")

        manufacture_process_date = self.ui.manufacture_date_input.date().toString(Qt.ISODate)
        ingredients_pullout_date = self.ui.ingredients_pullout_date_input.date().toString(Qt.ISODate)
        manufacture_currency = self.ui.currency_combobox.currentData()
        manufacture_currency_text = self.ui.currency_combobox.currentText()

        all_ingredients = {}
        warning = ""
        composition_id = self.ui.composition_combobox.currentData() or ''
        for product_id in produced_material_ids:
            ingredients = self.database_operations.fetchComposition(product_id, composition_id)

            if not ingredients:
                warning = f"⚠️ {self.language_manager.translate('ALERT_NO_COMPOSITION_FOR_PRODUCT')}: {product_id}"
                continue

            # Get standard and produced quantities for this product
            product_item = root.child(produced_material_ids.index(product_id))
            standard_quantities = [product_item.child(0).text(2), product_item.child(0).text(5), product_item.child(0).text(8)]
            produced_quantities = [product_item.child(1).text(2), product_item.child(1).text(5), product_item.child(1).text(8)]

            index_with_value_on_both_lists = next((i for i in range(3) if standard_quantities[i] != '' and produced_quantities[i] != ''), None)

            if index_with_value_on_both_lists is not None:
                fraction = float(produced_quantities[index_with_value_on_both_lists]) / float(standard_quantities[index_with_value_on_both_lists])
            else:
                fraction = 0

            for ingredient in ingredients:
                id = ingredient.get('id')
                material_name = ingredient.get('name')
                material_id = ingredient.get('composition_material_id')
                quantity = ingredient.get('quantity')
                unit = ingredient.get('unit')
                material_code = ingredient.get('code')
                unit_name = ingredient.get('unit_name')
                quantity_required = float(quantity) * float(fraction)

                if material_id in all_ingredients:
                    if all_ingredients[material_id]['unit']==unit:
                        all_ingredients[material_id]['quantity_required'] += quantity_required
                    else:
                        converstion_rate = self.database_operations.fetchUnitConversionValueBetween(all_ingredients[material_id]['unit'], unit)
                        if converstion_rate:
                            all_ingredients[material_id]['quantity_required'] += quantity_required*converstion_rate
                else:
                    all_ingredients[material_id] = {
                        'id': id,
                        'material_name': material_name,
                        'quantity': quantity,
                        'unit': unit,
                        'material_code': material_code,
                        'unit_name': unit_name,
                        'quantity_required': quantity_required
                    }
            
        # Fill the material_warehouses_table with produced materials
        self.ui.material_warehouses_table.setRowCount(0)
        for i, product_id in enumerate(produced_material_ids):
            product_item = root.child(i)
            material_name = product_item.text(1)
            
            # Add a new row
            row = self.ui.material_warehouses_table.rowCount()
            self.ui.material_warehouses_table.insertRow(row)
            
            # Set material name in first column
            material_name_item = QTableWidgetItem(material_name)
            material_name_item.setData(Qt.UserRole, product_id)
            self.ui.material_warehouses_table.setItem(row, 0, material_name_item)
            material_id_item = QTableWidgetItem(product_id)
            self.ui.material_warehouses_table.setItem(row, 1, material_id_item)
            
            # Create warehouse combobox for second column
            warehouse_combobox = QComboBox()
            warehouses = self.database_operations.fetchWarehouses()
            if warehouses:
                for warehouse in warehouses:
                    warehouse_id = warehouse['id']
                    warehouse_name = warehouse['name']
                    warehouse_combobox.addItem(warehouse_name, warehouse_id)
            
            # Connect signal to update values when warehouse changes
            # warehouse_combobox.currentIndexChanged.connect(
            #     lambda r=row: self.updateMaterialWarehouseSelection(r)
            # )
            
            # Add combobox to the table
            self.ui.material_warehouses_table.setCellWidget(row, 2, warehouse_combobox)

        if not all_ingredients:
            self.ui.status_bar_label.setText(self.language_manager.translate("ALERT_NO_COMPOSITION_FOR_PRODUCT"))
            return
        else:
            self.ui.status_bar_label.setText("")

        ingredients_details = {}
        warning = ""
        for material_id, ingredient in all_ingredients.items():
            quantity_required = ingredient['quantity_required']
            unit = ingredient['unit']

            materials_pullout_method = self.ui.ingredients_pullout_method_combobox.currentData()
            sort = 'desc' if str(materials_pullout_method).lower() == 'lifo' else 'asc'

            if self.ui.material_explicit_value_radio.isChecked():
                material_warehouses = self.database_operations.fetchMaterialWarehouses(material_id, sort=sort)
            else:
                material_warehouses = self.database_operations.fetchMaterialWarehouses(material_id, material_source='invoice', sort=sort)
            if not material_warehouses:
                warning = f"⚠️ {self.language_manager.translate('ALERT_NO_WAREHOUSES_FOR_MATERIAL')}: {ingredient['material_name']}"
                continue

            still_required = quantity_required
            for warehouse_id, data_list in material_warehouses.items():
                for data in data_list:
                    warehouse_entry_id = data['id']
                    warehouse_entry_material_id = data['material_id']
                    warehouse_entry_quantity = data['quantity']
                    warehouse_entry_unit = data['unit']
                    manufacture_id = data['production_batch_id']
                    receipt_doc_id = data['receipt_doc_id']
                    batch_number = data['batch_number']
                    batch_mfg = data['batch_mfg']
                    batch_exp = data['batch_exp']
                    warehouse_entry_invoice_item_id = data['invoice_item_id']
                    invoice_id = data['invoice_id']
                    invoice_date = data['invoice_date']
                    manufacture_date = data['manufacture_date']
                    warehouse_name = data['warehouse_name']
                    warehouse_id = warehouse_id
                    quantity_check_warehouse_account = data['warehouse_account_id']

                    invoice_item_unit_price = None
                    if self.ui.material_exact_invoice_radio.isChecked():   
                        invoice_item_data = self.database_operations.fetchInvoiceItem(warehouse_entry_invoice_item_id)
                        if invoice_item_data:
                            invoice_item_id = invoice_item_data[0]
                            invoice_item_material_id = invoice_item_data['material_id']
                            invoice_item_name = invoice_item_data['name']
                            invoice_item_unit_price = invoice_item_data['unit_price']
                            invoice_item_quantity1 = invoice_item_data['quantity1']
                            invoice_item_unit1_id = invoice_item_data['unit1_id']
                            invoice_item_unit_name = invoice_item_data['unit_name']
                            invoice_item_currency_id = invoice_item_data['currency_id']
                            invoice_item_invoice_date = invoice_item_data['invoice_date']
                            invoice_item_currency_name = invoice_item_data['currency_name']

                            if not invoice_item_unit_price:
                                warning = f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_MATERIAL')}: {invoice_item_name}"
                                return

                            if str(invoice_item_currency_id) != str(manufacture_currency):
                                exchange_value = self.database_operations.fetchExchangeValue(
                                    invoice_item_currency_id, manufacture_currency, invoice_item_invoice_date)
                                if exchange_value:
                                    invoice_item_unit_price = round((invoice_item_unit_price * float(exchange_value[0][1])), 4)
                                else:
                                    warning = f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_MATERIAL')}: {invoice_item_name}"         
                                    continue

                    if int(warehouse_entry_unit) != int(unit):
                        unit_conversion_rate = self.database_operations.fetchUnitConversionValueBetween(
                            warehouse_entry_unit, unit)
                        if unit_conversion_rate:
                            warehouse_entry_quantity = unit_conversion_rate * warehouse_entry_quantity
                        else:
                            warning = f"{self.language_manager.translate('ALERT_ERROR_CONVERTING_UNITS')}"
                            self.ui.composition_tree.clear()
                            continue

                    total_price = round((float(invoice_item_unit_price) * float(warehouse_entry_quantity)), 4) if invoice_item_unit_price else ''
                    quantity_to_use = min(float(warehouse_entry_quantity), float(still_required))

                    if material_id not in ingredients_details:
                        ingredients_details[material_id] = []

                    ingredients_details[material_id].append([
                        warehouse_id,
                        warehouse_name,
                        warehouse_entry_id,
                        warehouse_entry_quantity,
                        quantity_to_use,
                        unit,
                        manufacture_id,
                        warehouse_entry_invoice_item_id,
                        ingredient['material_code'],
                        ingredient['material_name'],
                        quantity_check_warehouse_account,
                        invoice_item_unit_price,
                        total_price,
                        manufacture_currency
                    ])

                    still_required -= quantity_to_use
                    if still_required <= 0:
                        break

                if still_required <= 0:
                    break
            total_pulledout_quantity = quantity_required - still_required

            unit_cost, cost = '', ''

            # 1- get the average price of the material from invoices

            if self.ui.material_invoices_average_radio.isChecked():
                self.material_pricing_method = 'avg_invoice'

                invoice_type = self.database_operations.fetchInvoiceTypes(name='buy')
                invoice_type=invoice_type[0]['id']

                average_price = self.database_operations.fetchAverageMaterialPrice(material_id, targeted_currency=manufacture_currency, to_date='9999-12-12', invoice_type=invoice_type,from_date='2000-01-01', currency_exchage_date=manufacture_process_date, targeted_unit=unit)
                if average_price:
                    cost = round((average_price * quantity_required), 4)
                    unit_cost = average_price
                else:
                    warning = f"{self.language_manager.translate('ALERT_NO_AVERAGE_INVOICE_PRICE')}"
                    self.ui.composition_tree.clear()
                    continue

            # 2- get the average price of the material from invoices till the pullout date

            elif self.ui.material_invoices_average_till_pollout_radio.isChecked():
                self.material_pricing_method = 'avg_invoice'

                invoice_type = self.database_operations.fetchInvoiceTypes(name='buy')
                invoice_type=invoice_type[0]['id']

                average_price = self.database_operations.fetchAverageMaterialPrice(material_id, targeted_currency=manufacture_currency, to_date=ingredients_pullout_date, invoice_type=invoice_type, currency_exchage_date=manufacture_process_date, targeted_unit=unit)
                if average_price:
                    cost = round((float(average_price) * float(quantity_required)), 4)
                else:
                    warning = f"{self.language_manager.translate('ALERT_NO_AVERAGE_INVOICE_PRICE')}"
                    self.ui.composition_tree.clear()
                    continue
                
            # 3- get the last purchase price of the material from invoices

            elif self.ui.material_last_purchase_radio.isChecked():
                self.material_pricing_method = 'last_invoice'
                manufacture_date = self.ui.manufacture_date_input.date().toString(QtCore.Qt.ISODate)
                price_data = self.database_operations.fetchLastInvoiceOfMaterial(material_id)
                if price_data:
                    quantity1 = price_data['quantity1']
                    quantity2 = price_data['quantity2']
                    quantity3 = price_data['quantity3']
                    unit1_id = price_data['unit1_id']
                    unit2_id = price_data['unit2_id']
                    unit3_id = price_data['unit3_id']
                    average_price_in_payment_currency = price_data['equilivance_price']
                    average_price_in_invoice_currency = price_data['unit_price']
                    payment_currency = price_data['payment_currency']
                    invoice_currency = price_data['invoice_currency']
                    invoice_date = price_data['date_col']
                    invoice_item_id = price_data['invoice_item_id']
                    invoice_id = price_data['invoices_id']

                    material_move_id = self.database_operations.fetchMaterialMove(origin='invoice',origin_id=invoice_item_id)

                    if material_move_id:
                        warehouse_data = self.database_operations.fetchInvoiceItemWarehouse(material_move_id['id'])
                        if warehouse_data and len(warehouse_data) > 0:
                            warehouse_quantity = warehouse_data[0]
                            warehouse_unit = warehouse_data[1]
                            warehouse_id = warehouse_data[2]
                            warehouse_name = warehouse_data[3]
                            warehouse_account_id = warehouse_data[4]
                            if float(warehouse_quantity) < float(quantity_required):
                                warning = f"{self.language_manager.translate('ALERT_REMAINING_QUANTITY_LESS_THAN_REQUIRED')}"
                                self.ui.composition_tree.clear()
                                continue
                        
                        else:
                            warning = f"{self.language_manager.translate('ALERT_NO_WAREHOUSE_FOR_MATERIAL')}"
                            self.ui.composition_tree.clear()
                            continue

                    price = 0
                    if unit in [unit1_id, unit2_id, unit3_id]:
                        if payment_currency == manufacture_currency:
                            price = average_price_in_payment_currency
                        elif invoice_currency == manufacture_currency:
                            price = average_price_in_invoice_currency
                        else:
                            exchange_value = self.database_operations.fetchExchangeValue(payment_currency, manufacture_currency, invoice_date)
                            if exchange_value:
                                price = average_price_in_payment_currency * float(exchange_value[0][1])
                            else:
                                exchange_value = self.database_operations.fetchExchangeValue(invoice_currency, manufacture_currency, invoice_date)
                                if exchange_value:
                                    price = average_price_in_invoice_currency * float(exchange_value[0][1])
                                else:
                                    warning = f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_INVOICE_ITEM_AND_MANUFACTURE_CURRENCY')}"
                                    self.ui.composition_tree.clear()
                                    continue

                        if unit == unit1_id:
                            unit_cost = float(price) / quantity1
                        elif unit == unit2_id:
                            unit_cost = float(price) / quantity2
                        elif unit == unit3_id:
                            unit_cost = float(price) / quantity3
                        cost = round((unit_cost * quantity_required), 4)
                else:
                    warning = f"{self.language_manager.translate('ALERT_NO_AVERAGE_INVOICE_PRICE')}"
                    self.ui.composition_tree.clear()
                    continue

            elif self.ui.material_explicit_value_radio.isChecked():
                explicit_price = self.ui.explicit_raw_materials_price_input.text()
                explicit_unit = self.ui.explicit_raw_materials_unit_combobox.currentData()
                explicit_unit_name = self.ui.explicit_raw_materials_unit_combobox.currentText()

                if explicit_price and explicit_unit:
                    try:
                        explicit_price = float(explicit_price)
                    except ValueError:
                        warning = f"{self.language_manager.translate('ALERT_INVALID_RAW_MATERIAL_PRICE')}"
                        self.ui.composition_tree.clear()
                        return

                    if explicit_unit == unit:
                        unit_cost = explicit_price
                    else:
                        converstion_rate = self.database_operations.fetchUnitConversionValueBetween(explicit_unit, unit)
                        if converstion_rate:
                            unit_cost = converstion_rate*explicit_price
                        else:
                            warning = f"{self.language_manager.translate('ALERT_CANNOT_CONVERT_UNITS')}: {explicit_unit_name}"
                            self.ui.composition_tree.clear()
                            continue

                    cost = round((unit_cost * quantity_required), 4)
                else:
                    warning = f"{self.language_manager.translate('ALERT_CHECK_ALL_REQUIRED_VALUES')}"
                    self.ui.composition_tree.clear()
                    continue
            
            root_item = QTreeWidgetItem([
                str(ingredient['id']), str(ingredient['material_code']), str(ingredient['material_name']),
                str(round(float(ingredient['quantity']), int(self.float_point_precision))), str(ingredient['unit']), str(ingredient['unit_name']),
                str(round(float(quantity_required), int(self.float_point_precision))), str(ingredient['unit']), str(ingredient['unit_name']),
                str(round(float(unit_cost), int(self.float_point_precision))) if unit_cost != '' else '', str(round(float(cost), int(self.float_point_precision))) if cost != '' else '', str(manufacture_currency), str(manufacture_currency_text),
                '', '', '', '', '', '', str(total_pulledout_quantity), str(still_required)
            ])
            root_item.setExpanded(True)

            if self.ui.material_exact_invoice_radio.isChecked():
                if ingredients_details:
                    for ingredient_warehouse in ingredients_details[material_id]:
                        quantity_check_warehouse_id = ingredient_warehouse[0]
                        quantity_check_warehouse_name = ingredient_warehouse[1]
                        warehouse_entry_id = ingredient_warehouse[2]
                        warehouse_entry_quantity = ingredient_warehouse[3]
                        pulled_quantity = ingredient_warehouse[4]
                        unit = ingredient_warehouse[5]
                        warehouse_entry_production_batch_id = ingredient_warehouse[6]
                        warehouse_entry_invoice_item_id = ingredient_warehouse[7]
                        warehouse_entry_code = ingredient_warehouse[8]
                        warehouse_entry_name = ingredient_warehouse[9]
                        quantity_check_warehouse_account = ingredient_warehouse[10]
                        unit_cost = ingredient_warehouse[11]
                        cost = ingredient_warehouse[12]
                        currency = ingredient_warehouse[13]
    
                        item = QTreeWidgetItem(['', '', '', '', '', '', '', '', '', str(unit_cost), str(round(float(cost), int(self.float_point_precision))) if cost != '' else '', '', '', str(quantity_check_warehouse_id) , str(quantity_check_warehouse_name), str(quantity_check_warehouse_account), str(warehouse_entry_quantity), str(unit), str(ingredient['unit_name']),str(round(float(pulled_quantity), int(self.float_point_precision))) if pulled_quantity != '' else ''])
                        root_item.addChild(item)

            if still_required <= 0:
                for i in range(self.ui.composition_tree.columnCount()):
                    root_item.setBackground(i, light_green_color)
            else:
                for i in range(self.ui.composition_tree.columnCount()):
                    root_item.setBackground(i, light_red_color)

            self.ui.composition_tree.addTopLevelItem(root_item)

        if warning:
            self.ui.status_bar_label.setText(warning)
        else:
            self.ui.status_bar_label.setText("")

        self.materials_costs_dict = ingredients_details
        print(self.materials_costs_dict)


    def updateMaterialWarehouse(self):
        selected_warehouse_id = self.ui.input_warehouse_combobox.currentData()
        
        # Update all warehouse comboboxes in the material_warehouses_table
        for row in range(self.ui.material_warehouses_table.rowCount()):
            warehouse_combobox = self.ui.material_warehouses_table.cellWidget(row, 2)
            if isinstance(warehouse_combobox, QComboBox):
                index = warehouse_combobox.findData(selected_warehouse_id)
                if index >= 0:
                    warehouse_combobox.setCurrentIndex(index)
        

    def updateQuantities(self):
        material_data = self.ui.produced_material_combobox.currentData()
        if material_data:
            id = material_data[0]
            unit1 = material_data[1]
            unit2 = material_data[2]
            unit3 = material_data[3]
            standard_unit1_quantity = material_data[4]
            standard_unit2_quantity = material_data[5]
            standard_unit3_quantity = material_data[6]
            unit1_to_unit2_rate = material_data[7]
            unit1_to_unit3_rate = material_data[8]
            working_hours = material_data[9]
            default_unit = material_data[10]

            caller = self.sender().objectName()  # the object that fired this function

            quantity1 = self.ui.produced_quantity1_input.text()
            quantity2 = self.ui.produced_quantity2_input.text()
            quantity3 = self.ui.produced_quantity3_input.text()
            standard_work_hours = self.ui.standard_work_hours_input.text()
            standard_quantity1 = self.ui.standard_quantity1_input.text()
            standard_quantity2 = self.ui.standard_quantity2_input.text()
            standard_quantity3 = self.ui.standard_quantity3_input.text()

            suggested_work_hours = None
            standart_produced_batches_count = None

            if str(caller).lower() == 'produced_quantity1_input':
                if quantity1:
                    if unit1_to_unit2_rate:
                        quantity2 = float(quantity1) * float(unit1_to_unit2_rate)
                        self.ui.produced_quantity2_input.setText(str(round(quantity2,4)))

                    if unit1_to_unit3_rate:
                        quantity3 = float(quantity1) * float(unit1_to_unit3_rate)
                        self.ui.produced_quantity3_input.setText(str(round(quantity3, 4)))

                if quantity1 and standard_quantity1:
                    standart_produced_batches_count = float(quantity1) / float(standard_quantity1)
                    if standard_work_hours:
                        suggested_work_hours = float(standard_work_hours) * float(quantity1) / float(standard_quantity1)

            elif str(caller).lower() == 'produced_quantity2_input':
                if quantity2:
                    if unit1_to_unit2_rate:
                        quantity1 = float(quantity2) * (1 / float(unit1_to_unit2_rate))
                        self.ui.produced_quantity1_input.setText(str(round(quantity1, 4)))

                    if unit1_to_unit3_rate and float(unit1_to_unit2_rate) != '':
                        unit2_to_unit3_rate = (1 / float(unit1_to_unit2_rate)) / (1 / float(unit1_to_unit3_rate))
                        quantity3 = float(quantity2) * unit2_to_unit3_rate
                        self.ui.produced_quantity3_input.setText(str(round(quantity3, 4)))

                if quantity2 and standard_quantity2:
                    standart_produced_batches_count = float(quantity1) / float(standard_quantity1)
                    if standard_work_hours:
                        suggested_work_hours = float(standard_work_hours) * float(quantity2) / float(standard_quantity2)

            elif str(caller).lower() == 'produced_quantity3_input':
                if quantity3 and float(unit1_to_unit3_rate):
                    quantity1 = float(quantity3) * (1 / float(unit1_to_unit3_rate))
                    self.ui.produced_quantity1_input.setText(str(round(quantity1, 4)))

                if unit1_to_unit2_rate and float(unit1_to_unit3_rate):
                    unit3_to_unit2_rate = unit1_to_unit2_rate / float(unit1_to_unit3_rate)
                    quantity2 = float(quantity3) * unit3_to_unit2_rate
                    self.ui.produced_quantity2_input.setText(str(round(quantity2, 4)))

                if quantity3 and standard_quantity3:
                    standart_produced_batches_count = float(quantity1) / float(standard_quantity1)
                    if standard_work_hours:
                        suggested_work_hours = float(standard_work_hours) * float(quantity3) / float(standard_quantity3)

            if suggested_work_hours:
                self.ui.working_hours_input.setText(str(suggested_work_hours))
            if standart_produced_batches_count:
                self.ui.standard_new_batches_count.setText(str(standart_produced_batches_count))

    def suggestNewBatchNumber(self):
        material_data = self.ui.produced_material_combobox.currentData()
        new_produced_batch_number = 1
        if material_data:
            id = material_data[0]
            unit1 = material_data[1]
            unit2 = material_data[2]
            unit3 = material_data[3]
            standard_unit1_quantity = material_data[4]
            standard_unit2_quantity = material_data[5]
            standard_unit3_quantity = material_data[6]
            unit1_to_unit2_rate = material_data[7]
            unit1_to_unit3_rate = material_data[8]
            working_hours = material_data[9]
            default_unit = material_data[10]
            batches = self.database_operations.fetchManufactureProcessesOfMaterial(
                id)  # to get previously manufactured batches
            if batches:
                batch_values = [batch['batch'] for batch in batches]
                if batch_values:
                    last_batch_number = max(batch_values)
                    new_produced_batch_number = int(float(last_batch_number) + 1)
            self.ui.batch_number_input.setText(str(new_produced_batch_number))

    def openCurrenciesWindow(self):
        Ui_Currencies_Logic(self.sql_connector).showUi()
    

    def fetchMaterialMachines(self):
        self.ui.machines_table.setRowCount(0)
        delegate = MyCustomTableCellDelegate(col=6, row=None, condition=[None, 5, 'No'])
        self.ui.machines_table.setItemDelegate(delegate)

        root = self.ui.produced_materials_tree.invisibleRootItem()
        time_overlap_mode = "sum" if self.ui.sum_machine_times_radio.isChecked() else "maximum"

        produced_materials_count = root.childCount()
        machine_usage_count = {}  # To track how many materials use each machine
        machine_usage_details = {}  # To track details of machine usage

        for i in range(produced_materials_count):
            material_item = root.child(i)
            material_id = material_item.text(0)
            material_name = material_item.text(1)
            
            if material_id and material_id != '':
                try:
                    machines = self.database_operations.fetchMaterialMachines(material_id)
                except Exception as e:
                    error_message = f"{self.language_manager.translate('ALERT_ERROR_FETCHING_MACHINES')}: {str(e)}"
                    self.ui.status_bar_label.setText(error_message)
                    continue

                if not machines:
                    warning_message = f"{self.language_manager.translate('ALERT_NO_MACHINES_FOR_MATERIAL')}: {material_name}"
                    self.ui.status_bar_label.setText(warning_message)
                    continue

                for machine in machines:
                    id = machine['id']
                    material_id = machine['material_id']
                    machine_id = machine['machine_id']
                    mode_id = machine['mode_id']
                    usage_duration = machine['usage_duration']
                    exclusive = machine['exclusive']
                    machine_name = machine['machine_name']
                    mode_name = machine['mode_name']
                    account_id = machine['account_id']
                    account_name = machine['account_name']
                    opposite_account_id = machine['opposite_account_id']
                    opposite_account_name = machine['opposite_account_name']

                    if exclusive != 1:
                        machine_usage_count[machine_id] = machine_usage_count.get(machine_id, 0) + 1

                    if machine_id not in machine_usage_details:
                        machine_usage_details[machine_id] = []

                    machine_usage_details[machine_id].append((machine_id, machine_name, mode_id, mode_name, usage_duration, exclusive, account_id, account_name, opposite_account_id, opposite_account_name))

        added_exclusive_machines = set()
        for machine_id, details in machine_usage_details.items():
            usage_count = machine_usage_count.get(machine_id, 1)
            if time_overlap_mode == "maximum":
                max_usage_duration = max((detail[4] for detail in details if detail[5] != 1), default=0)
                for i in range(len(details)):
                    if details[i][5] != 1:
                        details[i] = details[i][:4] + (max_usage_duration,) + details[i][5:]
            elif time_overlap_mode == "sum":
                total_usage_duration = sum(detail[4] for detail in details if detail[5] != 1)
                for i in range(len(details)):
                    if details[i][5] != 1:
                        details[i] = details[i][:4] + (total_usage_duration,) + details[i][5:]

            for detail in details:
                machine_id = detail[0]
                machine_name = detail[1]
                mode_id = detail[2]
                mode_name = detail[3]
                usage_duration = detail[4]
                usage_duration_hours = round(int(usage_duration) / 60, int(self.float_point_precision))
                exclusive = detail[5]
                account_id = detail[6] or ''
                account_name = detail[7] or ''
                opposite_account_id = detail[8] or ''
                opposite_account_name = detail[9] or ''
                if exclusive == 1 and machine_id in added_exclusive_machines:
                    continue
                usage_percentage = 100.0 if exclusive == 1 else 100.0 / usage_count
                numRows = self.ui.machines_table.rowCount()
                self.ui.machines_table.insertRow(numRows)

                # Add text to the row
                self.ui.machines_table.setItem(numRows, 0, QTableWidgetItem(str(machine_id)))
                self.ui.machines_table.setItem(numRows, 1, QTableWidgetItem(str(machine_name)))
                self.ui.machines_table.setItem(numRows, 2, QTableWidgetItem(str(mode_id)))
                self.ui.machines_table.setItem(numRows, 3, QTableWidgetItem(str(mode_name)))
                self.ui.machines_table.setItem(numRows, 4, MyTableWidgetItem(str(usage_duration_hours), int(usage_duration_hours)))
                self.ui.machines_table.setItem(numRows, 5, MyTableWidgetItem(str(usage_duration), int(usage_duration)))
                self.ui.machines_table.setItem(numRows, 6, QTableWidgetItem(str(exclusive)))
                self.ui.machines_table.setItem(numRows, 7, QTableWidgetItem(str(usage_percentage)))
                self.ui.machines_table.setItem(numRows, 8, QTableWidgetItem(str(account_id))) 
                self.ui.machines_table.setItem(numRows, 9, QTableWidgetItem(str(account_name)))
                self.ui.machines_table.setItem(numRows, 10, QTableWidgetItem(str(opposite_account_id)))
                self.ui.machines_table.setItem(numRows, 11, QTableWidgetItem(str(opposite_account_name)))

                if exclusive == 1:
                    added_exclusive_machines.add(machine_id)
    
    def manufacture(self):
        self.machines_operation_costs_dict.clear()
        currency_id = self.ui.currency_combobox.currentData()
        currency_text = self.ui.currency_combobox.currentText()
        fraction = 0

        # Get all produced material IDs from the produced_materials_tree
        produced_material_ids = []
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            produced_material_id = item.text(0)
            produced_material_ids.append(produced_material_id)
                
        for product_id in produced_material_ids:
            # Get standard and produced quantities for this product
            product_item = root.child(produced_material_ids.index(product_id))
            standard_quantities_and_units = [(product_item.child(0).text(2), product_item.child(0).text(3)), 
                                   (product_item.child(0).text(5), product_item.child(0).text(6)), 
                                   (product_item.child(0).text(8), product_item.child(0).text(9))]
            produced_quantities_and_units = [(product_item.child(1).text(2), product_item.child(1).text(3)), 
                                   (product_item.child(1).text(5), product_item.child(1).text(6)), 
                                   (product_item.child(1).text(8), product_item.child(1).text(9))]
            
            batch = product_item.child(1).text(11)

            index_with_value_on_both_lists = next((i for i in range(3) if standard_quantities_and_units[i] != '' and produced_quantities_and_units[i] != ''), None)

            if index_with_value_on_both_lists is not None:
                try:
                    fraction = float(produced_quantities_and_units[index_with_value_on_both_lists][0]) / float(standard_quantities_and_units[index_with_value_on_both_lists][0])
                except ValueError:
                    self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_PRODUCED_QUANTITY')}")
                    return

        if not fraction:
            self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_NO_PRODUCED_QUANTITY_DEFINED')}")
            return
        else:
            expenses_type = self.ui.expenses_type_combobox.currentData()
            quantity_expenses = self.ui.quantity_expenses_radio.isChecked()
            hours_expenses = self.ui.hours_expenses_radio.isChecked()
            quantity_expenses_target_unit = self.ui.radio_quantity_unit_expenses_combobox.currentData()
            working_hours = self.ui.working_hours_input.text()

            manufacture_currency = self.ui.currency_combobox.currentData()
            manufacture_date = self.ui.manufacture_date_input.date()
            raw_materials_total_cost = 0
            machines_operation_cost = 0
            salaries_cost = 0
            total_expenses = 0  # when using hourly or unitly expenses


            # Loop through the top-level items (rows)
            for row in range(self.ui.composition_tree.topLevelItemCount()):
                item = self.ui.composition_tree.topLevelItem(row)
                material_id = item.text(0)
                total_cost = 0
                if self.ui.material_exact_invoice_radio.isChecked():
                    for child_row in range(item.childCount()):
                        child_item = item.child(child_row)
                        total_cost = child_item.text(10)
                else:
                    total_cost = item.text(10)
                try:
                    raw_materials_total_cost += float(total_cost)
                except ValueError:
                    self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_RAW_MATERIALS_COST')}: {material_id}")
                    return

            if str(expenses_type).lower() == "real":  # real machines operation costs and salaries cost
                # Machines cost
                for row in range(self.ui.machines_table.rowCount()):
                    machine_id = self.ui.machines_table.item(row, 0).text()
                    machine_name = self.ui.machines_table.item(row, 1).text()
                    mode_id = self.ui.machines_table.item(row, 2).text()
                    mode_name = self.ui.machines_table.item(row, 3).text()
                    usage_duration_hours = self.ui.machines_table.item(row, 4).text()
                    usage_duration_minutes = self.ui.machines_table.item(row, 5).text()
                    exclusive = self.ui.machines_table.item(row, 6).text()
                    usage_percentage = self.ui.machines_table.item(row, 7).text()
                    account_id = self.ui.machines_table.item(row, 8).text()
                    account_name = self.ui.machines_table.item(row, 9).text()
                    opposite_account_id = self.ui.machines_table.item(row, 10).text()
                    opposite_account_name = self.ui.machines_table.item(row, 11).text()

                    mode_costs = self.database_operations.fetchModeCosts(mode_id)
                    for cost in mode_costs:
                        consumption_per_hour = cost[0]
                        unit = cost[1]
                        cost_per_minute = cost[2]
                        currency_id = cost[3]
                        resource_account_id = cost[4]
                        resource_name = cost[5]
                        resource_id = cost[6]

                        try:
                            consumption_per_usage = float(consumption_per_hour) * float(usage_duration_hours)
                            if str(exclusive).lower() == 'no':
                                consumption_per_usage = consumption_per_usage * float(usage_percentage) / 100

                            cost_per_usage = float(cost_per_minute) * float(usage_duration_minutes) * 60
                        except ValueError:
                            self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_MACHINE_COST')}: {machine_name}")
                            return

                        if currency_id != manufacture_currency:
                            exchange_value = self.database_operations.fetchExchangeValue(currency_id, manufacture_date.toString(Qt.ISODate))

                            if exchange_value:
                                cost_per_usage = cost_per_usage * float(exchange_value[0][1])
                            else:
                                win32api.MessageBox(0, f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_MACHINE_COST')}: {machine_name}", "تنبيه")
                                self.ui.composition_tree.clear()  # costing would be wrong, so don't add any items to the table
                                return

                        if resource_account_id in self.machines_operation_costs_dict:
                            # If the ID is already in the dictionary, update the price and currency_id in the existing list
                            existing_entry = self.machines_operation_costs_dict[resource_id]
                            existing_entry[0] += cost_per_usage  # Sum the price
                            existing_entry[1] = manufacture_currency  # Update the currency_id
                            existing_entry[2] = resource_account_id
                            existing_entry[3] = resource_name
                            existing_entry[4] = resource_account_id
                            existing_entry[5] = machine_name
                        else:
                            # If the ID is not in the dictionary, create a new entry with a list containing [price, currency_id]
                            self.machines_operation_costs_dict[resource_id] = [cost_per_usage, manufacture_currency,resource_account_id, resource_name, resource_account_id, machine_name]

                        machines_operation_cost += cost_per_usage
            ##########################################################################################################

                # Salaries cost
                start_date = self.ui.manufacture_date_input.date()
                work_hours = self.ui.standard_work_hours_input.text()
                if not work_hours:
                    self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_NO_WORK_HOURS_DEFINED')}")
                else:
                    try:
                        work_hours = float(work_hours)
                        work_duration = timedelta(hours=work_hours)
                        end_date = start_date.toPyDate() + work_duration
                        standard_work_hours_per_day = self.database_operations.fetchHRSetting('setting_day_hours')
                        standard_work_hours_per_day = standard_work_hours_per_day[0] if standard_work_hours_per_day else 0
                        if standard_work_hours_per_day == 0 or '':
                            self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_NO_WORK_HOURS_PER_DAY_DEFINED')}")
                        payrolls_details = self.database_operations.fetchPayrollDetails(
                            from_date=start_date.toString(Qt.ISODate), to_date=end_date.strftime('%Y-%m-%d'),
                            statement='paid_value', super=True)
                        for data in payrolls_details:
                            id = data[0]
                            salary_block_id = data[1]
                            employee_id = data[2]
                            statement = data[3]
                            value = data[4]
                            currency_id = data[5]
                            name = data[6]
                            currency_name = data[7]
                            from_date = data[8]
                            to_date = data[9]
                            account_id = data[10]

                            if currency_id != manufacture_currency:
                                exchange_value = self.database_operations.fetchExchangeValue(currency_id,manufacture_currency,manufacture_date.toString(Qt.ISODate))
                                if exchange_value:
                                    value = value * float(exchange_value[0][1])
                                else:
                                    win32api.MessageBox(0,f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_SALARIES')}: {name}", "تنبيه")
                                    self.ui.composition_tree.clear()  # costing would be wrong, so don't add any items to the tree
                                    return

                            if account_id in self.salaries_costs_dict:
                                # If the ID is already in the dictionary, update the price and currency_id in the existing list
                                existing_entry = self.salaries_costs_dict[account_id]
                                existing_entry[0] += value  # Sum the price
                                existing_entry[1] = manufacture_currency  # Update the currency_id
                            else:
                                # If the ID is not in the dictionary, create a new entry with a list containing [price, currency_id]
                                self.salaries_costs_dict[account_id] = [value, manufacture_currency]

                            try:
                                days_count = (to_date - from_date).days
                                salary_per_day = float(value) / float(days_count)
                                salary_per_hour = salary_per_day / float(standard_work_hours_per_day)
                                fraction = float(working_hours) / float(standard_work_hours_per_day)
                                cost = float(salary_per_hour) * float(fraction)
                                salaries_cost += cost
                            except ValueError:
                                self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_SALARIES_COST')}")
                                return

                    except ValueError:
                        self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_SALARIES_COST')}")

            ##########################################################################################################
            else:  # expenses types = monthly or yearly
                year = manufacture_date.year()
                if expenses_type == 'month':
                    month = manufacture_date.month()
                else:
                    month = ''

                expenses = None
                expenses_divider = None

                if quantity_expenses:
                    quantity_data = self.database_operations.fetchQuantityOfManufacturedMaterials(unit=quantity_expenses_target_unit, year=year, month=month)
                    if quantity_data:
                        expenses_divider = quantity_data[0]
                        # also include the quantity that is produced in this manufacture process
                        required_units = [self.ui.produced_unit1_combobox.currentData(),self.ui.produced_unit2_combobox.currentData(),self.ui.produced_unit3_combobox.currentData()]
                        
                        required_quantities = [self.ui.produced_quantity1_input.text(),self.ui.produced_quantity2_input.text(),self.ui.produced_quantity3_input.text()]

                        index_of_required_expenses_unit = required_units.index(
                            quantity_expenses_target_unit)  # comes from radio_quantity_unit_expenses_combobox
                        required_quantity_of_required_expenses_unit = required_quantities[
                            index_of_required_expenses_unit]
                        if expenses_divider and required_quantity_of_required_expenses_unit:
                            expenses_divider += float(required_quantity_of_required_expenses_unit)


                if hours_expenses:
                    hours_data = self.database_operations.fetchWorkHoursOfManufacturedMaterials(year=year, month=month)
                    if hours_data:
                        expenses_divider = hours_data[0]
                        # also include the time that is required for this manufacture process
                        if expenses_divider and working_hours:
                            expenses_divider += float(working_hours)

                expenses_data = self.database_operations.fetchExpenses(year=year, month=month,calculated_in_manufacture=True,time_slot=expenses_type)

                if len(expenses_data) > 0:
                    expenses_data = expenses_data[0]
                if expenses_data:
                    expenses = expenses_data[2]
                    currency = expenses_data[6]
                    account_id = expenses_data[10]
                    opposite_account_id = expenses_data[11]
                    id = expenses_data[0]
                    time_slot = expenses_data[1]
                    year = expenses_data[3]
                    month = expenses_data[4]
                    expense_type_id = expenses_data[5]
                    calculated_in_manufacture = expenses_data[7]
                    currency_name = expenses_data[8]
                    expense_name = expenses_data[9]
                    if currency != manufacture_currency:
                        exchange_value = self.database_operations.fetchExchangeValue(currency, manufacture_currency,manufacture_date.toString(Qt.ISODate))
                        if exchange_value:
                            expenses = expenses * float(exchange_value[0][1])
                        else:
                            response = win32api.MessageBox(0,f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_FOR_EXPENSES')}: {expense_name}", "تنبيه", 4)
                            if response == 6: # Yes
                                latest_exchange_value = self.database_operations.fetchLatestExchangeValue(currency, manufacture_currency)
                                if latest_exchange_value:
                                    expenses = expenses * float(latest_exchange_value[0][1])
                                else:
                                    win32api.MessageBox(0,f"{self.language_manager.translate('ALERT_NO_EXCHANGE_RATE_BETWEEN_CURRENCIES')}: {expense_name}", self.language_manager.translate('ALERT_ERROR'))
                                    self.ui.composition_tree.clear()
                                    return
                            else: # No
                                self.ui.composition_tree.clear()
                                return

                    if account_id in self.expenses_dict:
                        # If the ID is already in the dictionary, update the price and currency_id in the existing list
                        existing_entry = self.expenses_dict[account_id]
                        existing_entry[0] += expenses  # Sum the price
                        existing_entry[1] = manufacture_currency  # Update the currency_id
                    else:
                        # If the ID is not in the dictionary, create a new entry with a list containing [price, currency_id]
                        self.expenses_dict[account_id] = [expenses, manufacture_currency]

                if expenses and expenses_divider:
                    try:
                        total_expenses = float(expenses) / float(expenses_divider)
                    except ValueError:
                        self.ui.status_bar_label.setText(f"{self.language_manager.translate('ALERT_ERROR_CALCULATING_EXPENSES')}")
                        return
 
            ##########################################################################################################
            raw_materials_cost = round(raw_materials_total_cost, 3)
            machines_operation_cost = round(machines_operation_cost, 3)
            salaries_cost = round(salaries_cost, 3)
            total_expenses = round(total_expenses, 3)

            total_manufacture_cost = float(raw_materials_cost) + float(machines_operation_cost) + float(
                salaries_cost) + float(total_expenses)

            # Create rows for costs
            cost_items = [
                (self.language_manager.translate('RAW_MATERIALS_COST'), str(round(float(raw_materials_cost), int(self.float_point_precision))), str(currency_id), str(currency_text)),
                (self.language_manager.translate('MACHINES_OPERATION_COST'), str(round(float(machines_operation_cost), int(self.float_point_precision))), str(currency_id), str(currency_text)),
                (self.language_manager.translate('SALARIES_COST'), str(round(float(salaries_cost), int(self.float_point_precision))), str(currency_id), str(currency_text)),
                (self.language_manager.translate('EXPENSES'), str(round(float(total_expenses), int(self.float_point_precision))), str(currency_id), str(currency_text)),
                (self.language_manager.translate('TOTAL_MANUFACTURE_COST'), str(round(float(total_manufacture_cost), int(self.float_point_precision))), str(currency_id), str(currency_text))
            ]
            self.ui.manufacture_details_table.setRowCount(0)
            for row, cost_item in enumerate(cost_items):
                cost_name = cost_item[0]
                cost_value = cost_item[1]
                currency_id = cost_item[2]
                currency_text = cost_item[3]
                self.ui.manufacture_details_table.insertRow(row)
                self.ui.manufacture_details_table.setItem(row, 0, QTableWidgetItem(cost_name))
                self.ui.manufacture_details_table.setItem(row, 1, QTableWidgetItem(cost_value))
                self.ui.manufacture_details_table.setItem(row, 2, QTableWidgetItem(currency_id))
                self.ui.manufacture_details_table.setItem(row, 3, QTableWidgetItem(currency_text))

    def autoInvoiceNumber(self):
        last_invoice_number = self.database_operations.fetchLastInvoiceNumber()
        print(type(last_invoice_number))
        if (str(type(last_invoice_number)) == "<class 'NoneType'>"):
            return 1
        else:
            return int(last_invoice_number) + 1

    def openSelectPulloutAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.ingredients_pullout_account_combobox.setCurrentIndex(self.ui.ingredients_pullout_account_combobox.findData(result['id']))

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(result['id']))

    def openSelectInputWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.input_warehouse_combobox.setCurrentIndex(self.ui.input_warehouse_combobox.findData(result['id']))

    def openSelectMidAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.mid_account_combobox.setCurrentIndex(self.ui.mid_account_combobox.findData(result['id']))

    def openSelectMidAccountInputWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.mid_account_input_combobox.setCurrentIndex(self.ui.mid_account_input_combobox.findData(result['id']))

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            data = id = account['id']
            display_text = account['name']
            self.ui.account_combobox.addItem(display_text, data)
            self.ui.mid_account_combobox.addItem(display_text, data)
            self.ui.mid_account_input_combobox.addItem(display_text, data)
            self.ui.ingredients_pullout_account_combobox.addItem(display_text, data)

        # Ingredients pullout account is the warehouse account if, and only if, ingredients pricing method is 'real invoice' or 'last invoice'
        self.ui.ingredients_pullout_account_combobox.addItem(self.language_manager.translate('WAREHOUSE_ACCOUNT'), 'warehouse_account')

        output_account = self.database_operations.fetchSetting('output_account')
        if output_account:
            self.ui.ingredients_pullout_account_combobox.setCurrentIndex(self.ui.ingredients_pullout_account_combobox.findData(output_account))

        input_account = self.database_operations.fetchSetting('input_account')
        if input_account:
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(input_account))

        mid_output_account = self.database_operations.fetchSetting('mid_output_account')
        if mid_output_account:
            self.ui.mid_account_combobox.setCurrentIndex(self.ui.mid_account_combobox.findData(mid_output_account))

        mid_input_account = self.database_operations.fetchSetting('mid_input_account')
        if mid_input_account:
            self.ui.mid_account_input_combobox.setCurrentIndex(self.ui.mid_account_input_combobox.findData(mid_input_account))


    def setIngredientsPricingParameters(self):
        # Ingredients pullout account is the warehouse account if, and only if, ingredients pricing method is 'real invoice' or 'last invoice'
        if self.ui.material_invoices_average_till_pollout_radio.isChecked() or self.ui.material_invoices_average_radio.isChecked() or self.ui.material_last_purchase_radio.isChecked():
            try:
                self.ui.ingredients_pullout_account_combobox.model().item(
                    self.ui.ingredients_pullout_account_combobox.findData('warehouse_account')).setEnabled(False)
            except Exception as e:
                print(e)
        else:
            self.ui.ingredients_pullout_account_combobox.model().item(
                self.ui.ingredients_pullout_account_combobox.findData('warehouse_account')).setEnabled(True)

        if str(self.ui.ingredients_pullout_account_combobox.currentData()).lower() == 'warehouse_account':
            self.ui.material_invoices_average_radio.setEnabled(False)
            self.ui.material_invoices_average_till_pollout_radio.setEnabled(False)
            self.ui.material_last_purchase_radio.setEnabled(False)
        else:
            self.ui.material_invoices_average_radio.setEnabled(True)
            self.ui.material_invoices_average_till_pollout_radio.setEnabled(True)
            self.ui.material_last_purchase_radio.setEnabled(True)

    def openSelectWarehouseWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'warehouses', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            self.ui.output_warehouse_combobox.setCurrentIndex(self.ui.output_warehouse_combobox.findData(result['id']))

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        for warehouse in warehouses:
            data = id = warehouse['id']
            display_text = warehouse['name']
            self.ui.output_warehouse_combobox.addItem(display_text, data)
            self.ui.input_warehouse_combobox.addItem(display_text, data)

    def saveResults(self, window):
        production_date = self.ui.material_production_date_input.date().toString("yyyy-MM-dd")
        manufacture_date = self.ui.manufacture_date_input.date().toString("yyyy-MM-dd")
        working_hours = self.ui.working_hours_input.text()
        ingredients_pullout_date = self.ui.ingredients_pullout_date_input.date().toString("yyyy-MM-dd")
        output_warehouse = self.ui.output_warehouse_combobox.currentData()
        input_warehouse = self.ui.input_warehouse_combobox.currentData()
        account = self.ui.account_combobox.currentData()
        mid_account = self.ui.mid_account_combobox.currentData()
        mid_account_input = self.ui.mid_account_input_combobox.currentData()
        batch_number = self.ui.batch_number_input.text()

        expenses_type = self.ui.expenses_type_combobox.currentData()
        quantity_unit_expenses = self.ui.radio_quantity_unit_expenses_combobox.currentData()
        # currency = self.ui.currency_combobox.currentData()
        ingredients_pullout_method = self.ui.ingredients_pullout_method_combobox.currentData()
        ingredients_pullout_account = self.ui.ingredients_pullout_account_combobox.currentData()
        
        
        expenses_distribution = ""
        if self.ui.hours_expenses_radio.isChecked():
            expenses_distribution = self.ui.hours_expenses_radio.objectName()
        elif self.ui.no_expenses_radio.isChecked():
            expenses_distribution = self.ui.no_expenses_radio.objectName()
        elif self.ui.quantity_expenses_radio.isChecked():
            expenses_distribution = self.ui.quantity_expenses_radio.objectName()
        expenses_distribution = expenses_distribution.replace('_radio', '')

        material_pricing_method = ""
        if self.ui.material_exact_invoice_radio.isChecked():
            material_pricing_method = self.ui.material_exact_invoice_radio.objectName()
        elif self.ui.material_invoices_average_radio.isChecked():
            material_pricing_method = self.ui.material_invoices_average_radio.objectName()
        elif self.ui.material_last_purchase_radio.isChecked():
            material_pricing_method = self.ui.material_last_purchase_radio.objectName()
        elif self.ui.material_invoices_average_till_pollout_radio.isChecked():
            material_pricing_method = self.ui.material_invoices_average_till_pollout_radio.objectName()
        elif self.ui.material_explicit_value_radio.isChecked():
            material_pricing_method = self.ui.material_explicit_value_radio.objectName()
        material_pricing_method = material_pricing_method.replace('_radio', '')

       
        produced_materials = []
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            material_id = item.text(0)
            produced_quantities_and_units = {
                    "quantity1": {"amount": item.child(1).text(2), "unit": item.child(1).text(3)},
                    "quantity2": {"amount": item.child(1).text(5), "unit": item.child(1).text(6)},
                    "quantity3": {"amount": item.child(1).text(8), "unit": item.child(1).text(9)}
            }

            # Read referential quantities from child 0
            referential_quantities = {
                "quantity1": {"amount": item.child(0).text(2), "unit": item.child(0).text(3)},
                "quantity2": {"amount": item.child(0).text(5), "unit": item.child(0).text(6)},
                "quantity3": {"amount": item.child(0).text(8), "unit": item.child(0).text(9)}
            }

            # Read working hours from col 10 for children 0 and 1
            working_hours_ref = item.child(0).text(11)
            working_hours_produced = item.child(1).text(11)

            # Read batch from col 12 for child 1
            batch = item.child(1).text(13)

            # Get warehouse for this material from material_warehouses_table
            material_warehouse = None
            for row in range(self.ui.material_warehouses_table.rowCount()):
                if self.ui.material_warehouses_table.item(row, 1).text() == material_id:
                    warehouse_combobox = self.ui.material_warehouses_table.cellWidget(row, 2)
                    material_warehouse = warehouse_combobox.currentData()
                    break

            produced_materials.append({
                "material_id": material_id, 
                "quantities_and_units": produced_quantities_and_units,
                "referential_quantities": referential_quantities,
                "working_hours_ref": working_hours_ref,
                "working_hours_produced": working_hours_produced,
                "warehouse": material_warehouse,
                "batch": batch
            })
            
        manufactured_rows = self.ui.manufacture_details_table.rowCount()
        if manufactured_rows > 0:
            composition_materials_cost = self.ui.manufacture_details_table.item(0, 1).text()
            machines_operation_cost = self.ui.manufacture_details_table.item(1, 1).text()
            salaries_cost = self.ui.manufacture_details_table.item(2, 1).text()
            expenses_cost = self.ui.manufacture_details_table.item(3, 1).text()

            total_cost = self.ui.manufacture_details_table.item(4, 1).text()
            manufactue_currency = self.ui.manufacture_details_table.item(4, 2).text()
            manufactue_currency_name = self.ui.manufacture_details_table.item(4, 3).text()


            composition_rows = self.ui.composition_tree.topLevelItemCount()
            machines_rows = self.ui.machines_table.rowCount()

            composition_data = []
            if composition_rows:
                for item_index in range(self.ui.composition_tree.topLevelItemCount()):
                    item = self.ui.composition_tree.topLevelItem(item_index)
                    row_data = ['parent']
                    composition_item_id = item.text(0)
                    standard_quantity = item.text(3)
                    unit_id = item.text(4)
                    manufactured_quantity = item.text(6)
                    unit_cost = item.text(9)
                    currency = item.text(11)
                    warehouse_id = item.text(13)
                    warehouse_account_id = item.text(15)
                    warehouse_quantity = item.text(16)
                    pulled_quantity = item.text(19)
                    shortage = item.text(20)
                    row_data = ['parent', composition_item_id, standard_quantity, unit_id, manufactured_quantity,unit_cost, currency, warehouse_id, warehouse_account_id, warehouse_quantity,pulled_quantity, shortage]
                    composition_data.append(row_data)

                    # read the childs
                    for child_index in range(item.childCount()):
                        child_item = item.child(child_index)
                        composition_item_id = composition_item_id  # same as root row composition_item_id
                        standard_quantity = child_item.text(3)
                        unit_id = child_item.text(4)
                        manufactured_quantity = child_item.text(5)
                        unit_cost = child_item.text(6)
                        currency = child_item.text(9)
                        warehouse_id = child_item.text(10)
                        warehouse_account_id = child_item.text(11)
                        warehouse_quantity = child_item.text(12)
                        pulled_quantity = child_item.text(13)
                        shortage = child_item.text(14)
                        child_data = ['child', composition_item_id, standard_quantity, unit_id, manufactured_quantity, unit_cost, currency, warehouse_id, warehouse_account_id, warehouse_quantity, pulled_quantity, shortage]

                        composition_data.append(child_data)

            machines_data = []
            if machines_rows:
                for row in range(machines_rows):
                    machine_id = self.ui.machines_table.item(row, 0).text()
                    machine_name = self.ui.machines_table.item(row, 1).text()
                    mode_id = self.ui.machines_table.item(row, 2).text()
                    mode = self.ui.machines_table.item(row, 3).text()
                    duration_in_hours = self.ui.machines_table.item(row, 4).text()
                    exclusive_use = self.ui.machines_table.item(row, 5).text()
                    exclusive_percentage = self.ui.machines_table.item(row, 6).text()

                    exclusive_use = 1 if str(exclusive_use) == 'yes' else 0

                    machine_data = [machine_id, mode_id, duration_in_hours, exclusive_use, exclusive_percentage]
                    machines_data.append(machine_data)



            messagebox_result = win32api.MessageBox(None, self.language_manager.translate('ALERT_SAVE_MANUFACTURE_PROCESS'), "ALERT", MB_YESNO)
            if (messagebox_result == IDYES):
                manufacture_process_id = self.database_operations.saveManufactureProcess(produced_materials, manufacture_date, working_hours, ingredients_pullout_date, expenses_cost, manufactue_currency, input_warehouse, account, mid_account, mid_account_input, batch_number, expenses_type, expenses_distribution, material_pricing_method, composition_materials_cost, machines_operation_cost, salaries_cost, quantity_unit_expenses, ingredients_pullout_method, ingredients_pullout_account, composition_data, machines_data, production_date, commit=False)
                
                if self.ui.generate_journal_entry.isChecked() and manufacture_process_id:
                    self.saveJournalEntry(manufacture_process_id, commit=False)
                if self.ui.add_material_to_warehouse_checkbox.isChecked() and manufacture_process_id:
                    self.addToWarehouse(manufacture_process_id,manufactue_currency)
                    
            elif (messagebox_result == IDNO):
                pass
        self.sql_connector.conn.commit()

    def setIngredientsPulloutMethods(self):
        pullout_methods = {'FIFO': self.language_manager.translate('FIFO'), 'LIFO': self.language_manager.translate('LIFO')}
        for key, value in pullout_methods.items():
            self.ui.ingredients_pullout_method_combobox.addItem(str(value), str(key))

    def saveJournalEntry(self, manufacture_process_id, commit=True):
        mid_account = self.ui.mid_account_combobox.currentData()
        mid_account_input = self.ui.mid_account_input_combobox.currentData()
        input_account = self.ui.account_combobox.currentData()
        ingredients_pullout_account = self.ui.ingredients_pullout_account_combobox.currentData()
        cost_center_id = self.ui.cost_center_combobox.currentData()

        produced_materials = []
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            material_name = item.text(1)
            batch = item.child(1).text(13)
            produced_materials.append(f"{material_name} (batch: {batch})")
            
        date = self.ui.manufacture_date_input.date().toString("yyyy-MM-dd")
        manufacture_currency = self.ui.currency_combobox.currentData()

        journal_entry_id = None
        if self.ui.generate_journal_entry.isChecked():

            journal_entry_id = self.database_operations.addJournalEntry(date, manufacture_currency, origin_type='manufacture',origin_id=manufacture_process_id, commit=commit)

            # machines_costs
            if bool(self.machines_operation_costs_dict):
                for resource_id, data in self.machines_operation_costs_dict.items():
                    value = data[0]
                    currency = data[1]
                    account_id = data[2]
                    resource_name = data[3]
                    resource_account_id = data[4]
                    machine_name = data[5]
                    statement = "cost of using " + str(resource_name) + " to produce " + str(
                        material_name) + "/Batch:" + str(batch)
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement,account_id, mid_account, value,commit=False)

                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement, mid_account, account_id, value,commit=False)

            # salaries
            if bool(self.salaries_costs_dict):
                for account_id, data in self.salaries_costs_dict.items():
                    value = data[0]
                    currency = data[1]
                    statement = "cost of salaries to produce " + ", ".join(produced_materials)
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, account_id, mid_account, value,commit=False)

                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement,mid_account, account_id, value, commit=False)

                    # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, mid_account, manufacture_account, value, commit=False)

                    # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement,manufacture_account, mid_account, value, commit=False)

            # expenses
            if bool(self.salaries_costs_dict):
                for account_id, data in self.expenses_dict.items():
                    value = data[0]
                    currency = data[1]
                    statement = "Expenses to produce " + ", ".join(produced_materials)
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, account_id, mid_account, value, cost_center_id, commit=False)

                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement,mid_account, account_id, value, cost_center_id, commit=False)
                    
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement,mid_account, input_account, value, cost_center_id ,commit=False)
                    
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement, input_account, mid_account, value, cost_center_id, commit=False)

            # materials
            if bool(self.materials_costs_dict) and self.ui.material_exact_invoice_radio.isChecked():
                for material_id, ingredient_warehouses in self.materials_costs_dict.items():
                    for ingredient_warehouse in ingredient_warehouses:
                        warehouse_id, warehouse_name, warehouse_entry_id, warehouse_entry_quantity, pulled_quantity, unit, warehouse_entry_production_batch_id, warehouse_entry_invoice_item_id, warehouse_entry_code, warehouse_entry_name, warehouse_account, unit_cost, cost, currency = ingredient_warehouse

                        statement = "Cost of " + str(warehouse_entry_name) + " pulled from " + str(
                            warehouse_name) + " to produce " + str(material_name) + "/Batch:" + str(batch)
                        
                        self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, warehouse_account, mid_account_input, cost, cost_center_id, commit=False)

                        self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, mid_account, warehouse_account, cost, cost_center_id, commit=False)

                        # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement, mid_account, manufacture_account, cost, commit=False)

                        # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement,manufacture_account, mid_account, cost,commit=False)
                        if warehouse_account:
                            pass
                        else:
                            message = "لا يوجد حساب للمستودع " + str(warehouse_name) + " الذي سحبت منه المادة " + str(
                                material_name) + ". هل تريد تحميل الكلفة على حساب الاخراج؟"
                            messagebox_result = win32api.MessageBox(None, message, "ALERT", MB_YESNO)
                            if (messagebox_result == IDYES):
                                pass
                            elif (messagebox_result == IDNO):
                                message = self.language_manager.translate('ALERT_MANUFACTURE_PROCESS_NOT_SAVED')
                                win32api.MessageBox(0, message, "ALERT")
                                return  
            else:
                root_item = self.ui.composition_tree.invisibleRootItem()
                child_count = root_item.childCount()
                for i in range(child_count):
                    item = root_item.child(i)
                    material_name = item.text(2)
                    cost = item.text(10)
                    currency = item.text(11)
                    statement = "Cost of " + str(material_name) + " to produce " + str(material_name) + "/Batch:" + str(
                        batch)
                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement, mid_account , ingredients_pullout_account, cost, cost_center_id, commit=False)

                    self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement,input_account, mid_account_input, cost, cost_center_id, commit=False)

                    # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "creditor", statement,mid_account, ingredients_pullout_account, cost,commit=False)

                    # self.database_operations.addJournalEntryItem(journal_entry_id, currency, "debtor", statement, ingredients_pullout_account, mid_account, cost,commit=False)

            if commit:
                self.sql_connector.conn.commit()

    def addInputInvoice(self,manufacture_currency):
        # Get invoice number and date
        invoice_number = self.autoInvoiceNumber()
        production_date = self.ui.material_production_date_input.date().toString("yyyy-MM-dd")
        manufacture_currency = self.ui.currency_combobox.currentData()

        input_invoice_types = self.database_operations.fetchInvoiceTypes(name='input')
        input_invoice_type_id = input_invoice_types[0]['id'] if input_invoice_types else None

        input_invoice_id = self.database_operations.addInvoice(
            number=invoice_number,
            date=production_date,
            statement='manufacture invoice',
            type_col=input_invoice_type_id, 
            payment_method='cash',
            paid=1,
            invoice_currency=manufacture_currency
        )
        return input_invoice_id


    def addOutputInvoice(self,manufacture_currency):  
        # Create output invoice for composition materials
        output_invoice_types = self.database_operations.fetchInvoiceTypes(name='output')
        output_invoice_type_id = output_invoice_types[0]['id'] if output_invoice_types else None
        output_warehouse_id = self.ui.output_warehouse_combobox.currentData()
        production_date = self.ui.material_production_date_input.date().toString("yyyy-MM-dd")
        invoice_number = self.autoInvoiceNumber()

        output_invoice_id = self.database_operations.addInvoice(
            number=invoice_number,
            date=production_date, 
            statement='manufacture invoice',
            type_col=output_invoice_type_id , # Now using just the ID
            payment_method='cash',
            paid=1,
            invoice_currency=manufacture_currency,
            invoice_warehouse=output_warehouse_id
        )
        return output_invoice_id


    def addMaterialToInputInvoice(self,input_invoice_id,manufacture_currency):
        # Add manufactured materials to input invoice
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            material_id = item.text(0)
            
            # Get produced quantities and units
            produced_quantity1 = item.child(1).text(2)
            produced_unit1 = item.child(1).text(3)
            produced_quantity2 = item.child(1).text(5)
            produced_unit2 = item.child(1).text(6)
            produced_quantity3 = item.child(1).text(8)
            produced_unit3 = item.child(1).text(9)
            cost_center_id = self.ui.cost_center_combobox.currentData()
            warehouse_id = self.ui.output_warehouse_combobox.currentData()

            # Calculate unit price from total manufacture cost
            total_cost = float(self.ui.manufacture_details_table.item(3, 1).text())  # Total manufacture cost
            unit_price = total_cost
            
            # Add manufactured material to input invoice
            self.database_operations.addInvoiceMaterial(
                invoice_id=input_invoice_id,
                material_id=material_id,
                quantity1=produced_quantity1,
                unit1_id=produced_unit1,
                quantity2=produced_quantity2, 
                unit2_id=produced_unit2,
                quantity3=produced_quantity3,
                unit3_id=produced_unit3,
                unit_price=unit_price,
                currency_id=manufacture_currency,
                equilivance_price=unit_price,
                warehouse_id=warehouse_id,
                cost_center_id=cost_center_id,
                notes="Manufactured material",
            )


    def addMaterialToOutputInvoice(self,output_invoice_id,manufacture_currency):
        # Add composition materials to output invoice
        for row in range(self.ui.composition_tree.topLevelItemCount()):
            item = self.ui.composition_tree.topLevelItem(row)
            material_id = item.text(0)
            material_name = item.text(2)
            required_quantity = float(item.text(3))
            unit = item.text(4)
            unit_cost = float(item.text(9)) if item.text(9) else 0


            # Add composition material to output invoice
            invoice_item_id = self.database_operations.addInvoiceMaterial(
                invoice_id=output_invoice_id,
                material_id=material_id,
                quantity1=required_quantity,
                unit1_id=unit,
                unit_price=unit_cost,
                currency_id=manufacture_currency,
                equilivance_price=unit_cost,
                # warehouse_id=warehouse_id,  # Will be pulled from composition materials
                notes="Manufacturing composition material",
            )

            # self.database_operations.moveMaterial(
            #     quantity=required_quantity,
            #     move_unit=unit,
            #     to_warehouse=output_warehouse_id,
            #     to_warehouse_entry_id=warehouse_entry_id,
            #     origin_type='manufacture',
            #     origin_id=input_invoice_id,
            #     material_id=produced_material_id,
            #     record_move=True,
            #     record_journal_entry=False,
            #     record_only=True,
            #     commit=False
            # )

            # Record move for each composition material being consumed
            self.database_operations.moveMaterial(
                quantity=required_quantity,
                move_unit=unit,
                from_warehouse='',  # Material is taken from this warehouse
                to_warehouse='',  # Empty because material is consumed
                origin_type='pullout_material',
                origin_id=invoice_item_id,  # Link to output invoice since materials are being consumed
                material_id=material_id,
                material_name=material_name,
                from_warehouse_entry_id='',  # Will be determined by the system
                to_warehouse_entry_id='',
                quantity_using_source_warehouse_unit=required_quantity,
                source_production_batch_id='',
                source_invoice_item_id='',
                source_warehouse_unit=unit,
                cost='',
                currency='',
                to_account_warehouse='',
                from_account_warehouse='',
                to_account_name_warehouse='',
                from_account_name_warehouse='',
                record_move=True,
                record_journal_entry=False,
                record_only=True,
                commit=False
            )





    def addToWarehouse(self, manufacture_process_id, manufacture_currency):
        output_warehouse_id = self.ui.output_warehouse_combobox.currentData()
        root = self.ui.produced_materials_tree.invisibleRootItem()
        for i in range(root.childCount()):
            item = root.child(i)
            produced_material_id = item.text(0)
            produced_quantity1 = item.child(1).text(2)
            produced_unit1 = item.child(1).text(3)
            produced_quantity2 = item.child(1).text(5)
            produced_unit2 = item.child(1).text(6)
            produced_quantity3 = item.child(1).text(8)
            produced_unit3 = item.child(1).text(9)

            default_unit = item.child(1).text(14)

            quantity = None
            if produced_unit1 and int(default_unit) == int(produced_unit1):
                quantity = produced_quantity1
            elif produced_unit2 and int(default_unit) == int(produced_unit2):
                quantity = produced_quantity2
            elif produced_unit3 and int(default_unit) == int(produced_unit3):
                quantity = produced_quantity3

            if quantity and default_unit:

                input_invoice_id = self.addInputInvoice(manufacture_currency)

                self.addMaterialToInputInvoice(input_invoice_id,manufacture_currency)

                output_invoice_id = self.addOutputInvoice(manufacture_currency)

                self.addMaterialToOutputInvoice(output_invoice_id,manufacture_currency)


                self.sql_connector.conn.commit()

                warehouse_entry_id = self.database_operations.addMaterialToWarehouse(output_warehouse_id, produced_material_id, quantity, default_unit, production_batch_id=manufacture_process_id)
                if warehouse_entry_id:
                    self.database_operations.moveMaterial(
                        quantity=produced_quantity1,
                        move_unit=produced_unit1,
                        to_warehouse=output_warehouse_id,
                        to_warehouse_entry_id=warehouse_entry_id,
                        origin_type='manufacture',
                        origin_id=input_invoice_id,
                        material_id=produced_material_id,
                        record_move=True,
                        record_journal_entry=False,
                        record_only=True,
                        commit=False
                    )
                
                self.sql_connector.conn.commit()
