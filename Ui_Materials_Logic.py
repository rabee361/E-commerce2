from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QTableWidgetItem
from PyQt5.QtCore import Qt
import win32api
from win32con import MB_OKCANCEL, MB_YESNO, IDYES, IDNO

from Colors import colorizeTableRow, light_red_color, blue_sky_color, light_green_color ,black
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_AddMaterial_Logic import Ui_AddMaterial_Logic
from Ui_GrouppedMaterialComposition_Logic import Ui_GrouppedMaterialComposition_Logic
from Ui_Materials import Ui_Materials
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtCore import QTranslator
from LanguageManager import LanguageManager

class Ui_Materials_Logic(QDialog):
    def __init__(self, sqlconnector):
        super().__init__()
        self.sqlconnector = sqlconnector
        self.database_operations = DatabaseOperations(sqlconnector)
        self.ui = Ui_Materials()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_materials = QDialog()
        window_materials.setWindowTitle("Materials")
        window_materials.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window_materials.setWindowState(Qt.WindowMaximized)
        self.ui.setupUi(window_materials)
        self.language_manager.load_translated_ui(self.ui, window_materials)
        self.initialize(window_materials)
        window_materials.exec()

    def initialize(self, window):
        self.ui.moves_table.setSortingEnabled(True)

        # float_point_value = self.database_operations.fetchFloatPointValue()
        float_point_value = 2
        validator = QDoubleValidator()
        if float_point_value:
            validator.setDecimals(int(float_point_value))

        self.ui.current_quantity_input.setValidator(validator)
        self.ui.max_quantity_input.setValidator(validator)
        self.ui.min_quantity_input.setValidator(validator)
        self.ui.request_limit_input.setValidator(validator)
        self.ui.gift_input.setValidator(validator)
        self.ui.gift_for_input.setValidator(validator)
        self.ui.price1_1_input.setValidator(validator)
        self.ui.price2_1_input.setValidator(validator)
        self.ui.price3_1_input.setValidator(validator)
        self.ui.price4_1_input.setValidator(validator)
        self.ui.price5_1_input.setValidator(validator)
        self.ui.price6_1_input.setValidator(validator)
        self.ui.price1_2_input.setValidator(validator)
        self.ui.price2_2_input.setValidator(validator)
        self.ui.price3_2_input.setValidator(validator)
        self.ui.price4_2_input.setValidator(validator)
        self.ui.price5_2_input.setValidator(validator)
        self.ui.price6_2_input.setValidator(validator)
        self.ui.price1_3_input.setValidator(validator)
        self.ui.price2_3_input.setValidator(validator)
        self.ui.price3_3_input.setValidator(validator)
        self.ui.price4_3_input.setValidator(validator)
        self.ui.price5_3_input.setValidator(validator)
        self.ui.price6_3_input.setValidator(validator)

        material_types = {"stock": self.language_manager.translate("STOCK_MATERIAL"), "service": self.language_manager.translate("SERVICE_MATERIAL"), "assets": self.language_manager.translate("ASSETS_MATERIAL")}
        for key, value in material_types.items():
            self.ui.type_combobox.addItem(value, key)

        # self.ui.unit1_combobox.setEnabled(False)
        # self.ui.unit2_combobox.setEnabled(False)
        # self.ui.unit3_combobox.setEnabled(False)
        # self.ui.group_combobox.setEnabled(False)

        self.ui.materials_tree.hideColumn(2)
        self.ui.materials_tree.hideColumn(3)

        self.fetchAccounts()
        self.fetchCurrencies()
        self.fetchGroups()
        self.fetchMaterials()
        self.fetchPricesNames()
        self.fetchUnits()
        self.fetchMachines()
        self.fetchMachineModes()
        self.fetchManufactureHall()

        self.ui.materials_tree.clicked.connect(lambda: self.fetchSelectedMaterial())
        self.ui.materials_tree.clicked.connect(lambda: self.fetchMaterialMachines())
        self.ui.materials_tree.clicked.connect(lambda: self.fetchMaterialMoves())
        self.ui.save_btn.clicked.connect(lambda: self.saveMaterial())
        self.ui.add_new_material_btn.clicked.connect(lambda: self.openAddMaterialWindow())
        self.ui.delete_btn.clicked.connect(lambda: self.removeMaterial())
        self.ui.select_group_btn.clicked.connect(lambda: self.openSelectGroupWindow())
        self.ui.select_material_discount_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.material_discount_account_combobox))
        self.ui.select_material_addition_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.material_addition_account_combobox))


        self.ui.groupped_material_checkbox.clicked.connect(lambda: self.enableGrouppedMaterialCompositionButton())
        self.ui.groupped_material_btn.clicked.connect(lambda: self.openGrouppedMaterialCompositionWindow())

        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())

        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.enableUnit2andUnit3())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.enableUnit2Prices())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.enableUnit3Prices())

        self.ui.standard_unit1_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.standard_unit2_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.standard_unit3_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())

        self.ui.machines_combobox.currentIndexChanged.connect(lambda: self.fetchMachineModes())
        self.ui.add_machine_btn.clicked.connect(lambda: self.addMachine())
        self.ui.add_machine_btn.clicked.connect(lambda: self.fetchMaterialMachines())
        self.ui.delete_machine_btn.clicked.connect(lambda: self.removeMaterialMachine())
        self.ui.delete_machine_btn.clicked.connect(lambda: self.fetchMaterialMachines())
        self.ui.delete_move_btn.clicked.connect(lambda: self.removeMaterialMove())

    def fetchMaterials(self):
        # Get the materials and add each one to its appropriate group in tree
        materials = self.database_operations.fetchMaterials()
        ungrouped_materials = []
        for material in materials:
            id = material[0]
            code = material[1]
            name = material[2]
            group = material[3]

            title = str(code) + "-" + str(name)

            if not group:
                ungrouped_materials.append((title, id))
            else:
                groups_already_in_tree = self.ui.materials_tree.findItems(str(group), Qt.MatchExactly | Qt.MatchRecursive, 3)
                if len(groups_already_in_tree) > 0:  # Group already exists in tree, so append its child
                    group = groups_already_in_tree[0]  # only one would exist because we search using ID
                    material = QTreeWidgetItem(['', str(title), str(id), ''])
                    group.addChild(material)
        
        if ungrouped_materials:
            ungrouped_group = QTreeWidgetItem([self.language_manager.translate("UNGROUPED_MATERIALS"), '', '', ''])
            self.ui.materials_tree.addTopLevelItem(ungrouped_group)
            for title, id in ungrouped_materials:
                item = QTreeWidgetItem(['', str(title), str(id), ''])
                ungrouped_group.addChild(item)

    def fetchGroups(self):
        self.ui.materials_tree.clear()
        self.ui.group_combobox.clear()
        groups = self.database_operations.fetchGroups()

        # Add the groups to the tree
        children_queue = []
        for group in groups:
            print(group)
            id = group[0]
            name = group[1]
            code = group[2]
            date = group[3]
            parent_id = group[4]
            parent_name = group[5]

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(name), '', '', str(id)])
                self.ui.materials_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.materials_tree.findItems(str(parent_id),
                                                                         Qt.MatchExactly | Qt.MatchRecursive, 3)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(3)

                        child_item = QTreeWidgetItem([str(name), '', '', str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(group)
        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                code = child[2]
                date = child[3]
                parent_id = child[4]
                parent_name = child[5]

                items_already_in_tree = self.ui.materials_tree.findItems(str(parent_id),
                                                                         Qt.MatchExactly | Qt.MatchRecursive, 3)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(3)

                        child_item = QTreeWidgetItem([str(name), '', '', str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)
                            print("DELETED")

        # Add the groups to the groups combobox
        for group in groups:
            id = group[0]
            display_text = group[1]
            data = id
            self.ui.group_combobox.addItem(display_text, data)

    def fetchSelectedMaterial(self):
        material_id = self.ui.materials_tree.currentItem().text(2)
        if material_id and material_id != '':
            material = self.database_operations.fetchMaterial(material_id)
            id = material['id']
            code = material['code']
            name = material['name']
            group = material['group_col']
            specs = material['specs']
            size = material['size_col']
            manufacturer = material['manufacturer']
            color = material['color']
            origin = material['origin']
            quality = material['quality']
            type = material['type_col']
            model = material['model']
            unit1 = material['unit1']
            unit2 = material['unit2']
            unit3 = material['unit3']
            default_unit = material['default_unit']
            current_quantity = material['current_quantity']
            max_quantity = material['max_quantity']
            min_quantity = material['min_quantity']
            request_limit = material['request_limit']
            gift = material['gift']
            gift_for = material['gift_for']
            price1_desc = material['price1_desc']
            price1_1 = material['price1_1']
            price1_1_unit = material['price1_1_unit']
            price1_2 = material['price1_2']
            price1_2_unit = material['price1_2_unit']
            price1_3 = material['price1_3']
            price1_3_unit = material['price1_3_unit']
            price2_desc = material['price2_desc']
            price2_1 = material['price2_1']
            price2_1_unit = material['price2_1_unit']
            price2_2 = material['price2_2']
            price2_2_unit = material['price2_2_unit']
            price2_3 = material['price2_3']
            price2_3_unit = material['price2_3_unit']
            price3_desc = material['price3_desc']
            price3_1 = material['price3_1']
            price3_1_unit = material['price3_1_unit']
            price3_2 = material['price3_2']
            price3_2_unit = material['price3_2_unit']
            price3_3 = material['price3_3']
            price3_3_unit = material['price3_3_unit']
            price4_desc = material['price4_desc']
            price4_1 = material['price4_1']
            price4_1_unit = material['price4_1_unit']
            price4_2 = material['price4_2']
            price4_2_unit = material['price4_2_unit']
            price4_3 = material['price4_3']
            price4_3_unit = material['price4_3_unit']
            price5_desc = material['price5_desc']
            price5_1 = material['price5_1']
            price5_1_unit = material['price5_1_unit']
            price5_2 = material['price5_2']
            price5_2_unit = material['price5_2_unit']
            price5_3 = material['price5_3']
            price5_3_unit = material['price5_3_unit']
            price6_desc = material['price6_desc']
            price6_1 = material['price6_1']
            price6_1_unit = material['price6_1_unit']
            price6_2 = material['price6_2']
            price6_2_unit = material['price6_2_unit']
            price6_3 = material['price6_3']
            price6_3_unit = material['price6_3_unit']
            expiry = material['expiray']
            groupped_material = material['groupped']
            yearly_required = material['yearly_required']
            work_hours = material['work_hours']
            standard_unit3_quantity = material['standard_unit3_quantity']
            standard_unit2_quantity = material['standard_unit2_quantity']
            standard_unit1_quantity = material['standard_unit1_quantity']
            manufacture_hall = material['manufacture_hall']
            discount_account = material['discount_account']
            addition_account = material['addition_account']

            material_quantity = 0
            material_warehouses = self.database_operations.fetchMaterialWarehouses(material_id)
            for warehouse_id, records in material_warehouses.items():
                for record in records:
                    material_quantity += record['quantity']

            current_quantity = material_quantity

            if (str(code).lower() == 'none'):
                code = ''
            if (str(name).lower() == 'none'):
                name = ''
            if (str(group).lower() == 'none'):
                group = ''
            if (str(specs).lower() == 'none'):
                specs = ''
            if (str(size).lower() == 'none'):
                size = ''
            if (str(manufacturer).lower() == 'none'):
                manufacturer = ''
            if (str(color).lower() == 'none'):
                color = ''
            if (str(origin).lower() == 'none'):
                origin = ''
            if (str(quality).lower() == 'none'):
                quality = ''
            if (str(model).lower() == 'none'):
                model = ''
            if (str(unit1).lower() == 'none'):
                unit1 = ''
            if (str(unit2).lower() == 'none'):
                unit2 = ''
            if (str(unit3).lower() == 'none'):
                unit3 = ''
            if (str(default_unit).lower() == 'none'):
                default_unit = ''
            if (str(current_quantity).lower() == 'none'):
                current_quantity = ''
            if (str(max_quantity).lower() == 'none'):
                max_quantity = ''
            if (str(min_quantity).lower() == 'none'):
                min_quantity = ''
            if (str(request_limit).lower() == 'none'):
                request_limit = ''
            if (str(gift).lower() == 'none'):
                gift = ''
            if (str(gift_for).lower() == 'none'):
                gift_for = ''
            if (str(price1_desc).lower() == 'none'):
                price1_desc = ''
            if (str(price1_1).lower() == 'none'):
                price1_1 = ''
            if (str(price1_1_unit).lower() == 'none'):
                price1_1_unit = ''
            if (str(price1_2).lower() == 'none'):
                price1_2 = ''
            if (str(price1_2_unit).lower() == 'none'):
                price1_2_unit = ''
            if (str(price1_3).lower() == 'none'):
                price1_3 = ''
            if (str(price1_3_unit).lower() == 'none'):
                price1_3_unit = ''
            if (str(price2_desc).lower() == 'none'):
                price2_desc = ''
            if (str(price2_1).lower() == 'none'):
                price2_1 = ''
            if (str(price2_1_unit).lower() == 'none'):
                price2_1_unit = ''
            if (str(price2_2).lower() == 'none'):
                price2_2 = ''
            if (str(price2_2_unit).lower() == 'none'):
                price2_2_unit = ''
            if (str(price2_3).lower() == 'none'):
                price2_3 = ''
            if (str(price2_3_unit).lower() == 'none'):
                price2_3_unit = ''
            if (str(price3_desc).lower() == 'none'):
                price3_desc = ''
            if (str(price3_1).lower() == 'none'):
                price3_1 = ''
            if (str(price3_1_unit).lower() == 'none'):
                price3_1_unit = ''
            if (str(price3_2).lower() == 'none'):
                price3_2 = ''
            if (str(price3_2_unit).lower() == 'none'):
                price3_2_unit = ''
            if (str(price3_3).lower() == 'none'):
                price3_3 = ''
            if (str(price3_3_unit).lower() == 'none'):
                price3_3_unit = ''
            if (str(price4_desc).lower() == 'none'):
                price4_desc = ''
            if (str(price4_1).lower() == 'none'):
                price4_1 = ''
            if (str(price4_1_unit).lower() == 'none'):
                price4_1_unit = ''
            if (str(price4_2).lower() == 'none'):
                price4_2 = ''
            if (str(price4_2_unit).lower() == 'none'):
                price4_2_unit = ''
            if (str(price4_3).lower() == 'none'):
                price4_3 = ''
            if (str(price4_3_unit).lower() == 'none'):
                price4_3_unit = ''
            if (str(price5_desc).lower() == 'none'):
                price5_desc = ''
            if (str(price5_1).lower() == 'none'):
                price5_1 = ''
            if (str(price5_1_unit).lower() == 'none'):
                price5_1_unit = ''
            if (str(price5_2).lower() == 'none'):
                price5_2 = ''
            if (str(price5_2_unit).lower() == 'none'):
                price5_2_unit = ''
            if (str(price5_3).lower() == 'none'):
                price5_3 = ''
            if (str(price5_3_unit).lower() == 'none'):
                price5_3_unit = ''
            if (str(price6_desc).lower() == 'none'):
                price6_desc = ''
            if (str(price6_1).lower() == 'none'):
                price6_1 = ''
            if (str(price6_1_unit).lower() == 'none'):
                price6_1_unit = ''
            if (str(price6_2).lower() == 'none'):
                price6_2 = ''
            if (str(price6_2_unit).lower() == 'none'):
                price6_2_unit = ''
            if (str(price6_3).lower() == 'none'):
                price6_3 = ''
            if (str(price6_3_unit).lower() == 'none'):
                price6_3_unit = ''
            if (str(expiry).lower() == 'none'):
                expiry = ''

            if (str(yearly_required).lower()=='none'):
                yearly_required=''
            if (str(work_hours).lower()=='none'):
                work_hours=''
            if (str(standard_unit3_quantity).lower()=='none'):
                standard_unit3_quantity=''
            if (str(standard_unit2_quantity).lower()=='none'):
                standard_unit2_quantity=''
            if (str(standard_unit1_quantity).lower()=='none'):
                standard_unit1_quantity=''

            if (str(manufacture_hall).lower()=='none'):
                manufacture_hall=''

            self.ui.code_input.setText(str(code))
            self.ui.name_input.setText(str(name))
            self.ui.specs_input.setText(str(specs))
            self.ui.size_input.setText(str(size))
            self.ui.manufacturer_input.setText(str(manufacturer))
            self.ui.color_input.setText(str(color))
            self.ui.origin_input.setText(str(origin))
            self.ui.quality_input.setText(str(quality))
            self.ui.model_input.setText(str(model))
            self.ui.unit1_combobox.setCurrentIndex(self.ui.unit1_combobox.findData(str(unit1)))
            self.ui.unit2_combobox.setCurrentIndex(self.ui.unit2_combobox.findData(str(unit2)))
            self.ui.unit3_combobox.setCurrentIndex(self.ui.unit3_combobox.findData(str(unit3)))
            self.ui.current_quantity_input.setText(str(current_quantity))
            self.ui.max_quantity_input.setText(str(max_quantity))
            self.ui.min_quantity_input.setText(str(min_quantity))
            self.ui.request_limit_input.setText(str(request_limit))
            self.ui.gift_input.setText(str(gift))
            self.ui.gift_for_input.setText(str(gift_for))

            self.ui.price1_desc_combobox.setCurrentIndex(self.ui.price1_desc_combobox.findData(price1_desc))
            self.ui.price1_1_input.setText(str(price1_1))
            self.ui.price1_2_input.setText(str(price1_2))
            self.ui.price1_3_input.setText(str(price1_3))
            self.ui.price2_desc_combobox.setCurrentIndex(self.ui.price2_desc_combobox.findData(price2_desc))
            self.ui.price2_1_input.setText(str(price2_1))
            self.ui.price2_2_input.setText(str(price2_2))
            self.ui.price2_3_input.setText(str(price2_3))
            self.ui.price3_desc_combobox.setCurrentIndex(self.ui.price3_desc_combobox.findData(price3_desc))
            self.ui.price3_1_input.setText(str(price3_1))
            self.ui.price3_2_input.setText(str(price3_2))
            self.ui.price3_3_input.setText(str(price3_3))
            self.ui.price4_desc_combobox.setCurrentIndex(self.ui.price4_desc_combobox.findData(price4_desc))
            self.ui.price4_1_input.setText(str(price4_1))
            self.ui.price4_2_input.setText(str(price4_2))
            self.ui.price4_3_input.setText(str(price4_3))
            self.ui.price5_desc_combobox.setCurrentIndex(self.ui.price5_desc_combobox.findData(price5_desc))
            self.ui.price5_1_input.setText(str(price5_1))
            self.ui.price5_2_input.setText(str(price5_2))
            self.ui.price5_3_input.setText(str(price5_3))
            self.ui.price6_desc_combobox.setCurrentIndex(self.ui.price6_desc_combobox.findData(price6_desc))
            self.ui.price6_1_input.setText(str(price6_1))
            self.ui.price6_2_input.setText(str(price6_2))
            self.ui.price6_3_input.setText(str(price6_3))
            self.ui.expiry_input.setText(str(expiry))

            self.ui.group_combobox.setCurrentIndex(self.ui.group_combobox.findData(group))

            self.ui.price1_1_currency_combobox.setCurrentIndex(
                self.ui.price1_1_currency_combobox.findData(price1_1_unit))
            self.ui.price2_1_currency_combobox.setCurrentIndex(
                self.ui.price2_1_currency_combobox.findData(price2_1_unit))
            self.ui.price3_1_currency_combobox.setCurrentIndex(
                self.ui.price3_1_currency_combobox.findData(price3_1_unit))
            self.ui.price4_1_currency_combobox.setCurrentIndex(
                self.ui.price4_1_currency_combobox.findData(price4_1_unit))
            self.ui.price5_1_currency_combobox.setCurrentIndex(
                self.ui.price5_1_currency_combobox.findData(price5_1_unit))
            self.ui.price6_1_currency_combobox.setCurrentIndex(
                self.ui.price6_1_currency_combobox.findData(price6_1_unit))

            self.ui.price1_2_currency_combobox.setCurrentIndex(
                self.ui.price1_2_currency_combobox.findData(price1_2_unit))
            self.ui.price2_2_currency_combobox.setCurrentIndex(
                self.ui.price2_2_currency_combobox.findData(price2_2_unit))
            self.ui.price3_2_currency_combobox.setCurrentIndex(
                self.ui.price3_2_currency_combobox.findData(price3_2_unit))
            self.ui.price4_2_currency_combobox.setCurrentIndex(
                self.ui.price4_2_currency_combobox.findData(price4_2_unit))
            self.ui.price5_2_currency_combobox.setCurrentIndex(
                self.ui.price5_2_currency_combobox.findData(price5_2_unit))
            self.ui.price6_2_currency_combobox.setCurrentIndex(
                self.ui.price6_2_currency_combobox.findData(price6_2_unit))

            self.ui.price1_3_currency_combobox.setCurrentIndex(
                self.ui.price1_3_currency_combobox.findData(price1_3_unit))
            self.ui.price2_3_currency_combobox.setCurrentIndex(
                self.ui.price2_3_currency_combobox.findData(price2_3_unit))
            self.ui.price3_3_currency_combobox.setCurrentIndex(
                self.ui.price3_3_currency_combobox.findData(price3_3_unit))
            self.ui.price4_3_currency_combobox.setCurrentIndex(
                self.ui.price4_3_currency_combobox.findData(price4_3_unit))
            self.ui.price5_3_currency_combobox.setCurrentIndex(
                self.ui.price5_3_currency_combobox.findData(price5_3_unit))
            self.ui.price6_3_currency_combobox.setCurrentIndex(
                self.ui.price6_3_currency_combobox.findData(price6_3_unit))

            if default_unit == 1:
                self.ui.unit1_default_radiobox.setChecked(True)
            elif default_unit == 2:
                self.ui.unit2_default_radiobox.setChecked(True)
            elif default_unit == 3:
                self.ui.unit3_default_radiobox.setChecked(True)

            self.ui.type_combobox.setCurrentIndex(self.ui.type_combobox.findData(type))
            if int(groupped_material) == 1:
                self.ui.groupped_material_checkbox.setChecked(True)
                self.ui.groupped_material_btn.setEnabled(True)
            else:
                self.ui.groupped_material_checkbox.setChecked(False)
                self.ui.groupped_material_btn.setDisabled(True)

            self.ui.standard_unit1_combobox.setCurrentIndex(self.ui.unit1_combobox.findData(str(unit1)))
            self.ui.standard_unit2_combobox.setCurrentIndex(self.ui.unit2_combobox.findData(str(unit2)))
            self.ui.standard_unit3_combobox.setCurrentIndex(self.ui.unit3_combobox.findData(str(unit3)))

            self.ui.yearly_required_input.setText(str(yearly_required))
            self.ui.standard_work_hours_input.setText(str(work_hours))
            self.ui.standard_unit3_quantity_input.setText(str(standard_unit3_quantity))
            self.ui.standard_unit2_quantity_input.setText(str(standard_unit2_quantity))
            self.ui.standard_unit1_quantity_input.setText(str(standard_unit1_quantity))

            self.ui.manufacture_hall_combobox.setCurrentIndex(self.ui.manufacture_hall_combobox.findData(str(manufacture_hall)))

            self.ui.material_addition_account_combobox.setCurrentIndex(self.ui.material_addition_account_combobox.findData(addition_account))
            self.ui.material_discount_account_combobox.setCurrentIndex(self.ui.material_discount_account_combobox.findData(discount_account))
    
    def fetchAccounts(self):
        self.ui.material_addition_account_combobox.clear()
        self.ui.material_discount_account_combobox.clear()

        self.ui.material_addition_account_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.material_discount_account_combobox.addItem(self.language_manager.translate("NONE"), None)

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.material_addition_account_combobox.addItem(display_text, data)
            self.ui.material_discount_account_combobox.addItem(display_text, data)

    def fetchCurrencies(self):
        # clear previous items to prevent duplications
        self.ui.price1_1_currency_combobox.clear()
        self.ui.price1_2_currency_combobox.clear()
        self.ui.price1_3_currency_combobox.clear()

        self.ui.price2_1_currency_combobox.clear()
        self.ui.price2_2_currency_combobox.clear()
        self.ui.price2_3_currency_combobox.clear()

        self.ui.price3_1_currency_combobox.clear()
        self.ui.price3_2_currency_combobox.clear()
        self.ui.price3_3_currency_combobox.clear()

        self.ui.price4_1_currency_combobox.clear()
        self.ui.price4_2_currency_combobox.clear()
        self.ui.price4_3_currency_combobox.clear()

        self.ui.price5_1_currency_combobox.clear()
        self.ui.price5_2_currency_combobox.clear()
        self.ui.price5_3_currency_combobox.clear()

        self.ui.price6_1_currency_combobox.clear()
        self.ui.price6_2_currency_combobox.clear()
        self.ui.price6_3_currency_combobox.clear()

        # fetch new items
        currencies = self.database_operations.fetchCurrencies()

        # Add currencies to exchange combobox
        for currency in currencies:
            id = currency[0]
            display_text = currency[1]
            data = id

            self.ui.price1_1_currency_combobox.addItem(display_text, data)
            self.ui.price1_2_currency_combobox.addItem(display_text, data)
            self.ui.price1_3_currency_combobox.addItem(display_text, data)

            self.ui.price2_1_currency_combobox.addItem(display_text, data)
            self.ui.price2_2_currency_combobox.addItem(display_text, data)
            self.ui.price2_3_currency_combobox.addItem(display_text, data)

            self.ui.price3_1_currency_combobox.addItem(display_text, data)
            self.ui.price3_2_currency_combobox.addItem(display_text, data)
            self.ui.price3_3_currency_combobox.addItem(display_text, data)

            self.ui.price4_1_currency_combobox.addItem(display_text, data)
            self.ui.price4_2_currency_combobox.addItem(display_text, data)
            self.ui.price4_3_currency_combobox.addItem(display_text, data)

            self.ui.price5_1_currency_combobox.addItem(display_text, data)
            self.ui.price5_2_currency_combobox.addItem(display_text, data)
            self.ui.price5_3_currency_combobox.addItem(display_text, data)

            self.ui.price6_1_currency_combobox.addItem(display_text, data)
            self.ui.price6_2_currency_combobox.addItem(display_text, data)
            self.ui.price6_3_currency_combobox.addItem(display_text, data)

    def fetchPricesNames(self):
        prices_names = self.database_operations.fetchPrices()
        for price_name in prices_names:
            price_name_id = price_name[0]
            price_name_text = price_name[1]
            self.ui.price1_desc_combobox.addItem(price_name_text, price_name_id)
            self.ui.price2_desc_combobox.addItem(price_name_text, price_name_id)
            self.ui.price3_desc_combobox.addItem(price_name_text, price_name_id)
            self.ui.price4_desc_combobox.addItem(price_name_text, price_name_id)
            self.ui.price5_desc_combobox.addItem(price_name_text, price_name_id)
            self.ui.price6_desc_combobox.addItem(price_name_text, price_name_id)

    def openSelectAccountWindow(self, account_combobox):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            account_combobox.setCurrentIndex(account_combobox.findData(result['id']))

    def openSelectGroupWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sqlconnector, 'groups')
        result = data_picker.showUi()
        if result is not None:
            self.ui.group_combobox.setCurrentIndex(self.ui.group_combobox.findData(result['id']))

    def fetchUnits(self):
        self.ui.unit1_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.unit2_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.unit3_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.standard_unit1_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.standard_unit2_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.standard_unit3_combobox.addItem(self.language_manager.translate("NONE"), None)
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.unit1_combobox.addItem(display_text, data)
            self.ui.unit2_combobox.addItem(display_text, data)
            self.ui.unit3_combobox.addItem(display_text, data)

            self.ui.standard_unit1_combobox.addItem(display_text, data)
            self.ui.standard_unit2_combobox.addItem(display_text, data)
            self.ui.standard_unit3_combobox.addItem(display_text, data)


    def fetchUnitsConversionValue(self):
        unit1 = self.ui.unit1_combobox.currentData()
        unit2 = self.ui.unit2_combobox.currentData()
        unit3 = self.ui.unit3_combobox.currentData()
        if unit1 and unit1 != self.language_manager.translate("NONE"):
            if unit2 and unit2 != self.language_manager.translate("NONE"):
                conversion_value = self.database_operations.fetchUnitConversionValueBetween(unit2, unit1)
                if conversion_value:
                    self.ui.unit2_to_unit1_convert.setText(str(conversion_value))
                else:
                    self.ui.unit2_to_unit1_convert.setText(str(""))
            else:
                self.ui.unit2_to_unit1_convert.setText(str(""))
            if unit3 and unit3 != self.language_manager.translate("NONE"):   
                conversion_value = self.database_operations.fetchUnitConversionValueBetween(unit3, unit1)
                if conversion_value:
                    self.ui.unit3_to_unit1_convert.setText(str(conversion_value))
                else:
                    self.ui.unit3_to_unit1_convert.setText(str(""))
            else:
                self.ui.unit3_to_unit1_convert.setText(str(""))

    def saveMaterial(self):
        material = self.ui.materials_tree.currentItem()
        if (str(type(material)) == "<class 'NoneType'>"):
                pass
        else:
            material_id = material.text(2)
            if material_id and material_id != '':
                code = self.ui.code_input.text()
                name = self.ui.name_input.text()
                specs = self.ui.specs_input.text()
                size = self.ui.size_input.text()
                manufacturer = self.ui.manufacturer_input.text()
                color = self.ui.color_input.text()
                origin = self.ui.origin_input.text()
                quality = self.ui.quality_input.text()
                model = self.ui.model_input.text()
                manufacture_hall = self.ui.manufacture_hall_combobox.currentData()
                unit1 = self.ui.unit1_combobox.currentData()
                unit2 = self.ui.unit2_combobox.currentData()
                unit3 = self.ui.unit3_combobox.currentData()
                current_quantity = self.ui.current_quantity_input.text()
                max_quantity = self.ui.max_quantity_input.text()
                min_quantity = self.ui.min_quantity_input.text()
                request_limit = self.ui.request_limit_input.text()
                gift = self.ui.gift_input.text()
                gift_for = self.ui.gift_for_input.text()
                price1_desc = self.ui.price1_desc_combobox.currentData()
                price1_1 = self.ui.price1_1_input.text()
                price1_2 = self.ui.price1_2_input.text()
                price1_3 = self.ui.price1_3_input.text()
                price2_desc = self.ui.price2_desc_combobox.currentData()
                price2_1 = self.ui.price2_1_input.text()
                price2_2 = self.ui.price2_2_input.text()
                price2_3 = self.ui.price2_3_input.text()
                price3_desc = self.ui.price3_desc_combobox.currentData()
                price3_1 = self.ui.price3_1_input.text()
                price3_2 = self.ui.price3_2_input.text()
                price3_3 = self.ui.price3_3_input.text()
                price4_desc = self.ui.price4_desc_combobox.currentData()
                price4_1 = self.ui.price4_1_input.text()
                price4_2 = self.ui.price4_2_input.text()
                price4_3 = self.ui.price4_3_input.text()
                price5_desc = self.ui.price5_desc_combobox.currentData()
                price5_1 = self.ui.price5_1_input.text()
                price5_2 = self.ui.price5_2_input.text()
                price5_3 = self.ui.price5_3_input.text()
                price6_desc = self.ui.price6_desc_combobox.currentData()
                price6_1 = self.ui.price6_1_input.text()
                price6_2 = self.ui.price6_2_input.text()
                price6_3 = self.ui.price6_3_input.text()
                expiry = self.ui.expiry_input.text()
                group = self.ui.group_combobox.currentData()
                price1_1_unit = self.ui.price1_1_currency_combobox.currentData()
                price2_1_unit = self.ui.price2_1_currency_combobox.currentData()
                price3_1_unit = self.ui.price3_1_currency_combobox.currentData()
                price4_1_unit = self.ui.price4_1_currency_combobox.currentData()
                price5_1_unit = self.ui.price5_1_currency_combobox.currentData()
                price6_1_unit = self.ui.price6_1_currency_combobox.currentData()
                price1_2_unit = self.ui.price1_2_currency_combobox.currentData()
                price2_2_unit = self.ui.price2_2_currency_combobox.currentData()
                price3_2_unit = self.ui.price3_2_currency_combobox.currentData()
                price4_2_unit = self.ui.price4_2_currency_combobox.currentData()
                price5_2_unit = self.ui.price5_2_currency_combobox.currentData()
                price6_2_unit = self.ui.price6_2_currency_combobox.currentData()
                price1_3_unit = self.ui.price1_3_currency_combobox.currentData()
                price2_3_unit = self.ui.price2_3_currency_combobox.currentData()
                price3_3_unit = self.ui.price3_3_currency_combobox.currentData()
                price4_3_unit = self.ui.price4_3_currency_combobox.currentData()
                price5_3_unit = self.ui.price5_3_currency_combobox.currentData()
                price6_3_unit = self.ui.price6_3_currency_combobox.currentData()
                material_type = self.ui.type_combobox.currentData()  # Todo replace all combobox.itemData(combobox.currentIndex()) with combobox.currentData()
                groupped = 1 if self.ui.groupped_material_checkbox.isChecked() else 0
                standard_unit1_quantity = self.ui.standard_unit1_quantity_input.text()
                standard_unit2_quantity = self.ui.standard_unit2_quantity_input.text()
                standard_unit3_quantity = self.ui.standard_unit3_quantity_input.text()
                standard_work_hours = self.ui.standard_work_hours_input.text()
                yearly_required = self.ui.yearly_required_input.text()
                material_discount_account = self.ui.material_discount_account_combobox.currentData()
                material_addition_account = self.ui.material_addition_account_combobox.currentData()


                variables = [code, name, specs, size, manufacturer, color, origin, quality, model, manufacture_hall, unit1, unit2, unit3, current_quantity, max_quantity, min_quantity, request_limit, gift, gift_for, price1_desc, price1_1, price1_2, price1_3, price2_desc, price2_1, price2_2, price2_3, price3_desc, price3_1, price3_2, price3_3, price4_desc, price4_1, price4_2, price4_3, price5_desc, price5_1, price5_2, price5_3, price6_desc, price6_1, price6_2, price6_3, expiry, group, price1_1_unit, price2_1_unit, price3_1_unit, price4_1_unit, price5_1_unit, price6_1_unit, price1_2_unit, price2_2_unit, price3_2_unit, price4_2_unit, price5_2_unit, price6_2_unit, price1_3_unit, price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit, price6_3_unit, standard_unit1_quantity, standard_unit2_quantity, standard_unit3_quantity, standard_work_hours, yearly_required, material_discount_account, material_addition_account]
                for i in range(len(variables)):
                    if str(variables[i]).lower() == 'none':
                        variables[i] = ''
                (code, name, specs, size, manufacturer, color, origin, quality, model, manufacture_hall, unit1, unit2, unit3, current_quantity, max_quantity, min_quantity, request_limit, gift, gift_for, price1_desc, price1_1, price1_2, price1_3, price2_desc, price2_1, price2_2, price2_3, price3_desc, price3_1, price3_2, price3_3, price4_desc, price4_1, price4_2, price4_3, price5_desc, price5_1, price5_2, price5_3, price6_desc, price6_1, price6_2, price6_3, expiry, group, price1_1_unit, price2_1_unit, price3_1_unit, price4_1_unit, price5_1_unit, price6_1_unit, price1_2_unit, price2_2_unit, price3_2_unit, price4_2_unit, price5_2_unit, price6_2_unit, price1_3_unit, price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit, price6_3_unit, standard_unit1_quantity, standard_unit2_quantity, standard_unit3_quantity, standard_work_hours, yearly_required, material_discount_account, material_addition_account) = variables

                default_unit = 0
                if self.ui.unit1_default_radiobox.isChecked() and unit1 != '':
                    default_unit = 1
                if self.ui.unit2_default_radiobox.isChecked() and unit2 != '':
                    default_unit = 2
                if self.ui.unit3_default_radiobox.isChecked() and unit3 != '':
                    default_unit = 3

                if (name.replace(" ", "")):  # if name is not empty and not only spaces
                    if unit1 == '':
                        win32api.MessageBox(0, self.language_manager.translate("FIRST_UNIT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
                    elif (unit2 != '' and self.ui.unit2_to_unit1_convert.text() == '') or (unit3 != '' and self.ui.unit3_to_unit1_convert.text() == ''):
                        win32api.MessageBox(0, self.language_manager.translate("CONVERSION_FACTOR_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))
                    elif default_unit == 0:
                        win32api.MessageBox(0, self.language_manager.translate("DEFAULT_UNIT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
                    else:   
                        self.database_operations.updateMaterial(material_id, code, name, specs, size, manufacturer, color,
                                                            origin, quality, model, unit1, unit2, unit3, default_unit,
                                                            current_quantity,
                                                            max_quantity, min_quantity, request_limit, gift, gift_for,
                                                            price1_desc, price1_1, price1_2, price1_3, price2_desc,
                                                            price2_1, price2_2, price2_3, price3_desc, price3_1, price3_2,
                                                            price3_3, price4_desc, price4_1, price4_2, price4_3,
                                                            price5_desc, price5_1, price5_2, price5_3, price6_desc,
                                                            price6_1, price6_2, price6_3, expiry, group, price1_1_unit,
                                                            price2_1_unit, price3_1_unit, price4_1_unit, price5_1_unit,
                                                            price6_1_unit, price1_2_unit, price2_2_unit, price3_2_unit,
                                                            price4_2_unit, price5_2_unit, price6_2_unit, price1_3_unit,
                                                            price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit,
                                                            price6_3_unit, material_type, groupped,
                                                            standard_unit1_quantity, standard_unit2_quantity,
                                                            standard_unit3_quantity, standard_work_hours,
                                                            yearly_required, manufacture_hall, material_discount_account, material_addition_account)
                        
                        self.fetchGroups()
                        self.fetchMaterials()
                        self.clearFields()
                        self.ui.groupped_material_checkbox.setChecked(False)
                        self.enableGrouppedMaterialCompositionButton()
                else:
                    win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))

            
    def openAddMaterialWindow(self):
        # permission = self.database_operations.fetchUserPermission(current_user, 'materials', 'RW')
        # if permission:
        Ui_AddMaterial_Logic(self.sqlconnector).showUi()
        self.fetchGroups()
        self.fetchMaterials()
        # else:
        #     win32api.MessageBox(0, "ليس لديك الصلاحية لفتح هذه النافذة.", "خطأ")

    def openGrouppedMaterialCompositionWindow(self):
        material = self.ui.materials_tree.currentItem()
        if (str(type(material)) == "<class 'NoneType'>"):
            pass
        else:
            material_id = material.text(2)
            if not material_id:
                messagebox_result = win32api.MessageBox(0, self.language_manager.translate("MATERIAL_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"), MB_YESNO)
            else:
                messagebox_result = win32api.MessageBox(0, self.language_manager.translate("CURRENT_DATA_WILL_BE_SAVED"), self.language_manager.translate("ALERT"), MB_YESNO)
                if (messagebox_result == IDYES):
                    self.saveMaterial()
                    Ui_GrouppedMaterialComposition_Logic(self.sqlconnector, material_id).showUi()

    def enableGrouppedMaterialCompositionButton(self):
        self.ui.groupped_material_btn.setEnabled(
            True) if self.ui.groupped_material_checkbox.isChecked() else self.ui.groupped_material_btn.setDisabled(True)
        
    def enableUnit2andUnit3(self):
        unit1 = self.ui.unit1_combobox.currentData()
        if unit1 and unit1 != '':
            self.ui.unit2_combobox.setEnabled(True)
            self.ui.unit3_combobox.setEnabled(True)
        else:
            self.ui.unit2_combobox.setCurrentIndex(0)
            self.ui.unit3_combobox.setCurrentIndex(0)
            self.ui.unit2_combobox.setDisabled(True)
            self.ui.unit3_combobox.setDisabled(True)
            self.ui.unit2_to_unit1_convert.setText(str(""))
            self.ui.unit3_to_unit1_convert.setText(str(""))

    def enableUnit2Prices(self):
        unit2 = self.ui.unit2_combobox.currentData()
        if unit2 is not None:
            self.ui.price1_2_input.setEnabled(True)
            self.ui.price1_2_currency_combobox.setEnabled(True)
            self.ui.price2_2_input.setEnabled(True)
            self.ui.price2_2_currency_combobox.setEnabled(True)
            self.ui.price3_2_input.setEnabled(True)
            self.ui.price3_2_currency_combobox.setEnabled(True)
            self.ui.price4_2_input.setEnabled(True)
            self.ui.price4_2_currency_combobox.setEnabled(True)
            self.ui.price5_2_input.setEnabled(True)
            self.ui.price5_2_currency_combobox.setEnabled(True)
            self.ui.price6_2_input.setEnabled(True)
            self.ui.price6_2_currency_combobox.setEnabled(True)
        else:
            self.ui.price1_2_input.setDisabled(True)
            self.ui.price1_2_currency_combobox.setDisabled(True)
            self.ui.price2_2_input.setDisabled(True)
            self.ui.price2_2_currency_combobox.setDisabled(True)
            self.ui.price3_2_input.setDisabled(True)
            self.ui.price3_2_currency_combobox.setDisabled(True)
            self.ui.price4_2_input.setDisabled(True)
            self.ui.price4_2_currency_combobox.setDisabled(True)
            self.ui.price5_2_input.setDisabled(True)
            self.ui.price5_2_currency_combobox.setDisabled(True)
            self.ui.price6_2_input.setDisabled(True)
            self.ui.price6_2_currency_combobox.setDisabled(True)

            self.ui.price1_2_input.clear()
            self.ui.price2_2_input.clear()
            self.ui.price3_2_input.clear()
            self.ui.price4_2_input.clear()
            self.ui.price5_2_input.clear()
            self.ui.price6_2_input.clear()

    def enableUnit3Prices(self):
        unit3 = self.ui.unit3_combobox.currentData()
        if unit3 is not None:
            self.ui.price1_3_input.setEnabled(True)
            self.ui.price1_3_currency_combobox.setEnabled(True)
            self.ui.price2_3_input.setEnabled(True)
            self.ui.price2_3_currency_combobox.setEnabled(True)
            self.ui.price3_3_input.setEnabled(True)
            self.ui.price3_3_currency_combobox.setEnabled(True)
            self.ui.price4_3_input.setEnabled(True)
            self.ui.price4_3_currency_combobox.setEnabled(True)
            self.ui.price5_3_input.setEnabled(True)
            self.ui.price5_3_currency_combobox.setEnabled(True)
            self.ui.price6_3_input.setEnabled(True)
            self.ui.price6_3_currency_combobox.setEnabled(True)
        else:
            self.ui.price1_3_input.setDisabled(True)
            self.ui.price1_3_currency_combobox.setDisabled(True)
            self.ui.price2_3_input.setDisabled(True)
            self.ui.price2_3_currency_combobox.setDisabled(True)
            self.ui.price3_3_input.setDisabled(True)
            self.ui.price3_3_currency_combobox.setDisabled(True)
            self.ui.price4_3_input.setDisabled(True)
            self.ui.price4_3_currency_combobox.setDisabled(True)
            self.ui.price5_3_input.setDisabled(True)
            self.ui.price5_3_currency_combobox.setDisabled(True)
            self.ui.price6_3_input.setDisabled(True)
            self.ui.price6_3_currency_combobox.setDisabled(True)

            self.ui.price1_3_input.clear()
            self.ui.price2_3_input.clear()
            self.ui.price3_3_input.clear()
            self.ui.price4_3_input.clear()
            self.ui.price5_3_input.clear()
            self.ui.price6_3_input.clear()

    def updateQuantities(self):
        if hasattr(self, 'sender'):
            caller = self.sender().objectName()
            if str(caller).lower() == 'standard_unit1_quantity_input' or str(caller).lower() == 'unit1_combobox':
                unit1 = self.ui.unit1_combobox.currentData()
                quantity1 = self.ui.standard_unit1_quantity_input.text()

                if unit1 and unit1 != self.language_manager.translate("NONE"):
                    self.ui.standard_unit1_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit1))
                    self.ui.standard_unit1_quantity_input.setEnabled(True)
                else:
                    self.ui.standard_unit1_combobox.setCurrentIndex(0)
                    self.ui.standard_unit1_quantity_input.clear()
                    self.ui.standard_unit1_quantity_input.setDisabled(True)

                if self.ui.unit2_to_unit1_convert.text() != '':
                    unit1_to_unit2_rate = 1 / float(self.ui.unit2_to_unit1_convert.text())
                    if quantity1:
                        quantity2 = float(quantity1) * unit1_to_unit2_rate
                        self.ui.standard_unit2_quantity_input.setText(str(round(quantity2, 4)))

                if self.ui.unit3_to_unit1_convert.text() != '':
                    unit1_to_unit3_rate = 1 / float(self.ui.unit3_to_unit1_convert.text())
                    if quantity1:
                        quantity3 = float(quantity1) * unit1_to_unit3_rate
                        self.ui.standard_unit3_quantity_input.setText(str(round(quantity3, 4)))

            elif str(caller).lower() == 'standard_unit2_quantity_input' or str(caller).lower() == 'unit2_combobox':
                unit2 = self.ui.unit2_combobox.currentData()
                quantity2 = self.ui.standard_unit2_quantity_input.text()

                if unit2 and unit2 != self.language_manager.translate("NONE"):
                    self.ui.standard_unit2_combobox.setCurrentIndex(self.ui.standard_unit2_combobox.findData(unit2))
                    self.ui.standard_unit2_quantity_input.setEnabled(True)
                else:
                    self.ui.standard_unit2_combobox.setCurrentIndex(0)
                    self.ui.standard_unit2_quantity_input.clear()
                    self.ui.standard_unit2_quantity_input.setDisabled(True)

                unit2_to_unit1_rate = float(
                    self.ui.unit2_to_unit1_convert.text()) if self.ui.unit2_to_unit1_convert.text() else 0
                if quantity2 and unit2_to_unit1_rate:
                    quantity1 = float(quantity2) * unit2_to_unit1_rate
                    self.ui.standard_unit1_quantity_input.setText(str(round(quantity1, 4)))

                unit3_to_unit1_rate = float(
                    self.ui.unit3_to_unit1_convert.text()) if self.ui.unit3_to_unit1_convert.text() else 0
                if unit3_to_unit1_rate and unit2_to_unit1_rate != '':
                    unit2_to_unit3_rate = unit2_to_unit1_rate / unit3_to_unit1_rate
                    if quantity2:
                        quantity3 = float(quantity2) * unit2_to_unit3_rate
                        self.ui.standard_unit3_quantity_input.setText(str(round(quantity3, 4)))

            elif str(caller).lower() == 'standard_unit3_quantity_input' or str(caller).lower() == 'unit3_combobox':
                unit3 = self.ui.unit3_combobox.currentData()
                quantity3 = self.ui.standard_unit3_quantity_input.text()

                if unit3 and unit3 != self.language_manager.translate("NONE"):
                    self.ui.standard_unit3_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit3))
                    self.ui.standard_unit3_quantity_input.setEnabled(True)
                else:
                    self.ui.standard_unit3_combobox.setCurrentIndex(0)
                    self.ui.standard_unit3_quantity_input.clear()
                    self.ui.standard_unit3_quantity_input.setDisabled(True)
                unit3_to_unit1_rate = float(
                    self.ui.unit3_to_unit1_convert.text()) if self.ui.unit3_to_unit1_convert.text() else 0
                if quantity3 and unit3_to_unit1_rate:
                    quantity1 = float(quantity3) * unit3_to_unit1_rate
                    self.ui.standard_unit1_quantity_input.setText(str(round(quantity1, 4)))

                unit2_to_unit1_rate = float(
                    self.ui.unit2_to_unit1_convert.text()) if self.ui.unit2_to_unit1_convert.text() else 0
                if unit2_to_unit1_rate and unit3_to_unit1_rate:
                    unit3_to_unit2_rate = unit3_to_unit1_rate / unit2_to_unit1_rate
                    if quantity3:
                        quantity2 = float(quantity3) * unit3_to_unit2_rate
                        self.ui.standard_unit2_quantity_input.setText(str(round(quantity2, 4)))
        else:
            pass

    def fetchMachines(self):
        self.ui.machines_combobox.clear()
        machines = self.database_operations.fetchMachines()
        for machine in machines:
            id = machine[0]
            name = machine[1]
            # years_age = machone[2]
            # estimated_waste_value = machone[3]
            # estimated_waste_currency = machone[4]
            # estimated_waste_account = machone[5]
            # invoice_item_id = machone[6]
            # notes = machone[7]
            self.ui.machines_combobox.addItem(name, id)

    def fetchMachineModes(self):
        self.ui.machine_modes_combobox.clear()
        machine_id = self.ui.machines_combobox.currentData()
        if machine_id:
            machine_modes = self.database_operations.fetchMachineModes(machine_id)
            for machine_mode in machine_modes:
                id = machine_mode[0]
                machine_id = machine_mode[1]
                name = machine_mode[2]
                date = machine_mode[3]
                self.ui.machine_modes_combobox.addItem(name, id)

    def addMachine(self):
        material = self.ui.materials_tree.currentItem()  
        if material:
            material_id = material.text(2)
            if material_id:
                machine_id = self.ui.machines_combobox.currentData()
                machine_mode = self.ui.machine_modes_combobox.currentData()
                use_duration= self.ui.machine_use_duration_input.text()
                exclusive = int(self.ui.machine_exclusive.isChecked())

                if machine_id and machine_mode and str(use_duration).strip():
                    self.database_operations.addMaterialMachine(material_id, machine_id, machine_mode, use_duration, exclusive)
                else:
                    win32api.MessageBox(0, self.language_manager.translate("ALL_FIELDS_MUST_BE_ENTERED"), self.language_manager.translate("ALERT"))

    def removeMaterialMachine(self):
        messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"),  MB_YESNO)
        if(messagebox_result==IDYES):
            machine_usage_row = self.ui.machines_table.currentRow()
            if machine_usage_row >= 0:
                machine_usage_id = self.ui.machines_table.item(machine_usage_row, 0).text()
                if machine_usage_id:
                    self.database_operations.deleteMaterialMachine(machine_usage_id)
        elif(messagebox_result==IDNO):
            pass

    def fetchMaterialMachines(self):
        self.ui.machines_table.setRowCount(0)
        material = self.ui.materials_tree.currentItem()
        if material and material != '':
            material_id = material.text(2)
            machines = self.database_operations.fetchMaterialMachines(material_id)
            for machine in machines:
                id = machine[0]
                material_id = machine[1]
                machine_id = machine[2]
                mode_id = machine[3]
                usage_duration = machine[4]
                exclusive = machine[5]
                machine_name = machine[6]
                mode_name = machine[7]

                exclusive = 'Yes' if exclusive==1 else 'No'

                # Create a empty row at bottom of table
                numRows = self.ui.machines_table.rowCount()
                self.ui.machines_table.insertRow(numRows)

                # Add text to the row
                self.ui.machines_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.machines_table.setItem(numRows, 1, QTableWidgetItem(str(machine_id)))
                self.ui.machines_table.setItem(numRows, 2, QTableWidgetItem(str(machine_name)))
                self.ui.machines_table.setItem(numRows, 3, QTableWidgetItem(str(mode_id)))
                self.ui.machines_table.setItem(numRows, 4, QTableWidgetItem(str(mode_name)))
                self.ui.machines_table.setItem(numRows, 5, MyTableWidgetItem(str(usage_duration), int(usage_duration)))
                self.ui.machines_table.setItem(numRows, 6, QTableWidgetItem(str(exclusive)))

    def fetchManufactureHall(self):
        self.ui.manufacture_hall_combobox.addItem(self.language_manager.translate("NONE"), '')
        manufacture_halls = self.database_operations.fetchManufactureHalls()
        for manufacture_hall in manufacture_halls:
            id = manufacture_hall[0]
            warehouse_id = manufacture_hall[1]
            date = manufacture_hall[2]
            name = manufacture_hall[3]
            account_id = manufacture_hall[4]
            account_name = manufacture_hall[5]
            self.ui.manufacture_hall_combobox.addItem(name, id)
            
    def fetchMaterialMoves(self):
        self.ui.moves_table.setRowCount(0)
        material = self.ui.materials_tree.currentItem()
        if material:
            material_id = material.text(2)
            if material_id and material_id != '':
                moves = self.database_operations.fetchMaterialMoves(material_id)
                for move in moves:
                    move_id = move['move_id']
                    warehouse_id = move['warehouse_id']
                    move_type = move['move_type']
                    cause = move['move_origin'] or ''
                    cause_id = move['move_origin_id'] or ''
                    date = move['move_date']
                    quantity = move['move_quantity']
                    unit = move['move_unit']
                    material_id = move['material_id']
                    from_warehouse_name = move['from_warehouse_name'] or ''
                    material_name = move['material_name']
                    unit_name = move['unit_name']
                    to_warehouse_name = move['to_warehouse_name'] or ''
                    item_currency = move['item_currency']
                    item_currency_name = move['item_currency_name']
                    item_unit_price = move['item_unit_price']

                    # Create an empty row at the bottom of the table
                    numRows = self.ui.moves_table.rowCount()
                    self.ui.moves_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.moves_table.setItem(numRows, 0, QTableWidgetItem(str(move_id)))
                    self.ui.moves_table.setItem(numRows, 1, QTableWidgetItem(str(from_warehouse_name)))
                    self.ui.moves_table.setItem(numRows, 2, QTableWidgetItem(str(to_warehouse_name)))
                    self.ui.moves_table.setItem(numRows, 3, QTableWidgetItem(str(quantity)))
                    self.ui.moves_table.setItem(numRows, 4, QTableWidgetItem(str(unit)))
                    self.ui.moves_table.setItem(numRows, 5, QTableWidgetItem(str(unit_name)))
                    self.ui.moves_table.setItem(numRows, 6, QTableWidgetItem(str(move_type)))
                    self.ui.moves_table.setItem(numRows, 7, QTableWidgetItem(str(item_currency_name)))
                    self.ui.moves_table.setItem(numRows, 8, QTableWidgetItem(str(item_unit_price)))
                    self.ui.moves_table.setItem(numRows, 9, QTableWidgetItem(str(date)))
                    self.ui.moves_table.setItem(numRows, 10, QTableWidgetItem(str(cause)))
                    self.ui.moves_table.setItem(numRows, 11, QTableWidgetItem(str(cause_id)))

                    # Colorize the row red when move_type is reduce
                    if move_type == 'reduce':
                        colorizeTableRow(self.ui.moves_table, numRows, background_color=light_red_color, text_color=black)
                    elif move_type == 'add':
                        colorizeTableRow(self.ui.moves_table, numRows, background_color=light_green_color, text_color=black)
                    elif move_type == 'transfer':
                        colorizeTableRow(self.ui.moves_table, numRows, background_color=blue_sky_color, text_color=black)

    def removeMaterial(self):
        material_id = self.ui.materials_tree.currentItem().text(2)
        if material_id and material_id != '':
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if messagebox_result == IDYES:
                try:    
                    self.database_operations.removeMaterial(material_id)
                    self.fetchGroups()
                    self.fetchMaterials()
                except:
                    win32api.MessageBox(None, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ALERT"))

    def clearFields(self):
        # Define lists of fields by type
        input_fields = [
            'code_input', 'name_input', 'specs_input', 'size_input', 'manufacturer_input',
            'color_input', 'origin_input', 'quality_input', 'model_input',
            'current_quantity_input', 'max_quantity_input', 'min_quantity_input', 
            'request_limit_input', 'gift_input', 'gift_for_input',
            'unit2_to_unit1_convert', 'unit3_to_unit1_convert',
            'standard_unit1_quantity_input', 'standard_unit2_quantity_input', 
            'standard_unit3_quantity_input', 'standard_work_hours_input',
            'yearly_required_input',
            'price1_1_input', 'price2_1_input', 'price3_1_input', 'price4_1_input',
            'price5_1_input', 'price6_1_input',
        ]
        
        combobox_fields = [
            'manufacture_hall_combobox', 'machines_combobox', 'machine_modes_combobox',
            'unit1_combobox', 'unit2_combobox', 'unit3_combobox'
        ]

        # Clear all input fields
        for field in input_fields:
            getattr(self.ui, field).clear()
        
        # Reset all comboboxes to index 0
        for field in combobox_fields:
            getattr(self.ui, field).setCurrentIndex(0)
        
        # Clear table and tree selection
        self.ui.moves_table.setRowCount(0)
        self.ui.materials_tree.clearSelection()

    def removeMaterialMove(self):
        current_row = self.ui.moves_table.currentRow()
        move_id = self.ui.moves_table.item(current_row, 0).text() if current_row else None
        if move_id:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if messagebox_result == IDYES:
                self.database_operations.removeMaterialMove(move_id=move_id)
                self.fetchMaterialMoves()
