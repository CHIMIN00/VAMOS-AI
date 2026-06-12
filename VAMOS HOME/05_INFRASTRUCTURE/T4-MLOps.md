---
tags: [tier/T4, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [4-4, MLOps/LLMOps, MLOps-LLMOps]
tier: T4
domain: "4-4 MLOps-LLMOps"
sot_source: "D:\\VAMOS\\docs\\sot 2\\4-4_MLOps-LLMOps\\"
design_doc: "[[D2.0-04-Infra]]"
quality_gate: "APPROVED — Phase 4 RECOVERY Wave 1 #11 도메인 종료 (11 V3 NEW 77,588B, CONFLICT OPEN 0, 2026-06-01)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 프롬프트 버저닝+모델 카탈로그 | V2: 파이프라인·드리프트 7 NEW | V3: SOP·Fine-tuning·Guardrails 11 NEW"
created: 2026-06-12
---

# 4-4 MLOps-LLMOps

## 한줄 요약
프롬프트 버저닝·모델 평가·드리프트 감지·카나리 배포·피드백 루프 5축으로 LLM 운영 품질(ML-QoD)을 관장하는 정본 도메인.

## 핵심 정의
- ML-QoD 운영: 드리프트 7 메트릭(QoD 이동평균·KL·거부율 등, LOCK-ML-06) + QoD 24h 평균 < 0.60 → CRITICAL (LOCK-ML-07, DEC-010 0.0~1.0 스케일)
- QA-Gate(품질 게이트 5규칙, LOCK-ML-05): task_completion≥85% · QoD≥0.85 · safety<0.1% · p95<3s · cost<$0.05
- 카나리 5단계 Shadow(0%)→Canary(5%)→Partial(25%)→Majority(75%)→Full(100%) + 자동 롤백(QoD 차 >0.2 또는 에러율 >2×)
- 특이: Part2 NOT COVERED — Level 3 공백, sot 2/4-4가 What+How 유일 정본 겸임

## LOCK 항목 (LOCK-ML-01~12, 12건)
- ML-01 S7F-069~078 10항목 / ML-02 SemVer(PATCH/MINOR/MAJOR) / ML-03 상태 4단계 draft→staging→production→deprecated
- ML-04 A/B p<0.05 / ML-05 품질 게이트 5규칙 / ML-06 드리프트 7메트릭 / ML-07 QoD<0.60 CRITICAL
- ML-08 카나리 5단계 / ML-09 자동 롤백 조건 / ML-10 2주 스프린트(목표 QoD +0.1)
- ML-11 카탈로그 7필드 / ML-12 피드백 100% 로컬 저장·외부 전송 금지

## 의존성 (Depends On)
- [[T5-Benchmark]] — LOCK-BE-09 Prompt Injection 인용·회귀 알림 (양방향 통지) / [[T0-Governance]] — R1~R11

## 제공 (Provides To)
- [[T4-CICD]] — 모델 배포 게이트 (양방향 B12, 인프라 게이트는 4-2 소유)
- [[T3-Business-Model]] — LLM API 비용 최적화 / [[T6-Brain-Adapter]] — drift detection → 라우팅 가중치
- [[T6-EXP-Modules]] — 모듈 드리프트 감지 → 자동 비활성화

## 횡단 개념 연결
- [[Cost-Limits]] — cost<$0.05 게이트·비용 최적화 / [[SLA-Performance-Targets]] — p95<3s 게이트

## STEP7 매핑
- 출처: STEP7-F Part 9 (S7F-069~078, 10개 항목 — Part2 NOT COVERED)

## 버전별 범위
- V1: 프롬프트 버저닝 + 모델 카탈로그 / V2: 파이프라인·드리프트·카나리·피드백 7 NEW (7,790L) / V3: SOP 3 + LoRA/QLoRA 3 + Guardrails 4 rails + cross_validation 1 (11 NEW)

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY (2026-06-01), CONF-ML-002/003 RESOLVED 전환, OPEN 0
- LOCK 검증: 12/12 일치 (AUTHORITY_CHAIN 2026-06-01, verbatim 보존·재정의 0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\4-4_MLOps-LLMOps\
- Authority: 4-4_MLOps-LLMOps\AUTHORITY_CHAIN.md
- Design: STEP7-F Part 9 + [[D2.0-04-Infra]]
