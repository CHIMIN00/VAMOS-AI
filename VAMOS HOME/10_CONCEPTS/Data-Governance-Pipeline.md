---
tags: [type/concept, tier/all, version/V1, lock/ABSOLUTE]
aliases: [데이터 거버넌스, QoD 임계값, PII 마스킹]
created: 2026-06-12
---

# Data Governance Pipeline (QoD · PII)

## 정의
VAMOS 데이터 품질·개인정보 통제 체계. QoD(Quality of Data, 0.0~1.0)가 저장·출력 게이트 역할을 하고, PII는 저장 전 마스킹된다. 민감 개인정보 장기 저장은 Non-goal 2.4로 절대 금지.

## 이 개념이 등장하는 모든 도메인
- [[T6-Memory-RAG]] — 6-4 저장 게이트(L2 삽입·승격) 적용처
- [[T1-Auxiliary-Modules]] — I-15 Evidence & QoD Manager(AUX-QoD 정본)
- [[T4-MLOps]] — ML-QoD(LLM 출력 품질, 별도 체계)
- [[T6-Security]] — PII·data_retention·user_consent 불변 구역
- [[T6-Cloud-Library]] — 수집 품질 QoD(CC-003 이중 체계, 별도 목적)

## 값·수치 (LOCK)
- DEC-010: QoD 스케일 0.0~1.0
- QoD 임계값: **< 0.4 → L2 벡터삽입 금지 / < 0.7 → 출력 보류**
- DEC-014 QoD 가중치(RAG): relevance 0.30 + accuracy 0.25 + freshness 0.25 + completeness 0.20
- QoD 5요소(PLAN 정본): Accuracy 0.30 + Relevance 0.25 + Completeness 0.20 + Safety 0.15 + Efficiency 0.10
- PII 마스킹: **V1=정규식 / V2+=NER 모델+문맥 분류기**
- project_id 네임스페이스 필수 — 프로젝트 간 데이터 혼합 금지 / 검색 순서: 현재 프로젝트→글로벌→아카이브
- ⚠️ 용어 주의: AUX-QoD(1-2) vs ML-QoD(4-4) — [[Cross-Domain-Terminology]] #1

## 버전별 차이
- V1: 정규식 PII + L2 OFF / V2: NER 마스킹 + L2 제한(승인) / V3: L2/L3 전면 ON + 거버넌스 자동화

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §7.4/§15 / `D:\VAMOS\docs\sot\D2.0-06_06. VAMOS_DESIGN_2.0_STORAGE_MEMORY.md` / `D:\VAMOS\docs\sot 2\1-2_Auxiliary-Modules\`
