from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QHBoxLayout, QDialog, QMessageBox
from PyQt6.QtCore import Qt, pyqtSignal
from torchgen.executorch.api.et_cpp import return_names

from core.alert_manager import alert_error, alert_warning
from core.log_manager import log_warning, log_info, log_error, log_debug
from gui.dialogs.manual_calibration_dialog import ManualCalibrationDialog

class FunctionView(QWidget):
    #添加检测圆环的信号
    detect_circles_signal = pyqtSignal(bool)

    #开始数条纹的信号
    start_count_signal = pyqtSignal(bool)

    #可以标记的信号
    clicked_and_can_mark_signal = pyqtSignal(bool, list)

    #数据清理信号
    data_clear_signal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.manual_calibration_dialog = ManualCalibrationDialog(self)

        self.setup_ui()

        self.is_detecting = False
        self.is_brightness_detecting = False
        self._current_frame = None
        self.is_connected = False

        #标定中心
        self.current_center = []

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
            QLabel#data_analyse_label {
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

        # 1.自动检测 创建水平布局用于按钮和警告文字
        first_line_layout = QHBoxLayout()
        first_line_layout.setSpacing(10)  # 设置按钮和文字之间的间距
        
        # 创建按钮
        self.start_button = QPushButton("自动识别")
        self.start_button.setFixedSize(80, 30)
        font = self.start_button.font()
        font.setPointSize(10)
        self.start_button.setFont(font)

        # 创建警告标签
        self.warning_label = QLabel("请先连接摄像头")
        self.warning_label.setObjectName("warningLabel")  # 设置对象名，便于应用样式

        # 添加控件到水平布局
        first_line_layout.addWidget(self.start_button)
        first_line_layout.addWidget(self.warning_label)
        first_line_layout.addStretch()  # 添加弹性空间，使按钮和文字靠左对齐

        # 2. 手动识别按钮
        self.manual_button = QPushButton("手动识别")
        self.manual_button.setFixedSize(80, 30)
        self.manual_button.setFont(font)

        # 3.开启检测按钮
        self.start_detection_button = QPushButton("开启检测")
        self.start_detection_button.setFixedSize(80, 30)
        self.start_detection_button.setFont(font)

        self.data_analyse_label = QLabel("本次统计已结束，可以查看详细数据并导出")
        #允许换行
        self.data_analyse_label.setWordWrap(True)
        self.data_analyse_label.setObjectName("data_analyse_label")
        
        #初始时不可见
        self.data_analyse_label.setVisible(False)

        # 4. 数据清除按钮
        self.data_clear_button = QPushButton("数据清理")
        self.data_clear_button.setFixedSize(80, 30)
        self.data_clear_button.setFont(font)

        # 初始状态禁用按钮
        self.start_button.setEnabled(False)
        self.manual_button.setEnabled(False)
        self.start_detection_button.setEnabled(False)
        self.data_clear_button.setEnabled(False)

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
        self.data_clear_button.setStyleSheet(hover_style)

        # 将水平布局添加到主布局
        main_layout.addLayout(first_line_layout)
        main_layout.addWidget(self.manual_button)
        main_layout.addWidget(self.start_detection_button)
        main_layout.addWidget(self.data_analyse_label)
        main_layout.addWidget(self.data_clear_button)

        # 设置布局
        self.setLayout(main_layout)

        #连接点击开始检测按钮的点击事件
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.manual_button.clicked.connect(self.on_manual_button_clicked)
        self.start_detection_button.clicked.connect(self.on_start_detection_button_clicked)
        self.data_clear_button.clicked.connect(self.on_data_clear_button_clicked)

    #自动检测被点击
    def on_start_button_clicked(self):

        self.is_detecting = not self.is_detecting
        if self.is_detecting:
            self.start_button.setText("停止识别")
            log_info("即将开始自动识别圆环")
        else:
            self.start_button.setText("开启识别")
            log_info("已经手动停止自动识别")

        self.detect_circles_signal.emit(self.is_detecting)

    #获取当前帧
    def current_frame(self, pixmap):
        self._current_frame = pixmap
        
    #手动检测点击函数
    def on_manual_button_clicked(self):
        
        if self._current_frame:

            #设置当前帧
            self.manual_calibration_dialog.set_frame(self._current_frame)
                
            self.manual_calibration_dialog.show()

            if self.manual_calibration_dialog.exec() == QDialog.DialogCode.Accepted:

                self.current_center = self.manual_calibration_dialog.xy_position

                #发送可以标记信号
                self.clicked_and_can_mark_signal.emit(True, self.current_center)

                log_debug(f"用户已标定{self.current_center}为圆心")

                self.start_detection_button.setEnabled(True)

            else:
                log_info("用户手动关闭了手动标定窗口")
        else:
            log_warning("请先传入干涉图像")
            return

    def on_start_detection_button_clicked(self):

        if not self.is_connected:
            log_error("您断开了摄像头的连接！请重连")
            alert_error("您已断开了摄像头的连接")
            return

        self.is_brightness_detecting = not self.is_brightness_detecting

        if self.is_brightness_detecting:
            self.start_detection_button.setText("停止计数")
            log_info("即将开始数条纹进程...")
        else:
            self.start_detection_button.setText("开始计数")
            log_warning("手动停止数条纹进程")
            self.data_analyse_label.setVisible(True)
            self.clicked_and_can_mark_signal.emit(False, [])
            #可以清理数据
            self.data_clear_button.setEnabled(True)

        #发送信号
        self.start_count_signal.emit(self.is_brightness_detecting)

    #连接摄像头后重置按钮状态
    def set_camera_connected(self, is_connected):
        self.is_connected = is_connected
        self.start_button.setEnabled(is_connected)
        self.manual_button.setEnabled(is_connected)
        self.warning_label.setVisible(not is_connected)  # 隐藏第一条警告

    #数据清理按钮被点击
    def on_data_clear_button_clicked(self):

        state = alert_warning("确保您已保存数据！", self, "确认清理")

        if state == QMessageBox.StandardButton.Ok:

            self.data_clear_button.setEnabled(False)

            self.data_analyse_label.setVisible(False)

            self.current_center = []

            self.data_clear_signal.emit()
        else:
            return







