---
tags: [type/concept, module/COND, status/COND, tier/T2, version/V2]
aliases: [CAT-D, Media 모듈, 미디어 처리 COND]
created: 2026-06-11
---

# COND CAT-D: Media (8개)

## 정의
COND 106개 중 미디어 처리 카테고리. 이미지/오디오/비디오/문서의 변환·생성·검색을 담당하며, `MediaMixin`으로 Blue Node에 미디어 능력을 제공한다. 모듈 ID 범위 #16, #80-#84, #86, #109. 8개 전수 L3(구현 즉시 투입 가능) 승급 완료.

## 모듈 목록 (8)
| ID | 이름 | 핵심 백엔드 |
|---|---|---|
| COND-016 | 멀티미디어 라이브러리 (HUB) | Pillow / OpenCV / FFmpeg |
| COND-080 | 스타일 트랜스퍼 (GPU 필수) | AdaIN / Gatys / CLIP-guided |
| COND-081 | 로고/아이콘 생성 (GPU 필수) | Stable Diffusion + potrace |
| COND-082 | 화자분리 (Diarization) | pyannote + Whisper + ECAPA |
| COND-083 | 양식 자동생성 | Jinja2 + WeasyPrint + docxtpl |
| COND-084 | 크로스모달 검색 | CLIP / BLIP-2 / ImageBind |
| COND-086 | 코드 변환 | Tree-sitter + LLM polish |
| COND-109 | 인포그래픽 생성 | Vega-Lite + CairoSVG + LLM |

## 등장 도메인
- [[T2-COND-Modules]] — 정본 소유 (2-2 COND 카테고리 체계)
- [[T3-Multimodal]] — COND-084 통합 임베딩 공간, COND-082 오디오 파이프라인 교차 참조
- [[T3-Dev-Tools]] — COND-086 Tree-sitter grammar 공유
- [[T2-Blue-Node]] — Content/Creative Node가 주요 소비 (Permission P0~P1 혼합)

## 값·수치 (LOCK 여부)
- LOCK 준수: LOCK-CD-03(BaseModule ABC) / LOCK-CD-04(Runnable) / LOCK-CD-05/06(ErrorHandling + VamosError 4필드) / LOCK-CD-08(NODE 독립 실행 불가) / LOCK-CD-10(ModuleConfig 5필드)
- 의존 관계: CAT-A(ML 추론 — CLIP/Whisper/SD)·CAT-B(VectorStore)·CAT-C(인프라) 소비 — CORE→COND 역방향 import 금지(R7)
- Config Group: `media_config` (ffmpeg_path, max_file_size_mb, supported_formats, gpu_acceleration)

## 원본 경로
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\COND_MODULES_DETAIL_구조화_종합계획서.md` (L67~76)
- `D:\VAMOS\docs\sot 2\2-2_COND-Modules-Detail\04_cat-d-media\_index.md`
