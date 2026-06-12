# VAMOS 런타임 엔지니어링 계획서 — runtime_eng_plan.md (3-12)

> **확정일**: 2026-06-12 (P3-2) · **우선순위**: Should · **매트릭스 셀**: R2a/R2b/R2c → R3 → RF
> **입력**: R1 10개 결정(runtime_decisions.md + PHASE3-DEC-001~010) · **위상**: 결정 요약 + 로드맵 바인딩, 정본 무대체

## 1. R1 10결정 → R2 구현 셀 매핑

| R1 결정 (ADR) | R2a 코어 | R2b 도메인 | R2c 프론트 | config(4-5) |
|---------------|----------|-----------|-----------|-------------|
| DEC-001 5-Gate 순서 | ● 5-Gate 체인(V0 3종+슬롯) | | | |
| DEC-002 메모리 L0~L3 | ● L0~L3 + 승격/강등 | | | TTL 키 |
| DEC-003 Failover | | ● Multi-Brain Adapter(A-1) | | brain 체인 |
| DEC-004 DAG S0~S8 | ● 5-Phase Pipeline + 상태머신 | ● LangGraph DAG(어댑터) | | |
| DEC-005 CostGate | ● CostGate 80/100 | | ● 비용 HUD | cost.*_limit |
| DEC-006 IPC+A20 | ● Registry | | ● Rust IPC 바인딩 | |
| DEC-007 MCP | | ● MCP Bridge/Server/Client | | mcp.* |
| DEC-008 A21 3계층 | ● Layer 1/2/3 | | | LOCK 키 |
| DEC-009 A22 metadata | ● reasoning_trace 필드 | | ● [왜?] 버튼 | |
| DEC-010 A25 confidence | ● confidence 산출+분기 | | ● 신뢰도 표시 | confidence 3키 |

## 2. R2a: 코어 런타임 구현 (Must)
- **입력**: R1 LOCK 항목 + B1 환경(Phase 2 린터/테스트) + D2.1 스키마
- **V0 스코프**: ORANGE CORE **활성 5(I-1/2/3/5/19)+stub 3(I-8/9/20) = 8 파일**(PHASE3-GATE-03 — 전 25 선생성 안 함) + 5-Phase Pipeline + Gate 3종(Policy/Cost/Approval, 5-Gate 완성은 V1) + L0 메모리 + Registry + config 로드 + Defense Layer 1/3(정적·하드코딩이라 V0부터 완전체) + reasoning_trace(Gate 3종+SKIP) + confidence_score
- **V1 스코프**: **CORE 32 활성**(PHASE3-GATE-03 — PART2 §1.1; 매트릭스 "26"은 구집계) + 5-Gate 완성 + 전 계층 메모리 + 전 Defense Layer
- **완료조건**: V0 스캐폴드 13항목(PART2 V0 완료 체크) / V1 E2E 파이프라인 동작
- **자동화**: AI 코드 생성(B2a 하네스 통과 후) + 수동 리뷰 · **출력**: backend/orange_core/ + tests/

## 3. R2b: 도메인 실행 구현 (Must)
- **입력**: R2a 코어 + R1 에이전트 오케스트레이션(DEC-003/004) + SOT 2 도메인 사양
- **프로세스**: BLUE NODE(V0: Dev/Research/Productivity 스켈레톤, 명칭 D2.0-03) + LangGraph DAG(어댑터 경유, DEC-004) + RAG(BGE-M3→Chroma) + Multi-Brain Adapter(DEC-003) + COND 조건부 활성화 + A2A
- **완료조건**: V0 BLUE NODE 3 스켈레톤 동작 / V1 에이전트 3개 + RAG 기본 검색
- **순차**: R2a 위에서 동작 · **병렬**: ↔ R2c(API 인터페이스 합의 후)

## 4. R2c: 프론트엔드 구현 (Should)
- **입력**: R1 IPC(DEC-006) + B2c 타입 동기화(TS interface) + D2.0-08 UI/UX
- **프로세스**: Tauri 2.0 셸 + React 18 + Rust IPC 바인딩(invoke) + **[왜?] 버튼(DEC-009)** + **신뢰도 표시(DEC-010)** + 면책(A16)
- **완료조건**: V0 Tauri 기동+기본 입출력 / V1 입력→응답 E2E · **병렬**: ↔ R2a(IPC 계약만 공유)

## 5. R3: 운영/모니터링 (Phase 6)
- Agent Dog 모니터링(V1: SQLite 메트릭+JSONL / V2: Langfuse+Phoenix+Grafana) + 비용 추적(월 예산 소진율, DEC-005) + 용량 상한 실측(C.2 #9, D11 → 6-6)

## 6. RF: 역류 (실패 시 피드백 — A1)
- 운영(R3)/검증(Phase 5)에서 R1 설계 결함 발견 → **R1 수정**(SOT 정본 우선). SOT 자체 모순 → DF 역류 → D1 부분 재실행. 이벤트 기반(상시 행 아님).
- 트리거 예: confidence 임계값(0.85/0.60/0.30) 운영 부적합 → Approval Gate 승인 후 조정(LOCK 변경 절차)

## 7. 의존 순서
```
R1(완료) → R2a(Must,선행) → R2b(순차) ‖ R2c(병렬, IPC 계약 공유)
         → R3(운영) → RF(역류 시 R1로)
```

## 정본 인용
runtime_decisions.md + PHASE3-DEC-001~010 · STRATEGY_08 §4.3 R2a/R2b/R2c/R3 셀(L542-683) · PHASE3-GATE-03(분모) · 로드맵 Phase 4(4-1~4-7)/Phase 6
