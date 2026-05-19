# 패션 시대 분류 및 코디 추천 프로젝트

고려대학교 딥러닝 과목 팀 프로젝트

## 프로젝트 개요

연도별 패션 이미지를 학습하여 스타일 벡터를 추출하고,
사용자의 옷 이미지를 입력하면 어울리는 코디를 추천하는 시스템입니다.

- **데이터**: AI Hub — 연도별 패션 선호도 파악 및 추천 데이터 (CC BY-SA)
- **클래스**: 1990 / 2000 / 2010 / 2019 (4클래스)
- **이미지 수**: Training 14,438장 / Validation 7,547장

## 모델

| 모델 | Best Val Accuracy |
|------|-------------------|
| CustomCNN (from scratch) | 37.4% |
| ResNet18 (2단계 Transfer Learning) | **44.1%** |

## 실행 방법

```bash
# 1. 학습
python train.py --model resnet18

# 2. 평가
python evaluate.py --model resnet18

# 3. 특징 벡터 추출
python extract_features.py --model resnet18

# 4. 코디 추천
python recommend.py --image 내옷.jpg --model resnet18 --top_k 5
```

## 파일 구조

```
├── config.py              # 경로, 하이퍼파라미터 설정
├── dataset.py             # FashionEraDataset
├── model.py               # CustomCNN, ResNet18
├── train.py               # 학습 루프 (2단계 Transfer Learning)
├── evaluate.py            # 평가 & 혼동 행렬 시각화
├── extract_features.py    # 512-dim 특징 벡터 추출
├── recommend.py           # 코사인 유사도 기반 추천
├── checkpoints/           # 학습된 모델 가중치
├── results/               # 평가 결과 이미지
├── report.md              # 프로젝트 요약 (Notion 호환)
├── report.pdf             # 프로젝트 요약 PDF
└── presentation.pptx      # 발표 자료
```

## 기술 스택

- Python 3.11 / PyTorch 2.5.1
- Apple M4 Pro MPS (Metal Performance Shaders)
- torchvision, PIL, numpy, scikit-learn, seaborn
