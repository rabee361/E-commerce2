from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from win32api import MessageBox
from win32con import MB_YESNO, IDYES

from DatabaseOperations import DatabaseOperations
from UiStyles import UiStyles
from Ui_AddGroup_Logic import Ui_AddGroup_Logic
from Ui_GroupEdit_Logic import Ui_GroupEdit_Logic
from Ui_Groups import Ui_Groups
from PyQt5.QtCore import QCoreApplication , QTranslator
from LanguageManager import LanguageManager

class Ui_Groups_Logic(QDialog, UiStyles):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.ui = Ui_Groups()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        window = QDialog()
        window.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.makeItBlurry(window)
        self.ui.setupUi(window)
        self.initialize(window)
        self.language_manager.load_translated_ui(self.ui, window)
        window.exec()

    def initialize(self, window_activation):
        self.ui.groups_tree.hideColumn(2)
        self.ui.edit_btn.clicked.connect(lambda: self.openGroupEditWindow())
        self.ui.add_btn.clicked.connect(lambda: self.openAddGroupWindow())
        self.ui.delete_btn.clicked.connect(lambda: self.removeGroup())

        self.fetchGroups()

    def fetchGroups(self):
        self.ui.groups_tree.clear()
        groups = self.database_operations.fetchGroups()
        children_queue = []
        for group in groups:
            id = group['id']
            name = group['name']
            code = group['code']
            date = group['date_col']
            parent_id = group['parent_id']
            parent_name = group['parent_name']

            # check if it's a root element or a child element
            if (not parent_id):
                item = QTreeWidgetItem([str(code), str(name), str(id)])
                self.ui.groups_tree.addTopLevelItem(item)
            else:
                items_already_in_tree = self.ui.groups_tree.findItems(str(parent_id), Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                else:  # The parent is not added yet, save the child to add it later.
                    children_queue.append(group)

        while (len(children_queue) > 0):
            for child in children_queue:
                id = child[0];
                name = child[1];
                code = child[2]
                date = child[3];
                parent_id = child[4];
                parent_name = child[5];

                items_already_in_tree = self.ui.groups_tree.findItems(str(parent_id),
                                                                        Qt.MatchExactly | Qt.MatchRecursive, 2)

                if (len(items_already_in_tree) > 0):  # Parent already exists in tree, so append its child
                    for item in items_already_in_tree:
                        item_id = item.text(2)

                        child_item = QTreeWidgetItem([str(code), str(name), str(id)])
                        if (str(parent_id) == str(item_id)):
                            item.addChild(child_item)
                            children_queue.remove(child)
                            print("DELETED")

    def openAddGroupWindow(self):
        Ui_AddGroup_Logic(self.sql_connector).showUi()
        self.ui.groups_tree.clear()
        self.fetchGroups()

    def openGroupEditWindow(self):
        selected_item = self.ui.groups_tree.currentItem()
        if selected_item:
            id = selected_item.text(2)
            if id:
                Ui_GroupEdit_Logic(self.sql_connector, id).showUi()
                self.ui.groups_tree.clear()
                self.fetchGroups()


    def removeGroup(self):
        # Display confirmation dialog
        messagebox_result = MessageBox(None, self.language_manager.translate("DELETE_CONFIRM"), self.language_manager.translate("ALERT"), MB_YESNO)
        if messagebox_result == IDYES:
            # Assuming you have a method to get the selected group ID
            selected_group_id = self.ui.groups_tree.currentItem().text(2)
            if selected_group_id is not None:
                try:    
                    # Assuming you have a method in database_operations to remove a group by its ID
                    self.database_operations.removeGroup(selected_group_id)
                    # Optionally, refresh the groups list or UI
                    self.fetchGroups()
                except:
                    MessageBox(0, self.language_manager.translate("DELETE_ERROR"), self.language_manager.translate("ERROR"))
