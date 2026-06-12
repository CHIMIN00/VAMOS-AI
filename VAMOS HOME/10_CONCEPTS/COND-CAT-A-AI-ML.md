---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-A, AI/ML Engine COND, AIMLMixin]
created: 2026-06-12
---

# COND CAT-A: AI/ML Engine (13개)

## 정의
COND 106개 중 AI/ML 엔진 카테고리 13개. `AIMLMixin`으로 Blue Node에 ML 추론·학습 능력을 제공한다. 모듈 ID 범위 **#11-#15, #25-#26, #85, #102-#106**. 주요 의존성: PyTorch, ONNX, HuggingFace.

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T2-Blue-Node]] — Blue Node가 Mixin 경유로 소비
- [[T4-MLOps]] — 모델 운영/서빙(4-4) 인프라 연계
- [[COND-CAT-D-Media]] — CAT-D가 CAT-A의 ML 추론(CLIP/Whisper/SD) 소비

## 값·수치 (LOCK 여부)
- COND 합산 (CLAUDE.md §6 정본): 13+13+53+8+7+8+4 = **106** / 총 모듈 81 Named + 106 COND = 187
- 실행 모델: COND는 CORE 소비만 가능 — CORE→COND 역방향 import 금지 (R7, vamos_lint VL-003)
- ※ SOT 2 2-2 분류 체계(COND 106)는 D2.0-01 카탈로그의 status=COND 모듈(I-7 등 7개)과 별개 — 혼동 금지

## 버전별 차이
- COND는 조건부 실행 — 버전 게이트는 모듈별 Mixed (활성 조건은 2-2 종합명세 정본)

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_종합명세.md` (106개 I/O 스키마) / CAT-A_AI-ML-Engine\ 하위
