---
tags: [tier/T5, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [5-1, 벤치마크 평가, Benchmark-Evaluation]
tier: T5
domain: "5-1 Benchmark-Evaluation"
sot_source: "D:\\VAMOS\\docs\\sot 2\\5-1_Benchmark-Evaluation\\"
design_doc: "[[STEP7-Implementation-Bridge]]"
quality_gate: "APPROVED — Phase 4 RECOVERY Sub-A+Sub-B 도메인 종료 (88 S7G DONE 100%, CFL-21 RESOLVED, 2026-06-03)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: 표준 벤치마크+190 항목 | V2: 13 파일 V2 산출물 | V3: 인간평가 정례화+master INDEX 88"
created: 2026-06-12
---

# 5-1 Benchmark-Evaluation

## 한줄 요약
STEP7-G 88개 항목(S7G-001~088)·190+ 테스트·VBS·인간 평가를 측정하는 Tier 5 품질 횡단 정본 도메인.

## 핵심 정의
- 복합 출처: STEP7-G(88 항목 정본) + PHASE_B5(테스트 전략) — Level 2 이중 참조
- VBS-12~17 도메인 횡단 임계값은 해당 도메인 정본 소유자와 공동 관리 (R-18-5)
- 골든셋 v2 실데이터 162문항 전환 완료 (2026-06-11, Phase 2-0 재구축)

## LOCK 항목 (LOCK-BE-01~15, 15건)
- BE-01 MMLU ≥85% / BE-02 HumanEval pass@1 ≥85% / BE-03 LogicKor ≥8.0/10 / BE-04 ARC-AGI pass@3 ≥30%
- BE-05 Cohen's κ ≥0.6 / BE-06 Bootstrap 95% CI 필수 / BE-07 인간 평가 최소 2명(+2점차 시 3번째) / BE-08 seed=42 고정
- BE-09 Prompt Injection 방어율 ≥95% / BE-10 Faithfulness ≥0.90 / BE-11 RAGAS 4지표(0.90/0.80/0.75/0.75)
- BE-12 VBS Core 일간·전체 주간 / BE-13 골든셋 분기 교체(신규 ≥20%, Git LFS+암호화) / BE-14 회귀 3%(CRITICAL 1%) 하락 알림 / BE-15 190+ 항목·CRITICAL 45건 V1 배포 차단

## 의존성 (Depends On)
- [[T5-File-Context]] — 구간별 정확도 목표 정의 수신(S7G-040/041, 측정 위임 W12) / [[T6-Operations]] — 성능 모니터링 메트릭
- [[T0-Governance]] — R-18-1~5

## 제공 (Provides To)
- ALL 35개 도메인 — 벤치마크 실행/측정 결과 (T5→ALL, 단방향 Provider)
- [[T4-CICD]] — 회귀 알림·골든셋 주기 / [[T4-MLOps]] — RAGAS 4지표·VBS Core 주기 (양방향 통지)
- VBS 공동 관리: [[T3-PKM]] / [[T3-Education]] / [[T3-Health-EmotionAI]] / [[T3-Dev-Tools]] / [[T3-Agent-Protocol]] / [[AI-Investing-Overview]]

## 횡단 개념 연결
- [[Benchmark-Evaluation-Framework]] — 본 도메인이 프레임워크 정본 / [[SLA-Performance-Targets]] — 측정 기준선

## STEP7 매핑
- 출처: STEP7-G 88개 항목 (Part2는 러너+MMLU/HumanEval만 PARTIAL ~5%)

## 버전별 범위
- V1: 표준 벤치마크 + 190+ 테스트 항목 / V2: 13 파일(2-A 8 + 2-B 5) / V3: 인간평가 4 NEW + 12 신규(7 EXTEND+5 NEW) + master INDEX 88 매트릭스 100%

## 검증 상태
- Quality Gate: APPROVED — Phase 4 RECOVERY Wave 3 #22 (2026-06-03), CFL-21 RESOLVED·S7G-081/082/083 명칭 교정
- LOCK 검증: 15/15 일치 (AUTHORITY_CHAIN v1.1, immutable·재정의 0)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\5-1_Benchmark-Evaluation\
- Authority: 5-1_Benchmark-Evaluation\AUTHORITY_CHAIN.md (v1.1)
- Design: STEP7-G + PHASE_B5
