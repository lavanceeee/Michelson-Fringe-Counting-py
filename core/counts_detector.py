import numpy as np
from core.log_manager import log_warning, log_info, log_error, log_debug
from PyQt6.QtCore import QObject, pyqtSignal
from utils.image2numpyArray import ImageConverter

class CountsDetector(QObject): #继承QObject支持信号槽

    #每次更新的中心亮度
    center_brightness_signal = pyqtSignal(float)

    def __init__(self, parent=None):

        super().__init__(parent)

        self.center_pos = []

        self.center_pos_array = []

        self.start_update_frame = False


    def start_cout(self, center_list):

        self.center_pos = center_list

        #发送开始信号
        self.start_update_frame = True

    #更新帧率
    #frame 为QImage
    def update_frame(self, qimage_frame):
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
        
        # 实时发送数组坐标并渲染
        self.center_brightness_signal.emit(brightness)










    




         

    


        
        
