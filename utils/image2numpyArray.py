import numpy as np
from PyQt6.QtGui import QImage, QPixmap
import cv2

class ImageConverter:
    @staticmethod
    def image2numpyArray(image):
        if isinstance(image, QPixmap):
            # 转换为QImage
            qimage = image.toImage()
            return ImageConverter._processing(qimage)
        elif isinstance(image, QImage):
            return ImageConverter._processing(image)
        elif isinstance(image, np.ndarray):
            return image
        else:
            raise ValueError("输入的图像类型不支持")

    @staticmethod
    def _processing(qimage):
        # 确保图像是32位ARGB格式
        if qimage.format() != QImage.Format.Format_ARGB32:
            qimage = qimage.convertToFormat(QImage.Format.Format_ARGB32)
        
        # 获取图像尺寸
        width = qimage.width()
        height = qimage.height()

        # 将QImage转换为numpy数组
        ptr = qimage.bits()
        ptr.setsize(height * width * 4)  # 4 bytes per pixel (ARGB)
        arr = np.frombuffer(ptr, np.uint8).reshape((height, width, 4))
        
        # 转换为BGR格式（OpenCV格式）
        bgr = cv2.cvtColor(arr, cv2.COLOR_BGRA2BGR)
        
        return bgr