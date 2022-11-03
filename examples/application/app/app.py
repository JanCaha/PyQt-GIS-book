from typing import List
import sys

from PyQt5.QtWidgets import QApplication

from .gui.mainwindow import MainWindow


def run_app(args: List[str]) -> None:
    app = QApplication(args)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
