from typing import Union, List
from pathlib import Path

from PyQt5.QtCore import QObject, pyqtSignal

from osgeo import gdal, ogr, osr

from .enums import DataType
from ..settings.appsettings import ApplicationSettings


class SpatialData(QObject):

    dataChanged = pyqtSignal()
    layersChanged = pyqtSignal()

    def __init__(self, filename: Union[Path, str] = None) -> None:
        super().__init__()

        if filename:
            self._path_data = Path(filename)

        self.data_type = DataType.NONE

        self.vector_ds: ogr.DataSource = None
        self.raster_ds: gdal.Dataset = None
        self.driver: gdal.Driver = None
        self._sql_layer: ogr.Layer = None

        self._last_sql_error: str = None

    @property
    def is_vector(self) -> bool:
        return self.data_type == DataType.VECTOR

    @property
    def path_data(self) -> str:
        return self._path_data.absolute().as_posix()

    def read_data(self, filename: Union[Path, str]) -> None:
        if filename:
            self._path_data = Path(filename)
            app = ApplicationSettings()
            app.setValue(app.data_folder_key, self._path_data.parent.as_posix())

        self._identify_driver()
        self._read_data()

    def _read_data(self) -> None:
        if self.driver:

            ds_ogr: ogr.DataSource = ogr.Open(self.path_data, True)

            if ds_ogr:
                self.data_type = DataType.VECTOR
                self.vector_ds = ds_ogr
                self.dataChanged.emit()
                return

            ds_gdal: gdal.Dataset = gdal.OpenEx(self.path_data)

            if ds_gdal:
                self.data_type = DataType.RASTER
                self.raster_ds = ds_gdal
                self.dataChanged.emit()
                return

    def _identify_driver(self) -> None:
        if self._path_data:
            if self._path_data.exists():
                self.driver = gdal.IdentifyDriver(self.path_data)

    @property
    def driver_name(self) -> str:
        if self.driver:
            return self.driver.LongName
        return None

    @property
    def ds_allow_create_layer(self) -> bool:
        if self.is_vector and self.vector_ds:
            return self.vector_ds.TestCapability(ogr.ODsCCreateLayer)
        return False

    @property
    def ds_allow_delete_layer(self) -> bool:
        if self.is_vector and self.vector_ds:
            return self.vector_ds.TestCapability(ogr.ODsCDeleteLayer)
        return False

    @property
    def layers_names(self) -> List[str]:

        layer_names = []

        if self.is_vector and self.vector_ds:
            for i in range(self.vector_ds.GetLayerCount()):
                lyr = self.vector_ds.GetLayerByIndex(i)
                layer_names.append(lyr.GetName())

        return layer_names

    @property
    def sql_error(self) -> str:
        return self._last_sql_error

    @property
    def sql_layer(self) -> ogr.Layer:
        return self._sql_layer

    @property
    def sql_layer_feature_count(self) -> int:
        if self._sql_layer:
            return self._sql_layer.GetFeatureCount()
        else:
            return -1

    def read_feature_count(self, layer_name: str) -> int:
        layer = self.vector_ds.GetLayerByName(layer_name)
        return layer.GetFeatureCount()

    def read_fid_field(self, layer_name: str) -> List[str]:
        fields = []
        layer = self.vector_ds.GetLayerByName(layer_name)
        fields.append(f"{layer.GetFIDColumn()} (FID column)")
        return fields

    def read_geometry_fields(self, layer_name: str) -> List[str]:
        fields = []

        layer = self.vector_ds.GetLayerByName(layer_name)

        layerDef: ogr.FeatureDefn = layer.GetLayerDefn()

        for i in range(layerDef.GetGeomFieldCount()):
            fieldDef: ogr.GeomFieldDefn = layerDef.GetGeomFieldDefn(i)
            fields.append(f"{fieldDef.GetName()} ({ogr.GeometryTypeToName(fieldDef.GetType())})")

        return fields

    def read_attribute_fields(self, layer_name: str) -> List[str]:
        fields = []

        layer = self.vector_ds.GetLayerByName(layer_name)

        layerDef: ogr.FeatureDefn = layer.GetLayerDefn()

        for i in range(layerDef.GetFieldCount()):
            fieldDef: ogr.FieldDefn = layerDef.GetFieldDefn(i)
            fields.append(f"{fieldDef.GetName()} ({fieldDef.GetTypeName()})")

        return fields

    def crs(self, layer_name: str) -> osr.SpatialReference:
        layer = self.vector_ds.GetLayerByName(layer_name)

        if layer:
            crs: osr.SpatialReference = layer.GetSpatialRef()
            if crs:
                return crs
            return None

    def identify_crs(self, layer_name: str) -> str:

        crs: osr.SpatialReference = self.crs(layer_name)

        if crs:
            authority = crs.GetAuthorityName(None)
            code = crs.GetAuthorityCode(None)

            if authority and code:
                return f"{authority}:{code}"
            else:
                return f"{crs.ExportToWkt()}"

        return None

    def delete_layer(self, layer_name: str) -> None:
        if layer_name in self.layers_names:
            self.vector_ds.DeleteLayer(layer_name)
            self.layersChanged.emit()

    def execute_sql(self, sql: str, sql_flavor: str) -> None:
        self._sql_layer = self.vector_ds.ExecuteSQL(sql, dialect=sql_flavor)
        if self._sql_layer is None:
            self._last_sql_error = gdal.GetLastErrorMsg()
        else:
            self._last_sql_error = None

    def sql_layer_to_layer(self, new_layer_name: str) -> None:
        if self._sql_layer:
            self.vector_ds.CopyLayer(self._sql_layer, new_layer_name, options=["OVERWRITE=YES"])
            self.layersChanged.emit()

    def export_layer(self, layer_name: str, file_name: str) -> None:
        gdal.VectorTranslate(file_name,
                             self.vector_ds.GetDescription(),
                             layers=[layer_name],
                             layerName=layer_name)
