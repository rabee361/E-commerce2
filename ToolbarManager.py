from PyQt5.QtWidgets import QAction, QToolBar
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMainWindow
from FileManager import FileManager
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator  

class ToolbarManager:
    """
    # ToolbarManager

    The `ToolbarManager` class is responsible for creating, configuring, and managing the application's main toolbar. It provides a set of actions (buttons) that allow users to quickly access core features of the application, such as file operations, database connections, user management, and more.

    ## Functionality

    - **Initialization**: Sets up the toolbar, its appearance, and all available actions.
    - **Action Management**: Allows showing/hiding actions based on user preferences or application state.
    - **Internationalization**: Supports dynamic translation of toolbar action texts when the application language changes.
    - **Toolbar Appearance**: Configures icon size, button style, and visual appearance for a consistent user experience.

    > **Note:** Some actions may appear more than once with different icons for visual distinction.

    ## Key Methods

    - `__init__`: Initializes the toolbar and its actions.
    - `initialize`: Configures toolbar appearance and adds actions.
    - `showActions(preferences)`: Shows actions based on a list of preferred action names.
    - `clearToolBar()`: Removes all but the first 4 actions from the toolbar.
    - `add_toolbar_actions()`: Adds all defined actions to the toolbar.
    - `create_action(name, icon, text)`: Helper to create and add a toolbar action.
    - `retranslateToolbar()`: Updates action texts when the language changes.
    - `hideToolBar()`: Hides all toolbar actions.
    - `showToolBar(action_handlers)`: Shows actions based on provided handlers or shows all if none.

    ## Example Usage

    ```python
    toolbar_manager = ToolbarManager(window_manager, current_user, ui)
    toolbar_manager.showActions(['new_file', 'open_file'])
    toolbar_manager.retranslateToolbar()
    ```

    This class ensures a consistent, dynamic, and internationalized toolbar experience for the application's users.
    """

    def __init__(self, window_manager=None, current_user=0, ui=None):
        self.windows_manager = window_manager
        self.sql_connector = ''
        self.toolbar = QToolBar()
        self.current_user = current_user
        self.database_operations = ''
        self.ui = ui
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        self.actions = []  # Store actions for visibility management
        self.initialize()
        
    def initialize(self):
        # Set up the main window and toolbar properties
        window = QMainWindow()
        self.window = window
        self.filemanager = FileManager()
        self.toolbar.setMovable(False)
        self.toolbar.setFloatable(False)
        self.toolbar.setIconSize(QSize(32, 32))
        self.toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.toolbar.setStyleSheet("""
            QToolBar {
                spacing: 5px;
                background-color: #f0f0f0;
            }
            QToolButton {
                color: #333;
                border: none;
                padding: 10px 3px 4px 3px;
                text-align: center;
            }
            QToolButton:hover {
                background-color: #e0e0e0;
            }
        """)
        # Add toolbar actions
        self.add_toolbar_actions()
        # Hide all actions initially
        for action in self.actions:
            action.setVisible(False)
        # Show the first four actions by default
        self.actions[0].setVisible(True)
        self.actions[1].setVisible(True)
        self.actions[2].setVisible(True)
        self.actions[3].setVisible(True)

    def showActions(self, prefrences):
        # Show actions whose objectName matches any in the preferences list
        for prefrence in prefrences:
            for action in self.actions[4:]:
                if action.objectName() == prefrence:
                    action.setVisible(True)
                    
    def clearToolBar(self):
        # Remove all actions except the first 4 and the separator
        for action in self.toolbar.actions()[5:]:
            self.toolbar.removeAction(action)
        self.actions = self.actions[:5]

    def add_toolbar_actions(self):
        # Add all toolbar actions with their icons and translation keys
        self.create_action(
            name="new_file",
            icon="icons/plus.png",
            text="TOOLBAR_NEW"
        )
        self.create_action(
            name="connect_database", 
            icon="icons/connect_to_database.png",
            text="TOOLBAR_CONNECT"
        )
        self.create_action(
            name="open_file",
            icon="icons/file.png",
            text="TOOLBAR_OPEN"
        )
        self.create_action(
            name="calculator",
            icon="icons/calculator.png",
            text="TOOLBAR_CALCULATOR"
        )
        self.create_action(
            name="users",
            icon="icons/clients.png",
            text="TOOLBAR_USERS"
        )
        self.create_action(
            name="refresh",
            icon="icons/refresh.png", 
            text="TOOLBAR_REFRESH"
        )
        self.create_action(
            name="language",
            icon="icons/language.png", 
            text="TOOLBAR_LANGUAGE"
        )
        self.create_action(
            name="backup",
            icon="icons/batch_process.png", 
            text="TOOLBAR_BACKUP"
        )
        self.create_action(
            name="warehouses",
            icon="icons/warehouse.png", 
            text="TOOLBAR_WAREHOUSES"
        )
        self.create_action(
            name="material_move",
            icon="icons/motion_path.png",
            text="TOOLBAR_MATERIAL_MOVE"
        )
        self.create_action(
            name="materials",
            icon="icons/set_parent.png",
            text="TOOLBAR_MATERIALS"
        )
        self.create_action(
            name="customers",
            icon="icons/clients.png",
            text="TOOLBAR_CUSTOMERS"
        )
        self.create_action(
            name="suppliers",
            icon="icons/suppliers.png",
            text="TOOLBAR_SUPPLIERS"
        )
        self.create_action(
            name="ledger",
            icon="icons/bookkeeper.png",
            text="TOOLBAR_LEDGER"
        )
        self.create_action(
            name="manufacture",
            icon="icons/hammer.png",
            text="TOOLBAR_MANUFACTURE"
        )
        self.create_action(
            name="raw_materials_needs",
            icon="icons/resources.png",
            text="TOOLBAR_RAW_MATERIALS_NEEDS"
        )
        self.create_action(
            name="units",
            icon="icons/balance.png",
            text="TOOLBAR_UNITS"
        )
        self.create_action(
            name="cost_center",
            icon="icons/project.png",
            text="TOOLBAR_COST_CENTER"
        )
        self.create_action(
            name="currencies",
            icon="icons/coin_dollar.png",
            text="TOOLBAR_CURRENCIES"
        )
        self.create_action(
            name="cost_center",
            icon="icons/inventory.png",
            text="TOOLBAR_COST_CENTER"
        )
        self.create_action(
            name="clients_report",
            icon="icons/report2.png",
            text="TOOLBAR_CLIENT_REPORT"
        )
        self.create_action(
            name="suppliers_report",
            icon="icons/report2.png",
            text="TOOLBAR_SUPPLIER_REPORT"
        )
        self.create_action(
            name="invoices",
            icon="icons/papers.png",
            text="TOOLBAR_INVOICES"
        )
        # Add toolbar to main window
        self.window.addToolBar(self.toolbar)
        
    def create_action(self, name, icon, text):
        """Create and add a toolbar action with icon and translation key."""
        action = QAction(self.window)
        action.setIcon(QIcon(icon))
        action.setObjectName(name)
        action.setProperty("translationKey", text)
        action.setText(self.language_manager.translate(text))
        self.toolbar.addAction(action)
        self.actions.append(action)
        return action

    def retranslateToolbar(self):
        """Update toolbar text when language changes."""
        for action in self.actions:
            translation_key = action.property("translationKey")
            if translation_key:
                action.setText(self.language_manager.translate(translation_key))

    def hideToolBar(self):
        # Hide all toolbar actions
        for action in self.actions:
            action.setVisible(False)

    def showToolBar(self, action_handlers):
        # Show only actions whose objectName is in action_handlers, or all if not specified
        if action_handlers:
            for action in self.actions:
                if action.objectName() in action_handlers:
                    action.setVisible(True)
        else:
            for action in self.actions:
                action.setVisible(True)
