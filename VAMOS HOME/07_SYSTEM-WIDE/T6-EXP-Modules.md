---
tags: [tier/T6, module/EVX-series, status/EXP, version/V3, type/domain, lock/FREEZE]
aliases: [6-10, EXP 모듈 카탈로그, EXP-Modules-Detail]
tier: T6
domain: "6-10 EXP-Modules-Detail"
sot_source: "D:\\VAMOS\\docs\\sot 2\\6-10_EXP-Modules-Detail\\"
design_doc: "[[D2.0-01-Overview]]"
quality_gate: "APPROVED — Phase 7 FINAL PASS · Content A (S10-5), SDV 의도적 예외(카탈로그 형식)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1~V2: OFF | V3: V3-P2 전체 활성화"
created: 2026-06-12
---

# 6-10 EXP-Modules-Detail

## 한줄 요약
V3 EXP 확장 모듈 19개(B-시리즈 5 + EVX 6 + A-시리즈 4 + D-시리즈 4)의 카탈로그 정본을 소유하는 Tier 6 실험 도메인 (기본 전부 OFF).

## 핵심 정의
- 모듈 분류: B(학습 5: B-1/2/4/5/6) / EVX(실험 6: EVX-1~6) / A(고급AI 4: A-3/5/6/7) / D(생성 4: D-3~6) = 19
- 모든 EXP 모듈 `enabled=false` 기본, config 명시 활성화 + 07 Gate 승인/비용 통과 필수
- I/S/E/C-시리즈는 각 기존 도메인(1-2, 6-6, 3-2, 1-1)에서 관리 — 본 카탈로그 범위 외
- 카탈로그 형식 (표준 14-section 미적용, SDV EXEMPTED)

## LOCK 항목 (LOCK-610-1~8, 8건)
- 610-1 Module Catalog 표준 필드(category, module_id, enabled, version, dependencies)
- 610-2 EXP 기본 OFF / 610-3 EVX 네임스페이스 격리(`vamos-experimental` K8s)
- 610-4 V3 비용 상한 ₩266,000/월 / 610-5 07 Gate 필수(자동 ON 금지)
- 610-6 모듈 ID 체계(B/EVX/A/D + 순번) / 610-7 S-시리즈 순차 활성화(6-6 참조) / 610-8 GraphRAG 벤치마크 정확도 ≥90%

## 의존성 (Depends On)
- [[T1-Verifier-Engines]] — C-시리즈 추론 모듈 관리 (카탈로그 범위 외) / [[T1-Auxiliary-Modules]] — I/S-시리즈 정본 참조
- [[T4-MLOps]] — 모듈 드리프트 감지 → 자동 비활성화 / [[T6-Self-Evolution]] — S-시리즈(S-2~S-8) 정본 관리
- [[T6-Brain-Adapter]] — EVX-3 Log-prob, A-5 Lazy Gen, D-5 Parallel Gen 경유

## 제공 (Provides To)
- (소비 전용 도메인 — DEPENDENCY_GRAPH §2.3 6-10 행 Provider 에지 0)

## 횡단 개념 연결
- [[Module-Classification]] — B/EVX/A/D 분류 체계 / [[A-Series-Architecture-Extensions]] — A-시리즈 정의
- [[EVX-Verification-Chain]] — EVX 실험 모듈 / [[Cost-Limits]] — V3 상한 ₩266,000

## 관련 모듈 시리즈
- [[MODULE-MAP]] — B-Series / EVX-Series / A-Series / D-Series 카탈로그 정본

## STEP7 매핑
- 출처: D2.0-01 §5.6~§5.13 (모듈 카탈로그 정본) + Part2 V3-P2 (L3993-4335)

## 버전별 범위
- V1~V2: 전체 OFF / V3: V3-P2 전체 활성화 (07 Gate 경유, 순차)

## 검증 상태
- Quality Gate: APPROVED · Content A — SDV 예외 (EXEMPTED, 카탈로그 형식, Phase 11 S11-6)
- LOCK 검증: 8/8 일치 (AUTHORITY_CHAIN 실측, LOCK-610-1~8 보호 정상 적용)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\6-10_EXP-Modules-Detail\ (EXP_MODULES_DETAIL_카탈로그.md)
- Authority: 6-10_EXP-Modules-Detail\AUTHORITY_CHAIN.md
- Design: [[D2.0-01-Overview]] (§5.6~§5.13), [[D2.0-02-Orange-Core]]
