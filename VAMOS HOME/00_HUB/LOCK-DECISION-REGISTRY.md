---
tags: [type/hub, lock/ABSOLUTE]
aliases: [LOCK Registry, 락 레지스트리]
description: "VAMOS 469+ LOCK 항목 전체 인덱스 — DEC + 도메인별 LOCK 네임스페이스"
---

# LOCK Decision Registry

## 개요

- **총 LOCK 항목**: 469개 검증 완료 (484개 포함 DEFINED-HERE)
- **TRUE MISMATCH**: 0건
- **네임스페이스**: 28개
- **검증 상태**: Phase 11 ALL-A VERIFIED

## 문서 위계 (ABSOLUTE — DEC-001)

```
RULE 1.3 (절대규칙)
  > PLAN 3.0 (상위원칙)
    > DESIGN 2.0 LOCK
      > DESIGN 본문 (01~08)
        > 스키마/TECH_STACK (D1~D8, A1)
```

**충돌 시**: 상위 번호가 하위를 override
**삭제 금지**: DEPRECATE만 허용, 없는 내용 창작 금지

---

## 1. 아키텍처 LOCK (DEC 시리즈)

| ID | LOCK 내용 | 출처 |
|---|---|---|
| DEC-001 | 문서 우선순위: RULE > PLAN > DESIGN LOCK > 본문 > 스키마 | BASE-1.3 |
| DEC-002 | LangChain import 금지 (Allowlist: langchain-core/community/openai만) | PLAN-3.0 |
| DEC-003 | 도구 승인: 읽기전용=자동, 외부API/쓰기/코드실행=확인 | D2.0-07 |
| DEC-004 | GraphRAG: V1=64%+, V2=Hybrid+Rerank 83%+, V3=Self-RAG+Graph 90%+ | PLAN-3.0 |
| DEC-005 | Embedding: V1=BGE-M3(1024dim)/text-embedding-3-small | PLAN-3.0 |
| DEC-010 | QoD 스케일: 0.0~1.0 | PLAN-3.0 |
| DEC-011 | P2 재확인: 모달 | D2.0-08 |
| DEC-014 | QoD 가중치(RAG): relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20 | PLAN-3.0 |
| DEC-015 | 비용 경고 색상: 80%=#FBBF24(노란), 100%=#EF4444(빨간) | D2.0-08 |
| DEC-017 | MCP 전송: Streamable HTTP | D2.0-04 |

## 2. 핵심 엔진 LOCK

| 항목 | LOCK 내용 |
|---|---|
| Decision Lock | 한 시점/한 컨텍스트/한 결론 → locked=true (S3 이후 변경불가) |
| Gate 우회 불가 | Policy→Approval→Cost→Evidence→SelfCheck 필수 통과 |
| Self-check 임계값 | P0:70, P1:75, P2:80 |
| Self-check 루프 | Soft loop 자동 1회만, 이후 승인 필요 |
| 동시성 | MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5 |
| Multi-Brain Failover | GPT-4o→Claude→Ollama (3회 타임아웃 시 전환) |
| 대화 턴 상한 | P0=5, P1=10, P2=20 |

## 3. 비용/안전 LOCK (ABSOLUTE)

| 항목 | V1 | V2 | V3 |
|---|---|---|---|
| 월 상한 | ₩40,000 | ₩93,000 | ₩266,000 |
| 일 상한 | ₩1,300 | ₩3,100 | ₩8,900 |
| Downshift | 80% warn → 100% block | 동일 | 동일 |
| RBAC | OWNER(L3,P2) / ADMIN(L2,P2) / OPERATOR(L1) / VIEWER(L0) | | |
| Autonomy 기본 | L1 (SUPERVISED) | | |
| P2 자동 OFF | 세션 종료 시 즉시 OFF | | |

## 4. Self-evo LOCK

| 항목 | 내용 |
|---|---|
| 원칙 | 제안만 가능, 자동 적용 절대 금지 |
| 허용 6개 | 프롬프트 / 도구 조합 / 메모리 관리 / 출력 포맷 / 워크플로우 순서 / 모델 선택 |
| 불변 7개 | 정체성 / Non-goal / 법규윤리 / 비용상한 / 승인구조 / P0도메인 / P2생성활성화 |
| 롤백 잠금 | 동일 제안 롤백 후 14일 재적용 금지 |

## 5. 데이터/인프라 LOCK

