from typing import List

from PyQt5.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QTreeView)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt

from ...model.data import SpatialData


class DeleteLayersDialog(QDialog):

    def __init__(self, spatial_data: SpatialData, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Vymazat vrstvy z datového zdroje")

        self._spatial_data = spatial_data

        layout = QFormLayout()
        self.setLayout(layout)

        self.treeview = QTreeView()
        self.model = QStandardItemModel()
        self.model.setColumnCount(1)
        self.model.setHeaderData(0, Qt.Horizontal, "Vrstvy")
        self.root = self.model.invisibleRootItem()
        self.treeview.setModel(self.model)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout.addRow("Vrstvy ke smazání:", self.treeview)
        layout.addRow(self.button_box)

        for layer_name in self._spatial_data.layers_names:
            item = QStandardItem()
            item.setData(layer_name, Qt.ItemDataRole.DisplayRole)
            item.setCheckable(True)
            self.root.appendRow(item)

    @property
    def layers_to_delete(self) -> List[str]:
        to_delete = []
        for i in range(self.model.rowCount()):
            item = self.root.child(i)
            if item.checkState() == Qt.CheckState.Checked:
                to_delete.append(item.data(Qt.ItemDataRole.DisplayRole))
        return to_delete
