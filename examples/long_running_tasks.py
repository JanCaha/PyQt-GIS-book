from typing import Optional
import time
from datetime import datetime
import uuid
import sys

from PyQt5.QtCore import (QRunnable, pyqtSignal, QObject, QThreadPool)
from PyQt5.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QPushButton, QPlainTextEdit,
                             QApplication)


class WorkerSignals(QObject):
    finished = pyqtSignal()
    percentDone = pyqtSignal(str, float)
    result = pyqtSignal(str)


class Worker(QRunnable):

    def __init__(self, job_name: str):
        super(Worker, self).__init__()
        self.signal = WorkerSignals()
        self.job_name = job_name

    def run(self):
        for i in range(10):
            time.sleep(1)
            self.signal.percentDone.emit(self.job_name, (i / 10) * 100)
        self.signal.finished.emit()
        self.signal.result.emit("Job `{}` is done.".format(self.job_name))


class MainWindow(QMainWindow):

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self.setWindowTitle("Long Running Tasks")
        self.setMinimumSize(500, 200)

        widget = QWidget(self)
        self.setCentralWidget(widget)

        layout = QVBoxLayout()
        widget.setLayout(layout)

        self.button_test_interactivity = QPushButton("Test Interactivity", self)
        self.button_test_interactivity.clicked.connect(self.interactivity_clicked)

        self.text_field_interactivity = QPlainTextEdit(self)
        self.text_field_interactivity.setReadOnly(True)

        self.button_long_task = QPushButton("Create Long Running Taks", self)
        self.button_long_task.clicked.connect(self.run_long_task)

        self.button_worker = QPushButton("Create Worker", self)
        self.button_worker.clicked.connect(self.run_worker)

        self.text_field_worker = QPlainTextEdit(self)
        self.text_field_worker.setReadOnly(True)

        layout.addWidget(self.button_test_interactivity)
        layout.addWidget(self.text_field_interactivity)
        layout.addWidget(self.button_long_task)
        layout.addWidget(self.button_worker)
        layout.addWidget(self.text_field_worker)

        self.threadpool = QThreadPool()

    def interactivity_clicked(self) -> None:
        msg = "Clicked at: {}.".format(datetime.now())
        self.text_field_interactivity.setPlainText(msg)

    def run_long_task(self):
        for i in range(3):
            time.sleep(1)

    def run_worker(self):
        worker_id = str(uuid.uuid4()).split("-")[0]
        worker = Worker(worker_id)

        worker.signal.result.connect(self.print_worker_output)
        worker.signal.finished.connect(self.worker_finished)
        worker.signal.percentDone.connect(self.worker_percent_done)

        self.threadpool.start(worker)

    def print_worker_output(self, output: str):
        text = "{}\n{}".format(self.text_field_worker.toPlainText(), output)
        self.text_field_worker.setPlainText(text)

    def worker_finished(self):
        text = "{}\nWorker finished!".format(self.text_field_worker.toPlainText())
        self.text_field_worker.setPlainText(text)

    def worker_percent_done(self, worker_name: str, percent: float):
        msg = "Done {}%. ({})".format(percent, worker_name)
        text = "{}\n{}!".format(self.text_field_worker.toPlainText(), msg)
        self.text_field_worker.setPlainText(text)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    mw = MainWindow()
    mw.show()
    sys.exit(app.exec())
