from PyQt6.QtWidgets import QDialog, QProgressBar, QLabel, QVBoxLayout
from PyQt6.QtCore import Qt

class LoadingDialog:
    def __init__(self, parent=None):
        self.parent = parent
        self.dialog = None
        
    def show(self, message="正在计算，请稍候..."):

        if not self.dialog:
            self.dialog = QDialog(self.parent)
            self.dialog.setWindowTitle("请稍候")
            self.dialog.setWindowFlags(Qt.WindowType.Dialog | 
                                      Qt.WindowType.CustomizeWindowHint | 
                                      Qt.WindowType.WindowTitleHint)
            self.dialog.setModal(True)
            
            layout = QVBoxLayout()
            
            # 创建提示标签
            self.label = QLabel(message)
            self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # 创建进度条
            self.progress_bar = QProgressBar()
            self.progress_bar.setRange(0, 0)  # 不确定模式
            
            layout.addWidget(self.label)
            layout.addWidget(self.progress_bar)
            
            self.dialog.setLayout(layout)
            
        self.label.setText(message)
        
        self.dialog.show()
        
    def hide(self):
        if self.dialog:
            self.dialog.close()
