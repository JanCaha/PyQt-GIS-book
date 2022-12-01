from PyQt5.QtWidgets import (QDialog, QFormLayout, QDialogButtonBox, QPlainTextEdit, QLineEdit,
                             QComboBox)
from PyQt5.QtCore import pyqtSignal

from ...model.data import SpatialData


class CopyLayerDialog(QDialog):

    newLayerCopied = pyqtSignal()

    def __init__(self, spatial_data: SpatialData, parent=None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Vytvořit vrstvu jako výsledek SQL dotazu")

        layout = QFormLayout()
        self.setLayout(layout)

        self._spatial_data = spatial_data

        self.sql_layer = None

        self.new_layer_name = QLineEdit("")
        self.sql_query = QPlainTextEdit("")
        self.sql_query.textChanged.connect(self.execute_SQL)
        self.sql_type = QComboBox()
        self.sql_type.addItems(["OGRSQL", "SQLITE"])
        self.sql_error = QPlainTextEdit()
        self.sql_error.setFixedHeight(50)
        self.sql_error.setReadOnly(True)
        self.number_of_features = QLineEdit()
        self.number_of_features.setReadOnly(True)

        self.sql_type.currentIndexChanged.connect(self.execute_SQL)
        self.new_layer_name.textChanged.connect(self.enable_ok)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.button_box.button(QDialogButtonBox.Ok).setDisabled(True)

        layout.addRow("Název nové vrstvy:", self.new_layer_name)
        layout.addRow("SQL dotaz:", self.sql_query)
        layout.addRow("Typ SQL:", self.sql_type)
        layout.addRow("Chyba SQL:", self.sql_error)
        layout.addRow("Počet vybraných prvků:", self.number_of_features)
        layout.addWidget(self.button_box)

    def execute_SQL(self) -> None:
        self._spatial_data.execute_sql(self.sql_query.toPlainText(),
                                       sql_flavor=self.sql_type.currentText())
        self.number_of_features.setText(str(self._spatial_data.sql_layer_feature_count))
        self.sql_error.setPlainText(self._spatial_data.sql_error)

    def enable_ok(self) -> None:
        text = self.new_layer_name.text()
        usable_name = 0 < len(text)
        self.button_box.button(QDialogButtonBox.Ok).setDisabled(
            not usable_name and 1 > self._spatial_data.sql_layer_feature_count)

    @property
    def name_new_layer(self) -> str:
        return self.new_layer_name.text()
