# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_AddReceiptDocs.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddReceiptDocs(object):
    def setupUi(self, AddReceiptDocs):
        AddReceiptDocs.setObjectName("AddReceiptDocs")
        AddReceiptDocs.resize(416, 300)
        AddReceiptDocs.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.gridLayout = QtWidgets.QGridLayout(AddReceiptDocs)
        self.gridLayout.setObjectName("gridLayout")
        self.target_warehouse_label = QtWidgets.QLabel(AddReceiptDocs)
        self.target_warehouse_label.setObjectName("target_warehouse_label")
        self.gridLayout.addWidget(self.target_warehouse_label, 5, 2, 1, 1)
        self.date_input = QtWidgets.QDateEdit(AddReceiptDocs)
        self.date_input.setObjectName("date_input")
        self.gridLayout.addWidget(self.date_input, 0, 5, 1, 1)
        self.save_btn = QtWidgets.QPushButton(AddReceiptDocs)
        self.save_btn.setObjectName("save_btn")
        self.gridLayout.addWidget(self.save_btn, 10, 1, 1, 7)
        self.rejection_warehouse_combobox = QtWidgets.QComboBox(AddReceiptDocs)
        self.rejection_warehouse_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.rejection_warehouse_combobox.setObjectName("rejection_warehouse_combobox")
        self.gridLayout.addWidget(self.rejection_warehouse_combobox, 6, 5, 1, 1)
        self.material_label = QtWidgets.QLabel(AddReceiptDocs)
        self.material_label.setAlignment(QtCore.Qt.AlignCenter)
        self.material_label.setObjectName("material_label")
        self.gridLayout.addWidget(self.material_label, 2, 2, 1, 1)
        self.quantity_input = QtWidgets.QLineEdit(AddReceiptDocs)
        self.quantity_input.setObjectName("quantity_input")
        self.gridLayout.addWidget(self.quantity_input, 4, 5, 1, 1)
        self.quantity_label_2 = QtWidgets.QLabel(AddReceiptDocs)
        self.quantity_label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.quantity_label_2.setObjectName("quantity_label_2")
        self.gridLayout.addWidget(self.quantity_label_2, 7, 2, 1, 1)
        self.invoice_number_input = QtWidgets.QLineEdit(AddReceiptDocs)
        self.invoice_number_input.setEnabled(False)
        self.invoice_number_input.setStyleSheet("color:black;\n"
"background-color:white;\n"
"border:solid 1px;")
        self.invoice_number_input.setObjectName("invoice_number_input")
        self.gridLayout.addWidget(self.invoice_number_input, 7, 5, 1, 1)
        self.target_warehouse_combobox = QtWidgets.QComboBox(AddReceiptDocs)
        self.target_warehouse_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.target_warehouse_combobox.setObjectName("target_warehouse_combobox")
        self.gridLayout.addWidget(self.target_warehouse_combobox, 5, 5, 1, 1)
        self.materials_combobox = QtWidgets.QComboBox(AddReceiptDocs)
        self.materials_combobox.setEnabled(False)
        self.materials_combobox.setMinimumSize(QtCore.QSize(0, 0))
        self.materials_combobox.setObjectName("materials_combobox")
        self.gridLayout.addWidget(self.materials_combobox, 2, 5, 1, 1)
        self.quantity_label = QtWidgets.QLabel(AddReceiptDocs)
        self.quantity_label.setAlignment(QtCore.Qt.AlignCenter)
        self.quantity_label.setObjectName("quantity_label")
        self.gridLayout.addWidget(self.quantity_label, 4, 2, 1, 1)
        self.date_label = QtWidgets.QLabel(AddReceiptDocs)
        self.date_label.setAlignment(QtCore.Qt.AlignCenter)
        self.date_label.setObjectName("date_label")
        self.gridLayout.addWidget(self.date_label, 0, 2, 1, 1)
        self.rejection_warehouse_label = QtWidgets.QLabel(AddReceiptDocs)
        self.rejection_warehouse_label.setObjectName("rejection_warehouse_label")
        self.gridLayout.addWidget(self.rejection_warehouse_label, 6, 2, 1, 1)
        self.select_material_btn = QtWidgets.QToolButton(AddReceiptDocs)
        self.select_material_btn.setObjectName("select_material_btn")
        self.gridLayout.addWidget(self.select_material_btn, 2, 6, 1, 1)
        self.select_target_warehouse_btn = QtWidgets.QToolButton(AddReceiptDocs)
        self.select_target_warehouse_btn.setObjectName("select_target_warehouse_btn")
        self.gridLayout.addWidget(self.select_target_warehouse_btn, 5, 6, 1, 1)
        self.select_rejection_warehouse_btn = QtWidgets.QToolButton(AddReceiptDocs)
        self.select_rejection_warehouse_btn.setObjectName("select_rejection_warehouse_btn")
        self.gridLayout.addWidget(self.select_rejection_warehouse_btn, 6, 6, 1, 1)
        self.show_invoice_btn = QtWidgets.QPushButton(AddReceiptDocs)
        self.show_invoice_btn.setObjectName("show_invoice_btn")
        self.gridLayout.addWidget(self.show_invoice_btn, 7, 6, 1, 1)
        self.pick_invoice_btn = QtWidgets.QPushButton(AddReceiptDocs)
        self.pick_invoice_btn.setObjectName("pick_invoice_btn")
        self.gridLayout.addWidget(self.pick_invoice_btn, 8, 6, 1, 1)
        self.units_combobox = QtWidgets.QComboBox(AddReceiptDocs)
        self.units_combobox.setObjectName("units_combobox")
        self.gridLayout.addWidget(self.units_combobox, 4, 6, 1, 1)

        self.retranslateUi(AddReceiptDocs)
        QtCore.QMetaObject.connectSlotsByName(AddReceiptDocs)

    def retranslateUi(self, AddReceiptDocs):
        _translate = QtCore.QCoreApplication.translate
        AddReceiptDocs.setWindowTitle(_translate("AddReceiptDocs", "إضافة سند استلام"))
        self.target_warehouse_label.setText(_translate("AddReceiptDocs", "المستودع الهدف:"))
        self.save_btn.setText(_translate("AddReceiptDocs", "حفظ"))
        self.material_label.setText(_translate("AddReceiptDocs", "المادة:"))
        self.quantity_label_2.setText(_translate("AddReceiptDocs", "رقم الفاتورة المرتبطة:"))
        self.quantity_label.setText(_translate("AddReceiptDocs", "الكمية:"))
        self.date_label.setText(_translate("AddReceiptDocs", "التاريخ:"))
        self.rejection_warehouse_label.setText(_translate("AddReceiptDocs", "مستودع الرفض:"))
        self.select_material_btn.setText(_translate("AddReceiptDocs", "🔎"))
        self.select_target_warehouse_btn.setText(_translate("AddReceiptDocs", "🔎"))
        self.select_rejection_warehouse_btn.setText(_translate("AddReceiptDocs", "🔎"))
        self.show_invoice_btn.setText(_translate("AddReceiptDocs", "عرض الفاتورة"))
        self.pick_invoice_btn.setText(_translate("AddReceiptDocs", "اختيار فاتورة"))
