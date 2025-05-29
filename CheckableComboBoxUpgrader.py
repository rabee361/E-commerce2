from PyQt5.QtWidgets import QComboBox, QStyledItemDelegate, QApplication as qApp
from PyQt5.QtGui import QPalette, QStandardItem, QFontMetrics
from PyQt5.QtCore import Qt, QEvent, QObject

class CheckableComboBoxUpgrader(QObject):
    """
    A class that upgrades an existing QComboBox with checkable items functionality.
    """
    
    # Subclass Delegate to increase item height
    class Delegate(QStyledItemDelegate):
        def sizeHint(self, option, index):
            size = super().sizeHint(option, index)
            size.setHeight(20)
            return size

    def __init__(self, combobox):
        """
        Initialize the upgrader with an existing QComboBox.
        
        Args:
            combobox (QComboBox): The combobox to upgrade
        """
        super().__init__()
        self.combobox = combobox
        
        # Make the combo editable to set a custom text, but readonly
        self.combobox.setEditable(True)
        self.combobox.lineEdit().setReadOnly(True)
        
        # Make the lineedit the same color as QPushButton
        palette = qApp.palette()
        palette.setBrush(QPalette.Base, palette.button())
        self.combobox.lineEdit().setPalette(palette)

        # Use custom delegate
        self.combobox.setItemDelegate(self.Delegate())

        # Update the text when an item is toggled
        self.combobox.model().dataChanged.connect(self.updateText)

        # Hide and show popup when clicking the line edit
        self.combobox.lineEdit().installEventFilter(self)
        self.closeOnLineEditClick = False

        # Prevent popup from closing when clicking on an item
        self.combobox.view().viewport().installEventFilter(self)
        
        # Override original methods with our enhanced versions
        self.original_showPopup = self.combobox.showPopup
        self.original_hidePopup = self.combobox.hidePopup
        self.combobox.showPopup = self.showPopup
        self.combobox.hidePopup = self.hidePopup
        
        # Add our methods to the combobox
        self.combobox.addCheckableItem = self.addItem
        self.combobox.addCheckableItems = self.addItems
        self.combobox.getCheckedData = self.currentData
        self.combobox.getCheckedTexts = self.currentTexts
        
        # Connect to resize event
        self.combobox.resizeEvent = self.resizeEvent

    def resizeEvent(self, event):
        # Recompute text to elide as needed
        self.updateText()
        # Call the original resizeEvent
        QComboBox.resizeEvent(self.combobox, event)

    def eventFilter(self, object, event):
        if object == self.combobox.lineEdit():
            if event.type() == QEvent.MouseButtonRelease:
                if self.closeOnLineEditClick:
                    self.combobox.hidePopup()
                else:
                    self.combobox.showPopup()
                return True
            return False

        if object == self.combobox.view().viewport():
            if event.type() == QEvent.MouseButtonRelease:
                index = self.combobox.view().indexAt(event.pos())
                item = self.combobox.model().item(index.row())

                if item.checkState() == Qt.Checked:
                    item.setCheckState(Qt.Unchecked)
                else:
                    item.setCheckState(Qt.Checked)
                return True
        return False

    def showPopup(self):
        self.original_showPopup()
        # When the popup is displayed, a click on the lineedit should close it
        self.closeOnLineEditClick = True

    def hidePopup(self):
        self.original_hidePopup()
        # Used to prevent immediate reopening when clicking on the lineEdit
        self.combobox.startTimer(100)
        # Refresh the display text when closing
        self.updateText()

    def timerEvent(self, event):
        # After timeout, kill timer, and reenable click on line edit
        self.combobox.killTimer(event.timerId())
        self.closeOnLineEditClick = False
        
    # Add the timerEvent to the combobox
    def setupTimerEvent(self):
        self.combobox.timerEvent = self.timerEvent

    def updateText(self):
        texts = []
        for i in range(self.combobox.model().rowCount()):
            if self.combobox.model().item(i).checkState() == Qt.Checked:
                texts.append(self.combobox.model().item(i).text())
        text = ", ".join(texts)

        # Compute elided text (with "...")
        metrics = QFontMetrics(self.combobox.lineEdit().font())
        elidedText = metrics.elidedText(text, Qt.ElideRight, self.combobox.lineEdit().width())
        self.combobox.lineEdit().setText(elidedText)

    def addItem(self, text, data=None):
        item = QStandardItem()
        item.setText(text)
        if data is None:
            item.setData(text)
        else:
            item.setData(data)
        item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsUserCheckable)
        item.setData(Qt.Unchecked, Qt.CheckStateRole)
        self.combobox.model().appendRow(item)

    def addItems(self, texts, datalist=None):
        for i, text in enumerate(texts):
            try:
                data = datalist[i]
            except (TypeError, IndexError):
                data = None
            self.addItem(text, data)

    def currentData(self):
        # Return the list of selected items data
        res = []
        for i in range(self.combobox.model().rowCount()):
            if self.combobox.model().item(i).checkState() == Qt.Checked:
                res.append(self.combobox.model().item(i).data())
        return res
        
    def currentTexts(self):
        # Return the list of selected items texts
        res = []
        for i in range(self.combobox.model().rowCount()):
            if self.combobox.model().item(i).checkState() == Qt.Checked:
                res.append(self.combobox.model().item(i).text())
        return res
