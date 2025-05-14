import numpy as np
from core.log_manager import log_warning, log_info, log_error, log_debug
from PyQt6.QtCore import QObject, pyqtSignal
from utils.image2numpyArray import ImageConverter

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

        self.average_brightness = 0

        self.center_pos_array = []

        #临时的更新时间
        self.update_time = 0

    def start_cout(self, center_list):
        #开始检测
        self.start_signal = True

        self.center_pos = center_list

    #更新帧率
    #frame 为QImage
    def update_frame(self, qimage_frame):
        self.current_frame = qimage_frame

        #转换为numpy数组
        frame = ImageConverter.image2numpyArray(qimage_frame)

        if len(frame.shape) == 2:  # 灰度图
            brightness = frame[self.center_pos[1], self.center_pos[0]]
        else:  # 多通道图像
            # 获取所有通道的值并计算亮度
            pixel_values = frame[self.center_pos[1], self.center_pos[0]]
            brightness = np.mean(pixel_values)

        #转换为小数并保留两位
        brightness = round(float(brightness), 2)

        self.center_pos_array.append(brightness)

        self.update_time += 1
        
        # 实时发送数组坐标并渲染
        self.center_brightness_signal.emit(brightness, self.update_time)










    




         

    


        
        
