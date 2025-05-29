from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QPushButton, QLabel

class WindowsManager(QObject):
    def __init__(self, app):
        super().__init__()
        # QApplication instance
        self.app = app
        # Install event filter on the application
        self.app.installEventFilter(self)
        # List of minimized windows
        self.minimized_windows = []
        # Horizontal offset for placing floating tabs properly
        self.needed_horizontal_offset = 0

    # Check for opened sub-windows
    def checkForOpenWindows(self, current_window):
        # Get all top-level windows
        top_level_windows = self.app.topLevelWindows()
        # Count open windows excluding current window
        open_windows = sum(1 for w in top_level_windows if w.isVisible() and w != current_window)
        if open_windows > 1:
            return True
        return False
            
    def checkIfWindowIsOpen(self, window_name):
        # Get all top-level windows
        open_windows = [w for w in self.app.topLevelWindows() if w.isVisible()]

        # Check if Groups window is already open
        for open_window in open_windows:
            if open_window.objectName() == window_name:
                return True
            
        for minimized_window in self.minimized_windows:
            fixed_window_name = window_name.replace('Window', '')
            if minimized_window.objectName() == fixed_window_name:
                return True
            
        return False
    
    def raiseWindow(self, window_name):
        # Get all open windows
        open_windows = [w for w in self.app.topLevelWindows() if w.isVisible()]

        for open_window in open_windows:
            if open_window.objectName() == window_name:
                open_window.raise_()
                open_window.show()

        for minimized_window in self.minimized_windows:
            fixed_window_name = window_name.replace('Window', '')
            if minimized_window.objectName() == fixed_window_name:
                self.restoreWindow(minimized_window, minimized_window.floating_tab)

    def createFloatingTab(self, window):
        # Create floating widget
        tab = QWidget()
        tab.setWindowFlags(Qt.Window | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        tab.setAttribute(Qt.WA_TranslucentBackground)
        
        # Position at left corner of screen
        screen = QApplication.desktop().screenGeometry()
        tab.move(10 + self.needed_horizontal_offset, screen.height() - 110) 
        
        # Create main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Create container widget for controls
        container = QWidget()
        container.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0;
                border-radius: 4px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QLabel {
                font-size: 14px;
                padding: 5px;
                font-weight: 500;
            }
            QPushButton {
                border: none;
                padding: 4px;
                font-size: 18px;
                min-width: 32px;
                min-height: 32px;
                font-family: 'Segoe UI', Arial, sans-serif;
            }
            QPushButton:hover {
                background-color: #f5f5f5;
            }
        """)
        container_layout = QHBoxLayout()
        container_layout.setContentsMargins(0, 0, 6, 8)  
        container_layout.setSpacing(2)  
        container.setLayout(container_layout)
        
        # Create icon label
        icon_label = QLabel()
        icon = window.windowIcon()
        icon_label.setPixmap(icon.pixmap(24, 24))  # Adjust size as needed
        
        # Add window name label
        name_label = QLabel(window.windowTitle())
        
        # Add minimize button to restore window
        restore_btn = QPushButton("☐")
        restore_btn.setFixedSize(32, 32)  # Increased button size
        restore_btn.clicked.connect(lambda: self.restoreWindow(window, tab))
        
        # Add close button
        close_btn = QPushButton("✕") 
        close_btn.setFixedSize(32, 32)  # Increased button size
        close_btn.clicked.connect(lambda: self.closeWindow(window, tab))
        
        # Add drag functionality
        def mousePressEvent(event):
            if event.button() == Qt.LeftButton:
                tab._drag_pos = event.globalPos() - tab.pos()
        
        def mouseMoveEvent(event):
            if hasattr(tab, '_drag_pos'):
                tab.move(event.globalPos() - tab._drag_pos)
                
        def mouseReleaseEvent(event):
            if hasattr(tab, '_drag_pos'):
                del tab._drag_pos
        
        container.mousePressEvent = mousePressEvent
        container.mouseMoveEvent = mouseMoveEvent
        container.mouseReleaseEvent = mouseReleaseEvent
        
        # Add widgets to container
        container_layout.addWidget(icon_label, 0, Qt.AlignVCenter)
        container_layout.addWidget(name_label)
        container_layout.addWidget(restore_btn)
        container_layout.addWidget(close_btn)
        
        # Add container to main layout
        layout.addWidget(container)
        
        tab.setLayout(layout)
        tab.show()
        
        # Store reference to floating tab in the window
        window.floating_tab = tab

        # Add floating tab to list
        self.minimized_windows.append(window)

        # Increase horizontal offset for next floating tab
        self.needed_horizontal_offset += tab.width() + 10
        
        # Install event filter to handle window state changes
        window.installEventFilter(self)
        
    def eventFilter(self, source, event):
        if event.type() == event.WindowStateChange:
            if isinstance(source, QWidget) and source.windowState() & Qt.WindowMinimized and source.windowTitle() != "Epsilon":
                source.hide()
                self.createFloatingTab(source)
                return True
        return super().eventFilter(source, event)
    
    def restoreWindow(self, window, tab):
        window.setWindowState(Qt.WindowMaximized)
        window.show()
        tab.close()
        self.minimized_windows.remove(window)
        self.fixFloatingTabsPlacement(tab.x(), tab.width())

    def closeWindow(self, window, tab):
        window.close()
        tab.close()
        self.minimized_windows.remove(window)
        self.fixFloatingTabsPlacement(tab.x(), tab.width())

    def fixFloatingTabsPlacement(self, tab_x, tab_width):
        for window in self.minimized_windows:
            if window.floating_tab.x() > tab_x:
                window.floating_tab.move(window.floating_tab.x() - tab_width - 10, window.floating_tab.y())
        
        self.needed_horizontal_offset -= tab_width + 10

