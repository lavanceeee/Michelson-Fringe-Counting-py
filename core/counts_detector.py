import numpy as np
from core.log_manager import log_warning, log_info, log_error, log_debug
from PyQt6.QtCore import QObject, pyqtSignal

class CountsDetector(QObject): #继承QObject支持信号槽

    #平均亮度信号
    average_brightness_signal = pyqtSignal(float)
    #每次更新的中心亮度
    center_brightness_signal = pyqtSignal(float, float)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.center_pos = [0,0]

        self.current_frame = None

        self.start_signal = False

        self.first_frame = None

        self.average_brightness = 0

        #临时的更新时间
        self.update_time = 0

    def start_cout(self, center_list, first_frame):
        #开始检测
        self.start_signal = True

        self.center_pos = center_list

        self.first_frame = first_frame
        self.average_brightness = np.mean(first_frame)

        #发送信号
        self.average_brightness_signal.emit(self.average_brightness)

    #更新帧率
    def update_frame(self, frame):
        self.current_frame = frame

        # 计算此刻中心点的亮度
        brightness = self.calculate_current_frame_center_brightness(frame)
        
        # 将BGR数组转换为单个亮度值
        if isinstance(brightness, np.ndarray):
            # 方法1: BGR平均值
            brightness_value = float(np.mean(brightness))
            
            # 或者方法2: 标准灰度转换公式
            # brightness_value = float(0.299 * brightness[2] + 0.587 * brightness[1] + 0.114 * brightness[0])
        else:
            brightness_value = float(brightness)
        
        self.update_time += 0.1
        
        # 发送转换后的浮点数
        self.center_brightness_signal.emit(brightness_value, self.update_time)

    def calculate_current_frame_center_brightness(self, frame):
        log_info("---通道数---")
        log_info(f"{frame.shape}")

        brightness = frame[self.center_pos[1], self.center_pos[0]]

        return brightness









    




         

    


        
        
