
import win32api
from PyQt5.QtWidgets import QDialog
from win32con import MB_OK, MB_OKCANCEL, IDCANCEL
from PyQt5.QtCore import QTranslator, QCoreApplication

from UiStyles import UiStyles
from Ui_Users import Ui_Users
from Ui_AddUser_Logic import Ui_AddUser_Logic
from DatabaseOperations import DatabaseOperations
from PyQt5 import QtWidgets
from win32con import MB_YESNO, IDYES , MB_OK ,IDNO
from PyQt5 import QtCore
from Ui_ResetPassword_Logic import Ui_ResetPassword_Logic
from LanguageManager import LanguageManager
class Ui_Users_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.ui = Ui_Users()
        self.database_operations = DatabaseOperations(sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window_users = QDialog()
        self.ui.setupUi(window_users)
        self.initialize(window_users)
        self.language_manager.load_translated_ui(self.ui, window_users)
        window_users.exec()

    def initialize(self, window):
        self.AddColumnsUsersTable()
        self.fetchUserInfo()
        self.ui.add_user_btn.clicked.connect(lambda: self.openAddUserWindow())
        self.ui.remove_user_btn.clicked.connect(lambda: self.removeUser())
        self.ui.reset_password_btn.clicked.connect(lambda: self.resetPassword())
        self.ui.users_table.cellClicked.connect(self.onCellClicked)

    def AddColumnsUsersTable(self):
        criterias = self.database_operations.fetchCriterias()
        current_cols = self.ui.users_table.columnCount()
        for criterion in criterias:
            if criterion['key_name']:
                # Add read column
                col_idx = current_cols
                self.ui.users_table.insertColumn(col_idx)
                self.ui.users_table.setHorizontalHeaderItem(col_idx, QtWidgets.QTableWidgetItem(self.language_manager.translate(criterion['key_name']) + "/" + self.language_manager.translate("READ")))
                current_cols += 1

                # Add write column 
                col_idx = current_cols
                self.ui.users_table.insertColumn(col_idx)
                self.ui.users_table.setHorizontalHeaderItem(col_idx, QtWidgets.QTableWidgetItem(self.language_manager.translate(criterion['key_name']) + "/" + self.language_manager.translate("WRITE")))
                current_cols += 1


    def fetchUserInfo(self):
        users = self.database_operations.fetchUsers()
        self.ui.users_table.setRowCount(0)
        for user in users:
            criterias = self.database_operations.fetchUserPermissions(user['id'])
            numRows = self.ui.users_table.rowCount()
            self.ui.users_table.insertRow(numRows)
            self.ui.users_table.setItem(numRows, 0, QtWidgets.QTableWidgetItem(str(user['id'])))
            self.ui.users_table.setItem(numRows, 1, QtWidgets.QTableWidgetItem(str(user['username'])))
            
            # Get all columns starting from index 2 (after id and username)
            for col in range(2, self.ui.users_table.columnCount()):
                header_text = self.ui.users_table.horizontalHeaderItem(col).text()
                criteria_name = header_text.split("/")[0]
                permission_type = "R" if self.language_manager.translate("READ") in header_text else "W"
                
                # Check if user has this specific permission type for this criteria
                has_permission = any(
                    self.language_manager.translate(c['criteria_key']) == criteria_name and 
                    c['type_col'] == permission_type 
                    for c in criterias
                )
                
                # Add checkmark if user has permission, empty string if not
                check_mark = "✅" if has_permission else ""
                item = QtWidgets.QTableWidgetItem(check_mark)
                item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.users_table.setItem(numRows, col, item)

    def resetPassword(self):
        current_row = self.ui.users_table.currentRow()
        if current_row >= 1:
            user_id = self.ui.users_table.item(current_row, 0).text()
        
            reset_password_dialog = Ui_ResetPassword_Logic(sql_connector=self.sql_connector, user_id=user_id)
            reset_password_dialog.showUi()
            

    def openAddUserWindow(self):
        add_user_dialog = Ui_AddUser_Logic(sql_connector=self.sql_connector)
        add_user_dialog.showUi()
        self.ui.users_table.setRowCount(0)
        self.fetchUserInfo()

    def saveUser(self):
        username = self.ui.username_input.text()
        if username:    
            self.database_operations.updateUser(username)
            self.fetchUsers()
        else:
            win32api.MessageBox(0, self.language_manager.translate("ALERT_ENTER_USERNAME"), self.language_manager.translate("ERROR"))

    def removeUser(self):
        user = self.ui.users_table.currentItem()
        if user:
            user_id = self.ui.users_table.item(user.row(), 0).text()
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("ALERT_DELETE_USER"), self.language_manager.translate("ALERT"), MB_YESNO)
            if messagebox_result == IDYES:
                self.database_operations.removeUser(user_id)
                self.ui.users_table.setRowCount(0)
                self.fetchUserInfo()
            elif messagebox_result == IDNO:
                pass


    def onCellClicked(self, row, col):
        # Only handle clicks after the first 2 columns
        if col <= 1:
            return
            
        # Get the user ID from the first column
        user_id = self.ui.users_table.item(row, 0).text()
        
        # Get the header text for the clicked column
        header_text = self.ui.users_table.horizontalHeaderItem(col).text()

        # Get all criteria from database
        all_criteria = self.database_operations.fetchCriterias()
        
        # Find the criteria that matches this header
        criteria = None
        for c in all_criteria:
            # print(c['key_name'])
            # print(header_text.split("/")[0])
            if self.language_manager.translate(c['key_name']) == header_text.split("/")[0]:
                criteria = c
                break

        if criteria:
            # Get current cell item
            current_item = self.ui.users_table.item(row, col)
            has_permission = current_item.text() == "✅"
            
            # Determine if this is a read or write permission based on column header
            permission_type = "R" if self.language_manager.translate("READ") in header_text else "W"

            if has_permission:
                # Remove permission
                permission_id = self.database_operations.fetchUserPermission(user_id, criteria['name'], permission_type)
                if permission_id:
                    # Remove the permission from database
                    self.database_operations.removeUserPermission(permission_id)
                    # Clear the checkmark
                    current_item = QtWidgets.QTableWidgetItem("")
                    current_item.setTextAlignment(QtCore.Qt.AlignCenter)
                    self.ui.users_table.setItem(row, col, current_item)
            else:
                # Add permission
                self.database_operations.addUserPermission(criteria['id'], user_id, permission_type)
                # Add the checkmark 
                current_item = QtWidgets.QTableWidgetItem("✅")
                current_item.setTextAlignment(QtCore.Qt.AlignCenter)
                self.ui.users_table.setItem(row, col, current_item)


