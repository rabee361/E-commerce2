import win32api
from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QTableWidgetItem, QDialog, QAbstractItemView, QHeaderView
from win32con import IDCANCEL, MB_OKCANCEL

from DatabaseOperations import DatabaseOperations
from MyTableWidgetItem import MyTableWidgetItem
from Ui_ClientAccount_Logic import Ui_ClientAccounts_Logic
from Ui_ClientEdit_Logic import Ui_ClientEdit_Logic
from Ui_Suppliers import Ui_Suppliers
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIntValidator

class Ui_Suppliers_Logic(QDialog):
    database_operations = ''

    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_Suppliers()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_suppliers = QDialog()
        window_suppliers.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_suppliers)
        window_suppliers.setWindowIcon(QIcon('icons/suppliers.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_suppliers)
        window_suppliers.exec()

    def initialize(self):
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
        clients = self.database_operations.fetchClients(client_type='supplier')
        for client in clients:
            id = client['id']
            name = client['name']
            governorate = client['governorate']
            address = client['address']
            email = client['email']
            phone1 = client['phone1']
            phone2 = client['phone2']
            phone3 = client['phone3']
            phone4 = client['phone4']

            numRows = self.ui.clients_table.rowCount();
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

    def clearClientsTable(self):
        self.ui.clients_table.clear()
        self.ui.clients_table.setRowCount(0)
        font = QtGui.QFont()
        font.setBold(True)

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(0, item)
        item.setText("المعرف")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(1, item)
        item.setText("الاسم")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(2, item)
        item.setText("المحافظة")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(3, item)
        item.setText("العنوان التفصيلي")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(4, item)
        item.setText("هاتف 1")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(5, item)
        item.setText("هاتف 2")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(6, item)
        item.setText("هاتف 3")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(7, item)
        item.setText("هاتف 4")

        item = QtWidgets.QTableWidgetItem()
        item.setFont(font)
        self.ui.clients_table.setHorizontalHeaderItem(8, item)
        item.setText("بريد الكتروني")

    def saveClient(self):
        name = self.ui.name_input.text()
        governorate = self.ui.governorate_input.text()
        address = self.ui.address_input.text()
        email = self.ui.email_input.text()
        phone1 = self.ui.phone1_input.text()
        phone2 = self.ui.phone2_input.text()
        phone3 = self.ui.phone3_input.text()
        phone4 = self.ui.phone4_input.text()
        client_type = 'supplier'

        if name == '':
            pass
        else:
            # save to database
            self.database_operations.addClient(name, governorate, address, email, phone1, phone2, phone3, phone4, client_type)
    
            # reload table
            self.clearClientsTable()
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
            confirm = win32api.MessageBox(0, "هل تريد بالتأكيد حذف الموظف ؟", " ", MB_OKCANCEL)
            if confirm == IDCANCEL:
                pass
            else:
                if str(type(client_id_cell)) == "<class 'NoneType'>":
                    pass
                else:
                    client_id = client_id_cell.text()
                    self.database_operations.removeClient(client_id)
                    self.clearClientsTable()
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
            self.clearClientsTable()
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
