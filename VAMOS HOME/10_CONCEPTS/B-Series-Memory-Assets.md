---
tags: [type/concept, tier/all, module/B-series, version/V3, lock/FREEZE]
aliases: [B-Series, 메모리/스킬 자산, B1~B6]
created: 2026-06-12
---

# B-Series: Memory/Skill Assets (B-1~B-6)

## 정의
Memory/Skill/Self-evo 자산 모듈 6개. CORE 1(B-3) + EXP 5, V3 중심. 메모리 계층 L0~L3과 4쌍 교차 매핑된다.

| ID | 명칭 | status | V1 | V2 | V3 |
|---|---|---|---|---|---|
| B-1 | Skill Library (스킬 라이브러리) | EXP | OFF | OFF | ON |
| B-2 | Procedural Memory (방법론 메모리) | EXP | OFF | OFF | ON |
| B-3 | Memory Decay (망각/감쇠) | CORE | ON | ON | ON |
| B-4 | Auto Curriculum Generator | EXP | OFF | OFF | ON |
| B-5 | RL-like Self Trainer | EXP | OFF | OFF | ON |
| B-6 | DSPy Prompt Optimizer | EXP | OFF | OFF | ON |

## 이 개념이 등장하는 모든 도메인
- [[T6-Memory-RAG]] — L0~L3 저장/승격/강등 정본(6-4), B↔L 매핑 소비
- [[T6-Self-Evolution]] — B-5 RL-like Self Trainer·B-6 DSPy가 자기진화 자산
- [[T6-EXP-Modules]] — B-Series EXP 관리 정본(6-10)
- [[T1-Auxiliary-Modules]] — I-3 Memory System·I-14 Memory Distiller 연동

## 값·수치 (LOCK)
- **B↔L 매핑 4쌍 (CC-009, 교차 비직관 — LOCK 변경불가)**: L0 Session↔B-4(Working) / L1 Project↔B-1(Episodic) / L2 Long-term↔B-3(Semantic) / L3 Procedural↔B-2(Procedural) — [[Memory-Layers]] 참조
- L2 저장 정책: 기본 "승인 필요" (LOCK)
- V1 진입 GO/NO-GO에 "B↔L 매핑표 추가 (CC-009)" 항목 포함

## 버전별 차이
- V1: B-3만 ON / V2: 동일 / V3: B-1~B-6 전부 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §6 (B-Series 표)·§15 / `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` / `D:\VAMOS\docs\sot 2\6-10_EXP-Modules-Detail\`
