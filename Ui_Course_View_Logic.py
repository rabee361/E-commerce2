from PyQt5.QtCore import Qt
from PyQt5.QtCore import QDate
from Ui_Course_View import Ui_Course_View
from PyQt5.QtWidgets import QDialog, QMessageBox
from DatabaseOperations import DatabaseOperations
from Ui_DataPicker_Logic import Ui_DataPicker_Logic
from PyQt5.QtWidgets import QComboBox, QPushButton
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Course_View_Logic(QDialog):
    def __init__(self, sql_connector, selected_course_id=None, independent=False):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Course_View()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)
        self.selected_course_id = selected_course_id
        self.independent = independent

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        if self.independent:
            self.DisableAccountInputs()
        window.exec()


    def DisableAccountInputs(self):
        # Find and disable all comboboxes and buttons containing "account" in their name
        for widget in self.ui.__dict__.values():
            if isinstance(widget, (QComboBox, QPushButton)) and "account" in widget.objectName().lower():
                if isinstance(widget, QComboBox):
                    widget.clear()  # Clear the combobox items before disabling
                widget.setEnabled(False)


    def initialize(self, window):
        self.ui.course_date_input.setDate(QDate.currentDate())
        self.ui.course_costs_account_combobox.setDisabled(True)
        self.ui.course_costs_opposite_account_combobox.setDisabled(True)
        self.fetchAccounts()
        self.fetchCurrencies()
        if self.selected_course_id is not None:
            self.fetchSelectedCourse()
        self.ui.select_course_costs_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.course_costs_account_combobox))
        self.ui.select_course_costs_opposite_account_btn.clicked.connect(lambda: self.openSelectAccountWindow(self.ui.course_costs_opposite_account_combobox))
        self.ui.course_save_btn.clicked.connect(lambda: self.saveCourse(window))

    def fetchAccounts(self):
        self.ui.course_costs_account_combobox.addItem('لا يوجد', None)
        self.ui.course_costs_opposite_account_combobox.addItem('لا يوجد', None)
        accounts = self.database_operations.fetchAccounts()
        for account in accounts:
            id = account['id']
            name = account['name']
            self.ui.course_costs_account_combobox.addItem(name, id)
            self.ui.course_costs_opposite_account_combobox.addItem(name, id)

    def fetchCurrencies(self):
        currencies = self.database_operations.fetchCurrencies()
        for currency in currencies:
            id = currency['id']
            name = currency['name']
            self.ui.course_cost_currency_combobox.addItem(name, id)

    def fetchSelectedCourse(self):
        self.ui.course_name_input.clear()
        self.ui.course_cost_input.clear()
        self.ui.course_providor_input.clear()
        self.ui.course_place_input.clear()

        # Fetch course info
        course_info = self.database_operations.fetchSelectedCourse(self.selected_course_id)
        if course_info:
            id = course_info['id']
            title = course_info['title']
            providor = course_info['providor']
            account_id = course_info['account_id']
            opposite_account_id = course_info['opposite_account_id']
            cost = course_info['cost']
            currency_id = course_info['currency_id']
            date = course_info['date_col']
            location = course_info['location']

            # Update UI elements with fetched course info
            self.ui.course_name_input.setText(str(title))
            self.ui.course_cost_input.setText(str(cost))
            self.ui.course_providor_input.setText(str(providor))
            self.ui.course_place_input.setText(str(location))

            self.ui.course_costs_account_combobox.setCurrentIndex(
                self.ui.course_costs_account_combobox.findData(account_id))

            self.ui.course_costs_opposite_account_combobox.setCurrentIndex(
                self.ui.course_costs_opposite_account_combobox.findData(opposite_account_id))

            self.ui.course_cost_currency_combobox.setCurrentIndex(
                self.ui.course_cost_currency_combobox.findData(currency_id))

            self.ui.course_date_input.setDate(date)

    def openSelectAccountWindow(self, combobox):
        data_picker_logic = Ui_DataPicker_Logic(self.sql_connector, 'accounts', include_none_option=True)
        result = data_picker_logic.showUi()
        if result is not None:
            combobox.setCurrentIndex(combobox.findData(result['id']))

    def saveCourse(self, window):
        title = self.ui.course_name_input.text()
        cost = self.ui.course_cost_input.text()
        providor = self.ui.course_providor_input.text()
        location = self.ui.course_place_input.text()
        date = self.ui.course_date_input.date().toString(Qt.ISODate)
        currency_id = self.ui.course_cost_currency_combobox.currentData()
        course_costs_account_id = self.ui.course_costs_account_combobox.currentData()
        course_costs_opposite_account_id = self.ui.course_costs_opposite_account_combobox.currentData()

        if course_costs_account_id is None:
            course_costs_account_id = ''

        if course_costs_opposite_account_id is None:
            course_costs_opposite_account_id = ''

        if title != '' and cost != '' and providor != '' and location != '':
            if self.selected_course_id is None:
                course_id = self.database_operations.addNewCourse(title, cost, providor, location, course_costs_account_id, course_costs_opposite_account_id, currency_id, date)

                if not self.independent:
                    # entry = self.database_operations.fetchJournalEntries(origin_id=selected_position_id)
                    # if not entry:
                    entry_id = self.database_operations.addJournalEntry(entry_date=date, currency=currency_id, origin_type='course', origin_id=course_id)

                    if entry_id:
                        statement = 'course_expense'
                        self.database_operations.addJournalEntryItem(journal_entry_id=entry_id,currency=currency_id,type_col='creditor',account=course_costs_account_id,opposite_account= course_costs_opposite_account_id,statement=statement ,value=cost)
                
            else:
                self.database_operations.saveCourse(self.selected_course_id, title, cost, providor, location, course_costs_account_id, course_costs_opposite_account_id, currency_id, date)
            window.accept()
        else:
            QMessageBox.warning(window, self.language_manager.translate('ERROR'), self.language_manager.translate('ALL_FIELDS_MUST_BE_FILLED'))

