from PyQt5.QtWidgets import QDialog

from UiStyles import UiStyles
from Ui_Select_Language import Ui_SelectLanguage
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator

class Ui_Select_Language_Logic(QDialog, UiStyles):
    def __init__(self):
        super().__init__()
        self.ui = Ui_SelectLanguage()
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)


    def showUi(self):
        window_select_language = QDialog()
        self.ui.setupUi(window_select_language)
        self.language_manager.load_translated_ui(self.ui, window_select_language)
        self.initialize(window_select_language)
        window_select_language.exec()

    def initialize(self, window):
        self.fetchLanguages()
        self.fetchCurrentLanguage()
        self.ui.save_btn.clicked.connect(lambda: self.saveLanguage(window))

    def fetchCurrentLanguage(self):
        current_language = self.language_manager.get_current_language()
        self.ui.language_combobox.setCurrentIndex(self.ui.language_combobox.findData(current_language))

    def saveLanguage(self, window):
        language = self.ui.language_combobox.currentData()
        self.language_manager.set_default_language(language)
        window.accept()

    def fetchLanguages(self):
        self.ui.language_combobox.addItem("English", "en")
        self.ui.language_combobox.addItem("عربي", "ar")







