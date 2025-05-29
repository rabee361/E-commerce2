import Colors
from DatabaseOperations import DatabaseOperations
from PyQt5.QtCore import Qt, QDate , QDateTime
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QSizePolicy, QTableWidgetItem

from Ui_Ledger import Ui_Ledger
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from Ui_Machine_Maintenance import Ui_Machine_Maintenance
from PyQt5 import QtGui
from Ui_Add_Maintenance_Operation_Logic import Ui_Add_Maintenance_Operation_Logic

class Ui_Machine_Maintenance_Logic(QDialog):
    def __init__(self, sql_connector , machine_id=None):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Machine_Maintenance()
        self.machine_id = machine_id

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        # Set up integer validator for quantity input
        self.ui.quantity_input.setValidator(QtGui.QDoubleValidator())
        self.ui.account_combobox.setEnabled(False)
        self.ui.opposite_account_combobox.setEnabled(False)
        self.ui.add_machine_maintenance.clicked.connect(lambda: self.openAddMachineMaintenanceWindow(self))
        self.ui.select_account_btn.clicked.connect(lambda: self.openSelectAccountWindow())
        self.ui.select_opposite_account_btn.clicked.connect(lambda: self.openSelectOppositeAccountWindow())
        self.ui.delete_maintenance_operation_btn.clicked.connect(lambda: self.removeMaintenanceOperation(self))
        self.ui.maintenance_record_table.cellClicked.connect(self.fetchMachineMaintenanceOperation)
        self.ui.save_maintenance_info_btn.clicked.connect(lambda: self.saveMaintenanceInfo())

        self.ui.add_employee_btn.clicked.connect(lambda: self.addMaintenanceWorker(self))
        self.ui.delete_employee_btn.clicked.connect(lambda: self.removeMaintenanceWorker(self))
        #update workers

        self.ui.add_material_btn.clicked.connect(lambda: self.addMaintenanceOperationMaterial(self))
        self.ui.delete_material_btn.clicked.connect(lambda: self.removeMaintenanceOperationMaterial(self))
        #update materials

        self.fetchAccounts()

        self.fetchEmployees()
        self.fetchUnits()
        self.fetchMaintenanceMaterials()
        self.fetchMachineMaintenanceOperations()

        self.ui.maintenance_type_combobox.addItem("صيانة دورية", "صيانة دورية")
        self.ui.maintenance_type_combobox.addItem("صيانة طارئة", "صيانة طارئة")




    def openAddMachineMaintenanceWindow(self , window):
        Ui_Add_Maintenance_Operation_Logic(self.sql_connector , self.machine_id).showUi()
        self.fetchMachineMaintenanceOperations()

    def fetchMaintenanceMaterials(self):
        materials = self.database_operations.fetchMaintenanceMaterials()
        for material in materials:
            self.ui.materials_combobox.addItem(str(material['name']), material['id'])

    def fetchUnits(self):
        units = self.database_operations.fetchUnits()
        for unit in units:
            self.ui.unit_combobox.addItem(str(unit['name']), unit['id'])

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            self.ui.account_combobox.addItem(str(account['name']), account['id'])
            self.ui.opposite_account_combobox.addItem(str(account['name']), account['id'])

    def fetchEmployees(self):
        employees = self.database_operations.fetchAllEmployees()
        for employee in employees:
            self.ui.employees_combobox.addItem(str(employee['name']), employee['id'])

    def openSelectAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(result['id']))

    def openSelectOppositeAccountWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts')
        result = data_picker.showUi()
        if result is not None:
            self.ui.opposite_account_combobox.setCurrentIndex(self.ui.opposite_account_combobox.findData(result['id']))



    def fetchMachineMaintenanceOperations(self):
        # Clear existing rows first
        self.ui.maintenance_record_table.setRowCount(0)
        maintenance = self.database_operations.fetchMachineMaintenanceOperations(machine_id=self.machine_id)
        for record in maintenance:
            numRows = self.ui.maintenance_record_table.rowCount()
            self.ui.maintenance_record_table.insertRow(numRows)
            self.ui.maintenance_record_table.setItem(numRows, 0, QTableWidgetItem(str(record['id'])))
            self.ui.maintenance_record_table.setItem(numRows, 1, QTableWidgetItem(str(record['machine_name'])))
            self.ui.maintenance_record_table.setItem(numRows, 2, QTableWidgetItem(str(record['name'])))
            self.ui.maintenance_record_table.setItem(numRows, 3, QTableWidgetItem(str(record['maintenance_type'])))



    def addMaintenanceOperation(self):
        name = self.ui.maintenance_operation_name_input.text()
        if name:
            self.database_operations.addMachineMaintenance(machine_id=self.machine_id, name=name)
            self.ui.maintenance_record_table.setRowCount(0)
            self.fetchMachineMaintenanceOperations()
            self.ui.maintenance_operation_name_input.clear()


    def saveMaintenanceInfo(self):
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            name = self.ui.maintenance_operation_name_input.text()
            account = self.ui.account_combobox.currentData()
            opposite_account = self.ui.opposite_account_combobox.currentData()
            maintenance_type = self.ui.maintenance_type_combobox.currentText()
            start_date = self.ui.maintenance_start_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            end_date = self.ui.maintenance_end_date_input.dateTime().toString("yyyy-MM-dd HH:mm:ss")
            statment_col = self.ui.report_input.toPlainText()
            cost = self.ui.cost_input.text()
            self.database_operations.updateMachineMaintenance(maintenance_id=maintenance_id, name=name, account=account, opposite_account=opposite_account, maintenance_type=maintenance_type, start_date=start_date, end_date=end_date, statment_col=statment_col, cost=cost)
            self.fetchMachineMaintenanceOperation()


    def removeMaintenanceOperation(self):
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            self.database_operations.removeMachineMaintenance(maintenance_id=maintenance_id)
            self.fetchMachineMaintenanceOperations()


    def fetchMachineMaintenanceOperation(self):
        selected_maintenance = self.ui.maintenance_record_table.currentItem()
        if selected_maintenance is not None:
            maintenance_id = self.ui.maintenance_record_table.item(selected_maintenance.row(), 0).text()
            maintenance_info = self.database_operations.fetchMaintenanceOperation(maintenance_id=maintenance_id)
            if maintenance_info is not None:
                self.ui.maintenance_operation_name_input.setText(maintenance_info['name'])
                
                # Handle case where dates could be None or empty
                start_date = maintenance_info['start_date']
                end_date = maintenance_info['end_date']
                account = maintenance_info['account']
                opposite_account = maintenance_info['opposite_account']
                maintenance_type = maintenance_info['maintenance_type']
                
                if start_date:
                    start_date = start_date.strftime("%Y-%m-%d %H:%M:%S")
                    self.ui.maintenance_start_date_input.setDateTime(QDateTime.fromString(start_date, "yyyy-MM-dd HH:mm:ss"))
                
                if end_date:
                    end_date = end_date.strftime("%Y-%m-%d %H:%M:%S") 
                    self.ui.maintenance_end_date_input.setDateTime(QDateTime.fromString(end_date, "yyyy-MM-dd HH:mm:ss"))

                self.ui.maintenance_type_combobox.setCurrentIndex(self.ui.maintenance_type_combobox.findData(maintenance_type))

                self.ui.account_combobox.setCurrentIndex(self.ui.account_combobox.findData(account))
                self.ui.opposite_account_combobox.setCurrentIndex(self.ui.opposite_account_combobox.findData(opposite_account))

                self.ui.report_input.setText(maintenance_info['statment_col'])
                self.ui.cost_input.setText(str(maintenance_info['cost']))

            self.fetchMaintenanceWorkers()
            self.fetchMaintenanceOperationMaterials()



    def fetchMaintenanceWorkers(self):
        self.ui.employees_table.setRowCount(0)
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            workers = self.database_operations.fetchMaintenanceWorkers(maintenance_id=maintenance_id)
            for worker in workers:
                numRows = self.ui.employees_table.rowCount()
                self.ui.employees_table.insertRow(numRows)
                self.ui.employees_table.setItem(numRows, 0, QTableWidgetItem(str(worker['id'])))
                self.ui.employees_table.setItem(numRows, 1, QTableWidgetItem(str(worker['name'])))


    def removeMaintenanceWorker(self):
        worker_id = self.ui.employees_table.currentItem()
        if worker_id is not None:
            worker_id = self.ui.employees_table.item(worker_id.row(), 0).text()
            self.database_operations.removeMaintenanceWorker(worker_id=worker_id)
            self.fetchMaintenanceWorkers()


    def addMaintenanceWorker(self):
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            employee_id = self.ui.employees_combobox.currentData()
            self.database_operations.addMaintenanceWorker(maintenance_id=maintenance_id, employee_id=employee_id)
            self.fetchMaintenanceWorkers()






    def fetchMaintenanceOperationMaterials(self):
        self.ui.maintenance_materials_table.setRowCount(0)
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            materials = self.database_operations.fetchMaintenanceOperationMaterials(maintenance_id=maintenance_id)
            for material in materials:
                numRows = self.ui.maintenance_materials_table.rowCount()
                self.ui.maintenance_materials_table.insertRow(numRows)
                self.ui.maintenance_materials_table.setItem(numRows, 0, QTableWidgetItem(str(material['id'])))
                self.ui.maintenance_materials_table.setItem(numRows, 1, QTableWidgetItem(str(material['name'])))
                self.ui.maintenance_materials_table.setItem(numRows, 2, QTableWidgetItem(str(material['quantity'])))
                self.ui.maintenance_materials_table.setItem(numRows, 3, QTableWidgetItem(str(material['unit_name'])))

    def addMaintenanceOperationMaterial(self):   
        maintenance_id = self.ui.maintenance_record_table.currentItem()
        if maintenance_id is not None:
            maintenance_id = self.ui.maintenance_record_table.item(maintenance_id.row(), 0).text()
            quantity = self.ui.quantity_input.text()
            unit = self.ui.unit_combobox.currentData()
            material = self.ui.materials_combobox.currentText().split(' - ')[0]
            self.database_operations.addMaintenanceOperationMaterial(maintenance_id=maintenance_id, material_id=material, quantity=quantity, unit=unit)
            self.fetchMaintenanceOperationMaterials()

    def removeMaintenanceOperationMaterial(self):
        material_id = self.ui.maintenance_materials_table.currentItem()
        if material_id is not None:
            material_id = self.ui.maintenance_materials_table.item(material_id.row(), 0).text()
            self.database_operations.removeMaintenanceMaterial(material_id=material_id)
            self.fetchMaintenanceOperationMaterials()


