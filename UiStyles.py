from BlurWindow.blurWindow import blur
from PyQt5.QtCore import Qt


class UiStyles:
    def __int__(self):
        pass

    def makeItBlurry(self, window):
        window.setAttribute(Qt.WA_TranslucentBackground)
        hWnd = window.winId()
        blur(hWnd)
        window.setStyleSheet("background-color: rgba(255, 255, 255, 0.5)")
        window.setStyleSheet(" QPushButton {\n"
        "        background-color: red;\n"
        "        color: white;\n"
        "        border-radius: 4px;\n"
        "        padding: 8px 16px;\n"
        "    }\n"
        "    QPushButton:hover {\n"
        "        background-color: #1565C0;\n"
        "    }\n"
        "    QPushButton:pressed {\n"
        "        background-color: #0D47A1;\n"
        "    }")
