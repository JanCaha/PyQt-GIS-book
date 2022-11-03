from typing import Optional, Union
import sys

from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect, QPointF
from PyQt5.QtGui import QPainter, QBrush, QColor, QPaintEvent, QPen


class CustomPaintWidget(QWidget):

    def __init__(self,
                 parent: Optional[QWidget] = None,
                 flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)

    def paintEvent(self, e: QPaintEvent):

        painter = QPainter(self)

        painter.save()

        brush = QBrush()
        brush.setColor(QColor("#ff0000"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        painter.fillRect(
            QRect(int(self.width() * 0.1), int(self.height() * 0.1), int(self.width() * 0.8),
                  int(self.height() * 0.8)), brush)

        painter.restore()

        painter.save()

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        brush = QBrush()
        brush.setColor(QColor("#00ff00"))
        brush.setStyle(Qt.BrushStyle.SolidPattern)

        pen = QPen(QColor("#0000ff"), Qt.PenStyle.SolidLine)

        painter.setBrush(brush)
        painter.setPen(pen)

        radius = min(self.width() / 4, self.height() / 4)

        painter.drawEllipse(QPointF(self.width() / 2, self.height() / 2), radius, radius)

        painter.restore()


if __name__ == "__main__":

    app = QApplication([])
    w = CustomPaintWidget()
    w.show()
    sys.exit(app.exec())
