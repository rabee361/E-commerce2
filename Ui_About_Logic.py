from PyQt5.QtCore import Qt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from Ui_about import Ui_About
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_About_Logic(object):
    def __init__(self):
        super().__init__()
        self.ui = Ui_About()
        self.translator = QTranslator() 
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_about = QDialog()
        window_about.setWindowFlags(Qt.Window | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint)
        self.ui.setupUi(window_about)
        window_about.setWindowIcon(QIcon('icons/help.png'))
        self.initialize()
        self.language_manager.load_translated_ui(self.ui, window_about) 
        window_about.exec()

    def initialize(self):
        self.ui.about_version.setText("Version 0.Pre-Release_test-version 1.1")
        self.ui.about_label.setText("This is an internal version. not intended for end usage.")
        self.ui.about_label_2.setText("This trail version is temporarily activated for a limited slot of time.")