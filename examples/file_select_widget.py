from functools import partial
import sys
import typing
from pathlib import Path

from PyQt5.QtWidgets import (QApplication, QWidget, QHBoxLayout, QToolButton, QLineEdit,
                             QFileDialog, QAction, QStyle, QLabel)
from PyQt5.QtCore import Qt, pyqtSignal


class FileSelector(QWidget):

    fileSelected = pyqtSignal(str)
    fileCleared = pyqtSignal()

    def __init__(
            self,
            parent: typing.Optional[QWidget] = None,
            flags: typing.Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

        self.init_gui()

        self.dialog = QFileDialog(self, self.tr("Select File"))
        self.dialog.setFileMode(QFileDialog.ExistingFile)

        icon = self.style().standardIcon(QStyle.SP_DialogCloseButton)
        self.clear_action = QAction(icon, self.tr("Clear Selection"), self)
        self.clear_action.setCheckable(False)
        self.clear_action.triggered.connect(self.clear_value)

        self.path_file = None

    def init_gui(self) -> None:

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.button = QToolButton(self)
        self.button.setText("...")
        self.button.clicked.connect(self.show_process_file_dialog)
        self.text = QLineEdit(self)
        self.text.setMinimumWidth(150)
        self.text.textChanged.connect(self.path_defined)
        self.file_selected_label = QLabel()
        self.set_file_selected_label_icon(False)

        layout.addWidget(self.text)
        layout.addWidget(self.button)
        layout.addWidget(self.file_selected_label)

    def set_file_selected_label_icon(self, ok: bool) -> None:
        if ok:
            icon = self.style().standardIcon(QStyle.SP_DialogApplyButton)
        else:
            icon = self.style().standardIcon(QStyle.SP_CustomBase)
        self.file_selected_label.setPixmap(icon.pixmap(self.file_selected_label.size()))

    def set_selected_file_dialog(self) -> None:
        if self.path_file:
            self.dialog.selectFile(self.path_file)
        else:
            self.dialog.setDirectory(Path().expanduser().as_posix())
            self.dialog.selectFile(None)

    def show_process_file_dialog(self) -> None:
        self.set_selected_file_dialog()
        result = self.dialog.exec()

        if result == self.dialog.Accepted:
            file_name = self.dialog.selectedFiles()[0]
            if file_name:
                self.set_existing_file(file_name)
                self.show_file_path(file_name)
                self.show_clear_action()
            else:
                self.fileCleared.emit()

    def show_clear_action(self) -> None:
        self.text.addAction(self.clear_action, QLineEdit.ActionPosition.TrailingPosition)

    def set_existing_file(self, file_name: str) -> None:
        self.path_file = file_name
        self.fileSelected.emit(self.path_file)
        self.set_file_selected_label_icon(True)

    def show_file_path(self, path: str) -> None:
        self.text.blockSignals(True)
        self.text.setText(path)
        self.text.blockSignals(False)

    def path_defined(self) -> None:
        self.show_clear_action()
        path = Path(self.text.text())

        if path.exists() and path.is_file():
            if path.absolute().as_posix() != self.path_file:
                self.set_existing_file(self.text.text())
        else:
            self.clear_file()

        if self.text.text() == "":
            self.fileCleared.emit()

    def clear_file(self) -> None:
        shouldSignalEmit = self.path_file is not None
        self.path_file = None
        self.set_file_selected_label_icon(False)
        if shouldSignalEmit:
            self.fileCleared.emit()

    def clear_value(self) -> None:
        self.show_file_path("")
        self.text.removeAction(self.clear_action)
        self.clear_file()


def print_file(file: str) -> None:
    print(file)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = FileSelector()
    w.fileSelected.connect(print_file)
    w.fileCleared.connect(partial(print_file, "Cleared"))
    w.show()
    sys.exit(app.exec())
