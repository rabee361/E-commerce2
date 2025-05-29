import win32api
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QAbstractItemView, QHeaderView
from win32con import IDCANCEL, MB_OKCANCEL
from PyQt5.QtGui import QIntValidator

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_ClientAccount_Logic import Ui_ClientAccounts_Logic
from Ui_ClientEdit_Logic import Ui_ClientEdit_Logic
from Ui_Clients import Ui_Clients
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Clients_Logic(QDialog):
    database_operations = ''

    def __init__(self, sql_connector, client_type='customer'):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Clients()
        self.client_type = client_type
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize()
        if self.client_type == 'customer':
            window.setWindowTitle(self.language_manager.translate("CUSTOMERS"))
            window.setWindowIcon(QIcon('icons/clients.png'))
        elif self.client_type == 'supplier':
            window.setWindowTitle(self.language_manager.translate("SUPPLIERS"))
            window.setWindowIcon(QIcon('icons/suppliers.png'))
        window.exec()

    def initialize(self):
        if self.client_type == 'supplier':
            self.ui.groupBox.setTitle(self.language_manager.translate("NEW_SUPPLIER"))
        self.ui.phone1_input.setValidator(QIntValidator())
        self.ui.phone2_input.setValidator(QIntValidator())
        self.ui.phone3_input.setValidator(QIntValidator())
        self.ui.phone4_input.setValidator(QIntValidator())
        self.ui.clients_table.horizontalHeader().setSectionResizeMode(8, QHeaderView.Stretch)
        self.ui.clients_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.clients_table.setSelectionMode(QAbstractItemView.SingleSelection)
        self.ui.clients_table.verticalHeader().hide()
        self.ui.clients_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.ui.clients_table.itemDoubleClicked.connect(lambda: self.openClientAccountsWindow())

        self.ui.save_btn.clicked.connect(lambda: self.saveClient())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteClient())
        self.ui.edit_btn.clicked.connect(lambda: self.openEditClientWindow())
        self.ui.accounts_btn.clicked.connect(lambda: self.openClientAccountsWindow())
        self.getClients()

    def getClients(self):
        self.ui.clients_table.setRowCount(0)
        clients = self.database_operations.fetchClients(client_type=self.client_type)
        for client in clients:
            id = client['id']
            name = client['name']
            governorate = client['governorate'] or ''
            address = client['address'] or ''
            email = client['email'] or ''
            phone1 = client['phone1'] or ''
            phone2 = client['phone2'] or ''
            phone3 = client['phone3'] or ''
            phone4 = client['phone4'] or ''

            numRows = self.ui.clients_table.rowCount()
            self.ui.clients_table.insertRow(numRows)
            # Add text to the row
            self.ui.clients_table.setItem(numRows, 0, MyTableWidgetItem(str(id), id))
            self.ui.clients_table.setItem(numRows, 1, QTableWidgetItem(str(name)))
            self.ui.clients_table.setItem(numRows, 2, QTableWidgetItem(str(governorate)))
            self.ui.clients_table.setItem(numRows, 3, QTableWidgetItem(str(address)))
            self.ui.clients_table.setItem(numRows, 4, QTableWidgetItem(str(phone1)))
            self.ui.clients_table.setItem(numRows, 5, QTableWidgetItem(str(phone2)))
            self.ui.clients_table.setItem(numRows, 6, QTableWidgetItem(str(phone3)))
            self.ui.clients_table.setItem(numRows, 7, QTableWidgetItem(str(phone4)))
            self.ui.clients_table.setItem(numRows, 8, QTableWidgetItem(str(email)))

    def saveClient(self):
        name = self.ui.name_input.text()
        governorate = self.ui.governorate_input.text()
        address = self.ui.address_input.text()
        email = self.ui.email_input.text()
        phone1 = self.ui.phone1_input.text()
        phone2 = self.ui.phone2_input.text()
        phone3 = self.ui.phone3_input.text()
        phone4 = self.ui.phone4_input.text()
        client_type = self.client_type

        if name == '':
            pass
        else:
            # save to database
            self.database_operations.addClient(name, governorate, address, email, phone1, phone2, phone3, phone4, client_type)

            # reload table
            self.getClients()

            # clear inputs
            name = self.ui.name_input.setText("")
            governorate = self.ui.governorate_input.setText("")
            address = self.ui.address_input.setText("")
            email = self.ui.email_input.setText("")
            phone1 = self.ui.phone1_input.setText("")
            phone2 = self.ui.phone2_input.setText("")
            phone3 = self.ui.phone3_input.setText("")
            phone4 = self.ui.phone4_input.setText("")

    def deleteClient(self):
        client_id_cell = self.ui.clients_table.item(self.ui.clients_table.currentRow(), 0)
        if client_id_cell:
            confirm = win32api.MessageBox(0, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_OKCANCEL)
            if confirm == IDCANCEL:
                pass
            else:
                if str(type(client_id_cell)) == "<class 'NoneType'>":
                    pass
                else:
                    client_id = client_id_cell.text()
                    self.database_operations.removeClient(client_id)
                    self.getClients()
        else:
            pass

    def openEditClientWindow(self):
        client_id_cell = self.ui.clients_table.item(self.ui.clients_table.currentRow(), 0)
        if str(type(client_id_cell)) == "<class 'NoneType'>":
            pass
        else:
            client_id = client_id_cell.text()
            Ui_ClientEdit_Logic(self.sql_connector, client_id).showUi()
            self.getClients()

    def openClientAccountsWindow(self):
        # try:
        client_id_cell = self.ui.clients_table.item(self.ui.clients_table.currentRow(), 0)
        if str(type(client_id_cell)) == "<class 'NoneType'>":
            pass
        else:
            client_id = client_id_cell.text()
            if client_id:
                Ui_ClientAccounts_Logic(self.sql_connector, client_id).showUi()
    # except Exception as e:
    #     print(e)
