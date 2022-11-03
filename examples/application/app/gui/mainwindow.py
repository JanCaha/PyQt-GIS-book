from PyQt5.QtWidgets import (QMainWindow, QDialog, QMenu, QAction, QApplication)

from .dialogs.copydialog import CopyLayerDialog
from .dialogs.deletedialog import DeleteLayersDialog
from .dialogs.exportlayerdialog import ExportLayerDialog
from .widgets.mainwidget import MainWidget
from ..model.data import SpatialData


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setWindowTitle("GIS Data Information Application")
        self.setMinimumSize(500, 500)

        self._spatial_data = SpatialData()

        self.init_menu()

        self.main_widget = MainWidget(self._spatial_data, self)
        self._spatial_data.dataChanged.connect(self.enable_operations)

        self.setCentralWidget(self.main_widget)

    def init_menu(self) -> None:

        menu_operations = QMenu('Operace', self)
        self.menuBar().addMenu(menu_operations)

        menu_about = QMenu("O Aplikaci", self)
        self.menuBar().addMenu(menu_about)

        self.action_quit = QAction("Ukončit aplikaci", self)
        self.action_quit.setStatusTip("Ukončí aplikaci.")
        self.action_quit.triggered.connect(self.quit_application)
        self.action_quit.setEnabled(True)
        menu_about.addAction(self.action_quit)

        self.action_copy_layer_SQL = QAction("Kopírovat data", self)
        self.action_copy_layer_SQL.setStatusTip("Kopírovat data do nové vrstvy pomocí SQL")
        self.action_copy_layer_SQL.triggered.connect(self.copy_SQL_layer)
        self.action_copy_layer_SQL.setEnabled(False)
        menu_operations.addAction(self.action_copy_layer_SQL)

        self.action_export_layer = QAction("Exportovat vrstvu", self)
        self.action_export_layer.setStatusTip("Exportovat vrstvu do souboru")
        self.action_export_layer.triggered.connect(self.export_layer_to_file)
        self.action_export_layer.setEnabled(False)
        menu_operations.addAction(self.action_export_layer)

        self.action_delete_layer = QAction("Smazat vrstvy", self)
        self.action_delete_layer.setStatusTip("Smazat vrstvy z datového zdroje")
        self.action_delete_layer.triggered.connect(self.delete_layers)
        self.action_delete_layer.setEnabled(False)
        menu_operations.addAction(self.action_delete_layer)

    def enable_operations(self):
        self.action_copy_layer_SQL.setEnabled(self._spatial_data.ds_allow_create_layer)
        self.action_delete_layer.setEnabled(self._spatial_data.ds_allow_delete_layer)
        self.action_export_layer.setEnabled(self._spatial_data.is_vector)

    def copy_SQL_layer(self) -> None:

        dialog = CopyLayerDialog(self._spatial_data)

        result = dialog.exec()

        if result == QDialog.Accepted:
            self._spatial_data.sql_layer_to_layer(dialog.name_new_layer)

    def delete_layers(self) -> None:

        dialog = DeleteLayersDialog(self._spatial_data)

        result = dialog.exec()

        if result == QDialog.Accepted:
            self._spatial_data.delete_layers(dialog.layers_to_delete)

    def export_layer_to_file(self) -> None:

        dialog = ExportLayerDialog(self._spatial_data)

        result = dialog.exec()

        if result == QDialog.Accepted:
            self._spatial_data.export_layer(dialog.selected_layer, dialog.result_file_name)

    def showMessage(self, msg: str, timeout: int = 2000) -> None:
        self.statusBar().showMessage(msg, timeout)

    def quit_application(self) -> None:
        QApplication.exit(0)
