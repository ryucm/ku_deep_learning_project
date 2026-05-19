from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

OUTPUT = os.path.join(os.path.dirname(__file__), "report.pdf")

# 한글 폰트 등록
pdfmetrics.registerFont(TTFont("Korean",      "/Users/changmin/Library/Fonts/NanumGothic-Regular.ttf"))
pdfmetrics.registerFont(TTFont("Korean-Bold", "/Users/changmin/Library/Fonts/NanumGothic-Bold.ttf"))

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=2.5*cm, rightMargin=2.5*cm,
    topMargin=2.5*cm, bottomMargin=2.5*cm
)

styles = getSampleStyleSheet()
KO       = ParagraphStyle("KO",       fontName="Korean",      fontSize=10, leading=18)
KO_BOLD  = ParagraphStyle("KO_BOLD",  fontName="Korean-Bold", fontSize=10, leading=18)
TITLE    = ParagraphStyle("TITLE",    fontName="Korean-Bold", fontSize=18, leading=26, spaceAfter=6)
H1       = ParagraphStyle("H1",       fontName="Korean-Bold", fontSize=13, leading=20, spaceBefore=16, spaceAfter=6, textColor=colors.HexColor("#1a1a2e"))
H2       = ParagraphStyle("H2",       fontName="Korean-Bold", fontSize=11, leading=18, spaceBefore=10, spaceAfter=4, textColor=colors.HexColor("#16213e"))
CODE     = ParagraphStyle("CODE",     fontName="Courier",     fontSize=8.5, leading=14, backColor=colors.HexColor("#f4f4f4"), leftIndent=12, borderPad=6)
CAPTION  = ParagraphStyle("CAPTION",  fontName="Korean",      fontSize=9,  leading=14, textColor=colors.grey)

