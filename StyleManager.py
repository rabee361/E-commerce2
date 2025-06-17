class StyleManager:
    """
    Centralized style manager for the application.
    Contains all styles used across the application.
    """

    # Color palette
    PRIMARY_COLOR = "#2196F3"  # Blue
    SECONDARY_COLOR = "#FFC107"  # Amber
    SUCCESS_COLOR = "#4CAF50"  # Green
    ERROR_COLOR = "#F44336"  # Red
    WARNING_COLOR = "#FF9800"  # Orange
    INFO_COLOR = "#2196F3"  # Blue
    LIGHT_BG = "#F5F5F5"  # Light grey
    DARK_BG = "#424242"  # Dark grey
    WHITE = "#FFFFFF"
    BLACK = "#000000"
    BORDER_COLOR = "#DDDDDD"
    MENU_BG = "#FFFFFF"  # Menu background
    MENU_HOVER_BG = "#E3F2FD"  # Menu hover background
    MENU_TEXT = "#000000"  # Menu text color
    MENU_HOVER_TEXT = "#2196F3"  # Menu hover text color
    
    # Font settings
    FONT_FAMILY = "Tahoma"
    FONT_SIZE_SMALL = "12px"
    FONT_SIZE_MEDIUM = "14px"
    FONT_SIZE_LARGE = "16px"
    
    # UI element sizing
    CONTROL_HEIGHT = "24px"  # Standard height for controls
    CONTROL_PADDING = "2px 6px"  # Standard padding for controls
    CONTROL_BORDER_RADIUS = "4px"  # Standard border radius
    
    # Common styles
    @classmethod
    def get_main_window_style(cls):
        return f"""
            QMainWindow, QDialog {{
                background-color: {cls.LIGHT_BG};
            }}
        """
    
    @classmethod
    def get_button_style(cls, button_type="default"):
        if button_type == "primary":
            return f"""
                QPushButton {{
                    background-color: {cls.PRIMARY_COLOR};
                    color: {cls.WHITE};
                    border: none;
                    border-radius: {cls.CONTROL_BORDER_RADIUS};
                    padding: {cls.CONTROL_PADDING};
                    height: {cls.CONTROL_HEIGHT};
                    font-family: {cls.FONT_FAMILY};
                    font-size: {cls.FONT_SIZE_MEDIUM};
                }}
                QPushButton:hover {{
                    background-color: #1976D2;
                }}
                QPushButton:pressed {{
                    background-color: #0D47A1;
                }}
                QPushButton:disabled {{
                    background-color: #BBDEFB;
                    color: #78909C;
                }}
            """
        elif button_type == "success":
            return f"""
                QPushButton {{
                    background-color: {cls.SUCCESS_COLOR};
                    color: {cls.WHITE};
                    border: none;
                    border-radius: {cls.CONTROL_BORDER_RADIUS};
                    padding: {cls.CONTROL_PADDING};
                    height: {cls.CONTROL_HEIGHT};
                    font-family: {cls.FONT_FAMILY};
                    font-size: {cls.FONT_SIZE_MEDIUM};
                }}
                QPushButton:hover {{
                    background-color: #388E3C;
                }}
                QPushButton:pressed {{
                    background-color: #2E7D32;
                }}
                QPushButton:disabled {{
                    background-color: #C8E6C9;
                    color: #78909C;
                }}
            """
        elif button_type == "danger":
            return f"""
                QPushButton {{
                    background-color: {cls.ERROR_COLOR};
                    color: {cls.WHITE};
                    border: none;
                    border-radius: {cls.CONTROL_BORDER_RADIUS};
                    padding: {cls.CONTROL_PADDING};
                    height: {cls.CONTROL_HEIGHT};
                    font-family: {cls.FONT_FAMILY};
                    font-size: {cls.FONT_SIZE_MEDIUM};
                }}
                QPushButton:hover {{
                    background-color: #D32F2F;
                }}
                QPushButton:pressed {{
                    background-color: #B71C1C;
                }}
                QPushButton:disabled {{
                    background-color: #FFCDD2;
                    color: #78909C;
                }}
            """
        else:  # default
            return f"""
                QPushButton {{
                    background-color: {cls.WHITE};
                    color: {cls.BLACK};
                    border: 1px solid {cls.BORDER_COLOR};
                    border-radius: {cls.CONTROL_BORDER_RADIUS};
                    padding: {cls.CONTROL_PADDING};
                    height: {cls.CONTROL_HEIGHT};
                    font-family: {cls.FONT_FAMILY};
                    font-size: {cls.FONT_SIZE_MEDIUM};
                }}
                QPushButton:hover {{
                    background-color: #F5F5F5;
                }}
                QPushButton:pressed {{
                    background-color: #E0E0E0;
                }}
                QPushButton:disabled {{
                    background-color: #F5F5F5;
                    color: #9E9E9E;
                }}
            """
    
    @classmethod
    def get_combobox_style(cls):
        return f"""
            QComboBox {{
                background-color: {cls.WHITE};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.CONTROL_BORDER_RADIUS};
                min-width: 6em;
                height: {cls.CONTROL_HEIGHT};
            }}
            QComboBox:hover {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QComboBox:focus {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QComboBox:disabled {{
                background-color: #F5F5F5;
                color: #9E9E9E;
            }}
        """
    
    @classmethod
    def get_lineedit_style(cls):
        return f"""
            QLineEdit {{
                background-color: {cls.WHITE};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.CONTROL_BORDER_RADIUS};
                padding: 0px 6px;
                height: {cls.CONTROL_HEIGHT};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
            }}
            QLineEdit:hover {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QLineEdit:focus {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QLineEdit:disabled {{
                background-color: #F5F5F5;
                color: #9E9E9E;
            }}
        """
    
    @classmethod
    def get_dateedit_style(cls):
        return f"""
            QDateEdit {{
                background-color: {cls.WHITE};
                color: {cls.BLACK};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: {cls.CONTROL_BORDER_RADIUS};
                padding: {cls.CONTROL_PADDING};
                height: {cls.CONTROL_HEIGHT};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
            }}
            QDateEdit:hover {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QDateEdit:focus {{
                border: 1px solid {cls.PRIMARY_COLOR};
            }}
            QDateEdit:disabled {{
                background-color: #F5F5F5;
                color: #9E9E9E;
            }}
            QDateEdit::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: center right;
                width: 24px;
                border-left-width: 1px;
                border-left-color: {cls.BORDER_COLOR};
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
            }}
        """
    
    @classmethod
    def get_table_style(cls):
        return f"""
            QTableWidget {{
                background-color: {cls.WHITE};
                color: {cls.BLACK};
                border: 1px solid {cls.BORDER_COLOR};
                gridline-color: {cls.BORDER_COLOR};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                selection-background-color: #BBDEFB;
                selection-color: {cls.BLACK};
            }}
            QTableWidget::item {{
                padding: 4px;
                border-bottom: 1px solid {cls.BORDER_COLOR};
            }}
            QTableWidget::item:selected {{
                background-color: #BBDEFB;
                color: {cls.BLACK};
            }}
            QHeaderView::section {{
                background-color: #E0E0E0;
                color: {cls.BLACK};
                padding: 6px;
                font-weight: bold;
                border: none;
                border-right: 1px solid {cls.BORDER_COLOR};
                border-bottom: 1px solid {cls.BORDER_COLOR};
            }}
            QHeaderView::section:checked {{
                background-color: #BBDEFB;
            }}
        """
    
    @classmethod
    def get_groupbox_style(cls):
        return f"""
            QGroupBox {{
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_SMALL};
                font-weight: bold;
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 4px;
                margin-top: 5px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: {cls.BLACK};
            }}
        """
    
    @classmethod
    def get_label_style(cls):
        return f"""
            QLabel {{
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                color: {cls.BLACK};
            }}
        """
    
    @classmethod
    def get_radiobutton_style(cls):
        return f"""
            QRadioButton {{
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                color: {cls.BLACK};
                spacing: 5px;
            }}
            QRadioButton::indicator {{
                width: 15px;
                height: 15px;
                border-radius: 7px;
                border: 1px solid {cls.BORDER_COLOR};
            }}
            QRadioButton::indicator:checked {{
                background-color: {cls.PRIMARY_COLOR};
                border: 2px solid {cls.WHITE};
                outline: 1px solid {cls.PRIMARY_COLOR};
            }}
            QRadioButton::indicator:unchecked {{
                background-color: {cls.WHITE};
            }}
            QRadioButton:disabled {{
                color: #9E9E9E;
            }}
        """
    
    @classmethod
    def get_checkbox_style(cls):
        return f"""
            QCheckBox {{
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                color: {cls.BLACK};
                spacing: 5px;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 3px;
            }}
            QCheckBox::indicator:checked {{
                background-color: {cls.PRIMARY_COLOR};
                border: 1px solid {cls.PRIMARY_COLOR};
                image: url(icons/check.png);
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {cls.WHITE};
            }}
            QCheckBox:disabled {{
                color: #9E9E9E;
            }}
        """
    
    @classmethod
    def get_scrollbar_style(cls):
        return f"""
            QScrollBar:vertical {{
                border: none;
                background: #F0F0F0;
                width: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #BDBDBD;
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
            QScrollBar:horizontal {{
                border: none;
                background: #F0F0F0;
                height: 10px;
                margin: 0px 0px 0px 0px;
            }}
            QScrollBar::handle:horizontal {{
                background: #BDBDBD;
                min-width: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
                width: 0px;
            }}
        """
    
    @classmethod
    def get_menubar_style(cls):
        return f"""
            QMenuBar {{  
                background-color: {cls.MENU_BG};
                color: {cls.MENU_TEXT};
                border-bottom: 1px solid {cls.BORDER_COLOR};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                padding: 2px;
            }}
            QMenuBar::item {{  
                background-color: transparent;
                padding: 4px 8px;
                margin: 0px 2px;
                border-radius: 4px;
            }}
            QMenuBar::item:selected {{  
                background-color: {cls.MENU_HOVER_BG};
                color: {cls.MENU_HOVER_TEXT};
            }}
            QMenuBar::item:pressed {{  
                background-color: {cls.PRIMARY_COLOR};
                color: {cls.WHITE};
            }}
        """

    @classmethod
    def get_menu_style(cls):
        return f"""
            QMenu {{  
                background-color: {cls.MENU_BG};
                color: {cls.MENU_TEXT};
                border: 1px solid {cls.BORDER_COLOR};
                border-radius: 4px;
                padding: 4px;
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
            }}
            QMenu::item {{  
                background-color: transparent;
                padding: 6px 24px 6px 8px;
                border-radius: 2px;
                margin: 2px 4px;
            }}
            QMenu::item:selected {{  
                background-color: {cls.MENU_HOVER_BG};
                color: {cls.MENU_HOVER_TEXT};
            }}
            QMenu::separator {{  
                height: 1px;
                background-color: {cls.BORDER_COLOR};
                margin: 4px 8px;
            }}
            QMenu::indicator {{  
                width: 16px;
                height: 16px;
                margin-left: 4px;
            }}
        """

    @classmethod
    def get_global_style(cls):
        """Return the complete global stylesheet for the application"""
        return f"""
            {cls.get_main_window_style()}
            {cls.get_button_style("default")}
            {cls.get_combobox_style()}
            {cls.get_lineedit_style()}
            {cls.get_dateedit_style()}
            {cls.get_table_style()}
            {cls.get_groupbox_style()}
            {cls.get_label_style()}
            {cls.get_radiobutton_style()}
            {cls.get_checkbox_style()}
            {cls.get_scrollbar_style()}
            {cls.get_menubar_style()}
            {cls.get_menu_style()}
        """
    
    # Special component styles
    @classmethod
    def get_save_button_style(cls):
        return f"""
            QPushButton {{
                background-color: #C8E6C9;
                color: black;
                border: 1px solid #81C784;
                border-radius: {cls.CONTROL_BORDER_RADIUS};
                padding: {cls.CONTROL_PADDING};
                height: {cls.CONTROL_HEIGHT};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #A5D6A7;
            }}
            QPushButton:pressed {{
                background-color: #81C784;
            }}
            QPushButton:disabled {{
                background-color: #E8F5E9;
                color: #9E9E9E;
            }}
        """
    
    @classmethod
    def get_cancel_button_style(cls):
        return f"""
            QPushButton {{
                background-color: #FFCDD2;
                color: black;
                border: 1px solid #E57373;
                border-radius: {cls.CONTROL_BORDER_RADIUS};
                padding: {cls.CONTROL_PADDING};
                height: {cls.CONTROL_HEIGHT};
                font-family: {cls.FONT_FAMILY};
                font-size: {cls.FONT_SIZE_MEDIUM};
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #EF9A9A;
            }}
            QPushButton:pressed {{
                background-color: #E57373;
            }}
            QPushButton:disabled {{
                background-color: #FFEBEE;
                color: #9E9E9E;
            }}
        """