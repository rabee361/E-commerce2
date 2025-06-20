# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_AccountEdit.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AccountEdit(object):
    def setupUi(self, AccountEdit):
        AccountEdit.setObjectName("AccountEdit")
        AccountEdit.resize(400, 609)
        AccountEdit.setMinimumSize(QtCore.QSize(400, 300))
        AccountEdit.setMaximumSize(QtCore.QSize(1000, 1000))
        AccountEdit.setLayoutDirection(QtCore.Qt.RightToLeft)
        AccountEdit.setStyleSheet("")
        self.gridLayout = QtWidgets.QGridLayout(AccountEdit)
        self.gridLayout.setObjectName("gridLayout")
        self.groupBox = QtWidgets.QGroupBox(AccountEdit)
        self.groupBox.setStyleSheet("")
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 3, 0, 1, 1)
        self.account_code_input = QtWidgets.QLineEdit(self.groupBox)
        self.account_code_input.setObjectName("account_code_input")
        self.gridLayout_2.addWidget(self.account_code_input, 1, 1, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.gridLayout_2.addWidget(self.label_5, 4, 0, 1, 1)
        self.details_input = QtWidgets.QTextEdit(self.groupBox)
        self.details_input.setMaximumSize(QtCore.QSize(16777215, 50))
        self.details_input.setObjectName("details_input")
        self.gridLayout_2.addWidget(self.details_input, 2, 1, 1, 3)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 0, 0, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.groupBox)
        self.label_3.setObjectName("label_3")
        self.gridLayout_2.addWidget(self.label_3, 5, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout_2.addWidget(self.label_4, 2, 0, 1, 1)
        self.final_account_combobox = QtWidgets.QComboBox(self.groupBox)
        self.final_account_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.final_account_combobox.setObjectName("final_account_combobox")
        self.gridLayout_2.addWidget(self.final_account_combobox, 4, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox)
        self.label_6.setObjectName("label_6")
        self.gridLayout_2.addWidget(self.label_6, 1, 0, 1, 1)
        self.parent_combobox = QtWidgets.QComboBox(self.groupBox)
        self.parent_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.parent_combobox.setObjectName("parent_combobox")
        self.gridLayout_2.addWidget(self.parent_combobox, 3, 1, 1, 1)
        self.name_input = QtWidgets.QLineEdit(self.groupBox)
        self.name_input.setObjectName("name_input")
        self.gridLayout_2.addWidget(self.name_input, 0, 1, 1, 1)
        self.date_input = QtWidgets.QLineEdit(self.groupBox)
        self.date_input.setEnabled(False)
        self.date_input.setObjectName("date_input")
        self.gridLayout_2.addWidget(self.date_input, 5, 1, 1, 1)
        self.select_parent_account_btn = QtWidgets.QToolButton(self.groupBox)
        self.select_parent_account_btn.setObjectName("select_parent_account_btn")
        self.gridLayout_2.addWidget(self.select_parent_account_btn, 3, 2, 1, 1)
        self.select_final_account_btn = QtWidgets.QToolButton(self.groupBox)
        self.select_final_account_btn.setObjectName("select_final_account_btn")
        self.gridLayout_2.addWidget(self.select_final_account_btn, 4, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_4 = QtWidgets.QGroupBox(AccountEdit)
        self.groupBox_4.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.select_financial_statement_btn = QtWidgets.QToolButton(self.groupBox_4)
        self.select_financial_statement_btn.setObjectName("select_financial_statement_btn")
        self.gridLayout_7.addWidget(self.select_financial_statement_btn, 0, 1, 1, 1)
        self.financial_statements_combobox = QtWidgets.QComboBox(self.groupBox_4)
        self.financial_statements_combobox.setMinimumSize(QtCore.QSize(250, 0))
        self.financial_statements_combobox.setStyleSheet("QComboBox {\n"
"        background-color: #fafafa;\n"
"        border: 1px solid lightgrey;        \n"
"        height: 22px;\n"
"        color: black;\n"
"    }\n"
"    QComboBox::drop-down {\n"
"        border: none;\n"
"    }")
        self.financial_statements_combobox.setObjectName("financial_statements_combobox")
        self.gridLayout_7.addWidget(self.financial_statements_combobox, 0, 0, 1, 1)
        self.gridLayout.addWidget(self.groupBox_4, 1, 0, 1, 1)
        self.groupBox_7 = QtWidgets.QGroupBox(AccountEdit)
        self.groupBox_7.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_9 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_9.setObjectName("gridLayout_9")
        self.gridLayout.addWidget(self.groupBox_7, 2, 0, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(AccountEdit)
        self.groupBox_5.setMinimumSize(QtCore.QSize(0, 100))
        self.groupBox_5.setMaximumSize(QtCore.QSize(16777215, 500))
        self.groupBox_5.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.label_20 = QtWidgets.QLabel(self.groupBox_5)
        self.label_20.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_20.setObjectName("label_20")
        self.gridLayout_4.addWidget(self.label_20, 1, 1, 1, 1)
        self.force_cost_center_checkbox = QtWidgets.QCheckBox(self.groupBox_5)
        self.force_cost_center_checkbox.setObjectName("force_cost_center_checkbox")
        self.gridLayout_4.addWidget(self.force_cost_center_checkbox, 0, 1, 1, 1)
        self.cost_center_combobox = QtWidgets.QComboBox(self.groupBox_5)
        self.cost_center_combobox.setObjectName("cost_center_combobox")
        self.gridLayout_4.addWidget(self.cost_center_combobox, 1, 2, 1, 1)
        self.gridLayout.addWidget(self.groupBox_5, 3, 0, 1, 1)
        self.save_btn = QtWidgets.QPushButton(AccountEdit)
        self.save_btn.setObjectName("save_btn")
        self.gridLayout.addWidget(self.save_btn, 4, 0, 1, 1)

        self.retranslateUi(AccountEdit)
        QtCore.QMetaObject.connectSlotsByName(AccountEdit)

    def retranslateUi(self, AccountEdit):
        _translate = QtCore.QCoreApplication.translate
        AccountEdit.setWindowTitle(_translate("AccountEdit", "تعديل معلومات الحساب"))
        self.label_2.setText(_translate("AccountEdit", "الحساب الأب"))
        self.label_5.setText(_translate("AccountEdit", "الحساب الختامي:"))
        self.label.setText(_translate("AccountEdit", "اسم الحساب:"))
        self.label_3.setText(_translate("AccountEdit", "تاريخ الإنشاء"))
        self.label_4.setText(_translate("AccountEdit", "التفاصيل:"))
        self.label_6.setText(_translate("AccountEdit", "رمز الحساب:"))
        self.select_parent_account_btn.setText(_translate("AccountEdit", "🔎"))
        self.select_final_account_btn.setText(_translate("AccountEdit", "🔎"))
        self.groupBox_4.setTitle(_translate("AccountEdit", "القائمة المالية"))
        self.select_financial_statement_btn.setText(_translate("AccountEdit", "🔎"))
        self.groupBox_7.setTitle(_translate("AccountEdit", "تبويبات القائمة المالية"))
        self.label_20.setText(_translate("AccountEdit", "مركز الكلفة:"))
        self.force_cost_center_checkbox.setText(_translate("AccountEdit", "فرض مركز كلفة"))
        self.save_btn.setText(_translate("AccountEdit", "حفظ"))
