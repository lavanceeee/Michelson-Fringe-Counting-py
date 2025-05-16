from PyQt6.QtWidgets import QFileDialog, QDialog, QLabel, QVBoxLayout
from PyQt6.QtGui import QImage, QPixmap, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint
from core.log_manager import log_warning, log_info, log_debug, log_error
from core.alert_manager import alert_error, alert_success
import cv2
import numpy as np
from thread.video_processing_thread import VideoProcessingThread


class CustomLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.crosshair_pos = QPoint(0, 0)
        self.original_pixmap = None
    
    def setOriginalPixmap(self, pixmap):
        self.original_pixmap = pixmap
        self.setPixmap(pixmap)
    
    def updateCrosshair(self, pos):
        self.crosshair_pos = pos
        self.update()  # 触发重绘
    
    def paintEvent(self, event):
        if self.original_pixmap:
            painter = QPainter(self)
            # 绘制原始图像
            painter.drawPixmap(0, 0, self.original_pixmap)
            
            # 设置十字线颜色和宽度
            pen = QPen(Qt.GlobalColor.red)
            pen.setWidth(1)
            painter.setPen(pen)
            
            # 绘制水平线
            painter.drawLine(0, self.crosshair_pos.y(), 
                          self.width(), self.crosshair_pos.y())
            # 绘制垂直线
            painter.drawLine(self.crosshair_pos.x(), 0, 
                          self.crosshair_pos.x(), self.height())
            
class VideoCounter:
    def __init__(self, main_window):
        self.main_window = main_window
        self.video_path = None
        self.current_pos = [0,0]
        #标记不是灰度视频
        self.is_gray_video = False
        self.data_average_brightness = 0

    def show_video_select(self):

        video_fileter = "视频文件(*.mp4 *.avi *.mov)"
        
        #打开文件选择弹窗
        video_file_path, _ = QFileDialog.getOpenFileName(self.main_window, 
                                  caption="请选择视频文件",
                                  directory="",
                                  filter=video_fileter)
        if not video_file_path:
            log_warning("用户取消了视频选择")
            return
        else:
            log_info(f"视频路径为{video_file_path}")
            alert_success("视频选择成功，请在接下来的窗口上使用鼠标标定圆心坐标")

            self.video_path = video_file_path
            
            #提取并显示当前帧显示并标定
            self.extract_and_display_frame()
            
    def extract_and_display_frame(self):
        #读取视频
        cap = cv2.VideoCapture(self.video_path)

        if not cap.isOpened():
            alert_error(message="无法打开视频文件", title="视频读取错误")
            return
        
        #拿到第一帧
        _, first_frame = cap.read()
        
        #将第一帧转为灰度
        gray_frame = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)

        #图片的大小
        frame_width = gray_frame.shape[1]
        frame_height = gray_frame.shape[0]

        log_info(f"视频第一帧的宽度为{frame_width},高度为{frame_height}")

        #创建弹窗窗口
        first_frame_dialog = QDialog(self.main_window)
        first_frame_dialog.setWindowTitle("圆心标定")
        first_frame_dialog.setFixedSize(frame_width, frame_height)

        #创建布局
        layout = QVBoxLayout()

        #创建自定义标签替代QLabel
        self.image_label = CustomLabel()
        self.image_label.setFixedSize(frame_width, frame_height)

        layout.addWidget(self.image_label)

        first_frame_dialog.setLayout(layout)

        # 转换OpenCV图像到QPixmap
        height, width = gray_frame.shape
        bytes_per_line =  width
        q_image = QImage(gray_frame.data, width, height, 
                        bytes_per_line, QImage.Format.Format_Grayscale8)
        pixmap = QPixmap.fromImage(q_image)

        # 设置原始图像
        self.image_label.setOriginalPixmap(pixmap)
        
        self.image_label.mouseMoveEvent = self.on_mouse_move
        
        # 鼠标点击事件
        self.image_label.mousePressEvent = self.mouse_click_event

        
        first_frame_dialog.exec()

        log_debug("打开窗口成功")

    def mouse_click_event(self, event):
        log_info(f"手动标定圆心坐标为{self.current_pos}")

        #关闭窗口
        self.image_label.parent().close()

        self.data_count()

    # 鼠标移动事件
    def on_mouse_move(self, event):
        self.current_pos = event.pos()
        self.image_label.updateCrosshair(event.pos())

    def data_count(self):

        try:
            # 创建处理线程
            self.process_thread = VideoProcessingThread(self.video_path, self.current_pos)

        
            # 连接信号
            self.process_thread.result_signal.connect(self.handle_result, Qt.ConnectionType.QueuedConnection)

            log_debug(f"信号定义: {self.process_thread.result_signal}")
        
            
            # 启动线程
            self.process_thread.start()
        except Exception as e:
            import traceback
            log_error(f"创建或启动线程出错: {e}\n{traceback.format_exc()}")
        
    def handle_result(self, n, threshold):
        print(f"--- handle_result CALLED with n={n}, threshold={threshold} ---")
        try:
            alert_success(f"计算完成！N值为{n}，阈值为{threshold}")
            # 处理逻辑...
        except Exception as e:
            import traceback
            log_error(f"handle_result 内部出错: {e}\n{traceback.format_exc()}")

        

                



                

            



        
        

        
        
        
            



        

        


   