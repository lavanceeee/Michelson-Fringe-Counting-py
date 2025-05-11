from PyQt6.QtWidgets import QPushButton
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout
import pyqtgraph as pg

"""
摄像头区域右侧的亮度检测可视化区域
"""

class FigureView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()


    def setup_ui(self):
        #设置背景
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        self.setFixedSize(500, 250)

        #主布局
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        main_layout.setContentsMargins(10, 10, 20, 20)

        #1. 绘图布局 plot_widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        self.plot_widget.setFixedHeight(220)

        self.plot_widget.showGrid(x=True, y=True)
        self.plot_widget.setLabel('left', 'light')
        self.plot_widget.setLabel('bottom', 'time')

        #设置初始x轴从0开始
        self.plot_widget.setXRange(0, 1)

        #限制x轴的最小缩放
        self.plot_widget.setLimits(xMin=0)

        main_layout.addWidget(self.plot_widget)

        self.setLayout(main_layout)







        



        


