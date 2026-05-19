import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim.lr_scheduler import CosineAnnealingLR
import argparse
import config
from dataset import FashionEraDataset
from model import CustomCNN, ResNet18

STAGE1_EPOCHS = 5   # backbone 동결, head만 학습
STAGE2_EPOCHS = 25  # 전체 fine-tuning


def train_epoch(model, loader, criterion, optimizer, device):
    model.train()
    total_loss, correct = 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        optimizer.zero_grad()
        out = model(imgs)
        loss = criterion(out, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(labels)
        correct += (out.argmax(1) == labels).sum().item()
    n = len(loader.dataset)
    return total_loss / n, correct / n


@torch.no_grad()
def validate(model, loader, criterion, device):
    model.eval()
    total_loss, correct = 0, 0
    for imgs, labels in loader:
        imgs, labels = imgs.to(device), labels.to(device)
        out = model(imgs)
        loss = criterion(out, labels)
        total_loss += loss.item() * len(labels)
        correct += (out.argmax(1) == labels).sum().item()
    n = len(loader.dataset)
    return total_loss / n, correct / n


def run_loop(model, train_loader, val_loader, criterion, optimizer, scheduler,
             device, num_epochs, model_type, best_val_acc, patience_limit=10):
    patience = 0
    for epoch in range(1, num_epochs + 1):
        train_loss, train_acc = train_epoch(model, train_loader, criterion, optimizer, device)
        val_loss, val_acc     = validate(model, val_loader, criterion, device)
        scheduler.step()

        print(f"  Epoch {epoch:02d}/{num_epochs} | "
              f"Train Loss: {train_loss:.4f}  Acc: {train_acc:.4f} | "
              f"Val Loss: {val_loss:.4f}  Acc: {val_acc:.4f}")

        if val_acc > best_val_acc:
            best_val_acc = val_acc
            ckpt_path = config.CHECKPOINT_DIR / f"best_{model_type}.pth"
            torch.save(model.state_dict(), ckpt_path)
            print(f"    → 체크포인트 저장 (Val Acc: {best_val_acc:.4f})")
            patience = 0
        else:
            patience += 1
            if patience >= patience_limit:
                print(f"  Early stopping (epoch {epoch})")
                break

    return best_val_acc


def main(model_type):
    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    print(f"Device: {device} | Model: {model_type}")

    train_ds = FashionEraDataset("train")
    val_ds   = FashionEraDataset("val")
    train_loader = DataLoader(train_ds, batch_size=config.BATCH_SIZE, shuffle=True,  num_workers=config.NUM_WORKERS)
    val_loader   = DataLoader(val_ds,   batch_size=config.BATCH_SIZE, shuffle=False, num_workers=config.NUM_WORKERS)

    model = CustomCNN() if model_type == "custom" else ResNet18()
    model = model.to(device)

    # label smoothing: 정답 레이블에 100% 확신하지 않도록 → 과적합 완화
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)

    best_val_acc = 0.0

    if model_type == "resnet18":
        # ── Stage 1: backbone 동결, head만 학습 ──────────────────────────
        print(f"\n=== Stage 1: backbone 동결, head만 학습 ({STAGE1_EPOCHS} epoch) ===")
        for param in model.backbone.parameters():
            param.requires_grad = False

        optimizer = torch.optim.Adam(
            model.head.parameters(), lr=1e-3, weight_decay=1e-4
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=STAGE1_EPOCHS)
        best_val_acc = run_loop(
            model, train_loader, val_loader, criterion, optimizer, scheduler,
            device, STAGE1_EPOCHS, model_type, best_val_acc, patience_limit=STAGE1_EPOCHS
        )

        # ── Stage 2: 전체 fine-tuning (차등 학습률) ───────────────────────
        print(f"\n=== Stage 2: 전체 fine-tuning ({STAGE2_EPOCHS} epoch) ===")
        for param in model.backbone.parameters():
            param.requires_grad = True

        optimizer = torch.optim.Adam([
            {'params': model.backbone.parameters(), 'lr': 1e-4},  # backbone: 낮은 lr
            {'params': model.head.parameters(),     'lr': 1e-3},  # head: 높은 lr
        ], weight_decay=1e-4)
        scheduler = CosineAnnealingLR(optimizer, T_max=STAGE2_EPOCHS)
        best_val_acc = run_loop(
            model, train_loader, val_loader, criterion, optimizer, scheduler,
            device, STAGE2_EPOCHS, model_type, best_val_acc, patience_limit=10
        )

    else:
        # CustomCNN: 사전학습 없으므로 단일 단계
        print(f"\n=== 학습 시작 ({config.NUM_EPOCHS} epoch) ===")
        optimizer = torch.optim.Adam(
            model.parameters(), lr=config.LR, weight_decay=1e-4
        )
        scheduler = CosineAnnealingLR(optimizer, T_max=config.NUM_EPOCHS)
        best_val_acc = run_loop(
            model, train_loader, val_loader, criterion, optimizer, scheduler,
            device, config.NUM_EPOCHS, model_type, best_val_acc, patience_limit=10
        )

    print(f"\n최종 Best Val Acc: {best_val_acc:.4f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", choices=["custom", "resnet18"], default="custom")
    args = parser.parse_args()
    main(args.model)
