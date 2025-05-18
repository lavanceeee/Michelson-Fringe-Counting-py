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
        self.camera_url = url
        
    def run(self):
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
                
                blurred = preprocess_for_circle_detection(frame)
                if blurred is not None:
                    h, w = blurred.shape
                    processed_qt_image = QImage(blurred.data, w, h, w*1, QImage.Format.Format_Grayscale8)

                    self.frame_ready.emit(processed_qt_image)
                
        except Exception:
            self.connection_lost.emit()
        finally:
            if self.camera:
                self.camera.release()
    
    def stop(self):
        self.running = False
        self.wait()  # 等待线程结束
    
