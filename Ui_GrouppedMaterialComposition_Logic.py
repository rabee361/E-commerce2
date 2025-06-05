import win32api
from PyQt5 import QtCore
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QTableWidgetItem, QAbstractItemView, QHeaderView, QApplication
from DatabaseOperations import DatabaseOperations
from Ui_GrouppedMaterialComposition import Ui_GrouppedMaterialComposition
from PyQt5.QtCore import Qt, QTranslator
from LanguageManager import LanguageManager
from Colors import blue_sky_color  

class Ui_GrouppedMaterialComposition_Logic(QDialog):
    def __init__(self, sql_connector, material_id):
        super().__init__()
        self.material_id = material_id
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_GrouppedMaterialComposition()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.fetchSelectedMaterial()
        self.fetchGroups()
        self.fetchMaterials()
        self.fetchCompositions()
        self.fetchCompositionData()
        self.fetchUnits()
        self.ui.quantity1_input.setValidator(QDoubleValidator())
        self.ui.quantity2_input.setValidator(QDoubleValidator())
        self.ui.quantity3_input.setValidator(QDoubleValidator())

        self.ui.quantity1_input.textEdited.connect(lambda: self.updateMaterialQuantities())
        self.ui.quantity2_input.textEdited.connect(lambda: self.updateMaterialQuantities())
        self.ui.quantity3_input.textEdited.connect(lambda: self.updateMaterialQuantities())

        self.ui.save_composition_btn.clicked.connect(lambda: self.addComposition())

        self.ui.materials_tree.clicked.connect(lambda: self.updateMaterialUnits())
        self.ui.add_material_btn.clicked.connect(lambda: self.addMaterial())
        self.ui.remove_material_btn.clicked.connect(lambda: self.removeMaterial())
        self.ui.save_btn.clicked.connect(lambda: self.save(window))

    def fetchGroups(self):
        self.ui.materials_tree.clear()
        groups = self.database_operations.fetchGroups()

        # Create dictionary to hold group information for quick parent lookup
        group_dict = {}
        for group in groups:
            id = group['id']
            name = group['name']
            code = group['code']
            date = group['date_col']
            parent_id = group['parent_id']
            parent_name = group['parent_name']

            item = QTreeWidgetItem([str(name), '', '', str(id)])
            group_dict[id] = {"item": item, "parent_id": parent_id}

        # Add the groups to the tree
        for id, group in group_dict.items():
            parent_id = group["parent_id"]
            if not parent_id:  # Root element
                self.ui.materials_tree.addTopLevelItem(group["item"])
                print(group["item"].text(0))
            else:  # Child element
                parent_group = group_dict.get(parent_id)
                if parent_group:
                    parent_group["item"].addChild(group["item"])
                else:  # Parent not added yet
                    children_list = group_dict.get(parent_id, {}).get("children", [])
                    children_list.append(group)
                    group_dict[parent_id]["children"] = children_list

        # Add any children that were not added in the first pass
        while True:
            added_child = False
            for id, group in group_dict.items():
                children_list = group.get("children")
                if children_list:
                    for child in children_list:
                        parent_group = group_dict.get(child["parent_id"])
                        if parent_group and parent_group["item"] is not None:
                            parent_group["item"].addChild(child["item"])
                            children_list.remove(child)
                            added_child = True
            if not added_child:
                break

    def fetchMaterials(self):
        # Get the materials and add each one to its appropriate group in tree
        materials = self.database_operations.fetchMaterials()
        for material in materials:
            id = material['id']
            code = material['code']
            name = material['name']
            group = material['group_col']
            unit1 = material['unit1']
            unit2 = material['unit2']
            unit3 = material['unit3']
            groupped = material['groupped']
            unit1_to_unit2_rate = material['unit1_to_unit2_rate']
            unit1_to_unit3_rate = material['unit1_to_unit3_rate']

            if str(unit1_to_unit2_rate).lower()=='none':
                unit1_to_unit2_rate=''
            if str(unit1_to_unit3_rate).lower()=='none':
                unit1_to_unit3_rate=''

            units_data = [unit1, unit2, unit3, unit1_to_unit2_rate, unit1_to_unit3_rate]
            print(units_data)
            if (int(id) != int(self.material_id) and int(groupped)!=int(1)): #Because the material cannot be composed of itself
                title = str(code) + "-" + str(name)

                if not group:
                    item = QTreeWidgetItem(['', str(title), str(id), ''])
                    item.setData(0, QtCore.Qt.UserRole, units_data)
                    print(item.text(0))
                    self.ui.materials_tree.addTopLevelItem(item)
                else:
                    groups_already_in_tree = self.ui.materials_tree.findItems(str(group),Qt.MatchExactly | Qt.MatchRecursive, 3)
                    if (len(groups_already_in_tree) > 0):  # Group already exists in tree, so append its child
                        group = groups_already_in_tree[0]  # only one would exist because we search using ID
                        material = QTreeWidgetItem(['', str(title), str(id), ''])
                        material.setData(0, QtCore.Qt.UserRole, units_data)
                        group.addChild(material)

    def fetchUnits(self):
        self.ui.unit1_combobox.clear()
        self.ui.unit2_combobox.clear()
        self.ui.unit3_combobox.clear()
        self.ui.unit1_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.unit2_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.unit3_combobox.addItem(self.language_manager.translate("NONE"), None)
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.unit1_combobox.addItem(display_text, data)
            self.ui.unit2_combobox.addItem(display_text, data)
            self.ui.unit3_combobox.addItem(display_text, data)

    def fetchSelectedMaterial(self):
        material = self.database_operations.fetchMaterial(self.material_id)
        id = material[0]
        code = material[1]
        name = material[2]

        if (str(code).lower() == 'none'):
            code = ''
        if (str(name).lower() == 'none'):
            name = ''

        self.ui.code_input.setText(str(code))
        self.ui.name_input.setText(str(name))
        self.ui.id_input.setText(str(id))
        
    def updateMaterialUnits(self):
        self.ui.unit1_to_unit2_rate_input.clear()
        self.ui.unit1_to_unit3_rate_input.clear()

        material_id = self.ui.materials_tree.currentItem().text(2)
        if material_id and material_id != '':

            units_data = self.ui.materials_tree.currentItem().data(0, QtCore.Qt.UserRole)
            print(units_data)
            unit1, unit2, unit3, unit2_to_unit1_rate, unit3_to_unit1_rate = units_data

            if unit1 is not None and str(unit1) != '' and str(unit1).lower() != 'none':
                self.ui.unit1_combobox.setCurrentIndex(self.ui.unit1_combobox.findData(unit1))
                self.ui.quantity1_input.setEnabled(True)
            else:
                self.ui.quantity1_input.setDisabled(True)

            if unit2 is not None and str(unit2) != '' and str(unit2).lower() != 'none':
                self.ui.unit2_combobox.setCurrentIndex(self.ui.unit2_combobox.findData(unit2))
                self.ui.quantity2_input.setEnabled(True)
                self.ui.unit1_to_unit2_rate_input.setText(str(unit2_to_unit1_rate))
            else:
                self.ui.quantity2_input.setDisabled(True)

            if unit3 is not None and str(unit3) != '' and str(unit3).lower() != 'none':
                self.ui.unit3_combobox.setCurrentIndex(self.ui.unit3_combobox.findData(unit3))
                self.ui.quantity3_input.setEnabled(True)
                self.ui.unit1_to_unit3_rate_input.setText(str(unit3_to_unit1_rate))
            else:
                self.ui.quantity3_input.setDisabled(True)
            # TODO if unit is modified in material card

    def updateMaterialQuantities(self):
        caller = self.sender().objectName() #the object that fired this function
        if str(caller).lower()=='quantity1_input':
            quantity1=self.ui.quantity1_input.text()
            if self.ui.unit1_to_unit2_rate_input.text()!='' and quantity1 != '':
                unit1_to_unit2_rate = float(self.ui.unit1_to_unit2_rate_input.text())
                quantity2 = float(quantity1) * unit1_to_unit2_rate
                self.ui.quantity2_input.setText(str(round(quantity2, 4)))
            else:
                self.ui.quantity2_input.setText('')
            if self.ui.unit1_to_unit3_rate_input.text()!='' and quantity1 != '':
                unit1_to_unit3_rate = float(self.ui.unit1_to_unit3_rate_input.text())
                quantity3 = float(quantity1) * unit1_to_unit3_rate
                self.ui.quantity3_input.setText(str(round(quantity3, 4)))
            else:
                self.ui.quantity3_input.setText('')
        elif str(caller).lower()=='quantity2_input':
            quantity2=self.ui.quantity2_input.text()
            unit2_to_unit1_rate = 1/float(self.ui.unit1_to_unit2_rate_input.text())
            quantity1 = float(quantity2) * unit2_to_unit1_rate
            self.ui.quantity1_input.setText(str(quantity1))
            if self.ui.unit1_to_unit3_rate_input.text()!='' and quantity2 != '':
                unit2_to_unit3_rate =  float(self.ui.unit1_to_unit3_rate_input.text())/float(self.ui.unit1_to_unit2_rate_input.text())
                quantity3=float(quantity2)*unit2_to_unit3_rate
                self.ui.quantity3_input.setText(str(round(quantity3, 4)))
        elif str(caller).lower()=='quantity3_input':
            quantity3=self.ui.quantity3_input.text()
            unit3_to_unit1_rate = 1/float(self.ui.unit1_to_unit3_rate_input.text())
            print(str(unit3_to_unit1_rate))
            quantity1=float(quantity3)*unit3_to_unit1_rate
            self.ui.quantity1_input.setText(str(quantity1))
            if self.ui.unit1_to_unit2_rate_input.text()!='' and quantity3 != '':
                unit3_to_unit2_rate =  float(self.ui.unit1_to_unit2_rate_input.text())/float(self.ui.unit1_to_unit3_rate_input.text())
                quantity2=float(quantity3)*unit3_to_unit2_rate
                self.ui.quantity2_input.setText(str(round(quantity2, 4)))

    # def addMaterial(self):
    #     selected_tree_item = self.ui.materials_tree.currentItem()
    #     composition_id = self.ui.composition_combobox.currentText() or ''
    #     selected_material_id = selected_tree_item.text(1)
    #     selected_material_name = selected_tree_item.text(2)
        
    #     if selected_material_id:
    #         quantity = self.ui.quantity1_input.text()
    #         unit = self.ui.unit1_combobox.currentData()
    #         unit_name = self.ui.unit1_combobox.currentText()
            
    #         if not quantity:
    #             win32api.MessageBox(0,self.language_manager.translate("QUANTITY_MUST_BE_ENTERED"), self.language_manager.translate("ERROR")) # type: ignore
    #         else:
    #             # Find or create composition parent row
    #             root = self.ui.material_composition_tree.invisibleRootItem()
    #             composition_parent = None
    #             for i in range(root.childCount()):
    #                 item = root.child(i)
    #                 if item.text(0) == str(composition_id):
    #                     composition_parent = item
    #                     break
                
    #             if not composition_parent:
    #                 # Create new composition parent
    #                 composition_parent = QTreeWidgetItem(['',str(composition_id), '', '', '', '','','',''])
    #                 composition_parent.setBackground(0, QtCore.Qt.lightGray)
    #                 self.ui.material_composition_tree.addTopLevelItem(composition_parent)
                
    #             # Create and add material item under composition parent
    #             material_item = QTreeWidgetItem(['','','',str(selected_material_name), str(selected_material_id), str(quantity), str(unit_name), str(unit)])
    #             for i in range(material_item.columnCount()):
    #                 material_item.setBackground(i, QtCore.Qt.blue)
    #             composition_parent.addChild(material_item)

    def addMaterial(self):
        selected_tree_item = self.ui.materials_tree.currentItem()
        composition_id = self.ui.composition_combobox.currentData() or ''
        selected_material_id = selected_tree_item.text(2)
        selected_material_name = selected_tree_item.text(1)
        
        if selected_material_id:
            quantity = self.ui.quantity1_input.text()
            unit = self.ui.unit1_combobox.currentData()
            unit_name = self.ui.unit1_combobox.currentText()
            
            if not quantity:
                win32api.MessageBox(0,self.language_manager.translate("QUANTITY_MUST_BE_ENTERED"), self.language_manager.translate("ERROR")) # type: ignore
            else:
                # Find composition parent row
                root = self.ui.material_composition_tree.invisibleRootItem()
                composition_parent = None
                for i in range(root.childCount()):
                    item = root.child(i)
                    if item.text(0) == str(composition_id):
                        composition_parent = item
                        break
                
                if composition_parent:
                    # Check if material already exists in this composition
                    material_exists = False
                    for i in range(composition_parent.childCount()):
                        child = composition_parent.child(i)
                        if child.text(3) == selected_material_id:
                            material_exists = True
                            break
                    
                    if not material_exists:
                        # Create and add material item under composition parent
                        material_item = QTreeWidgetItem(['','','',str(selected_material_id), str(selected_material_name), str(quantity), str(unit_name), str(unit)])
                        for i in range(material_item.columnCount()):
                            material_item.setBackground(i, blue_sky_color)
                        composition_parent.addChild(material_item)
                    else:
                        win32api.MessageBox(0,self.language_manager.translate("MATERIAL_ALREADY_EXISTS_IN_COMPOSITION"), self.language_manager.translate("ERROR")) # type: ignore
                else:
                    win32api.MessageBox(0,self.language_manager.translate("COMPOSITION_MUST_EXIST"), self.language_manager.translate("ERROR")) # type: ignore

    def removeMaterial(self):
        composition_tree = self.ui.material_composition_tree
        selected_item = composition_tree.currentItem()
        if selected_item:
            #get material ID
            composition_material_id = selected_item.text(4)
            #remove the item from the composition tree
            root = composition_tree.invisibleRootItem()
            (selected_item.parent() or root).removeChild(selected_item)
                
    def save(self, window):
        groupped_material_id = self.material_id
        root = self.ui.material_composition_tree.invisibleRootItem()
        
        # Loop through all parent nodes (compositions)
        for i in range(root.childCount()):
            composition_parent = root.child(i)
            composition_id = composition_parent.text(0)
            
            # Get all materials for this composition
            composition_materials = []
            for j in range(composition_parent.childCount()):
                material_item = composition_parent.child(j)
                composition_material_id = material_item.text(3)
                quantity = material_item.text(5)
                unit = material_item.text(7)
                composition_materials.append([composition_material_id, quantity, unit])
            
            # Update the database for this composition
            self.database_operations.updateGrouppedMaterialComposition(composition_id, groupped_material_id, composition_materials)
        window.accept()

    def fetchCompositions(self):
        self.ui.composition_combobox.clear()
        composition_materials = self.database_operations.fetchMaterialCompositions(self.material_id)
        for material in composition_materials:
            composition_id = material['id'] 
            composition_name = material['name']
            self.ui.composition_combobox.addItem(str(composition_name), composition_id)
            
    def fetchCompositionData(self):
        self.ui.material_composition_tree.clear()
        composition_materials = self.database_operations.fetchMaterialCompositionsData(self.material_id)
        
        # Group materials by composition
        compositions = {}
        for material in composition_materials:
            composition_id = material['composition_id'] 
            composition_name = material['composition_name']

            if composition_id not in compositions:
                compositions[composition_id] = {
                    'name': composition_name,
                    'materials': []
                }
            compositions[composition_id]['materials'].append(material)

        # Add compositions and their materials to tree
        for composition_id, composition in compositions.items():
            # Create parent composition item
            parent = QTreeWidgetItem([str(composition_id), str(composition['name']),'','','','',''])
            parent.setBackground(0, QtCore.Qt.lightGray) # Set parent background color
            for i in range(parent.columnCount()):
                parent.setBackground(i, QtCore.Qt.lightGray)
            self.ui.material_composition_tree.addTopLevelItem(parent)

            # Add child materials
            for material in composition['materials']:
                composition_material_id = material['composition_material_id']
                quantity = material['quantity']
                unit_name = material['unit_name'] 
                unit = material['unit']

                materials_in_tree = self.ui.materials_tree.findItems(str(composition_material_id), Qt.MatchExactly | Qt.MatchRecursive, 2)
                if (len(materials_in_tree) > 0):
                    composition_material_name = materials_in_tree[0].text(1)
                    
                    child = QTreeWidgetItem(['','','', str(composition_material_id), str(composition_material_name) , str(quantity), str(unit_name), str(unit)])
                    # Set child background color
                    for i in range(child.columnCount()):
                        child.setBackground(i, blue_sky_color)
                    parent.addChild(child)

    def addComposition(self):
        composition_name = self.ui.composition_name_input.text()
        if composition_name:
            composition_in_tree = self.ui.material_composition_tree.findItems(str(composition_name), Qt.MatchExactly | Qt.MatchRecursive, 1)
            
            if (len(composition_in_tree) > 0):
                # Composition already exists, add the material to it
                parent = composition_in_tree[0]
            else:
                composition_id = self.database_operations.addComposition(composition_name, self.material_id)
                parent = QTreeWidgetItem([str(composition_id), str(composition_name),'','','','',''])
                parent.setBackground(0, QtCore.Qt.lightGray) # Set parent background color
                for i in range(parent.columnCount()):
                    parent.setBackground(i, QtCore.Qt.lightGray)
                self.ui.material_composition_tree.addTopLevelItem(parent)
                self.fetchCompositions()

            self.ui.composition_name_input.clear()

