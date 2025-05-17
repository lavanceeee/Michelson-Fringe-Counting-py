from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout,QLabel
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from core.log_manager import log_debug


class DataViewDialog(QDialog):
    def __init__(self, parent=None,smoothed_data=None, n=0, threshold=0):
        super().__init__(parent)

        self.smoothed_data = smoothed_data
        self.result_N = n  
        self.threshold = threshold 

        self.setup_ui()

        self.time_data = [i for i in range(len(self.smoothed_data))]
        
        # 加载图表数据
        self.load_plot_data()

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

        self.result_N_value = QLabel(f"N值：{self.result_N}")

        self.result_data_layout.addWidget(self.result_N_value)

        self.result_data_layout.addStretch()

        self.first_line_layout.addLayout(self.result_data_layout)

        main_layout.addLayout(self.first_line_layout)
        
        self.setLayout(main_layout)

            
    #可视化数据
    def load_plot_data(self):
        # 清空图表
        self.plot_widget.clear()
        
        if self.smoothed_data is not None:
            self.plot_widget.plot(self.time_data, self.smoothed_data, 
                                 pen=pg.mkPen('r', width=2), name='平滑后亮度')
        
        # 添加阈值线
        if self.threshold is not None:
            self.plot_widget.addLine(y=self.threshold, 
                                   pen=pg.mkPen('b', width=2, style=Qt.PenStyle.DashLine), 
                                   name='阈值')
        
        # 设置图表标签
        self.plot_widget.setLabel('left', '亮度')
        self.plot_widget.setLabel('bottom', '帧')
        self.plot_widget.addLegend()


        

        

        

        

        










    