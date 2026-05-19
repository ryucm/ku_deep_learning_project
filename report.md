# 패션 시대 분류 및 코디 추천 프로젝트

---

## 1. 데이터의 종류 및 특성

**출처**: AI Hub — 연도별 패션 선호도 파악 및 추천 데이터

| 항목 | 내용 |
|------|------|
| 이미지 수 | Training 14,438장 / Validation 7,547장 |
| 원본 해상도 | 3000×4000px (패션 전신 사진) |
| 레이블 | 촬영 연도 (1990 / 2000 / 2010 / 2019) — 4클래스 |
| 성별 | 남성 / 여성 |
| 부가 정보 | 스타일명 27종 (normcore, hiphop, hippie 등), 사용자 설문 응답 |

**데이터 특성**

- 단순 카테고리(상의/하의)가 아닌 **시대별 스타일 변화**를 담은 데이터
- 인접 연도(2010 ↔ 2019)는 시각적 차이가 작아 분류 난이도 높음
- 원본 이미지가 3000×4000px으로 매우 커서 학습 전 256×256으로 사전 리사이즈 처리

---

## 2. 데이터에 따른 모델 선택 이유

**CNN 선택 이유**

패션 스타일은 색감, 실루엣, 텍스처 같은 **공간적 패턴**으로 구분된다. 이미지의 지역 특징을 추출하는 CNN이 적합하며, 시간 순서가 중요한 태스크가 아니므로 RNN은 불필요하다.

**두 가지 모델 비교**

| | CustomCNN | ResNet18 |
|--|-----------|----------|
| 구조 | Conv 블록 4개 직접 설계 | ImageNet 사전학습 모델 |
| 특징 벡터 | 512-dim | 512-dim |
| 학습 방식 | 처음부터 학습 (from scratch) | Transfer Learning |
| 목적 | 구조 이해 | 성능 향상 |

---

## 3. 모델 학습 방법

### CustomCNN

```
이미지 (3×224×224)
  → ConvBlock × 4 (Conv + BatchNorm + ReLU + MaxPool)
  → AdaptiveAvgPool → Flatten
  → Linear(256→512) → ReLU → Dropout(0.5)
  → Linear(512→4) → 클래스 확률
```

- Loss: CrossEntropy (Label Smoothing 0.1)
- Optimizer: Adam (lr=1e-3, weight decay=1e-4)
- Scheduler: CosineAnnealingLR
- Early Stopping: patience=10

### ResNet18 — 2단계 Transfer Learning

**Stage 1 (5 epoch): backbone 동결, head만 학습**
- ImageNet 사전학습 가중치 보호
- FC 레이어만 업데이트 → 분류기 초기화

**Stage 2 (25 epoch): 전체 fine-tuning (차등 학습률)**
- backbone lr = 1e-4 (미세 조정)
- head lr = 1e-3 (적극 학습)
- 사전학습 정보 유지하며 패션 도메인에 적응

---

## 4. 실험 결과

| 모델 | Best Val Accuracy | 비고 |
|------|-------------------|------|
| CustomCNN | 37.4% | Epoch 9에서 최고, 이후 과적합 |
| ResNet18 (1단계) | 42.5% | 과적합 심각 (Train 93% vs Val 42%) |
| ResNet18 (2단계 학습) | 측정 중 | - |

**랜덤 기준선 (4클래스)**: 25%

---

## 5. 최종 Output

### 1차 Output — 시대 분류 모델

```
입력: 패션 이미지
출력: 1990 / 2000 / 2010 / 2019 중 하나
```

### 2차 Output — 스타일 추천 시스템

```
입력:  사용자의 옷 이미지 1장
처리:  CNN encode() → 512-dim 스타일 벡터 추출
       → 데이터셋 전체와 코사인 유사도 계산
출력:  가장 어울리는 코디 이미지 Top-K 추천
```

**실행 방법**

```bash
# 1. 학습
python train.py --model resnet18

# 2. 특징 벡터 인덱스 구축
python extract_features.py --model resnet18

# 3. 추천 실행
python recommend.py --image 내옷.jpg --model resnet18 --top_k 5
```

---

## 6. 기술 스택

| 항목 | 내용 |
|------|------|
| 언어 | Python 3.11 |
| 프레임워크 | PyTorch 2.5.1 |
| 가속기 | Apple M4 Pro MPS |
| 주요 라이브러리 | torchvision, PIL, numpy, scikit-learn, seaborn |
| 데이터 출처 | AI Hub (CC BY-SA) |
