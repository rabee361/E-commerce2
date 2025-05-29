from PyQt5.QtWidgets import QProgressDialog 
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtWidgets import QApplication


class ProgressBarWorker(QThread):
    progress_signal = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.is_running = False
        
    def run(self):
        self.is_running = True
        # Start at 0%
        self.progress_signal.emit(0)
        QApplication.processEvents()
        
        # Emit progress updates
        for i in range(0, 101, 10):
            if not self.is_running:
                break
            self.progress_signal.emit(i)
            self.msleep(100)  # Short delay between updates
            QApplication.processEvents()
            
        self.finished.emit()


class ProgressBar:
    def __init__(self):
        self.progress = QProgressDialog("جاري التحميل...", None, 0, 100)
        self.progress.setWindowTitle("Loading")
        
        # Set window flags to stay on top and be frameless
        self.progress.setWindowFlags(
            Qt.Dialog | 
            Qt.FramelessWindowHint | 
            Qt.WindowStaysOnTopHint |
            Qt.Tool |
            Qt.X11BypassWindowManagerHint  # Added to ensure it stays on top
        )
        
        # Make it modal and disable parent window
        self.progress.setWindowModality(Qt.ApplicationModal)
        self.progress.setAutoClose(True)
        self.progress.setCancelButton(None)
        self.progress.setMinimumDuration(0)
        self.progress.setFixedSize(300, 100)
        
        # Enhanced style for loading bar
        self.progress.setStyleSheet("""
            QProgressDialog {
                border: 1px solid #c0c0c0;
                background-color: white;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
            }
            QProgressBar {
                border: 1px solid #c0c0c0;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                width: 10px;
                margin: 0.5px;
            }
            QLabel {
                color: #000000;
                font-size: 12px;
                padding: 5px;
            }
        """)
        
        # Initialize worker thread
        self.worker = ProgressBarWorker()
        self.worker.progress_signal.connect(self.progress.setValue)
        self.worker.finished.connect(self.progress.close)

    def show(self):
        # Center on screen
        screenGeometry = QApplication.desktop().screenGeometry()
        x = (screenGeometry.width() - self.progress.width()) // 2
        y = (screenGeometry.height() - self.progress.height()) // 2
        self.progress.move(x, y)
        self.progress.show()
        self.progress.raise_()
        QApplication.processEvents()

    def close(self):
        self.worker.is_running = False
        self.progress.close()
        
    def start(self):
        self.show()
        self.worker.start()
        QApplication.processEvents()

    def stop(self):
        self.worker.is_running = False
        self.worker.quit()
        self.worker.wait()
        self.close()




