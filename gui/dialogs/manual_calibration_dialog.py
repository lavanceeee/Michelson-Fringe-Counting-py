from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QHBoxLayout, QPushButton)
from core.log_manager import log_debug, log_error, log_info

from gui.components.manual_pixmap_view import ManualPixmapView
"""
手动标定对话弹窗
"""

class ManualCalibrationDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)
        log_debug("手动标定对话框被创建")
        self.frame_label = None #声明frame_label
        self.setup_ui()

        #当前帧的图像全局变量
        self.frame_when_click = None

        #坐标数组
        self.xy_position = [0, 0]

    def setup_ui(self):

        self.setWindowTitle("手动标定")
        self.setFixedSize(600,500)

        #主布局为水平布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        #创建显示标定帧的Label
        self.frame_label = ManualPixmapView(self)
        self.frame_label.setStyleSheet(
            """
            QLabel {
                border: 2px solid #666666;
                border-radius: 5px;
            }              
            """)

        main_layout.addWidget(self.frame_label)

        #右侧信息显示与确定区域
        function_widget = QWidget()
        function_layout = QVBoxLayout()
        #将function_layout添加到function_widget
        function_widget.setLayout(function_layout)

        btn1 = QPushButton("测试", self)
        btn1.setFixedSize(300, 250)
        function_layout.addWidget(btn1)

        main_layout.addWidget(function_widget)

#连接摄像头并显示画面
    def set_frame(self, pixmap):
        log_debug("进入manual函数的update_frame")

        try:
            if pixmap is None:
                log_error("update_frame | 传入是None")
                return
            else:
                log_debug("update_camera函数 | is not None")

                log_info("2.-----pixmap-----")
                log_info(pixmap.width())
                log_info(pixmap.height())
                log_info("-----pixmap-----")

                self.frame_when_click = pixmap

                self.frame_label.set_base_pixmap(pixmap)

                #鼠标追踪
                self.frame_label.setMouseTracking(True)

                #鼠标移动信号连接
                self.frame_label.mouseMoveEvent = self.mouse_move_event
        except Exception as e:
            log_error(f"手动标定函数中的update_frame出错:{e}")

    """
    鼠标点击事件:
    1. 获取坐标
    2. 记录在数组
    """
    def mouse_move_event(self, event):
        log_info("鼠标移动了，触发mouse_move_event函数")

        label_width = self.frame_label.width()
        label_height = self.frame_label.height()
        pixmap = self.frame_label.pixmap()
        if pixmap:
            img_width = pixmap.width()
            img_height = pixmap.height()
            log_info("-----")
            log_info(f"图像尺寸: {img_width}x{img_height}")
            log_info(f"组件的尺寸：{label_width}x{label_height}")
            log_info("-----")

        #鼠标点击的相对位置，就是像素位置
        pos = event.pos()
        self.xy_position = [pos.x(), pos.y()]

        log_info(f"鼠标坐标：x:{pos.x()}, y:{pos.y()}")

        log_info(f"数组中的坐标确认：{self.xy_position[0]},{self.xy_position[1]}")

        if self.xy_position[0] != 0 and self.xy_position[1] != 0 and pixmap:

            # marked_pixmap = self.draw_mark(self.frame_when_click, self.xy_position)
            # self.frame_label.setPixmap(marked_pixmap)

            self.frame_label.set_maker(pos)

    # """
    # 实时绘制可视化十字并显示
    # 直接使用QPainter
    # """
    # @staticmethod
    # def draw_mark(pixmap,position):
    #     try:
    #         #不使用原图像
    #         pixmap_copy = pixmap.copy()

    #         #初始化QPainter
    #         painter = QPainter(pixmap_copy)

    #         #绘图参数 QPen
    #         pen = QPen(QColor(255,0,0),2)
    #         pen.setWidth(2)
    #         painter.setPen(pen)

    #         center_x = position[0]
    #         center_y = position[1]

    #         log_debug("----draw_mark中的坐标----")
    #         log_debug(f"----center_x:{center_x}, center_y:{center_y}----")

    #         #绘制水平和竖直十字
    #         painter.drawLine(0, center_y, pixmap_copy.width(), center_y)
    #         painter.drawLine(center_x, 0, center_x, pixmap_copy.height())

    #         painter.end()

    #         return pixmap_copy
    #     except Exception as e:
    #         log_debug(f"调用draw_mark抛出异常:{e}")
    #         return None



        

        






























