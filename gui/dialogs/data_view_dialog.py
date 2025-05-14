from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout,QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from algorithm.figure_N import FigureN
from core.log_manager import log_debug


class DataViewDialog(QDialog):
    def __init__(self, parent=None, center_brightness_save=None, time_save=None):
        super().__init__(parent)

        self.center_brightness_save = center_brightness_save
        self.time_data = time_save

        self.setup_ui()

        self.result_N = 0

        self.threshold = 0

        #为计算N单独开一个方法
        self.calculate_N()

         #加载图表数据
        self.load_plot_data(self.center_brightness_save, self.time_data)

    def setup_ui(self):
        self.setWindowTitle("数据查看")
        self.setFixedSize(800, 400)

        #主功能区域

        main_layout = QVBoxLayout()

        self.first_line_layout = QHBoxLayout()

        #1.1 左侧的图表显示
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        #size
        self.plot_widget.setFixedSize(500, 250)
        self.first_line_layout.addWidget(self.plot_widget)

        #1.2 右侧的数据展示区域
        self.result_data_layout = QVBoxLayout()

        self.result_N_label = QLabel("N值：")

        self.result_N_value = QLabel("N/A")

        self.result_data_layout.addWidget(self.result_N_label)
        self.result_data_layout.addWidget(self.result_N_value)

        self.result_data_layout.addStretch()

        self.first_line_layout.addLayout(self.result_data_layout)

        main_layout.addLayout(self.first_line_layout)
        
        self.setLayout(main_layout)


    def calculate_N(self):
        if self.center_brightness_save is not None:
            try:
                self.result_N, self.threshold = FigureN.figureN(self.center_brightness_save)
                self.result_N_value.setText(str(self.result_N))

                log_debug(f"显示页面的N值为{self.result_N}")
            except Exception as e:
                log_debug(f"计算N值时发生错误: {e}")

    #可视化数据
    def load_plot_data(self, center_brightness_save, time_data):

        # 绘制中心亮度数据
        self.plot_widget.clear()
        self.plot_widget.plot(time_data, center_brightness_save, pen=pg.mkPen('r', width=2), name='中心亮度')
        
        # 添加平均亮度线
        if self.threshold is not None:
            self.plot_widget.addLine(y=self.threshold, pen=pg.mkPen('b', width=2, style=Qt.PenStyle.DashLine), name='平均亮度')
        
        # 设置坐标轴标签
        self.plot_widget.setLabel('left', '亮度')
        self.plot_widget.setLabel('bottom', '帧')
        self.plot_widget.addLegend()


        

        

        

        

        










    