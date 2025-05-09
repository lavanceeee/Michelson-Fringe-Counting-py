import cv2
import numpy as np
from core.log_manager import log_info, log_error, log_debug, log_warning
import time

class CircleDetector:
    #圆环检测
    #动态数组，保存每一个圆的x,y坐标
    # circle_center_positions = []

    # @staticmethod
    # def process_preprocessed_frame(blurred):

    #     start_time = time.perf_counter()
        
    #     try:
    #         # 创建副本用于绘制，避免修改原始输入
    #         result_image = blurred.copy()
            
    #         # 执行圆环检测
    #         circles = cv2.HoughCircles(
    #             blurred, 
    #             cv2.HOUGH_GRADIENT,
    #             dp=1, 
    #             minDist=20,
    #             param1=60, #比例柔和的边缘选小一点
    #             param2=200, #一个圆需要多少边缘投投票点才可以被选出来
    #             minRadius=10,
    #             maxRadius=250
    #         )
            
    #         if circles is not None:
    #             #np.around 四舍五入
    #             #转换为无符号16位整数
    #             circles = np.uint16(np.around(circles))

    #             for circle in circles[0, :]:
    #                 center_x, center_y, radius = circle

    #                 # 1. 圆环轮廓 - 使用黑色 (0)，在亮区域能清楚看到
    #                 cv2.circle(result_image, (center_x, center_y), radius, 0, 2)
            
    #                 #将圆心坐标加入动态数组
    #                 CircleDetector.circle_center_positions.append((center_x, center_y))
    #         #未检测到圆环
    #         else:
    #             log_error("--------------------------------")
    #             log_error("这一帧没检测到圆环，请调整？")
    #             log_error("--------------------------------")

    #         # 得到一系列的圆心，计算它们的中心值
    #         if CircleDetector.circle_center_positions:
    #             average_circle_x = sum(position[0] for position in CircleDetector.circle_center_positions) / len(CircleDetector.circle_center_positions)
    #             average_circle_y = sum(position[1] for position in CircleDetector.circle_center_positions) / len(CircleDetector.circle_center_positions)

    #             # 计算中心点
    #             center_x = int(average_circle_x)
    #             center_y = int(average_circle_y)

    #             log_debug(f"平均圆心坐标: ({center_x}, {center_y})")

    #             #直接标定平均的圆心
    #             cv2.circle(result_image, (center_x, center_y), 5, 255, -1)
 
    #         # 计算处理时间
    #         end_time = time.perf_counter()
    #         duration_ms = (end_time - start_time) * 1000
    #         log_debug(f"----Frame processing time: {duration_ms:.2f} ms----")
            
    #         num_circles = circles.shape[1] if circles is not None else 0
    #         return result_image, num_circles
            
    #     except Exception as e:
    #         log_error(f"Detect circles error: {e}")
    #         return blurred, 0 #出错时返回0个圆
            
    @staticmethod
    def process_opencv_frame(frame):
        """
        原始的处理方法，现在内部使用预处理+处理的组合
        """
        # from utils.image_pre_processing import preprocess_for_circle_detection
        
        # # 先进行预处理
        # blurred = preprocess_for_circle_detection(frame)
        # if blurred is None:
        #     return frame, 0   
        # 调用新方法处理
        # return CircleDetector.process_preprocessed_frame(blurred)
    
        #调用cnn_circle_detector.py
        from algorithm.cnn_circle_detector import get_heatmap_and_center
        result = get_heatmap_and_center(frame)
        if result is None:
            log_debug("circle_detector.py调用cnn_circle_detector.py图像为None")
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