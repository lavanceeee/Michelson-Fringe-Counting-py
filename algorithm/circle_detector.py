import cv2
import numpy as np
from core.log_manager import log_info, log_error, log_debug, log_warning
import time

#新的圆心检测
class CircleDetector:
    @staticmethod
    def process_opencv_frame(frame):

        from algorithm.cnn_circle_detector import get_heatmap_and_center
        result = get_heatmap_and_center(frame)
        if result is None:
            return frame.copy(), 0
        
        output_heatmap, center_xy = result
        if center_xy:
            # center_xy 是来自 256x256 热力图的坐标 (x, y)
            heatmap_x, heatmap_y = center_xy[0], center_xy[1]

            # 获取原始帧的尺寸
            original_h, original_w = frame.shape[:2]

            # 计算从 256x256 缩放回原始尺寸的比例
            scale_x = original_w / 256.0
            scale_y = original_h / 256.0

            # 将热力图坐标缩放回原始帧坐标
            original_center_x = heatmap_x * scale_x
            original_center_y = heatmap_y * scale_y

            # 转换为整数坐标用于绘制
            center_x_int = int(original_center_x)
            center_y_int = int(original_center_y)

            marked_frame = frame.copy()
            # 使用缩放后的坐标在原始帧副本上画圆
            cv2.circle(marked_frame, (center_x_int, center_y_int), radius=5, color=(0, 255, 0), thickness=-1)

            log_debug(f"圆心坐标: ({center_x_int}, {center_y_int}),已标记，调用circle_detector.py结束")
            return marked_frame, 1
        else:
            log_warning("circle_detector.py调用cnn_circle_detector.py未检测到圆心")
            return frame.copy(), 0