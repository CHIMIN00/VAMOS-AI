---
tags: [type/workflow, tier/T1, version/V1, status/CORE, lock/FREEZE]
aliases: [셀프체크 루프, Soft Loop, 자체 품질 검증]
description: "S5→S6 Self-check Soft loop 1회·임계값 P0:70/P1:75/P2:80 — CLAUDE.md §7.2·§20"
created: 2026-06-11
---

# Self-Check Loop (Soft Loop)

## 한줄 요약
S5 출력 준비 후 S6에서 I-6 Self-check Engine이 품질을 채점하고, 임계값 미달 시 Soft loop을 자동 1회만 재시도하는 검증 워크플로우.

## 핵심 LOCK 값 (CLAUDE.md §7.2·§20)
| 항목 | 값 | LOCK |
|------|-----|------|
| self_check.threshold_p0 | 70 | LOCK |
| self_check.threshold_p1 | 75 | LOCK |
| self_check.threshold_p2 | 80 | LOCK |
| self_check.soft_loop_max | 1 | LOCK |

## 동작 흐름
1. S5_OUTPUT_READY → SelfCheckGate 진입 (담당: I-6 + EVX 체인)
2. 도메인 우선순위별 임계값 채점: P0=70, P1=75, P2=80
3. 판정 PASS → S6_SELF_CHECKED → S7 메모리 커밋 진행
4. 판정 WARN/FAIL → **Soft loop 자동 1회만** 재생성 시도
5. 재시도 후에도 실패 → 사용자 승인 필요 또는 deny (자동 무한루프 금지)

## 결과 스키마 (ResponseEnvelope 내)
- `self_check{score(0~1), verdict(PASS|WARN|FAIL), reasons[], retry_allowed}`

## 관련 모듈
- I-6 Self-check Engine(CORE) / S-1 Self-check(V1 ON) / EVX-1~6 검증 체인 — [[EVX-Verification-Chain]]

## 연결
- [[Gate-Rejection-Paths]] — SelfCheckGate 실패 분기의 상세
- [[End-to-End-Request-Flow]] / [[5-Gate-Decision-Framework]] / [[T1-Verifier-Engines]]

## 원본
- `D:\VAMOS\CLAUDE.md` §5 Gate표·§7.2 핵심 엔진 LOCK·§20 config.v1.toml LOCK 값
