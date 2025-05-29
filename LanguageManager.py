import os
import locale
from PyQt5.QtCore import QCoreApplication
import json
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import Qt


class LanguageManager():
    """A class that manages language settings and translations for a Qt application.
    Handles both UI translations (.qm files) and string translations (from JSON).
    Supports Right-to-Left (RTL) languages and persists language preferences.
    """

    _current_language = 'en'  # Class-level variable to store the current language code

    def __init__(self, translator='') -> None:
        """Initialize the LanguageManager.
        
        Args:
            translator: Qt translator object for UI translations
        """
        self.translator = translator  # Qt translator for UI files
        self.current_language = "en"  # Default language
        self.translations = {}  # Dictionary to store string translations
        self.load_translations()  # Load string translations from JSON
        self.load_default_language()  # Load saved language preference

    @classmethod
    def set_default_language(cls, language_code):
        """Save the preferred language code to a configuration file.
        The file is stored in the OS-specific application data directory.
        
        Args:
            language_code (str): Two-letter language code (e.g., 'en', 'ar')
        """

        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        # Create 'epsilon' directory if it doesn't exist
        if not os.path.exists(epsilon_dir):
            os.makedirs(epsilon_dir)

        language_file = os.path.join(epsilon_dir, 'language.inf')

        with open(language_file, 'w') as f:
            f.write(f"[Language]\ndefault_language={language_code}")

        cls._current_language = language_code

    @classmethod
    def load_default_language(cls):
        """Load the preferred language from the configuration file.
        If no configuration exists, defaults to 'en' (English).
        
        Returns:
            str: The loaded language code
        """
        """Load default language from language.inf file"""
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        language_file = os.path.join(epsilon_dir, 'language.inf')
        try:
            with open(language_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('default_language='):
                        current_language = line.split('=')[1].strip()
                        break
                else:
                    current_language = 'en'
        except:
            current_language = 'en'

        cls._current_language = current_language
        return current_language

    @classmethod
    def get_current_language(cls):
        """Get the current language code. If not set, uses system locale.
        
        Returns:
            str: Two-letter language code (e.g., 'en', 'ar')
        """
        if cls._current_language is None:   # if no language.inf file or no current_language setting, use system language
            system_locale = locale.getdefaultlocale()[0]
            cls._current_language = system_locale[:2].lower()
        return cls._current_language

    def load_translations(self):
        """Load string translations from the JSON file.
        The JSON file should be structured as:
        {
            "en": {"key": "value"},
            "ar": {"key": "value"}
        }
        """
        json_path = os.path.join("translations", "string_translations.json")
        with open(json_path, 'r', encoding='utf-8') as f:
            self.translations = json.load(f)

    def translate(self, key):
        """Get the translation for a given key in the current language.
        
        Args:
            key (str): The translation key to look up
            
        Returns:
            str: Translated text if found, otherwise returns the key itself
        """
        current_language = self.get_current_language()
        if current_language in self.translations:
            lang_dict = self.translations[current_language]
            if key in lang_dict:
                return lang_dict[key]
        return key  # Fallback to key if translation not found

    def load_translated_ui(self, ui, window):
        """Load and apply UI translations for a window.
        Also handles Right-to-Left (RTL) layout for appropriate languages.
        
        Args:
            ui: The UI class instance to translate
            window: The QWidget window to apply translations to
            
        Returns:
            QTranslator: The translator object with loaded translations
        """
        ui_filename = ui.__class__.__name__
        qm_file = "translations/" + str(LanguageManager._current_language) + "/" + ui_filename + "_" + str(LanguageManager._current_language) + ".qm"
        self.translator.load(qm_file)

        QCoreApplication.installTranslator(self.translator)
        # Set layout direction based on language
        if LanguageManager._current_language in ['ar', 'he', 'fa', 'ur']:
            window.setLayoutDirection(Qt.RightToLeft)
            # Apply RTL layout to all child widgets
            for child in window.findChildren(QWidget):
                child.setLayoutDirection(Qt.RightToLeft)
        else:
            window.setLayoutDirection(Qt.LeftToRight)
            # Apply LTR layout to all child widgets
            for child in window.findChildren(QWidget):
                child.setLayoutDirection(Qt.LeftToRight)

        ui.retranslateUi(window)
        return self.translator
