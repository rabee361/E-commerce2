import mysql
from PyQt5.QtWidgets import QDialog
from Ui_Databases import Ui_Databases


class Ui_Databases_Logic(QDialog):
    def __init__(self, Mysql_Connection):
        super().__init__()
        self.conn = Mysql_Connection
        self.ui = Ui_Databases()

    def showUi(self):
        window = QDialog()
        self.ui.setupUi(window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        pass

    def getDatabases(self):
        curser = self.conn.cursor()
        curser.execute("SHOW DATABASES")
        for item in curser:
            print(str(item))
            if (str('eps_') in str('item')):
                self.ui.db_list.addItem(item)
                #dbexists = True

    def connectToDatabase(self):
        db_name = self.ui.db_list.item(self.ui.db_list.currentIndex())
        print("Connecting to database...")
        try:
            self.conn = mysql.connector.connect(db_name)
            print("Connected to database.")
            self.is_connected = True;
        except:
            print("Unable to connect to database.")
            self.is_connected = False

    def createDatabase(self):
        print("Creating database...")
        self.createDatabase()
        self.is_connected = True
