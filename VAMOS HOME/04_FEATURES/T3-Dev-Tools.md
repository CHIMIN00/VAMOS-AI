---
tags: [tier/T3, module/C-series, status/COND, version/V1, type/domain, lock/FREEZE]
aliases: [3-7, 개발자 도구, Developer-Tools-API-SDK]
tier: T3
domain: "3-7 Developer-Tools-API-SDK"
sot_source: "D:\\VAMOS\\docs\\sot 2\\3-7_Developer-Tools-API-SDK\\"
design_doc: "[[D2.0-02-Orange-Core]]"
quality_gate: "APPROVED — Phase 5 FINAL PASS / Phase 4 RECOVERY 4 V3 NEW (2026-06-01)"
step7_category: "[[STEP7-Implementation-Bridge]]"
version_gate: "V1: P1 MVP 로컬 | V2: P2 API+Plugin | V3: P3 마켓플레이스"
created: 2026-06-12
---

# 3-7 Developer-Tools-API-SDK

## 한줄 요약
AI 코딩 엔진·FIM 자동완성·Plugin SDK(WASM)·REST API/SDK/CLI·VADD 마켓플레이스를 구현 정본으로 관리하는 Tier 3 개발자 도구 도메인.

## 핵심 정의
- 7개 서브폴더 정본: 01 coding-engine(21항목) / 02 code-completion / 03 refactoring / 04 test-generation / 05 plugin-sdk / 06 vscode-extension / 07 marketplace
- 권한 체인: STEP7-L(56 L-ID, 항목 존재 정본) → sot 2/3-7 계획서(What+How) → 서브폴더 상세 → Part2 §6(MENTION-ONLY, 정본 아님)
- Phase 2 V2 = 17 변경(14 NEW+1 UPDATE+2 EXTEND), LOCK 386 지점 verbatim, STEP7-L 315 line refs
- ★ cross-domain LOCK-BM-09 verbatim cite-only first specialty (3-9 정본 "70% 개발자 / 30% VAMOS" 첫 인용 도메인)

## LOCK 항목 (LOCK-DT-01~10, 10건)
- DT-01 API 버저닝 `/api/v{N}/` + semantic versioning / DT-02 SDK 호환 Python≥3.9·Node.js≥18·Rust≥1.70
- DT-03 CLI `vamos {동사} {명사} [옵션]` 패턴 / DT-04 FIM fallback Qwen 2.5 Coder 7B(로컬)→gpt-4o→claude-sonnet
- DT-05 플러그인 WASM 격리·선언된 권한만 허용 / DT-06 코드 실행 타임아웃 30초 (D2.0-02/03 근거)
- DT-07 자동완성 디바운스 150ms / DT-08 Rate Limiting 분당 60 요청(기본)
- DT-09 매니페스트 plugin-manifest-v1.json(필드 추가만) / DT-10 테스트 커버리지 ≥80% (STEP7-F 근거)

## 의존성 (Depends On)
- [[T0-Governance]] — R1~R11 / [[T1-Verifier-Engines]] — LLM 추론 결과 검증 (#3)
- [[T2-Blue-Node]] — BN 런타임 (#5) / [[T4-MCP]] — 도구 호출 프로토콜 (#25)
- [[T6-Security]] — 코드 샌드박스·플러그인 보안 (#35) / [[T6-Event-Logging]] — 개발 도구 로깅 표준 (#58)

## 제공 (Provides To)
- [[T3-Education]] — 코드 실행 환경·린터·테스트 러너 (#17)
- [[T3-Workflow-RPA]] — 자동화 파이프라인 ↔ CI/CD 통합 (B6) / [[T3-Agent-Protocol]] — Plugin SDK·VADD 마켓 ↔ 코드 리뷰 위임 (B8)

## 횡단 개념 연결
- [[C-Series-Verifiers]] — C-3 Code Verifier 검증 연계 / [[MCP-Bridge-Layer]] — 도구 호출 소비
- [[Failover-Chain-Pattern]] — FIM 모델 fallback chain / [[Benchmark-Evaluation-Framework]] — VBS-13 Code 벤치마크 협의

## 관련 모듈 시리즈
- [[MODULE-MAP]] — 코딩 엔진·플러그인 시스템 (L-001~L-050 매핑)

## STEP7 매핑
- 출처: STEP7-L (56 L-ID, L-001~L-050) + STEP7-F §테스트전략 (DT-10)

## 버전별 범위
- V1: P1 MVP 로컬 / V2: P2 API+Plugin (V2 17 변경 등재) / V3: P3 마켓플레이스 (realtime_collaboration·vbs13_benchmark·graphql_api·vadd_marketplace 4 V3 NEW)

## 검증 상태
- Quality Gate: APPROVED (AUTHORITY v2.3, Phase 4 RECOVERY genuine write 2026-06-01, DRAFT→APPROVED 4/4, 평균 L3 87.5)
- LOCK 검증: 10/10 일치 (immutable 재정의 0, CFL 4건 전부 RESOLVED, CONFLICT OPEN 0 영구)

## 원본 문서
- SOT 2: D:\VAMOS\docs\sot 2\3-7_Developer-Tools-API-SDK\
- Authority: 3-7_Developer-Tools-API-SDK\AUTHORITY_CHAIN.md (v2.3)
- Design: [[D2.0-02-Orange-Core]] §실행제한, [[D2.0-03-Blue-Nodes]] §도구호출 (DT-06)
