import torch
import torch.nn as nn
import torchvision.models as models

class CircleCenterNet(nn.Module):
    def __init__(self, pretrained=True):
        super().__init__()
        # 使用预训练的ResNet18作为backbone
        resnet_weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        backbone = models.resnet18(weights=resnet_weights)
        # 修改第一层以接收灰度图输入
        #1通道灰度图
        backbone.conv1 = nn.Conv2d(1, 64, kernel_size=7, stride=2, padding=3, bias=False)
        
        # 提取特征层
        #去掉最后平均池化和全连接层
        self.features = nn.Sequential(*list(backbone.children())[:-2])
        
        # 热力图头部 (包含上采样以恢复到原始尺寸)
        #卷积+上采样
        self.heatmap_head = nn.Sequential(
            # 减少通道
            nn.Conv2d(512, 256, 3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(inplace=True),
            
            # 第一次上采样 8x8 -> 32x32
            nn.ConvTranspose2d(256, 128, kernel_size=4, stride=4, padding=0),
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),
            
            # 第二次上采样 32x32 -> 128x128
            nn.ConvTranspose2d(128, 64, kernel_size=4, stride=4, padding=0),
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),
            
            # 第三次上采样 128x128 -> 256x256
            nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2, padding=0),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            
            # 最终输出为1通道热力图
            nn.Conv2d(32, 1, 1),
            nn.Sigmoid()
        )

    def forward(self, x):
        features = self.features(x)
        heatmap = self.heatmap_head(features)
        return heatmap
