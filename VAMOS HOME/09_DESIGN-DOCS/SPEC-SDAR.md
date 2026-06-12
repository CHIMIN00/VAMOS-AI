---
tags: [tier/T6, module/I-series, status/COND, version/V3, type/design, lock/ABSOLUTE]
aliases: [SDAR SPEC, Self-Diagnosis Auto-Repair, I-25, 자기진단 자동수리]
sot_source: "D:\\VAMOS\\docs\\sot\\VAMOS_SDAR_DESIGN_SPECIFICATION.md"
created: 2026-06-12
---

# SPEC SDAR

## 역할
**SDAR(Self-Diagnosis & Auto-Repair, 모듈 I-25) 자기진단·자동수리 시스템** 완전 설계 명세 (v1.0.0, 2026-02-23). 오류 실시간 감지→근본 원인 분석→위험 수준별 자동/반자동 수리. 연관: I-6, I-16, I-18, I-20, S-1, S-4, S-8.

## 핵심 섹션
- §2 5-Layer Pipeline: DETECTION→DIAGNOSIS→(계획/정책검증)→승인→실행·보고 — S-1/S-4가 신호·패턴 공급, I-19 승인, I-8 PolicyCheck, S-8 거버넌스 보고
- §3 단계적 자율 모델(Graduated Autonomy): AR-L0/L1(Manual/Notify)→AR-L2(AUTO_SAFE: 재시도/재시작 완전자동)→AR-L3(MODERATE: Config/Prompt Patch, 가역+알림)→AR-L4(HIGH: Code Patch/Migration, 스냅샷+알림)
- §4 오류 분류: 보안 오류 SDAR_E01~E06(인젝션/무단접근/유출/권한상승/안전우회/PII)은 전부 CRITICAL+NEVER_AUTO
- §5 수리 액션 카탈로그: RA_001~014 (자동 가능) + RA_NEVER_01~10
- §10 버전 로드맵: V1 OFF(I-20 기본 Fallback만) → V2 COND(AR-L2만) → V3 ON(AR-L3~L4 확대)

## LOCK 하이라이트
- **NEVER_AUTO 수리 액션 10개 (절대 자동 실행 금지)**: RA_NEVER_01~07 = 7개 불변 구역(safety_rules/cost_ceiling/approval_flow/non_goals/audit_format/data_retention/user_consent) + 08 자체 권한 상승(RBAC 위반) + 09 Guardrails 비활성화 + 10 Gate 우회
- Autonomy L3(FULL_AUTO)에서도 NEVER_AUTO는 절대 자동 실행 불가 — **코드 레벨 하드코딩 차단**(frozenset, 설정 우회 불가)
- 7개 불변 구역은 감지/진단까지만, 수리 제안도 금지 → SDAR 즉시 중단 + CRITICAL 알림
- §9 제약 및 안전 규칙(LOCK) 전용 장

## 연결
- [[T6-SDAR]] — 6-5 도메인 구현 / [[SDAR-Emergency-Response]] — Kill switch 개념
- [[Autonomy-Level-Framework]] — L0~L4 + NEVER 체계
- [[D2.0-07-Safety-Cost]] / [[Non-Goals]] — 불변 구역·승인 정본
- [[T6-Self-Evolution]] — S-8 거버넌스 연동 / [[Failover-Chain-Pattern]] — I-20 확장 관계

## 원본 문서
- `D:\VAMOS\docs\sot\VAMOS_SDAR_DESIGN_SPECIFICATION.md`
