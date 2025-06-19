from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QRect
from PyQt5.QtGui import QPainter, QFont, QColor, QIcon


class DigitalDisplay(QWidget):
    def __init__(self, display_type='time', parent=None):
        super().__init__(parent)
        self.display_type = display_type
        self.showUi()

    def showUi(self):
        # Create horizontal layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)
        
        # Set fixed size for the widget
        self.setFixedSize(280, 50)
        
        # Set background color to white
        self.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                border-radius: 5px;
                padding: 0px;
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
        
        # Calculate dimensions
        total_width = self.width()
        total_height = self.height()
        icon_container_width = total_height  # Square container
        text_width = total_width - icon_container_width
        
        # Draw red background for icon container (right side)
        painter.fillRect(total_width - icon_container_width, 0, 
                         icon_container_width, total_height, 
                         QColor(220, 50, 50))  # Red background
        
        # Configure font and color for text
        font = QFont('Arial', 16, QFont.Bold)
        painter.setFont(font)
        painter.setPen(QColor(0, 0, 0))
        
        # Draw icon in the red square
        icon_size = int(icon_container_width * 0.6)
        icon_x = total_width - icon_container_width + (icon_container_width - icon_size) // 2
        icon_y = (total_height - icon_size) // 2
        
        if self.display_type == 'time':
            icon = QIcon("icons/clock.png")
            display_str = self.current_time.toString('hh:mm:ss AP')
        else:  # date
            icon = QIcon("icons/calendar_year.png")
            # Add day of week to the date display
            day_of_week = self.current_date.toString('dddd')
            display_str = f"{day_of_week}\n{self.current_date.toString('yyyy-MM-dd')}"
            
        icon.paint(painter, icon_x, icon_y, icon_size, icon_size)
        
        # Draw text in the remaining space (left side)
        text_rect = QRect(10, 0, text_width - 20, total_height)
        
        # Align text differently based on type
        if self.display_type == 'time':
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter, display_str)
        else:
            # Use smaller font for date with day of week
            font.setPointSize(14)
            painter.setFont(font)
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
