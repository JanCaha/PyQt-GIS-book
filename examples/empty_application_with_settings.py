import sys
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QMainWindow, QMenu, QAction)
from PyQt5.QtCore import QSettings
from PyQt5.QtGui import (QResizeEvent, QMoveEvent)


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Aplikace s nastavením")

        self.settings = QSettings()

        # settings_file = Path(__file__).parent / "app_setting.ini"
        # self.settings = QSettings(settings_file.as_posix(), QSettings.Format.IniFormat)

        self.resize_and_move()

        self.ds = None

        self.init_gui()

    def resize_and_move(self):

        size = self.settings.value("mainwindow/size", None)

        if size:
            self.resize(size)
        else:
            self.resize(500, 200)

        position = self.settings.value("mainwindow/position", None)

        if position:
            self.move(position)

    def resizeEvent(self, a0: QResizeEvent) -> None:
        self.settings.setValue("mainwindow/size", self.size())
        return super().resizeEvent(a0)

    def moveEvent(self, a0: QMoveEvent) -> None:
        self.settings.setValue("mainwindow/position", self.pos())
        return super().moveEvent(a0)

    def init_gui(self):

        menu = QMenu('Aplikace', self)
        self.menuBar().addMenu(menu)

        self.action_clean_settings = QAction("Vymazat nastavení", self)
        self.action_clean_settings.triggered.connect(self.clean_settings)

        self.action_end = QAction("Ukončit", self)
        self.action_end.triggered.connect(self.exit)

        menu.addAction(self.action_clean_settings)
        menu.addAction(self.action_end)

    def exit(self):
        app = QApplication.instance()
        app.quit()

    def clean_settings(self):
        self.settings.clear()
        self.resize_and_move()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    QApplication.setOrganizationName("MySoft")
    QApplication.setOrganizationDomain("mysoft.com")
    QApplication.setApplicationName("Star Runner")

    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
