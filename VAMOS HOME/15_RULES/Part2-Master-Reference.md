---
tags: [type/rule, version/V0, version/V1, version/V2, version/V3]
aliases: [PART2 마스터 참조, 모든 도메인 근거]
description: "구현가이드 PART2 목차 구조 요약 — 모든 도메인 구현의 근거 문서 (구조 실측 2026-06-12)"
created: 2026-06-12
---

# Part2 Master Reference (PART2 마스터 참조)

## 한줄 요약
구현가이드 PART2는 SOT 68개를 구현 순서로 재구성한 **구현 정본**으로, 모든 도메인(SOT 2 36개)의 Phase별 구현 근거가 이 문서의 §2~§5에 매핑된다 — 목차 구조 요약 노트.

## 목차 구조 요약 (실측)
| 절 | 범위 | 비고 |
|----|------|------|
| 목차 + Reading Guide + Glossary | 읽기 규약·용어 | v25 신설 |
| §1 전체 구현 로드맵 개요 | §1.1 버전별 활성 모듈(V0=5/V1=32/V2=42/V3=81) · §1.2 의존성 체인 · §1.3 AI 공통 규칙 | 산술 정합 검증됨 |
| §2 V0 구현 | V0-STEP-1~6 (스캐폴딩→스키마→IPC→파이프라인→저장소·로깅→CI) | 각 STEP 자기완결 프롬프트 |
| §3 V1 구현 | V1-Phase 1~6 (CORE 완성→Memory·RAG→Workflow·Agent→UI/UX→Integration→Investing MVP·MCP) | |
| §4 V2 구현 | COND 10 + v10 확장 106 config | |
| §5 V3 구현 | EXP 모듈 공통 패턴 (Self-evo/Knowledge/Multimodal/External/RT-BNP V3 등) | |
| §6 시스템별 상세 | 운영 §6.12(11서브) · 보안(HMAC/STRIDE/OWASP LLM) · §6.13 산술표 | v11에서 신설·보강 |
| §7 최종 검토 | GO/NO-GO 64건 + Stage Gate 204건 | |

## 규칙 측면 (15_RULES 소속 사유)
- 문서 위계: RULE 1.3 > PLAN 3.0 > DESIGN LOCK > 본문 — PART2는 이 위계 하에서만 유효
- LOCK 값·기존 행 변경 0건 원칙으로 버전업(v22→v25.2.0+) — 검증 라운드가 무결성 보증 ([[V13-Results]])

## 연결
- [[Implementation-Part2]] — 가이드 측 상세 노트 / [[Implementation-Part1]] / [[BASE-1.3-Rules]] / [[PLAN-3.0-Roadmap]]
- [[V10-Results]] / [[V11-Results]] / [[V12-Results]] — 버전업 이력

## 원본
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md`
