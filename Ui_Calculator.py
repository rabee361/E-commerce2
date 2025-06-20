# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_Calculator.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Calculator(object):
    def setupUi(self, Calculator):
        Calculator.setObjectName("Calculator")
        Calculator.resize(350, 400)
        Calculator.setMinimumSize(QtCore.QSize(350, 400))
        Calculator.setMaximumSize(QtCore.QSize(350, 400))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.xpm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        Calculator.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(Calculator)
        self.gridLayout.setObjectName("gridLayout")
        self.display = QtWidgets.QLineEdit(Calculator)
        self.display.setMinimumSize(QtCore.QSize(0, 75))
        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(-1)
        font.setBold(True)
        font.setWeight(75)
        self.display.setFont(font)
        self.display.setStyleSheet("QLineEdit {\n"
"    font-family: \"Segoe UI\";\n"
"    font-size: 30px;\n"
"    font-weight: bold;\n"
"    color: #000000; /* DodgerBlue */\n"
"    background-color:#F0F0F0;\n"
"    border-radius: 10px;\n"
"    padding: 5px;\n"
"    text-align: center;\n"
"}")
        self.display.setMaxLength(15)
        self.display.setAlignment(QtCore.Qt.AlignRight)
        self.display.setObjectName("display")
        self.gridLayout.addWidget(self.display, 0, 0, 1, 1)
        self.buttonGrid = QtWidgets.QGridLayout()
        self.buttonGrid.setSpacing(5)
        self.buttonGrid.setObjectName("buttonGrid")
        self.btn0 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn0.sizePolicy().hasHeightForWidth())
        self.btn0.setSizePolicy(sizePolicy)
        self.btn0.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn0.setFont(font)
        self.btn0.setObjectName("btn0")
        self.buttonGrid.addWidget(self.btn0, 7, 0, 1, 1)
        self.btnMultiply = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnMultiply.sizePolicy().hasHeightForWidth())
        self.btnMultiply.setSizePolicy(sizePolicy)
        self.btnMultiply.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnMultiply.setFont(font)
        self.btnMultiply.setObjectName("btnMultiply")
        self.buttonGrid.addWidget(self.btnMultiply, 4, 3, 1, 1)
        self.btn8 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn8.sizePolicy().hasHeightForWidth())
        self.btn8.setSizePolicy(sizePolicy)
        self.btn8.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn8.setFont(font)
        self.btn8.setObjectName("btn8")
        self.buttonGrid.addWidget(self.btn8, 4, 1, 1, 1)
        self.btnRoot = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnRoot.sizePolicy().hasHeightForWidth())
        self.btnRoot.setSizePolicy(sizePolicy)
        self.btnRoot.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        font.setBold(True)
        font.setWeight(75)
        self.btnRoot.setFont(font)
        self.btnRoot.setObjectName("btnRoot")
        self.buttonGrid.addWidget(self.btnRoot, 2, 2, 1, 1)
        self.btnDot = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDot.sizePolicy().hasHeightForWidth())
        self.btnDot.setSizePolicy(sizePolicy)
        self.btnDot.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnDot.setFont(font)
        self.btnDot.setObjectName("btnDot")
        self.buttonGrid.addWidget(self.btnDot, 7, 2, 1, 1)
        self.add_memory = QtWidgets.QPushButton(Calculator)
        self.add_memory.setObjectName("add_memory")
        self.buttonGrid.addWidget(self.add_memory, 1, 1, 1, 1)
        self.btn3 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn3.sizePolicy().hasHeightForWidth())
        self.btn3.setSizePolicy(sizePolicy)
        self.btn3.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn3.setFont(font)
        self.btn3.setObjectName("btn3")
        self.buttonGrid.addWidget(self.btn3, 6, 2, 1, 1)
        self.show_memory = QtWidgets.QPushButton(Calculator)
        self.show_memory.setObjectName("show_memory")
        self.buttonGrid.addWidget(self.show_memory, 1, 3, 1, 1)
        self.btn7 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn7.sizePolicy().hasHeightForWidth())
        self.btn7.setSizePolicy(sizePolicy)
        self.btn7.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn7.setFont(font)
        self.btn7.setObjectName("btn7")
        self.buttonGrid.addWidget(self.btn7, 4, 0, 1, 1)
        self.btnDivide = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnDivide.sizePolicy().hasHeightForWidth())
        self.btnDivide.setSizePolicy(sizePolicy)
        self.btnDivide.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnDivide.setFont(font)
        self.btnDivide.setObjectName("btnDivide")
        self.buttonGrid.addWidget(self.btnDivide, 2, 3, 1, 1)
        self.btn6 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn6.sizePolicy().hasHeightForWidth())
        self.btn6.setSizePolicy(sizePolicy)
        self.btn6.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn6.setFont(font)
        self.btn6.setObjectName("btn6")
        self.buttonGrid.addWidget(self.btn6, 5, 2, 1, 1)
        self.btn00 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn00.sizePolicy().hasHeightForWidth())
        self.btn00.setSizePolicy(sizePolicy)
        self.btn00.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn00.setFont(font)
        self.btn00.setObjectName("btn00")
        self.buttonGrid.addWidget(self.btn00, 7, 1, 1, 1)
        self.btn4 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn4.sizePolicy().hasHeightForWidth())
        self.btn4.setSizePolicy(sizePolicy)
        self.btn4.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn4.setFont(font)
        self.btn4.setObjectName("btn4")
        self.buttonGrid.addWidget(self.btn4, 5, 0, 1, 1)
        self.btnPlus = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnPlus.sizePolicy().hasHeightForWidth())
        self.btnPlus.setSizePolicy(sizePolicy)
        self.btnPlus.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnPlus.setFont(font)
        self.btnPlus.setObjectName("btnPlus")
        self.buttonGrid.addWidget(self.btnPlus, 6, 3, 1, 1)
        self.btnEquals = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnEquals.sizePolicy().hasHeightForWidth())
        self.btnEquals.setSizePolicy(sizePolicy)
        self.btnEquals.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnEquals.setFont(font)
        self.btnEquals.setObjectName("btnEquals")
        self.buttonGrid.addWidget(self.btnEquals, 7, 3, 1, 1)
        self.btn2 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn2.sizePolicy().hasHeightForWidth())
        self.btn2.setSizePolicy(sizePolicy)
        self.btn2.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn2.setFont(font)
        self.btn2.setObjectName("btn2")
        self.buttonGrid.addWidget(self.btn2, 6, 1, 1, 1)
        self.btnCls = QtWidgets.QPushButton(Calculator)
        self.btnCls.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnCls.setFont(font)
        self.btnCls.setStyleSheet("background-color: #ff9257;")
        self.btnCls.setObjectName("btnCls")
        self.buttonGrid.addWidget(self.btnCls, 2, 0, 1, 1)
        self.btnBck = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnBck.sizePolicy().hasHeightForWidth())
        self.btnBck.setSizePolicy(sizePolicy)
        self.btnBck.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnBck.setFont(font)
        self.btnBck.setStyleSheet("background-color: #ff9257;")
        self.btnBck.setObjectName("btnBck")
        self.buttonGrid.addWidget(self.btnBck, 2, 1, 1, 1)
        self.btn9 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn9.sizePolicy().hasHeightForWidth())
        self.btn9.setSizePolicy(sizePolicy)
        self.btn9.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn9.setFont(font)
        self.btn9.setObjectName("btn9")
        self.buttonGrid.addWidget(self.btn9, 4, 2, 1, 1)
        self.subtract_memory = QtWidgets.QPushButton(Calculator)
        self.subtract_memory.setObjectName("subtract_memory")
        self.buttonGrid.addWidget(self.subtract_memory, 1, 0, 1, 1)
        self.btn1 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn1.sizePolicy().hasHeightForWidth())
        self.btn1.setSizePolicy(sizePolicy)
        self.btn1.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn1.setFont(font)
        self.btn1.setObjectName("btn1")
        self.buttonGrid.addWidget(self.btn1, 6, 0, 1, 1)
        self.btn5 = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btn5.sizePolicy().hasHeightForWidth())
        self.btn5.setSizePolicy(sizePolicy)
        self.btn5.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btn5.setFont(font)
        self.btn5.setObjectName("btn5")
        self.buttonGrid.addWidget(self.btn5, 5, 1, 1, 1)
        self.btnMinus = QtWidgets.QPushButton(Calculator)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.btnMinus.sizePolicy().hasHeightForWidth())
        self.btnMinus.setSizePolicy(sizePolicy)
        self.btnMinus.setMinimumSize(QtCore.QSize(0, 40))
        font = QtGui.QFont()
        font.setPointSize(12)
        self.btnMinus.setFont(font)
        self.btnMinus.setObjectName("btnMinus")
        self.buttonGrid.addWidget(self.btnMinus, 5, 3, 1, 1)
        self.clear_memory = QtWidgets.QPushButton(Calculator)
        self.clear_memory.setObjectName("clear_memory")
        self.buttonGrid.addWidget(self.clear_memory, 1, 2, 1, 1)
        self.gridLayout.addLayout(self.buttonGrid, 1, 0, 1, 1)

        self.retranslateUi(Calculator)
        QtCore.QMetaObject.connectSlotsByName(Calculator)

    def retranslateUi(self, Calculator):
        _translate = QtCore.QCoreApplication.translate
        Calculator.setWindowTitle(_translate("Calculator", "الالة الحاسبة"))
        self.display.setText(_translate("Calculator", "0"))
        self.btn0.setText(_translate("Calculator", "0"))
        self.btnMultiply.setText(_translate("Calculator", "×"))
        self.btn8.setText(_translate("Calculator", "8"))
        self.btnRoot.setText(_translate("Calculator", "√ "))
        self.btnDot.setText(_translate("Calculator", "."))
        self.add_memory.setText(_translate("Calculator", "M+"))
        self.btn3.setText(_translate("Calculator", "3"))
        self.show_memory.setText(_translate("Calculator", "MS"))
        self.btn7.setText(_translate("Calculator", "7"))
        self.btnDivide.setText(_translate("Calculator", "÷"))
        self.btn6.setText(_translate("Calculator", "6"))
        self.btn00.setText(_translate("Calculator", "00"))
        self.btn4.setText(_translate("Calculator", "4"))
        self.btnPlus.setText(_translate("Calculator", "+"))
        self.btnEquals.setText(_translate("Calculator", "="))
        self.btn2.setText(_translate("Calculator", "2"))
        self.btnCls.setText(_translate("Calculator", "AC"))
        self.btnBck.setText(_translate("Calculator", "C"))
        self.btn9.setText(_translate("Calculator", "9"))
        self.subtract_memory.setText(_translate("Calculator", "M-"))
        self.btn1.setText(_translate("Calculator", "1"))
        self.btn5.setText(_translate("Calculator", "5"))
        self.btnMinus.setText(_translate("Calculator", "-"))
        self.clear_memory.setText(_translate("Calculator", "MC"))
