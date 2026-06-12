# VAMOS R1 런타임 설계 결정 — runtime_decisions.md

> **확정일**: 2026-06-12 (P3-1 세션) · **스코프**: 로드맵 3-1~3-7c (10개 결정, 전부 Must)
> **위상 (로드맵 L293)**: 본 문서는 기존 정본(D2.0-01~08·PHASE_B1~B7·SOT 2 도메인 정본)의 **결정 요약 + 로드맵 바인딩** 문서다. 기존 정본을 대체하지 않으며, 충돌 시 기존 정본이 우선하고 변경은 LOCK 절차를 따른다.
> **ADR**: decisions/PHASE3-DEC-001~010 (A6 — 각 결정의 이유·대안·근거 전문) · 기존 LOCK 재정의 **0** · 신규 LOCK 등록 3건(LOCK-DECISION-REGISTRY §8)

| # | 결정 | 단일 결론 | 정본 인용 (라인) | ADR |
|---|------|----------|------------------|-----|
| 3-1 | 5-Gate 실행 순서 | **Policy → Approval → Cost → Evidence → SelfCheck** (우회·생략 불가) | D2.0-07 L969·L954 / D2.0-02 §8.1 / Registry §2 | DEC-001 |
| 3-2 | 메모리 L0~L3 | 계층·TTL(L0 세션/L1 90일/L2 무기한/L3 게이트 필수) + 승격: L0→L1 세션종료 자동, L1→L2 재참조3회∨확인∨QoD≥0.7, L2→L3 크로스참조∨명시 + score=access×0.4+recency×0.3+conf×0.3 + 강등: 미참조 기반·pinned 제외·확인 후 + 검색 L0→L3 / B↔L 매핑(B-4/B-1/B-3/B-2) 불변 | D2.0-06 L87-97·L305-348·L416-422 / Registry §5 | DEC-002 |
| 3-3 | Multi-Brain Failover | **GPT-4o → Claude Sonnet → Ollama**, 전환 = 연속 3회 타임아웃 ∨ HTTP 5xx, trace_id 유지+LogEvent+I-8 연동 | D2.0-02 §11.1.2 L3887-3891 / Registry §2 | DEC-003 |
| 3-4 | DAG 상태 전이 | **9-State S0~S8** + S3 후 결론 불변 + S6 FAIL Soft loop 자동 1회만 + 경계 model_validate 의무. **V1 기본 = 자체 경량 프레임워크**, LangGraph는 오케스트레이션 전용 예외(Gate/Decision 우회 금지, §7.3 어댑터 경유) | D2.0-02 §2.2 L313-330·L69 / D2.0-05 L191-198·L217 | DEC-004 |
| 3-5 | CostGate 임계값 | **80% 경고+force_mini / 100% 차단(deny)+승인요청+P2 중지** — 100%는 LOCK(변경 불가), 80%는 OWNER 승인 조정 가능. 절대 한도 V1 ₩40K/₩1.3K(BASE-1.3) | D2.0-07 §4.2 L216·L1635-1636·L2059-2060 / Registry §3 | DEC-005 |
| 3-6 | IPC JSON-RPC + A20 | **JSON-RPC 2.0 over subprocess stdin/stdout (V1)** + 메서드 **13개**(PHASE_B1 §5.2 전수) + **A20: Pydantic v2 단일 정본·serde/TS 자동 생성·직접 수정 금지·왕복 테스트·4파일 동시 커밋** | PHASE_B1 §3.0 L1401·§5.2 L2052-2068 / STRATEGY_06 §2 L41-80 | DEC-006 |
| 3-7 | MCP 통신 계약 | **Streamable HTTP** (DEC-017, stdio 제거) + timeout 10s/10s/15s + **max_retries V1/V2=2·V3=3**(GATE-07d 단일 표기) + 구현 정본 sot2 4-3(LOCK-MCP-01~10) | Registry §1 DEC-017 / PHASE_B4 §3.9 L356-360 / PHASE_B1 §5.3 | DEC-007 |
| 3-7a | 다층 방어 (A21) | **독립 3계층**: L1 config LOCK(정적) / L2 5-Gate 체인(동적·게이트 간 의존성 0) / L3 NEVER_AUTO 10항목 frozenset 하드코딩(RA_NEVER_01~10). ※ PART2 "Security Layer"와 별개 개념 | STRATEGY_05 §3.2 L90-117 / SDAR §5.1 L590-603 / BASE-1.3 7불변 | DEC-008 |
| 3-7b | 투명성 (A22) | **D6 기확정 틀(metadata 내부·top-level 불변) 안에서 스키마 상세 확정**: reasoning_trace(list[GateTraceEntry]) + evidence_sources(list[source/date/relevance]) + confidence_score + disclaimer — D2.1-D5 metadata(object)에 수용, UI는 [왜?] 펼침 | D6(DECISION_REGISTER) / STRATEGY_05 §4.2 L154-169 / D2.1-D5 §4.9 L394 | DEC-009 |
| 3-7c | 예측 신뢰도 (A25) | Decision에 **confidence_score(0~1)+confidence_level 신규 추가**(A20 절차) + 임계값 **0.85/0.60/0.30 LOCK**(config 신규 3키 — 분모 20→23, D13 재정의 아님) + 분기 HIGH/MEDIUM/LOW/**REFUSE**(<0.30 거부) + EvidenceGate insufficient→강제 REFUSE | STRATEGY_05 §5.2 L215-233·§5.3 / 로드맵 3-7c·4-5 / D2.1-D2 부재 실측 | DEC-010 |

## 결정 간 연결 (런타임 흐름)
```
요청 → [9-State S0~S8 (DEC-004)] 위에서
  5-Gate 순서대로 판정 (DEC-001) — 비용은 80/100 (DEC-005)
  Brain 장애 시 Failover 체인 (DEC-003) → CostGate 재평가
  Decision에 confidence 산출 (DEC-010) — insufficient 근거면 REFUSE
  응답은 metadata에 reasoning_trace 등 기록 (DEC-009)
  저장은 L0~L3 승격 규칙 (DEC-002)
  전 과정을 3계층 방어가 감싼다 (DEC-008)
  Python↔Rust는 JSON-RPC 13 + A20 (DEC-006), 도구는 MCP Streamable HTTP (DEC-007)
```

## Phase 3→4 인수인계 바인딩 (로드맵 "Phase 3→4 인수인계" 충족)
- **→ 4-1 (B2c 타입 동기화)**: DEC-006 A20 규칙 + DEC-010 confidence 필드 + DEC-009 metadata 키 4종 — Pydantic 정본에서 시작
- **→ 4-2 (ORANGE CORE)**: DEC-001 게이트 체인(V0 3종+슬롯 예약) + DEC-004 S0~S8 + DEC-008 Layer 2/3 + DEC-010 분기 로직
- **→ 4-3 (프론트엔드)**: DEC-009 [왜?] 버튼 + DEC-010 신뢰도 표시
- **→ 4-5 (config.v1.toml)**: DEC-005 cost 키 + DEC-010 confidence 3키(LOCK 분모 20→23 갱신 집행) + DEC-008 Layer 1
- **→ V1-Phase 1/2/3/6**: DEC-003(Brain Adapter)·DEC-002(전 계층 메모리)·DEC-004(StateGraph/CB)·DEC-007(MCP)

## 회귀·정합 확인 (2026-06-12)
- CLAUDE.md §5(5-Phase·Gate 표·S0~S8)와 모순 0 — §5 Gate 표는 역할 정의표로 순서 주장 아님(DEC-001 비고)
- 발견 이형 1건 처리: STRATEGY_05 §3.1 L85 게이트 순서 표기 오기(Cost↔Approval) → 정본(D2.0-07) 기준 교정 완료(Engineering 문서)
- P3-0 게이트 결정 수용: GATE-07d(MCP max_retries)·GATE-02 #10(일반 API 재시도와 MCP 분리)·D6·D13 전건 정합
