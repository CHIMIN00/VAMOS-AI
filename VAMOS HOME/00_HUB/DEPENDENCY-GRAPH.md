---
tags: [type/hub, tier/all]
aliases: [Dependency Graph, 의존성 그래프]
description: "VAMOS 36개 도메인 간 112개 의존성 엣지 전체 매핑"
---

# VAMOS Dependency Graph

## 통계

- **도메인**: 36개
- **총 엣지**: 112개 (90 단방향 + 27 양방향 쌍)
- **순환 의존성**: 0개
- **교차 Tier 양방향**: 6개 (모두 정당화됨)
- **검증**: Phase 11 S11-4 Layer 1 PASS

## Tier별 흐름 방향

```
T0 (Governance)      ──→ ALL 35개 (단방향 Provider)
T1 (Core Intelligence) ──→ T3, T6 (지능 서비스 제공)
T2 (Execution)       ──→ T3 (런타임 실행 환경 제공)
T3 (Features)        ←→ T3 내부 (동일 Tier 양방향 허용)
T4 (Infrastructure)  ──→ ALL (인프라 서비스 제공)
T5 (Quality)         ──→ ALL (측정/품질 서비스)
T6 (System-wide)     ←→ 밀집 양방향 메쉬 (27 양방향 쌍 중심)
```

## 27개 양방향 쌍 (전체)

### 동일 Tier 내 (허용)
| # | 도메인 A | 도메인 B | 관계 |
|---|---------|---------|------|
| 1 | [[T2-Blue-Node\|2-1]] | [[T2-COND-Modules\|2-2]] | BN↔COND 실행 |
| 2 | [[T3-Multimodal\|3-2]] | [[T3-PKM\|3-3]] | 멀티모달↔지식관리 |
| 3 | [[T3-Multimodal\|3-2]] | [[T3-Health-EmotionAI\|3-6]] | 미디어↔감성AI |
| 4 | [[T3-PKM\|3-3]] | [[T3-Education\|3-5]] | PKM↔교육 (SM-2) |
| 5 | [[T3-Workflow-RPA\|3-4]] | [[T3-Health-EmotionAI\|3-6]] | 자동화↔웰니스 |
| 6 | [[T3-Workflow-RPA\|3-4]] | [[T3-Dev-Tools\|3-7]] | 자동화↔개발도구 |
| 7 | [[T3-Education\|3-5]] | [[T3-Health-EmotionAI\|3-6]] | 교육↔건강 |
| 8 | [[T3-Dev-Tools\|3-7]] | [[T3-Agent-Protocol\|3-10]] | 도구↔프로토콜 |
| 9 | [[T3-A2A-Protocol\|3-8]] | [[T3-Agent-Protocol\|3-10]] | A2A↔AP |
| 10 | [[T3-A2A-Protocol\|3-8]] | [[T4-MCP\|4-3]] | A2A↔MCP |
| 11 | [[T4-Rust-Tauri\|4-1]] | [[T4-CICD\|4-2]] | 빌드↔배포 |
| 12 | [[T4-CICD\|4-2]] | [[T4-MLOps\|4-4]] | CI/CD↔MLOps |
| 13 | [[T6-UI-UX\|6-1]] | [[T6-Hologram\|6-11]] | UI↔Hologram |
| 14 | [[T6-Security\|6-2]] | [[T6-SDAR\|6-5]] | 보안↔SDAR |
| 15 | [[T6-Security\|6-2]] | [[T6-Event-Logging\|6-12]] | 보안↔로깅 |
| 16 | [[T6-Agent-Teams\|6-3]] | [[T6-Security\|6-2]] | 팀↔보안 |
| 17 | [[T6-Agent-Teams\|6-3]] | [[T6-SDAR\|6-5]] | 팀↔SDAR |
| 18 | [[T6-Memory-RAG\|6-4]] | [[T6-SDAR\|6-5]] | 메모리↔SDAR |
| 19 | [[T6-SDAR\|6-5]] | [[T6-Self-Evolution\|6-6]] | SDAR↔Self-evo |
| 20 | [[T6-RT-BNP-DCL\|6-7]] | [[T6-Cloud-Library\|6-8]] | RT↔Cloud |
| 21 | [[T6-Event-Logging\|6-12]] | [[T6-Operations\|6-13]] | 로깅↔운영 |

### 교차 Tier (정당화 필요, 6개)
| # | 도메인 A | 도메인 B | 정당화 |
|---|---------|---------|--------|
| 22 | [[T6-Agent-Teams\|6-3]] | [[T3-A2A-Protocol\|3-8]] | 팀 통신 = A2A 프로토콜 |
| 23 | [[T6-Agent-Teams\|6-3]] | [[T3-Agent-Protocol\|3-10]] | 자율성 수준 참조 (재정의 안함) |
| 24 | [[T6-Memory-RAG\|6-4]] | [[T1-Auxiliary-Modules\|1-2]] | 메모리 승격/강등 |
| 25 | [[T6-Memory-RAG\|6-4]] | [[T3-PKM\|3-3]] | L2 지식 저장소 |
| 26 | [[T6-SDAR\|6-5]] | [[T1-Auxiliary-Modules\|1-2]] | 진단 결과 피드백 |
| 27 | [[T6-Brain-Adapter\|6-9]] | [[T6-Hologram\|6-11]] | 2-tier 라우팅 |

## 핵심 Provider→Consumer 흐름

### 가장 많이 참조되는 도메인 (Inbound)
1. **[[T0-Governance]]** — 37 inbound (ALL)
2. **[[T2-Blue-Node]]** — 15 inbound (T3 전체)
3. **[[T6-SDAR]]** — 14 inbound (시스템 전역)
4. **[[T6-Memory-RAG]]** — 13 inbound
5. **[[T3-Agent-Protocol]]** — 12 inbound

### 가장 많이 제공하는 도메인 (Outbound)
1. **[[T0-Governance]]** — 37 outbound
2. **[[T6-SDAR]]** — 11 outbound
3. **[[T6-Security]]** — 12 outbound
4. **[[T2-COND-Modules]]** — 10 outbound

## 의존 규칙

- **R7**: CORE→COND 단방향만 허용 (역방향 금지)
- **R-63-10**: 6-3은 3-10의 L0-L4를 참조하되 재정의하지 않음
- **R-63-11**: 6-3은 3-8의 A2A를 참조하되 재정의하지 않음
- **R-64-2**: B↔L 매핑 고정 (변경 불가)

## 알려진 갭 (6건, 모두 LOW-MEDIUM)

1. G1: 6-10 EXP dependencies missing from central graph (fixed)
2. G2: 3-4→3-5 education provision not in matrix (documented)
3. G3-G6: Minor consumer-only domain declarations (acceptable)

## 원본 참조

- `D:\VAMOS\docs\sot 2\0-0_Governance-Rules-Meta\DEPENDENCY_GRAPH.md`
- `D:\VAMOS\docs\sot 2\_cross-ref\S11-4_SOT2_CROSS_REF_REPORT.md`
