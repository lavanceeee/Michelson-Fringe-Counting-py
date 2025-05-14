from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout
import pyqtgraph as pg
from core.log_manager import log_info

"""
亮度检测可视化区域
"""

class FigureView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setup_ui()

        self.average_brightness = 0
        self.center_brightness_save = []
        self.time_save = []

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
            pen = pg.mkPen('r', width=3),
            name = 'center lightness'
        )

        #图例
        self.plot_widget.addLegend()

        main_layout.addWidget(self.plot_widget)
        self.setLayout(main_layout)

    def init_average_brightness_data(self, average_brightness):
        self.average_brightness = average_brightness

        avg_line = pg.InfiniteLine(
            pos = self.average_brightness,
            angle = 0,
            pen=pg.mkPen('b', width=3, style=Qt.PenStyle.DashLine),
            label=f'平均亮度: {average_brightness:.2f}',
            labelOpts={
            'position': 0.1,             # 标签位置 (左侧10%)
            'color': (0, 0, 255),        # 蓝色文字
            'fill': (200, 200, 200, 50), # 半透明背景
            'movable': True              # 允许用户移动标签位置
            }
        )

        self.plot_widget.addItem(avg_line)

    def update_point_data(self, brightness, time):

        log_info("----进入组件更新点数据----")
        log_info(f"当前中心亮度: {brightness}")
        log_info(f"当前时间: {time}")

        self.center_brightness_save.append(brightness)
        self.time_save.append(time)

        self.center_curve.setData(self.time_save, self.center_brightness_save)

        if time > 1:
            self.plot_widget.setXRange(max(0, time-20), time+2)














        



        


