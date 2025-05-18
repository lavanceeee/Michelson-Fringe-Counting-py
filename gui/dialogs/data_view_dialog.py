from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout,QLabel,QFrame,QPushButton,QFileDialog
from PyQt6.QtCore import Qt
import pyqtgraph as pg
from core.log_manager import log_debug
from gui.elements.select_dialog import SelectDialog
from thread.data_export_thread import DataExportThread
from datetime import datetime


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
        self.plot_frame = QFrame()
        self.plot_frame.setFixedSize(400, 250)
        self.plot_frame.setObjectName("plot_frame") #类名
        plot_layout = QVBoxLayout(self.plot_frame)

        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground('w')
        #size
        self.plot_widget.setFixedSize(380, 230)
        #设置样式
        self.plot_widget.setBackground('w')
        self.plot_widget.setStyleSheet("""
            QWidget {
                background-color: white;
                border-radius: 5px;
            }
        """)
        plot_layout.addWidget(self.plot_widget)

        #plot在frame居中显示
        plot_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.first_line_layout.addWidget(self.plot_frame)

        #1.2 右侧的数据展示区域
        self.function_frame = QFrame()
        self.function_frame.setFixedSize(200, 250)
        self.function_frame.setObjectName("function_frame") #类名
        function_layout = QVBoxLayout(self.function_frame)
        self.result_N_value = QLabel(f"N值：{self.result_N}")

        function_layout.addWidget(self.result_N_value)
        function_layout.addStretch() #拉伸

        #通用样式
        StyleSheet = """
            #plot_frame {
                border: 2px solid #666666;
                border-radius: 5px;
            }
            #function_frame {
                border: 2px solid #666666;
                border-radius: 5px;
            }
            #bottom_function_frame {
                border: 2px solid #666666;
                border-radius: 5px;
            }
        """

        self.setStyleSheet(StyleSheet)

        self.first_line_layout.addWidget(self.function_frame) 

        self.first_line_layout.setSpacing(10)

        self.second_line_layout = QHBoxLayout()
        self.bottom_function_frame = QFrame()
        
        #底部功能区
        self.bottom_function_frame.setFixedSize(610, 90)
        self.bottom_function_frame.setObjectName("bottom_function_frame") #类名
        bottom_function_layout = QHBoxLayout(self.bottom_function_frame)

        #数据导出按钮
        self.export_data_button = QPushButton("数据导出")
        self.export_data_button.setFixedSize(80, 30)
        bottom_function_layout.addWidget(self.export_data_button)

        self.second_line_layout.addWidget(self.bottom_function_frame)

        self.export_data_button.clicked.connect(self.export_data)

        #主功能区
        main_layout.addLayout(self.first_line_layout)
        main_layout.addLayout(self.second_line_layout)

        #在主布局中左右居中
        main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.setLayout(main_layout)

    #可视化数据
    def load_plot_data(self):
        # 清空图表
        self.plot_widget.clear()
        
        if self.smoothed_data is not None:
            self.plot_widget.plot(self.time_data, self.smoothed_data, 
                                 pen=pg.mkPen('r', width=2), name='smoothed brightness')
        
        # 添加阈值线
        if self.threshold is not None:
            self.plot_widget.addLine(y=self.threshold, 
                                   pen=pg.mkPen('b', width=2, style=Qt.PenStyle.DashLine), 
                                   name='threshold')
        
        # 设置图表标签
        self.plot_widget.setLabel('left', 'brightness')
        self.plot_widget.setLabel('bottom', 'frame')
        self.plot_widget.addLegend()


    def export_data(self):
        #弹出弹窗，选择需要导出的数据和类型
        data_type_select_dialog = SelectDialog(self)

        data_type_select_dialog.send_data_type_signal.connect(self.export_data_by_type) #连接到处理线程
        
        data_type_select_dialog.exec() #阻塞式

    def export_data_by_type(self, selected_data_types):

        save_path = []

        for data_type in selected_data_types:
                save_path = self.select_save_path(data_type)

                data_export_thread = DataExportThread(self, 
                                        data_type, 
                                        self.smoothed_data, 
                                        self.result_N, 
                                        self.threshold,
                                        save_path)
                data_export_thread.start()

    def select_save_path(self, data_type):
        timestamp = datetime.now().strftime("%d%H%M%S")

        file_type = data_type.split("(")[1].strip(")")
        file_name = f"result_data_N={self.result_N}_{timestamp}.{file_type}"
        save_path, _ = QFileDialog.getSaveFileName(self, "保存文件", file_name, f"{file_type}文件 (*.{file_type})")
        return save_path




        

        

        

        










    