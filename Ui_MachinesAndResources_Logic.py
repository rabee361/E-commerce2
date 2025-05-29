import win32api
from PyQt5.QtWidgets import QDialog, QInputDialog, QTableWidgetItem
from win32con import IDYES, IDNO, MB_YESNO
from MyCustomTableCellDelegate import MyCustomTableCellDelegate

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_MachinesAndResources import Ui_MachinesAndResources
from PyQt5.QtGui import QDoubleValidator
from Ui_Machine_Maintenance_Logic import Ui_Machine_Maintenance_Logic
from PyQt5.QtCore import Qt
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon
class Ui_MachinesAndResources_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_MachinesAndResources()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.setWindowIcon(QIcon('icons/factory.png'))
        window.exec()

    def initialize(self, window):
        self.ui.machine_invoice_item_id_input.setVisible(False)
        self.ui.resource_account_combobox.setEnabled(False)
        self.ui.estimated_waste_account_combobox.setEnabled(False)

        self.ui.mode_resource_consumption_per_minute_input.setValidator(QDoubleValidator())
        self.ui.resources_cost_per_minute_input.setValidator(QDoubleValidator())

        self.ui.select_resource_account_btn.clicked.connect(lambda: self.openSelectAccountWindow('resource_account'))
        self.ui.select_estimated_waste_account_btn.clicked.connect(lambda: self.openSelectAccountWindow('estimated_waste_account'))
        self.ui.select_machine_btn.clicked.connect(lambda: self.openMachinesWindow())

        self.ui.add_production_line_btn.clicked.connect(lambda: self.addProductionLine())
        self.ui.add_production_line_btn.clicked.connect(lambda: self.fetchProductionLines())
        self.ui.save_production_line_btn.clicked.connect(lambda: self.fetchProductionLines())
        self.ui.production_lines_table.itemSelectionChanged.connect(lambda: self.fetchSelectedProductionLine())
        self.ui.delete_production_line_btn.clicked.connect(lambda: self.removeProductionLine())
        self.ui.save_production_line_btn.clicked.connect(lambda: self.saveProductionLine())

        self.ui.production_lines_table.itemSelectionChanged.connect(lambda: self.fetchProductionLineMachines())
        self.ui.add_production_line_machine_btn.clicked.connect(lambda: self.addProductionLineMachine())
        self.ui.delete_production_line_machine_btn.clicked.connect(lambda: self.removeProductionLineMachine())
            
        self.ui.machines_table.itemSelectionChanged.connect(lambda: self.fetchSelectedMachine())
        self.ui.machines_table.itemSelectionChanged.connect(lambda: self.fetchMachineModes())
        self.ui.select_machine_account_btn.clicked.connect(lambda: self.openSelectMachineAccount())
        self.ui.select_machine_opposite_account_btn.clicked.connect(lambda: self.openSelectMachineOppositeAccount())
        self.ui.add_machine_btn.clicked.connect(lambda: self.addMachine())
        self.ui.add_machine_btn.clicked.connect(lambda: self.fetchMachines())
        self.ui.save_machine_btn.clicked.connect(lambda: self.saveMachine())
        self.ui.save_machine_btn.clicked.connect(lambda: self.fetchMachines())
        self.ui.delete_machine_btn.clicked.connect(lambda: self.removeMachine())

        self.ui.add_machine_mode_btn.clicked.connect(lambda: self.addMachineMode())
        self.ui.delete_machine_mode_btn.clicked.connect(lambda: self.removeMachineMode())
        self.ui.add_mode_resource_btn.clicked.connect(lambda: self.addModeResource())
        # self.ui.select_machine_acount_btn.connect(lambda: self.openSelectMachineAccountWindow)

        self.ui.delete_mode_resource_btn.clicked.connect(lambda: self.removeModeResource())
        self.ui.mode_resources_combobox.currentIndexChanged.connect(lambda: self.setModeResourceUnit())
        self.ui.machine_modes_table.itemSelectionChanged.connect(lambda: self.fetchModeResources())

        self.ui.resources_table.itemSelectionChanged.connect(lambda: self.fetchSelectedResource())
        self.ui.resources_table.itemSelectionChanged.connect(lambda: self.fetchResourceCosts())
        self.ui.add_resource_btn.clicked.connect(lambda: self.addResource())
        self.ui.save_resource_btn.clicked.connect(lambda: self.saveResource())
        self.ui.add_resource_cost_btn.clicked.connect(lambda: self.addResourceCost())
        self.ui.delete_resource_cost_btn.clicked.connect(lambda: self.removeResourceCost())
        self.ui.delete_resouce_btn.clicked.connect(lambda: self.deleteResource())

        self.ui.machine_maintenance_record_btn.clicked.connect(lambda: self.openMaintenanceRecord())

        
        self.ui.machines_browse_invoices_btn.clicked.connect(lambda: self.openInvoicePicker())
        self.ui.standard_hours_age_input.setValidator(QDoubleValidator())
        self.ui.machine_standard_age_input.setValidator(QDoubleValidator())
        self.ui.machine_standard_age_input.textChanged.connect(lambda: self.yearsHours(target='hours'))
        self.ui.standard_hours_age_input.textChanged.connect(lambda: self.yearsHours(target='years'))
        self.fetchMachines()
        self.fetchResources()
        self.fetchProductionLines()
        self.fetchCurrencies()
        self.fetchAccounts()
        self.fetchUnits()


    def openMaintenanceRecord(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id:
                Ui_Machine_Maintenance_Logic(self.sql_connector, machine_id=selected_machine_id).showUi()


    def openSelectMachineAccount(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.machine_account_combobox.setCurrentIndex(self.ui.machine_account_combobox.findData(result['id']))


    def openSelectMachineOppositeAccount(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.opposite_machine_account_combobox.setCurrentIndex(self.ui.opposite_machine_account_combobox.findData(result['id']))


    def openSelectAccountWindow(self, account_type):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            if account_type == 'resource_account':
                self.ui.resource_account_combobox.setCurrentIndex(self.ui.resource_account_combobox.findData(result['id']))
            elif account_type == 'estimated_waste_account':
                self.ui.estimated_waste_account_combobox.setCurrentIndex(self.ui.estimated_waste_account_combobox.findData(result['id']))

    def openMachinesWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'machines')
        result = data_picker.showUi()
        if result is not None:
            self.ui.production_line_machines_combobox.setCurrentIndex(self.ui.production_line_machines_combobox.findData(result['id']))

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            id = unit[0]
            display_text = unit[1]
            data = id
            self.ui.resource_cost_unit_combobox.addItem(display_text, data)

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            display_text = account[1]
            data = id
            self.ui.estimated_waste_account_combobox.addItem(display_text, data)
            self.ui.resource_account_combobox.addItem(display_text, data)
            self.ui.machine_account_combobox.addItem(display_text, data)
            self.ui.opposite_machine_account_combobox.addItem(display_text, data)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currencie in currencies:
            id = currencie[0]
            display_text = currencie[1]
            data = id
            self.ui.machine_cost_currency_combobox.addItem(display_text, data)
            self.ui.machine_estimated_waste_currency_combobox.addItem(display_text, data)
            self.ui.resource_cost_currency_combobox.addItem(display_text, data)

    def openSelectMachineAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.machine_account_combobox.setCurrentIndex(self.ui.machine_account_combobox.findData(result['id']))

    def fetchMachines(self):
        self.ui.machines_table.setRowCount(0)
        machines = self.database_operations.fetchMachines()
        for machine in machines:
            id = machine['id']
            name = machine['name']

            # Create a empty row at bottom of table
            numRows = self.ui.machines_table.rowCount()
            self.ui.machines_table.insertRow(numRows)

            self.ui.machines_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
            self.ui.machines_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

            # Add machine to production line machines combobox
            self.ui.production_line_machines_combobox.addItem(str(name), id)

    def fetchProductionLines(self):
        self.ui.production_lines_table.setRowCount(0)
        production_lines = self.database_operations.fetchProductionLines()
        delegate = MyCustomTableCellDelegate(col=1,row=None)
        self.ui.production_lines_table.setItemDelegate(delegate)
        if len(production_lines) > 0:
            for line in production_lines:
                id = line[0]
                name = line[1]

                # Create empty row at bottom of table
                numRows = self.ui.production_lines_table.rowCount()
                self.ui.production_lines_table.insertRow(numRows)

                # Add id and name to the row
                self.ui.production_lines_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.production_lines_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
                
    def fetchSelectedProductionLine(self):
        selected_row = self.ui.production_lines_table.currentRow()
        if selected_row >= 0:
            production_line_id = self.ui.production_lines_table.item(selected_row, 0).text()
            production_line = self.database_operations.fetchProductionLine(production_line_id)
            production_line_machines = self.database_operations.fetchProductionLineMachines(production_line_id)
            name = production_line['name'] or ''
            notes = production_line['notes'] or ''
            self.ui.production_line_name_input.setText(name)
            self.ui.production_line_notes_input.setText(notes)
            for machine in production_line_machines:
                numRows = self.ui.production_line_machines_table.rowCount()
                self.ui.production_line_machines_table.insertRow(numRows)
                self.ui.production_line_machines_table.setItem(numRows, 0, QTableWidgetItem(str(machine['id'])))
                self.ui.production_line_machines_table.setItem(numRows, 1, QTableWidgetItem(str(machine['machine_name'])))
                self.ui.production_line_machines_table.setItem(numRows, 2, QTableWidgetItem(str(machine['machine_notes'])))

    def fetchProductionLineMachines(self):
        selected_row = self.ui.production_lines_table.currentRow()
        if selected_row >= 0:
            self.ui.production_line_machines_table.setRowCount(0)  # Clear the table first
            production_line_id = self.ui.production_lines_table.item(selected_row, 0).text()
            production_line_machines = self.database_operations.fetchProductionLineMachines(production_line_id)
            delegate = MyCustomTableCellDelegate(col=2,row=None,)
            self.ui.production_line_machines_table.setItemDelegate(delegate)
            for machine in production_line_machines:
                # Create new row
                numRows = self.ui.production_line_machines_table.rowCount()
                self.ui.production_line_machines_table.insertRow(numRows)
                
                # Add machine details to table
                self.ui.production_line_machines_table.setItem(numRows, 0, QTableWidgetItem(str(machine['id'])))
                self.ui.production_line_machines_table.setItem(numRows, 1, QTableWidgetItem(str(machine['machine_name'])))
                self.ui.production_line_machines_table.setItem(numRows, 2, QTableWidgetItem(str(machine['machine_notes'])))

    def addProductionLineMachine(self):
        selected_row = self.ui.production_lines_table.currentRow()
        if selected_row >= 0:
            production_line_id = self.ui.production_lines_table.item(selected_row, 0).text()
            machine_id = self.ui.production_line_machines_combobox.currentData()
            machine_notes = self.ui.production_line_machines_notes_input.text()
            
            if machine_id:
                self.database_operations.addProductionLineMachine(production_line_id, machine_id,machine_notes)
                self.fetchProductionLineMachines()
                self.ui.production_line_machines_notes_input.clear()

    def removeProductionLineMachine(self):
        selected_row = self.ui.production_line_machines_table.currentRow()
        if selected_row >= 0:
            production_line_machine_id = self.ui.production_line_machines_table.item(selected_row, 0).text()
            self.database_operations.removeProductionLineMachine(production_line_machine_id)
            self.fetchProductionLineMachines()

    def addProductionLine(self):
        production_line_name, ok_pressed = QInputDialog.getText(None, "أضافة خط إنتاج جديد", "اسم الخط الإنتاجي:")
        if production_line_name.strip() != '':
            print(production_line_name)
            self.database_operations.addProductionLine(production_line_name)

    def saveProductionLine(self):
        selected_item = self.ui.production_lines_table.currentRow()
        if selected_item >= 0:  # Changed to >= 0 since currentRow() returns -1 if no selection
            try:
                production_line_id = self.ui.production_lines_table.item(selected_item, 0).text()
                name = self.ui.production_line_name_input.text()
                notes = self.ui.production_line_notes_input.text()
                if name.strip() != '':
                    self.database_operations.updateProductionLine(production_line_id, name, notes)
                    self.fetchProductionLines()
                    self.ui.production_line_name_input.clear()
                    self.ui.production_line_notes_input.clear()
            except AttributeError:
                pass

    def removeProductionLine(self):
        selected_row = self.ui.production_lines_table.currentRow()
        if selected_row >= 0:
            production_line_id = self.ui.production_lines_table.item(selected_row, 0).text()
            self.database_operations.removeProductionLine(production_line_id)
            self.fetchProductionLines()
            self.ui.production_line_name_input.clear()
            self.ui.production_line_notes_input.clear()

    def addMachine(self):
        machine_name, ok_pressed = QInputDialog.getText(None, "أضافة آلة جديدة", "اسم الآلة:")
        if machine_name.strip() and machine_name.strip() != '':
            self.database_operations.addMachine(machine_name)

    def fetchSelectedMachine(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id:
                machine_info = self.database_operations.fetchMachine(selected_machine_id)
                id = machine_info['id']
                name = machine_info['name']
                years_age = machine_info['years_age']
                estimated_waste_value = machine_info['estimated_waste_value']
                estimated_waste_currency = machine_info['estimated_waste_currency']
                estimated_waste_account = machine_info['estimated_waste_account']
                invoice_item_id = machine_info['invoice_item_id']
                notes = machine_info['notes']
                unit_price = machine_info['unit_price']
                currency_id = machine_info['currency_id']
                machine_account = machine_info['account']
                machine_opposite_account = machine_info['opposite_account']

                if name is None:
                    name = ""
                if years_age is None:
                    years_age = ""
                if estimated_waste_value is None:
                    estimated_waste_value = ""
                if invoice_item_id is None:
                    invoice_item_id = ""
                if notes is None:
                    notes = ""
                if unit_price is None:
                    unit_price = ""

                # Populate the UI inputs with the fetched machine information
                self.ui.machine_name_input.setText(name)
                self.ui.machine_cost_input.setText(str(unit_price))
                self.ui.machine_notes_input.setText(notes)
                self.ui.machine_standard_age_input.setText(str(years_age))
                self.ui.machine_estimated_waste_input.setText(str(estimated_waste_value))
                self.ui.machine_invoice_item_id_input.setText(str(invoice_item_id))
                self.ui.machine_estimated_waste_currency_combobox.setCurrentIndex(
                    self.ui.machine_estimated_waste_currency_combobox.findData(estimated_waste_currency))
                self.ui.machine_cost_currency_combobox.setCurrentIndex(
                    self.ui.machine_cost_currency_combobox.findData(currency_id))
                self.ui.estimated_waste_account_combobox.setCurrentIndex(
                    self.ui.estimated_waste_account_combobox.findData(estimated_waste_account))
                self.ui.machine_account_combobox.setCurrentIndex(
                    self.ui.machine_account_combobox.findData(machine_account))
                self.ui.opposite_machine_account_combobox.setCurrentIndex(
                    self.ui.opposite_machine_account_combobox.findData(machine_opposite_account))
                # Set the value of invoice_item_id to the respective input if applicable
                # self.ui.invoice_item_id_input.setText(str(invoice_item_id))
                self.fetchMachineConsumption()

    def fetchMachineConsumption(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            
            if selected_machine_id:
                # Clear existing data
                self.ui.machine_consumption_table.setRowCount(0)
                machine_work = self.database_operations.fetchTotalMachineWork(selected_machine_id)
                machine_resource_consumption = self.database_operations.fetchMachineModeResources(selected_machine_id)
                
                for machine_resource_consumption in machine_resource_consumption:
                    mode_id = machine_resource_consumption['mode_id']
                    mode_name = machine_resource_consumption['mode_name']
                    resource_id = machine_resource_consumption['resource_id']
                    consumption_per_minute = machine_resource_consumption['consumption_per_minute']
                    consumption_per_hour = consumption_per_minute * 60
                    resource_name = machine_resource_consumption['resource_name']
                    consumption_unit = machine_resource_consumption['consumption_unit']
                    resource_cost = machine_resource_consumption['resource_cost'] 
                    consumption_cost_per_minute = resource_cost * machine_work * consumption_per_minute
                    consumption_cost_per_hour = resource_cost * machine_work * consumption_per_hour
                    currency_name = machine_resource_consumption['currency_name']

                    numRows = self.ui.machine_consumption_table.rowCount()
                    self.ui.machine_consumption_table.insertRow(numRows)
                    
                    # Add resource details to table
                    self.ui.machine_consumption_table.setItem(numRows, 0, QTableWidgetItem(str(resource_id)))
                    self.ui.machine_consumption_table.setItem(numRows, 1, QTableWidgetItem(str(resource_name)))
                    self.ui.machine_consumption_table.setItem(numRows, 2, QTableWidgetItem(str(mode_name)))
                    self.ui.machine_consumption_table.setItem(numRows, 3, QTableWidgetItem(str(consumption_per_minute)))
                    self.ui.machine_consumption_table.setItem(numRows, 4, QTableWidgetItem(str(consumption_per_hour)))
                    self.ui.machine_consumption_table.setItem(numRows, 5, QTableWidgetItem(str(consumption_unit)))
                    self.ui.machine_consumption_table.setItem(numRows, 6, QTableWidgetItem(str(consumption_cost_per_minute)))
                    self.ui.machine_consumption_table.setItem(numRows, 7, QTableWidgetItem(str(consumption_cost_per_hour)))
                    self.ui.machine_consumption_table.setItem(numRows, 8, QTableWidgetItem(str(currency_name)))

    def saveMachine(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id: 
                name = self.ui.machine_name_input.text()
                estimated_waste_value = self.ui.machine_estimated_waste_input.text()
                machine_standard_age = self.ui.machine_standard_age_input.text()
                machine_notes = self.ui.machine_notes_input.text()
                machine_account = self.ui.machine_account_combobox.currentData()
                machine_cost_currency = self.ui.machine_cost_currency_combobox.currentData()
                machine_opposite_account = self.ui.opposite_machine_account_combobox.currentData()
                machine_invoice_item_id = self.ui.machine_invoice_item_id_input.text()
                estimated_waste_currency = self.ui.machine_estimated_waste_currency_combobox.currentData()
                estimated_waste_account = self.ui.estimated_waste_account_combobox.currentData()

                if not estimated_waste_currency:
                    estimated_waste_currency = ''
                if not estimated_waste_account:
                    estimated_waste_account = ''

                if str(name).strip():
                    self.database_operations.updateMachine(selected_machine_id, machine_account, machine_opposite_account, name, estimated_waste_value, machine_standard_age, machine_notes, machine_invoice_item_id,estimated_waste_currency, estimated_waste_account)

                    self.ui.machine_estimated_waste_input.clear()
                    self.ui.standard_hours_age_input.clear()
                    self.ui.machine_notes_input.clear()
                    self.ui.machine_account_combobox.setCurrentIndex(self.ui.machine_account_combobox.findData(0))
                    self.ui.machine_estimated_waste_currency_combobox.setCurrentIndex(self.ui.machine_estimated_waste_currency_combobox.findData(0))
                    self.ui.opposite_machine_account_combobox.setCurrentIndex(self.ui.opposite_machine_account_combobox.findData(0))
                    self.ui.estimated_waste_account_combobox.setCurrentIndex(self.ui.estimated_waste_account_combobox.findData(0))

    def removeMachine(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id:
                modes = self.database_operations.fetchMachineModes(selected_machine_id)
                prod_lines = self.database_operations.fetchProductionLineMachines(machine_id=selected_machine_id)
                if len(modes) > 0:
                    win32api.MessageBox(0, 'لا يمكن حذف الآلة لأنها مرتبطة بنمط.', 'تنبيه')
                elif len(prod_lines) > 0:
                    win32api.MessageBox(0, 'لا يمكن حذف الآلة لأنها مرتبطة بخط إنتاج.', 'تنبيه')
                else:
                    self.database_operations.removeMachine(selected_machine_id)
                    self.fetchMachines()
                    self.ui.machine_estimated_waste_input.clear()
                    self.ui.machine_estimated_waste_currency_combobox.setCurrentIndex(self.ui.machine_estimated_waste_currency_combobox.findData(0))
                    self.ui.estimated_waste_account_combobox.setCurrentIndex(self.ui.estimated_waste_account_combobox.findData(0))



    def addMachineMode(self):
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id:
                mode = self.ui.machine_mode_name_input.text()
                if str(mode).strip():
                    self.database_operations.addMachineMode(selected_machine_id, mode)
                    self.ui.machine_mode_name_input.clear()
                    self.fetchMachineModes()

    def fetchMachineModes(self):
        self.ui.machine_modes_table.setRowCount(0)
        selected_machine = self.ui.machines_table.currentItem()
        if selected_machine is not None:
            selected_machine_id = self.ui.machines_table.item(selected_machine.row(), 0).text()
            if selected_machine_id:
                machine_modes = self.database_operations.fetchMachineModes(selected_machine_id)
                for machine_mode in machine_modes:
                    id = machine_mode[0]
                    machine_id = machine_mode[1]
                    name = machine_mode[2]
                    date = machine_mode[3]

                    # Create a empty row at bottom of table
                    numRows = self.ui.machine_modes_table.rowCount()
                    self.ui.machine_modes_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.machine_modes_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.machine_modes_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
                    self.ui.machine_modes_table.setItem(numRows, 2, QTableWidgetItem(str(date)))

    def removeMachineMode(self):
        messagebox_result = win32api.MessageBox(None, "هل انت متأكد", "تنبيه", MB_YESNO);
        if (messagebox_result == IDYES):
            selected_mode = self.ui.machine_modes_table.currentItem()
            if selected_mode is not None:
                selected_mode_id = self.ui.machine_modes_table.item(selected_mode.row(), 0).text()
                if selected_mode_id:
                    resources = self.database_operations.fetchModeResources(selected_mode_id)
                    if len(resources) > 0:
                        win32api.MessageBox(0, 'لا يمكن حذف النمط لأنه يحتوي على موارد.', 'تنبيه')
                    else:
                        self.database_operations.removeMachineMode(selected_mode_id)
                        self.fetchMachineModes()
        elif (messagebox_result == IDNO):
            pass

    def fetchResources(self):
        self.ui.resources_table.setRowCount(0)
        resources = self.database_operations.fetchResources()
        if len(resources) > 0:
            for resource in resources:
                # Create a empty row at bottom of table
                numRows = self.ui.resources_table.rowCount()
                self.ui.resources_table.insertRow(numRows)

                id = resource['id']
                name = resource['name'] 
                account_id = resource['account_id']
                notes = resource['notes']
                cost = resource['cost']
                unit_id = resource['unit_id']
                unit_name = resource['unit_name']

                self.ui.resources_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                self.ui.resources_table.setItem(numRows, 1, QTableWidgetItem(str(name)))

                # loop through the combobox and check if item already exists in combobox
                if not any(self.ui.mode_resources_combobox.itemText(i) == name 
                          for i in range(self.ui.mode_resources_combobox.count())):
                             self.ui.mode_resources_combobox.addItem(name, [id, unit_id, unit_name])


    def addResource(self):
        resouce_name, ok_pressed = QInputDialog.getText(None, "أضافة مورد جديد", "اسم المورد:")
        if resouce_name.strip() and resouce_name.strip() != '':
            self.database_operations.addResource(resouce_name)
            self.fetchResources()

    def saveResource(self):
        selected_resource = self.ui.resources_table.currentItem()
        if selected_resource is not None:
            selected_resource_id = self.ui.resources_table.item(selected_resource.row(), 0).text()
            if selected_resource_id:
                resource_name = self.ui.resource_name_input.text()
                resource_account = self.ui.resource_account_combobox.currentData() or ''
                resource_notes = self.ui.resource_notes_input.text()

                if str(resource_name).strip():
                    self.database_operations.updateResource(selected_resource_id, resource_name, resource_account, resource_notes)
                self.fetchResources()
                self.setModeResourceUnit()

    def deleteResource(self):
        selected_resource = self.ui.resources_table.currentItem()
        if selected_resource is not None:
            selected_resource_id = self.ui.resources_table.item(selected_resource.row(), 0).text()
            if selected_resource_id:
                messagebox_result = win32api.MessageBox(None, "هل انت متأكد", "تنبيه", MB_YESNO)
                if (messagebox_result == IDYES):
                    self.database_operations.removeResource(selected_resource_id)
                    self.fetchResources()
                    self.ui.resource_name_input.clear()
                    self.ui.resource_account_combobox.setCurrentIndex(self.ui.resource_account_combobox.findData(0))
                    self.ui.resource_notes_input.clear()
                    self.fetchResourceCosts()

                elif (messagebox_result == IDNO):
                    pass

    def addResourceCost(self):
        selected_resource = self.ui.resources_table.currentItem()
        if selected_resource is not None:
            selected_resource_id = self.ui.resources_table.item(selected_resource.row(), 0).text()
            if selected_resource_id:
                resource_cost_per_minute = self.ui.resources_cost_per_minute_input.text() or ''
                resource_cost_currency = self.ui.resource_cost_currency_combobox.currentData() or ''
                resource_cost_unit = self.ui.resource_cost_unit_combobox.currentData() or ''
                resource_notes = self.ui.resource_cost_notes_input.text()
                if resource_cost_per_minute and resource_cost_currency and resource_cost_unit :
                    self.database_operations.addResourceCost(selected_resource_id, resource_cost_per_minute,resource_cost_currency, resource_cost_unit, resource_notes)
                    # Clear the fields after adding
                    self.ui.resources_cost_per_minute_input.clear()
                    self.ui.resource_cost_currency_combobox.setCurrentIndex(self.ui.resource_cost_currency_combobox.findData(0))
                    self.ui.resource_cost_unit_combobox.setCurrentIndex(self.ui.resource_cost_unit_combobox.findData(0))
                    self.ui.resource_cost_notes_input.clear()
                self.fetchResourceCosts()


    def removeResourceCost(self):
        selected_resource_cost = self.ui.resouces_costs_table.currentItem()
        if selected_resource_cost is not None:
            selected_resource_cost_id = self.ui.resouces_costs_table.item(selected_resource_cost.row(), 0).text()
            if selected_resource_cost_id:
                self.database_operations.removeResourceCost(selected_resource_cost_id)
                self.fetchResourceCosts()



    def fetchResourceCosts(self):
        self.ui.resouces_costs_table.setRowCount(0)
        selected_resource = self.ui.resources_table.currentItem()
        if selected_resource is not None:
            selected_resource_id = self.ui.resources_table.item(selected_resource.row(), 0).text()
            if selected_resource_id:
                resrouce_costs = self.database_operations.fetchResouceCosts(selected_resource_id)
                for resrouce_cost in resrouce_costs:
                    id = resrouce_cost['id']
                    resource_id = resrouce_cost['resource_id']
                    value = resrouce_cost['value_col']
                    currency_id = resrouce_cost['currency_id']
                    unit_id = resrouce_cost['unit_id']
                    notes = resrouce_cost['notes']
                    date = resrouce_cost['date_col']
                    currency_name = resrouce_cost['currency_name']
                    unit_name = resrouce_cost['unit_name']

                    # Create a empty row at bottom of table
                    numRows = self.ui.resouces_costs_table.rowCount()
                    self.ui.resouces_costs_table.insertRow(numRows)

                    # Add text to the row
                    self.ui.resouces_costs_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.resouces_costs_table.setItem(numRows, 1, MyTableWidgetItem(str(value), float(value)))
                    self.ui.resouces_costs_table.setItem(numRows, 2, QTableWidgetItem(str(currency_id)))
                    self.ui.resouces_costs_table.setItem(numRows, 3, QTableWidgetItem(str(currency_name)))
                    self.ui.resouces_costs_table.setItem(numRows, 4, QTableWidgetItem(str(unit_id)))
                    self.ui.resouces_costs_table.setItem(numRows, 5, QTableWidgetItem(str(unit_name)))
                    self.ui.resouces_costs_table.setItem(numRows, 6, QTableWidgetItem(str(date)))
                    self.ui.resouces_costs_table.setItem(numRows, 7, QTableWidgetItem(str(notes)))

    def fetchSelectedResource(self):
        selected_resource = self.ui.resources_table.currentItem()
        if selected_resource is not None:
            selected_resource_id = self.ui.resources_table.item(selected_resource.row(), 0).text()
            if selected_resource_id:
                resource_info = self.database_operations.fetchResource(selected_resource_id)
                id = resource_info[0]
                name = resource_info[1]
                account_id = resource_info[2]
                notes = resource_info[3]

                # Populate the UI inputs with the fetched machine information
                self.ui.resource_name_input.setText(name)
                self.ui.resource_notes_input.setText(notes)
                self.ui.resource_account_combobox.setCurrentIndex(
                    self.ui.resource_account_combobox.findData(account_id))


    def addModeResource(self):
        selected_mode = self.ui.machine_modes_table.currentItem()
        if selected_mode is not None:
            selected_mode_id = self.ui.machine_modes_table.item(selected_mode.row(), 0).text()
            if selected_mode_id:
                resource_id = None
                resource_data = self.ui.mode_resources_combobox.currentData()
                if resource_data:
                    resource_id = resource_data[0]
                consumption_per_minute = self.ui.mode_resource_consumption_per_minute_input.text()
                unit = self.ui.mode_resource_consumption_per_minute_unit_combobox.currentData()
                if consumption_per_minute and unit and consumption_per_minute:
                    self.database_operations.addModeResource(selected_mode_id, resource_id, consumption_per_minute,unit)
                    self.ui.mode_resource_consumption_per_minute_input.clear()
                    self.fetchModeResources()
                    

    def removeModeResource(self):
        selected_mode = self.ui.machine_resources_table.currentItem()
        if selected_mode is not None:
            selected_mode_id = self.ui.machine_resources_table.item(selected_mode.row(), 0).text()
            if selected_mode_id:
                self.database_operations.removeModeResource(selected_mode_id)
                self.fetchModeResources()


    def fetchModeResources(self):
        self.ui.machine_resources_table.setRowCount(0)
        selected_mode = self.ui.machine_modes_table.currentItem()
        if selected_mode is not None:
            selected_mode_id = self.ui.machine_modes_table.item(selected_mode.row(), 0).text()
            if selected_mode_id:
                mode_resources = self.database_operations.fetchModeResources(selected_mode_id)
                for mode_resource in mode_resources:
                    id = mode_resource['id']
                    mode_id = mode_resource['mode_id'] 
                    resource_id = mode_resource['resource_id']
                    consumption_per_minute = mode_resource['consumption_per_minute']
                    unit = mode_resource['unit']
                    resource_name = mode_resource['resource_name']
                    unit_name = mode_resource['unit_name']

                    # Create a empty row at bottom of table
                    numRows = self.ui.machine_resources_table.rowCount()
                    self.ui.machine_resources_table.insertRow(numRows)
                    # Add text to the row
                    self.ui.machine_resources_table.setItem(numRows, 0, QTableWidgetItem(str(id)))
                    self.ui.machine_resources_table.setItem(numRows, 1, QTableWidgetItem(str(resource_id)))
                    self.ui.machine_resources_table.setItem(numRows, 2, QTableWidgetItem(str(resource_name)))
                    self.ui.machine_resources_table.setItem(numRows, 3, MyTableWidgetItem(str(consumption_per_minute),float(consumption_per_minute)))
                    self.ui.machine_resources_table.setItem(numRows, 4, QTableWidgetItem(str(unit)))
                    self.ui.machine_resources_table.setItem(numRows, 5, QTableWidgetItem(str(unit_name)))

    def setModeResourceUnit(self):
        self.ui.mode_resource_consumption_per_minute_unit_combobox.clear()
        data = self.ui.mode_resources_combobox.currentData()
        if len(data) > 0:
            resource_id = data[0]
            unit_id = data[1]
            unit_name = data[2]
            if str(unit_name).lower() in ['', 'none']:
                unit_id = None
                unit_name = ''            
            # Fetch resource costs for this resource
            resource_costs = self.database_operations.fetchResouceCosts(resource_id)
            for cost in resource_costs:
                self.ui.mode_resource_consumption_per_minute_unit_combobox.addItem(cost['unit_name'], cost['unit_id'])


    def openInvoicePicker(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            invoice_columns = ['id', 'client_id', 'name', 'date_col']
            invoice_items_columns = ['id', 'material_id', 'name', 'unit_price', 'quantity1', 'unit1_id', 'unit_name']

            # Create picker with column lists
            picker = Ui_DataPicker_Logic(
                self.sql_connector,
                table_name='invoices',
                columns=invoice_columns,
                linked_table='invoice_items',
                linked_columns=invoice_items_columns,
                search_column='name'
            )

            result = picker.showUi()

            if result:
                invoice_item_id = result['linked']['id']    # linked data is related to invoice_item
                if invoice_item_id:
                    invoice_item_data_material_id = result['linked']['material_id']
                    name = result['linked']['name']
                    unit_price = result['linked']['unit_price']
                    quantity1 = result['linked']['quantity1']
                    unit1_id = result['linked']['unit1_id']
                    unit_name = result['linked']['unit_name']
                    currency_id = result['primary']['currency']

                    cost = float(unit_price) * float(quantity1)
                    self.ui.machine_invoice_item_id_input.setText(str(invoice_item_id))
                    self.ui.machine_cost_input.setText(str(cost))
                    self.ui.machine_cost_currency_combobox.setCurrentIndex(
                    self.ui.machine_cost_currency_combobox.findData(currency_id))

        else:
            win32api.MessageBox(0, 'يجب فتح/إنشاء ملف أولاً.', 'title')

    def handler(self, invoice_item_id):
        print("parent=" + str(invoice_item_id))

    def yearsHours(self, target=None):
        # self.ui.machine_standard_age_input.clear()
        # self.ui.standard_hours_age_input.clear()
        if target == 'hours':
            years = self.ui.machine_standard_age_input.text()
            if years and str(years).strip().lower() != '':
                hours = float(years) * 365 * 24
                hours = round(hours, 3)
                self.ui.standard_hours_age_input.setText(str(hours))
        elif target == 'years':
            hours = self.ui.standard_hours_age_input.text()
            if hours and str(hours).strip().lower() != '':
                years = float(hours) / (365 * 24)
                years = round(years, 3)
                self.ui.machine_standard_age_input.setText(str(years))
