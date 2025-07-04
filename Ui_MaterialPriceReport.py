# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_MaterialPriceReport.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MaterialPriceReport(object):
    def setupUi(self, MaterialPriceReport):
        MaterialPriceReport.setObjectName("MaterialPriceReport")
        MaterialPriceReport.setWindowModality(QtCore.Qt.WindowModal)
        MaterialPriceReport.resize(837, 472)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.xpm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MaterialPriceReport.setWindowIcon(icon)
        MaterialPriceReport.setLayoutDirection(QtCore.Qt.RightToLeft)
        MaterialPriceReport.setModal(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(MaterialPriceReport)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.chart_groupbox = QtWidgets.QGroupBox(MaterialPriceReport)
        self.chart_groupbox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.chart_groupbox.setTitle("")
        self.chart_groupbox.setObjectName("chart_groupbox")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.chart_groupbox)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.material_table = QtWidgets.QTableWidget(self.chart_groupbox)
        self.material_table.setObjectName("material_table")
        self.material_table.setColumnCount(3)
        self.material_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.material_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.material_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        item.setTextAlignment(QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.material_table.setHorizontalHeaderItem(2, item)
        self.gridLayout_3.addWidget(self.material_table, 0, 0, 1, 1)
        self.gridLayout_2.addWidget(self.chart_groupbox, 1, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(MaterialPriceReport)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 0, 1, 1)
        self.material_combobox = QtWidgets.QComboBox(self.groupBox)
        self.material_combobox.setMaximumSize(QtCore.QSize(500, 16777215))
        self.material_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.material_combobox.setObjectName("material_combobox")
        self.gridLayout.addWidget(self.material_combobox, 0, 1, 1, 1)
        self.select_material_btn = QtWidgets.QPushButton(self.groupBox)
        self.select_material_btn.setObjectName("select_material_btn")
        self.gridLayout.addWidget(self.select_material_btn, 0, 2, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_2.setWordWrap(True)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 3, 1, 1)
        self.pricing_method_combobox = QtWidgets.QComboBox(self.groupBox)
        self.pricing_method_combobox.setObjectName("pricing_method_combobox")
        self.gridLayout.addWidget(self.pricing_method_combobox, 0, 4, 1, 1)
        self.calc_btn = QtWidgets.QPushButton(self.groupBox)
        self.calc_btn.setObjectName("calc_btn")
        self.gridLayout.addWidget(self.calc_btn, 0, 5, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 0, 6, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(MaterialPriceReport)
        QtCore.QMetaObject.connectSlotsByName(MaterialPriceReport)

    def retranslateUi(self, MaterialPriceReport):
        _translate = QtCore.QCoreApplication.translate
        MaterialPriceReport.setWindowTitle(_translate("MaterialPriceReport", "تقرير قيمة المادة"))
        item = self.material_table.horizontalHeaderItem(0)
        item.setText(_translate("MaterialPriceReport", "معرف المادة"))
        item = self.material_table.horizontalHeaderItem(1)
        item.setText(_translate("MaterialPriceReport", "المادة"))
        item = self.material_table.horizontalHeaderItem(2)
        item.setText(_translate("MaterialPriceReport", "القيمة الاجمالية"))
        self.label.setText(_translate("MaterialPriceReport", "المنتج:"))
        self.select_material_btn.setText(_translate("MaterialPriceReport", "...اختيار"))
        self.label_2.setText(_translate("MaterialPriceReport", "طريقة التسعير:"))
        self.calc_btn.setText(_translate("MaterialPriceReport", "حساب النتيجة"))
