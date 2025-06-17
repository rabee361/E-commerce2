import win32api
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog
from DatabaseOperations import DatabaseOperations
from Ui_AddMaterial import Ui_AddMaterial
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtCore import QTranslator
from LanguageManager import LanguageManager

class Ui_AddMaterial_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_AddMaterial()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowTitle("add material")
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.current_quantity_input.setValidator(QDoubleValidator())
        self.ui.max_quantity_input.setValidator(QDoubleValidator())
        self.ui.min_quantity_input.setValidator(QDoubleValidator())
        self.ui.request_limit_input.setValidator(QDoubleValidator())
        self.ui.gift_input.setValidator(QDoubleValidator())
        self.ui.gift_for_input.setValidator(QDoubleValidator())
        self.ui.price1_1_input.setValidator(QDoubleValidator())
        self.ui.price2_1_input.setValidator(QDoubleValidator())
        self.ui.price3_1_input.setValidator(QDoubleValidator())
        self.ui.price4_1_input.setValidator(QDoubleValidator())
        self.ui.price5_1_input.setValidator(QDoubleValidator())
        self.ui.price6_1_input.setValidator(QDoubleValidator())
        self.ui.price1_2_input.setValidator(QDoubleValidator())
        self.ui.price2_2_input.setValidator(QDoubleValidator())
        self.ui.price3_2_input.setValidator(QDoubleValidator())
        self.ui.price4_2_input.setValidator(QDoubleValidator())
        self.ui.price5_2_input.setValidator(QDoubleValidator())
        self.ui.price6_2_input.setValidator(QDoubleValidator())
        self.ui.price1_3_input.setValidator(QDoubleValidator())
        self.ui.price2_3_input.setValidator(QDoubleValidator())
        self.ui.price3_3_input.setValidator(QDoubleValidator())
        self.ui.price4_3_input.setValidator(QDoubleValidator())
        self.ui.price5_3_input.setValidator(QDoubleValidator())
        self.ui.price6_3_input.setValidator(QDoubleValidator())

        self.fetchAccounts()
        self.fetchCurrencies()
        self.fetchGroups()
        self.fetchPricesNames()
        self.fetchUnits()
        self.fetchMachines()
        self.fetchMachineModes()
        self.fetchManufactureHall()

        material_types={"stock":self.language_manager.translate("STOCK"), "service":self.language_manager.translate("SERVICE"), "assets":self.language_manager.translate("ASSETS")}
        for key,value in material_types.items():
            self.ui.type_combobox.addItem(value, key)
        
        # self.ui.unit1_combobox.setEnabled(False)
        self.ui.unit2_combobox.setEnabled(False)
        self.ui.unit3_combobox.setEnabled(False)
        self.ui.group_combobox.setEnabled(False)

        self.ui.groupped_material_checkbox.clicked.connect(lambda: self.enableGrouppedMaterialCompositionButton())
        self.ui.groupped_material_btn.clicked.connect(lambda: self.openGrouppedMaterialCompositionWindow())
        self.ui.add_machine_btn.clicked.connect(lambda: self.openMachineWindow())

        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.fetchUnitsConversionValue())

        self.ui.save_btn.clicked.connect(lambda: self.save(window)) #pass (window) parameter to close it if everything went well.

        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.enableUnit2andUnit3())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.enableUnit2Prices())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.enableUnit3Prices())

        self.ui.standard_unit1_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.standard_unit2_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.standard_unit3_quantity_input.textEdited.connect(lambda: self.updateQuantities())
        self.ui.unit1_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())
        self.ui.unit2_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())
        self.ui.unit3_combobox.currentIndexChanged.connect(lambda: self.updateQuantities())

        self.ui.select_group_btn.clicked.connect(lambda: self.openSelectGroupWindow())
        self.ui.select_material_addition_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.material_addition_account_combobox))
        self.ui.select_material_discount_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.material_discount_account_combobox))

    def openSelectAccountWindow(self, combobox):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))


    def fetchGroups(self):
        self.ui.group_combobox.clear()
        groups = self.database_operations.fetchGroups()

        # Add the groups to the groups combobox
        for group in groups:
            id = group[0]
            display_text = group[1]
            data = id
            self.ui.group_combobox.addItem(display_text, data)

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

    def openSelectGroupWindow(self):
        data_picker = Ui_DataPicker_Logic(self.sql_connector, 'groups')
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
        unit1=self.ui.unit1_combobox.currentData()
        unit2=self.ui.unit2_combobox.currentData()
        unit3=self.ui.unit3_combobox.currentData()
        if unit2:
            conversion_value = self.database_operations.fetchUnitConversionValueBetween(unit2, unit1)
            if conversion_value:
                self.ui.unit2_to_unit1_convert.setText(str(conversion_value))
            else:
                self.ui.unit2_to_unit1_convert.setText(str(""))
        else:
            self.ui.unit2_to_unit1_convert.setText(str(""))
        if unit3:
            conversion_value = self.database_operations.fetchUnitConversionValueBetween(unit3, unit1)
            if conversion_value:
                self.ui.unit3_to_unit1_convert.setText(str(conversion_value))
            else:
                self.ui.unit3_to_unit1_convert.setText(str(""))
        else:
            self.ui.unit3_to_unit1_convert.setText(str(""))

    def save(self, window):
        code = self.ui.code_input.text()
        name = self.ui.name_input.text()
        specs = self.ui.specs_input.text()
        size = self.ui.size_input.text()
        manufacturer = self.ui.manufacturer_input.text()
        color = self.ui.color_input.text()
        origin = self.ui.origin_input.text()
        quality = self.ui.quality_input.text()
        model = self.ui.model_input.text()
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
        expiray = self.ui.expiray_input.text()
        group = self.ui.group_combobox.itemData(self.ui.group_combobox.currentIndex())
        price1_1_unit = self.ui.price1_1_currency_combobox.itemData(self.ui.price1_1_currency_combobox.currentIndex())
        price2_1_unit = self.ui.price2_1_currency_combobox.itemData(self.ui.price2_1_currency_combobox.currentIndex())
        price3_1_unit = self.ui.price3_1_currency_combobox.itemData(self.ui.price3_1_currency_combobox.currentIndex())
        price4_1_unit = self.ui.price4_1_currency_combobox.itemData(self.ui.price4_1_currency_combobox.currentIndex())
        price5_1_unit = self.ui.price5_1_currency_combobox.itemData(self.ui.price5_1_currency_combobox.currentIndex())
        price6_1_unit = self.ui.price6_1_currency_combobox.itemData(self.ui.price6_1_currency_combobox.currentIndex())
        price1_2_unit = self.ui.price1_2_currency_combobox.itemData(self.ui.price1_2_currency_combobox.currentIndex())
        price2_2_unit = self.ui.price2_2_currency_combobox.itemData(self.ui.price2_2_currency_combobox.currentIndex())
        price3_2_unit = self.ui.price3_2_currency_combobox.itemData(self.ui.price3_2_currency_combobox.currentIndex())
        price4_2_unit = self.ui.price4_2_currency_combobox.itemData(self.ui.price4_2_currency_combobox.currentIndex())
        price5_2_unit = self.ui.price5_2_currency_combobox.itemData(self.ui.price5_2_currency_combobox.currentIndex())
        price6_2_unit = self.ui.price6_2_currency_combobox.itemData(self.ui.price6_2_currency_combobox.currentIndex())
        price1_3_unit = self.ui.price1_3_currency_combobox.itemData(self.ui.price1_3_currency_combobox.currentIndex())
        price2_3_unit = self.ui.price2_3_currency_combobox.itemData(self.ui.price2_3_currency_combobox.currentIndex())
        price3_3_unit = self.ui.price3_3_currency_combobox.itemData(self.ui.price3_3_currency_combobox.currentIndex())
        price4_3_unit = self.ui.price4_3_currency_combobox.itemData(self.ui.price4_3_currency_combobox.currentIndex())
        price5_3_unit = self.ui.price5_3_currency_combobox.itemData(self.ui.price5_3_currency_combobox.currentIndex())
        price6_3_unit = self.ui.price6_3_currency_combobox.itemData(self.ui.price6_3_currency_combobox.currentIndex())
        material_type = self.ui.type_combobox.currentData() #Todo replace all combobox.itemData(combobox.currentIndex()) with combobox.currentData()
        groupped = 1 if self.ui.groupped_material_checkbox.isChecked() else 0

        standard_unit1_quantity = self.ui.standard_unit1_quantity_input.text()
        standard_unit2_quantity = self.ui.standard_unit2_quantity_input.text()
        standard_unit3_quantity = self.ui.standard_unit3_quantity_input.text()
        standard_work_hours = self.ui.standard_work_hours_input.text()
        yearly_required = self.ui.yearly_required_input.text()
        manufacture_hall = self.ui.manufacture_hall_combobox.currentData()

        material_addition_account = self.ui.material_addition_account_combobox.currentData()
        material_discount_account = self.ui.material_discount_account_combobox.currentData()

        if str(code).lower() == 'none':
            code = ''
        if str(name).lower() == 'none':
            name = ''
        if str(specs).lower() == 'none':
            specs = ''
        if str(size).lower() == 'none':
            size = ''
        if str(manufacturer).lower() == 'none':
            manufacturer = ''
        if str(color).lower() == 'none':
            color = ''
        if str(origin).lower() == 'none':
            origin = ''
        if str(quality).lower() == 'none':
            quality = ''
        if str(model).lower() == 'none':
            model = ''
        if str(unit1).lower() == 'none':
            unit1 = ''
        if str(unit2).lower() == 'none':
            unit2 = ''
        if str(unit3).lower() == 'none':
            unit3 = ''
        if str(current_quantity).lower() == 'none':
            current_quantity = ''
        if str(max_quantity).lower() == 'none':
            max_quantity = ''
        if str(min_quantity).lower() == 'none':
            min_quantity = ''
        if str(request_limit).lower() == 'none':
            request_limit = ''
        if str(gift).lower() == 'none':
            gift = ''
        if str(gift_for).lower() == 'none':
            gift_for = ''
        if str(price1_desc).lower() == 'none':
            price1_desc = ''
        if str(price1_1).lower() == 'none':
            price1_1 = ''
        if str(price1_2).lower() == 'none':
            price1_2 = ''
        if str(price1_3).lower() == 'none':
            price1_3 = ''
        if str(price2_desc).lower() == 'none':
            price2_desc = ''
        if str(price2_1).lower() == 'none':
            price2_1 = ''
        if str(price2_2).lower() == 'none':
            price2_2 = ''
        if str(price2_3).lower() == 'none':
            price2_3 = ''
        if str(price3_desc).lower() == 'none':
            price3_desc = ''
        if str(price3_1).lower() == 'none':
            price3_1 = ''
        if str(price3_2).lower() == 'none':
            price3_2 = ''
        if str(price3_3).lower() == 'none':
            price3_3 = ''
        if str(price4_desc).lower() == 'none':
            price4_desc = ''
        if str(price4_1).lower() == 'none':
            price4_1 = ''
        if str(price4_2).lower() == 'none':
            price4_2 = ''
        if str(price4_3).lower() == 'none':
            price4_3 = ''
        if str(price5_desc).lower() == 'none':
            price5_desc = ''
        if str(price5_1).lower() == 'none':
            price5_1 = ''
        if str(price5_2).lower() == 'none':
            price5_2 = ''
        if str(price5_3).lower() == 'none':
            price5_3 = ''
        if str(price6_desc).lower() == 'none':
            price6_desc = ''
        if str(price6_1).lower() == 'none':
            price6_1 = ''
        if str(price6_2).lower() == 'none':
            price6_2 = ''
        if str(price6_3).lower() == 'none':
            price6_3 = ''
        if str(expiray).lower() == 'none':
            expiray = ''
        if str(group).lower() == 'none':
            group = ''
        if str(price1_1_unit).lower() == 'none':
            price1_1_unit = ''
        if str(price2_1_unit).lower() == 'none':
            price2_1_unit = ''
        if str(price3_1_unit).lower() == 'none':
            price3_1_unit = ''
        if str(price4_1_unit).lower() == 'none':
            price4_1_unit = ''
        if str(price5_1_unit).lower() == 'none':
            price5_1_unit = ''
        if str(price6_1_unit).lower() == 'none':
            price6_1_unit = ''
        if str(price1_2_unit).lower() == 'none':
            price1_2_unit = ''
        if str(price2_2_unit).lower() == 'none':
            price2_2_unit = ''
        if str(price3_2_unit).lower() == 'none':
            price3_2_unit = ''
        if str(price4_2_unit).lower() == 'none':
            price4_2_unit = ''
        if str(price5_2_unit).lower() == 'none':
            price5_2_unit = ''
        if str(price6_2_unit).lower() == 'none':
            price6_2_unit = ''
        if str(price1_3_unit).lower() == 'none':
            price1_3_unit = ''
        if str(price2_3_unit).lower() == 'none':
            price2_3_unit = ''
        if str(price3_3_unit).lower() == 'none':
            price3_3_unit = ''
        if str(price4_3_unit).lower() == 'none':
            price4_3_unit = ''
        if str(price5_3_unit).lower() == 'none':
            price5_3_unit = ''
        if str(price6_3_unit).lower() == 'none':
            price6_3_unit = ''
        if str(standard_unit1_quantity).lower() == 'none':
                standard_unit1_quantity = ''
        if str(standard_unit2_quantity).lower() == 'none':
                standard_unit2_quantity = ''
        if str(standard_unit3_quantity).lower() == 'none':
                standard_unit3_quantity = ''
        if str(standard_work_hours).lower() == 'none':
                standard_work_hours = ''
        if str(yearly_required).lower() == 'none':
                yearly_required = ''

        default_unit = 0
        if self.ui.unit1_default_radiobox.isChecked() and unit1 != '':
            default_unit = 1
        if self.ui.unit2_default_radiobox.isChecked() and unit2 != '':
            default_unit = 2
        if self.ui.unit3_default_radiobox.isChecked() and unit3 != '':
            default_unit = 3

        if str(manufacture_hall).lower() == 'none':
            manufacture_hall = ''

        if str(material_addition_account).lower() == 'none':
            material_addition_account = ''
        if str(material_discount_account).lower() == 'none':
            material_discount_account = ''

        if(name.replace(" ","")): # if name is not empty and not only spaces
            if unit1 == '':
                win32api.MessageBox(0, self.language_manager.translate("FIRST_UNIT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
            elif (unit2 != '' and self.ui.unit2_to_unit1_convert.text() == '') or (unit3 != '' and self.ui.unit3_to_unit1_convert.text() == ''):
                win32api.MessageBox(0, self.language_manager.translate("CONVERSION_FACTOR_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))
            elif default_unit == 0:
                win32api.MessageBox(0, self.language_manager.translate("DEFAULT_UNIT_MUST_BE_SELECTED"), self.language_manager.translate("ERROR"))
            else:
                self.database_operations.addMaterial(code, name, specs, size, manufacturer, color, origin, quality, model,
                                             unit1, unit2, unit3, default_unit, current_quantity,
                                             max_quantity, min_quantity, request_limit, gift, gift_for, price1_desc,
                                             price1_1, price1_2, price1_3, price2_desc, price2_1, price2_2, price2_3,
                                             price3_desc, price3_1, price3_2, price3_3, price4_desc, price4_1, price4_2,
                                             price4_3, price5_desc, price5_1, price5_2, price5_3, price6_desc, price6_1,
                                             price6_2, price6_3, expiray, group, price1_1_unit, price2_1_unit,
                                             price3_1_unit, price4_1_unit, price5_1_unit, price6_1_unit, price1_2_unit,
                                             price2_2_unit, price3_2_unit, price4_2_unit, price5_2_unit, price6_2_unit,
                                             price1_3_unit, price2_3_unit, price3_3_unit, price4_3_unit, price5_3_unit,
                                             price6_3_unit, material_type, groupped, standard_unit1_quantity, standard_unit2_quantity,
                                                        standard_unit3_quantity, standard_work_hours,
                                                        yearly_required, manufacture_hall, material_addition_account, material_discount_account)
                window.accept()
        else:
            win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))
    
    def openGrouppedMaterialCompositionWindow(self):
        win32api.MessageBox(0,self.language_manager.translate("GROUPPED_MATERIAL_CAN_BE_ADDED_AFTER_SAVING_THE_MATERIAL"), self.language_manager.translate("ALERT"))

    def openMachineWindow(self):
        win32api.MessageBox(0,self.language_manager.translate("MACHINES_CAN_BE_ADDED_AFTER_SAVING_THE_MATERIAL"), self.language_manager.translate("ALERT"))

    def enableGrouppedMaterialCompositionButton(self):
        self.ui.groupped_material_btn.setEnabled(True) if self.ui.groupped_material_checkbox.isChecked() else self.ui.groupped_material_btn.setDisabled(True)

    def enableUnit2andUnit3(self):
        unit1 = self.ui.unit1_combobox.currentData()
        if unit1 is not None:
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
        caller = self.sender().objectName()  # the object that fired this function

        if str(caller).lower() == 'standard_unit1_quantity_input' or str(caller).lower() == 'unit1_combobox':
            unit1 = self.ui.unit1_combobox.currentData()
            quantity1 = self.ui.standard_unit1_quantity_input.text()

            if unit1:
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
                    self.ui.standard_unit2_quantity_input.setText(str(quantity2))

            if self.ui.unit3_to_unit1_convert.text() != '':
                unit1_to_unit3_rate = 1 / float(self.ui.unit3_to_unit1_convert.text())
                if quantity1:
                    quantity3 = float(quantity1) * unit1_to_unit3_rate
                    self.ui.standard_unit3_quantity_input.setText(str(quantity3))

        elif str(caller).lower() == 'standard_unit2_quantity_input' or str(caller).lower() == 'unit2_combobox':
            unit2 = self.ui.unit2_combobox.currentData()
            quantity2 = self.ui.standard_unit2_quantity_input.text()

            if unit2:
                self.ui.standard_unit2_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit2))
                self.ui.standard_unit2_quantity_input.setEnabled(True)
            else:
                self.ui.standard_unit2_combobox.setCurrentIndex(0)
                self.ui.standard_unit2_quantity_input.clear()
                self.ui.standard_unit2_quantity_input.setDisabled(True)

            unit2_to_unit1_rate = float(self.ui.unit2_to_unit1_convert.text()) if self.ui.unit2_to_unit1_convert.text() else 0
            if quantity2 and unit2_to_unit1_rate:
                quantity1 = float(quantity2) * unit2_to_unit1_rate
                self.ui.standard_unit1_quantity_input.setText(str(quantity1))

            unit3_to_unit1_rate = float(self.ui.unit3_to_unit1_convert.text()) if self.ui.unit3_to_unit1_convert.text() else 0
            if unit3_to_unit1_rate and unit2_to_unit1_rate != '':
                unit2_to_unit3_rate = unit2_to_unit1_rate / unit3_to_unit1_rate
                if quantity2:
                    quantity3 = float(quantity2) * unit2_to_unit3_rate
                    self.ui.standard_unit3_quantity_input.setText(str(quantity3))

        elif str(caller).lower() == 'standard_unit3_quantity_input' or str(caller).lower() == 'unit3_combobox':
            unit3 = self.ui.unit3_combobox.currentData()
            quantity3 = self.ui.standard_unit3_quantity_input.text()

            if unit3:
                self.ui.standard_unit3_combobox.setCurrentIndex(self.ui.standard_unit1_combobox.findData(unit3))
                self.ui.standard_unit3_quantity_input.setEnabled(True)
            else:
                self.ui.standard_unit3_combobox.setCurrentIndex(0)
                self.ui.standard_unit3_quantity_input.clear()
                self.ui.standard_unit3_quantity_input.setDisabled(True)

            unit3_to_unit1_rate = float(self.ui.unit3_to_unit1_convert.text()) if self.ui.unit3_to_unit1_convert.text() else 0
            if quantity3 and unit3_to_unit1_rate:
                quantity1 = float(quantity3) * unit3_to_unit1_rate
                self.ui.standard_unit1_quantity_input.setText(str(quantity1))

            unit2_to_unit1_rate = float(self.ui.unit2_to_unit1_convert.text()) if self.ui.unit2_to_unit1_convert.text() else 0
            if unit2_to_unit1_rate and unit3_to_unit1_rate:
                unit3_to_unit2_rate = unit3_to_unit1_rate / unit2_to_unit1_rate
                if quantity3:
                    quantity2 = float(quantity3) * unit3_to_unit2_rate
                    self.ui.standard_unit2_quantity_input.setText(str(quantity2))

    def fetchMachines(self):
        machines = self.database_operations.fetchMachines()
        for machine in machines:
            id = machine[0]
            name = machine[1]
            # years_age = machine[2]
            # estimated_waste_value = machine[3]
            # estimated_waste_currency = machine[4]
            # estimated_waste_account = machine[5]
            # invoice_item_id = machine[6]
            # notes = machine[7]
            self.ui.machines_combobox.addItem(name, id)

    def fetchMachineModes(self):
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
        win32api.MessageBox(0, self.language_manager.translate("MACHINES_CAN_BE_ADDED_AFTER_SAVING_THE_MATERIAL"), self.language_manager.translate("ALERT"))
        # material_id =
        # machine_id = self.ui.machines_combobox.currentData()
        # machine_mode = self.ui.machine_modes_combobox.currentData()
        # use_duration= self.ui.machine_use_duration_input.text()
        #
        # if machine_id and machine_mode and str(use_duration).strip():
        #     self.database_operations.addMaterialMachine(machine_id, machine_mode, use_duration)

    def fetchAccounts(self):
        self.ui.material_addition_account_combobox.clear()
        self.ui.material_discount_account_combobox.clear()
        self.ui.material_addition_account_combobox.addItem(self.language_manager.translate("NONE"), None)
        self.ui.material_discount_account_combobox.addItem(self.language_manager.translate("NONE"), None)

        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account[0]
            name = account[1]
            self.ui.material_addition_account_combobox.addItem(name, id)
            self.ui.material_discount_account_combobox.addItem(name, id)

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