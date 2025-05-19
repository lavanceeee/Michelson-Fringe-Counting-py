import sys
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
from algorithm.circle_detector import CircleDetector
from algorithm.cnn_circle_detector import load_inference_model
from core.counts_detector import CountsDetector
"""
创建一个主窗口类
主窗口类，继承自QMainWindow
负责创建和管理应用程序的主界面
"""
class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 初始化界面
        self.setup_ui()

        # 初始化摄像头
        self.setup_camera()

        self.current_position = [0, 0]

        self.detection_start_time = None
        self.current_processed_frame = None
        self.last_original_cv_frame = None
        # 添加一个变量来存储最后显示的未标记图像
        self.last_unmarked_pixmap = None
        self.is_displaying_marked_image = False
        self.orignal_qimage = None
        self.should_show_mark = False  # 是否需要显示十字标记

    def setup_ui(self):
        self.setWindowTitle("Kama")

        self.setGeometry(50, 50, 600, 600)

        self.menu_manager = MenuBarManger(self)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        # 主布局垂直
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(20)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignTop) # 整体内容顶部对齐

        #1. 创建一个容器来包装顶部布局
        top_container = QFrame()
        top_container.setObjectName("topContainer")  # 设置对象名
        top_container.setFrameShape(QFrame.Shape.StyledPanel)
        top_container.setStyleSheet("""
            #topContainer {  
                border: 1px solid red;
                border-radius: 5px;
            }
        """)

        # 1. ---创建顶部水平布局---
        self.top_layout = QHBoxLayout(top_container)  # 将布局直接设置给容器
        self.top_layout.setContentsMargins(10, 10, 10, 10)  # 设置内边距

        # 添加组件到顶部布局
        self.camera_display = CameraDisplay()
        self.figure_view = FigureView()
        self.top_layout.addWidget(self.camera_display)
        self.top_layout.addWidget(self.figure_view)

        # 将包含边框的容器添加到主布局
        self.main_layout.addWidget(top_container)

        # 2. 创建一个容器来包装底部布局，与顶部容器相同
        bottom_container = QFrame()
        bottom_container.setObjectName("bottomContainer")  # 设置对象名
        bottom_container.setFrameShape(QFrame.Shape.StyledPanel)
        bottom_container.setStyleSheet("""
            #bottomContainer {  
                border: 1px solid red;
                border-radius: 5px;
            }
        """)

        # 创建底部水平布局并设置给容器
        self.bottom_layout = QHBoxLayout(bottom_container)  # 将布局直接设置给容器
        self.bottom_layout.setContentsMargins(10, 10, 10, 10)  # 设置内边距

        # 添加组件到底部布局
        self.function_view = FunctionView(self)
        self.console_view = ConsoleView()
        self.bottom_layout.addWidget(self.function_view)
        self.bottom_layout.addWidget(self.console_view)

        # 添加日志管理器
        log_manager.set_console_view(self.console_view)
        log_info("调试窗口初始化完成")
        log_warning("请先连接摄像头设备")

        # 将包含边框的底部容器添加到主布局
        self.main_layout.addWidget(bottom_container)

        # 当点击自动检测按钮时，调用toggle_detection
        self.function_view.detect_circles_signal.connect(self.toggle_detection)

        #点击确定，标记圆心坐标
        self.function_view.clicked_and_can_mark_signal.connect(self.mark_center)

        #连接开始数条纹的信号
        self.function_view.start_count_signal.connect(self.toggle_light_count)

        # 创建CountsDetector实例
        self.counts_detector = CountsDetector()
        
        self.counts_detector.center_brightness_signal.connect(self.figure_view.update_point_data)

        #清理数据
        self.function_view.data_clear_signal.connect(self.clear_history_data)

    def setup_camera(self):
        self.camera_controller = CameraController()

        # 将图像object连接到update_frame
        self.camera_controller.frame_ready.connect(self.update_frame)
        
        # 添加对摄像头连接状态的处理
        self.camera_controller.connection_lost.connect(self.handle_camera_disconnected)

    def update_frame(self, image):
        # 1. 首先处理 None 的情况
        if image is None:
            self.camera_display.clear()
            self.camera_display.setText("等待摄像头...")
            self.function_view.set_camera_connected(False)
            self.last_unmarked_pixmap = None
            self.last_original_cv_frame = None 
            return 

        if isinstance(image, QImage):
            try:
                #  创建用于显示的Pixmap
                pixmap = QPixmap.fromImage(image) 

                self.last_unmarked_pixmap = pixmap
                self.function_view.current_frame(pixmap)
                
                # QImage -> NumPy
                image_copy = image.copy() 
                qimage_format = image_copy.format()
                self.orignal_qimage = image

                # 转换方式
                if qimage_format == QImage.Format.Format_RGB32 or \
                   qimage_format == QImage.Format.Format_ARGB32 or \
                   qimage_format == QImage.Format.Format_ARGB32_Premultiplied:
                    # 4通道 (RGBA 或 ARGB)
                    ptr = image_copy.constBits()
                    h, w = image_copy.height(), image_copy.width()
                    ptr.setsize(h * w * 4)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 4))
                    # OpenCV 需要 BGR，所以从 RGBA 转 BGR
                    cv_frame_for_processing = cv2.cvtColor(arr[:, :, :3], cv2.COLOR_RGB2BGR) # 取前3通道转 BGR

                elif qimage_format == QImage.Format.Format_RGB888:
                     # 3通道 RGB
                    ptr = image_copy.constBits()
                    h, w = image_copy.height(), image_copy.width()
                    ptr.setsize(h * w * 3)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w, 3))
                    cv_frame_for_processing = cv2.cvtColor(arr, cv2.COLOR_RGB2BGR)

                elif qimage_format == QImage.Format.Format_Grayscale8:
                    # 1通道灰度
                    ptr = image_copy.constBits()
                    h, w = image_copy.height(), image_copy.width()
                    ptr.setsize(h * w * 1)
                    arr = np.frombuffer(ptr, dtype=np.uint8).reshape((h, w))
                    # 如果后续处理需要3通道 BGR 图像
                    cv_frame_for_processing = cv2.cvtColor(arr, cv2.COLOR_GRAY2BGR)

                self.last_original_cv_frame = cv_frame_for_processing.copy() 

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
            log_error(f"在 update_frame 中接收到意外的帧类型: {type(image)}")
            self.camera_display.clear()
            self.function_view.set_camera_connected(False)
            self.last_unmarked_pixmap = None
            self.last_original_cv_frame = None

    def handle_camera_disconnected(self):
        log_debug("handle_camera_disconnected被调用")
        self.function_view.set_camera_connected(False)
        self.detection_start_time = None
        self.current_processed_frame = None
        self.last_original_cv_frame = None
        self.last_unmarked_pixmap = None
        self.is_displaying_marked_image = False

    def toggle_detection(self, start):
        if start:

            # 开始检测
            self.detection_start_time = QDateTime.currentMSecsSinceEpoch() 

            #初始化CNN连接
            model_path = r"D:\SoftwareEngining\workAndHue\compatation\physics\write\pythonFileNewVer\models\model_weights\best_model.pth"

            log_info("正在加载CNN模型...")

            if load_inference_model(model_path):
                log_info("CNN 模型加载成功。")
            else:
                log_error("CNN 模型加载失败，检测功能将不可用")

            #直接检测
            self.detect_circles()
        else:
            self.detection_start_time = None
            # 停止定时器
            if self.detection_timer.isActive():
                self.detection_timer.stop() 
            
            #停止后，恢复显示最后一次收到的未标记图像
            if self.last_unmarked_pixmap:
                 self.camera_display.setPixmap(self.last_unmarked_pixmap)
                 log_debug("已停止检测，恢复显示最后一次收到的未标记图像.")
            else:
                 self.camera_display.clear()
                 self.camera_display.setText("摄像头已断开")
            self.is_displaying_marked_image = False 

    def detect_circles(self):
        try:
            log_info("开始检测圆环...")

            marked_frame, circle_count = CircleDetector.process_opencv_frame(
                self.last_original_cv_frame
            )
            
            # 转换为QImage显示
            try:
                if len(marked_frame.shape) == 3 and marked_frame.shape[2] == 3:
                    # BGR 彩色图像
                    h, w, ch = marked_frame.shape
                    bytes_per_line = ch * w
                    qt_image = QImage(marked_frame.data, w, h, bytes_per_line, QImage.Format.Format_BGR888).copy() # 使用 BGR 格式
                    log_debug("已将BGR图像转换为QImage")
                elif len(marked_frame.shape) == 2:
                    # 灰度图像
                    h, w = marked_frame.shape
                    qt_image = QImage(marked_frame.data, w, h, w, QImage.Format.Format_Grayscale8).copy()
                    log_debug("已将灰度图像转换为QImage")

            except Exception as img_error:
                log_error(f"图像转换为QImage失败: {img_error}")
                return

            #更新UI 
            try:
                #转换出的图像
                pixmap = QPixmap.fromImage(qt_image)
                scaled_pixmap = pixmap.scaled(
                    self.camera_display.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
                #  只有这里更新显示 
                self.camera_display.setPixmap(scaled_pixmap) 
                self.is_displaying_marked_image = True # 设置标记：现在显示的是标记图
                log_info(f"显示标记图 - 检测到 {circle_count} 个圆环")

                #启动单次定时器，0.5秒后恢复显示未标记图像
                QTimer.singleShot(500, self.restore_unmarked_display) 

            except Exception as ui_error:
                log_error(f"UI更新失败: {ui_error}")
                self.is_displaying_marked_image = False # 更新失败，重置标记
                return
            
        except Exception as e:
            # 捕获所有可能的异常
            log_error(f"圆环检测过程出错: {e}")
            self.is_displaying_marked_image = False # 出错，重置标记

    #不检测时恢复原始图像
    def restore_unmarked_display(self):
        # 检查检测是否仍然开启，并且当前确实是在显示标记图
            if self.last_unmarked_pixmap:
                self.camera_display.setPixmap(self.last_unmarked_pixmap)


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