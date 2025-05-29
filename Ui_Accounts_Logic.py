from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from win32con import MB_YESNO, IDYES, IDNO
import win32api
import Colors
from DatabaseOperations import DatabaseOperations
from Ui_AccountEdit_Logic import Ui_AccountEdit_Logic
from Ui_Accounts import Ui_Accounts
from Ui_AddAccount_Logic import Ui_AddAccount_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator
from PyQt5.QtGui import QIcon

class Ui_Accounts_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_Accounts()
        self.all_accounts = []  # Store all accounts for filtering
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)    

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window)
        window.setWindowIcon(QIcon('icons/clipboard.png'))
        self.language_manager.load_translated_ui(self.ui, window)
        self.initialize(window)
        window.exec()

    def initialize(self, window):
        self.ui.accounts_tree.hideColumn(2)
        self.ui.edit_btn.clicked.connect(lambda: self.openAccountEditWindow())
        self.ui.add_btn.clicked.connect(lambda: self.openAddAccountWindow())
        self.ui.delete_btn.clicked.connect(lambda: self.deleteAccount())
        self.ui.accounts_tree.itemDoubleClicked.connect(lambda item: self.openAccountEditWindow())
        
        # Connect search box to filter function
        self.ui.search_box.textChanged.connect(self.filterAccounts)
        
        self.fetchAccounts()

    def fetchAccounts(self):
        accounts = self.database_operations.fetchAccounts()
        children_queue = []
        for account in accounts:
            id = account['id']
            name = account['name'] 
            code = account['code']
            details = account['details']
            date = account['date_col']
            parent_id = account['parent_id']
            parent_name = account['parent_name']
            account_type = account['type_col']
            final_account = account['final_account']
            financial_statement = account['financial_statement']
            financial_statement_block = account['financial_statement_block']

            if not parent_id:
                item = QTreeWidgetItem([str(code), str(name), str(id)])
                self.ui.accounts_tree.addTopLevelItem(item)
                if account_type == "final":
                    for col in range(item.columnCount()):
                        item.setBackground(col, Colors.blue_sky_color)  # Light Blue color
            else:
                items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id),
                                                                        Qt.MatchExactly | Qt.MatchRecursive, 2)
                if len(items_already_in_tree) > 0:
                    for item in items_already_in_tree:
                        item_id = item.text(2)
                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])

                        if str(parent_id) == str(item_id):
                            if account_type == "final":
                                for col in range(child_item.columnCount()):
                                    child_item.setBackground(col, Colors.blue_sky_color)  # Light Blue color
                            item.addChild(child_item)
                else:
                    children_queue.append(account)

        for child in children_queue:
            id = child['id']
            name = child['name']
            code = child['code']
            details = child['details']
            date = child['date_col']
            parent_id = child['parent_id']
            parent_name = child['parent_name']
            account_type = child['type_col']
            final_account = child['final_account']
            financial_statement = child['financial_statement']
            financial_statement_block = child['financial_statement_block']
            items_already_in_tree = self.ui.accounts_tree.findItems(str(parent_id),
                                                                    Qt.MatchExactly | Qt.MatchRecursive, 2)

            if len(items_already_in_tree) > 0:
                for item in items_already_in_tree:
                    item_id = item.text(2)
                    child_item = QTreeWidgetItem([str(code), str(name), str(id)])

                    if str(parent_id) == str(item_id):
                        if account_type == "final":
                            for col in range(child_item.columnCount()):
                                child_item.setBackground(col, Colors.blue_sky_color)  # Light Blue color
                        item.addChild(child_item)
                        children_queue.remove(child)
                        print("DELETED")
        self.ui.accounts_tree.setCurrentItem(None)  # Explicitly clear the current selection


    def filterAccounts(self, search_text):
        # Reset all items to visible and collapsed
        root = self.ui.accounts_tree.invisibleRootItem()
        for i in range(root.childCount()):
            root.child(i).setHidden(False)
            self.collapseAllChildren(root.child(i))

        if not search_text:
            return

        # Do DFS to find matching items and show their path
        matching_paths = []
        for i in range(root.childCount()):
            self.dfsSearch(root.child(i), search_text.lower(), [], matching_paths)

        # Hide non-matching top level items that don't have matching descendants
        for i in range(root.childCount()):
            top_item = root.child(i)
            top_item_id = top_item.text(2)
            has_match = False
            for path in matching_paths:
                if str(top_item_id) in path:
                    has_match = True
                    break
            if not has_match:
                top_item.setHidden(True)

        # Expand paths to matching items
        for path in matching_paths:
            current = root
            for item_id in path:
                for i in range(current.childCount()):
                    if current.child(i).text(2) == str(item_id):
                        current.child(i).setExpanded(True)
                        current = current.child(i)
                        break

    def dfsSearch(self, item, search_text, current_path, matching_paths):
        # Check if current item matches search
        if search_text in item.text(1).lower():
            path = current_path + [item.text(2)]
            if path not in matching_paths:
                matching_paths.append(path)
            
        # Recursively search children
        for i in range(item.childCount()):
            self.dfsSearch(item.child(i), search_text, 
                         current_path + [item.text(2)],
                         matching_paths)

    def collapseAllChildren(self, item):
        item.setExpanded(False)
        for i in range(item.childCount()):
            self.collapseAllChildren(item.child(i))

    def openAddAccountWindow(self):
        selected_account = self.ui.accounts_tree.currentItem()
        if str(type(selected_account)) == "<class 'NoneType'>":
            parent_account_id = None
            parent_account_name = None
        else:
            parent_account_id = selected_account.text(2)
            parent_account_name = selected_account.text(1)
        Ui_AddAccount_Logic(self.sql_connector, parent_account_id=parent_account_id, parent_account_name=parent_account_name).showUi()
        self.ui.accounts_tree.clear()
        self.fetchAccounts()

    def openAccountEditWindow(self):
        selected_account = self.ui.accounts_tree.currentItem()
        if str(type(selected_account)) == "<class 'NoneType'>":
            pass
        else:
            id = selected_account.text(2)
            Ui_AccountEdit_Logic(self.sql_connector, id).showUi()
            self.ui.accounts_tree.clear()
            self.fetchAccounts()

    def deleteAccount(self):
        account = self.ui.accounts_tree.currentItem()
        if account:
            messagebox_result = win32api.MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
            if (messagebox_result == IDYES):
                try:
                    id = account.text(2)
                    deleted = self.database_operations.removeAccount(id)
                    if deleted:
                        self.ui.accounts_tree.clear()
                        self.fetchAccounts()
                    else:
                        win32api.MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
                except:
                    pass
            elif (messagebox_result == IDNO):
                pass
