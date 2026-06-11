---
tags: [type/hub, tier/all]
aliases: [39 Files, Master Index, 39개 파일]
description: "SOT 39개 마스터 파일 계층 구조 + 역할 매핑"
---

# 39-FILE Master Index

## 문서 위계 (ABSOLUTE — DEC-001)

```
RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
```

## A그룹: 설계 21개 (~35,472줄)

### RULE (1개)
| 파일 | 줄 수 | 역할 |
|------|------|------|
| BASE-1.3_VAMOS_RULE_1.3_BASE.md | 633 | 절대 불변 규칙 (Identity/Safety/Cost/Non-goal) |

→ [[BASE-1.3-Rules]]

### PLAN (1개)
| 파일 | 줄 수 | 역할 |
|------|------|------|
| PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md | 6,948 | 로드맵/비용/버전 정본. DEC-001~017 |

→ [[PLAN-3.0-Roadmap]]

### DESIGN D2.0 (8개)
| 파일 | 줄 수 | 역할 | 노트 |
|------|------|------|------|
| D2.0-01 OVERVIEW | 1,718 | 아키텍처 허브, 모듈 레지스트리 | [[D2.0-01-Overview]] |
| D2.0-02 ORANGE CORE | 4,230 | I-1~I-25 상세설계 | [[D2.0-02-Orange-Core]] |
| D2.0-03 BLUE NODES | 1,943 | Blue Node 7 컴포넌트 | [[D2.0-03-Blue-Nodes]] |
| D2.0-04 INFRA CORE | 1,591 | Brain Engine, MCP, Tool | [[D2.0-04-Infra]] |
| D2.0-05 AGENT WORKFLOW | 1,982 | 5-Phase Pipeline, LangGraph | [[D2.0-05-Agent-Workflow]] |
| D2.0-06 STORAGE MEMORY | 2,428 | L0~L3, RAG 6단계, Vector DB | [[D2.0-06-Storage-Memory]] |
| D2.0-07 SAFETY COST | 2,655 | 5-Gate, RBAC, Guardrails | [[D2.0-07-Safety-Cost]] |
| D2.0-08 UI UX | 2,696 | Tauri+React, Builder/Hologram | [[D2.0-08-UI-UX]] |

### SCHEMA D2.1 (11개)
| 파일 | 역할 | 노트 |
|------|------|------|
| D2.1-D1 GLOSSARY | 용어 정의 | [[D2.1-Schema-Index]] |
| D2.1-D2 ORANGE CORE | OC 스키마 | |
| D2.1-D3 BLUE NODES | BN 스키마 | |
| D2.1-D4 INFRA CORE | 인프라 스키마 | |
| D2.1-D5 AGENT WORKFLOW | 워크플로우 스키마 | |
| D2.1-D6 STORAGE MEMORY | 저장소 스키마 | |
| D2.1-D7 SAFETY COST | 안전/비용 스키마 | |
| D2.1-D8 UI UX | UI 스키마 | |
| D2.1-A1 TECH STACK | 기술 스택 정의 | |
| D2.1-Q1 AUDIT REPORT | 감사 보고서 | |

## B그룹: 구현가이드 7개 (~9,618줄)

| 파일 | 역할 | 노트 |
|------|------|------|
| PHASE_B1 API CONTRACT | 88개 엔드포인트 | [[D2.0-05-Agent-Workflow]] |
| PHASE_B2 PROJECT STRUCTURE | 모노레포 레이아웃 (LOCK) | |
| PHASE_B3 DEPENDENCIES | pip/npm/cargo 의존성 | |
| PHASE_B4 CONFIG SPEC | config.toml (LOCK) | [[VAMOS-Configuration-Framework]] |
| PHASE_B5 TEST STRATEGY | 테스트 전략 80%+ | |
| PHASE_B6 CICD PIPELINE | GitHub Actions 8-stage | |
| PHASE_B7 MIGRATION STRATEGY | V1→V2→V3 마이그레이션 | |

## C그룹: 특화 SPEC 5개 (~8,543줄)

| 파일 | 역할 | 노트 |
|------|------|------|
| VAMOS_MASTER_SPECIFICATION | 전체 통합 참조점 (1,893줄) | [[VAMOS-HOME]] |
| VAMOS_AI_INVESTING_SPEC | AI 투자 상세 | [[AI-Investing-Overview]] |
| VAMOS_CLOUD_LIBRARY_SPEC | Cloud Library | [[SPEC-Cloud-Library]] |
| VAMOS_AGENT_TEAMS_SPEC | Agent Teams | [[SPEC-Agent-Teams]] |
| VAMOS_SDAR_DESIGN_SPECIFICATION | SDAR 자가진단 | [[SPEC-SDAR]] |

## D그룹: STEP7 상세명세 5개 (~9,019줄)

| 파일 | 역할 | 노트 |
|------|------|------|
| VAMOS_STEP7_A-E_상세명세서 | A~E 카테고리 | [[STEP7-Implementation-Bridge]] |
| VAMOS_STEP7_F-I_상세명세서 | F~I 카테고리 | |
| VAMOS_STEP7_J-M_상세명세서 | J~M 카테고리 | |
| VAMOS_STEP7_N-P_보강_상세명세서 | N~P 카테고리 | |
| VAMOS_STEP7_보강_통합명세서 | 통합 | |

→ 총 3,101건 AI기술보강 (16개 카테고리 A~P)

## E그룹: 기타 1개 (~1,853줄)

| 파일 | 역할 |
|------|------|
| VAMOS_BEGINNER_GUIDE | 초보자 온보딩 가이드 |

→ [[Beginner-Guide]]

## 원본 경로

`D:\VAMOS\docs\sot\` (68개 파일, 89,413줄)
