import sys
from PyQt5.QtWidgets import QApplication, QMainWindow

app = QApplication(sys.argv)
ex = QMainWindow()
ex.setWindowTitle("První Aplikace")
ex.show()
sys.exit(app.exec())
