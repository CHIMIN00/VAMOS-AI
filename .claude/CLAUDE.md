# VAMOS AI Project — Claude Code v13 작업 설정

> 프로젝트 전체 컨텍스트는 `D:\VAMOS\CLAUDE.md` 참조 (자동 로딩됨)
> 본 파일은 v13 검증 작업의 규칙/도구/파이프라인 정의
> **v13 Enhanced Pipeline 경로**:
>   계획서: `D:\VAMOS\04. 구현단계\v13_enhanced_plan.md`
>   산출물: `D:\VAMOS\04. 구현단계\v13_results\`
>   SOT: `D:\VAMOS\docs\sot\` (68개 파일)

---

## 1. 2계층 검증 아키텍처 (v13.2.0)

```
Layer A: 결정론적 검증 (Python 스크립트 — AI 판단 0%)
  EA 검증: DV-1~DV-10 (스키마/카운트/라인범위/텍스트매칭/ID연속/타입/COUNT↔LIST/표준키/해시/후반부커버리지)
  CM 검증: CM-DV1~DV6 (스키마/카운트/참조확인/SOT대조/유효성/중복탐지)
  → CRITICAL 있으면 FAIL → Hook이 저장 차단

Layer B: AI 의미적 검증 (Skill 에이전트 — Layer A PASS 후에만)
  → SV-1~SV-3: 의미 정확성, 추출 완전성, 표준 키 적절성
  → AD-1~AD-4: 환각 탐지(40%), 값 변조, 약점 패턴, 키 일관성
  → 확증 편향 방지: ANTI-BIAS-1~4 규칙 적용
```

---

## 2. Skills (55개 — 아래 표는 핵심 11개)

| 명령어 | 계층 | 용도 |
|--------|------|------|
| `/validate [파일]` | A+B | 결정론적 검증(DV/CM-DV) + AI 의미 검증(SV) |
| `/audit [파일]` | B | 적대적 감사 v2: 환각/변조/누락/약점/확증편향 |
| `/sot-check [EA\|key]` | B | SOT 원본 파일 직접 대조 |
| `/quality-gate [파일]` | A+B | 전체 파이프라인 1회 실행 (권장) |
| `/extract [all\|EA번호]` | - | SOT → EA JSON 추출 자동화 (C1~C8, 56 표준키) |
| `/cross-match [EA쌍\|C유형\|all]` | - | EA 간 교차매칭 (C1~C8 비교 패턴) |
| `/delta-apply [status\|apply\|verify]` | - | SOT delta 추적/적용 (APPLIED/PENDING/CONFLICT/OUTDATED) |
| `/phase-run [N]` | - | Phase 1~7 오케스트레이터 (의존성 관리, 병렬 실행) |
| `/report [N\|summary\|compare]` | - | Phase별 종합 리포트 (GOLD/SILVER/BRONZE/REJECT) |
| `/integrity [파일\|all\|impact]` | - | SOT 68파일 무결성 모니터 (SHA-256 해시 비교) |
| `/sot-cache [load\|refresh\|status]` | - | v6~v13 검증 산출물을 참조 캐시로 활용 (6-Tier) |

### 검증 파이프라인

```
EA/CM 추출 완료
  → [자동] PreToolUse Hook이 DV/CM-DV 실행 → FAIL이면 저장 차단
  → [자동] Bash/Edit 우회 시 차단/경고
  → [자동] PostToolUse Hook이 검증 결과 요약 출력
  → /quality-gate 파일경로 → 전체 파이프라인
  → GOLD/SILVER → 다음 Phase 진행 가능
  → REJECT → 수정 후 재추출
