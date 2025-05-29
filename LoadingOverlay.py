from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QMovie

class LoadingOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Set window flags to stay on top
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # Create layout
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)  # Remove any margins
        
        # Create label for the loading GIF
        self.loading_label = QLabel()
        self.movie = QMovie("assets/loading.gif")  # Make sure to have this GIF file
        self.loading_label.setMovie(self.movie)
        self.loading_label.setAlignment(Qt.AlignCenter)
        
        # Add label to layout
        layout.addWidget(self.loading_label)
        layout.setAlignment(Qt.AlignCenter)
        self.setLayout(layout)
        
    def showEvent(self, event):
        # Start the movie when widget is shown
        self.movie.start()
        super().showEvent(event)
        
    def hideEvent(self, event):
        # Stop the movie when widget is hidden
        self.movie.stop()
        super().hideEvent(event) 