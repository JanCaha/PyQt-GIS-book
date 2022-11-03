from typing import Optional
from enum import Enum

from PyQt5.QtWidgets import (QWidget, QTabWidget, QFormLayout, QLineEdit, QListWidget, QComboBox,
                             QVBoxLayout, QListWidgetItem)
from PyQt5.QtCore import pyqtSignal

from .fileselect import FileSelectWidget
from ...model.enums import DataType
from ...model.data import SpatialData
from ...settings.appsettings import ApplicationSettings


class Tabs(Enum):
    DATASOURCE = 0
    LAYER = 1


class MainWidget(QWidget):

    dataSourceLoaded = pyqtSignal()

    text_not_identified = "Neidentifikován!"

    def __init__(self, spatial_data: SpatialData, parent: Optional['QWidget'] = None) -> None:
        super().__init__(parent)

        self._spatial_data = spatial_data
        self._spatial_data.dataChanged.connect(self.set_datasource_info)
        self._spatial_data.layersChanged.connect(self.set_layers)
        self._spatial_data.layersChanged.connect(self.set_datasource_info)

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.tabs.addTab(self.create_tab_datasource(), "Zdroj dat")
        self.tabs.addTab(self.create_tab_layers(), "Vrstvy")
        self.tabs.setTabEnabled(Tabs.LAYER.value, False)

        self.settings = ApplicationSettings()

    def create_tab_datasource(self) -> QWidget:

        self.widget_datasource = QWidget(self.tabs)
        layout = QFormLayout()
        self.widget_datasource.setLayout(layout)

        self.file_select = FileSelectWidget(self)
        self.file_select.fileSelected.connect(self._spatial_data.read_data)

        self.driver_name = QLineEdit(self)
        self.driver_name.setReadOnly(True)
        self.driver_name.setText(self.text_not_identified)

        self.elements_count = QLineEdit(self)
        self.elements_count.setReadOnly(True)
        self.elements_count.setText("0")

        layout.addRow("Zvolte soubor:", self.file_select)
        layout.addRow("Identifikovaný GDAL/OGR driver:", self.driver_name)
        layout.addRow("Počet prvků v datové sadě:", self.elements_count)

        return self.widget_datasource

    def create_tab_layers(self) -> QWidget:

        self.widget_layers = QWidget(self.tabs)
        layout = QFormLayout()
        self.widget_layers.setLayout(layout)

        self.layer_selection = QComboBox()
        self.layer_selection.currentIndexChanged.connect(self.get_layer_info)

        self.crs_name = QLineEdit(self)
        self.crs_name.setReadOnly(True)
        self.crs_name.setText(self.text_not_identified)

        self.feature_count = QLineEdit(self)
        self.feature_count.setReadOnly(True)
        self.feature_count.setText("0")

        self.fields = QListWidget()
        # self.fields.setSelectionMode(QListWidget.SelectionMode.MultiSelection)

        layout.addRow("Vrstva:", self.layer_selection)
        layout.addRow("Identifikovaný CRS:", self.crs_name)
        layout.addRow("Atributy:", self.fields)
        layout.addRow("Počet prvků:", self.feature_count)

        return self.widget_layers

    def set_datasource_info(self) -> None:
        self.driver_name.setText(self._spatial_data.driver_name)
        if self._spatial_data.data_type == DataType.VECTOR:
            self.tabs.setTabEnabled(Tabs.LAYER.value, True)
            self.elements_count.setText(f"{len(self._spatial_data.layers_names)} vrstvy/vrstev")
            self.set_layers()
        if self._spatial_data.data_type == DataType.RASTER:
            self.tabs.setTabEnabled(Tabs.LAYER.value, False)
            self.elements_count.setText(
                f"{len(self._spatial_data.layers_names)} pásem")  # TODO fix

    def get_layer_info(self):
        layer_name = self.layer_selection.currentText()
        if layer_name != "":
            self.set_crs(layer_name)
            self.feature_count.setText(str(self._spatial_data.read_feature_count(layer_name)))
            self.set_fields(layer_name)
        else:
            self.crs_name.setText("")
            self.feature_count.setText("")
            self.fields.clear()

    def set_layers(self) -> None:
        self.layer_selection.clear()
        self.layer_selection.addItem("")
        self.layer_selection.addItems(self._spatial_data.layers_names)

    def set_crs(self, layer_name: str) -> None:
        crs = self._spatial_data.identify_crs(layer_name)
        if crs is None:
            crs = self.text_not_identified
        self.crs_name.setText(crs)

    def set_fields(self, layer_name: str):
        self.fields.clear()

        for field in self._spatial_data.read_fid_field(layer_name):
            self.fields.addItem(QListWidgetItem(field))

        self.fields.addItem(QListWidgetItem("---"))

        for field in self._spatial_data.read_geometry_fields(layer_name):
            self.fields.addItem(QListWidgetItem(field))

        self.fields.addItem(QListWidgetItem("---"))

        for field in self._spatial_data.read_attribute_fields(layer_name):
            self.fields.addItem(QListWidgetItem(field))
