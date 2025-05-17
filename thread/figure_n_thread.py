from PyQt6.QtCore import QThread, pyqtSignal
from algorithm.figure_N import FigureN
import time

class FigureNThread(QThread):

    #开始信号
    is_running = pyqtSignal(bool)
    finished_data_signal = pyqtSignal(int, float, list)

    def __init__(self, brightness_list):
        super().__init__()
        self.brightness_list = brightness_list

    def run(self):
        try:
            self.is_running.emit(True)
            n, threshold, smoothed_data = FigureN.figureN(self.brightness_list)

            time.sleep(5)
            self.is_running.emit(False)

            self.finished_data_signal.emit(n, threshold, smoothed_data)

        except Exception as e:
            print(f"计算N值时发生错误: {e}")

