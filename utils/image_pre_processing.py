import cv2
import numpy as np
from core.log_manager import log_error

def preprocess_for_circle_detection(frame):
    try:
        # 确保输入是 NumPy 数组
        if not isinstance(frame, np.ndarray):
            raise TypeError(f"输入类型应为 NumPy 数组，但收到 {type(frame)}")

        target_size = (256, 256)

        # resize
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
        elif len(frame.shape) == 3 and frame.shape[2] == 4: # 例如 BGRA
             # resize 四通道图像
             resized_bgra = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
             # 丢弃 alpha 通道
             resized = resized_bgra[:, :, :3]
        elif len(frame.shape) == 2:
            # 已经是单通道灰度图，直接 resize
            resized = cv2.resize(frame, target_size, interpolation=cv2.INTER_LINEAR)
            # resized = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR) # 或者直接返回灰度
            gray = resized # 如果已经是灰度，直接赋值
            return gray 
        else:
            raise ValueError(f"不支持的图像通道数: {frame.shape}")

        # 度图 
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

        return gray # 返回 uint8 [0, 255] 的灰度图

    except Exception as e:
        log_error(f"实时图像预处理错误: {e}")
        return None
