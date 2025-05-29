from PyQt5.QtCore import QObject, Qt
from PyQt5.QtGui import QDoubleValidator
from PyQt5.QtWidgets import QDialog, QApplication
from Ui_Calculator import Ui_Calculator
import math
import sys

class Ui_Calculator_Logic(QDialog):
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Ui_Calculator_Logic, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        if not hasattr(self, '_initialized') or not self._initialized:
            super().__init__()
            self.calculator_result = ''
            self.memory = 0
            self.dialog = None
            self.ui = Ui_Calculator()
            self.ui.setupUi(self)
            self._initialized = True
        
    def showUi(self):
        self.show()
        self.initialize()
        self.exec_()

        
    def initialize(self):
        # Set up input validation for numbers
        self.ui.display.setValidator(QDoubleValidator())
        
        # Connect all calculator buttons
        buttons = [
            self.ui.btn0, self.ui.btn1, self.ui.btn2, self.ui.btn3, 
            self.ui.btn4, self.ui.btn5, self.ui.btn6, self.ui.btn7,
            self.ui.btn8, self.ui.btn9, self.ui.btn00,
            self.ui.btnPlus, self.ui.btnMinus, self.ui.btnMultiply, 
            self.ui.btnDivide, self.ui.btnEquals, self.ui.btnDot,
            self.ui.btnCls, self.ui.btnBck, self.ui.btnRoot,
            self.ui.add_memory, self.ui.subtract_memory,
            self.ui.clear_memory, self.ui.show_memory
        ]
        
        for button in buttons:
            if button.text() == '':
                continue
            button.clicked.connect(self.calculator_btn_clicked)

        # Set up keyboard shortcuts
        self.key_mapping = {
            Qt.Key_0: self.ui.btn0,
            Qt.Key_1: self.ui.btn1,
            Qt.Key_2: self.ui.btn2,
            Qt.Key_3: self.ui.btn3,
            Qt.Key_4: self.ui.btn4,
            Qt.Key_5: self.ui.btn5,
            Qt.Key_6: self.ui.btn6,
            Qt.Key_7: self.ui.btn7,
            Qt.Key_8: self.ui.btn8,
            Qt.Key_9: self.ui.btn9,
            Qt.Key_Plus: self.ui.btnPlus,
            Qt.Key_Minus: self.ui.btnMinus,
            Qt.Key_Asterisk: self.ui.btnMultiply,
            Qt.Key_Slash: self.ui.btnDivide,
            Qt.Key_Equal: self.ui.btnEquals,
            Qt.Key_Enter: self.ui.btnEquals,
            Qt.Key_Return: self.ui.btnEquals,
            Qt.Key_Period: self.ui.btnDot,
            Qt.Key_Backspace: self.ui.btnBck,
        }

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            key = event.key()
            if key in self.key_mapping:
                self.key_mapping[key].click()
                return True
        return super().eventFilter(obj, event)

    def calculator_btn_clicked(self):
        button_text = self.sender().text()
        try:
            if button_text == 'AC':
                self.calculator_result = ''
                self.ui.display.setText('0')
            elif button_text == 'C':
                self.calculator_result = self.calculator_result[:-1]
                self.ui.display.setText(self.calculator_result if self.calculator_result else '0')
            elif button_text == 'M+':
                self.memory = self.memory + float(self.calculator_result)
                print("M+ "+self.calculator_result)
                print(self.memory)
            elif button_text == 'M-':
                self.memory = self.memory - float(self.calculator_result)
                print("M- "+self.calculator_result)
                print(self.memory)
            elif button_text == 'MC':
                self.memory = 0
                print(self.memory)
            elif button_text == 'MS':
                self.ui.display.setText(str(self.memory))
                print(self.memory)
            elif button_text == '√ ':
                self.calculator_result = str(round(math.sqrt(float(self.calculator_result)), 2))
                self.ui.display.setText(self.calculator_result)
            elif button_text == '=':
                if u"\N{DIVISION SIGN}" in self.calculator_result:
                    self.calculator_result = self.calculator_result.replace(u"\N{DIVISION SIGN}", '/')
                elif u"\N{MULTIPLICATION SIGN}" in self.calculator_result:
                    self.calculator_result = self.calculator_result.replace(u"\N{MULTIPLICATION SIGN}", "*")
                self.calculator_result = str(eval(self.calculator_result))
                self.ui.display.setText(self.calculator_result)
            else:
                self.calculator_result += button_text
                self.ui.display.setText(self.calculator_result)
        except Exception as e:
            self.calculator_result = 'Error!'
            self.ui.display.setText(self.calculator_result)

