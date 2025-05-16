from PyQt6.QtCore import QThread, pyqtSignal
import cv2
from algorithm.figure_N import FigureN
import logging
from core.log_manager import log_warning, log_info, log_debug, log_error

log_debug = logging.getLogger('debug_logger').debug
log_error = logging.getLogger('error_logger').error

class VideoProcessingThread(QThread):
    # 定义信号

    result_signal = pyqtSignal(int, float)  # N值、阈值
    
    def __init__(self, video_path, center_pos):
        super().__init__()
        self.video_path = video_path
        self.center_pos = center_pos
        
    def run(self):
        cap = None # Initialize cap to None
        try:
            print("线程开始执行")
            
            # 视频处理过程中添加更多日志
            print(f"打开视频: {self.video_path}")
            
            cap = cv2.VideoCapture(self.video_path)
            print("执行完打开操作")
            if not cap.isOpened(): # Check if cap was opened successfully
                print(f"无法打开视频文件: {self.video_path}")
                return

            total_frame = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            center_brightness_list = []
            x, y = self.center_pos.x(), self.center_pos.y()
            
            for _ in range(1, total_frame):
                ret, frame = cap.read()
                if not ret:
                    break
                    
                # 处理帧
                gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                if 0 <= y < gray_frame.shape[0] and 0 <= x < gray_frame.shape[1]:
                    brightness = gray_frame[y, x]
                    center_brightness_list.append(brightness)
                    
            # 计算结果
            if not center_brightness_list: # Check if list is empty
                print("未能收集到亮度数据，无法计算N值")
                return

            n, threshold, _ = FigureN.figureN(center_brightness_list)
            
            
            # 在发送信号前添加日志
            print(f"准备发送结果信号: n={n}, threshold={threshold}")
            
            # 发送结果信号
            self.result_signal.emit(n, threshold)
            
            
            # cap.release() # Moved to finally block
            
            print("线程执行完成")
        except Exception as e:
            import traceback
            print(f"线程执行出错: {e}\n{traceback.format_exc()}")
        finally:
            if cap is not None and cap.isOpened(): # Ensure cap is not None and is opened before releasing
                cap.release()
                print("摄像头资源已在finally中释放")
