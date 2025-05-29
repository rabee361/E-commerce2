from PyQt5.QtWidgets import QTableWidgetItem
class MyTableWidgetItem(QTableWidgetItem):
    def __init__(self, text, sortKey):
            QTableWidgetItem.__init__(self, text, QTableWidgetItem.UserType)
            self.sortKey = sortKey
    def __lt__(self, other):
        print(str("self.sortKey=")+str(self.sortKey))
        print(str("other.sortKey=")+str(other.sortKey))
        return self.sortKey < other.sortKey