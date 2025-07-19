import cv2
import numpy as np
from PyQt6.QtWidgets import QMessageBox
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from gui.components.figure_view import FigureView
from gui.menu_bar import MenuBarManger
from gui.components.camera_view import CameraDisplay
from core.camera_controller import CameraController
from gui.components.function_view import FunctionView
from gui.components.console_view import ConsoleView
from core.log_manager import log_manager, log_info, log_warning, log_error, log_debug
# from algorithm.circle_detector import CircleDetector
# from algorithm.cnn_circle_detector import load_inference_model
from core.counts_detector import CountsDetector

class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setup_ui()

        self.setup_camera()

        self.current_position = [0, 0]

        self.detection_timer = QTimer(self)
        self.detection_timer.timeout.connect(self.detect_circles)

        self.detection_start_time = None
        self.current_processed_frame = None
        self.last_original_cv_frame = None

        self.last_unmarked_pixmap = None
        self.is_displaying_marked_image = False
        self.orignal_qimage = None
        self.should_show_mark = False 

    def setup_ui(self):
        self.setWindowTitle("Kama")

        self.setGeometry(50, 50, 600, 600)

        self.menu_manager = MenuBarManger(self)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop) 

        top_container = QFrame()
        top_container.setObjectName("topContainer")  
        top_container.setFrameShape(QFrame.Shape.StyledPanel)
        top_container.setStyleSheet("""
            #topContainer {  
                border: 1px solid red;
                border-radius: 5px;
            }
        """)

        self.top_layout = QHBoxLayout(top_container)  
        self.top_layout.setContentsMargins(10, 10, 10, 10) 

        self.camera_display = CameraDisplay()
        self.figure_view = FigureView()
        self.top_layout.addWidget(self.camera_display)
        self.top_layout.addWidget(self.figure_view)

        self.main_layout.addWidget(top_container)

        bottom_container = QFrame()
        bottom_container.setObjectName("bottomContainer")  
        bottom_container.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_container.setStyleSheet("""
            #bottomContainer {  
                border: 1px solid red;
                border-radius: 5px;
            }
        """)

        self.bottom_layout = QHBoxLayout(bottom_container)  
        self.bottom_layout.setContentsMargins(10, 10, 10, 10)  

        self.function_view = FunctionView(self)
        self.console_view = ConsoleView()
        self.bottom_layout.addWidget(self.function_view)
        self.bottom_layout.addWidget(self.console_view)

        log_manager.set_console_view(self.console_view)
        log_info("调试窗口初始化完成")
        log_warning("请先连接摄像头设备")

        self.main_layout.addWidget(bottom_container)

        self.function_view.detect_circles_signal.connect(self.toggle_detection)

        self.function_view.clicked_and_can_mark_signal.connect(self.mark_center)

        self.function_view.start_count_signal.connect(self.toggle_light_count)

        self.counts_detector = CountsDetector()
        
        self.counts_detector.center_brightness_signal.connect(self.figure_view.update_point_data)

        self.function_view.data_clear_signal.connect(self.clear_history_data)

    def setup_camera(self):
        self.camera_controller = CameraController()

        self.camera_controller.frame_ready.connect(self.update_frame)
        
        self.camera_controller.connection_lost.connect(self.handle_camera_disconnected)

    def update_frame(self, image):
        if image is None:
            self.camera_display.clear()
            self.camera_display.setText("等待摄像头...")
            self.function_view.set_camera_connected(False)
            self.last_unmarked_pixmap = None
            self.last_original_cv_frame = None 
            return 

        if isinstance(image, QImage):
            try:
                pixmap = QPixmap.fromImage(image) 

                self.last_unmarked_pixmap = pixmap
                self.function_view.current_frame(pixmap)
                
                image_copy = image.copy() 
                qimage_format = image_copy.format()
                self.orignal_qimage = image

                if image_copy.isNull():
                    log_error("接收到的 QImage 是空的")
                    self.last_original_cv_frame = None
                    return

                # 尝试更健壮的转换方式
                if qimage_format == QImage.Format.Format_RGB32 or \
                   qimage_format == QImage.Format.Format_ARGB32 or \
                   qimage_format == QImage.Format.Format_ARGB32_Premultiplied:
                    # 4通道 (RGBA 或 ARGB)
                    ptr = image_copy.constBits()

                    h, w = image_copy.height(), image_copy.width()
                    if h * w * 4 == 0:
                         log_error("QImage 尺寸为0")
                         self.last_original_cv_frame = None
                         return
                    ptr.setsize(h * w * 4)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 4))
                    # OpenCV 需要 BGR，所以从 RGBA 转 BGR
                    cv_frame_for_processing = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR) # 取前3通道转 BGR
                elif qimage_format == QImage.Format.Format_RGB888:
                     # 3通道 RGB
                    ptr = image_copy.constBits()
                    h, w = image_copy.height(), image_copy.width()
                    if h * w * 3 == 0:
                         log_error("QImage 尺寸为0")
                         self.last_original_cv_frame = None
                         return
                    ptr.setsize(h * w * 3)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 3))
                    cv_frame_for_processing = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)
                elif qimage_format == QImage.Format.Format_Grayscale8:
                    # 1通道灰度
                    ptr = image_copy.constBits()
                    h, w = image_copy.height(), image_copy.width()
                    if h * w * 1 == 0:
                         log_error("QImage 尺寸为0")
                         self.last_original_cv_frame = None
                         return
                    ptr.setsize(h * w * 1)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w))
                    # 如果后续处理需要3通道 BGR 图像
                    cv_frame_for_processing = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)

                else:
                    log_error(f"不支持的 QImage 格式用于转换: {qimage_format}")
                    self.last_original_cv_frame = None
                    self.camera_display.clear()
                    self.camera_display.setText("格式不支持")
                    self.function_view.set_camera_connected(False)
                    return


                self.last_original_cv_frame = cv_frame_for_processing.copy() # 存储 NumPy 数组

                #计数信号
                if self.counts_detector.start_update_frame:
                    self.counts_detector.update_frame(self.orignal_qimage)

                #所有按钮可以点击
                self.function_view.set_camera_connected(True)

                # 在显示图像之前检查是否需要绘制十字
                if self.should_show_mark and self.last_unmarked_pixmap:
                    display_pixmap = self.last_unmarked_pixmap.copy()
                    painter = QPainter(display_pixmap)
                    pen = QPen(QColor(255, 0, 0))
                    pen.setWidth(2)
                    painter.setPen(pen)
                    
                    # 绘制十字
                    x, y = self.current_position[0], self.current_position[1]
                    painter.drawLine(x - 10, y, x + 10, y)
                    painter.drawLine(x, y - 10, x, y + 10)
                    painter.end()
                    
                    # 显示带标记的图像
                    self.camera_display.setPixmap(display_pixmap)
                else:
                    self.camera_display.setPixmap(self.last_unmarked_pixmap)

            except Exception as e:
                 log_error(f"在 update_frame 中处理/转换 QImage 时出错: {e}")
                 import traceback
                 log_error(traceback.format_exc()) # 打印详细的回溯信息
                 self.camera_display.clear()
                 self.camera_display.setText("处理帧出错")
                 self.function_view.set_camera_connected(False)
                 self.last_unmarked_pixmap = None
                 self.last_original_cv_frame = None
        else:
            # 如果 image 不是 None 也不是 QImage，记录一个错误
            log_error(f"在 update_frame 中接收到意外的帧类型: {type(image)}")
            self.camera_display.clear()
            self.camera_display.setText("意外帧类型")
            self.function_view.set_camera_connected(False)
            self.last_unmarked_pixmap = None
            self.last_original_cv_frame = None

    def handle_camera_disconnected(self):
        """摄像头断开连接时的处理"""
        log_debug("handle_camera_disconnected被调用")
        self.function_view.set_camera_connected(False)
        
        # *** 停止检测定时器并重置状态 ***
        if self.detection_timer.isActive():
            self.detection_timer.stop()
            log_warning("停止检测，因为摄像头断开")
        
        self.detection_start_time = None
        self.current_processed_frame = None
        self.last_original_cv_frame = None
        # CircleDetector.last_position = None
        self.last_unmarked_pixmap = None
        self.is_displaying_marked_image = False # 重置标记

    def toggle_detection(self, start):
        if start:
            # 检查摄像头是否已连接
            if self.camera_controller is None or not self.camera_controller.is_connected:
                 log_warning("摄像头未连接！")
                 return

            # 开始检测
            self.detection_start_time = QDateTime.currentMSecsSinceEpoch() # 标记检测已开始

            #初始化CNN连接
            # 绝对路径
            model_path = r"D:\Software_engining\workAndHue\compatation\physics\write\pythonFileNewVer\models\model_weights\best_model.pth"

            log_info("正在加载CNN模型...")

            if load_inference_model(model_path):
                log_info("CNN 模型加载成功。")
            else:
                log_error("CNN 模型加载失败，检测功能将不可用")

            if self.last_original_cv_frame is not None:
                 log_debug("立即检测一次...")
                 self.detect_circles() # 立即执行一次检测并更新显示
            else:
                log_warning("没有可用的图像，等待定时器触发...")

            # 启动定时器，每5000毫秒 (5秒) 触发一次 detect_circles
            log_debug("启动检测定时器 (2s间隔).")
            self.detection_timer.start(2000)
        else:
            log_warning("检测已暂停")
            self.detection_start_time = None
            # 停止定时器
            if self.detection_timer.isActive():
                self.detection_timer.stop() 
                log_debug("Detection timer stopped.")
            
            #停止后，恢复显示最后一次收到的未标记图像
            if self.last_unmarked_pixmap:
                 self.camera_display.setPixmap(self.last_unmarked_pixmap)
                 log_debug("已停止检测，恢复显示最后一次收到的未标记图像.")
            elif self.camera_controller and self.camera_controller.is_connected:
                 # 如果没有存储的pixmap但摄像头还在连接，显示等待文本
                 self.camera_display.clear()
                 self.camera_display.setText("检测已停止") 
            else:
                 # 如果摄像头也断了，显示断开连接
                 self.camera_display.clear()
                 self.camera_display.setText("摄像头已断开")
            self.is_displaying_marked_image = False # 重置标记

    def detect_circles(self):
        try:
            if self.last_original_cv_frame is None:
                log_warning("No original frame available for detection.")
                return # 没有帧就直接返回

            if self.detection_start_time is None:
                log_debug("Scheduled detection skipped: Detection was stopped.")
                # 确保定时器也停止了
                if self.detection_timer.isActive():
                    self.detection_timer.stop()
                return

            log_debug("detect_circles被调用")

            log_debug("开始调用基于CNN的圆环检测方法...")
            # 调用基于 CNN 的处理方法，传入原始帧
            marked_frame, circle_count = CircleDetector.process_opencv_frame(
                self.last_original_cv_frame
            )
            
            # 转换为QImage显示
            try:
                # 检查返回的图像是彩色还是灰度
                if marked_frame is None:
                     raise ValueError("检测函数返回空帧")

                if len(marked_frame.shape) == 3 and marked_frame.shape[2] == 3:
                    # BGR 彩色图像
                    h, w, ch = marked_frame.shape
                    bytes_per_line = ch * w
                    # OpenCV 是 BGR, QImage 需要 RGB，或者直接用 Format_BGR888
                    # qt_image = QImage(cv2.cvtColor(marked_frame, cv2.COLOR_BGR2RGB).data, w, h, bytes_per_line, QImage.Format.Format_RGB888).copy()
                    qt_image = QImage(marked_frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888).copy() # 使用 BGR 格式
                    log_debug("Converted marked BGR frame to QImage.")
                elif len(marked_frame.shape) == 2:
                    # 灰度图像
                    h, w = marked_frame.shape
                    qt_image = QImage(marked_frame.data, w, h, w, QImage.Format.Format_Grayscale8).copy()
                    log_debug("Converted marked Grayscale frame to QImage.")
                else:
                    raise ValueError(f"Unsupported image shape: {marked_frame.shape}")
                 # <--- 修改：新的转换逻辑

            except Exception as img_error:
                log_error(f"Marked image conversion to QImage failed: {img_error}")
                # 如果转换失败，可能就不更新显示了
                return

            # *** 更新UI - 显示检测后的带标记图像 ***
            try:
                #转换出的图像
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.camera_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                # *** 只有这里更新显示 ***
                self.camera_display.setPixmap(scaled_pixmap) 
                self.is_displaying_marked_image = True # 设置标记：现在显示的是标记图
                log_info(f"显示标记图 - 检测到 {circle_count} 个圆环")

                # *** 启动单次定时器，0.5秒后恢复显示未标记图像 ***
                QTimer.singleShot(500, self.restore_unmarked_display) 

            except Exception as ui_error:
                log_error(f"UI更新失败: {ui_error}")
                self.is_displaying_marked_image = False # 更新失败，重置标记
                return
            
        except Exception as e:
            # 捕获所有可能的异常
            log_error(f"圆环检测过程出错: {e}")
            import traceback
            log_error(traceback.format_exc())
            self.is_displaying_marked_image = False # 出错，重置标记

    #在不检测的时候恢复显示未标记的图像
    def restore_unmarked_display(self):
        """由单次定时器调用，恢复显示最新的未标记图像"""
        # 检查检测是否仍然开启，并且当前确实是在显示标记图
        if self.detection_start_time is not None and self.is_displaying_marked_image:
            if self.last_unmarked_pixmap:
                self.camera_display.setPixmap(self.last_unmarked_pixmap)
                log_debug("恢复显示未标记图像")
            else:
                # 如果碰巧没有未标记的图像了，可以清空或显示提示
                self.camera_display.clear()
                self.camera_display.setText("...") 
            self.is_displaying_marked_image = False # 重置标记：现在显示的不是标记图了
        else:
             log_debug("恢复显示被跳过 (可能检测已停止或状态已改变)")


    def toggle_light_count(self, is_start):
        if is_start:

            self.counts_detector.start_cout(self.current_position)
        else:
            self.counts_detector.start_update_frame = False
            #清空中心点
            self.counts_detector.center_pos = [0,0]
            
    def mark_center(self, can_mark, center_list):
        self.current_position = center_list
        self.should_show_mark = can_mark

    def clear_history_data(self):
        self.current_position = []
        
        #清空图表
        self.figure_view.clear_data()

        #清理counts_detector
        self.counts_detector.center_pos = []
        self.counts_detector.center_pos_array = []

    #重写closeEvent方法
    def closeEvent(self, event):
        replay = QMessageBox.question(
            self,
            "退出确认",
            "确定退出程序吗？未保存数据将丢失。",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        ) 
        if replay == QMessageBox.StandardButton.Yes:
            #检查并关闭摄像头连接
            if self.camera_controller and self.camera_controller.is_connected:
                self.camera_controller.disconnect()
            event.accept()
        else:
            event.ignore()

if __name__ == "__main__":
    app = QApplication([])
    main_window = MyWindow()
    main_window.show()
    app.exec()