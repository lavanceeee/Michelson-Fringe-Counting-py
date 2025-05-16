from PyQt6.QtCore import QThread, pyqtSignal
import cv2
from PyQt6.QtGui import QImage
from utils.image_pre_processing import preprocess_for_circle_detection

class CameraThread(QThread):
    # 定义信号：原始帧和处理后的帧
    frame_ready = pyqtSignal(object)
    # processed_frame_ready = pyqtSignal(object)
    connection_lost = pyqtSignal()
    
    def __init__(self, camera_url=None):
        super().__init__()
        self.camera_url = camera_url
        self.running = False
        self.camera = None
    
    def set_camera_url(self, url):
        """设置摄像头URL"""
        self.camera_url = url
        
    def run(self):
        """线程主函数，循环读取摄像头"""
        try:
            self.camera = cv2.VideoCapture(self.camera_url)
            if not self.camera.isOpened():
                self.connection_lost.emit()
                return
                
            self.running = True
            while self.running:
                ret, frame = self.camera.read()
                if not ret:
                    self.connection_lost.emit()
                    break
                    
                # # 处理图像并发送信号
                # # 原始图像转为QImage
                # h, w, ch = frame.shape
                # bytes_per_line = ch * w
                # qt_image = QImage(frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888).copy()
                # self.frame_ready.emit(qt_image)
                
                blurred = preprocess_for_circle_detection(frame)
                if blurred is not None:
                    h, w = blurred.shape
                    processed_qt_image = QImage(blurred.data, w, h, w*1, QImage.Format.Format_Grayscale8)
                    # self.processed_frame_ready.emit(blurred)

                    self.frame_ready.emit(processed_qt_image)
                
                # # 控制帧率
                # self.msleep(30)  # 约33fps
                
        except Exception as e:
            self.connection_lost.emit()
        finally:
            if self.camera:
                self.camera.release()
    
    def stop(self):
        """停止线程"""
        self.running = False
        self.wait()  # 等待线程结束
    
