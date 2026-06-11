---
tags: [type/concept, tier/all, module/B-series, version/V1, lock/FREEZE]
aliases: [메모리 계층, L0~L3 메모리, 4계층 메모리]
created: 2026-06-11
---

# Memory Layers (L0~L3)

## 정의
I-3 Memory System의 4계층 저장 구조. 각 계층은 범위·TTL·B-Series 매핑·버전 활성이 고정되어 있다.

| 계층 | 범위 | TTL | B-Series | V1 | V2 | V3 |
|------|------|-----|----------|----|----|----|
| L0 Session | 단일 세션 | 7일 (최대 30일) | B-4 Working | ON | ON | ON |
| L1 Project | project_id 단위 | 90일 (연장 가능) | B-1 Episodic | 선택적 | ON | ON |
| L2 Long-term | 전역 (검색 기반) | 무기한 | B-3 Semantic | OFF | 제한(승인) | ON |
| L3 Procedural | 전역/프로젝트 | 무기한 | B-2 Procedural | OFF | 제한 | ON |

## 이 개념이 등장하는 모든 도메인
- [[T6-Memory-RAG]] — L0~L3 저장/승격/강등 정본(6-4)
- [[T1-Auxiliary-Modules]] — I-3 Memory System, I-14 Memory Distiller
- [[T6-Self-Evolution]] — B-Series 메모리 자산 진화
- [[T5-File-Context]] — Context Rot 대응 시 계층 검색 순서 활용

## 값·수치 (LOCK)
- B↔L 매핑 4쌍(교차 비직관, CC-009 — LOCK 변경불가): L0↔B-4 / L1↔B-1 / L2↔B-3 / L3↔B-2
- L2 저장 정책: 기본 "승인 필요"(LOCK) / QoD < 0.4 → L2 벡터삽입 금지, < 0.7 → 출력 보류
- project_id 필드 필수, 프로젝트 간 데이터 혼합 금지 / 검색 순서: 현재 프로젝트→글로벌→아카이브
- PII 마스킹: V1=정규식, V2+=NER 모델+문맥 분류기

## 버전별 차이
- V1: L0(+L1 선택적)만 / V2: L1 ON, L2·L3 제한(승인) / V3: 전 계층 ON

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §15 / `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` / `D:\VAMOS\docs\sot 2\6-4_Memory-RAG-Storage\`
