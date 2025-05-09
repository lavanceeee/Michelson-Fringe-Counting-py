from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton)
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialogButtonBox

class CameraConfigDialog(QDialog):
    """
    DroidCam摄像头配置对话框类
    摄像头IP配置相关的UI和逻辑
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        #设置弹窗相关属性
        self.setWindowTitle("DroidCamIP配置")
        self.setFixedSize(400, 200)

        #创建主布局
        layout = QVBoxLayout()
        self.setLayout(layout)

        #创建IP输入区域
        ip_layout = QHBoxLayout()
        ip_label = QLabel("Device IP:")
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("请输入Device IP：")
        ip_layout.addWidget(ip_label)
        ip_layout.addWidget(self.ip_input)

        #创建DroidCam 端口号输入
        port_layout = QHBoxLayout()
        port_label = QLabel("DroidCam Port:")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("请输入端口号：")
        port_layout.addWidget(port_label)
        port_layout.addWidget(self.port_input)

        #Tips区域
        #主布局
        tips_layout = QVBoxLayout()
        
        first_line = QHBoxLayout()
        tips_label = QLabel("Tips:")
        first_line.addWidget(tips_label)
        first_line.addStretch()

        second_line = QHBoxLayout()
        link_line = QLabel()
        link_line.setText('<a href="https://droidcam.app/">入门与下载DroidCam</a>')
        link_line.setOpenExternalLinks(True)
        second_line.addWidget(link_line)
        second_line.addStretch()

        third_line = QHBoxLayout()
        phone_tip = QLabel("请在手机端DroidCam查看Device IP")
        third_line.addWidget(phone_tip)
        third_line.addStretch()

        fourth_line = QHBoxLayout()
        port_tip = QLabel("默认端口号(DroidCam Port): 4747")
        fourth_line.addWidget(port_tip)
        fourth_line.addStretch()

        #添加所有的Tips到垂直布局
        tips_layout.addLayout(first_line)
        tips_layout.addLayout(second_line)
        tips_layout.addLayout(third_line)
        tips_layout.addLayout(fourth_line)

        #创建windows原生按钮
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )

        #更改按钮为中文
        button_box.button(QDialogButtonBox.StandardButton.Ok).setText("保存")
        button_box.button(QDialogButtonBox.StandardButton.Cancel).setText("取消")

        #连接按钮点击事件
        button_box.accepted.connect(self.save_config)
        button_box.rejected.connect(self.reject)

        # 添加所有布局到主布局
        layout.addLayout(ip_layout)
        layout.addLayout(port_layout)
        layout.addLayout(tips_layout)
        layout.addStretch() #弹性布局，把按钮放到底部
        layout.addWidget(button_box) #自动右对齐


    def save_config(self):
        """
        保存配置
        """
        deviceIP = self.ip_input.text()
        devicePort = self.port_input.text()
        if deviceIP and devicePort:
            self.saved_ip = deviceIP
            self.saved_port = devicePort
            self.accept() #关闭对话框并返回接受状态
        else:
            print("输入有空，请检查")

    def get_camera_config(self):
        #返回IP和端口号
        return self.saved_ip, self.saved_port