| 항목 | 내용 |
|---|---|
| Semantic Cache | cosine ≥ 0.95 |
| Vector DB | V1=Chroma, V2+=Qdrant |
| RAG Pipeline | 6단계: Collect→Chunk(300~500tok)→Embed→Store→Retrieve→Generate |
| 병렬 실행 상한 | 3 (LOCK) |
| 설정 우선순위 | ENV > config.toml > default |
| 로깅 | JSON Structured (평문 금지, trace_id 필수) |
| B↔L 매핑 | B-4→L0, B-1→L1, B-3→L2, B-2→L3 (변경불가) |

## 6. UI/UX LOCK

| 항목 | 내용 |
|---|---|
| 프레임워크 | Tauri 2.0 + React 18 (V2: +PWA) |
| 2-View | Builder(개발/관리) + Hologram(사용자 대화) |
| 3-Panel | Left(Nav/Timeline) + Center(Canvas/Stream) + Right(Control/HUD) |
| ORANGE 색상 | #F97316, BLUE NODE: #00F6FF |

## 7. 도메인별 LOCK 네임스페이스 (28개)

| 네임스페이스 | 도메인 | 항목 수 |
|---|---|---|
| LOCK-GOV | 0-0 Governance | 15 |
| LOCK-VR | 1-1 Verifier | 15 |
| LOCK-AUX | 1-2 Auxiliary | ~12 |
| LOCK-BN | 2-1 Blue-Node | 19 |
| LOCK-COND | 2-2 COND | 11 |
| LOCK-MM | 3-2 Multimodal | ~10 |
| LOCK-PKM | 3-3 PKM | 12 |
| LOCK-WF | 3-4 Workflow | 10 |
| LOCK-EDU | 3-5 Education | ~10 |
| LOCK-HW | 3-6 Health/Wellness | ~10 |
| LOCK-DT | 3-7 Dev-Tools | ~10 |
| LOCK-A2A | 3-8 A2A | 10 |
| LOCK-BM | 3-9 Business | 10 |
| LOCK-AP | 3-10 Agent-Protocol | 10 |
| LOCK-RT | 4-1 Rust-Tauri | 15 |
| LOCK-CI | 4-2 CI/CD | 12 |
| LOCK-MCP | 4-3 MCP | 10 |
| LOCK-ML | 4-4 MLOps | ~10 |
| LOCK-BE | 5-1 Benchmark | 15 |
| LOCK-FC | 5-2 File-Context | ~8 |
| LOCK-AT | 6-3 Agent-Teams | 17 |
| LOCK-MR | 6-4 Memory-RAG | 19 |
| LOCK-SD | 6-5 SDAR | 20 |
| LOCK-SE | 6-6 Self-Evolution | ~10 |
| LOCK-BA | 6-9 Brain-Adapter | 15 |
| LOCK-EL | 6-12 Event-Logging | ~8 |
| LOCK-AINV | Ai-investing | ~15 |
| 기타 | v12/v23 확장 | ~20 |

**상세**: 각 도메인 노트의 "LOCK 항목" 섹션 참조

## 8. Phase 3 R1 신규 LOCK (2026-06-12 — decisions/PHASE3-DEC-001~010)

> 기존 LOCK 재정의 0 — 아래 3건만 신규. 상세·근거는 `VAMOS Engineering/runtime_decisions.md` + 각 ADR.

| ID | LOCK 내용 | 출처 |
|---|---|---|
| R1-A25 | confidence 임계값: high=0.85 / medium=0.60 / refuse=0.30 (config.v1.toml 3키 — config LOCK 분모 20→23, V0 구현 시 집행) + 분기 HIGH/MEDIUM/LOW/REFUSE | STRATEGY_05 §5.2 → PHASE3-DEC-010 |
| R1-A21 | Defense Layer 3계층 독립(config LOCK / 5-Gate / NEVER_AUTO frozenset) — 계층 간 의존성 0, NEVER_AUTO는 config로 우회 불가 | STRATEGY_05 §3.2 + SDAR §5.1 → PHASE3-DEC-008 |
| R1-A22 | ResponseEnvelope 확장은 metadata(dict) 내부 한정(top-level 필드 추가 금지) — 키 4종: reasoning_trace/evidence_sources/confidence_score/disclaimer | D6 + STRATEGY_05 §4.2 → PHASE3-DEC-009 |

## 관련 노드

- [[VAMOS-Authority-Chain]] — 문서 위계 + 변경 프로토콜
- [[T0-Governance]] — R1~R11 규칙
- [[Non-Goals]] — 7개 절대 금지
- [[5-Gate-Decision-Framework]] — Gate 우회 불가
- [[Cost-Limits]] — 비용 절대 한도
