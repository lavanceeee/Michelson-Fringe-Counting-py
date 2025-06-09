import numpy as np
from scipy import ndimage

from core.log_manager import log_debug


class FigureN:

    @staticmethod
    def figureN(center_brightness_save):
        brightness_array = np.array(center_brightness_save)
        
        # 高斯平滑
        smoothed_data = ndimage.gaussian_filter1d(brightness_array, sigma=5)
        
        # 计算平滑后数据的平均值作为阈值
        threshold = round(np.mean(smoothed_data), 2)

        # 计数穿越
        crossings = 0
        above_threshold = smoothed_data[0] > threshold
        
        for i in range(1, len(smoothed_data)):

            current_above = smoothed_data[i] > threshold

            if current_above != above_threshold:

                crossings += 1

                above_threshold = current_above
                
        N = int(crossings / 2)
        return N, threshold, smoothed_data
        





