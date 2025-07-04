import uuid


class mac_address:
    def __init__(self):
        super().__init__()

    def getMacAddress():
        mac_num = hex(uuid.getnode()).replace('0x', '').upper()
        mac = '-'.join(mac_num[i: i + 2] for i in range(0, 11, 2))
        return mac