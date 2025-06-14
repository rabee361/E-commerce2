# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'Ui_PlanPercent.ui'
#
# Created by: PyQt5 UI code generator 5.15.9
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_PlanPercent(object):
    def setupUi(self, PlanPercent):
        PlanPercent.setObjectName("PlanPercent")
        PlanPercent.setWindowModality(QtCore.Qt.WindowModal)
        PlanPercent.resize(801, 550)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("graphics/icon.xpm"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        PlanPercent.setWindowIcon(icon)
        PlanPercent.setModal(True)
        self.gridLayout_2 = QtWidgets.QGridLayout(PlanPercent)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.groupBox = QtWidgets.QGroupBox(PlanPercent)
        self.groupBox.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBox.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName("gridLayout")
        self.percent_input = QtWidgets.QDoubleSpinBox(self.groupBox)
        self.percent_input.setStyleSheet("QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {\n"
"    width: 0px;\n"
"    height: 0px;\n"
"    border: none;\n"
"}")
        self.percent_input.setObjectName("percent_input")
        self.gridLayout.addWidget(self.percent_input, 0, 19, 1, 1)
        self.target_input = QtWidgets.QLineEdit(self.groupBox)
        self.target_input.setEnabled(True)
        self.target_input.setMaximumSize(QtCore.QSize(150, 16777215))
        self.target_input.setText("")
        self.target_input.setObjectName("target_input")
        self.gridLayout.addWidget(self.target_input, 0, 17, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.groupBox)
        self.label_2.setMaximumSize(QtCore.QSize(40, 16777215))
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 14, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setMaximumSize(QtCore.QSize(80, 16777215))
        self.label_5.setObjectName("label_5")
        self.gridLayout.addWidget(self.label_5, 0, 18, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.groupBox)
        self.label_4.setObjectName("label_4")
        self.gridLayout.addWidget(self.label_4, 0, 16, 1, 1)
        self.batches_input = QtWidgets.QLineEdit(self.groupBox)
        self.batches_input.setEnabled(False)
        self.batches_input.setMaximumSize(QtCore.QSize(150, 16777215))
        self.batches_input.setObjectName("batches_input")
        self.gridLayout.addWidget(self.batches_input, 0, 15, 1, 1)
        self.calc_btn = QtWidgets.QPushButton(self.groupBox)
        self.calc_btn.setObjectName("calc_btn")
        self.gridLayout.addWidget(self.calc_btn, 0, 21, 1, 1)
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setMaximumSize(QtCore.QSize(50, 16777215))
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 0, 11, 1, 1)
        self.add_btn = QtWidgets.QPushButton(self.groupBox)
        self.add_btn.setObjectName("add_btn")
        self.gridLayout.addWidget(self.add_btn, 0, 20, 1, 1)
        self.products_btn = QtWidgets.QPushButton(self.groupBox)
        self.products_btn.setObjectName("products_btn")
        self.gridLayout.addWidget(self.products_btn, 0, 13, 1, 1)
        self.products = QtWidgets.QComboBox(self.groupBox)
        self.products.setMaximumSize(QtCore.QSize(500, 16777215))
        self.products.setObjectName("products")
        self.gridLayout.addWidget(self.products, 0, 12, 1, 1)
        self.gridLayout_2.addWidget(self.groupBox, 0, 0, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(PlanPercent)
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.plan_percent_items_table = QtWidgets.QTableWidget(self.groupBox_2)
        self.plan_percent_items_table.setGeometry(QtCore.QRect(10, 10, 951, 421))
        self.plan_percent_items_table.setMaximumSize(QtCore.QSize(16777215, 500))
        self.plan_percent_items_table.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.plan_percent_items_table.setObjectName("plan_percent_items_table")
        self.plan_percent_items_table.setColumnCount(6)
        self.plan_percent_items_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.plan_percent_items_table.setHorizontalHeaderItem(5, item)
        self.plan_percent_items_table.horizontalHeader().setStretchLastSection(False)
        self.plan_percent_items_table.verticalHeader().setStretchLastSection(False)
        self.gridLayout_2.addWidget(self.groupBox_2, 1, 0, 1, 1)
        self.groupBox_3 = QtWidgets.QGroupBox(PlanPercent)
        self.groupBox_3.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_3.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.clear_btn = QtWidgets.QPushButton(self.groupBox_3)
        self.clear_btn.setMaximumSize(QtCore.QSize(100, 16777215))
        self.clear_btn.setMouseTracking(False)
        self.clear_btn.setObjectName("clear_btn")
        self.horizontalLayout.addWidget(self.clear_btn)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.gridLayout_2.addWidget(self.groupBox_3, 2, 0, 1, 1)

        self.retranslateUi(PlanPercent)
        QtCore.QMetaObject.connectSlotsByName(PlanPercent)

    def retranslateUi(self, PlanPercent):
        _translate = QtCore.QCoreApplication.translate
        PlanPercent.setWindowTitle(_translate("PlanPercent", "الخطة بالنسبة المئوية"))
        self.label_2.setText(_translate("PlanPercent", "الوجبات:"))
        self.label_5.setText(_translate("PlanPercent", "النسبة المئوية:"))
        self.label_4.setText(_translate("PlanPercent", "عدد القطع الهدف:"))
        self.batches_input.setText(_translate("PlanPercent", "1"))
        self.calc_btn.setText(_translate("PlanPercent", "حساب النتيجة"))
        self.label.setText(_translate("PlanPercent", "المنتج:"))
        self.add_btn.setText(_translate("PlanPercent", "اضافة"))
        self.products_btn.setText(_translate("PlanPercent", "...اختيار"))
        item = self.plan_percent_items_table.horizontalHeaderItem(0)
        item.setText(_translate("PlanPercent", "المعرف"))
        item = self.plan_percent_items_table.horizontalHeaderItem(1)
        item.setText(_translate("PlanPercent", "الكود"))
        item = self.plan_percent_items_table.horizontalHeaderItem(2)
        item.setText(_translate("PlanPercent", "المنتج"))
        item = self.plan_percent_items_table.horizontalHeaderItem(3)
        item.setText(_translate("PlanPercent", "النسبة المئوية"))
        item = self.plan_percent_items_table.horizontalHeaderItem(4)
        item.setText(_translate("PlanPercent", "الأولوية"))
        item = self.plan_percent_items_table.horizontalHeaderItem(5)
        item.setText(_translate("PlanPercent", "حذف"))
        self.clear_btn.setText(_translate("PlanPercent", "حذف الكل"))
