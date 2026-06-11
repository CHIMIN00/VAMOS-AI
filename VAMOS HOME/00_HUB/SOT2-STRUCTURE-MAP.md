---
tags: [type/hub, tier/all]
aliases: [SOT2 Map, SOT 2 구조]
description: "SOT 2 42개 폴더 구조 + 도메인 매핑 + 완성도 현황"
---

# SOT 2 Structure Map

## 개요

- **위치**: `D:\VAMOS\docs\sot 2\`
- **총 파일**: 648개
- **총 라인**: 169,628줄
- **도메인**: 36개 (+ _cross-ref 1 + FILE CONTEXT 1)
- **상태**: ALL-A VERIFIED (2026-03-27, Phase 11)
- **마스터 인덱스**: `SOT2_MASTER_INDEX.md` (674줄)

## 도메인 전체 목록

### Tier 0: Governance (1)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 0-0 | Governance-Rules-Meta | 규칙서.md | 474 | GOLD | [[T0-Governance]] |

### Tier 1: Core Intelligence (2)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 1-1 | Verifier-Reasoning-Engines | ✅ | 1,978 | GOLD | [[T1-Verifier-Engines]] |
| 1-2 | Auxiliary-Modules | ✅ | 1,785 | GOLD | [[T1-Auxiliary-Modules]] |

### Tier 2: Domain Execution (2)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 2-1 | Blue-Node-Architecture | ✅ | 1,064 | GOLD | [[T2-Blue-Node]] |
| 2-2 | COND-Modules-Detail | ✅ | 882 | GOLD | [[T2-COND-Modules]] |

### Tier 3: Feature Domains (9) — 3-1 의도적 결번
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 3-2 | Multimodal-Processing | ✅ | 1,283 | GOLD | [[T3-Multimodal]] |
| 3-3 | PKM-Knowledge-Management | ✅ | 1,084 | GOLD | [[T3-PKM]] |
| 3-4 | Workflow-RPA | ✅ | 992 | GOLD | [[T3-Workflow-RPA]] |
| 3-5 | Education-Learning | ✅ | 1,114 | GOLD | [[T3-Education]] |
| 3-6 | Health-Wellness-EmotionAI | ✅ | 1,383 | GOLD | [[T3-Health-EmotionAI]] |
| 3-7 | Developer-Tools-API-SDK | ✅ | 980 | GOLD | [[T3-Dev-Tools]] |
| 3-8 | Conversation-A2A | ✅ | 739 | GOLD | [[T3-A2A-Protocol]] |
| 3-9 | Business-Model-Strategy | ✅ | 771 | SILVER | [[T3-Business-Model]] |
| 3-10 | Agent-Protocol-Interoperability | ✅ | 872 | GOLD | [[T3-Agent-Protocol]] |

### Tier 4: Infrastructure (4)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 4-1 | Rust-Tauri-Infrastructure | ✅ | 723 | GOLD | [[T4-Rust-Tauri]] |
| 4-2 | CICD-Pipeline | ✅ | 717 | GOLD | [[T4-CICD]] |
| 4-3 | MCP-Server-Client | ✅ | 652 | GOLD | [[T4-MCP]] |
| 4-4 | MLOps-LLMOps | ✅ | 778 | GOLD | [[T4-MLOps]] |

### Tier 5: Quality & Cross-cutting (4)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 5-1 | Benchmark-Evaluation | ✅ | 1,729 | GOLD | [[T5-Benchmark]] |
| 5-2 | File-Context | ✅ | 806 | GOLD | [[T5-File-Context]] |
| 5-3 | v12-Additions-Detail | ✅ | 829 | SILVER | [[T5-v12-Additions]] |
| 5-4 | v23-Extension-Items | ✅ | 758 | SILVER | [[T5-v23-Extensions]] |

### Tier 6: System-wide (13)
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| 6-1 | UI-UX-System | ✅ | 747 | GOLD | [[T6-UI-UX]] |
| 6-2 | Security-Governance | ✅ | 673 | GOLD | [[T6-Security]] |
| 6-3 | Agent-Teams-PARL | ✅ | 1,479 | GOLD | [[T6-Agent-Teams]] |
| 6-4 | Memory-RAG-Storage | ✅ | 712 | GOLD | [[T6-Memory-RAG]] |
| 6-5 | SDAR-System | ✅ | 636 | GOLD | [[T6-SDAR]] |
| 6-6 | Self-Evolution-System | ✅ | 653 | SILVER | [[T6-Self-Evolution]] |
| 6-7 | RT-BNP-DCL | ✅ | 684 | GOLD | [[T6-RT-BNP-DCL]] |
| 6-8 | Cloud-Library | ✅ | 673 | GOLD | [[T6-Cloud-Library]] |
| 6-9 | Brain-Adapter-HAL | ✅ | 570 | GOLD | [[T6-Brain-Adapter]] |
| 6-10 | EXP-Modules-Detail | 카탈로그.md | 375 | SILVER | [[T6-EXP-Modules]] |
| 6-11 | Hologram-Main-LLM | ✅ | 1,038 | GOLD | [[T6-Hologram]] |
| 6-12 | Event-Logging | ✅ | 541 | SILVER | [[T6-Event-Logging]] |
| 6-13 | Operations | 운영매뉴얼.md | 281 | BRONZE | [[T6-Operations]] |

### 특수
| # | 폴더명 | 종합계획서 | 줄 수 | Quality | 노트 |
|---|--------|----------|------|---------|------|
| - | Ai-investing-detail | ✅ | 2,671 | GOLD | [[AI-Investing-Overview]] |
| - | _cross-ref | N/A (검증 메타) | - | - | [[SOT-Consistency-Audits]] |
| - | FILE CONTEXT | N/A (메타데이터) | - | - | - |

## 각 도메인 표준 파일 구조

```
{domain}/
├── {DOMAIN}_구조화_종합계획서.md    ← 14-section 마스터 문서
├── AUTHORITY_CHAIN.md              ← 권위 체인 (SOT 출처)
├── CONFLICT_LOG.md                 ← 변경/충돌 이력
└── {01_section}/ ~ {14_section}/   ← 하위 섹션 폴더
    └── _index.md
```

**예외 명명**:
- 0-0: `규칙서.md` (종합계획서 대신)
- 6-10: `카탈로그.md`
- 6-13: `운영매뉴얼.md`

## Quality Gate 분포

| 등급 | 개수 | 비율 |
|------|------|------|
| GOLD | 29 | 80.6% |
| SILVER | 6 | 16.7% |
| BRONZE | 1 | 2.8% |
| REJECT | 0 | 0% |

## 검증 현황

- Phase 11 검증 완료 (56 sessions, S1-1 ~ S11-8)
- LOCK 484건 불일치 0건
- 환각 탐지 0건 (405 atomic claims)
- 최종: ALL-A VERIFIED (20A + 16A-)
