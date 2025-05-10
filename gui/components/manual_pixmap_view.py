from PyQt6.QtWidgets import QLabel
from PyQt6.QtGui import QPixmap, QPainter, QPen, QColor
from PyQt6.QtCore import QPoint
from core.log_manager import log_info

class ManualPixmapView(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.base_pixmap = None
        self.maker_position = None

    def set_base_pixmap(self, pixmap:QPixmap):
        self.base_pixmap = pixmap

        log_info("----在ManualPixmapView中set_base_pixmap----")
        log_info(f"base_pixmap的尺寸：{pixmap.size()}")
        log_info("----在ManualPixmapView中set_base_pixmap----")

        self.setFixedSize(pixmap.size())
        self.update()

    def set_maker(self, pos:QPoint):
        self.maker_position = pos
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)

        if self.base_pixmap:
            #绘制base_pixmap
            painter.drawPixmap(0,0,self.base_pixmap)

        if self.maker_position:
            #绘制maker_position
            painter.setPen(QPen(QColor(255,0,0),2))
            x_position = self.maker_position.x()
            y_position = self.maker_position.y()

            log_info(f"maker_position的坐标：x:{x_position}, y:{y_position}")

            painter.drawLine(0,y_position,self.width(),y_position)
            painter.drawLine(x_position,0,x_position,self.height())



    

    




