---
tags: [type/concept, tier/all, version/V1, lock/FREEZE]
aliases: [VamosMessage, ResponseEnvelope, IntentFrame]
created: 2026-06-11
---

# VamosMessage Schema (Envelope + IntentFrame)

## 정의
VAMOS 요청-응답의 정본 메시지 스키마. 입력은 **IntentFrame**(I-1 산출), 출력은 **ResponseEnvelope 5필드(LOCK)**. Python `contracts.py`(Pydantic v2)가 SOT이며 TypeScript Zod / Rust serde 타입을 파생 생성한다.

## 값·수치 (LOCK)
- ResponseEnvelope 5필드(LOCK):
  1. `answer{summary, details, next_actions[]}`
  2. `evidence{coverage(0~1), items[], qod(0~1)}`
  3. `self_check{score(0~1), verdict(PASS|WARN|FAIL), reasons[], retry_allowed}`
  4. `decision_ref{decision_id, gates{}}`
  5. `audit{event_ids[], failure_codes[], fallback_ids[]}`
- IntentFrame 주요 필드: intent_id, trace_id, user_goal, task_type, domain_hint(P0|P1|P2), constraints{}, risk_flags{}, ambiguity{clarification_questions 0~3}, confidence(0~1, **<0.5 시 HITL**), sub_intents
- API 응답 규격: `{success, data/error, trace_id}` — trace_id 필수(LOCK)

## 이 개념이 등장하는 모든 도메인
- [[T1-Auxiliary-Modules]] — I-1 Intent Detector(IntentFrame), I-11 Output Composer(Envelope)
- [[T4-Rust-Tauri]] — serde 구조체, JSON-RPC 직렬화
- [[T6-Hologram]] — Envelope 기반 최종 출력 렌더링
- [[T6-Event-Logging]] — audit 필드 소비(trace_id, failure_codes)
- [[T6-Memory-RAG]] — evidence/qod 필드 생성 측

## 버전별 차이
- V1~V3 공통 스키마 — V0 진입 시 D2.1 전체 v3.0.0 통일 승격(CC-001), Python/TS 동기화 도구(CC-007)

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §12 / D2.1 스키마(`D:\VAMOS\docs\sot\` D2.1-D1~D8) / `D:\VAMOS\docs\sot\PHASE_B1_API_CONTRACT.md`
