import sys
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, QTime, QDate
from PyQt5.QtGui import QPainter, QFont, QColor, QIcon
from PyQt5.QtCore import Qt

class DigitalDisplay(QWidget):
    def __init__(self, display_type='time', parent=None):
        super().__init__(parent)
        self.display_type = display_type
        self.showUi()

    def showUi(self):
        # Create horizontal layout
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Set fixed size for the widget
        self.setFixedSize(280, 50) # Increased width to accommodate icon
        
        # Set background color to white and black text
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                width: 100%;
                border-radius: 5px;
                padding: 2px;
                color: #000000;
                margin: 5px;
            }
        """)
        
        # Ensure the widget is visible
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setVisible(True)
        
        # Start timer to update display
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateDisplay)
        self.timer.start(1000)  # Update every second
        
        self.current_time = QTime.currentTime()
        self.current_date = QDate.currentDate()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Configure font and color - black text
        font = QFont('Arial', 18, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        
        # Draw icon
        icon_size = 24
        icon_x = 10
        icon_y = (self.height() - icon_size) // 2
        
        if self.display_type == 'time':
            icon = QIcon("icons/clock.png")
            display_str = self.current_time.toString('hh:mm:ss AP')
        else:  # date
            icon = QIcon("icons/calendar_year.png")
            display_str = self.current_date.toString('yyyy-MM-dd')
            
        icon.paint(painter, icon_x, icon_y, icon_size, icon_size)
        
        # Draw text with offset to accommodate icon
        text_rect = event.rect()
        text_rect.setLeft(icon_x + icon_size + 10)  # Offset text to right of icon
        painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, display_str)

    def updateDisplay(self):
        if self.display_type == 'time':
            self.current_time = QTime.currentTime()
        else:
            self.current_date = QDate.currentDate()
        self.update()


# For backwards compatibility  
class DigitalClock(DigitalDisplay):
    def __init__(self, parent=None):
        super().__init__(display_type='time', parent=parent)