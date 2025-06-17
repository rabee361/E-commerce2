from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog, QPushButton, QComboBox, QLineEdit, QDateEdit, QTableWidget, QGroupBox, QLabel, QRadioButton, QCheckBox, QMenuBar, QMenu
from StyleManager import StyleManager

class StyleApplicator:
    """
    Utility class to apply styles to UI elements.
    """
    
    @staticmethod
    def apply_global_style():
        """Apply the global style to the entire application"""
        QApplication.instance().setStyleSheet(StyleManager.get_global_style())
    
    @staticmethod
    def apply_styles_to_ui(ui_instance):
        """Apply appropriate styles to all widgets in a UI instance"""
        # Apply styles to buttons
        for widget_name in dir(ui_instance):
            widget = getattr(ui_instance, widget_name)
            
            # Apply button styles
            if isinstance(widget, QPushButton):
                if widget_name == "save_btn" or "save" in widget_name.lower():
                    widget.setStyleSheet(StyleManager.get_save_button_style())
                elif widget_name == "cancel_btn" or "cancel" in widget_name.lower() or "delete" in widget_name.lower() or "remove" in widget_name.lower():
                    widget.setStyleSheet(StyleManager.get_cancel_button_style())
                else:
                    widget.setStyleSheet(StyleManager.get_button_style())
            
            # Apply combobox styles
            elif isinstance(widget, QComboBox):
                widget.setStyleSheet(StyleManager.get_combobox_style())
            
            # Apply lineedit styles
            elif isinstance(widget, QLineEdit):
                widget.setStyleSheet(StyleManager.get_lineedit_style())
            
            # Apply dateedit styles
            elif isinstance(widget, QDateEdit):
                widget.setStyleSheet(StyleManager.get_dateedit_style())
            
            # Apply table styles
            elif isinstance(widget, QTableWidget):
                widget.setStyleSheet(StyleManager.get_table_style())
            
            # Apply groupbox styles
            elif isinstance(widget, QGroupBox):
                widget.setStyleSheet(StyleManager.get_groupbox_style())
            
            # Apply label styles
            elif isinstance(widget, QLabel):
                widget.setStyleSheet(StyleManager.get_label_style())
            
            # Apply radiobutton styles
            elif isinstance(widget, QRadioButton):
                widget.setStyleSheet(StyleManager.get_radiobutton_style())
            
            # Apply checkbox styles
            elif isinstance(widget, QCheckBox):
                widget.setStyleSheet(StyleManager.get_checkbox_style())
            
            # Apply menubar styles
            elif isinstance(widget, QMenuBar):
                widget.setStyleSheet(StyleManager.get_menubar_style())
                
                # Also apply styles to all menus in the menubar
                for action in widget.actions():
                    menu = action.menu()
                    if menu:
                        menu.setStyleSheet(StyleManager.get_menu_style())
            
            # Apply menu styles
            elif isinstance(widget, QMenu):
                widget.setStyleSheet(StyleManager.get_menu_style())
                
        # Apply styles to the main window's menubar if it exists
        if hasattr(ui_instance, 'menubar'):
            ui_instance.menubar.setStyleSheet(StyleManager.get_menubar_style())
            
            # Apply styles to all menus in the menubar
            for action in ui_instance.menubar.actions():
                menu = action.menu()
                if menu:
                    menu.setStyleSheet(StyleManager.get_menu_style())
                    
                    # Apply styles to submenus recursively
                    StyleApplicator._apply_style_to_submenus(menu)
    
    @staticmethod
    def _apply_style_to_submenus(menu):
        """Recursively apply styles to all submenus"""
        for action in menu.actions():
            submenu = action.menu()
            if submenu:
                submenu.setStyleSheet(StyleManager.get_menu_style())
                StyleApplicator._apply_style_to_submenus(submenu)
