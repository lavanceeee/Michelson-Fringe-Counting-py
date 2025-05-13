
class FigureN:

    @staticmethod
    def figureN(average_brightness, center_brightness_save):
        
        total_points = len(center_brightness_save)

        #亮度阈值
        threshold = average_brightness

        #计数
        crossings = 0

        above_threshold = center_brightness_save[0] > threshold

        for i in range(1, total_points):
            current_above = center_brightness_save[i] > threshold
            if current_above != above_threshold:
                crossings += 1
                current_above = above_threshold

        N = crossings / 2
        return N
        





