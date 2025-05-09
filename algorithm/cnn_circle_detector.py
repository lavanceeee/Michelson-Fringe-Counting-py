import torch
from models.network import CircleCenterNet
from core.log_manager import log_info, log_debug, log_error
from utils.image_pre_processing import preprocess_for_circle_detection
import numpy as np

#全局变量：加载模型 设备
inference_model = None 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

#峰值坐标查找函数
def find_peak_coordinates(heatmaps):
    batch_size, _, height, width = heatmaps.shape
    peak_coords = []

    #展平空间维度,用来计算峰值坐标
    heatmaps_flat = heatmaps.view(batch_size, -1)

    #找到展平后heatmaps中最大值的索引
    _, max_indices = torch.max(heatmaps_flat, dim=1)

    #将一维索引转换为二维坐标
    for idx in max_indices:
        y = (idx // width).item()
        x = (idx % width).item()
        peak_coords.append((x, y))

    return peak_coords

#模型加载函数
def load_inference_model(model_weight_path):
    global inference_model

    try:
        log_info(f"正在从{model_weight_path}加载模型权重")

        inference_model = CircleCenterNet(pretrained=False) #pretrained=False 表示加载自己的权重

        #加载权重
        checkpoint = torch.load(model_weight_path, map_location=DEVICE)

        #获取state_dict
        state_dict = checkpoint.get('model_state_dict', checkpoint)

        #加载模型权重
        inference_model.load_state_dict(state_dict)

        #将模型移动到合适设备
        inference_model.to(DEVICE)

        #设置为评估模式
        inference_model.eval()

        log_debug(f"模型成功加载到{DEVICE}")
        return True
    except Exception as e:
        log_error(f"模型加载失败: {e}")
        inference_model = None
        return False
    

#主功能函数
def get_heatmap_and_center(image):
    #将image处理为图像张量
    #期望 shape: [1, 256, 256] 或 [1, 1, 256, 256]。
    processed_image_np = preprocess_for_circle_detection(image)

    if not isinstance(processed_image_np, np.ndarray):
        log_error(f"预处理失败，返回值类型为 {type(processed_image_np)}, 期望是 np.ndarray。跳过此帧。")
        return None 

    # 将Numpy数组转换为PyTorch张量,并确保是float类型
    # 只有当 processed_image_np 是有效的 NumPy 数组时，这行代码才会执行
    image_tensor = torch.from_numpy(processed_image_np).float()

    global inference_model #访问全局变量
    if inference_model is None:
        log_error("模型未加载,请先加载模型")
        return None
    
    #确保输入张量在正确的设备上
    input_tensor = image_tensor.to(DEVICE)

    # --- 确保输入维度正确: [Batch, Channel, Height, Width] ---
    if input_tensor.ndim == 3: # C, H, W (假设 Channel=1)
        input_tensor = input_tensor.unsqueeze(0) # 添加 Batch 维度 -> [1, C, H, W]
    elif input_tensor.ndim == 2: # H, W (假设灰度图)
        input_tensor = input_tensor.unsqueeze(0).unsqueeze(0) # 添加 Batch 和 Channel 维度 -> [1, 1, H, W]

    # 检查最终维度是否符合预期
    if input_tensor.ndim != 4 or input_tensor.shape[0] != 1 or input_tensor.shape[1] != 1:
        log_error(f"错误：输入张量维度不正确 ({input_tensor.shape})，期望 [1, 1, H, W]")
        return None
    
    try:
        #执行推理
        # 推理时不需要计算梯度
        with torch.no_grad():
            output_heatmap = inference_model(input_tensor) # 输出 shape 应该是 [1, 1, H, W]

        # --- 从热力图计算中心点 ---
        # find_peak_coordinates 需要 [B, C, H, W] 输入
        predicted_coords_list = find_peak_coordinates(output_heatmap)
        center_xy = predicted_coords_list[0] if predicted_coords_list else None

        return output_heatmap, center_xy
    except Exception as e:
        log_error(f"推理失败: {e}")
        return None















