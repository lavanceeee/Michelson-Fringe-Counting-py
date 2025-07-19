import cv2
import numpy as np
import code.finder as finder
from matplotlib import pyplot as plt

#change to your own image
img = cv2.imread("test/img.png")
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

blur = cv2.GaussianBlur(gray, (5,5), 0)

threshold_val = 40
_, binary = cv2.threshold(blur, threshold_val, 255, cv2.THRESH_BINARY)

#open operation
kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 4))
opened = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

#clean
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(opened, connectivity=8)
clean = np.zeros_like(gray)

for i in range(1, num_labels):
    area = stats[i, cv2.CC_STAT_AREA]
    #600,1500 -> 300,2000 -> 300,2800
    if 300 < area < 2800:
        clean[labels == i] = 255

#100,2500 -> 100,None
x0, y0 = finder.find_circle_center_voting(clean,100)

#results visuable
output = img.copy()
x0, y0 = int(x0), int(y0)
cross_len = 20

cv2.line(output, (x0 - cross_len, y0), (x0 + cross_len, y0), (255, 0, 255), thickness=5)
cv2.line(output, (x0, y0 - cross_len), (x0, y0 + cross_len), (255, 0, 255), thickness=5)

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
original_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
plt.imshow(original_rgb)
plt.title("original image")
plt.axis('off')

plt.subplot(1, 2, 2)
output_rgb = cv2.cvtColor(output, cv2.COLOR_BGR2RGB)
plt.imshow(output_rgb)
plt.title("output")
plt.axis('off')

plt.tight_layout()
plt.show()





