from PyQt5.QtWidgets import QDialog, QLabel, QCheckBox, QVBoxLayout, QWidget, QHBoxLayout
from PyQt5 import QtCore
import win32api
import win32con
from DatabaseOperations import DatabaseOperations
from Ui_ShortCutSettings import Ui_ShortCutSettings
from Ui_AuthenticateUser_Logic import Ui_AuthenticateUser_Logic
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_ShortCutSettings_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(sql_connector)
        self.ui = Ui_ShortCutSettings()
        self.checkboxes = {}
        self.current_user = Ui_AuthenticateUser_Logic(self.sql_connector).getCurrentUser()
        self.window = ''  
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)

    def showUi(self):
        self.window = QDialog()
        self.window.setWindowModality(QtCore.Qt.WindowModal)
        self.ui.setupUi(self.window)
        self.language_manager.load_translated_ui(self.ui, self.window)
        self.initialize(self.window)
        self.window.exec()

    def initialize(self, window):
        # Define shortcuts here instead of in initialize
        self.shortcuts = {
            'reports': 'TOOLBAR_REPORTS',
            'materials': 'TOOLBAR_MATERIALS', 
            'warehouses': 'TOOLBAR_WAREHOUSES',
            'currency': 'TOOLBAR_CURRENCIES',
            'units': 'TOOLBAR_UNITS',
            'customers': 'TOOLBAR_CUSTOMERS',
            'material_move': 'TOOLBAR_MATERIAL_MOVE',
            'manufacture': 'TOOLBAR_MANUFACTURE',
            'ledger': 'TOOLBAR_LEDGER',
            'journal_entry': 'TOOLBAR_JOURNAL_ENTRY',
            'raw_materials_needs': 'TOOLBAR_RAW_MATERIALS_NEEDS',
            'daily_journal': 'TOOLBAR_DAILY_JOURNAL',
            'warehouse_report': 'TOOLBAR_WAREHOUSE_REPORT',
            'suppliers': 'TOOLBAR_SUPPLIERS',
            'clients_report': 'TOOLBAR_CLIENT_REPORT',
            'invoices': 'TOOLBAR_INVOICES',
            'suppliers_report': 'TOOLBAR_SUPPLIER_REPORT',
        }

        self.fetchUserShortcutSettings()
        self.ui.save_btn.clicked.connect(self.saveShortcutSettings)

    def fetchUserShortcutSettings(self):
        # Get the layout containers for both columns
        right_column = self.ui.scrollAreaWidgetContents.findChild(QVBoxLayout, "right_column")
        left_column = self.ui.scrollAreaWidgetContents.findChild(QVBoxLayout, "left_column")
        
        # Set smaller spacing for the columns
        right_column.setSpacing(5)
        left_column.setSpacing(5)
        
        # Get the main horizontal layout and set its margins to minimum
        main_layout = self.ui.scrollAreaWidgetContents.findChild(QHBoxLayout, "horizontalLayout")
        main_layout.setContentsMargins(5, 5, 5, 5)
        
        user_settings = self.database_operations.fetchUserSettings(self.current_user)
        user_settings = [row['name'] for row in user_settings]
        
        # Calculate the midpoint to split shortcuts between columns
        total_shortcuts = len(self.shortcuts)
        midpoint = (total_shortcuts + 1) // 2
        
        # Counter to track which column to add to
        counter = 0
        
        # Find the longest label to set fixed width
        max_width = 0
        test_label = QLabel()
        font = test_label.font()
        font_metrics = test_label.fontMetrics()
        
        for translated_name in self.shortcuts.values():
            width = font_metrics.horizontalAdvance(translated_name)
            max_width = max(max_width, width)
        
        # Add less padding to the max width
        max_width += 20  # Reduce padding from 50 to 20 pixels
        
        for name, translated_name in self.shortcuts.items():
            # Create container for each shortcut
            container = QWidget()
            container_layout = QHBoxLayout(container)
            container_layout.setContentsMargins(0, 0, 0, 0)
            container_layout.setSpacing(5)  # Further reduce spacing from 10 to 5
            
            # Create label with Arabic text and fixed width
            label = QLabel()
            label.setText(self.language_manager.translate(translated_name))
            label.setMinimumWidth(max_width)
            checkbox = QCheckBox()
            
            # Load existing setting from database
            if name in user_settings:
                checkbox.setChecked(True)
            else:
                checkbox.setChecked(False)
            
            # Store checkbox reference
            self.checkboxes[name] = checkbox
            
            # Add widgets to container
            container_layout.addWidget(checkbox)
            container_layout.addWidget(label)
            
            # Add to appropriate column
            if counter < midpoint:
                right_column.addWidget(container)
            else:
                left_column.addWidget(container)
            
            counter += 1
        
        # Add stretch to both columns to keep items at the top
        right_column.addStretch()
        left_column.addStretch()

    def saveShortcutSettings(self):
        for shortcut_key, checkbox in self.checkboxes.items():
            # If checkbox is checked, add setting if it doesn't exist
            user_shortcut = self.database_operations.fetchUserSetting(self.current_user,shortcut_key)
            if checkbox.isChecked():
                if not user_shortcut:
                    self.database_operations.saveUserSetting(self.current_user, shortcut_key)
            # If checkbox is unchecked, remove setting if it exists
            else:
                if user_shortcut:
                    self.database_operations.removeUserSetting(self.current_user, shortcut_key)
                
        win32api.MessageBox(0, self.language_manager.translate("SAVED_SUCCESSFULLY"), self.language_manager.translate("SUCCESS"), win32con.MB_OK)
        self.window.close() # Close the window after saving
