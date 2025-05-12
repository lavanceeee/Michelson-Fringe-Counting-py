from PyQt6.QtCore import QObject, QTimer, pyqtSignal
from PyQt6.QtGui import QImage
import cv2
from core.log_manager import log_error
from utils.image_pre_processing import preprocess_for_circle_detection

#摄像头控制逻辑
class CameraController(QObject):
    
    #这里先定义一个信号，用于传递图像
    #QImage不能接受None，导致程序异常，改成object
    frame_ready = pyqtSignal(object)
    connection_lost = pyqtSignal()  # 添加新的信号用于通知连接断开

    #拿到预处理后的图像
    processed_frame_ready = pyqtSignal(object) 

    def __init__(self):
        super().__init__()
        self.camera = None
        self.timer = QTimer()
        self.timer.timeout.connect(self.get_frame)
        self.is_connected = False

    def connect_camera(self, ip, port):
        #连接DroidCam
        try:
            url = f"http://{ip}:{port}/video"
            self.camera = cv2.VideoCapture(url)
            if self.camera.isOpened():
                self.is_connected = True
                self.timer.start(30) #30ms获取一帧
                return True
            return False
        
        except Exception as e:
            log_error(f"Connect camera failed: {e}")
            return False

    def get_frame(self):
        """获取摄像头画面"""
        try:
            if self.camera and self.camera.isOpened():
                ret, frame = self.camera.read()
                if ret:

                    #预处理
                    blurred = preprocess_for_circle_detection(frame)
                    
                    if blurred is not None:
                        h, w = blurred.shape
                        #fix:需要的是字节步长， w*1
                        qt_image = QImage(blurred.data, w, h, w*1, QImage.Format.Format_Grayscale8)
                        self.frame_ready.emit(qt_image)

                        #frame_ready信号发送处理后的图像
                        self.processed_frame_ready.emit(blurred)
                else:
                    log_error("Camera disconnected.")
                    self.handle_disconnection()
            else:
                log_error("Camera not connected, Try again.")
                self.handle_disconnection()
        except Exception as e:
            log_error(f"Error getting frame: {e}")
            self.handle_disconnection()  # 处理异常情况

    def handle_disconnection(self):
        """处理摄像头断开的情况"""
        if self.is_connected:  # 只有在之前是连接状态时才处理
            self.is_connected = False
            self.timer.stop()
            if self.camera:
                self.camera.release()
                self.camera = None
            self.frame_ready.emit(None) #发送空白的图像，消除最后一帧卡着的bug
            self.connection_lost.emit()  # 发出连接断开的信号

