from PyQt6.QtCore import QThread, pyqtSignal
import cv2
from algorithm.figure_N import FigureN

class VideoProcessingThread(QThread):
    # 定义信号

    result_signal = pyqtSignal(int, float)  # N值、阈值
    
    def __init__(self, video_path, center_pos):
        super().__init__()
        self.video_path = video_path
        self.center_pos = center_pos
        
    def run(self):
        cap = None 
        try:
            cap = cv2.VideoCapture(self.video_path)

            if not cap.isOpened(): 
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

            n, threshold, _ = FigureN.figureN(center_brightness_list)
            
            # 发送结果信号
            self.result_signal.emit(n, threshold)
            
        except Exception as e:
            import traceback
            print(f"线程执行出错: {e}\n{traceback.format_exc()}")
            
        finally:
            if cap is not None and cap.isOpened(): 
                cap.release()

