from torch.utils.data import Dataset
from torchvision import transforms
from PIL import Image
import config


def get_transforms(split):
    # 이미지가 이미 256×256으로 저장됨 → Resize 생략, CenterCrop으로 224×224 추출
    if split == "train":
        return transforms.Compose([
            transforms.RandomHorizontalFlip(),
            transforms.RandomCrop(config.IMG_SIZE, padding=16),
            transforms.ColorJitter(brightness=0.3, contrast=0.3, saturation=0.3),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
    else:
        return transforms.Compose([
            transforms.CenterCrop(config.IMG_SIZE),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])


class FashionEraDataset(Dataset):
    SPLIT_MAP = {
        "train": "Training",
        "val":   "Validation",
        "test":  "Validation",  # 별도 test set 없음, Validation 재사용
    }

    def __init__(self, split, return_path=False):
        self.transform = get_transforms(split)
        self.return_path = return_path
        self.samples = []

        split_dir = config.IMAGE_DIR / self.SPLIT_MAP[split]
        for gender in ["man", "woman"]:
            for era in config.TARGET_ERAS:
                era_dir = split_dir / gender / str(era)
                if not era_dir.exists():
                    continue
                for img_path in sorted(era_dir.glob("*.jpg")):
                    self.samples.append((img_path, config.ERA_TO_IDX[era]))

        print(f"[{split}] {len(self.samples)}장 로드")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        img_path, label = self.samples[idx]
        img = Image.open(img_path).convert("RGB")
        img = self.transform(img)
        if self.return_path:
            return img, label, str(img_path)
        return img, label
