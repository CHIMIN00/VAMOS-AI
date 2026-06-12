---
tags: [type/guide, version/V0, version/V1, version/V2, version/V3]
aliases: [구현가이드 PART2, 구현단계 가이드]
description: "VAMOS 구현가이드 PART2 구현단계 — V0-STEP·V1-Phase·V2·V3 구조 (실측 2026-06-12)"
created: 2026-06-12
---

# Implementation Part 2 (구현가이드 PART 2 — 구현단계 진입)

## 한줄 요약
V0→V1→V2→V3 전체 구현 로드맵의 **구현 정본** — v8~v12 검증 라운드의 대상 문서이자 모든 STEP/Phase별 AI 실행 프롬프트 포함.

## 문서 구조 (실측)
| 절 | 내용 |
|----|------|
| §1 | 전체 로드맵 개요 — 버전별 활성 모듈 수(V0=5→V1=32→V2=42→V3=81) · 의존성 체인 · AI 구현 공통 규칙 |
| §2 **V0 구현** | V0-STEP-1 스캐폴딩(Day1-2) → STEP-2 스키마(Day2-3) → STEP-3 IPC(Day3-5) → STEP-4 ORANGE CORE 최소 파이프라인(Day5-8) → STEP-5 저장소+로깅(Day8-9) → STEP-6 CI+테스트(Day9-10) |
| §3 **V1 구현** | V1-Phase 1 ORANGE CORE 완성(W1-4) → Phase 2 Storage+Memory+RAG(W5-8) → Phase 3 Workflow+Agent(W9-12) → Phase 4 UI/UX(W13-14) → Phase 5 Integration+Test(W15-16) → Phase 6 AI Investing MVP+MCP(W13-16 병렬) |
| §4 **V2 구현** | COND 모듈 확장 (원본 10개 개별 config + v10 확장 106개 카테고리 그룹 config) |
| §5 **V3 구현** | EXP 모듈 — Self-evo/Knowledge/Multimodal/External/Learning·Reasoning/Experimental/RT-BNP V3 (공통 패턴) |
| §6 | 시스템별 상세 구현 가이드 (보안 HMAC 패턴·NEVER_AUTO 탐지기 등) |
| §7 | 최종 검토사항 |

## 위치 부여
- 검증 이력: v10에서 v23.0.0 → v11에서 v25.0.0 → v12 최종 검증 ([[V10-Results]]·[[V11-Results]]·[[V12-Results]])
- 목차/근거 구조 요약은 [[Part2-Master-Reference]] (15_RULES 측 노트)

## 연결
- [[Implementation-Part1]] — 진입전 선행 / [[Part2-Master-Reference]] / [[Beginner-Guide]]
- [[VAMOS-Version-Strategy]] / [[Current-Phase]] / [[STEP7-Implementation-Bridge]]

## 원본
- `D:\VAMOS\docs\guides\VAMOS_구현가이드_PART2_구현단계.md`
