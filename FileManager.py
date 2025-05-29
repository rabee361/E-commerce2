import json

import win32api
from PyQt5.QtWidgets import (QMainWindow, QFileDialog)

class FileManager(QMainWindow):
    file_name=''
    def __init__(self):
        super().__init__()
        print("File Manager class initiaited.")

    def createEmptyFile(self,extension):
        name = QFileDialog.getSaveFileName(self, 'Save File',"","."+extension)[0]+"."+extension
        if name != '.'+extension:
            file = open(name, 'w')
            print("Created empty file: "+name)
            file.close()
            self.file_name=file.name
            return file.name
        else:
            return ""

    def openFile(self,extension):
        name = QFileDialog.getOpenFileName(self, 'Open File',"","*."+extension)[0]
        if name.endswith("."+extension):
            try:
                file = open(name, 'a+')
                print("Open file: " + name)
                file.close()
                self.file_name=file.name
                return file.name
            except:
                win32api.MessageBox(0,'خطأ في الملف! قد يكون الملف تالف أو مفتوح في تطبيق آخر','خطأ')
                return ""
        else:
            return ""

    def getFolderPath(self):
        folder_path = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        return folder_path

    def fileExists(self, file):
        if file.is_file():
            return True
        else:
            return False

    def readJsonFile(self, file):
        json_file = open(file)
        json_data = json.load(json_file)
        return json_data




