"""VAMOS Verifier/Reasoning Engines (1-1 도메인) — V1 CORE 6-3 결정론 인터페이스 계층.

정본: D2.0-01 §5.11 (C-Series Verifier) + §5.12 (D-Series Brain/Planner) +
docs/sot 2/1-1_Verifier-Reasoning-Engines (00_common BaseVerifier/BaseReasoningEngine,
01_logic/02_math/03_code/04_think-engine/05_multimodal-engine 상세명세).

본 패키지(C-1/C-2/C-3 + D-1/D-2)는 6-3 범위 = 인터페이스 + 결정론 검증/판정 + 6-4 위임 stub.
실 LLM 추론·Z3 solver(E-6)·Docker 샌드박스(E-4)·CLIP/Whisper/OCR = 6-4 (defer 마킹).
결과 타입은 모듈 내부 dataclass — 잠긴 contracts.py 25 분모 무변경(A20). 에스컬레이션은
should_escalate() 결정론 노출(실 I-20 라우팅은 호출측/파이프라인 — R-01-8). 본 패키지는 순수
계산(미등록 이벤트 발행 금지 — 로깅은 파이프라인/I-6 계층에서 registries 정본 이벤트로 수행).
"""
