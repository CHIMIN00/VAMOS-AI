# P4-0 SOT 수정 지시 — ✅ 사용자 승인·집행 완료 (2026-06-12)

> **⟦집행 기록 (2026-06-12 사용자 승인)⟧**: A/B(4곳 — L1813 포함)/C 전건 집행 완료.
> - 정정 2건: ①MASTER_SPEC L78 원문은 "구현**직접**가이드(B1~B7)" — 표의 "구현단계가이드"는 추정 오기, 원문 기준 집행 ②C항 신설 번호는 **§3.16**(B4 실측: §3.1~3.15+3.8a/3.8b=17섹션, 다음 번호 3.16 — "§3.17" 표기는 추정 오기). §4.1 V1 프리셋 toml에도 [confidence] 동반 추가(동일 결정의 일관 반영, 추가만).
> - 추가 확인: **PHASE_B4 §3.7 정본 자체가 warn_threshold=80/block_threshold=100** — PHASE4-DEC-002 병존 설계와 정확 일치(PART2 템플릿 70/85/95가 B4 정본 이탈이었음 확정).
> - EOL 무회귀: MASTER_SPEC CRLF(CR=LF=1904) 보존 / D2.0-01·BEGINNER·PHASE_B4 LF(CR 0) 보존. 백업 `_targets/_integ/backup_p4_0/*.pre-sot-edit.md`.
> - integrity 신규 체크: `v13_integrity_check_20260612T230000.json` — **CHANGED_AS_APPROVED**(승인 4파일 + CLAUDE.md[DEC-011 F1 기집행분, SHA 45120F11 검증] 한정, 이외 변경 0) → 새 참조 기준.
> - ⚠️ MASTER_SPEC은 CRLF-디스크/LF-blob 이중 상태였음 — 본 커밋으로 blob이 디스크 진실(CRLF)로 수렴(PHASE4-DEC-006 자연 수렴 경로, d5bc6e8 선례 공시).

---

(이하 원문 — 승인 전 제시본)

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
