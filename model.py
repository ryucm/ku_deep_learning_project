import torch.nn as nn
from torchvision import models
import config


class ConvBlock(nn.Module):
    def __init__(self, in_ch, out_ch):
        super().__init__()
        self.block = nn.Sequential(
            nn.Conv2d(in_ch, out_ch, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_ch),
            nn.ReLU(inplace=True),
            nn.MaxPool2d(2),
        )

    def forward(self, x):
        return self.block(x)


class CustomCNN(nn.Module):
    """
    입력: (B, 3, 224, 224)
    features: Conv 블록 4개 → (B, 256, 14, 14)
    encoder:  AdaptiveAvgPool → Flatten → Linear → 512-dim 벡터
    head:     Linear → num_classes
    """
    def __init__(self, num_classes=config.NUM_CLASSES):
        super().__init__()
        self.features = nn.Sequential(
            ConvBlock(3,   32),
            ConvBlock(32,  64),
            ConvBlock(64,  128),
            ConvBlock(128, 256),
        )
        self.encoder = nn.Sequential(
            nn.AdaptiveAvgPool2d(1),
            nn.Flatten(),
            nn.Linear(256, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.5),
        )
        self.head = nn.Linear(512, num_classes)

    def encode(self, x):
        """512-dim 스타일 벡터 반환 (추천에 사용)"""
        return self.encoder(self.features(x))

    def forward(self, x):
        return self.head(self.encode(x))


class ResNet18(nn.Module):
    """
    ImageNet 사전학습 ResNet18.
    backbone: FC 제거한 ResNet → 512-dim 벡터
    head:     Linear → num_classes
    """
    def __init__(self, num_classes=config.NUM_CLASSES, pretrained=True):
        super().__init__()
        weights = models.ResNet18_Weights.IMAGENET1K_V1 if pretrained else None
        base = models.resnet18(weights=weights)
        self.backbone = nn.Sequential(*list(base.children())[:-1])  # (B, 512, 1, 1)
        self.head = nn.Linear(512, num_classes)

    def encode(self, x):
        """512-dim 스타일 벡터 반환 (추천에 사용)"""
        return self.backbone(x).flatten(1)

    def forward(self, x):
        return self.head(self.encode(x))