```

---

## 3. Hooks (16개)

### PreToolUse — 사전 차단/경고 (6개)

| # | Matcher | 대상 | 동작 | 스크립트 |
|---|---------|------|------|----------|
| 1 | Write | EA JSON (`v13_EA*.json`) | DV-1~DV-10 검증 → CRITICAL 시 **저장 차단** | `block_invalid_ea.sh` |
| 2 | Write | CM JSON (`v13_CM*.json`) | CM-DV1~DV6 검증 → CRITICAL 시 **저장 차단** | `block_invalid_cm.sh` |
| 3 | Bash | EA/CM JSON | Bash로 EA/CM 우회 생성 **차단** (약점F) | inline |
| 4 | Edit | EA JSON | Edit 수정 시 DV 재검증 **경고** (약점F) | inline |
| 5 | Edit | CM JSON | Edit 수정 시 CM-DV 재검증 **경고** | inline |
| 6 | Edit | SOT 파일 (`docs/sot/`) | SOT 수정 전 integrity **경고** | inline |

### PostToolUse — 사후 검증/알림 (9개)

| # | Matcher | 대상 | 동작 | 스크립트 |
|---|---------|------|------|----------|
| 1 | Write | EA JSON | DV 자동 실행 + 품질등급 + /quality-gate 권장 | `deterministic_validator.py` |
| 2 | Write | CM JSON | CM-DV 자동 실행 + /validate 권장 | `cm_validator.py` |
| 3 | Write | 검증 결과 | `_dv_result/_sv_result/_cm_dv_result/_audit/_sot_check/_quality_gate` 저장 알림 | inline |
| 4 | Write | Delta 파일 | Delta 저장 시 `/delta-apply status` + `/integrity all` 안내 | inline |
| 5 | Write | Phase 리포트 | `phase*_report.md` 저장 시 `/report summary` 안내 | inline |
| 6 | Edit | EA JSON | DV 재검증 자동 실행 (약점F) | `deterministic_validator.py` |
| 7 | Edit | CM JSON | CM-DV 재검증 자동 실행 | `cm_validator.py` |
| 8 | Edit | SOT 파일 | 영향받는 EA 목록 + 재추출 필요 안내 | `sot_change_detector.sh` |
| 9 | Write | SOT 파일 | 영향받는 EA 목록 + 재추출 필요 안내 | `sot_change_detector.sh` |

### Stop — 세션 종료 체크 (1개)

| # | 동작 |
|---|------|
| 1 | EA FAIL + CM FAIL + 미완료 항목 전수 스캔 → 알림 |

---

## 4. Hook 스크립트 (5개)

| 스크립트 | 역할 | 줄 수 |
|----------|------|-------|
| `hooks/deterministic_validator.py` | Layer A EA 검증기 (DV-1~DV-10), exit 2=FAIL | ~713줄 |
| `hooks/cm_validator.py` | Layer A CM 검증기 (CM-DV1~DV6), exit 2=FAIL | ~382줄 |
| `hooks/block_invalid_ea.sh` | PreToolUse EA 차단 (임시파일→DV→차단/허용) | ~48줄 |
| `hooks/block_invalid_cm.sh` | PreToolUse CM 차단 (임시파일→CM-DV→차단/허용) | ~48줄 |
| `hooks/sot_change_detector.sh` | SOT 수정 감지→영향 EA 목록 출력 | ~45줄 |

---

## 5. v13 작업 규칙

1. **SOT 파일은 전체 읽기**: 2000줄 초과 시 offset 분할하여 전체 읽기
2. **환각 방지 규칙 R1~R8 항상 적용**: v13_plan.md §3.3 참조
3. **Agent tool 병렬 실행**: 독립적인 EA/CM 에이전트는 반드시 병렬 투입
4. **결과 즉시 저장**: 세션 종료 시 미완료 항목은 JSON으로 저장 (R6)
5. **표준 키 사용**: phase0_A_extraction_prompt.md의 표준 키 목록 준수 (DV-8이 검증)
6. **source_file_hashes 필수**: EA metadata에 SOT 파일 SHA-256 해시 포함 (DV-9가 검증)
7. **후반부 누락 방지**: 파일 70% 이후 추출 비율 30% 이상 확인 (DV-10이 검증)
8. **python 명령어**: Windows에서는 `python` 사용 (`python3` 아님)
9. **CM 검증 필수**: CM JSON 저장 시 CM-DV1~DV6 자동 검증 (Hook)
10. **SOT 수정 시 integrity 확인**: SOT 파일 수정 후 반드시 `/integrity` 실행

---

## 6. 디렉토리 구조

```
D:\VAMOS\
├── CLAUDE.md                             # 프로젝트 전체 컨텍스트 (자동 로딩)
├── docs\sot\                             # SOT 68개 파일 (정본)
├── 04. 구현단계\
│   ├── v13_plan.md                       # v13 계획서
│   ├── v13\prompts\                      # Phase별 프롬프트
│   ├── v8_results\                       # v8 검증 결과 (Tier 4 캐시)
│   ├── v9_results\                       # v9 검증 결과 (Tier 4 캐시)
│   ├── v10_results\                      # v10 Feature Registry (Tier 2 캐시)
│   ├── v11_results\                      # v11 인덱스 (Tier 5 캐시)
│   ├── v12\v12_results\                  # v12 구조 인덱스 (Tier 1 캐시)
│   └── v13_results\
│       └── phase0\
│           ├── extraction\               # EA-1~15 추출 결과
│           │   ├── validation\           # DV + SV 결과
│           │   ├── audit\                # 적대적 감사 결과
│           │   └── sot_check\            # SOT 대조 결과
│           ├── cross_match\              # CM C1~C8 크로스매칭
│           │   └── validation\           # CM-DV 검증 결과
│           ├── fixes\                    # Phase 0-CDF 수정
│           └── integrity\                # SOT 무결성 체크 결과
└── .claude\
    ├── CLAUDE.md                         # 본 파일 (v13 작업 규칙)
    ├── settings.json                     # Hooks 설정 (16개)
    ├── hooks\                            # 결정론적 검증 스크립트 (5개)
    │   ├── deterministic_validator.py    # DV-1~DV-10
    │   ├── cm_validator.py               # CM-DV1~DV6
    │   ├── block_invalid_ea.sh           # EA 저장 차단
    │   ├── block_invalid_cm.sh           # CM 저장 차단
    │   └── sot_change_detector.sh        # SOT 수정 감지
    └── skills\                           # 스킬 11개
        ├── validate\SKILL.md             # /validate
        ├── audit\SKILL.md                # /audit
        ├── sot-check\SKILL.md            # /sot-check
        ├── quality-gate\SKILL.md         # /quality-gate
        ├── extract\SKILL.md              # /extract
        ├── cross-match\SKILL.md          # /cross-match
        ├── delta-apply\SKILL.md          # /delta-apply
        ├── phase-run\SKILL.md            # /phase-run
        ├── report\SKILL.md               # /report
        ├── integrity\SKILL.md            # /integrity
        ├── sot-cache\SKILL.md            # /sot-cache
        └── TOOL_GUIDE_32.md              # 32개 외부 도구 가이드
```

---

## 7. 품질 등급 (Quality Gate)

| 등급 | 조건 | 다음 단계 |
|------|------|----------|
| **GOLD** | DV PASS + SV PASS + Audit PASS + SOT-Check PASS | Phase 진행 가능 |
| **SILVER** | DV PASS + SV PASS + (Audit/SOT-Check에 minor만) | Phase 진행 가능 (주의) |
| **BRONZE** | DV PASS + (SV에 WARNING 있음) | 수정 권장 후 진행 |
| **REJECT** | DV FAIL 또는 CRITICAL 미해결 | 수정 후 재추출 필수 |
