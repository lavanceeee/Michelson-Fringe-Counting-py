from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout
import pyqtgraph as pg

"""
亮度检测可视化区域
"""

class FigureView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

        self.center_brightness_save = []
        self.x_values = []

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
        self.plot_widget.setXRange(0,1)

        #限制x轴的最小缩放
        self.plot_widget.setLimits(xMin=0)

        self.center_curve = self.plot_widget.plot(
            pen = pg.mkPen('b', width=3),
            name = 'center lightness'
        )

        #图例
        self.plot_widget.addLegend()

        main_layout.addWidget(self.plot_widget)
        self.setLayout(main_layout)


    def update_point_data(self, brightness):

        self.center_brightness_save.append(brightness)

        self.x_values = list(range(len(self.center_brightness_save)))

        self.center_curve.setData(self.x_values, self.center_brightness_save)















        



        


