# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_ClientReport.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ClientReport(object):
    def setupUi(self, ClientReport):
        ClientReport.setObjectName("ClientReport")
        ClientReport.setWindowModality(QtCore.Qt.WindowModal)
        ClientReport.resize(1248, 804)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.xpm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ClientReport.setWindowIcon(icon)
        ClientReport.setModal(True)
        self.gridLayout = QtWidgets.QGridLayout(ClientReport)
        self.gridLayout.setObjectName("gridLayout")
        self.export_btn = QtWidgets.QPushButton(ClientReport)
        self.export_btn.setObjectName("export_btn")
        self.gridLayout.addWidget(self.export_btn, 3, 0, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout.addItem(spacerItem, 3, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(ClientReport)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_2.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.total_input = QtWidgets.QLineEdit(self.groupBox_2)
        self.total_input.setEnabled(True)
        self.total_input.setAlignment(QtCore.Qt.AlignCenter)
        self.total_input.setReadOnly(True)
        self.total_input.setObjectName("total_input")
        self.gridLayout_4.addWidget(self.total_input, 0, 5, 1, 1)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem1, 0, 9, 1, 1)
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem2, 0, 14, 1, 1)
        self.paid_input = QtWidgets.QLineEdit(self.groupBox_2)
        self.paid_input.setEnabled(True)
        self.paid_input.setAlignment(QtCore.Qt.AlignCenter)
        self.paid_input.setReadOnly(True)
        self.paid_input.setObjectName("paid_input")
        self.gridLayout_4.addWidget(self.paid_input, 0, 8, 1, 1)
        self.label_8 = QtWidgets.QLabel(self.groupBox_2)
        self.label_8.setObjectName("label_8")
        self.gridLayout_4.addWidget(self.label_8, 0, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_4.addWidget(self.label_5, 0, 7, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_4.addWidget(self.label_4, 0, 3, 1, 1)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem3, 0, 6, 1, 1)
        self.debt_input = QtWidgets.QLineEdit(self.groupBox_2)
        self.debt_input.setEnabled(True)
        self.debt_input.setAlignment(QtCore.Qt.AlignCenter)
        self.debt_input.setReadOnly(True)
        self.debt_input.setObjectName("debt_input")
        self.gridLayout_4.addWidget(self.debt_input, 0, 12, 1, 1)
        self.currency_combobox = QtWidgets.QComboBox(self.groupBox_2)
        self.currency_combobox.setMinimumSize(QtCore.QSize(125, 0))
        self.currency_combobox.setObjectName("currency_combobox")
        self.gridLayout_4.addWidget(self.currency_combobox, 0, 1, 1, 1)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.gridLayout_4.addItem(spacerItem4, 0, 2, 1, 1)
        self.label_7 = QtWidgets.QLabel(self.groupBox_2)
        self.label_7.setObjectName("label_7")
        self.gridLayout_4.addWidget(self.label_7, 0, 11, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout_4.addWidget(self.label_6, 0, 15, 1, 1)
        self.remain_input = QtWidgets.QLineEdit(self.groupBox_2)
        self.remain_input.setEnabled(True)
        self.remain_input.setAlignment(QtCore.Qt.AlignCenter)
        self.remain_input.setReadOnly(True)
        self.remain_input.setObjectName("remain_input")
        self.gridLayout_4.addWidget(self.remain_input, 0, 16, 1, 1)
        self.gridLayout.addWidget(self.groupBox_2, 2, 0, 1, 2)
        self.groupBox = QtWidgets.QGroupBox(ClientReport)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.to_date_input = QtWidgets.QDateEdit(self.groupBox)
        self.to_date_input.setObjectName("to_date_input")
        self.gridLayout_2.addWidget(self.to_date_input, 0, 6, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 0, 5, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.clients_combobox = QtWidgets.QComboBox(self.groupBox)
        self.clients_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.clients_combobox.setObjectName("clients_combobox")
        self.gridLayout_2.addWidget(self.clients_combobox, 0, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 0, 3, 1, 1)
        self.select_client_btn = QtWidgets.QToolButton(self.groupBox)
        self.select_client_btn.setObjectName("select_client_btn")
        self.gridLayout_2.addWidget(self.select_client_btn, 0, 2, 1, 1)
        self.calc_btn = QtWidgets.QPushButton(self.groupBox)
        self.calc_btn.setObjectName("calc_btn")
        self.gridLayout_2.addWidget(self.calc_btn, 0, 7, 1, 1)
        self.from_date_input = QtWidgets.QDateEdit(self.groupBox)
        self.from_date_input.setObjectName("from_date_input")
        self.gridLayout_2.addWidget(self.from_date_input, 0, 4, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 2)
        self.groupBox_3 = QtWidgets.QGroupBox(ClientReport)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.client_operations_table = QtWidgets.QTableWidget(self.groupBox_3)
        self.client_operations_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.client_operations_table.setObjectName("client_operations_table")
        self.client_operations_table.setColumnCount(9)
        self.client_operations_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(7, item)
        item = QtWidgets.QTableWidgetItem()
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        item.setFont(font)
        self.client_operations_table.setHorizontalHeaderItem(8, item)
        self.client_operations_table.horizontalHeader().setStretchLastSection(True)
        self.gridLayout_3.addWidget(self.client_operations_table, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_3, 1, 0, 1, 2)

        self.retranslateUi(ClientReport)
        QtCore.QMetaObject.connectSlotsByName(ClientReport)

    def retranslateUi(self, ClientReport):
        _translate = QtCore.QCoreApplication.translate
        ClientReport.setWindowTitle(_translate("ClientReport", "تقرير زبون"))
        self.export_btn.setText(_translate("ClientReport", "تصدير"))
        self.label_8.setText(_translate("ClientReport", "العملة:"))
        self.label_5.setText(_translate("ClientReport", "المدفوع"))
        self.label_4.setText(_translate("ClientReport", "الاجمالي"))
        self.label_7.setText(_translate("ClientReport", "الدين:"))
        self.label_6.setText(_translate("ClientReport", "الباقي في الرصيد"))
        self.groupBox.setTitle(_translate("ClientReport", "تقرير زبون"))
        self.label_3.setText(_translate("ClientReport", "إلى تاريخ:"))
        self.label.setText(_translate("ClientReport", "الزبون:"))
        self.label_2.setText(_translate("ClientReport", "من تاريخ:"))
        self.select_client_btn.setText(_translate("ClientReport", "🔎"))
        self.calc_btn.setText(_translate("ClientReport", "عرض"))
        item = self.client_operations_table.horizontalHeaderItem(0)
        item.setText(_translate("ClientReport", "معرف الفاتورة"))
        item = self.client_operations_table.horizontalHeaderItem(1)
        item.setText(_translate("ClientReport", "نوع الفاتورة"))
        item = self.client_operations_table.horizontalHeaderItem(2)
        item.setText(_translate("ClientReport", "رقم الفاتورة"))
        item = self.client_operations_table.horizontalHeaderItem(3)
        item.setText(_translate("ClientReport", "الدفع"))
        item = self.client_operations_table.horizontalHeaderItem(4)
        item.setText(_translate("ClientReport", "التاريخ"))
        item = self.client_operations_table.horizontalHeaderItem(5)
        item.setText(_translate("ClientReport", "معرف العملة"))
        item = self.client_operations_table.horizontalHeaderItem(6)
        item.setText(_translate("ClientReport", "العملة"))
        item = self.client_operations_table.horizontalHeaderItem(7)
        item.setText(_translate("ClientReport", "مدفوع"))
        item = self.client_operations_table.horizontalHeaderItem(8)
        item.setText(_translate("ClientReport", "البيان"))
