---
tags: [type/concept, tier/all, version/V1, lock/FREEZE]
aliases: [SLA, 성능 목표, S0~S8 타임아웃]
created: 2026-06-12
---

# SLA Performance Targets (S0~S8 단계 타임아웃)

## 정의
VAMOS 요청 처리 상태머신(S0~S8)의 단계별 타임아웃과 실행 제한. 5-Phase 파이프라인의 각 전이가 제한 시간 내 완료되어야 하며, 초과 시 Failure/Fallback 경로로 진입한다.

## 이 개념이 등장하는 모든 도메인
- [[T0-Governance]] — 상태머신·Gate 정본
- [[T1-Auxiliary-Modules]] — I-5 Decision, I-20 Failure/Fallback Manager
- [[T6-Operations]] — 운영 모니터링·장애대응 기준
- [[T5-Benchmark]] — p95 등 성능 측정 위임(5-1)
- [[End-to-End-Request-Flow]] — S0→S8 전체 흐름

## 값·수치 (LOCK — CLAUDE.md §12 상태머신)
- S0_RECEIVED → **S1_INTENT_PARSED(5s)** → **S2_EVIDENCE_READY(30s)** → **S3_DECISION_LOCKED(120s)** → **S4_EXECUTING(10s)** → **S5_OUTPUT_READY(15s)** → S6_SELF_CHECKED → S7_MEMORY_COMMITTED → S8_DONE
- S6~S8: §12 기준 별도 타임아웃 수치 미표기 (Self-check soft loop 1회 제한 적용)
- 승인 타임아웃: 600s(10분 미응답 → 자동 거부), P2 도메인 300s
- 코드 실행 격리: Docker 샌드박스, 네트워크 차단, **30초**
- 동시성: MAX_CONCURRENT_BLUE_NODES=3, TOOLS=5 / Multi-Brain Failover: 3회 타임아웃 시 전환
- 대화 턴 상한 P0=5/P1=10/P2=20, TEE 반복 P0=3/P1=5/P2=10

## 버전별 차이
- V1: 로컬 기준 동일 적용 / V2: 서버 스택에서 동일 LOCK 유지 / V3: K8s·50+ 에이전트에서도 단계 타임아웃 불변

## 원본 참조
- `D:\VAMOS\CLAUDE.md` §12/§7.2/§20 / `D:\VAMOS\docs\sot\D2.0-05_05. VAMOS_DESIGN_2.0_AGENT_WORKFLOW.md`
