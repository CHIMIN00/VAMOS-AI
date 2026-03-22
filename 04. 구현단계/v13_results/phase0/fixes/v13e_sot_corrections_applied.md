# v13 Enhanced — SOT 수정 적용 기록

> **적용일**: 2026-03-21
> **세션**: v13 Enhanced Pipeline Session 7
> **원칙**: D-2 전건 수정 (CRITICAL+MAJOR+MINOR 전부)

## 수정 요약

| # | FIX ID | 심각도 | 파일 | 수정 내용 |
|---|--------|--------|------|-----------|
| 1 | FIX-E001 | CRITICAL | B4_CONFIG_SPEC | max_retries 3→2 (4곳: 테이블, V1 TOML, V2 TOML, Pydantic) |
| 2 | FIX-E002 | CRITICAL | D2.0-04_INFRA_CORE | 토큰 한도 100K에 비용 상한 관계 명시 (₩1,300 LOCK) |
| 3 | FIX-E003 | MAJOR | PLAN-3.0 | QoD < 0.40 L2 벡터삽입 금지 임계값 추가 |
| 4 | FIX-E004 | MAJOR | MASTER_SPEC | B/C/D/EVX 확장 시리즈 교차 참조 추가 (I-Series 직후) |
| 5 | FIX-E005 | MAJOR | CLAUDE.md | CI/CD 8-stage 구성 명칭 인라인 정의 |
| 6 | FIX-E006 | MAJOR | SDAR_SPEC | max_retries=1 계층 구분 명시 (MCP 레벨과 별개) |
| 7 | FIX-E007 | MINOR | MASTER_SPEC | V0 정의에 PLAN-3.0 교차 참조 추가 |
| 8 | FIX-E008a | MINOR | MASTER_SPEC | V1 정의에 PLAN-3.0 교차 참조 추가 |
| 9 | FIX-E008b | MINOR | MASTER_SPEC | V2 정의에 PLAN-3.0 교차 참조 추가 |
| 10 | FIX-E008c | MINOR | MASTER_SPEC | V3 정의에 PLAN-3.0 교차 참조 추가 |
| 11 | FIX-E011 | MINOR | PLAN-3.0 | V0 정의에 MASTER_SPEC 교차 참조 추가 (양방향) |

## 수정하지 않은 항목

| FIX ID | 사유 |
|--------|------|
| FIX-E009 (EXP_MODULE_COUNT) | Phase 1 재집계 시 자동 확인 |
| FIX-E010 (PYDANTIC_MODEL_COUNT) | FIX-E004에 포함 |
| FIX-E012 (RANGE_VALUE) | EA 추출 아티팩트, SOT 문제 아님 |

## 백업 파일

- `B4_CONFIG_SPEC_backup_v13e.md`
- `D2.0-04_INFRA_CORE_backup_v13e.md`
- `PLAN-3.0_backup_v13e.md`
- `MASTER_SPEC_backup_v13e.md`
- `CLAUDE_backup_v13e.md`
- `SDAR_SPEC_backup_v13e.md`
