import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QComboBox, QVBoxLayout, QWidget, QLabel
from CheckableComboBoxUpgrader import CheckableComboBoxUpgrader

class ExampleWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Checkable ComboBox Example")
        self.setGeometry(100, 100, 400, 200)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create a label
        label = QLabel("Select items from the combo box:")
        layout.addWidget(label)
        
        # Create a regular QComboBox
        self.combo = QComboBox()
        layout.addWidget(self.combo)
        
        # Upgrade the regular combobox to a checkable one
        self.checkable_combo = CheckableComboBoxUpgrader(self.combo)
        
        # Setup the timer event handler
        self.checkable_combo.setupTimerEvent()
        
        # Add some items
        self.combo.addCheckableItems(["Item 1", "Item 2", "Item 3", "Item 4", "Item 5"])
        
        # Create a label to show selected items
        self.selection_label = QLabel("Selected: None")
        layout.addWidget(self.selection_label)
        
        # Connect to data changed signal to update the label
        self.combo.model().dataChanged.connect(self.update_selection_label)
    
    def update_selection_label(self):
        selected = self.combo.getCheckedTexts()
        if selected:
            self.selection_label.setText("Selected: " + ", ".join(selected))
        else:
            self.selection_label.setText("Selected: None")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ExampleWindow()
    window.show()
    sys.exit(app.exec_())
