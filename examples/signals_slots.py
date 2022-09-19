from datetime import datetime

from PyQt5.QtCore import QObject, pyqtSignal


class Test(QObject):

    valueChanged = pyqtSignal(int, datetime)

    def __init__(self) -> None:
        super().__init__(None)
        self.value = 0

    def set_value(self, value: int) -> None:
        self.value = value
        self.valueChanged.emit(value, datetime.now())


def print_value_changed(value: int, date_time: datetime):
    print("Test object value changed to {} at {}.".format(
        value, date_time.isoformat()))


if __name__ == "__main__":
    o = Test()
    o.valueChanged.connect(print_value_changed)
    o.set_value(5)
    o.set_value(7)
    o.blockSignals(True)
    o.set_value(15)
    o.blockSignals(False)
    o.set_value(9)
    o.valueChanged.disconnect(print_value_changed)
    o.set_value(10)
