from PyQt6.QtCore import QObject, pyqtSignal
from core.log_manager import log_error
from thread.camera_thread import CameraThread  
from core.alert_manager import alert_error
from core.log_manager import log_debug

class CameraController(QObject):

    frame_ready = pyqtSignal(object)
    connection_lost = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.is_connected = False
        # 创建线程
        self.camera_thread = CameraThread()

        # 连接线程信号到控制器信号  
        self.camera_thread.frame_ready.connect(self.frame_ready)
        self.camera_thread.connection_lost.connect(self.handle_disconnection)

    def connect_camera(self, ip, port):
        # 连接DroidCam
        try:
            url = f"http://{ip}:{port}/video"
            self.camera_thread.set_camera_url(url)
            self.camera_thread.start()
            self.is_connected = True
        except Exception as e:
            log_error(f"连接摄像头失败 {e}")

    def handle_disconnection(self):
        alert_error("摄像头连接失败！请检查ip和端口是否正确")
        self.is_connected = False
        self.camera_thread.stop()
        self.frame_ready.emit(None)
        self.connection_lost.emit()
            