def tbl(data, col_widths, header_bg=colors.HexColor("#16213e")):
    t = Table(data, colWidths=col_widths)
    style = [
        ("BACKGROUND", (0,0), (-1,0), header_bg),
        ("TEXTCOLOR",  (0,0), (-1,0), colors.white),
        ("FONTNAME",   (0,0), (-1,0), "Korean-Bold"),
        ("FONTNAME",   (0,1), (-1,-1), "Korean"),
        ("FONTSIZE",   (0,0), (-1,-1), 9),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#f8f8f8")]),
        ("GRID",       (0,0), (-1,-1), 0.5, colors.HexColor("#cccccc")),
        ("ALIGN",      (0,0), (-1,-1), "LEFT"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("TOPPADDING", (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
    ]
    t.setStyle(TableStyle(style))
    return t

story = []

# ── 제목 ──────────────────────────────────────────────────
story.append(Paragraph("패션 시대 분류 및 코디 추천 프로젝트", TITLE))
story.append(Paragraph("Fashion Era Classification & Outfit Recommendation", CAPTION))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#16213e"), spaceAfter=16))

# ── 1. 데이터 ─────────────────────────────────────────────
story.append(Paragraph("1. 데이터의 종류 및 특성", H1))
story.append(Paragraph("출처: AI Hub — 연도별 패션 선호도 파악 및 추천 데이터 (CC BY-SA)", KO))
story.append(Spacer(1, 8))

data1 = [
    ["항목", "내용"],
    ["이미지 수", "Training 14,438장 / Validation 7,547장"],
    ["원본 해상도", "3000×4000px (패션 전신 사진)"],
    ["레이블", "촬영 연도 4클래스 (1990 / 2000 / 2010 / 2019)"],
    ["성별", "남성 / 여성"],
    ["부가 정보", "스타일명 27종, 사용자 설문 응답"],
]
data1 = [[Paragraph(c, KO_BOLD if r==0 else KO) for c in row] for r, row in enumerate(data1)]
story.append(tbl(data1, [4*cm, 12*cm]))
story.append(Spacer(1, 8))
story.append(Paragraph("인접 연도(2010 ↔ 2019)는 시각적 차이가 작아 분류 난이도가 높으며, 원본 이미지가 커서 학습 전 256×256으로 사전 리사이즈 처리.", KO))

# ── 2. 모델 선택 ──────────────────────────────────────────
story.append(Paragraph("2. 데이터에 따른 모델 선택 이유", H1))
story.append(Paragraph("패션 스타일은 색감, 실루엣, 텍스처 같은 공간적 패턴으로 구분된다. 이미지의 지역 특징을 추출하는 CNN이 적합하며, 시간 순서가 중요한 태스크가 아니므로 RNN은 불필요하다.", KO))
story.append(Spacer(1, 8))

data2 = [
    ["", "CustomCNN", "ResNet18"],
    ["구조", "Conv 블록 4개 직접 설계", "ImageNet 사전학습 모델"],
    ["특징 벡터", "512-dim", "512-dim"],
    ["학습 방식", "From scratch", "Transfer Learning"],
    ["목적", "구조 이해", "성능 향상"],
]
data2 = [[Paragraph(c, KO_BOLD if r==0 else KO) for c in row] for r, row in enumerate(data2)]
story.append(tbl(data2, [3.5*cm, 6.5*cm, 6*cm]))

# ── 3. 학습 방법 ──────────────────────────────────────────
story.append(Paragraph("3. 모델 학습 방법", H1))
story.append(Paragraph("CustomCNN — From Scratch", H2))
story.append(Paragraph("ConvBlock(Conv+BN+ReLU+MaxPool) × 4 → AdaptiveAvgPool → FC(512) → Dropout → FC(4)", CODE))
story.append(Spacer(1, 6))
story.append(Paragraph("Loss: CrossEntropy (Label Smoothing 0.1)  |  Optimizer: Adam (lr=1e-3, weight decay=1e-4)  |  Early Stopping: patience=10", KO))

story.append(Paragraph("ResNet18 — 2단계 Transfer Learning", H2))
data3 = [
    ["단계", "설명", "학습률"],
    ["Stage 1 (5 epoch)", "backbone 완전 동결 → head(FC)만 학습", "head: 1e-3"],
    ["Stage 2 (25 epoch)", "전체 fine-tuning (차등 학습률)", "backbone: 1e-4 / head: 1e-3"],
]
data3 = [[Paragraph(c, KO_BOLD if r==0 else KO) for c in row] for r, row in enumerate(data3)]
story.append(tbl(data3, [4*cm, 9*cm, 4*cm]))

# ── 4. 실험 결과 ──────────────────────────────────────────
story.append(Paragraph("4. 실험 결과", H1))
story.append(Paragraph("랜덤 기준선 (4클래스): 25%", CAPTION))
story.append(Spacer(1, 4))
data4 = [
    ["모델", "Best Val Accuracy", "비고"],
    ["CustomCNN", "37.4%", "Epoch 9 최고, 이후 과적합"],
    ["ResNet18 (기본)", "42.5%", "Train 93% vs Val 42% — 심각한 과적합"],
    ["ResNet18 (2단계)", "측정 중", "차등 학습률 + Label Smoothing 적용"],
]
data4 = [[Paragraph(c, KO_BOLD if r==0 else KO) for c in row] for r, row in enumerate(data4)]
story.append(tbl(data4, [4*cm, 4.5*cm, 7.5*cm]))

# ── 5. 최종 Output ────────────────────────────────────────
story.append(Paragraph("5. 최종 Output", H1))
story.append(Paragraph("1차 Output — 시대 분류 모델", H2))
story.append(Paragraph("입력: 패션 이미지  →  출력: 1990 / 2000 / 2010 / 2019 분류", CODE))

story.append(Paragraph("2차 Output — 스타일 추천 시스템", H2))
story.append(Paragraph(
    "입력: 사용자 옷 이미지 1장  →  CNN encode() → 512-dim 벡터 추출  →  데이터셋 전체와 코사인 유사도 계산  →  Top-K 코디 추천", CODE))
story.append(Spacer(1, 8))
story.append(Paragraph("python recommend.py --image 내옷.jpg --model resnet18 --top_k 5", CODE))

# ── 6. 기술 스택 ──────────────────────────────────────────
story.append(Paragraph("6. 기술 스택", H1))
data5 = [
    ["항목", "내용"],
    ["언어", "Python 3.11"],
    ["프레임워크", "PyTorch 2.5.1 / torchvision 0.20.1"],
    ["가속기", "Apple M4 Pro MPS (Metal Performance Shaders)"],
    ["주요 라이브러리", "PIL, numpy, scikit-learn, seaborn"],
    ["데이터 출처", "AI Hub (CC BY-SA)"],
]
data5 = [[Paragraph(c, KO_BOLD if r==0 else KO) for c in row] for r, row in enumerate(data5)]
story.append(tbl(data5, [4*cm, 12*cm]))

doc.build(story)
print(f"PDF 생성 완료: {OUTPUT}")
