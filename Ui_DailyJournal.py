# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_DailyJournal.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_DailyJournal(object):
    def setupUi(self, DailyJournal):
        DailyJournal.setObjectName("DailyJournal")
        DailyJournal.setWindowModality(QtCore.Qt.WindowModal)
        DailyJournal.resize(1417, 831)
        DailyJournal.setMinimumSize(QtCore.QSize(0, 500))
        DailyJournal.setLayoutDirection(QtCore.Qt.RightToLeft)
        DailyJournal.setModal(True)
        self.gridLayout_4 = QtWidgets.QGridLayout(DailyJournal)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.groupBox_3 = QtWidgets.QGroupBox(DailyJournal)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_3.sizePolicy().hasHeightForWidth())
        self.groupBox_3.setSizePolicy(sizePolicy)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox_3.setObjectName("groupBox_3")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox_3)
        self.gridLayout_2.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_2.setSpacing(3)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.results_tree = QtWidgets.QTreeWidget(self.groupBox_3)
        self.results_tree.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.results_tree.setStyleSheet("QScrollBar:vertical {\n"
"    background-color: #f1f1f1;\n"
"    width: 12px;\n"
"    margin: 12px 0 12px 0;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background-color: #888;\n"
"    min-height: 20px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background-color: #555;\n"
"}\n"
"\n"
"QTreeWidget{background-color:rgb(252, 255, 210);}")
        self.results_tree.setObjectName("results_tree")
        self.results_tree.headerItem().setTextAlignment(0, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(1, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(2, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(3, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(4, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(5, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(6, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(7, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.results_tree.headerItem().setTextAlignment(8, QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.gridLayout_2.addWidget(self.results_tree, 0, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_3, 1, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(DailyJournal)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.groupBox_2.sizePolicy().hasHeightForWidth())
        self.groupBox_2.setSizePolicy(sizePolicy)
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 200))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)
        self.gridLayout_3.setSpacing(3)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.label_2 = QtWidgets.QLabel(self.groupBox_2)
        self.label_2.setObjectName("label_2")
        self.gridLayout_3.addWidget(self.label_2, 0, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox_2)
        self.label.setObjectName("label")
        self.gridLayout_3.addWidget(self.label, 0, 1, 1, 1)
        self.creditors_sum_tree = QtWidgets.QTreeWidget(self.groupBox_2)
        self.creditors_sum_tree.setStyleSheet("QScrollBar:vertical {\n"
"    background-color: #00b05e;\n"
"    width: 12px;\n"
"    margin: 12px 0 12px 0;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background-color: #888;\n"
"    min-height: 20px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background-color: #555;\n"
"}\n"
"\n"
"QTreeWidget{background-color:#41bf9e;}")
        self.creditors_sum_tree.setObjectName("creditors_sum_tree")
        self.gridLayout_3.addWidget(self.creditors_sum_tree, 1, 0, 1, 1)
        self.debtors_sum_tree = QtWidgets.QTreeWidget(self.groupBox_2)
        self.debtors_sum_tree.setStyleSheet("QScrollBar:vertical {\n"
"    background-color: #00b05e;\n"
"    width: 12px;\n"
"    margin: 12px 0 12px 0;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical {\n"
"    background-color: #888;\n"
"    min-height: 20px;\n"
"    border-radius: 4px;\n"
"}\n"
"\n"
"QScrollBar::handle:vertical:hover {\n"
"    background-color: #555;\n"
"}\n"
"\n"
"QTreeWidget{background-color:#41bf9e;}")
        self.debtors_sum_tree.setObjectName("debtors_sum_tree")
        self.gridLayout_3.addWidget(self.debtors_sum_tree, 1, 1, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox_2, 2, 0, 1, 1)
        self.groupBox = QtWidgets.QGroupBox(DailyJournal)
        self.groupBox.setMinimumSize(QtCore.QSize(0, 120))
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 16777215))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_7 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_7.setContentsMargins(10, 3, 10, 3)
        self.gridLayout_7.setSpacing(3)
        self.gridLayout_7.setObjectName("gridLayout_7")
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setMaximumSize(QtCore.QSize(30, 16777215))
        self.label_5.setObjectName("label_5")
        self.gridLayout_7.addWidget(self.label_5, 3, 0, 1, 1)
        self.groupBox_6 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_6.setObjectName("groupBox_6")
        self.gridLayout_5 = QtWidgets.QGridLayout(self.groupBox_6)
        self.gridLayout_5.setObjectName("gridLayout_5")
        self.select_invoices_btn = QtWidgets.QPushButton(self.groupBox_6)
        self.select_invoices_btn.setMaximumSize(QtCore.QSize(125, 16777215))
        self.select_invoices_btn.setObjectName("select_invoices_btn")
        self.gridLayout_5.addWidget(self.select_invoices_btn, 3, 1, 1, 1)
        self.source_loans_checkbox = QtWidgets.QCheckBox(self.groupBox_6)
        self.source_loans_checkbox.setChecked(True)
        self.source_loans_checkbox.setObjectName("source_loans_checkbox")
        self.gridLayout_5.addWidget(self.source_loans_checkbox, 2, 1, 1, 1)
        self.source_manufacture_checkbox = QtWidgets.QCheckBox(self.groupBox_6)
        self.source_manufacture_checkbox.setChecked(True)
        self.source_manufacture_checkbox.setObjectName("source_manufacture_checkbox")
        self.gridLayout_5.addWidget(self.source_manufacture_checkbox, 0, 1, 1, 1)
        self.source_period_start_material_checkbox = QtWidgets.QCheckBox(self.groupBox_6)
        self.source_period_start_material_checkbox.setChecked(True)
        self.source_period_start_material_checkbox.setObjectName("source_period_start_material_checkbox")
        self.gridLayout_5.addWidget(self.source_period_start_material_checkbox, 0, 0, 1, 1)
        self.source_period_start_checkbox = QtWidgets.QCheckBox(self.groupBox_6)
        self.source_period_start_checkbox.setChecked(True)
        self.source_period_start_checkbox.setObjectName("source_period_start_checkbox")
        self.gridLayout_5.addWidget(self.source_period_start_checkbox, 2, 0, 1, 1)
        self.source_journal_checkbox = QtWidgets.QCheckBox(self.groupBox_6)
        self.source_journal_checkbox.setChecked(True)
        self.source_journal_checkbox.setObjectName("source_journal_checkbox")
        self.gridLayout_5.addWidget(self.source_journal_checkbox, 3, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_6, 0, 4, 5, 1)
        self.to_date_input = QtWidgets.QDateEdit(self.groupBox)
        self.to_date_input.setObjectName("to_date_input")
        self.gridLayout_7.addWidget(self.to_date_input, 3, 1, 1, 1)
        self.calculate_btn = QtWidgets.QPushButton(self.groupBox)
        self.calculate_btn.setMaximumSize(QtCore.QSize(100, 16777215))
        self.calculate_btn.setObjectName("calculate_btn")
        self.gridLayout_7.addWidget(self.calculate_btn, 2, 5, 1, 1)
        self.groupBox_5 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_5.setEnabled(True)
        self.groupBox_5.setTitle("")
        self.groupBox_5.setObjectName("groupBox_5")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_5)
        self.gridLayout.setContentsMargins(0, 0, 3, 0)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.exchange_date_input = QtWidgets.QDateEdit(self.groupBox_5)
        self.exchange_date_input.setObjectName("exchange_date_input")
        self.gridLayout.addWidget(self.exchange_date_input, 0, 1, 1, 1)
        self.distinct_exchange_date_radio = QtWidgets.QRadioButton(self.groupBox_5)
        self.distinct_exchange_date_radio.setObjectName("distinct_exchange_date_radio")
        self.gridLayout.addWidget(self.distinct_exchange_date_radio, 1, 0, 1, 2)
        self.unified_exchange_date_radio = QtWidgets.QRadioButton(self.groupBox_5)
        self.unified_exchange_date_radio.setChecked(True)
        self.unified_exchange_date_radio.setObjectName("unified_exchange_date_radio")
        self.gridLayout.addWidget(self.unified_exchange_date_radio, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_5, 0, 3, 5, 1)
        self.groupBox_7 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_7.setTitle("")
        self.groupBox_7.setObjectName("groupBox_7")
        self.gridLayout_8 = QtWidgets.QGridLayout(self.groupBox_7)
        self.gridLayout_8.setContentsMargins(3, 3, 3, 3)
        self.gridLayout_8.setSpacing(3)
        self.gridLayout_8.setObjectName("gridLayout_8")
        self.unified_currency_radio = QtWidgets.QRadioButton(self.groupBox_7)
        self.unified_currency_radio.setMaximumSize(QtCore.QSize(150, 16777215))
        self.unified_currency_radio.setChecked(True)
        self.unified_currency_radio.setObjectName("unified_currency_radio")
        self.gridLayout_8.addWidget(self.unified_currency_radio, 1, 0, 1, 1)
        self.currency_combobox = QtWidgets.QComboBox(self.groupBox_7)
        self.currency_combobox.setEnabled(True)
        self.currency_combobox.setObjectName("currency_combobox")
        self.gridLayout_8.addWidget(self.currency_combobox, 1, 1, 1, 1)
        self.distinct_currency_radio = QtWidgets.QRadioButton(self.groupBox_7)
        self.distinct_currency_radio.setMaximumSize(QtCore.QSize(180, 16777215))
        self.distinct_currency_radio.setObjectName("distinct_currency_radio")
        self.gridLayout_8.addWidget(self.distinct_currency_radio, 0, 0, 1, 1)
        self.gridLayout_7.addWidget(self.groupBox_7, 0, 2, 5, 1)
        self.from_date_input = QtWidgets.QDateEdit(self.groupBox)
        self.from_date_input.setObjectName("from_date_input")
        self.gridLayout_7.addWidget(self.from_date_input, 1, 1, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setMaximumSize(QtCore.QSize(30, 16777215))
        self.label_4.setObjectName("label_4")
        self.gridLayout_7.addWidget(self.label_4, 1, 0, 1, 1)
        self.gridLayout_4.addWidget(self.groupBox, 0, 0, 1, 1)

        self.retranslateUi(DailyJournal)
        QtCore.QMetaObject.connectSlotsByName(DailyJournal)

    def retranslateUi(self, DailyJournal):
        _translate = QtCore.QCoreApplication.translate
        DailyJournal.setWindowTitle(_translate("DailyJournal", "دفتر اليومية"))
        self.groupBox_3.setTitle(_translate("DailyJournal", "التفصيل"))
        self.results_tree.headerItem().setText(0, _translate("DailyJournal", "معرف السند"))
        self.results_tree.headerItem().setText(1, _translate("DailyJournal", "معرف مدخلة السند"))
        self.results_tree.headerItem().setText(2, _translate("DailyJournal", "المصدر"))
        self.results_tree.headerItem().setText(3, _translate("DailyJournal", "الحساب"))
        self.results_tree.headerItem().setText(4, _translate("DailyJournal", "دائن"))
        self.results_tree.headerItem().setText(5, _translate("DailyJournal", "مدين"))
        self.results_tree.headerItem().setText(6, _translate("DailyJournal", "معرف العملة"))
        self.results_tree.headerItem().setText(7, _translate("DailyJournal", "العملة"))
        self.results_tree.headerItem().setText(8, _translate("DailyJournal", "البيان"))
        self.label_2.setText(_translate("DailyJournal", "دائن"))
        self.label.setText(_translate("DailyJournal", "مدين"))
        self.creditors_sum_tree.headerItem().setText(0, _translate("DailyJournal", "معرف العملة"))
        self.creditors_sum_tree.headerItem().setText(1, _translate("DailyJournal", "العملة"))
        self.creditors_sum_tree.headerItem().setText(2, _translate("DailyJournal", "المجموع"))
        self.debtors_sum_tree.headerItem().setText(0, _translate("DailyJournal", "معرف العملة"))
        self.debtors_sum_tree.headerItem().setText(1, _translate("DailyJournal", "العملة"))
        self.debtors_sum_tree.headerItem().setText(2, _translate("DailyJournal", "المجموع"))
        self.label_5.setText(_translate("DailyJournal", "إلى:"))
        self.groupBox_6.setTitle(_translate("DailyJournal", "المصادر"))
        self.select_invoices_btn.setText(_translate("DailyJournal", "...فواتير"))
        self.source_loans_checkbox.setText(_translate("DailyJournal", "القروض"))
        self.source_manufacture_checkbox.setText(_translate("DailyJournal", "عمليات التصنيع"))
        self.source_period_start_material_checkbox.setText(_translate("DailyJournal", "بضاعة أول المدة"))
        self.source_period_start_checkbox.setText(_translate("DailyJournal", "القيود الافتتاحية"))
        self.source_journal_checkbox.setText(_translate("DailyJournal", "سندات القيد"))
        self.calculate_btn.setText(_translate("DailyJournal", "حساب"))
        self.distinct_exchange_date_radio.setText(_translate("DailyJournal", "اعتماد التاريخ الخاص بكل سجل قيد كتاريخ لتعادل العملة"))
        self.unified_exchange_date_radio.setText(_translate("DailyJournal", ":اعتماد تعادل العملة في التاريخ التالي"))
        self.unified_currency_radio.setText(_translate("DailyJournal", "استخدام عملة واحدة"))
        self.distinct_currency_radio.setText(_translate("DailyJournal", "حساب كل عملة  على حدى"))
        self.label_4.setText(_translate("DailyJournal", "من:"))
