from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

from DatabaseOperations import DatabaseOperations
from Ui_ClientEdit import Ui_ClientEdit
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_ClientEdit_Logic(object):
    database_operations = ''
    client_id = ''
    
    def __init__(self, sql_connector, client_id):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.client_id = client_id
        self.ui = Ui_ClientEdit()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_edit_client = QDialog()
        self.ui.setupUi(window_edit_client)
        self.initialize(window_edit_client)
        self.language_manager.load_translated_ui(self.ui, window_edit_client)
        window_edit_client.exec()
        
    def initialize(self, window):
        self.ui.save_btn.clicked.connect(lambda: self.saveClient())
        self.ui.save_btn.clicked.connect(window.accept)
        self.getClientData()

    def getClientData(self):
        client = self.database_operations.fetchClient(self.client_id)
        name = client['name']
        governorate = client['governorate']
        address = client['address']
        email = client['email']
        phone1 = client['phone1']
        phone2 = client['phone2']
        phone3 = client['phone3']
        phone4 = client['phone4']

        self.ui.name_input.setText(str(name))
        self.ui.governorate_input.setText(str(governorate))
        self.ui.address_input.setText(str(address))
        self.ui.email_input.setText(str(email))
        self.ui.phone1_input.setText(str(phone1))
        self.ui.phone2_input.setText(str(phone2))
        self.ui.phone3_input.setText(str(phone3))
        self.ui.phone4_input.setText(str(phone4))

    def saveClient(self):
        name = self.ui.name_input.text()
        governorate = self.ui.governorate_input.text()
        address = self.ui.address_input.text()
        email = self.ui.email_input.text()
        phone1 = self.ui.phone1_input.text()
        phone2 = self.ui.phone2_input.text()
        phone3 = self.ui.phone3_input.text()
        phone4 = self.ui.phone4_input.text()

        if name == '':
            pass
        else:
            #save to database
            self.database_operations.updateClient(self.client_id, name, governorate, address, email, phone1, phone2, phone3, phone4)
