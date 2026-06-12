---
tags: [tier/T6, module/I-series, status/CORE, version/V1, type/domain, lock/FREEZE]
aliases: [6-13, 운영, Operations]
tier: T6
domain: "6-13 Operations"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-13_Operations\\"
design_doc: "[[Implementation-Part2]]"
quality_gate: "APPROVED (운영매뉴얼 형식, SDV 의도적 예외 EXEMPTED)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V0~V1: 기본 | V2: 강화 | V3: 고급"
created: 2026-06-12
---

# 6-13 Operations

## 한줄 요약
모니터링·백업/복구(RPO/RTO)·인시던트·롤백·헬스체크·로그 보존 등 Part2 §6.12 12개 운영 서브섹션의 운영 매뉴얼 정본을 소유하는 Tier 6 횡단 운영 도메인.

## 핵심 정의
- Part2 §6.12 12개 서브섹션 1:1 매핑 (모니터링/Hetzner/백업/인시던트/알림/롤백/헬스체크/로그보존/비용/SDAR폴백/RT-BNP장애/Cloud페일오버)
- RPO: V0-V1 1일 / V2 1시간 / V3 15분, RTO: V0-V1 30분 / V2 2시간 / V3 30분
- 비용 알림 임계값: 경고 70% / 주의 85% / 위험 95% / 초과 100%, 월간 상한 $200
- 운영매뉴얼 형식 (14-섹션 종합계획서 미적용, SDV EXEMPTED)

## LOCK 항목 (LOCK-OP-01~14, 14건)
- OP-01~03 RPO (1일/1시간/15분) / OP-04~06 RTO (30분/2시간/30분)
- OP-07 비용 알림 임계값 4단계 / OP-08 월간 비용 상한 $200 / OP-09 헬스체크 주기 (V1 30초/V2 15초/V3 10초)
- OP-10 로그 보존 (90일/180일/365일) / OP-11 인시던트 P0 복구 15분 / OP-12 P0 즉시 롤백
- OP-13 Hetzner CX31 스펙 (2vCPU/8GB/80GB) / OP-14 S3a 승인 대기 타임아웃 600초

## 의존성 (Depends On)
- [[T6-Event-Logging]] — 운영 모니터링/알림 이벤트 수신 (양방향 B21)

## 제공 (Provides To)
- [[T4-Rust-Tauri]] — 헬스체크·롤백·모니터링 표준 / [[T4-CICD]] — 배포 롤백·인시던트 대응
- [[T4-MCP]] — 헬스체크·로그 보존 / [[T5-Benchmark]] — 성능 모니터링 메트릭
- [[T6-SDAR]] — SDAR 수동 폴백 절차 / [[T6-RT-BNP-DCL]] — 소스 장애 대응
- [[T6-Cloud-Library]] — 페일오버 절차 / [[T6-Event-Logging]] — 로그 보존 정책 (양방향 B21)

## 횡단 개념 연결
- [[SLA-Performance-Targets]] — RPO/RTO·헬스체크 / [[Cost-Limits]] — 비용 초과 대응
- [[Event-Logging-Standard]] — 로그 소비·보존

## 관련 모듈 시리즈
- [[MODULE-MAP]] — I-9 로그/I-15 스냅샷 산출물의 운영 소비 측

## STEP7 매핑
- 출처: Part2 §6.12 (L5976-6126, 12개 서브섹션)

## 버전별 범위
- V0~V1: 기본 운영 (RPO 1일) / V2: 강화 (RPO 1시간) / V3: 고급 (RPO 15분, 헬스체크 10초)

## 검증 상태
- Quality Gate: APPROVED — SDV 의도적 예외 (운영매뉴얼 형식, Phase 11 S11-6 V-2)
- LOCK 검증: 14/14 일치 (AUTHORITY_CHAIN 실측, LOCK-OP-01~14 보호 정상 적용)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-13_Operations\ (OPERATIONS_운영매뉴얼.md)
- Authority: 6-13_Operations\AUTHORITY_CHAIN.md
- Design: [[Implementation-Part2]] (§6.12 정본)
