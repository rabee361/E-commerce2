# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_FloatPointSettings.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_FloatPointSettings(object):
    def setupUi(self, FloatPointSettings):
        FloatPointSettings.setObjectName("FloatPointSettings")
        FloatPointSettings.resize(303, 145)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.xpm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        FloatPointSettings.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(FloatPointSettings)
        self.gridLayout.setObjectName("gridLayout")
        self.float_point_input = QtWidgets.QLineEdit(FloatPointSettings)
        self.float_point_input.setObjectName("float_point_input")
        self.gridLayout.addWidget(self.float_point_input, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(FloatPointSettings)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 1, 1, 1)
        self.save_btn = QtWidgets.QPushButton(FloatPointSettings)
        self.save_btn.setObjectName("save_btn")
        self.gridLayout.addWidget(self.save_btn, 1, 0, 1, 2)

        self.retranslateUi(FloatPointSettings)
        QtCore.QMetaObject.connectSlotsByName(FloatPointSettings)

    def retranslateUi(self, FloatPointSettings):
        _translate = QtCore.QCoreApplication.translate
        FloatPointSettings.setWindowTitle(_translate("FloatPointSettings", "ضبط متغيرات الفاصلة"))
        self.label.setText(_translate("FloatPointSettings", " عدد الأرقم بعد الفاصلة: "))
        self.save_btn.setText(_translate("FloatPointSettings", "حفظ"))
