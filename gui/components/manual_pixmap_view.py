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

        self.setFixedSize(pixmap.size())
        self.update()

    def set_maker(self, pos:QPoint):
        old_pos = self.maker_position
        self.maker_position = pos

        #优化
        if old_pos:
            self.update(0, old_pos.y()-2, self.width(), 4)  # 旧的水平线
            self.update(old_pos.x()-2, 0, 4, self.height())  # 旧的垂直线
        
        self.update(0, pos.y()-2, self.width(), 4)  # 新的水平线
        self.update(pos.x()-2, 0, 4, self.height())  # 新的垂直线
            

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

            painter.drawLine(0,y_position,self.width(),y_position)
            painter.drawLine(x_position,0,x_position,self.height())



    

    




