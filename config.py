from pathlib import Path

DATA_ROOT = Path.home() / "Desktop/대학원/딥러닝/010.연도별 패션 선호도 파악 및 추천 데이터"
IMAGE_DIR = Path(__file__).parent / "data_resized"  # 미리 256×256 리사이즈된 이미지

TARGET_ERAS = [1990, 2000, 2010, 2019]
ERA_TO_IDX = {era: idx for idx, era in enumerate(TARGET_ERAS)}
IDX_TO_ERA = {idx: era for era, idx in ERA_TO_IDX.items()}
NUM_CLASSES = len(TARGET_ERAS)

IMG_SIZE = 224
BATCH_SIZE = 32
NUM_EPOCHS = 30
LR = 1e-3
NUM_WORKERS = 4

CHECKPOINT_DIR = Path(__file__).parent / "checkpoints"
CHECKPOINT_DIR.mkdir(exist_ok=True)

FEATURE_DIR = Path(__file__).parent / "features"
FEATURE_DIR.mkdir(exist_ok=True)
FEATURE_NPY  = FEATURE_DIR / "features.npy"   # (N, 512) 벡터 배열
FEATURE_META = FEATURE_DIR / "metadata.json"  # 이미지 경로 + era 인덱스
