# TIER 1 APPLIED — Phase 0·1 문서 정합 정정 (사용자 승인 후 실집행)

> 2026-06-06 · 사용자 지시 "a 진행" 승인분. 원본 백업: `_targets/_integ/backup/` (전 파일 pre-edit 사본). 편집 EOL/freeze(ReadOnly) 보존.
> 검증: 각 치환은 assertion-guarded(기대 발생수 일치 시에만 적용). 적용 후 grep 재검증 = 잔여 0(의도적 보존 2건 제외).

## 적용 내역 (총 ~45 치환 / 14 파일)

| # | 항목 | 변경 | 파일·위치 | 상태 |
|---|---|---|---|---|
| 1-1 | T3 도메인 링크 | 구→신 경로 3 | challenge_leaderboard.md:39, realtime_collaboration.md:40·41 | ✅ (신 경로 실존 dir 확인) |
| 1-3 | 로드맵 overclaim | "CONFLICT OPEN 0"→"active 0·이연 OPEN 5(5-3)" | VAMOS_최종_로드맵.md:28·31 | ✅ |
| 1-5 | 핵심 도메인 12→5 | 5줄(전수, :144 누락분 포함) | STRATEGY_01:61·180, STRATEGY_02:51·144·175 | ✅ |
| 1-4 | 매트릭스 22→20 | 14줄(box-art 정렬 보존) | STRATEGY_08(×4)·10(×2)·11·P0-2_OBSIDIAN·ROADMAP_SESSION(×2)·phase0_retro(×2)·로드맵 | ✅ |
| 1-6 | SOT2 파일수 648/710→2,654 (폴더 38→42) | 22줄(box-art width-preserving, 산술결합 716→2,722 포함) | STRATEGY_11·08·09·10·01·P0-2(×2)·로드맵 | ✅ (전수) |
| 1-8 | benchmark_results 5→4 | 2줄 | STRATEGY_11:51·423 | ✅ (디스크 실측 4) |
| 1-2 | D2.0-09/10/11 dangling | 주석 플래그(⚠️미생성) 5줄 — **대체 SOT 미지정(사람확인)** | SOT2_SESSION_EXECUTION_PROMPTS.md:7678·7803·7804·8015·8016 | ◐ 플래그(fabrication 회피) |
| 1-7 | 백업 git push | **미실행 — 사람 결정 필요** | (origin) | ⏸ 보류 |

## 의도적 보존 (수정 안 함 — 오류 아님)
- `phase0_retro.md:30` — "648→710 증가" **과거 시점 서술**(P0-0/P0-3 history). 현행 2,654 주석 추가만.
- `STRATEGY_08` 일부 그 외 illustrative 다이어그램은 모두 정정 완료. (STRATEGY_10:36 junction 다이어그램은 width-preserving 정정함.)

## 미실행·미결 (사람 결정)
- **1-7 git push**: 워킹트리에 본 작업과 **무관한 미커밋 변경 다수**(.gitignore·.vscode·v13_results/*.json 등) 존재. 그대로 push 시 전부 번들됨. → 본 Phase0/1 문서 정정만 별도 커밋 후 push 권장. **명시 지시 시 실행**.
- **1-2 D2.0 대체 SOT**: D2.0-09(INFRASTRUCTURE)≈D2.0-04(INFRA_CORE)? / D2.0-10(BENCHMARK)·D2.0-11(TECHNICAL_STACK)은 깔끔한 D2.0 대응문서 부재 → 올바른 대상 **사람 확정** 필요(추측 교체 금지).

## 되돌리기
`_targets/_integ/backup/{A,B,C,D,E,F}__<파일>` 에 각 패스 직전 원본 보존. 복원 = 해당 백업을 원위치 복사(SOT2 freeze 파일은 RO 해제 후 복사·재설정).
