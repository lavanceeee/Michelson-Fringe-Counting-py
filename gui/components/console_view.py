from datetime import datetime

from PyQt6.QtWidgets import QWidget, QLabel, QVBoxLayout, QFrame, QTextEdit
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QTextCursor

class ConsoleView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()

    def setup_ui(self):

        self.setFixedSize(500, 250)

        # 创建布局
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop) # 内容顶部对齐
        layout.setContentsMargins(5, 5, 5, 5)       # 内部边距
        layout.setSpacing(5)                         # 元素间距

        # 创建标题标签
        self.title_label = QLabel("Terminal")

        # # 创建分隔线
        # self.separator_line = QFrame()
        # self.separator_line.setFrameShape(QFrame.Shape.HLine)  # 设置为水平线
        # self.separator_line.setFrameShadow(QFrame.Shadow.Sunken) # 使用默认的阴影效果来显示线条

        #创建日志文本区域
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True) #将文本区域设置为只读
        self.log_text.setLineWrapMode(QTextEdit.LineWrapMode.NoWrap) #设置不自动换行
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #f8f8f8;
                border: 1px solid #ddd;
                font-family: Consolas, Monospace;
                font-size: 10pt;
            }
        """)

        # 添加到布局
        layout.addWidget(self.title_label)
        # layout.addWidget(self.separator_line)
        layout.addWidget(self.log_text)

        # 添加伸展项，保持内容在顶部
        layout.addStretch(1)

        # 设置布局
        self.setLayout(layout)

    #level是日志级别，默认为info
    def add_log(self,message,level="info"):
        """添加日志消息到控制台"""
        color_map = {
            "INFO": "#000000",    # 黑色
            "WARNING": "#FFA500",  # 橙色
            "ERROR": "#FF0000",    # 红色
            "DEBUG": "#0000FF"     # 蓝色
        }

        #设置颜色
        #如果level不在color_map中，则使用默认颜色黑色
        color = color_map.get(level, "#000000")

        #格式化消息
        formatted_msg = f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{level}] {message}\n"

        #添加消息到文本区域
        #1.将光标移动到文本区域底部
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)
        #2.插入消息
        self.log_text.insertHtml(f'<span style="color:{color}">{formatted_msg}</span><br>')
        #3.滚动到最底部
        self.log_text.moveCursor(QTextCursor.MoveOperation.End)

    
        
