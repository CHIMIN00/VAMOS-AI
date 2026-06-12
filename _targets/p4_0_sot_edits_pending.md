# P4-0 SOT 수정 지시 — 사용자 승인 대기 (2026-06-12)

> **원칙**: SOT(docs\sot·docs\sot 2) 자동 수정 금지 — 아래 edits는 제시만 하며 집행은 사용자 승인 후(백업+EOL 무회귀+integrity 재기록 동반).
> **차단성**: 전건 표기 명확화/신설 지시 — **Phase 4 비차단** (구현 상세 정본은 PART2 기반영).
> 라인 번호는 2026-06-12 P4-0 재실측값.

## A. GATE-06 #4 (READINESS §8 #4, V0-002) — MASTER_SPEC §0 인덱스 B그룹 표기

| 파일 | 라인 | 현행 | 수정안 |
|------|------|------|--------|
| docs\sot\VAMOS_MASTER_SPECIFICATION.md | L78 (분류 범례) | `PHASE=구현단계가이드(B1~B7)` | `PHASE=구현단계가이드(B1~B7, = IMPLEMENTATION 계층)` |

## B. GATE-07 §a C-001 — 4-게이트 열거 → 5-Gate 전체 열거 (정본: D2.0-02 §8.1 LOCK Policy→Approval→Cost→Evidence→SelfCheck)

| # | 파일 | 라인 (재실측) | 현행 | 수정안 |
|---|------|--------------|------|--------|
| 1 | docs\sot\D2.0-01_01. VAMOS_DESIGN_2_0_OVERVIEW.md | L208 | `모든 액션은 **Policy → Approval → Cost → Evidence** 게이트를 반드시 통과` | `모든 액션은 **Policy → Approval → Cost → Evidence → SelfCheck** 게이트를 반드시 통과` |
| 2 | docs\sot\VAMOS_MASTER_SPECIFICATION.md | L1512 | `\| Gate 우회 불가 \| Policy→Approval→Cost→Evidence 필수 \|` | `\| Gate 우회 불가 \| Policy→Approval→Cost→Evidence→SelfCheck 필수 \|` |
| 3 | docs\sot\VAMOS_BEGINNER_GUIDE.md | L1376 | (L1512와 동일 행) | (동일 수정) |
| 4* | docs\sot\VAMOS_BEGINNER_GUIDE.md | L1813 | `I-5: 게이트 검사 (Policy→Cost→Approval→Evidence)` | `I-5: 게이트 검사 (Policy→Approval→Cost→Evidence; SelfCheck는 verify 노드)` — **P4-0 신규 발견(동계열·순서 오기 포함), GATE-07 기처분 3곳에 추가 제안** |

※ sot CLAUDE.md L236 건은 GATE-07b 동기화로 기해소(SHA 45120F11 일치 재확인 2026-06-12).

## C. PHASE4-DEC-003 (DEC-010 confidence) — PHASE_B4 §3.17 신설 지시

| 파일 | 위치 | 내용 |
|------|------|------|
| docs\sot\PHASE_B4_CONFIG_SPEC.md | §3 말미 신설 (§3.17) | `[confidence]` 섹션: `confidence_high_threshold = 0.85 (LOCK)` / `confidence_medium_threshold = 0.60 (LOCK)` / `confidence_refuse_threshold = 0.30 (LOCK)` — 근거 PHASE3-DEC-010(LOCK Registry §8 R1-A25), V0부터 적용(분모 20→23). 기존 §3.1~3.16 무변경(추가만). |

## 처분 상태

- **승인 대기** (P4-0 세션은 자율 실행 — 사용자 부재로 승인 게이트 통과 불가). 승인 시 집행 절차: 백업(_targets\_integ\backup_p4_0\) → 단일 행 치환 → EOL 사전/사후 CR 실측 무회귀 → integrity 신규 체크.
- 미승인 지속 시: Phase 4 비차단 유지, P4-3(Phase 4 Gate) 재상정.
