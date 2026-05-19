"""
학습된 CNN으로 데이터셋 전체 이미지를 512-dim 벡터로 변환하여 저장.
추천 시스템의 인덱스 역할.

실행: python extract_features.py --model custom
"""
import torch
import numpy as np
import json
from torch.utils.data import DataLoader
import argparse
import config
from dataset import FashionEraDataset
from model import CustomCNN, ResNet18


@torch.no_grad()
def extract_all(model, device):
    all_feats, all_paths, all_eras = [], [], []

    for split in ["train", "val", "test"]:
        ds = FashionEraDataset(split, return_path=True)
        loader = DataLoader(ds, batch_size=64, shuffle=False, num_workers=config.NUM_WORKERS)

        model.eval()
        for imgs, labels, paths in loader:
            feats = model.encode(imgs.to(device)).cpu().numpy()
            all_feats.append(feats)
            all_paths.extend(paths)
            all_eras.extend(labels.tolist())

    return np.vstack(all_feats), all_paths, all_eras


def main(model_type):
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")

    model = CustomCNN() if model_type == "custom" else ResNet18(pretrained=False)
    ckpt_path = config.CHECKPOINT_DIR / f"best_{model_type}.pth"
    model.load_state_dict(torch.load(ckpt_path, map_location=device))
    model = model.to(device)
    print(f"체크포인트 로드: {ckpt_path}")

    features, paths, eras = extract_all(model, device)
    print(f"추출 완료: {features.shape[0]}개 이미지, {features.shape[1]}-dim 벡터")

    np.save(config.FEATURE_NPY, features)
    with open(config.FEATURE_META, "w") as f:
        json.dump({"paths": paths, "eras": eras}, f)

    print(f"저장 완료: {config.FEATURE_NPY}, {config.FEATURE_META}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["custom", "resnet18"], default="custom")
    args = parser.parse_args()
    main(args.model)
