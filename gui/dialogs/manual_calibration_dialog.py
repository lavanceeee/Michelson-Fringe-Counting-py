from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QWidget, QHBoxLayout,QMessageBox, QFrame, QLabel)
from core.log_manager import log_debug, log_error

from gui.components.manual_pixmap_view import ManualPixmapView
"""
手动标定对话弹窗
"""

class ManualCalibrationDialog(QDialog):

    def __init__(self, parent=None):

        super().__init__(parent)

        self.frame_label = None #声明frame_label

        #定义坐标数组于setup_ui上面
        self.xy_position = [0, 0]

        self.setup_ui()

        #当前帧的图像全局变量
        self.frame_when_click = None

    def setup_ui(self):

        self.setWindowTitle("手动标定")
        self.setFixedSize(600,500)

        #主布局为水平布局
        main_layout = QHBoxLayout()
        self.setLayout(main_layout)

        #1. 左侧标定帧的Label
        self.frame_label = ManualPixmapView(self)

        main_layout.addWidget(self.frame_label)

        #2. 右侧辅助信息框

        #2.1 QFrame QWidget的子组件
        frame = QFrame()
        frame.setFixedSize(256, 256)

        #布局管理器
        layout = QVBoxLayout(frame)
        #布局边界与控件之间的距离:上、左、右、下
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)

        #2.2 内容
        alert_label = QLabel("提示")

        alert_text01 = QLabel("在左侧当前帧找到干涉圆心")
        alert_text02 = QLabel("将鼠标放置左侧当前帧") 
        alert_text03 = QLabel("左键鼠标以确认")
        alert_text04 = QLabel(":)")

        alert_divider = QLabel("--------------------------------")

        alert_pos_info_alert = QLabel("您当前选定的坐标为：")
        self.alert_pos_info = QLabel("当前还未进行标定")

        #添加到布局
        layout.addWidget(alert_label)
        layout.addWidget(alert_text01)
        layout.addWidget(alert_text02)
        layout.addWidget(alert_text03)
        layout.addWidget(alert_text04)
        layout.addWidget(alert_divider)
        layout.addWidget(alert_pos_info_alert)
        layout.addWidget(self.alert_pos_info)

        layout.addStretch(1)

        #3. 将frame添加到主布局
        main_layout.addWidget(frame)

#连接摄像头并显示画面
    def set_frame(self, pixmap):

        try:
            if pixmap is None:
                log_error("update_frame | 传入是None")
                return
            else:

                self.frame_when_click = pixmap

                self.frame_label.set_base_pixmap(pixmap)

                #鼠标追踪
                self.frame_label.setMouseTracking(True)

                #鼠标移动监听
                self.frame_label.mouseMoveEvent = self.mouse_move_event

                #鼠标点击监听
                self.frame_label.mousePressEvent = self.mouse_click_event
        except Exception as e:
            log_error(f"手动标定函数中的update_frame出错:{e}")

    """
    鼠标移动事件:
    1. 获取坐标
    2. 记录在数组
    """
    def mouse_move_event(self, event):
        pixmap = self.frame_label.pixmap()

        #鼠标点击的相对位置，就是像素位置
        pos = event.pos()
        self.xy_position = [pos.x(), pos.y()]

        if self.xy_position[0] != 0 and self.xy_position[1] != 0 and pixmap:

            self.frame_label.set_maker(pos)

            # 更新右侧坐标信息
            self.alert_pos_info.setText(f"{self.xy_position[0]}x{self.xy_position[1]}")

    """
    鼠标点击事件
    """
    def mouse_click_event(self, event):
        # 创建消息框
        msg_box = QMessageBox(
            QMessageBox.Icon.Question,
            "确定圆心",
            f"您已选定圆心坐标为十字处：{self.xy_position[0]}x{self.xy_position[1]},是否继续？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            self
        )

        # 自定义按钮文本
        msg_box.button(QMessageBox.StandardButton.Yes).setText("确定")
        msg_box.button(QMessageBox.StandardButton.No).setText("取消")

        # 获取结果
        reply = msg_box.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.accept()
        else:
            log_debug("选择了取消")

