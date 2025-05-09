from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QWidget, QHBoxLayout, QPushButton)
from core.log_manager import log_debug, log_error
"""
手动标定对话弹窗
"""

class ManualCalibrationDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        log_debug("手动标定对话框被创建")
        self.frame_label = None #声明frame_label
        self.setup_ui()

    def setup_ui(self):

        self.setWindowTitle("手动标定")
        self.setFixedSize(600,500)

        #创建主布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        #创建显示标定帧的Label
        self.frame_label = QLabel(self)
        self.frame_label.setFixedSize(256, 256)
        self.frame_label.setStyleSheet(
            """
            QLabel {
                border: 2px solid #666666;
                border-radius: 5px;
            }              
            """)
        self.frame_label.setText("测试")

        main_layout.addWidget(self.frame_label)

        #右侧信息显示与确定区域
        function_widget = QWidget()
        function_layout = QVBoxLayout()
        #将function_layout添加到function_widget
        function_widget.setLayout(function_layout)

        btn1 = QPushButton("测试", self)
        function_layout.addWidget(btn1)

        main_layout.addWidget(function_widget)

#连接摄像头并显示画面
    def set_frame(self, pixmap):
        log_debug("进入manual函数的update_frame")

        try:
            if pixmap is None:
                log_error("update_frame | 传入是None")
                return
            else:
                log_debug("update_camera函数 | is not None")

                #显示画面
                self.frame_label.setPixmap(pixmap)

        except Exception as e:
            log_error(f"手动标定函数中的update_frame出错:{e}")




        

        






























