from PyQt5 import QtGui
from PyQt5.QtGui import QColor, QBrush

light_green_color = QtGui.QColor(181, 255, 153)
light_red_color = QtGui.QColor(255, 128, 128)
yellow_color = QtGui.QColor(255, 255, 0)
light_yellow_color = QtGui.QColor(238, 255, 153)
dark_yellow_color = QtGui.QColor(166, 162, 45)
blue_sky_color = QtGui.QColor(102, 252, 255)
white_color = QtGui.QColor(255, 255, 255)
dark_green = QtGui.QColor(0, 100, 0)
light_grey = QtGui.QColor(128, 128, 128)
blue = QtGui.QColor(0, 0, 255)
orange = QtGui.QColor(255, 140, 70)
black = QtGui.QColor(0, 0, 0)
white = QtGui.QColor(255, 255, 255)

def textColorForBackground(background_color):
    brightness = (background_color.red() * 299 + background_color.green() * 587 + background_color.blue() * 114) / 1000
    if brightness > 125:
        return QColor(0, 0, 0)  # Black text for light background
    else:
        return QColor(255, 255, 255)  # White text for dark background


def colorizeTreeItems(treeWidget, color=blue, item=None, depth=0):
    if item is None:
        for i in range(treeWidget.topLevelItemCount()):
            top_item = treeWidget.topLevelItem(i)
            colorizeTreeItems(treeWidget, color, top_item, depth)
    else:
        # Only apply color if no background color is already set
        if all(item.background(col) == QBrush() for col in range(item.columnCount())):
            # Adjust color shade based on depth
            color = color.lighter(100 + (depth * 10))
            text_color = textColorForBackground(color)

            # Apply color to the entire row
            for col in range(item.columnCount()):
                brush = QBrush(color)
                item.setBackground(col, brush)
                item.setForeground(col, QBrush(text_color))

        for i in range(item.childCount()):
            child_item = item.child(i)
            colorizeTreeItems(treeWidget, color, child_item, depth + 1)

def colorizeTableRow(tableWidget, row=0, background_color=blue, text_color=black):
    for col in range(tableWidget.columnCount()):
        item = tableWidget.item(row, col)
        if item:
            item.setBackground(background_color)

    for col in range(tableWidget.columnCount()):
        item = tableWidget.item(row, col)
        if item:
            item.setForeground(text_color)