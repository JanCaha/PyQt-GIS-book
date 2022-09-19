import sys
from osgeo import ogr
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFormLayout,
                             QToolButton, QLineEdit, QFileDialog, QWidget,
                             QMenu, QAction)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("První Aplikace")
        self.setMinimumSize(500, 200)

        self.ds = None

        self.init_gui()

    def init_gui(self):

        menu = QMenu('Aplikace', self)
        self.menuBar().addMenu(menu)

        self.action_end = QAction("Ukončit", self)
        self.action_end.triggered.connect(self.exit)

        menu.addAction(self.action_end)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QFormLayout(self.central_widget)
        self.central_widget.setLayout(layout)

        self.select_file = QToolButton()
        self.select_file.setText("Vyberte soubor")
        self.select_file.clicked.connect(self.open_file)

        self.file_path = QLineEdit("")
        self.file_path.setReadOnly(False)

        self.ogr_file = QLineEdit("")

        layout.addWidget(self.select_file)
        layout.addRow("Vybraný soubor:", self.file_path)
        layout.addRow("Otevřít pomocí OGR:", self.ogr_file)

    def exit(self):
        app = QApplication.instance()
        app.quit()

    def open_file(self) -> None:

        filename, _ = QFileDialog.getOpenFileName(self, "Vyberte soubor")

        if filename:
            self.file_path.setText(filename)

            self.ds = ogr.Open(filename, True)

            if self.ds:
                self.ogr_file.setText("Otevřeno OGR!")
            else:
                self.ogr_file.setText("Nelze otevřít pomocí OGR!")

            self.statusBar().showMessage(
                "Soubor `{}` vybrán a zkušebně otevřen.".format(filename), 2000)

        else:
            self.file_path.setText("")
            self.ogr_file.setText("")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
