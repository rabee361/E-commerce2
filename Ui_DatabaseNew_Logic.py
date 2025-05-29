from PyQt5.QtWidgets import QDialog
import win32api
from Ui_DatabaseNew import Ui_DatabaseNew
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_DatabaseNew_Logic(QDialog):
    def __init__(self, mysql_connector):
        super().__init__()
        self.mysql_connector = mysql_connector
        self.ui = Ui_DatabaseNew()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.create_btn.clicked.connect(lambda: self.createDatabase(window))

    def createDatabase(self, window):
        name = self.ui.db_name_input.text()
        if name != '':
            # get all databases names 
            existing_databases = self.mysql_connector.getDatabasesList()            
            # clean up the databases names
            cleaned_dbs = []
            for db in existing_databases:
                db = str(db).replace("('","").replace("',)","").replace("eps_acc_","")
                cleaned_dbs.append(db)
            if name in cleaned_dbs:
                win32api.MessageBox(0, "يوجد قاعدة بيانات بنفس الاسم", "خطأ")
            else:
                self.mysql_connector.createDatabase(name)
                window.accept()


