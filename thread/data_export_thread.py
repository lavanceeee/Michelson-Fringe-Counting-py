from PyQt6.QtCore import QThread
from openpyxl import Workbook
import matplotlib
matplotlib.use('Agg')  # 禁用 GUI 后端，避免线程中崩溃
import matplotlib.pyplot as plt
plt.rcParams['font.family'] = 'Microsoft YaHei'  # 使用黑体
# 避免负号乱码（必须）
plt.rcParams['axes.unicode_minus'] = False

class DataExportThread(QThread):
    def __init__(self, parent=None, 
                 data_type=None, 
                 smoothed_data=None, 
                 result_N=None, 
                 threshold=None,
                 save_path=None):
        
        super().__init__(parent)
        self.data_type = data_type
        self.smoothed_data = smoothed_data
        self.result_N = result_N
        self.threshold = threshold
        self.save_path = save_path

    def run(self):
        try:
            if self.data_type == "亮度数组(xlsx)":
                self.export_excel()
            elif self.data_type == "亮度图(png)":
                self.export_png()
            elif self.data_type == "已录制视频(mp4)":
                self.export_video()
        except Exception as e:
            print(f"导出数据时发生错误: {e}")

    def export_excel(self):
        wb = Workbook()
        ws = wb.active #获取默认工作表

        ws.title = "result_data" #sheet重命名
        ws.append(["帧率", "亮度值(平滑后)", "N值"])

        for i in range(len(self.smoothed_data)):
            if i == 0:
                ws.append([i, self.smoothed_data[i], self.result_N])
            else:
                ws.append([i, self.smoothed_data[i]])

        if self.save_path:
            wb.save(self.save_path)
        else:
            return

    def export_png(self):
        x_data = list(range(len(self.smoothed_data)))
        x_data = list(range(len(self.smoothed_data)))
        y_data = self.smoothed_data

        fig = plt.figure(figsize=(10, 5))
        grid = fig.add_gridspec(1, 2, width_ratios=[2, 1])

        #左侧画图
        ax_plot = fig.add_subplot(grid[0, 0])
        ax_plot.plot(x_data, y_data, color="blue", linewidth=2, label="Smoothed Data")
        ax_plot.set_title("亮度值(平滑处理)")
        ax_plot.set_xlabel("帧数")
        ax_plot.set_ylabel("亮度值")
        ax_plot.legend()

        #右侧的文本
        ax_info = fig.add_subplot(grid[0, 1])
        ax_info.axis("off") #关闭坐标轴

        #添加文本
        ax_info.text(0.5, 0.5, f"N值: {self.result_N}", 
                     ha="center", va="center", 
                     fontsize=12, 
                     bbox=dict(facecolor="white", alpha=0.8))
        
        plt.tight_layout()
        if self.save_path:
            plt.savefig(self.save_path)
        else:
            return
        plt.close()

    def export_video(self):
        return
        











    

    