import os
import subprocess
from pathlib import Path

# TranslationGenerator is a utility class for managing Qt UI translations
# It handles the generation of translation files (.ts) and compiled message files (.qm)
# for Qt-based user interfaces across multiple languages
class TranslationGenerator:
    def __init__(self, ui_files=None, languages=None):
        # Initialize with a list of Qt UI files (.ui) to process
        self.ui_files = ui_files or []  # List of UI file paths
        # Set supported languages, defaults to English and Arabic
        self.languages = languages or ['en', 'ar']  # Default languages
        
    def find_ui_files(self):
        """Return the list of provided UI files"""
        return [Path(file) for file in self.ui_files]
    
    def generate_translations(self, command):
        """Main method to generate translation files using Qt tools.
        Supports two commands:
        - 'pylupdate5': Extracts translatable strings from UI files into .ts files
        - 'lrelease': Compiles .ts files into binary .qm files used by the application
        
        Args:
            command (str): Either 'pylupdate5' or 'lrelease'
        """
        ui_files = self.find_ui_files()
        if not ui_files:
            print("No UI files provided!")
            return
        
        for ui_file in ui_files:
            base_name = ui_file.stem  # Get filename without extension
            
            for lang in self.languages:
                # Create translation directory if it doesn't exist
                trans_dir = f'translations/{lang}'
                os.makedirs(trans_dir, exist_ok=True)
                
                ts_file = f'{trans_dir}/{base_name}_{lang}.ts'
                qm_file = f'{trans_dir}/{base_name}_{lang}.qm'
                
                if command == 'pylupdate5':
                    # Run pylupdate5
                    print(f"\nProcessing {ui_file} for {lang}...")
                    pylupdate_cmd = ['pylupdate5', '-verbose', str(ui_file), '-ts', ts_file]
                    try:
                        result = subprocess.run(pylupdate_cmd, capture_output=True, text=True)
                        print(result.stdout)
                        if result.stderr:
                            print("Errors:", result.stderr)
                    except Exception as e:
                        print(f"Error running pylupdate5: {e}")
                        continue
                
                if command == 'lrelease':
                    # Run lrelease
                    lrelease_cmd = ['lrelease', ts_file, '-qm', qm_file]
                    try:
                        result = subprocess.run(lrelease_cmd, capture_output=True, text=True)
                        print(result.stdout)
                        if result.stderr:
                            print("Errors:", result.stderr)
                    except Exception as e:
                        print(f"Error running lrelease: {e}")

def main():
    # Example usage of the TranslationGenerator
    # Initialize with a UI file and target language
    generator = TranslationGenerator(
        ui_files=['.ui'],  # List of Qt UI files to process
        languages=['en']  # Target languages for translation
    )
    # Pass command: 'pylupdate5', 'lrelease'
    generator.generate_translations('pylupdate5')

if __name__ == '__main__':
    main()