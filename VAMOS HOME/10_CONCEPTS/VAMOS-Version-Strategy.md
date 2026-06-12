---
tags: [type/concept, tier/all, version/V0, lock/ABSOLUTE]
aliases: [버전 전략, V0→V3, 버전 로드맵]
created: 2026-06-12
---

# VAMOS Version Strategy (V0→V1→V2→V3)

## 정의
VAMOS의 4단계 버전 로드맵. **V0(구조기반, 1~2주) → V1(MVP, 8~12주) → V2(Pro) → V3(Enterprise)**. 각 단계는 GO/NO-GO 체크리스트와 정량 전환 조건을 통과해야 진입할 수 있다(PLAN-3.0 정본).

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — 비용한도·전환 게이트 정본(R1~R11)
- [[PLAN-3.0-Roadmap]] — 로드맵/비용/버전 정본(DEC-001~017)
- [[Cost-Limits]] — 버전별 절대 비용 상한
- 전 도메인 — 모든 모듈(187개)이 V1/V2/V3 ON·OFF·COND 게이트를 가짐

## 값·수치 (LOCK)
- 비용 상한: **V0=₩0(로컬 전용, D10 정본 단일화)** / V1=₩40,000/월(₩1,300/일) / V2=₩93,000/월 / V3=₩266,000/월 — ABSOLUTE
  - ※ V0의 "₩40,000 하드코딩"(GO/NO-GO #14)은 V1 진입 준비 구성이며 V0 지출 허용액 아님(D10)
- GO/NO-GO 항목 수: V0=16 / V1=21 / V2=14 / V3=11
- V1→V2 전환: QoD ≥ 0.85(30일) / RAG 정확도 ≥ 60% / 메모리 승격·강등 오류율 < 1% / P0 테스트 100% / 비용 초과 없이 30일 / 사용자 승인
- V2→V3 전환: QoD ≥ 0.90(60일) / 2-tier LLM 최적화 / P1 고급 테스트 / Self-evo 검증 / V3 비용 재검토+승인 / Loki+Grafana 배포

## 버전별 차이
- V0: 스캐폴딩+스켈레톤(I-1~I-5+I-19), Ollama+Chroma+SQLite / V1: Mini 90%+ / V2: Mini 60-70%+Main 30-40%, 서버 스택 / V3: Main 중심+Flagship, K8s

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §1/§7.3/§10 / `D:\VAMOS\docs\sot\PLAN-3.0_VAMOS_PLAN_3_0_최종완성본.md` / `D:\VAMOS\_targets\DECISION_REGISTER.md` (D10)
