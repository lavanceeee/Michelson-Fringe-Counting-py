import sys
import cv2
import numpy as np
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt, QTimer, QDateTime
from PyQt6.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from gui.components.figure_view import FigureView
from gui.menu_bar import MenuBarManger
from gui.components.camera_view import CameraDisplay
from core.camera_controller import CameraController
from gui.dialogs.camera_config_dialog import CameraConfigDialog
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

        # 使用绝对路径
        model_path = r"D:\SoftwareEngining\workAndHue\compatation\physics\write\pythonFileNewVer\models\model_weights\best_model.pth"

        log_info(f"从绝对路径 {model_path} 加载模型...")

        if load_inference_model(model_path):
             log_info("CNN 模型加载成功。")
        else:
             log_error("CNN 模型加载失败，检测功能将不可用")

        self.current_position = [0, 0]

        # 创建检测定时器
        self.detection_timer = QTimer(self)
        self.detection_timer.timeout.connect(self.detect_circles) # 定时器触发时调用检测方法

        #创建亮度检测定时器
        self.brightness_timer = QTimer(self)
        self.brightness_timer.setInterval(100)
        self.brightness_timer.timeout.connect(self.update_brightness_detection)

        self.detection_start_time = None # 仅用于标记检测是否开启
        self.current_processed_frame = None # 存储当前处理后的帧 (可能不再需要，取决于预处理是否只在CNN内部做)
        self.last_original_cv_frame = None # <--- 新增：存储原始 OpenCV 帧
        # 添加一个变量来存储最后显示的未标记图像
        self.last_unmarked_pixmap = None
        self.is_displaying_marked_image = False # 标记当前是否显示的是带标记的图
        self.orignal_qimage = None

    def setup_ui(self):
        self.setWindowTitle("Kama")
        # 重新调整窗口大小以适应新布局，宽度可以小一些
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
            #topContainer {  /* 使用ID选择器，只选择特定对象 */
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
            #bottomContainer {  /* 使用ID选择器，只选择特定对象 */
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
        log_info("Console initialized.")
        log_warning("Please connect the camera device first.")

        # 将包含边框的底部容器添加到主布局
        self.main_layout.addWidget(bottom_container)

        # 当点击自动检测按钮时，调用toggle_detection
        self.function_view.detect_circles_signal.connect(self.toggle_detection)

        #连接开始数条纹的信号
        self.function_view.start_count_signal.connect(self.toggle_light_count)

        # 创建CountsDetector实例
        self.counts_detector = CountsDetector()
        
        # 一次性连接信号
        self.counts_detector.center_brightness_signal.connect(self.figure_view.update_point_data)
        self.counts_detector.average_brightness_signal.connect(self.figure_view.init_average_brightness_data)

    def setup_camera(self):
        self.camera_controller = CameraController()

        # 将图像object连接到update_frame
        self.camera_controller.frame_ready.connect(self.update_frame)
        
        # 添加对摄像头连接状态的处理
        self.camera_controller.connection_lost.connect(self.handle_camera_disconnected)

    def update_frame(self, image): # 输入可能是 QImage 或 None
        # 1. 首先处理 None 的情况
        if image is None:
            self.camera_display.clear()
            self.camera_display.setText("等待摄像头...")
            log_warning("在 update_frame: 接收到 None.")
            self.function_view.set_camera_connected(False)
            self.last_unmarked_pixmap = None
            self.last_original_cv_frame = None # 确保重置
            return # 如果 image 是 None，停止处理

        # 2. 如果接收到的是 QImage (根据错误推断这是主要情况)
        if isinstance(image, QImage):
            try:
                # A. 直接使用接收到的 QImage 创建用于显示的 Pixmap
                pixmap = QPixmap.fromImage(image) 

                self.last_unmarked_pixmap = pixmap # 存储用于显示的 pixmap
                self.function_view.current_frame(pixmap)
                
                # B. 将 QImage 转换为 OpenCV 格式 (NumPy 数组) 以便后续处理
                #    需要处理不同的 QImage 格式
                image_copy = image.copy() # 操作副本以防修改原始 QImage
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
                    # ptr.setsize(image_copy.sizeInBytes()) # sizeInBytes 可能不准确，用 h*w*4
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
                    # 如果后续处理可以接受单通道灰度图，则用:
                    # cv_frame_for_processing = arr
                else:
                    log_error(f"不支持的 QImage 格式用于转换: {qimage_format}")
                    self.last_original_cv_frame = None
                    self.camera_display.clear()
                    self.camera_display.setText("格式不支持")
                    self.function_view.set_camera_connected(False)
                    return

                # 存储转换后的 OpenCV 帧 (NumPy 数组)
                self.last_original_cv_frame = cv_frame_for_processing.copy() # 存储 NumPy 数组

                # if self.counts_detector.start_signal:
                #     self.counts_detector.update_frame(self.last_original_cv_frame)

                # C. 更新显示 (仅在当前未显示标记图像时)

                # ----- is_detecting的定义----
                # ----- 如果没检测的话，这里是直接显示未标记的图像
                is_detecting = self.detection_start_time is not None
                if not is_detecting or not self.is_displaying_marked_image:
                    self.camera_display.setPixmap(self.last_unmarked_pixmap) # 使用存储的 pixmap

                    #标定一次当前帧的圆心
                    self.mark_center(self.last_unmarked_pixmap)

                # D. 更新连接状态
                #使得自动检测按钮可以点击
                self.function_view.set_camera_connected(True)

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

    def show_about(self):
        """显示关于对话框"""
        log_info("打开关于对话框")

    def toggle_detection(self, start):
        if start:
            # 检查摄像头是否已连接
            if self.camera_controller is None or not self.camera_controller.is_connected:
                 log_warning("Cannot start detection: Camera not connected.")
                 # 重置按钮状态 (如果 FunctionView 支持)
                 # self.function_view.reset_button_state() 
                 return

            # 开始检测
            log_debug("toggle_detection被调用，开始检测")
            log_info("开始检测 - 定时 (5s间隔), 短暂显示结果")
            self.detection_start_time = QDateTime.currentMSecsSinceEpoch() # 标记检测已开始
            
            # 检查是否有图像可以立即检测一次
            # (修改为检查是否有原始帧)
            if self.last_original_cv_frame is not None: # <--- 修改：检查原始帧
                 log_debug("立即检测一次...")
                 self.detect_circles() # 立即执行一次检测并更新显示
            else:
                log_warning("没有可用的图像，等待定时器触发...")

            # 启动定时器，每5000毫秒 (5秒) 触发一次 detect_circles
            log_debug("启动检测定时器 (2s间隔).")
            self.detection_timer.start(2000)
        else:
            # 停止检测
            log_debug("toggle_detection的else部分被调用，停止检测")
            log_warning("Detection stopped by user.")
            self.detection_start_time = None # 标记检测已停止
            # 停止定时器
            if self.detection_timer.isActive():
                self.detection_timer.stop() 
                log_debug("Detection timer stopped.")
            
            # *** 停止后，恢复显示最后一次收到的未标记图像 ***
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
        # 这个方法现在只由定时器调用
        try:
            # 检查处理后的灰度图是否可用 (修改为检查原始帧)
            # if not hasattr(self, 'current_processed_frame') or self.current_processed_frame is None:
            #     log_warning("No processed frame available for scheduled detection")
            #     return
            if self.last_original_cv_frame is None: # <--- 修改：检查原始帧
                log_warning("No original frame available for detection.")
                return # 没有帧就直接返回

            # 检查检测是否应该运行 (以防万一在定时器触发和执行之间被停止)
            if self.detection_start_time is None:
                log_debug("Scheduled detection skipped: Detection was stopped.")
                # 确保定时器也停止了
                if self.detection_timer.isActive():
                    self.detection_timer.stop()
                return

            log_debug("detect_circles被调用")

            # 调用灰度图检测方法 (修改为调用处理原始帧的方法)
            # processed_frame, circle_count = CircleDetector.process_preprocessed_frame(
            #     self.current_processed_frame
            # )
            log_debug("开始调用基于CNN的圆环检测方法...")
            # 调用基于 CNN 的处理方法，传入原始帧
            marked_frame, circle_count = CircleDetector.process_opencv_frame(
                self.last_original_cv_frame
            ) # <--- 修改：调用新方法并传入原始帧
            
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


    def toggle_light_count(self, is_start, center_list):
        if is_start:

            #中心坐标
            self.current_position = center_list

            self.counts_detector.start_cout(center_list)
            self.brightness_timer.start()

            log_debug(f"在主函数的即将传递的坐标是：{center_list[0]} and {center_list[1]}---")
        else:

            self.counts_detector.start_signal = False
            #清空第一帧
            self.counts_detector.first_frame = None
            #清空当前帧
            self.counts_detector.current_frame = None
            #清空中心点
            self.counts_detector.center_pos = [0,0]
            #清空时间
            self.counts_detector.update_time = 0
            #结束定时器
            self.brightness_timer.stop()

    def mark_center(self, marked_frame):
        # 标定一次当前帧的圆心
        painter = QPainter(marked_frame)

        pen = QPen(QColor(255, 0, 0))  # 红色
        pen.setWidth(2)  # 设置边框宽度
        painter.setPen(pen)

        painter.drawLine(self.current_position[0] - 10, self.current_position[1], self.current_position[0] + 10, self.current_position[1])
        painter.drawLine(self.current_position[0], self.current_position[1] - 10, self.current_position[0], self.current_position[1] + 10)

        painter.end()
        self.camera_display.setPixmap(marked_frame)

    def update_brightness_detection(self):
        """
        每1000ms触发一次的亮度检测
        直接发送原始QImage
        """

        if self.counts_detector.start_signal:

            self.counts_detector.update_frame(self.orignal_qimage)
            
if __name__ == "__main__":
    app = QApplication([])
    main_window = MyWindow()
    main_window.show()
    app.exec()