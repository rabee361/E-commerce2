from PyQt5.QtWidgets import QVBoxLayout
from PyQt5.QtGui import QPainter, QColor
from DatabaseOperations import DatabaseOperations
from PyQt5.QtChart import QChart, QChartView, QPieSeries, QPieSlice, QBarSeries, QBarSet, QValueAxis, QBarCategoryAxis
from win32 import win32gui
from win32con import MB_OK, MB_ICONWARNING
from win32api import MessageBox
from PyQt5.QtCore import QTranslator, Qt
from LanguageManager import LanguageManager

class Statistics():
    def __init__(self, sql_connector , ui):
        self.sql_connector = sql_connector
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = ui
        self.initialize()

    def initialize(self):
        # self.fetchMaterialsCount()
        self.ui.select_chart_combobox.setEnabled(True)
        self.ui.select_chart_combobox.addItem(self.language_manager.translate("INVOICES"))
        self.ui.select_chart_combobox.addItem(self.language_manager.translate("MATERIALS"))
        self.fetchWarehouses()
        self.ui.select_chart_btn.setEnabled(True)
        self.ui.select_chart_btn.clicked.connect(self.showChart)

        # try:
        self.fetchInvoicesCount()
        # # self.fetchEmployeesCount()
        # self.fetchDepartmentsCount()
        # # self.fetchEmploymentRequestsCount()
        # self.fetchGroupsCount()
        # self.fetchLastManufatureProcess()
        # self.fetchLastMaterialMovement()
        self.showChart()
        # except Exception as e:
        #     print(f"Error refreshing statistics: {str(e)}")
        #     MessageBox(0, self.language_manager.translate(key="STATS_PERMISSION_DENIED"), self.language_manager.translate("ALERT"))

            
       
    # def fetchMaterialsCount(self):
    #     if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
    #         materials_count = self.database_operations.fetchMaterialsCount()
    #         if materials_count:
    #             self.ui.groupped_materials_count.setText(str(materials_count[0]['materials_count']))
    #             self.ui.composite_materials_count.setText(str(materials_count[1]['materials_count']))
    #             self.ui.materials_count.setText(str(materials_count[0]['materials_count'] + materials_count[1]['materials_count']))
    #     else:
    #         pass

    def fetchWarehouses(self):
        warehouses = self.database_operations.fetchWarehouses()
        if warehouses:
            self.ui.select_chart_combobox.addItems([warehouse['name'] for warehouse in warehouses])
        else:
            pass

    def fetchInvoicesCount(self):
        if self.sql_connector != '' and self.sql_connector.is_connected_to_database:
            invoices_count = self.database_operations.fetchInvoicesCount()
            if invoices_count:
                buy_return_invoice_count = str(invoices_count['buy_return']) or 0
                sell_return_invoice_count = str(invoices_count['sell_return']) or 0
                buy_invoice_count = str(invoices_count['buy']) or 0
                sell_invoice_count = str(invoices_count['sell']) or 0
                input_invoice_count = str(invoices_count['input']) or 0
                output_invoice_count = str(invoices_count['output']) or 0
                other_count = int(buy_return_invoice_count) + int(sell_invoice_count) + int(buy_invoice_count) + int(sell_return_invoice_count) + int(input_invoice_count) + int(output_invoice_count)
    
                self.ui.buy_return_invoice_count.setText(buy_return_invoice_count)
                self.ui.sell_return_invoice_count.setText(sell_return_invoice_count)
                self.ui.sell_invoice_count.setText(sell_invoice_count)
                self.ui.buy_invoice_count.setText(buy_invoice_count)
                self.ui.input_invoice_count.setText(input_invoice_count)
                self.ui.output_invoice_count.setText(output_invoice_count)
                # self.ui.other_invoice_count.setText(other_count)

    def fetchDepartmentsCount(self):
        departments_count = self.database_operations.fetchDepartmentsCount()
        if departments_count:
            self.ui.departments_count.setText(str(departments_count['departments_count']))
        else:
            pass

    def fetchGroupsCount(self):
        groups_count = self.database_operations.fetchGroupsCount()
    
    def fetchWarehousesCount(self):
        warehouses_count = self.database_operations.fetchWarehousesCount()
    
    def fetchEmployeesCount(self):
        current_employees_count = self.database_operations.fetchEmployeesCount()
        if current_employees_count:
            self.ui.current_employees_count.setText(str(current_employees_count['current_count']))
            self.ui.former_employees_count.setText(str(current_employees_count['resigned_count']))
            self.ui.employees_count.setText(str(current_employees_count['total_count']))
        else:
            pass

    def fetchEmploymentRequestsCount(self):
        employment_requests_count = self.database_operations.fetchEmploymentRequestsCount()
        if employment_requests_count:
            self.ui.employ_request_count.setText(str(employment_requests_count['pending_employment_requests_count']))
        else:
            pass

    def fetchLastManufatureProcess(self):
        last_manufature_process = self.database_operations.fetchLastManufatureProcess()
        if last_manufature_process: 
            manufacture_cost = last_manufature_process['machines_operation_cost'] + last_manufature_process['salaries_cost'] + last_manufature_process['composition_materials_cost'] + last_manufature_process['expenses_cost']
            self.ui.manufacture_material.setText(str(last_manufature_process['material_name']))
            self.ui.manufacture_date.setText(str(last_manufature_process['date_col']))
            self.ui.manufacture_quantity.setText(str(last_manufature_process['quantity1']))
            self.ui.manufature_cost.setText(str(manufacture_cost))
        else:
            pass

    def fetchLastMaterialMovement(self):
        pass
        # last_material_movement = self.database_operations.fetchLastMaterialMovement()
        # if last_material_movement:
        #     self.ui.last_material_movement_date.setText(str(last_material_movement[0]['date_col'].strftime('%Y-%m-%d')))
        #     self.ui.material.setText(str(last_material_movement[0]['material_name']))
        #     self.ui.move_reason.setText(str(last_material_movement[0]['origin']))
        #     self.ui.from_warehouse.setText(str(last_material_movement[0]['source_warehouse_name'] or ''))
        #     self.ui.to_warehouse.setText(str(last_material_movement[0]['destination_warehouse_name'] or ''))
        #     self.ui.quantity.setText(str(last_material_movement[0]['quantity']))
        # else:
        #     pass

    def showChart(self):
        # Get existing chart view if it exists
        chart_view = self.ui.chart_table.findChild(QChartView)
        chart_type = self.ui.select_chart_combobox.currentText()
        
        if not chart_view:
            # First time setup - create layout and chart view
            chart_table_layout = QVBoxLayout()
            self.ui.chart_table.setLayout(chart_table_layout)
            
            chart = QChart()
            chart.setAnimationOptions(QChart.SeriesAnimations)
            
            chart_view = QChartView(chart)
            chart_view.setRenderHint(QPainter.Antialiasing)
            chart_table_layout.addWidget(chart_view)
        else:
            # Get existing chart to update
            chart = chart_view.chart()
            chart.removeAllSeries()

        if chart_type == self.language_manager.translate("INVOICES"):
            # Create new pie series with updated data
            pie_series = QPieSeries()
            chart.setTitle(self.language_manager.translate("INVOICES_COUNT"))
            
            # Fetch latest invoice data
            invoices_count = self.database_operations.fetchInvoicesCount()

            # Colors for pie slices
            colors = {
                'BUY_RETURN': QColor('#FF9999'),
                'SELL_RETURN': QColor('#66B2FF'), 
                'SELL': QColor('#99FF99'),
                'BUY': QColor('#FFCC99'),
                'INPUT': QColor('#FF99CC'),
                'OUTPUT': QColor('#FFFF99')
            }

            # Update pie slices with new data
            if invoices_count:
                for label, count in {
                    "BUY_RETURN": invoices_count['buy_return'],
                    "SELL_RETURN": invoices_count['sell_return'],
                    "SELL": invoices_count['sell'],
                    "BUY": invoices_count['buy'],
                    "INPUT": invoices_count['input'],
                    "OUTPUT": invoices_count['output']
                }.items():
                    slice = QPieSlice(self.language_manager.translate(label), count)
                    slice.setColor(colors[label])
                    slice.setLabelVisible(True)
                    slice.setLabel(f"{self.language_manager.translate(label)}: {count}")
                    pie_series.append(slice)

                # Add updated series to chart
                chart.addSeries(pie_series)
        
        else:
            # Handle warehouse fullness chart
            try:
                # Get selected warehouse
                selected_warehouse = self.ui.select_chart_combobox.currentText()
                warehouses = self.database_operations.fetchWarehouses()
                warehouse_id = None
                
                # Find the selected warehouse ID
                for warehouse in warehouses:
                    if warehouse['name'] == selected_warehouse:
                        warehouse_id = warehouse['id']
                        break
                
                if warehouse_id:
                    # Get materials in this warehouse
                    warehouse = self.database_operations.fetchWarehouse(warehouse_id)
                    materials = self.database_operations.fetchWarehouseMaterials(warehouse_id)
                    
                    if materials:
                        # Calculate total capacity and used space
                        total_capacity = warehouse['capacity']
                        used_space = 0
                        
                        for material in materials:
                            if material['quantity'] and str(material['quantity']).replace('.','').isdigit():
                                used_space += float(material['quantity'])

                        
                        # Create pie series for warehouse fullness
                        pie_series = QPieSeries()
                        chart.setTitle(f"{self.language_manager.translate('WAREHOUSE_FULLNESS')} - {selected_warehouse}")
                        
                        # Add used and free space slices
                        if total_capacity > 0:
                            used_percentage = (used_space / total_capacity) * 100
                            free_percentage = 100 - used_percentage
                            
                            used_slice = QPieSlice(f"{self.language_manager.translate('USED_SPACE')}: {used_percentage:.1f}%", used_percentage)
                            used_slice.setColor(QColor('#FF9999'))
                            used_slice.setLabelVisible(True)
                            
                            free_slice = QPieSlice(f"{self.language_manager.translate('FREE_SPACE')}: {free_percentage:.1f}%", free_percentage)
                            free_slice.setColor(QColor('#99FF99'))
                            free_slice.setLabelVisible(True)
                            
                            pie_series.append(used_slice)
                            pie_series.append(free_slice)
                            
                            chart.addSeries(pie_series)
                        else:
                            chart.setTitle(self.language_manager.translate("NO_CAPACITY_DATA"))
                    else:
                        chart.setTitle(self.language_manager.translate("NO_MATERIALS_FOUND"))
                else:
                    chart.setTitle(self.language_manager.translate("WAREHOUSE_NOT_FOUND"))
                    
            except Exception as e:
                print(f"Error creating warehouse chart: {str(e)}")
                chart.setTitle(self.language_manager.translate("ERROR_LOADING_CHART"))

    def refresh(self):
        # Clear any existing chart first
        chart_view = self.ui.chart_table.findChild(QChartView)
        if chart_view:
            chart = chart_view.chart()
            chart.removeAllSeries()

        # try:
        # self.fetchInvoicesCount()
        # # self.fetchEmployeesCount()
        # self.fetchDepartmentsCount()
        # # self.fetchEmploymentRequestsCount()
        # self.fetchGroupsCount()
        # self.fetchLastManufatureProcess()
        # self.fetchLastMaterialMovement()
        self.showChart()
        # except Exception as e:
        #     print(f"Error refreshing statistics: {str(e)}")
        #     MessageBox(0, self.language_manager.translate(key="STATS_PERMISSION_DENIED"), self.language_manager.translate("ALERT"))

            
        
