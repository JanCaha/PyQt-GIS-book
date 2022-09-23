from typing import Optional, Union
import sys
from enum import Enum

from PyQt5.QtWidgets import QWidget, QApplication, QToolTip
from PyQt5.QtCore import Qt, QRect, QEvent, QPointF
from PyQt5.QtGui import QPainter, QBrush, QColor, QPaintEvent, QPen, QMouseEvent


class LightStatus(Enum):
    RED = 1
    ORANGE1 = 2
    GREEN = 3
    ORANGE2 = 4

    def next(self):
        v = self.value
        if v == 4:
            return LightStatus.RED
        return LightStatus(v + 1)

    def prev(self):
        v = self.value
        if v == 1:
            return LightStatus.ORANGE2
        return LightStatus(v - 1)


class TrafficLight(QWidget):

    def __init__(self,
                 light_status: LightStatus = LightStatus.GREEN,
                 read_only: bool = False,
                 parent: Optional[QWidget] = None,
                 flags: Union[Qt.WindowFlags, Qt.WindowType] = Qt.WindowType.Widget) -> None:
        super().__init__(parent, flags)
        self._light_status = light_status
        self._read_only = read_only
        self._color_red = QColor('#D60000')
        self._color_orange = QColor('#D6B100')
        self._color_green = QColor('#00AE23')
        self._darken_by = 300
        self._circle_radius: float = None
        self._vertical_offset: float = None

    def circle_radius(self) -> int:
        return min(self.height() * 0.3, self.width() * 0.9)

    def drawCircle(self, painter: QPainter, center: QPointF, radius: float, color: QColor) -> None:
        painter.save()

        painter.setRenderHint(QPainter.Antialiasing)
        painter.setRenderHint(QPainter.HighQualityAntialiasing)

        brush = QBrush()
        brush.setColor(color)
        brush.setStyle(Qt.SolidPattern)

        pen = QPen(Qt.NoPen)

        painter.setBrush(brush)
        painter.setPen(pen)

        painter.drawEllipse(center, radius, radius)
        painter.restore()

    def color_status(self, color: QColor, turned_off_status: bool) -> QColor:
        if turned_off_status:
            color = color.darker(self._darken_by)
        return color

    @property
    def red_color(self) -> QColor:
        return self.color_status(self._color_red, self._light_status != LightStatus.RED)

    @property
    def orange_color(self) -> QColor:
        return self.color_status(
            self._color_orange, self._light_status
            not in [LightStatus.ORANGE1, LightStatus.ORANGE2])

    @property
    def green_color(self) -> QColor:
        return self.color_status(self._color_green, self._light_status != LightStatus.GREEN)

    def checkedState(self) -> Qt.CheckState:
        if self._light_status == LightStatus.GREEN:
            return Qt.Checked
        if self._light_status == LightStatus.RED:
            return Qt.Unchecked
        if self._light_status in [LightStatus.ORANGE1, LightStatus.ORANGE2]:
            return Qt.PartiallyChecked

    def setReadOnly(self, readOnly: bool) -> None:
        self._read_only = readOnly

    def readOnly(self) -> bool:
        return self._read_only

    def _rectangle(self, circle_radius: float, vertical_offset: float) -> QRect:
        diameter = circle_radius * 2
        return QRect(int(self.width() / 2 - circle_radius - vertical_offset), int(0),
                     int(diameter + 2 * vertical_offset), int(diameter * 3 + vertical_offset * 4))

    def main_shape(self) -> QRect:
        return self._rectangle(self._circle_radius, self._vertical_offset)

    def calculate_sizes(self) -> None:
        if self.height() * 0.3 < self.width() * 0.9:
            self._circle_radius = (self.height() * 0.3) / 2
            self._vertical_offset = (self.height() * 0.1) / 4
        else:
            self._circle_radius = (self.width() * 0.9) / 2
            self._vertical_offset = (self._circle_radius / 3) / 4

    def paintEvent(self, e: QPaintEvent):

        painter = QPainter(self)

        self.calculate_sizes()

        painter.save()

        brush = QBrush()
        brush.setColor(QColor('black'))
        brush.setStyle(Qt.SolidPattern)

        painter.fillRect(self.main_shape(), brush)

        painter.restore()

        width_midpoint = self.width() / 2

        self.drawCircle(painter,
                        QPointF(width_midpoint, self._vertical_offset + self._circle_radius),
                        self._circle_radius, self.red_color)

        self.drawCircle(
            painter,
            QPointF(width_midpoint,
                    self._vertical_offset * 2 + self._circle_radius + self._circle_radius * 2),
            self._circle_radius, self.orange_color)

        self.drawCircle(
            painter,
            QPointF(width_midpoint,
                    self._vertical_offset * 3 + self._circle_radius * 4 + self._circle_radius),
            self._circle_radius, self.green_color)

    def event(self, event: QEvent) -> bool:

        if event.type() == QEvent.ToolTip:
            if self.main_shape().contains(event.pos()):
                tooltip = ""
                if self._light_status == LightStatus.RED:
                    tooltip = "Red"
                if self._light_status == LightStatus.GREEN:
                    tooltip = "Green"
                if self._light_status in [LightStatus.ORANGE1, LightStatus.ORANGE2]:
                    tooltip = "Orange"
                QToolTip.showText(event.globalPos(), tooltip)
            else:
                QToolTip.hideText()

        elif event.type() == QEvent.Leave:
            QToolTip.hideText()

        return super().event(event)

    def mouseReleaseEvent(self, a0: QMouseEvent) -> None:
        if not self._read_only:
            if a0.button() == Qt.LeftButton:
                self._light_status = self._light_status.next()
            if a0.button() == Qt.RightButton:
                self._light_status = self._light_status.prev()
            self.update()
        return super().mouseReleaseEvent(a0)


if __name__ == "__main__":

    app = QApplication([])
    w = TrafficLight()
    w.show()
    sys.exit(app.exec())
