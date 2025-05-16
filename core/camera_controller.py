from PyQt6.QtCore import QObject, pyqtSignal
from core.log_manager import log_error
from thread.camera_thread import CameraThread  # 导入新的线程类

class CameraController(QObject):
    # 保持原有的信号定义
    frame_ready = pyqtSignal(object)
    connection_lost = pyqtSignal()
    # processed_frame_ready = pyqtSignal(object)

    def __init__(self):
        super().__init__()
        self.is_connected = False
        # 创建线程但不启动
        self.camera_thread = CameraThread()
        
        # 连接线程信号到控制器信号
        self.camera_thread.frame_ready.connect(self.frame_ready)
        # self.camera_thread.processed_frame_ready.connect(self.processed_frame_ready)
        self.camera_thread.connection_lost.connect(self.handle_disconnection)

    def connect_camera(self, ip, port):
        # 连接DroidCam
        try:
            url = f"http://{ip}:{port}/video"
            self.camera_thread.set_camera_url(url)
            
            # 启动线程
            self.camera_thread.start()
            self.is_connected = True
            return True
            
        except Exception as e:
            log_error(f"Connect camera failed: {e}")
            return False

    def handle_disconnection(self):
        """处理摄像头断开的情况"""
        if self.is_connected:
            self.is_connected = False
            self.camera_thread.stop()
            self.frame_ready.emit(None)
            self.connection_lost.emit()

