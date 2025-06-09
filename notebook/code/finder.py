import cv2
import numpy as np
import matplotlib.pyplot as plt

def find_circle_center_voting(clean_img, min_radius=10, max_radius=None):
    if max_radius is None:
        max_radius = int(min(clean_img.shape) * 0.5)  #70%

    edges = cv2.Canny(clean_img, 50, 150)

    sobel_x = cv2.Sobel(clean_img, cv2.CV_64F, 1, 0, ksize=5)
    sobel_y = cv2.Sobel(clean_img, cv2.CV_64F, 0, 1, ksize=5)

    accumulator = np.zeros_like(clean_img, dtype=np.float32)

    edge_points = np.column_stack(np.where(edges > 0))

    #vote
    for y, x in edge_points:
        # Gradient Vector
        gx = sobel_x[y, x]
        gy = sobel_y[y, x]
        mag = np.sqrt(gx ** 2 + gy ** 2)

        if mag < 1e-5:
            continue

        # 归一化
        nx = gx / mag
        ny = gy / mag

        for direction in [-1, 1]:

            for r in range(min_radius, max_radius + 1): 
                cx = int(x + direction * r * nx)
                cy = int(y + direction * r * ny)

                if 0 <= cy < accumulator.shape[0] and 0 <= cx < accumulator.shape[1]:
                    accumulator[cy, cx] += 1

    # find center(max of voting result)
    _, _, _, max_loc = cv2.minMaxLoc(accumulator)
    center_x, center_y = max_loc

    # 可视化累加器
    plt.figure(figsize=(10, 5))
    plt.subplot(121), plt.imshow(accumulator, cmap='hot'), plt.title('Accumulator Space')
    plt.subplot(122), plt.imshow(cv2.cvtColor(clean_img, cv2.COLOR_GRAY2RGB))
    plt.scatter(center_x, center_y, s=100, c='red', marker='+')
    plt.title('Detected Center')
    plt.show()

    return center_x, center_y