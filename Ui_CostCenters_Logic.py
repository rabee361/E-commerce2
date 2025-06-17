import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QHeaderView, QTableWidgetItem
from win32con import MB_YESNO, IDYES, IDNO
from PyQt5.QtCore import QCoreApplication , QTranslator
from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_AddCostCenter_Logic import Ui_AddCostCenter_Logic
from Ui_CostCenters import Ui_CostCenters
from PyQt5.QtCore import Qt
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon


class Ui_CostCenters_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_CostCenters()
        self.pendingSave = False  # This changes when an attribute of the cost center changed and not yet saved using save()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        
    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        window.setWindowIcon(QIcon(':/icons/dispatch.png'))
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.division_factor_input.setValidator(QDoubleValidator())
        self.ui.cost_center_combobox.setEnabled(False)
        self.ui.parent_combobox.setEnabled(False)
        self.ui.cost_centers_tree.hideColumn(1)
        self.ui.aggregation_distributive_table.hideColumn(0)
        self.ui.aggregation_distributive_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.fetchCostCenters()
        self.ui.save_btn.clicked.connect(lambda: self.save())
        self.ui.add_btn.clicked.connect(lambda: self.addAggregationDistributiveCostCenter())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteCostCenter())
        self.ui.add_new_btn.clicked.connect(lambda: self.openAddCostCenterWindow())
        self.ui.cost_centers_tree.clicked.connect(lambda: self.fetchSelectedCostCenter())
        self.ui.type_combobox.currentIndexChanged.connect(lambda: self.uiElementsEnabler())
        self.ui.select_cost_center_btn.clicked.connect(lambda: self.openSelectCostCenterWindow())
        self.ui.select_parent_btn.clicked.connect(lambda: self.openSelectParentWindow())

        # when changing anything, set PendingSave to True
        self.ui.name_input.textChanged.connect(lambda: self.setPendingSave(True))
        self.ui.notes_input.textChanged.connect(lambda: self.setPendingSave(True))
        self.ui.type_combobox.currentIndexChanged.connect(lambda: self.setPendingSave(True))
        self.ui.parent_combobox.currentIndexChanged.connect(lambda: self.setPendingSave(True))

        # Initialize items in the 'type_combobox' QComboBox of the 'ui' object with Arabic text and corresponding English values
        self.ui.type_combobox.addItem(self.language_manager.translate("NORMAL"), "normal")
        self.ui.type_combobox.addItem(self.language_manager.translate("AGGREGATOR"), "aggregator")
        self.ui.type_combobox.addItem(self.language_manager.translate("DISTRIBUTOR"), "distributor")  # Replace with the correct Arabic word

        self.ui.division_factor_changable_checkbox.clicked.connect(lambda: self.updateChangableDivisionFactorState())

    def setPendingSave(self, value):
        self.pendingSave = value

    def openSelectCostCenterWindow(self):
        selected_cost_center = self.ui.cost_centers_tree.currentItem()
        if selected_cost_center:
            selected_cost_center_id = int(selected_cost_center.text(1))
            data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True, exclusions=[selected_cost_center_id])
            result = data_picker.showUi()
            if result is not None:
                self.ui.cost_center_combobox.setCurrentIndex(self.ui.cost_center_combobox.findData(result['id']))

    def openSelectParentWindow(self):
        exclusions = []
        cost_centers = self.database_operations.fetchCostCenters(cost_center_type=['distributor', 'aggregator'])
        for cost_center in cost_centers:
            exclusions.append(cost_center[0])
            selected_cost_center = self.ui.cost_centers_tree.currentItem()
            if selected_cost_center:
                selected_cost_center_id = int(selected_cost_center.text(1))
                exclusions.append(selected_cost_center_id)
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'cost_centers', include_none_option=True, exclusions=exclusions)
        result = data_picker.showUi()
        if result is not None:
            self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(result['id']))

    def fetchCostCenters(self):
        cost_centers = self.database_operations.fetchCostCenters()
        self.ui.parent_combobox.clear()
        self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)
        children_queue = []
        for cost_center in cost_centers:
            id = cost_center[0]
            name = cost_center[1]
            parent_id = cost_center[4]

            self.ui.parent_combobox.addItem(name, id)
            self.ui.cost_center_combobox.addItem(name, id)

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(name), str(id)])
                self.ui.cost_centers_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.cost_centers_tree.findItems(str(parent_id),
                                                                            Qt.MatchExactly | Qt.MatchRecursive, 1)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(1)

                        child_item = QTreeWidgetItem([str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(cost_center)

        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0]
                name = child[1]
                parent_id = child[4]

                items_already_in_tree = self.ui.cost_centers_tree.findItems(str(parent_id),
                                                                            Qt.MatchExactly | Qt.MatchRecursive, 1)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(1)

                        child_item = QTreeWidgetItem([str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)

        self.setPendingSave(False)  # all data is new, nothing changed to be saved

    def addAggregationDistributiveCostCenter(self):
        master_cost_center = self.ui.cost_centers_tree.currentItem()
        if master_cost_center and master_cost_center != '':
            master_cost_center = master_cost_center.text(1) 
            type = self.ui.type_combobox.currentData()
            if type in ('distributor', 'aggregator'):  # otherwise, we cant add agg/dist centers
                #if type is distributive, check if the new total sum of division parameters does not exceed 100
                total_percentage = 0
                for row in range(self.ui.aggregation_distributive_table.rowCount()):
                    item = self.ui.aggregation_distributive_table.item(row, 2)  # 2 is the column index
                    if item and item.text().isdigit():
                        total_percentage += float(item.text())

                if total_percentage>100:
                    win32api.MessageBox(0, self.language_manager.translate("SUM_OF_PARTS_SHOULD_NOT_EXCEED_100"), self.language_manager.translate("ALERT"))
                else:
                    if self.pendingSave:
                        self.save()
                    cost_center = self.ui.cost_center_combobox.currentData()
                    division_factor = self.ui.division_factor_input.text()
                    if int(cost_center) != int(master_cost_center):
                        self.database_operations.addAggregationDistributiveCostCenter(master_cost_center, cost_center,
                                                                                      division_factor)
                        self.fetchCostCenterAggregationsDistributives()

    def openAddCostCenterWindow(self):
        Ui_AddCostCenter_Logic(self.sql_connector).showUi()
        self.ui.cost_centers_tree.clear()
        self.fetchCostCenters()

    def fetchSelectedCostCenter(self):
        cost_center_id = self.ui.cost_centers_tree.currentItem().text(1)
        if cost_center_id and cost_center_id != '':
            cost_center = self.database_operations.fetchCostCenter(cost_center_id)
            id = cost_center[0]
            name = cost_center[1]
            notes = cost_center[2]
            type = cost_center[3]
            parent_id = cost_center[4]
            changable_division_factor = cost_center[5]

            if (str(name).lower() == 'none'):
                name = ''
            if (str(notes).lower() == 'none'):
                notes = ''
            if (str(parent_id).lower() == 'none'):
                parent_id = None

            self.ui.name_input.setText(str(name))
            self.ui.notes_input.setPlainText(str(notes))
            self.ui.type_combobox.setCurrentIndex(self.ui.type_combobox.findText(type))
            
            # Clear and repopulate parent combobox
            self.ui.parent_combobox.clear()
            self.ui.cost_center_combobox.clear()
            self.ui.parent_combobox.addItem(self.language_manager.translate("NONE"), None)
            self.ui.cost_center_combobox.addItem(self.language_manager.translate("NONE"), None)
            cost_centers = self.database_operations.fetchCostCenters()
            for center in cost_centers:
                # Skip adding the currently selected cost center as a parent option
                if str(center[0]) != str(cost_center_id):
                    self.ui.parent_combobox.addItem(center[1], center[0])
                    self.ui.cost_center_combobox.addItem(center[1], center[0])
            # Set the parent if one exists
            if parent_id:
                self.ui.parent_combobox.setCurrentIndex(self.ui.parent_combobox.findData(parent_id))
            else:
                self.ui.parent_combobox.setCurrentIndex(0)
            self.ui.division_factor_changable_checkbox.setChecked(bool(changable_division_factor))
            self.uiElementsEnabler()
            self.setPendingSave(False)
            self.fetchCostCenterAggregationsDistributives()

    def deleteCostCenter(self):
        id = self.ui.cost_centers_tree.currentItem()
        if (str(type(id)) == "<class 'NoneType'>"):
            pass
        else:
            if win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO) == IDYES:
                # Find and remove the item from the combobox , cost center tree and the input fields
                cost_center = self.database_operations.fetchCostCenter(id.text(1))
                current_item = self.ui.cost_centers_tree.currentItem()
                index = self.ui.cost_centers_tree.indexOfTopLevelItem(current_item)
                id = cost_center[0]
                combobox_index = self.ui.cost_center_combobox.findData(id)
                try:
                    # delete from the database
                    self.database_operations.deleteCostCenter(id)
                    self.ui.type_combobox.setCurrentText(self.language_manager.translate("NORMAL"))
                    self.uiElementsEnabler()
                    if combobox_index != -1:
                        self.ui.cost_center_combobox.removeItem(combobox_index)
                    if index != -1:
                        self.ui.cost_centers_tree.takeTopLevelItem(index)
                    self.ui.name_input.clear()
                    self.ui.notes_input.clear()
                except:
                    win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
                    return

    def save(self):
        try:
            cost_center_id = self.ui.cost_centers_tree.currentItem().text(1)
            if cost_center_id and cost_center_id != '':
                name = self.ui.name_input.text()
                notes = self.ui.notes_input.toPlainText()
                type = self.ui.type_combobox.currentText()
                parent = self.ui.parent_combobox.currentData()

                if str(type) in ('aggregator', 'distributor', self.language_manager.translate("AGGREGATOR"), self.language_manager.translate("DISTRIBUTOR")):
                    parent = None
                    messagebox_result = win32api.MessageBox(None, self.language_manager.translate("ALERT_COST_CENTER_CANNOT_BE_PARENT"), self.language_manager.translate("ALERT"), MB_YESNO)
                    if (messagebox_result == IDYES):
                        save = True
                    if (messagebox_result == IDNO):
                        save = False
                else:
                    save = True

                if (save):
                    if str(name).strip():
                        self.database_operations.updateCostCenter(cost_center_id, name, notes, type, parent)
                        self.ui.cost_centers_tree.clear()
                        self.ui.cost_center_combobox.clear()
                        self.ui.parent_combobox.clear()
                        self.ui.name_input.clear()
                        self.ui.notes_input.clear()
                        self.fetchCostCenters()
                        self.setPendingSave(False)
        except:
            pass

    def uiElementsEnabler(self):
        type = self.ui.type_combobox.currentText()

        if str(type) in ('normal', self.language_manager.translate("NORMAL")):
            self.ui.aggregation_distributive_groupBox.setDisabled(True)
            self.ui.select_parent_btn.setEnabled(True)
            self.ui.aggregation_distributive_groupBox.setDisabled(True)
        else:
            self.ui.parent_combobox.setCurrentIndex(0)
            self.ui.select_parent_btn.setEnabled(False)
            self.ui.aggregation_distributive_groupBox.setEnabled(True)

            if str(type) in ('aggregator', self.language_manager.translate("AGGREGATOR")):
                self.ui.aggregation_distributive_table.hideColumn(2)
                self.ui.division_factor_changable_checkbox.setDisabled(True)
                self.ui.division_factors_sum_input.setDisabled(True)
                self.ui.division_factor_input.setDisabled(True)

            elif str(type) in ('distributor', self.language_manager.translate("DISTRIBUTOR")):
                self.ui.aggregation_distributive_table.showColumn(2)
                self.ui.division_factor_changable_checkbox.setEnabled(True)
                self.ui.division_factors_sum_input.setEnabled(True)
                self.ui.division_factor_input.setEnabled(True)

    def fetchCostCenterAggregationsDistributives(self):
        self.ui.aggregation_distributive_table.setRowCount(0)
        cost_center_id = self.ui.cost_centers_tree.currentItem()
        division_factors_sum = 0
        if cost_center_id and cost_center_id != '':
            cost_center_id = self.ui.cost_centers_tree.currentItem().text(1)
            cost_center_aggregations_distributives = self.database_operations.fetchCostCenterAggregationsDistributives(cost_center_id)
            for cost_center_aggregation_distributive in cost_center_aggregations_distributives:
                id = cost_center_aggregation_distributive[0]
                master_cost_center = cost_center_aggregation_distributive[1]
                cost_center = cost_center_aggregation_distributive[2]
                division_factor = cost_center_aggregation_distributive[3]
                if division_factor:
                    division_factors_sum += float(division_factor)

                name = cost_center_aggregation_distributive[4]
                numRows = self.ui.aggregation_distributive_table.rowCount()
                self.ui.aggregation_distributive_table.insertRow(numRows)
                self.ui.aggregation_distributive_table.setItem(numRows, 0, MyTableWidgetItem(str(id), int(id)))
                self.ui.aggregation_distributive_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
                self.ui.aggregation_distributive_table.setItem(numRows, 2, QTableWidgetItem(str(division_factor)))
        self.ui.division_factors_sum_input.setText(str(division_factors_sum))

    def updateChangableDivisionFactorState(self):
        state = self.ui.division_factor_changable_checkbox.isChecked()
        try:
            cost_center_id = self.ui.cost_centers_tree.currentItem().text(1)
            if cost_center_id and cost_center_id != '':
                self.database_operations.updateCostCenterChangableDivisionFactorState(cost_center_id, state)
        except:
            pass
