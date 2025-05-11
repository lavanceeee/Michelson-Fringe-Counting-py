from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QDialog
from PyQt6.QtCore import Qt
from core.log_manager import log_warning, log_info, log_error, log_debug
from PyQt6.QtCore import pyqtSignal
from gui.dialogs.manual_calibration_dialog import ManualCalibrationDialog

class FunctionView(QWidget):
    #添加检测圆环的信号
    detect_circles_signal = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)

        #创建manual_calibration_dialog实例
        self.manual_calibration_dialog = ManualCalibrationDialog(self)

        self.setup_ui()
        
        self.is_detecting = False
        self._current_frame = None

        #标定中心
        self.current_center = [0, 0]

    def setup_ui(self):
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)

        # 设置功能区大小
        self.setFixedSize(250, 250)
        
        self.setStyleSheet("""
            QLabel#warningLabel {
                color: #d9534f; 
                font-size: 12px;
                border: none; 
                margin-left: 5px; 
            }
        """)

        # 创建主布局 (垂直)
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft) 
        main_layout.setContentsMargins(10, 10, 20, 20) 

        # 创建水平布局用于按钮和警告文字
        first_line_layout = QHBoxLayout()
        first_line_layout.setSpacing(10)  # 设置按钮和文字之间的间距
        
        # 创建按钮
        self.start_button = QPushButton("自动识别")
        self.start_button.setFixedSize(80, 30)
        font = self.start_button.font()
        font.setPointSize(10)
        self.start_button.setFont(font)

        # 创建警告标签
        self.warning_label = QLabel("请先传入干涉图像")
        self.warning_label.setObjectName("warningLabel")  # 设置对象名，便于应用样式

        # 手动识别按钮
        self.manual_button = QPushButton("手动识别")
        self.manual_button.setFixedSize(80, 30)
        self.manual_button.setFont(font)

        # 开启检测按钮
        self.start_detection_button = QPushButton("开启检测")
        self.start_detection_button.setFixedSize(80, 30)
        self.start_detection_button.setFont(font)

        # 初始状态禁用按钮
        self.start_button.setEnabled(False)
        self.manual_button.setEnabled(False)
        self.start_detection_button.setEnabled(False)

        # 鼠标悬浮效果复用
        hover_style = """
            QPushButton:hover {
                background-color: #e0e0e0;
            }
            QPushButton:disabled {
                color: #999999;
                background-color: #f0f0f0;                            
            }
        """

        self.start_button.setStyleSheet(hover_style)
        self.manual_button.setStyleSheet(hover_style)
        self.start_detection_button.setStyleSheet(hover_style)

        # 添加控件到水平布局
        first_line_layout.addWidget(self.start_button)
        first_line_layout.addWidget(self.warning_label)
        first_line_layout.addStretch()  # 添加弹性空间，使按钮和文字靠左对齐

        # 将水平布局添加到主布局
        main_layout.addLayout(first_line_layout)
        main_layout.addWidget(self.manual_button)
        main_layout.addWidget(self.start_detection_button)

        # 设置布局
        self.setLayout(main_layout)

        #连接点击开始检测按钮的点击事件
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.manual_button.clicked.connect(self.on_manual_button_clicked)
        # self.start_detection_button.clicked.connect(self.on_start_detection_button_clicked)

    #自动检测被点击
    def on_start_button_clicked(self):
        #处理点击事件
        #发送检测信号
        #.emit() 发送信号，触发信号的连接函数

        self.is_detecting = not self.is_detecting
        if self.is_detecting:
            self.start_button.setText("停止识别")
            log_info("开始识别圆环")
        else:
            self.start_button.setText("开启识别")
            log_warning("手动停止识别")

        self.detect_circles_signal.emit(self.is_detecting)

    #获取当前帧
    def current_frame(self, pixmap):
        self._current_frame = pixmap
        
    #手动检测点击函数
    def on_manual_button_clicked(self):

        self.is_detecting = not self.is_detecting
        
        try:

            if self.is_detecting and self._current_frame:

                #设置当前帧
                self.manual_calibration_dialog.set_frame(self._current_frame)
                
                self.manual_calibration_dialog.show()

                if self.manual_calibration_dialog.exec() == QDialog.DialogCode.Accepted:
                    self.current_center = self.manual_calibration_dialog.xy_position
                    log_debug(f"用户标定数据{self.current_center}成功存储到function_view")
            else:
                log_info("退出手动定位圆心模式")
        except Exception as e:
            log_error(f"手动检测点击函数出错：{e}")

    # def on_start_detection_button_clicked(self):



    def set_camera_connected(self, is_connected):
        """根据摄像头连接状态设置按钮状态和提示标签可见性"""
        self.start_button.setEnabled(is_connected)
        self.manual_button.setEnabled(is_connected)
        self.warning_label.setVisible(not is_connected)  # 当摄像头连接时隐藏警告

