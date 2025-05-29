# Import necessary modules
from PyQt5.QtWidgets import QLineEdit, QItemDelegate

"""
MyCustomTableCellDelegate is a custom delegate class that inherits from QItemDelegate.
The purpose of this subclass is to control the editability of specific cells in a QTableView
based on certain conditions. It allows for fine-grained control over which cells can be edited
by the user, depending on the row, column, and specific conditions provided.
"""

# Custom delegate to control cell editability
class MyCustomTableCellDelegate(QItemDelegate):
    def __init__(self, parent=None, col=None, row=None, condition=None):
        super().__init__(parent)
        self.col = col  # Column index of the cell to control editability
        self.row = row  # Row index of the cell to control editability
        self.condition = condition  # Condition for controlling editability of the cell


    def createEditor(self, parent, option, index):
        editor = QLineEdit(parent)  # Create a line edit widget as the editor for the cell

        # Check if the cell at the specified index should be editable
        if self.col and self.row:
            if index.row() == self.row and index.column() == self.col:
                if self.condition:
                    condition_row = self.condition[0]  # Row index of the cell to check for a condition
                    condition_col = self.condition[1]  # Column index of the cell to check for a condition
                    what_to_see = self.condition[2]  # Value to compare with the dependent cell's value

                    # Get the value of the dependent cell
                    dependent_value = index.model().index(condition_row, condition_col).data()

                    # Check if the dependent value matches the specified condition value
                    if str(dependent_value).lower() == str(what_to_see).lower():
                        return editor  # Allow editing the cell

                else:
                    return editor  # Allow editing the cell

        elif self.col and not self.row:
            if index.column() == self.col:
                if self.condition:
                    condition_col = self.condition[1]  # Column index of the cell to check for a condition
                    what_to_see = self.condition[2]  # Value to compare with the dependent cell's value

                    # Get the value of the dependent cell
                    dependent_value = index.model().index(index.row(), condition_col).data()

                    # Check if the dependent value matches the specified condition value
                    if str(dependent_value).lower() == str(what_to_see).lower():
                        return editor  # Allow editing the cell

                else:
                    return editor  # Allow editing the cell

        elif self.row and not self.col:
            if index.row() == self.row:
                if self.condition:
                    condition_row = self.condition[0]  # Row index of the cell to check for a condition
                    what_to_see = self.condition[2]  # Value to compare with the dependent cell's value

                    # Get the value of the dependent cell
                    dependent_value = index.model().index(condition_row, index.column()).data()

                    # Check if the dependent value matches the specified condition value
                    if str(dependent_value).lower() == str(what_to_see).lower():
                        return editor  # Allow editing the cell

                else:
                    return editor  # Allow editing the cell

        # Return None for other cells to use the default behavior (not editable)
        return None
