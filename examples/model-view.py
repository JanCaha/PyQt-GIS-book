from typing import Optional
import sys
from osgeo import ogr, osr
from PyQt5.QtWidgets import (QApplication, QMainWindow, QFormLayout, QTableView, QLineEdit, QLabel,
                             QWidget)
from PyQt5.QtCore import QAbstractTableModel, QObject, QModelIndex, Qt
from file_select_widget import FileSelector


class TableModel(QAbstractTableModel):

    def __init__(self, datasource: ogr.DataSource, parent: Optional[QObject] = None) -> None:
        super().__init__(parent)
        self._ds = datasource

    def set_ds(self, ds: ogr.DataSource) -> None:
        self._ds = ds
        self.layoutChanged.emit()

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        if parent == QModelIndex() and self._ds:
            return self._ds.GetLayerCount()
        return 0

    def columnCount(self, parent: QModelIndex = QModelIndex) -> int:
        if parent == QModelIndex():
            return 4
        return 0

    def headerData(self, section: int, orientation: Qt.Orientation, role: Qt.ItemDataRole):

        if role == Qt.DisplayRole:

            if orientation == Qt.Horizontal:

                if section == 0:
                    return "Layer Name"

                elif section == 1:
                    return "Feature Type"

                elif section == 2:
                    return "Feature Count"

                elif section == 3:
                    return "CRS"

        return None

    def data(self, index: QModelIndex, role=Qt.ItemDataRole) -> str:

        if role == Qt.DisplayRole:

            layer: ogr.Layer = self._ds.GetLayer(index.row())

            if index.column() == 0:
                return layer.GetName()

            elif index.column() == 1:
                return ogr.GeometryTypeToName(layer.GetGeomType())

            elif index.column() == 2:
                return layer.GetFeatureCount()

            elif index.column() == 3:
                crs: osr.SpatialReference = layer.GetSpatialRef()
                authority = crs.GetAuthorityName(None)
                code = crs.GetAuthorityCode(None)
                if authority and code:
                    return "{}:{}".format(authority, code)
                else:
                    crs.ExportToWkt()

            else:
                return ""

        return None


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("Informace o vrstvách v souboru")
        self.setMinimumSize(550, 300)

        self.ds: ogr.DataSource = None
        self.table_model = TableModel(self.ds)

        self.init_gui()

    def init_gui(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        layout = QFormLayout(self.central_widget)
        self.central_widget.setLayout(layout)

        self.ogr_file = QLineEdit("Soubor nevybrán.")
        self.ogr_file.setReadOnly(True)

        self.file_selector = FileSelector()
        self.file_selector.fileSelected.connect(self.check_is_ogr_ds)
        self.file_selector.fileCleared.connect(self.file_deselected)

        self.table_label = QLabel("Informační tabulka o vrstvách")
        self.table = QTableView(self)
        self.table.setModel(self.table_model)

        layout.addRow("Vyberte soubor:", self.file_selector)
        layout.addRow("OGR soubor?", self.ogr_file)
        layout.addWidget(self.table_label)
        layout.addWidget(self.table)

    def file_deselected(self) -> None:
        self.ogr_file.setText("Soubor nevybrán.")
        self.table_model.set_ds(None)

    def check_is_ogr_ds(self, file_name: str) -> None:
        self.ds = ogr.Open(file_name)
        if self.ds:
            self.ogr_file.setText("Ano. Datasource obsahuje {} vrstev.".format(
                self.ds.GetLayerCount()))
            self.table_model.set_ds(self.ds)
        else:
            self.ogr_file.setText("Ne.")


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
