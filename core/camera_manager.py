from PyQt6.QtCore import QObject, pyqtSignal, QDateTime
from PyQt6.QtGui import QImage
import cv2
from core.camera_controller import CameraController
from algorithm.circle_detector import CircleDetector
from core.log_manager import log_info, log_warning, log_error, log_debug

class CameraManager(QObject):
    # 定义信号
    frame_ready = pyqtSignal(QImage)  # 图像准备好（原始或处理后）
    detection_status_changed = pyqtSignal(bool)  # 检测状态变化
    camera_connection_changed = pyqtSignal(bool)  # 摄像头连接状态变化
    
    def __init__(self):
        super().__init__()
        self.camera_controller = CameraController()
        self.detection_enabled = False
        self.detection_start_time = None
        
        # 连接信号
        self.camera_controller.frame_ready.connect(self._handle_frame)
        self.camera_controller.connection_lost.connect(self._handle_disconnection)
        self.camera_controller.processed_frame_ready.connect(self._store_processed_frame)
    
    def connect_camera(self, ip, port):
        """连接摄像头"""
        success = self.camera_controller.connect_camera(ip, port)
        if success:
            self.camera_connection_changed.emit(True)
        else:
            self.camera_connection_changed.emit(False)
        return success
    
    def _handle_frame(self, image):
        """处理接收到的图像帧"""
        if not isinstance(image, QImage):
            # 发送空图像
            self.frame_ready.emit(None)
            return
            
        # 如果检测已开启，处理当前图像
        if self.detection_enabled and hasattr(self, 'current_processed_frame'):
            self._detect_circles()
        else:
            # 否则直接转发原始图像
            self.frame_ready.emit(image)
    
    def _store_processed_frame(self, blurred):
        """存储预处理后的灰度图"""
        self.current_processed_frame = blurred
    
    def _handle_disconnection(self):
        """处理摄像头断开连接"""
        self.camera_connection_changed.emit(False)
        # 清理状态
        if hasattr(self, 'current_processed_frame'):
            delattr(self, 'current_processed_frame')
        self.stop_detection()
    
    def toggle_detection(self, enable):
        """切换检测状态"""
        self.detection_enabled = enable
        
        if enable:
            log_info("开始圆环检测")
            self.detection_start_time = QDateTime.currentMSecsSinceEpoch()
            
            # 如果已有处理后的图像，立即开始检测
            if hasattr(self, 'current_processed_frame'):
                self._detect_circles()
        else:
            log_warning("停止圆环检测")
            self.detection_start_time = None
            # 重置检测器状态
            CircleDetector.last_position = None
        
        # 通知状态变化
        self.detection_status_changed.emit(enable)
    
    def stop_detection(self):
        """停止检测"""
        if self.detection_enabled:
            self.toggle_detection(False)
    
    def _detect_circles(self):
        """执行圆环检测"""
        try:
            # 检查预处理后的图像是否可用
            if not hasattr(self, 'current_processed_frame') or self.current_processed_frame is None:
                log_warning("No processed frame available")
                return
            
            # 调用检测方法
            processed_frame, circle_count = CircleDetector.process_preprocessed_frame(
                self.current_processed_frame
            )
            
            # 创建并发送QImage
            try:
                h, w = processed_frame.shape
                qt_image = QImage(processed_frame.data, w, h, w, QImage.Format.Format_Grayscale8).copy()
                self.frame_ready.emit(qt_image)
            except Exception as e:
                log_error(f"图像转换失败: {e}")
                return
                
            # 记录日志
            log_info(f"检测到 {circle_count} 个圆环")
            
        except Exception as e:
            log_error(f"圆环检测过程出错: {e}")
            import traceback
            log_error(traceback.format_exc())
