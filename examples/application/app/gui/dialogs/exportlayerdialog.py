from pathlib import Path
from PyQt5.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QComboBox, QPushButton,
                             QFileDialog, QLineEdit)
from PyQt5.QtCore import pyqtSignal, Qt

from osgeo import gdal, ogr

from ...model.data import SpatialData
from ..widgets.fileselect import FileSelectWidget


class ExportLayerDialog(QDialog):

    def __init__(self, spatial_data: SpatialData, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Exportovat vrstvu do souboru")

        layout = QFormLayout()
        self.setLayout(layout)

        self._spatial_data = spatial_data
        self._result_file_name: str = None
        self._selected_file_name: str = None

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(False)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        self.layer_selection = QComboBox()
        for layer in self._spatial_data.layers_names:
            self.layer_selection.addItem(layer)

        self.save_type = QComboBox()
        self.save_type.currentIndexChanged.connect(self.prepare_file_name)

        for i in range(ogr.GetDriverCount()):
            driver: ogr.Driver = ogr.GetDriver(i)
            metadata = driver.GetMetadata()
            if driver.TestCapability(ogr.ODrCCreateDataSource):
                long_name = metadata.get("DMD_LONGNAME", None)
                extension = metadata.get("DMD_EXTENSIONS", None)
                if extension:
                    extension = extension.split(" ")
                    extension = extension[0]
                if long_name and extension:
                    self.save_type.addItem("{} (*.{})".format(long_name, extension),
                                           (driver, extension))

        self.file_select = QPushButton("...", self)
        self.file_select.clicked.connect(self.set_selected_file_name)

        self.file_name = QLineEdit(self)
        self.file_name.setReadOnly(True)

        layout.addRow("Vrstva:", self.layer_selection)
        layout.addRow("Uložit jako:", self.save_type)
        layout.addRow("Zvolit soubor:", self.file_select)
        layout.addRow("Výsledný soubor:", self.file_name)
        layout.addWidget(self.button_box)

    def set_selected_file_name(self):
        self._selected_file_name, _ = QFileDialog.getSaveFileName(self, "Set File name")
        self.prepare_file_name()

    def prepare_file_name(self):
        if self._selected_file_name:
            file_path = Path(self._selected_file_name)
            ext = self.save_type.currentData(Qt.UserRole)[1]
            if file_path.suffix.replace(".", "").lower() != ext.lower():
                file_path = file_path.parent / "{}.{}".format(file_path.stem, ext)
            self._result_file_name = file_path.as_posix()
            self.file_name.setText(self._result_file_name)
        self.enable_ok()

    def enable_ok(self) -> None:
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(self._result_file_name is not None)

    @property
    def selected_layer(self) -> str:
        return self.layer_selection.currentText()

    @property
    def result_file_name(self) -> str:
        return self._result_file_name
