import os
import win32api
from PyQt5.QtCore import Qt
from Ui_Media import Ui_Media
from PyQt5.QtGui import QPixmap
from FileManager import FileManager
from DatabaseOperations import DatabaseOperations
from PyQt5.QtWidgets import QDialog, QTableWidgetItem
from LanguageManager import LanguageManager
from PyQt5.QtCore import QTranslator


class Ui_Media_Logic(QDialog):
    def __init__(self, sql_connector):
        super().__init__()
        self.filemanager = FileManager()
        self.sql_connector = sql_connector
        self.database_operations = DatabaseOperations(self.sql_connector)
        self.translator = QTranslator()
        self.language_manager = LanguageManager(self.translator)
        
        # Set up the UI
        self.ui = Ui_Media()
        self.ui.setupUi(self)
        self.language_manager.load_translated_ui(self.ui, self)
        # Connect buttons
        self.ui.select_image_btn.clicked.connect(self.selectImage)
        self.ui.save_btn.clicked.connect(self.saveImage)
        
        # Initialize image data
        self.image_data = None
        self.image_path = None
        
        # Set up table
        self.setupTable()
        
        # Connect table selection
        self.ui.media_table.itemSelectionChanged.connect(self.onTableSelectionChanged)
        self.ui.delete_btn.clicked.connect(self.deleteImage)

    def setupTable(self):
        # Set table properties
        self.ui.media_table.setColumnCount(2)
        self.ui.media_table.setHorizontalHeaderLabels([f'{self.language_manager.translate("ID")}', f'{self.language_manager.translate("NAME")}'])
        self.ui.media_table.horizontalHeader().setStretchLastSection(True)
        
        # Load media data
        self.loadMediaData()

    def loadMediaData(self):
        try:
            # Fetch all media from database
            media_list = self.database_operations.fetchAllMedia()
            
            # Clear existing rows
            self.ui.media_table.setRowCount(0)
            
            # Add media to table
            for media in media_list:
                row_position = self.ui.media_table.rowCount()
                self.ui.media_table.insertRow(row_position)
                
                # Add ID and name
                self.ui.media_table.setItem(row_position, 0, QTableWidgetItem(str(media['id'])))
                self.ui.media_table.setItem(row_position, 1, QTableWidgetItem(media['name']))
                
        except Exception as e:
            win32api.MessageBox(0, f'{self.language_manager.translate("LOADING_MEDIA_ERROR")}: {str(e)}', self.language_manager.translate("ERROR"))
            print(f"Error loading media: {str(e)}")

    def onTableSelectionChanged(self):
        selected_rows = self.ui.media_table.selectedItems()
        if selected_rows:
            # Get media name from selected row
            media_name = self.ui.media_table.item(selected_rows[0].row(), 1).text()
            
            try:
                # Fetch media data
                media = self.database_operations.fetchMedia(media_name)
                if media and media['file']:
                    # Convert binary data to QPixmap
                    image_data = media['file']
                    pixmap = QPixmap()
                    pixmap.loadFromData(image_data)
                    
                    # Display in preview label
                    self.ui.image_preview_label.setPixmap(
                        pixmap.scaled(
                            self.ui.image_preview_label.size(),
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                    )
                    
                    # Update name input
                    self.ui.media_name_input.setText(media_name)
                    
                    # Store image data
                    self.image_data = image_data
                    
            except Exception as e:
                win32api.MessageBox(0, f'{self.language_manager.translate("LOADING_IMAGE_ERROR")}: {str(e)}', self.language_manager.translate("ERROR"))
                print(f"Error loading image: {str(e)}")

    def showUi(self):
        self.show()
        self.exec_()

    def selectImage(self):
        # Use FileManager to open image file
        self.image_path = self.filemanager.openFile("jpg")
        
        if not self.image_path:
            # Try png if jpg failed
            self.image_path = self.filemanager.openFile("png")
            
        if self.image_path:
            # Check file size (limit to 2MB)
            file_size = os.path.getsize(self.image_path)
            if file_size > 2 * 1024 * 1024:  # 2MB in bytes
                win32api.MessageBox(0, self.language_manager.translate("ALERT_IMAGE_SIZE"), self.language_manager.translate("ERROR"))
                self.image_path = None
                return
                
            # Read the image file
            with open(self.image_path, 'rb') as file:
                self.image_data = file.read()
                
            # Display preview
            pixmap = QPixmap(self.image_path)
            self.ui.image_preview_label.setPixmap(
                pixmap.scaled(
                    self.ui.image_preview_label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
            )
            
            # Enable save button
            self.ui.save_btn.setEnabled(True)

    def saveImage(self):
        if self.image_data:
            media_name = self.ui.media_name_input.text().strip()
            if not media_name:
                win32api.MessageBox(0, self.language_manager.translate("NAME_FIELD_MUST_BE_ENTERED"), self.language_manager.translate("ERROR"))
                return
            
            try:
                # First check if media name already exists
                existing_media = self.database_operations.fetchMedia(media_name)
                if existing_media:
                    win32api.MessageBox(0, self.language_manager.translate("NAME_ALREADY_EXISTS_ERROR"), self.language_manager.translate("ERROR"))
                    return

                # Save image to database using parameterized query
                self.database_operations.addMedia(
                    name=media_name,
                    file=self.image_data
                )
                
                # Refresh the table
                self.loadMediaData()
                
                win32api.MessageBox(0, self.language_manager.translate("SAVED_SUCCESSFULLY"), self.language_manager.translate("SUCCESS"))
                
            except Exception as e:
                win32api.MessageBox(0, f'{self.language_manager.translate("SAVING_IMAGE_ERROR")}: {str(e)}', self.language_manager.translate("ERROR"))
                print(f"Error saving image: {str(e)}")  # For debugging
        else:
            win32api.MessageBox(0, self.language_manager.translate("IMAGE_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))

    def deleteImage(self):
        selected_items = self.ui.media_table.selectedItems()
        if selected_items:
            # Get the media name from the selected row
            media_name = self.ui.media_table.item(selected_items[0].row(), 1).text()
            
            try:
                # Delete from database
                self.database_operations.deleteMedia(media_name)
                
                # Refresh the table
                self.loadMediaData()
                
                # Clear the preview
                self.ui.image_preview_label.clear()
                self.ui.image_preview_label.setText(self.language_manager.translate("PREVIEW_IMAGE"))
                
                # Clear the name input
                self.ui.media_name_input.clear()
                
                # Clear stored image data
                self.image_data = None
                self.image_path = None
                
                # Disable save button
                self.ui.save_btn.setEnabled(False)
                
                win32api.MessageBox(0, self.language_manager.translate("DELETED_SUCCESSFULLY"), self.language_manager.translate("SUCCESS"))
                
            except Exception as e:
                win32api.MessageBox(0, f'{self.language_manager.translate("DELETE_ERROR")}: {str(e)}', self.language_manager.translate("ERROR"))
                print(f"Error deleting image: {str(e)}")
        else:
            win32api.MessageBox(0, self.language_manager.translate("IMAGE_MUST_BE_SELECTED"), self.language_manager.translate("ALERT"))