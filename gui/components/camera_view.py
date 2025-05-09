from PyQt6.QtWidgets import QLabel
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap
import cv2

class CameraDisplay(QLabel):
    #视频组件
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):
        #摄像头区域UI
        self.setFixedSize(400,250)
        #设置图片大小
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("""
            QLabel {
                border: 2px solid #666666;
                border-radius: 5px;
            }              
                        """)
        self.setText("等待摄像头连接...")

