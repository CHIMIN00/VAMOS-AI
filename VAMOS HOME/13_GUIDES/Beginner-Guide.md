---
tags: [type/guide]
aliases: [초보자 가이드, 전체해설, VAMOS 해설 정본]
description: "VAMOS AI 전체해설 초보자 가이드 v1.1.0 요약 (헤더 실측 2026-06-12)"
created: 2026-06-12
---

# Beginner Guide (VAMOS AI 전체 해설 — 초보자 완전 가이드)

## 한줄 요약
VAMOS AI의 모든 기능·모듈·스킬·아키텍처를 초보자 관점에서 빠짐없이 설명하는 **이해/해설 정본** — SOT 68개 전수 크로스체크 기반 (v1.1.0, 2026-03-13).

## 문서 성격 (헤더 실측)
- 정본 우선순위: RULE 1.3 > PLAN 3.0 > DESIGN 2.0 LOCK > DESIGN 본문 > 스키마/TECH_STACK
- PART2 구현가이드는 **구현 정본**, 본 문서는 **이해/해설 정본** (역할 분리)
- v1.0.0 대비 Gap 18개 보완 완료 (CRITICAL 7 / HIGH 7 / MEDIUM 3 / LOW 1)

## 목차 구조 (실측)
- **PART A: VAMOS AI 이해하기 (What & Why)** — §1 정의·6대 철학·우선순위·14대 목표·7대 Non-Goals·기존 AI 비교 / §2 4계층 아키텍처(Front Mini LLM → ORANGE CORE → BLUE NODES → OTHER BRAINS/INFRA-CORE + Main/Hologram LLM)
- **PART B: 핵심 시스템 동작 원리 (How)** — §3 처리 파이프라인(9-State S0~S8 · 5-Phase · 3-Part Output · TEE Loop · Soft/Hard Loop/Circuit Breaker) / §4 5-Gate 검증(Policy/Cost/Approval/Evidence/SelfCheck)
- 이후 모듈·도메인·메모리·RAG·보안·운영 해설은 세션 분할본과 동일 범위 ([[SESSION-GUIDES-MAP]])

## 연결
- [[SESSION-GUIDES-MAP]] — 세션 분할본 34개 / [[Implementation-Part1]] / [[Implementation-Part2]]
- [[Non-Goals]] / [[5-Gate-Decision-Framework]] / [[End-to-End-Request-Flow]]

## 원본
- `D:\VAMOS\docs\guides\VAMOS_AI_전체해설_초보자가이드.md`
- 세션 운영: `D:\VAMOS\docs\guides\VAMOS_초보자가이드_작업세션_운영가이드.md`
