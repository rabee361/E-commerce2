import os
from PyQt5.QtWidgets import QDialog
from mac_address import mac_address
from Ui_Activation import Ui_Activation


class Ui_Activation_Logic(QDialog):
    def __init__(self):
        super().__init__()
        self.Activation = ''
        self.ui = Ui_Activation()

    def showUi(self):
        window_activation = QDialog()
        self.ui.setupUi(window_activation)
        self.initialize(window_activation)
        window_activation.exec()

    def initialize(self, window_activation):
        self.ui.save_btn.clicked.connect(lambda: self.saveActivationCode(window_activation))
        self.ui.cancel_btn.clicked.connect(lambda: self.quit())
        self.ui.code1_input.setReadOnly(True)
        self.setCode1()

    def setCode1(self):
        mac = mac_address.getMacAddress()
        code1 = str(mac).replace(":","")
        code1 = str(mac).replace("-","")
        self.ui.code1_input.setText(code1)

    def saveActivationCode(self, Activation):
        code = self.ui.code2_input.text()
        if os.name == 'nt':  # Check if running on Windows
            appdata_dir = os.getenv('APPDATA')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')
        else:
            appdata_dir = os.path.expanduser('~/.config')
            epsilon_dir = os.path.join(appdata_dir, 'epsilon')

        # Create 'epsilon' directory if it doesn't exist
        if not os.path.exists(epsilon_dir):
            os.makedirs(epsilon_dir)

        activation_file = os.path.join(epsilon_dir, 'activation.dat')

        with open(activation_file, 'w+') as file:
            file.write(code)

        Activation.accept()

    def quit(self):
        quit()
