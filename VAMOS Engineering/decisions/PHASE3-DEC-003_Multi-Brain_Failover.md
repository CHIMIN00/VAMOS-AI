# PHASE3-DEC-003 (3-3): Multi-Brain Failover 순서/조건

> **결정일**: 2026-06-12 (P3-1) · **포맷**: A6 · **우선순위**: Must

## 결정
- **Failover 체인 (LOCK 추인)**: ① GPT-4o (주) → ② Claude Sonnet (1차 대체) → ③ 로컬 Ollama (2차 대체)
- **전환 조건**: 연속 **3회 타임아웃** 또는 **HTTP 5xx** 응답
- **전환 시 의무**: trace_id 유지 + Failover 이벤트 LogEvent 기록 + 자동 다운시프트(I-8) 연동(비용/성능 조건 재평가)

## 근거 (정본 라인)
- D2.0-02 §11.1.2 L3887-3891 (S03-ADD-006): "Failover 순서(LOCK): 1) GPT-4o (주) → 2) Claude Sonnet (1차 대체) → 3) 로컬 Ollama (2차 대체)" + "전환 조건: 연속 3회 타임아웃 또는 HTTP 5xx"
- LOCK Registry §2 "Multi-Brain Failover: GPT-4o→Claude→Ollama (3회 타임아웃 시 전환)" — 일치, 재정의 0

## 이유
정본 LOCK 기확정 — 추인. 5xx는 서버측 장애(재시도 무의미 가능성)로 즉시 전환, 타임아웃은 3회 누적으로 일시 지연과 장애를 구분.

## 검토 대안 (기각)
- V1 비용 관점 Ollama 우선 체인 — 기각: 라우팅 정책(저난도→Ollama)은 I-8 다운시프트/모델 선택의 영역이고, Failover는 "선택된 주 Brain의 장애 대체" 체계로 별개. LOCK 재정의 금지.

## 구현 바인딩
- V1-Phase 1 Brain Adapter(D2.0-04)에서 구현. Anthropic 채널 모델 ID는 구현 시점 최신 정본 채택(체인 슬롯 의미는 "Claude 계열 1차 대체"로 고정 — LOCK은 체인/조건이며 특정 모델 버전 핀 아님을 명기).
- Failover 발동은 CostGate 재평가를 트리거(주→대체 전환 시 단가 변동).
